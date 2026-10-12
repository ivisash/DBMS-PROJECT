-- ============================================================================
-- PHARMACY PRESCRIPTION AND MEDICINE STOCK MANAGEMENT SYSTEM
-- Review 2: Analytical SQL Queries and Views
-- Covering: Joins, Nested Queries, Aggregations, Views, Window Functions
-- ============================================================================

USE pharmacy_db;

-- ============================================================================
-- VIEW 1: Current Stock Summary with Reorder Alerts
-- ============================================================================
CREATE OR REPLACE VIEW view_current_stock AS
SELECT 
    m.medicine_id,
    m.brand_name,
    m.generic_name,
    c.category_name,
    mf.company_name AS manufacturer,
    m.dosage_form,
    m.strength,
    m.reorder_level,
    COALESCE(SUM(b.current_stock), 0) AS total_units_in_stock,
    COUNT(b.batch_id) AS active_batches_count,
    CASE 
        WHEN COALESCE(SUM(b.current_stock), 0) = 0 THEN 'OUT OF STOCK'
        WHEN COALESCE(SUM(b.current_stock), 0) <= m.reorder_level THEN 'REORDER REQUIRED'
        ELSE 'SUFFICIENT'
    END AS stock_status,
    COALESCE(SUM(b.current_stock * b.unit_sale_price), 0.00) AS total_inventory_mrp_value
FROM medicines m
JOIN categories c ON m.category_id = c.category_id
JOIN manufacturers mf ON m.manufacturer_id = mf.manufacturer_id
LEFT JOIN batches b ON m.medicine_id = b.medicine_id AND b.current_stock > 0
GROUP BY m.medicine_id, m.brand_name, m.generic_name, c.category_name, mf.company_name, m.dosage_form, m.strength, m.reorder_level;

-- Test View 1:
SELECT * FROM view_current_stock ORDER BY stock_status DESC, brand_name;


-- ============================================================================
-- VIEW 2: Near-Expiry Batches Report (Expiring within 60 days or Already Expired)
-- ============================================================================
CREATE OR REPLACE VIEW view_near_expiry_batches AS
SELECT 
    b.batch_id,
    b.batch_number,
    m.brand_name,
    m.generic_name,
    c.category_name,
    b.expiry_date,
    DATEDIFF(b.expiry_date, CURDATE()) AS days_until_expiry,
    b.current_stock,
    b.unit_sale_price,
    (b.current_stock * b.unit_cost_price) AS capital_at_risk,
    CASE 
        WHEN b.expiry_date < CURDATE() THEN 'EXPIRED (DO NOT SELL)'
        WHEN DATEDIFF(b.expiry_date, CURDATE()) <= 30 THEN 'CRITICAL (<30 Days)'
        WHEN DATEDIFF(b.expiry_date, CURDATE()) <= 60 THEN 'WARNING (<60 Days)'
        ELSE 'SAFE'
    END AS alert_status
FROM batches b
JOIN medicines m ON b.medicine_id = m.medicine_id
JOIN categories c ON m.category_id = c.category_id
WHERE b.current_stock > 0
  AND DATEDIFF(b.expiry_date, CURDATE()) <= 90
ORDER BY b.expiry_date ASC;

-- Test View 2:
SELECT * FROM view_near_expiry_batches;


-- ============================================================================
-- VIEW 3: Supplier Purchases Summary (Procurement Aggregations)
-- ============================================================================
CREATE OR REPLACE VIEW view_supplier_purchases AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.gst_number,
    s.phone,
    COUNT(p.purchase_id) AS total_orders_placed,
    COALESCE(SUM(p.total_amount), 0.00) AS total_procurement_value,
    COALESCE(SUM(b.initial_quantity), 0) AS total_units_procured,
    MAX(p.purchase_date) AS latest_purchase_date
FROM suppliers s
LEFT JOIN purchases p ON s.supplier_id = p.supplier_id
LEFT JOIN batches b ON p.purchase_id = b.purchase_id
GROUP BY s.supplier_id, s.supplier_name, s.gst_number, s.phone;

-- Test View 3:
SELECT * FROM view_supplier_purchases ORDER BY total_procurement_value DESC;


-- ============================================================================
-- VIEW 4: Prescription Sales & Regulatory Compliance View
-- Tracks sales containing restricted Schedule H medicines with doctor details
-- ============================================================================
CREATE OR REPLACE VIEW view_prescription_sales AS
SELECT 
    s.invoice_number,
    s.sale_date,
    c.full_name AS patient_name,
    c.phone_number AS patient_phone,
    p.prescription_code,
    p.doctor_name,
    p.doctor_reg_no,
    p.clinic_name,
    m.brand_name AS medicine_dispensed,
    b.batch_number,
    si.quantity AS units_dispensed,
    si.total_price AS item_amount
FROM sales s
JOIN prescriptions p ON s.prescription_id = p.prescription_id
JOIN customers c ON s.customer_id = c.customer_id
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN batches b ON si.batch_id = b.batch_id
JOIN medicines m ON b.medicine_id = m.medicine_id
ORDER BY s.sale_date DESC;

-- Test View 4:
SELECT * FROM view_prescription_sales;


-- ============================================================================
-- VIEW 5: Fast-Moving Medicines (Sales Volume & Frequency Ranking)
-- ============================================================================
CREATE OR REPLACE VIEW view_fast_moving_items AS
SELECT 
    m.medicine_id,
    m.brand_name,
    m.generic_name,
    c.category_name,
    COUNT(DISTINCT si.sale_id) AS bills_count,
    SUM(si.quantity) AS total_units_sold,
    SUM(si.total_price) AS total_gross_revenue,
    DENSE_RANK() OVER (ORDER BY SUM(si.quantity) DESC) AS sales_rank
FROM medicines m
JOIN categories c ON m.category_id = c.category_id
JOIN batches b ON m.medicine_id = b.medicine_id
JOIN sale_items si ON b.batch_id = si.batch_id
GROUP BY m.medicine_id, m.brand_name, m.generic_name, c.category_name;

-- Test View 5:
SELECT * FROM view_fast_moving_items ORDER BY sales_rank ASC;


-- ============================================================================
-- VIEW 6: Profit and Financial Margin Analysis
-- Calculates Gross Profit = (Selling Price - Cost Price) * Quantity Sold
-- ============================================================================
CREATE OR REPLACE VIEW view_profit_analysis AS
SELECT 
    m.medicine_id,
    m.brand_name,
    c.category_name,
    SUM(si.quantity) AS units_sold,
    SUM(si.quantity * b.unit_cost_price) AS total_cost_of_goods_sold,
    SUM(si.total_price) AS total_revenue_generated,
    SUM(si.total_price) - SUM(si.quantity * b.unit_cost_price) AS gross_profit,
    ROUND(
        ((SUM(si.total_price) - SUM(si.quantity * b.unit_cost_price)) / NULLIF(SUM(si.total_price), 0)) * 100, 
        2
    ) AS profit_margin_percentage
FROM sale_items si
JOIN batches b ON si.batch_id = b.batch_id
JOIN medicines m ON b.medicine_id = m.medicine_id
JOIN categories c ON m.category_id = c.category_id
GROUP BY m.medicine_id, m.brand_name, c.category_name;

-- Test View 6:
SELECT * FROM view_profit_analysis ORDER BY gross_profit DESC;


-- ============================================================================
-- SAMPLE COMPLEX NESTED QUERIES (For Review 2 Viva and Evaluation)
-- ============================================================================

-- Query 1: Medicines whose stock is below average stock of their category (Nested Correlated Subquery)
SELECT 
    m.brand_name,
    c.category_name,
    COALESCE(SUM(b.current_stock), 0) AS current_stock
FROM medicines m
JOIN categories c ON m.category_id = c.category_id
LEFT JOIN batches b ON m.medicine_id = b.medicine_id
GROUP BY m.medicine_id, m.brand_name, c.category_name, m.category_id
HAVING current_stock < (
    SELECT AVG(cat_stock.stock_sum)
    FROM (
        SELECT m2.category_id, COALESCE(SUM(b2.current_stock), 0) AS stock_sum
        FROM medicines m2
        LEFT JOIN batches b2 ON m2.medicine_id = b2.medicine_id
        GROUP BY m2.medicine_id, m2.category_id
    ) cat_stock
    WHERE cat_stock.category_id = m.category_id
);

-- Query 2: Customers who have bought restricted medicines without returning (Set Difference / Subquery)
SELECT customer_id, full_name, phone_number
FROM customers
WHERE customer_id IN (
    SELECT s.customer_id
    FROM sales s
    JOIN sale_items si ON s.sale_id = si.sale_id
    JOIN batches b ON si.batch_id = b.batch_id
    JOIN medicines m ON b.medicine_id = m.medicine_id
    WHERE m.requires_prescription = 1
);
