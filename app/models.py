"""
Pharmacy Management System - Business Logic & Repository Functions
"""
from datetime import datetime, date
from app.db import get_connection, execute_query


def list_categories():
    rows, _, _ = execute_query("SELECT category_id, category_name, description FROM categories ORDER BY category_name")
    return rows


def list_manufacturers():
    rows, _, _ = execute_query("SELECT manufacturer_id, company_name, contact_email, phone FROM manufacturers ORDER BY company_name")
    return rows


def list_suppliers():
    rows, _, _ = execute_query("SELECT supplier_id, supplier_name, gst_number, phone, contact_person FROM suppliers ORDER BY supplier_name")
    return rows


def list_medicines(search=""):
    sql = """
        SELECT m.medicine_id, m.brand_name, m.generic_name, c.category_name, 
               mf.company_name AS manufacturer, m.dosage_form, m.strength, 
               m.reorder_level, m.requires_prescription,
               COALESCE(SUM(b.current_stock), 0) AS total_stock
        FROM medicines m
        JOIN categories c ON m.category_id = c.category_id
        JOIN manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
        LEFT JOIN batches b ON m.medicine_id = b.medicine_id
        WHERE m.brand_name LIKE ? OR m.generic_name LIKE ?
        GROUP BY m.medicine_id
        ORDER BY m.brand_name
    """
    param = f"%{search}%"
    rows, _, _ = execute_query(sql, (param, param))
    return rows


def add_medicine(brand_name, generic_name, category_id, manufacturer_id, dosage_form, strength, reorder_level, requires_rx):
    sql = """
        INSERT INTO medicines (brand_name, generic_name, category_id, manufacturer_id, dosage_form, strength, reorder_level, requires_prescription)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    _, last_id, _ = execute_query(sql, (brand_name, generic_name, category_id, manufacturer_id, dosage_form, strength, int(reorder_level), int(requires_rx)), commit=True)
    return last_id


def list_batches(medicine_id=None, active_only=True):
    sql = """
        SELECT b.batch_id, b.batch_number, m.brand_name, m.dosage_form, m.strength,
               b.manufacture_date, b.expiry_date, b.unit_cost_price, b.unit_sale_price,
               b.initial_quantity, b.current_stock,
               m.requires_prescription
        FROM batches b
        JOIN medicines m ON b.medicine_id = m.medicine_id
        WHERE 1=1
    """
    params = []
    if medicine_id:
        sql += " AND b.medicine_id = ?"
        params.append(medicine_id)
    if active_only:
        sql += " AND b.current_stock > 0"
    sql += " ORDER BY b.expiry_date ASC"
    rows, _, _ = execute_query(sql, tuple(params))
    return rows


def add_purchase_and_batch(invoice_number, supplier_id, purchase_date, medicine_id, batch_number,
                           mfg_date, exp_date, unit_cost, unit_sale, quantity):
    """
    Enforces atomic purchase and batch intake.
    """
    total_cost = float(unit_cost) * int(quantity)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Insert Purchase
        cursor.execute(
            "INSERT INTO purchases (invoice_number, supplier_id, purchase_date, total_amount, payment_status) VALUES (?, ?, ?, ?, 'PAID')",
            (invoice_number, supplier_id, purchase_date, total_cost)
        )
        purchase_id = cursor.lastrowid

        # 2. Insert Batch
        cursor.execute(
            """INSERT INTO batches 
               (batch_number, medicine_id, purchase_id, manufacture_date, expiry_date, unit_cost_price, unit_sale_price, initial_quantity, current_stock)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (batch_number, medicine_id, purchase_id, mfg_date, exp_date, float(unit_cost), float(unit_sale), int(quantity), int(quantity))
        )
        batch_id = cursor.lastrowid

        # 3. Log Stock Movement
        cursor.execute(
            "INSERT INTO stock_movements (batch_id, movement_type, quantity, reference_id, remarks) VALUES (?, 'PURCHASE_IN', ?, ?, ?)",
            (batch_id, int(quantity), purchase_id, f"Inward shipment against invoice {invoice_number}")
        )

        conn.commit()
        return purchase_id, batch_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def list_customers():
    rows, _, _ = execute_query("SELECT customer_id, full_name, phone_number, email, address FROM customers ORDER BY full_name")
    return rows


def add_customer(full_name, phone_number, email=None, gender="Male", address=None):
    sql = "INSERT INTO customers (full_name, phone_number, email, gender, address) VALUES (?, ?, ?, ?, ?)"
    _, cust_id, _ = execute_query(sql, (full_name, phone_number, email, gender, address), commit=True)
    return cust_id


def list_prescriptions(customer_id=None):
    sql = """
        SELECT p.prescription_id, p.prescription_code, c.full_name AS customer_name, c.phone_number,
               p.doctor_name, p.doctor_reg_no, p.clinic_name, p.issue_date, p.notes
        FROM prescriptions p
        JOIN customers c ON p.customer_id = c.customer_id
    """
    params = []
    if customer_id:
        sql += " WHERE p.customer_id = ?"
        params.append(customer_id)
    sql += " ORDER BY p.issue_date DESC"
    rows, _, _ = execute_query(sql, tuple(params))
    return rows


def add_prescription(prescription_code, customer_id, doctor_name, doctor_reg_no, clinic_name, issue_date, notes=""):
    sql = """
        INSERT INTO prescriptions (prescription_code, customer_id, doctor_name, doctor_reg_no, clinic_name, issue_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    _, rx_id, _ = execute_query(sql, (prescription_code, customer_id, doctor_name, doctor_reg_no, clinic_name, issue_date, notes), commit=True)
    return rx_id


def process_sale_transaction(invoice_number, customer_id, prescription_id, items, payment_method="CASH", discount=0.0):
    """
    Processes sales billing with strict business rules:
    - items = [{'batch_id': int, 'quantity': int}]
    - Validates no expired medicines
    - Validates sufficient stock
    - Validates prescription requirement
    - Updates batch current_stock
    - Logs stock movements
    """
    today_str = date.today().isoformat()
    conn = get_connection()
    try:
        cursor = conn.cursor()

        subtotal = 0.0
        validated_items = []

        for item in items:
            b_id = item['batch_id']
            qty = int(item['quantity'])

            # Fetch batch & medicine info
            cursor.execute(
                """SELECT b.batch_number, b.expiry_date, b.current_stock, b.unit_sale_price,
                          m.brand_name, m.requires_prescription
                   FROM batches b
                   JOIN medicines m ON b.medicine_id = m.medicine_id
                   WHERE b.batch_id = ?""",
                (b_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Batch ID {b_id} does not exist.")

            batch_data = dict(row)
            # 1. Expiry Check
            if str(batch_data['expiry_date']) < today_str:
                raise ValueError(f"CRITICAL SAFETY VIOLATION: Batch {batch_data['batch_number']} of '{batch_data['brand_name']}' expired on {batch_data['expiry_date']}! Cannot dispense.")

            # 2. Stock Limit Check
            if batch_data['current_stock'] < qty:
                raise ValueError(f"Stock shortage: Batch {batch_data['batch_number']} only has {batch_data['current_stock']} units, requested {qty}.")

            # 3. Prescription Check
            if batch_data['requires_prescription'] == 1 and not prescription_id:
                raise ValueError(f"Prescription required: '{batch_data['brand_name']}' is a restricted medicine. Valid Prescription ID must be provided.")

            line_total = qty * float(batch_data['unit_sale_price'])
            subtotal += line_total
            validated_items.append({
                'batch_id': b_id,
                'quantity': qty,
                'unit_price': float(batch_data['unit_sale_price']),
                'line_total': line_total,
                'brand_name': batch_data['brand_name']
            })

        tax_amount = round(subtotal * 0.05, 2)  # 5% GST on medicines
        net_amount = round(subtotal - discount + tax_amount, 2)

        # Insert Sale record
        cursor.execute(
            """INSERT INTO sales (invoice_number, customer_id, prescription_id, sale_date, subtotal, discount_amount, tax_amount, net_amount, payment_method)
               VALUES (?, ?, ?, datetime('now'), ?, ?, ?, ?, ?)""",
            (invoice_number, customer_id, prescription_id, subtotal, discount, tax_amount, net_amount, payment_method)
        )
        sale_id = cursor.lastrowid

        # Insert items and deduct stock
        for v_item in validated_items:
            cursor.execute(
                "INSERT INTO sale_items (sale_id, batch_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
                (sale_id, v_item['batch_id'], v_item['quantity'], v_item['unit_price'], v_item['line_total'])
            )
            cursor.execute(
                "UPDATE batches SET current_stock = current_stock - ? WHERE batch_id = ?",
                (v_item['quantity'], v_item['batch_id'])
            )
            cursor.execute(
                "INSERT INTO stock_movements (batch_id, movement_type, quantity, reference_id, remarks) VALUES (?, 'SALE_OUT', ?, ?, ?)",
                (v_item['batch_id'], v_item['quantity'], sale_id, f"Sold via invoice {invoice_number}")
            )

        # Payment log
        cursor.execute(
            "INSERT INTO payments (transaction_type, reference_id, amount, payment_mode, transaction_status) VALUES ('SALE_COLLECTION', ?, ?, ?, 'SUCCESS')",
            (sale_id, net_amount, payment_method)
        )

        conn.commit()
        return sale_id, net_amount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ============================================================================
# REPORTS & ANALYTICS (PBL Evaluation Requirements)
# ============================================================================

def report_current_stock():
    sql = """
        SELECT m.brand_name, m.generic_name, c.category_name, m.dosage_form, m.strength,
               m.reorder_level,
               COALESCE(SUM(b.current_stock), 0) AS current_stock,
               COUNT(b.batch_id) AS batch_count,
               CASE 
                   WHEN COALESCE(SUM(b.current_stock), 0) = 0 THEN 'OUT OF STOCK'
                   WHEN COALESCE(SUM(b.current_stock), 0) <= m.reorder_level THEN 'REORDER NEEDED'
                   ELSE 'ADEQUATE'
               END AS status
        FROM medicines m
        JOIN categories c ON m.category_id = c.category_id
        LEFT JOIN batches b ON m.medicine_id = b.medicine_id AND b.current_stock > 0
        GROUP BY m.medicine_id
        ORDER BY current_stock ASC
    """
    rows, _, _ = execute_query(sql)
    return rows


def report_near_expiry_batches():
    """Returns batches with stock expiring soon or already expired."""
    sql = """
        SELECT b.batch_number, m.brand_name, c.category_name, b.expiry_date,
               b.current_stock, b.unit_sale_price,
               (b.current_stock * b.unit_cost_price) AS capital_at_risk,
               CASE 
                   WHEN b.expiry_date < date('now') THEN 'EXPIRED'
                   WHEN b.expiry_date <= date('now', '+30 days') THEN 'CRITICAL (<30d)'
                   WHEN b.expiry_date <= date('now', '+60 days') THEN 'WARNING (<60d)'
                   ELSE 'SAFE'
               END AS alert_status
        FROM batches b
        JOIN medicines m ON b.medicine_id = m.medicine_id
        JOIN categories c ON m.category_id = c.category_id
        WHERE b.current_stock > 0
          AND b.expiry_date <= date('now', '+90 days')
        ORDER BY b.expiry_date ASC
    """
    rows, _, _ = execute_query(sql)
    return rows


def report_supplier_purchases():
    sql = """
        SELECT s.supplier_name, s.gst_number, s.phone,
               COUNT(p.purchase_id) AS total_orders,
               COALESCE(SUM(p.total_amount), 0.0) AS total_procurement_val,
               MAX(p.purchase_date) AS last_purchase_date
        FROM suppliers s
        LEFT JOIN purchases p ON s.supplier_id = p.supplier_id
        GROUP BY s.supplier_id
        ORDER BY total_procurement_val DESC
    """
    rows, _, _ = execute_query(sql)
    return rows


def report_prescription_sales():
    sql = """
        SELECT s.invoice_number, s.sale_date, c.full_name AS patient,
               p.prescription_code, p.doctor_name, p.doctor_reg_no,
               m.brand_name AS medicine, si.quantity, si.total_price
        FROM sales s
        JOIN prescriptions p ON s.prescription_id = p.prescription_id
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN sale_items si ON s.sale_id = si.sale_id
        JOIN batches b ON si.batch_id = b.batch_id
        JOIN medicines m ON b.medicine_id = m.medicine_id
        ORDER BY s.sale_date DESC
    """
    rows, _, _ = execute_query(sql)
    return rows


def report_fast_moving_items():
    sql = """
        SELECT m.brand_name, m.generic_name, c.category_name,
               SUM(si.quantity) AS total_units_sold,
               SUM(si.total_price) AS gross_revenue
        FROM medicines m
        JOIN categories c ON m.category_id = c.category_id
        JOIN batches b ON m.medicine_id = b.medicine_id
        JOIN sale_items si ON b.batch_id = si.batch_id
        GROUP BY m.medicine_id
        ORDER BY total_units_sold DESC
    """
    rows, _, _ = execute_query(sql)
    return rows


def report_profit_analysis():
    sql = """
        SELECT m.brand_name, c.category_name,
               SUM(si.quantity) AS units_sold,
               ROUND(SUM(si.quantity * b.unit_cost_price), 2) AS total_cost,
               ROUND(SUM(si.total_price), 2) AS total_revenue,
               ROUND(SUM(si.total_price) - SUM(si.quantity * b.unit_cost_price), 2) AS gross_profit,
               ROUND(((SUM(si.total_price) - SUM(si.quantity * b.unit_cost_price)) / SUM(si.total_price)) * 100, 1) AS margin_pct
        FROM sale_items si
        JOIN batches b ON si.batch_id = b.batch_id
        JOIN medicines m ON b.medicine_id = m.medicine_id
        JOIN categories c ON m.category_id = c.category_id
        GROUP BY m.medicine_id
        ORDER BY gross_profit DESC
    """
    rows, _, _ = execute_query(sql)
    return rows
