"""
Pharmacy Prescription and Medicine Stock Management System
Interactive Command-Line Interface (CLI)
"""
import sys
import os
from datetime import date
from tabulate import tabulate

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import models
from app.db import init_database


def clear_screen():
    print("\n" + "=" * 80 + "\n")


def display_header():
    print("""
  +----------------------------------------------------------------------------+
  |       PHARMACY PRESCRIPTION & MEDICINE STOCK MANAGEMENT SYSTEM             |
  |                   Database Management Systems (DBMS PBL)                   |
  +----------------------------------------------------------------------------+
    """)


def view_medicines_menu():
    clear_screen()
    print(">>> MEDICINE CATALOGUE & STOCK SUMMARY")
    search = input("Enter search keyword (Brand or Generic, press Enter for all): ").strip()
    meds = models.list_medicines(search)
    if not meds:
        print("[!] No medicines found.")
        return

    table = []
    for m in meds:
        rx_tag = "Rx (Restricted)" if m["requires_prescription"] else "OTC"
        table.append([
            m["medicine_id"],
            m["brand_name"],
            m["generic_name"],
            m["category_name"],
            m["dosage_form"],
            m["strength"],
            m["total_stock"],
            m["reorder_level"],
            rx_tag
        ])
    print(tabulate(table, headers=["ID", "Brand Name", "Generic Name", "Category", "Form", "Strength", "Stock", "Reorder", "Type"], tablefmt="grid"))


def add_medicine_menu():
    clear_screen()
    print(">>> ADD NEW MEDICINE")
    categories = models.list_categories()
    manufacturers = models.list_manufacturers()

    print("\nAvailable Categories:")
    for c in categories:
        print(f"  [{c['category_id']}] {c['category_name']}")
    
    print("\nAvailable Manufacturers:")
    for m in manufacturers:
        print(f"  [{m['manufacturer_id']}] {m['company_name']}")

    try:
        brand = input("\nBrand Name (e.g. Dolo 650): ").strip()
        generic = input("Generic Name (e.g. Paracetamol): ").strip()
        cat_id = int(input("Category ID: ").strip())
        mfr_id = int(input("Manufacturer ID: ").strip())
        form = input("Dosage Form (Tablet/Capsule/Syrup/Injection/Ointment): ").strip().capitalize()
        strength = input("Strength (e.g. 650mg): ").strip()
        reorder = int(input("Reorder Level threshold (e.g. 30): ").strip())
        is_rx = int(input("Requires Prescription? (1 for Yes / 0 for No): ").strip())

        new_id = models.add_medicine(brand, generic, cat_id, mfr_id, form, strength, reorder, is_rx)
        print(f"\n[OK] Successfully added '{brand}' with Medicine ID: {new_id}")
    except Exception as e:
        print(f"\n[FAIL] Failed to add medicine: {e}")


def view_batches_menu():
    clear_screen()
    print(">>> BATCH-WISE STOCK INVENTORY")
    batches = models.list_batches(active_only=False)
    if not batches:
        print("[!] No batches recorded.")
        return

    table = []
    for b in batches:
        table.append([
            b["batch_id"],
            b["batch_number"],
            b["brand_name"],
            f"{b['dosage_form']} ({b['strength']})",
            b["manufacture_date"],
            b["expiry_date"],
            f"Rs.{b['unit_cost_price']:.2f}",
            f"Rs.{b['unit_sale_price']:.2f}",
            b["current_stock"],
            b["initial_quantity"]
        ])
    print(tabulate(table, headers=["ID", "Batch #", "Medicine", "Form", "Mfg Date", "Exp Date", "Cost (Rs)", "Sale (Rs)", "Stock", "Initial Qty"], tablefmt="grid"))


def purchase_intake_menu():
    clear_screen()
    print(">>> SUPPLIER PURCHASE & BATCH INTAKE")
    suppliers = models.list_suppliers()
    print("\nSuppliers:")
    for s in suppliers:
        print(f"  [{s['supplier_id']}] {s['supplier_name']} (Phone: {s['phone']})")

    try:
        inv_no = input("\nSupplier Invoice Number: ").strip()
        supp_id = int(input("Supplier ID: ").strip())
        purch_date = input(f"Purchase Date (YYYY-MM-DD) [{date.today().isoformat()}]: ").strip() or date.today().isoformat()
        med_id = int(input("Medicine ID to receive: ").strip())
        batch_no = input("Batch Number: ").strip()
        mfg_date = input("Manufacture Date (YYYY-MM-DD): ").strip()
        exp_date = input("Expiry Date (YYYY-MM-DD): ").strip()
        cost_price = float(input("Unit Cost / Purchase Price (Rs): ").strip())
        sale_price = float(input("Unit MRP / Sale Price (Rs): ").strip())
        qty = int(input("Quantity Received: ").strip())

        p_id, b_id = models.add_purchase_and_batch(
            inv_no, supp_id, purch_date, med_id, batch_no, mfg_date, exp_date, cost_price, sale_price, qty
        )
        print(f"\n[OK] Purchase recorded successfully (Purchase ID: {p_id}, Batch ID: {b_id})")
        print(f"[OK] Added {qty} units into Batch '{batch_no}'.")
    except Exception as e:
        print(f"\n[FAIL] Error processing purchase entry: {e}")


def customer_and_rx_menu():
    clear_screen()
    print(">>> CUSTOMER & PRESCRIPTION MANAGEMENT")
    print("1. View Customers")
    print("2. Register New Customer")
    print("3. View Prescriptions")
    print("4. Add New Prescription")
    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        custs = models.list_customers()
        table = [[c["customer_id"], c["full_name"], c["phone_number"], c["email"] or "N/A", c["address"] or "N/A"] for c in custs]
        print(tabulate(table, headers=["ID", "Name", "Phone", "Email", "Address"], tablefmt="grid"))
    elif choice == "2":
        name = input("Full Name: ").strip()
        phone = input("Phone Number: ").strip()
        email = input("Email: ").strip()
        address = input("Address: ").strip()
        cid = models.add_customer(name, phone, email, "Male", address)
        print(f"\n[OK] Customer registered with ID: {cid}")
    elif choice == "3":
        rxs = models.list_prescriptions()
        table = [[r["prescription_id"], r["prescription_code"], r["customer_name"], r["doctor_name"], r["doctor_reg_no"], r["issue_date"], r["notes"]] for r in rxs]
        print(tabulate(table, headers=["ID", "Rx Code", "Patient", "Doctor", "Reg No", "Date", "Notes"], tablefmt="grid"))
    elif choice == "4":
        code = input("Prescription Code (e.g. RX-2026-901): ").strip()
        cust_id = int(input("Customer ID: ").strip())
        doc_name = input("Doctor Name (Dr. ...): ").strip()
        reg_no = input("Doctor Medical Reg Number: ").strip()
        clinic = input("Clinic / Hospital Name: ").strip()
        dt = input(f"Issue Date (YYYY-MM-DD) [{date.today().isoformat()}]: ").strip() or date.today().isoformat()
        notes = input("Diagnosis / Instructions: ").strip()
        rx_id = models.add_prescription(code, cust_id, doc_name, reg_no, clinic, dt, notes)
        print(f"\n[OK] Prescription registered with ID: {rx_id}")


def sales_billing_menu():
    clear_screen()
    print(">>> POINT OF SALE (POS) BILLING & DISPENSING")
    
    # 1. Customer
    cust_id_input = input("Customer ID (leave blank for Walk-in): ").strip()
    cust_id = int(cust_id_input) if cust_id_input else None

    # 2. Prescription check
    rx_id_input = input("Prescription ID (Required for Schedule H restricted drugs): ").strip()
    rx_id = int(rx_id_input) if rx_id_input else None

    # 3. Add items
    items = []
    print("\n--- Enter Items (type 'done' when finished) ---")
    while True:
        b_input = input("\nEnter Batch ID to dispense (or 'done'): ").strip()
        if b_input.lower() == 'done':
            break
        try:
            b_id = int(b_input)
            qty = int(input("Quantity to dispense: ").strip())
            items.append({'batch_id': b_id, 'quantity': qty})
            print(f"[+] Added Batch {b_id} x {qty} to cart.")
        except ValueError:
            print("[!] Invalid input. Try again.")

    if not items:
        print("[!] No items in cart. Transaction cancelled.")
        return

    discount = float(input("\nDiscount Amount (Rs) [0]: ").strip() or 0)
    pay_method = input("Payment Method (CASH/CARD/UPI/NET_BANKING) [CASH]: ").strip().upper() or "CASH"
    inv_no = f"BILL-{date.today().strftime('%Y%m%d')}-{abs(hash(str(items))) % 10000:04d}"

    try:
        sale_id, net_amt = models.process_sale_transaction(
            inv_no, cust_id, rx_id, items, payment_method=pay_method, discount=discount
        )
        print(f"\n[OK] SALE COMPLETED SUCCESSFULLY!")
        print(f"    Invoice Number : {inv_no}")
        print(f"    Sale ID        : {sale_id}")
        print(f"    Total Payable  : Rs.{net_amt:.2f}")
        print(f"    Payment Method : {pay_method}")
        print(f"    Inventory stock updated & movement audit logged.")
    except Exception as e:
        print(f"\n[FAIL] TRANSACTION REJECTED BY BUSINESS RULES: {e}")


def reports_menu():
    while True:
        clear_screen()
        print(">>> ANALYTICAL REPORTS & AUDIT DASHBOARD")
        print("1. Current Stock & Low Stock Reorder Alerts")
        print("2. Near-Expiry & Expired Batches Warning (<60 / <90 Days)")
        print("3. Fast-Moving Medicines (Sales Volume Leaderboard)")
        print("4. Gross Profit & Revenue Margins Analysis")
        print("5. Prescription Sales Compliance Audit")
        print("6. Supplier Purchases & Procurement Summary")
        print("7. Return to Main Menu")
        
        choice = input("\nSelect Report (1-7): ").strip()
        if choice == "1":
            data = models.report_current_stock()
            table = [[r["brand_name"], r["generic_name"], r["category_name"], r["current_stock"], r["reorder_level"], r["status"]] for r in data]
            print("\n" + tabulate(table, headers=["Brand", "Generic", "Category", "Stock", "Reorder Level", "Status"], tablefmt="grid"))
            input("\nPress Enter to continue...")
        elif choice == "2":
            data = models.report_near_expiry_batches()
            if not data:
                print("\n[OK] No batches near expiry within the next 90 days.")
            else:
                table = [[r["batch_number"], r["brand_name"], r["expiry_date"], r["current_stock"], f"Rs.{r['capital_at_risk']:.2f}", r["alert_status"]] for r in data]
                print("\n" + tabulate(table, headers=["Batch #", "Medicine", "Expiry Date", "Stock", "Capital at Risk", "Alert"], tablefmt="grid"))
            input("\nPress Enter to continue...")
        elif choice == "3":
            data = models.report_fast_moving_items()
            table = [[r["brand_name"], r["generic_name"], r["category_name"], r["total_units_sold"], f"Rs.{r['gross_revenue']:.2f}"] for r in data]
            print("\n" + tabulate(table, headers=["Brand", "Generic", "Category", "Units Sold", "Gross Revenue"], tablefmt="grid"))
            input("\nPress Enter to continue...")
        elif choice == "4":
            data = models.report_profit_analysis()
            table = [[r["brand_name"], r["category_name"], r["units_sold"], f"Rs.{r['total_cost']:.2f}", f"Rs.{r['total_revenue']:.2f}", f"Rs.{r['gross_profit']:.2f}", f"{r['margin_pct']}%"] for r in data]
            print("\n" + tabulate(table, headers=["Brand", "Category", "Qty Sold", "Cost (COGS)", "Revenue", "Gross Profit", "Margin %"], tablefmt="grid"))
            input("\nPress Enter to continue...")
        elif choice == "5":
            data = models.report_prescription_sales()
            table = [[r["invoice_number"], r["sale_date"], r["patient"], r["doctor_name"], r["medicine"], r["quantity"], f"Rs.{r['total_price']:.2f}"] for r in data]
            print("\n" + tabulate(table, headers=["Invoice #", "Date", "Patient", "Prescribing Doctor", "Medicine", "Qty", "Amount"], tablefmt="grid"))
            input("\nPress Enter to continue...")
        elif choice == "6":
            data = models.report_supplier_purchases()
            table = [[r["supplier_name"], r["gst_number"], r["phone"], r["total_orders"], f"Rs.{r['total_procurement_val']:.2f}", r["last_purchase_date"]] for r in data]
            print("\n" + tabulate(table, headers=["Supplier", "GST No.", "Phone", "Orders", "Total Value", "Last Order"], tablefmt="grid"))
            input("\nPress Enter to continue...")
        elif choice == "7":
            break


def main():
    init_database()
    while True:
        display_header()
        print("MAIN MENU:")
        print("1. View Medicines & Current Stock")
        print("2. Add New Medicine")
        print("3. View Batches & Inventory Details")
        print("4. Record Supplier Purchase & Batch Intake")
        print("5. Customer & Prescription Management")
        print("6. Point of Sale (POS) Billing & Dispensing")
        print("7. Analytical Reports & Performance Dashboard")
        print("8. Exit Application")

        choice = input("\nEnter your choice (1-8): ").strip()
        if choice == "1":
            view_medicines_menu()
        elif choice == "2":
            add_medicine_menu()
        elif choice == "3":
            view_batches_menu()
        elif choice == "4":
            purchase_intake_menu()
        elif choice == "5":
            customer_and_rx_menu()
        elif choice == "6":
            sales_billing_menu()
        elif choice == "7":
            reports_menu()
        elif choice == "8":
            print("\nThank you for using Pharmacy Management System. Exiting...")
            break
        else:
            print("\n[!] Invalid selection. Please enter a number between 1 and 8.")
        
        input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()
