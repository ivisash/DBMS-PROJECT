"""
Pharmacy Prescription and Medicine Stock Management System
Modern Graphical User Interface (Tkinter Desktop Application)
"""
import sys
import os
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure app path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import models
from app.db import init_database


class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacy Prescription & Medicine Stock Management System")
        self.geometry("1100x720")
        self.minsize(950, 600)

        # Initialize DB
        init_database()

        # Cart for billing tab
        self.cart_items = []

        # Configure Theme and Styles
        self._setup_styles()

        # Top Header Banner
        self._build_header()

        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Dashboard
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text=" Dashboard ")
        self._build_dashboard_tab()

        # Tab 2: Medicine Catalogue
        self.tab_medicines = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_medicines, text=" Medicines ")
        self._build_medicines_tab()

        # Tab 3: Batches & Stock
        self.tab_batches = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_batches, text=" Batches & Stock ")
        self._build_batches_tab()

        # Tab 4: Prescriptions & Customers
        self.tab_rx = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rx, text=" Prescriptions & Patients ")
        self._build_rx_tab()

        # Tab 5: POS Billing
        self.tab_billing = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_billing, text=" POS & Billing ")
        self._build_billing_tab()

        # Tab 6: Purchase Inward
        self.tab_purchases = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_purchases, text=" Inward Purchases ")
        self._build_purchases_tab()

        # Tab 7: Reports & Analytics
        self.tab_reports = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reports, text=" Reports & Analytics ")
        self._build_reports_tab()

        # Refresh dashboard on start
        self.refresh_dashboard()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Colors
        self.PRIMARY_COLOR = "#0056b3"
        self.BG_LIGHT = "#f8f9fa"
        self.ACCENT_WARN = "#dc3545"

        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#ffffff", background="#0d6efd")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10), foreground="#e0e0e0", background="#0d6efd")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground="#333333")
        style.configure("CardValue.TLabel", font=("Segoe UI", 20, "bold"), foreground="#0d6efd")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)

    def _build_header(self):
        header_frame = tk.Frame(self, bg="#0d6efd", height=65)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title = ttk.Label(header_frame, text="PHARMACY PRESCRIPTION & MEDICINE STOCK MANAGEMENT SYSTEM", style="Header.TLabel")
        title.pack(anchor="w", padx=20, pady=(10, 0))

        subtitle = ttk.Label(header_frame, text="Normalized Relational DBMS | 3NF Architecture | Business Rule & Expiry Enforcement", style="SubHeader.TLabel")
        subtitle.pack(anchor="w", padx=20, pady=(0, 10))

    # -------------------------------------------------------------------------
    # TAB 1: DASHBOARD
    # -------------------------------------------------------------------------
    def _build_dashboard_tab(self):
        container = ttk.Frame(self.tab_dashboard, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        cards_frame = ttk.Frame(container)
        cards_frame.pack(fill=tk.X, pady=(0, 20))

        # KPI 1: Total Medicines
        self.kpi_meds = self._create_kpi_card(cards_frame, "Total Medicines", "0", 0)
        # KPI 2: Reorder Alerts
        self.kpi_reorder = self._create_kpi_card(cards_frame, "Low Stock Reorders", "0", 1, color="#fd7e14")
        # KPI 3: Near Expiry Alerts
        self.kpi_expiry = self._create_kpi_card(cards_frame, "Near Expiry Batches", "0", 2, color="#dc3545")
        # KPI 4: Total Revenue
        self.kpi_rev = self._create_kpi_card(cards_frame, "Total Sales Revenue", "Rs.0.00", 3, color="#198754")

        # Quick Actions
        btn_box = ttk.LabelFrame(container, text="Quick Operations", padding=15)
        btn_box.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(btn_box, text="+ New Sale Invoice", style="Action.TButton", command=lambda: self.notebook.select(self.tab_billing)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_box, text="+ Record Purchase Shipment", style="Action.TButton", command=lambda: self.notebook.select(self.tab_purchases)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_box, text="View Expiry Alerts", style="Action.TButton", command=lambda: self._show_quick_report(2)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_box, text="Refresh Dashboard", command=self.refresh_dashboard).pack(side=tk.RIGHT, padx=10)

        # Overview Table: Near Expiry Batches preview
        lbl_frame = ttk.LabelFrame(container, text="Critical Attention: Batches Expiring in Next 90 Days", padding=10)
        lbl_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("batch_no", "medicine", "category", "expiry", "stock", "risk", "status")
        self.tree_dash_expiry = ttk.Treeview(lbl_frame, columns=cols, show="headings", height=8)
        self.tree_dash_expiry.heading("batch_no", text="Batch #")
        self.tree_dash_expiry.heading("medicine", text="Medicine Name")
        self.tree_dash_expiry.heading("category", text="Category")
        self.tree_dash_expiry.heading("expiry", text="Expiry Date")
        self.tree_dash_expiry.heading("stock", text="Current Stock")
        self.tree_dash_expiry.heading("risk", text="Capital at Risk")
        self.tree_dash_expiry.heading("status", text="Alert Status")

        self.tree_dash_expiry.column("batch_no", width=100)
        self.tree_dash_expiry.column("medicine", width=180)
        self.tree_dash_expiry.column("category", width=140)
        self.tree_dash_expiry.column("expiry", width=100)
        self.tree_dash_expiry.column("stock", width=90, anchor="center")
        self.tree_dash_expiry.column("risk", width=110, anchor="e")
        self.tree_dash_expiry.column("status", width=140)

        scrollbar = ttk.Scrollbar(lbl_frame, orient=tk.VERTICAL, command=self.tree_dash_expiry.yview)
        self.tree_dash_expiry.configure(yscroll=scrollbar.set)
        self.tree_dash_expiry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_kpi_card(self, parent, title, val, col_idx, color="#0d6efd"):
        card = tk.Frame(parent, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=12)
        card.grid(row=0, column=col_idx, padx=8, sticky="nsew")
        parent.grid_columnconfigure(col_idx, weight=1)

        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg="#6c757d", bg="#ffffff")
        lbl_t.pack(anchor="w")

        lbl_v = tk.Label(card, text=val, font=("Segoe UI", 18, "bold"), fg=color, bg="#ffffff")
        lbl_v.pack(anchor="w", pady=(5, 0))
        return lbl_v

    def refresh_dashboard(self):
        try:
            meds = models.list_medicines()
            self.kpi_meds.config(text=str(len(meds)))

            stock_data = models.report_current_stock()
            reorder_count = sum(1 for s in stock_data if s["status"] in ("REORDER NEEDED", "OUT OF STOCK"))
            self.kpi_reorder.config(text=str(reorder_count))

            expiry_data = models.report_near_expiry_batches()
            self.kpi_expiry.config(text=str(len(expiry_data)))

            profits = models.report_profit_analysis()
            total_rev = sum(p["total_revenue"] for p in profits)
            self.kpi_rev.config(text=f"Rs.{total_rev:,.2f}")

            # Populate preview
            for item in self.tree_dash_expiry.get_children():
                self.tree_dash_expiry.delete(item)
            for row in expiry_data:
                self.tree_dash_expiry.insert("", tk.END, values=(
                    row["batch_number"],
                    row["brand_name"],
                    row["category_name"],
                    row["expiry_date"],
                    row["current_stock"],
                    f"Rs.{row['capital_at_risk']:.2f}",
                    row["alert_status"]
                ))
        except Exception as e:
            print("Error refreshing dashboard:", e)

    def _show_quick_report(self, report_idx):
        self.notebook.select(self.tab_reports)
        self.report_selector.current(report_idx)
        self.load_selected_report()

    # -------------------------------------------------------------------------
    # TAB 2: MEDICINES
    # -------------------------------------------------------------------------
    def _build_medicines_tab(self):
        container = ttk.Frame(self.tab_medicines, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Top Toolbar
        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_bar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.ent_med_search = ttk.Entry(top_bar, width=25)
        self.ent_med_search.pack(side=tk.LEFT, padx=5)
        self.ent_med_search.bind("<Return>", lambda e: self.load_medicines())

        ttk.Button(top_bar, text="Search", command=self.load_medicines).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_bar, text="Show All", command=lambda: (self.ent_med_search.delete(0, tk.END), self.load_medicines())).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_bar, text="+ Add Medicine", style="Action.TButton", command=self._popup_add_medicine).pack(side=tk.RIGHT, padx=5)

        # Treeview
        cols = ("id", "brand", "generic", "category", "form", "strength", "stock", "reorder", "rx")
        self.tree_meds = ttk.Treeview(container, columns=cols, show="headings")
        self.tree_meds.heading("id", text="ID")
        self.tree_meds.heading("brand", text="Brand Name")
        self.tree_meds.heading("generic", text="Generic Active Molecule")
        self.tree_meds.heading("category", text="Therapeutic Category")
        self.tree_meds.heading("form", text="Form")
        self.tree_meds.heading("strength", text="Strength")
        self.tree_meds.heading("stock", text="Total Stock")
        self.tree_meds.heading("reorder", text="Reorder Lvl")
        self.tree_meds.heading("rx", text="Prescription Req")

        self.tree_meds.column("id", width=45, anchor="center")
        self.tree_meds.column("brand", width=140)
        self.tree_meds.column("generic", width=180)
        self.tree_meds.column("category", width=130)
        self.tree_meds.column("form", width=80)
        self.tree_meds.column("strength", width=80)
        self.tree_meds.column("stock", width=85, anchor="center")
        self.tree_meds.column("reorder", width=80, anchor="center")
        self.tree_meds.column("rx", width=110, anchor="center")

        sb = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree_meds.yview)
        self.tree_meds.configure(yscroll=sb.set)
        self.tree_meds.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_medicines()

    def load_medicines(self):
        query = self.ent_med_search.get().strip()
        data = models.list_medicines(query)
        for item in self.tree_meds.get_children():
            self.tree_meds.delete(item)
        for row in data:
            rx_lbl = "Required (Rx)" if row["requires_prescription"] else "OTC"
            self.tree_meds.insert("", tk.END, values=(
                row["medicine_id"],
                row["brand_name"],
                row["generic_name"],
                row["category_name"],
                row["dosage_form"],
                row["strength"],
                row["total_stock"],
                row["reorder_level"],
                rx_lbl
            ))

    def _popup_add_medicine(self):
        win = tk.Toplevel(self)
        win.title("Add New Medicine Record")
        win.geometry("450x480")
        win.grab_set()

        categories = models.list_categories()
        manufacturers = models.list_manufacturers()

        f = ttk.Frame(win, padding=20)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Brand Name (e.g. Paracetamol 500):").grid(row=0, column=0, sticky="w", pady=4)
        ent_brand = ttk.Entry(f, width=30)
        ent_brand.grid(row=0, column=1, pady=4)

        ttk.Label(f, text="Generic Chemical Name:").grid(row=1, column=0, sticky="w", pady=4)
        ent_generic = ttk.Entry(f, width=30)
        ent_generic.grid(row=1, column=1, pady=4)

        ttk.Label(f, text="Category:").grid(row=2, column=0, sticky="w", pady=4)
        cb_cat = ttk.Combobox(f, values=[f"{c['category_id']}: {c['category_name']}" for c in categories], width=28, state="readonly")
        if categories:
            cb_cat.current(0)
        cb_cat.grid(row=2, column=1, pady=4)

        ttk.Label(f, text="Manufacturer:").grid(row=3, column=0, sticky="w", pady=4)
        cb_mfr = ttk.Combobox(f, values=[f"{m['manufacturer_id']}: {m['company_name']}" for m in manufacturers], width=28, state="readonly")
        if manufacturers:
            cb_mfr.current(0)
        cb_mfr.grid(row=3, column=1, pady=4)

        ttk.Label(f, text="Dosage Form:").grid(row=4, column=0, sticky="w", pady=4)
        cb_form = ttk.Combobox(f, values=["Tablet", "Capsule", "Syrup", "Injection", "Ointment", "Drops"], width=28, state="readonly")
        cb_form.current(0)
        cb_form.grid(row=4, column=1, pady=4)

        ttk.Label(f, text="Strength (e.g. 500mg, 10ml):").grid(row=5, column=0, sticky="w", pady=4)
        ent_str = ttk.Entry(f, width=30)
        ent_str.grid(row=5, column=1, pady=4)

        ttk.Label(f, text="Reorder Level Threshold:").grid(row=6, column=0, sticky="w", pady=4)
        ent_reorder = ttk.Entry(f, width=30)
        ent_reorder.insert(0, "20")
        ent_reorder.grid(row=6, column=1, pady=4)

        rx_var = tk.IntVar(value=0)
        chk_rx = ttk.Checkbutton(f, text="Requires Prescription (Schedule H / Rx)", variable=rx_var)
        chk_rx.grid(row=7, column=0, columnspan=2, sticky="w", pady=10)

        def save():
            try:
                b = ent_brand.get().strip()
                g = ent_generic.get().strip()
                c_id = int(cb_cat.get().split(":")[0])
                m_id = int(cb_mfr.get().split(":")[0])
                fm = cb_form.get()
                st = ent_str.get().strip()
                ro = int(ent_reorder.get().strip())
                is_rx = rx_var.get()

                if not b or not g or not st:
                    messagebox.showerror("Validation Error", "All fields are required!")
                    return

                new_id = models.add_medicine(b, g, c_id, m_id, fm, st, ro, is_rx)
                messagebox.showinfo("Success", f"Medicine '{b}' added successfully with ID {new_id}!")
                win.destroy()
                self.load_medicines()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save medicine: {e}")

        ttk.Button(f, text="Save Medicine", style="Action.TButton", command=save).grid(row=8, column=0, columnspan=2, pady=15)

    # -------------------------------------------------------------------------
    # TAB 3: BATCHES & STOCK
    # -------------------------------------------------------------------------
    def _build_batches_tab(self):
        container = ttk.Frame(self.tab_batches, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        self.var_active_batches = tk.BooleanVar(value=True)
        chk = ttk.Checkbutton(top_bar, text="Show Available Stock Only (> 0)", variable=self.var_active_batches, command=self.load_batches)
        chk.pack(side=tk.LEFT)

        ttk.Button(top_bar, text="Refresh Batches", command=self.load_batches).pack(side=tk.RIGHT)

        cols = ("batch_id", "batch_no", "medicine", "form", "mfg", "expiry", "cost", "mrp", "stock", "rx")
        self.tree_batches = ttk.Treeview(container, columns=cols, show="headings")
        self.tree_batches.heading("batch_id", text="Batch ID")
        self.tree_batches.heading("batch_no", text="Batch #")
        self.tree_batches.heading("medicine", text="Medicine Name")
        self.tree_batches.heading("form", text="Dosage & Strength")
        self.tree_batches.heading("mfg", text="Mfg Date")
        self.tree_batches.heading("expiry", text="Expiry Date")
        self.tree_batches.heading("cost", text="Cost Rate (Rs)")
        self.tree_batches.heading("mrp", text="MRP / Sale (Rs)")
        self.tree_batches.heading("stock", text="Current Stock")
        self.tree_batches.heading("rx", text="Restricted (Rx)")

        self.tree_batches.column("batch_id", width=65, anchor="center")
        self.tree_batches.column("batch_no", width=100)
        self.tree_batches.column("medicine", width=160)
        self.tree_batches.column("form", width=120)
        self.tree_batches.column("mfg", width=95)
        self.tree_batches.column("expiry", width=95)
        self.tree_batches.column("cost", width=95, anchor="e")
        self.tree_batches.column("mrp", width=95, anchor="e")
        self.tree_batches.column("stock", width=95, anchor="center")
        self.tree_batches.column("rx", width=100, anchor="center")

        sb = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree_batches.yview)
        self.tree_batches.configure(yscroll=sb.set)
        self.tree_batches.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_batches()

    def load_batches(self):
        active_only = self.var_active_batches.get()
        data = models.list_batches(active_only=active_only)
        for item in self.tree_batches.get_children():
            self.tree_batches.delete(item)
        for r in data:
            self.tree_batches.insert("", tk.END, values=(
                r["batch_id"],
                r["batch_number"],
                r["brand_name"],
                f"{r['dosage_form']} ({r['strength']})",
                r["manufacture_date"],
                r["expiry_date"],
                f"Rs.{r['unit_cost_price']:.2f}",
                f"Rs.{r['unit_sale_price']:.2f}",
                r["current_stock"],
                "Yes (Rx)" if r["requires_prescription"] else "No (OTC)"
            ))

    # -------------------------------------------------------------------------
    # TAB 4: PRESCRIPTIONS & CUSTOMERS
    # -------------------------------------------------------------------------
    def _build_rx_tab(self):
        container = ttk.Frame(self.tab_rx, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        paned = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left pane: Customers
        f_left = ttk.LabelFrame(paned, text="Registered Customers", padding=10)
        paned.add(f_left, weight=1)

        btn_cust = ttk.Button(f_left, text="+ Register Customer", command=self._popup_add_customer)
        btn_cust.pack(anchor="w", pady=(0, 5))

        self.tree_cust = ttk.Treeview(f_left, columns=("id", "name", "phone"), show="headings", height=12)
        self.tree_cust.heading("id", text="ID")
        self.tree_cust.heading("name", text="Name")
        self.tree_cust.heading("phone", text="Phone")
        self.tree_cust.column("id", width=40, anchor="center")
        self.tree_cust.column("name", width=130)
        self.tree_cust.column("phone", width=110)
        self.tree_cust.pack(fill=tk.BOTH, expand=True)

        # Right pane: Prescriptions
        f_right = ttk.LabelFrame(paned, text="Prescriptions & Medical Records", padding=10)
        paned.add(f_right, weight=2)

        btn_rx = ttk.Button(f_right, text="+ Add Prescription", command=self._popup_add_prescription)
        btn_rx.pack(anchor="w", pady=(0, 5))

        cols = ("rx_id", "code", "patient", "doctor", "reg_no", "date", "notes")
        self.tree_rx_view = ttk.Treeview(f_right, columns=cols, show="headings", height=12)
        self.tree_rx_view.heading("rx_id", text="ID")
        self.tree_rx_view.heading("code", text="Rx Code")
        self.tree_rx_view.heading("patient", text="Patient Name")
        self.tree_rx_view.heading("doctor", text="Doctor")
        self.tree_rx_view.heading("reg_no", text="Reg No")
        self.tree_rx_view.heading("date", text="Issue Date")
        self.tree_rx_view.heading("notes", text="Clinical Notes")

        self.tree_rx_view.column("rx_id", width=40, anchor="center")
        self.tree_rx_view.column("code", width=95)
        self.tree_rx_view.column("patient", width=120)
        self.tree_rx_view.column("doctor", width=130)
        self.tree_rx_view.column("reg_no", width=90)
        self.tree_rx_view.column("date", width=85)
        self.tree_rx_view.column("notes", width=140)
        self.tree_rx_view.pack(fill=tk.BOTH, expand=True)

        self.load_customers_and_prescriptions()

    def load_customers_and_prescriptions(self):
        # Customers
        for i in self.tree_cust.get_children():
            self.tree_cust.delete(i)
        for c in models.list_customers():
            self.tree_cust.insert("", tk.END, values=(c["customer_id"], c["full_name"], c["phone_number"]))

        # Prescriptions
        for i in self.tree_rx_view.get_children():
            self.tree_rx_view.delete(i)
        for r in models.list_prescriptions():
            self.tree_rx_view.insert("", tk.END, values=(
                r["prescription_id"],
                r["prescription_code"],
                r["customer_name"],
                r["doctor_name"],
                r["doctor_reg_no"],
                r["issue_date"],
                r["notes"]
            ))

    def _popup_add_customer(self):
        win = tk.Toplevel(self)
        win.title("Register New Customer")
        win.geometry("400x320")
        f = ttk.Frame(win, padding=15)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Full Name:").pack(anchor="w")
        ent_name = ttk.Entry(f, width=35)
        ent_name.pack(fill=tk.X, pady=3)

        ttk.Label(f, text="Phone Number:").pack(anchor="w")
        ent_phone = ttk.Entry(f, width=35)
        ent_phone.pack(fill=tk.X, pady=3)

        ttk.Label(f, text="Email:").pack(anchor="w")
        ent_email = ttk.Entry(f, width=35)
        ent_email.pack(fill=tk.X, pady=3)

        ttk.Label(f, text="Address:").pack(anchor="w")
        ent_addr = ttk.Entry(f, width=35)
        ent_addr.pack(fill=tk.X, pady=3)

        def save():
            n = ent_name.get().strip()
            p = ent_phone.get().strip()
            if not n or not p:
                messagebox.showerror("Error", "Name and Phone are mandatory!")
                return
            try:
                models.add_customer(n, p, ent_email.get().strip(), "Male", ent_addr.get().strip())
                messagebox.showinfo("Success", f"Customer {n} registered!")
                win.destroy()
                self.load_customers_and_prescriptions()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(f, text="Register", style="Action.TButton", command=save).pack(pady=12)

    def _popup_add_prescription(self):
        win = tk.Toplevel(self)
        win.title("Add Doctor Prescription")
        win.geometry("460x420")
        f = ttk.Frame(win, padding=15)
        f.pack(fill=tk.BOTH, expand=True)

        custs = models.list_customers()
        ttk.Label(f, text="Select Patient:").grid(row=0, column=0, sticky="w", pady=4)
        cb_cust = ttk.Combobox(f, values=[f"{c['customer_id']}: {c['full_name']} ({c['phone_number']})" for c in custs], width=30, state="readonly")
        if custs:
            cb_cust.current(0)
        cb_cust.grid(row=0, column=1, pady=4)

        ttk.Label(f, text="Prescription Code:").grid(row=1, column=0, sticky="w", pady=4)
        ent_code = ttk.Entry(f, width=30)
        ent_code.insert(0, f"RX-{date.today().strftime('%Y')}-{abs(hash(str(date.today()))) % 1000:03d}")
        ent_code.grid(row=1, column=1, pady=4)

        ttk.Label(f, text="Doctor Name:").grid(row=2, column=0, sticky="w", pady=4)
        ent_doc = ttk.Entry(f, width=30)
        ent_doc.grid(row=2, column=1, pady=4)

        ttk.Label(f, text="Medical Council Reg No:").grid(row=3, column=0, sticky="w", pady=4)
        ent_reg = ttk.Entry(f, width=30)
        ent_reg.grid(row=3, column=1, pady=4)

        ttk.Label(f, text="Clinic / Hospital:").grid(row=4, column=0, sticky="w", pady=4)
        ent_cl = ttk.Entry(f, width=30)
        ent_cl.grid(row=4, column=1, pady=4)

        ttk.Label(f, text="Clinical Notes / Medicine:").grid(row=5, column=0, sticky="w", pady=4)
        ent_notes = ttk.Entry(f, width=30)
        ent_notes.grid(row=5, column=1, pady=4)

        def save():
            try:
                cid = int(cb_cust.get().split(":")[0])
                code = ent_code.get().strip()
                doc = ent_doc.get().strip()
                reg = ent_reg.get().strip()
                if not doc or not reg:
                    messagebox.showerror("Validation", "Doctor Name and Reg No are mandatory!")
                    return
                models.add_prescription(code, cid, doc, reg, ent_cl.get().strip(), date.today().isoformat(), ent_notes.get().strip())
                messagebox.showinfo("Success", f"Prescription {code} recorded!")
                win.destroy()
                self.load_customers_and_prescriptions()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(f, text="Save Prescription", style="Action.TButton", command=save).grid(row=6, column=0, columnspan=2, pady=15)

    # -------------------------------------------------------------------------
    # TAB 5: POS & BILLING
    # -------------------------------------------------------------------------
    def _build_billing_tab(self):
        container = ttk.Frame(self.tab_billing, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Header controls
        top_box = ttk.LabelFrame(container, text="Transaction Header", padding=10)
        top_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_box, text="Customer:").grid(row=0, column=0, sticky="w", padx=5)
        self.cb_bill_cust = ttk.Combobox(top_box, width=30, state="readonly")
        self.cb_bill_cust.grid(row=0, column=1, padx=5)

        ttk.Label(top_box, text="Prescription:").grid(row=0, column=2, sticky="w", padx=5)
        self.cb_bill_rx = ttk.Combobox(top_box, width=30, state="readonly")
        self.cb_bill_rx.grid(row=0, column=3, padx=5)

        ttk.Label(top_box, text="Payment Method:").grid(row=0, column=4, sticky="w", padx=5)
        self.cb_bill_pay = ttk.Combobox(top_box, values=["CASH", "UPI", "CARD", "NET_BANKING"], width=15, state="readonly")
        self.cb_bill_pay.current(0)
        self.cb_bill_pay.grid(row=0, column=5, padx=5)

        # Item Selector
        item_box = ttk.LabelFrame(container, text="Select Medicine & Batch", padding=10)
        item_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(item_box, text="Active Batch:").grid(row=0, column=0, sticky="w", padx=5)
        self.cb_bill_batch = ttk.Combobox(item_box, width=45, state="readonly")
        self.cb_bill_batch.grid(row=0, column=1, padx=5)

        ttk.Label(item_box, text="Quantity:").grid(row=0, column=2, sticky="w", padx=5)
        self.ent_bill_qty = ttk.Entry(item_box, width=10)
        self.ent_bill_qty.insert(0, "1")
        self.ent_bill_qty.grid(row=0, column=3, padx=5)

        ttk.Button(item_box, text="+ Add to Bill", style="Action.TButton", command=self._add_item_to_cart).grid(row=0, column=4, padx=10)
        ttk.Button(item_box, text="Refresh Lists", command=self.refresh_billing_selectors).grid(row=0, column=5, padx=5)

        # Cart Table
        cols = ("batch_id", "batch_no", "medicine", "exp", "qty", "rate", "total")
        self.tree_cart = ttk.Treeview(container, columns=cols, show="headings", height=8)
        self.tree_cart.heading("batch_id", text="ID")
        self.tree_cart.heading("batch_no", text="Batch #")
        self.tree_cart.heading("medicine", text="Medicine")
        self.tree_cart.heading("exp", text="Expiry")
        self.tree_cart.heading("qty", text="Quantity")
        self.tree_cart.heading("rate", text="Unit Rate (Rs)")
        self.tree_cart.heading("total", text="Total (Rs)")

        self.tree_cart.column("batch_id", width=40, anchor="center")
        self.tree_cart.column("batch_no", width=100)
        self.tree_cart.column("medicine", width=180)
        self.tree_cart.column("exp", width=100)
        self.tree_cart.column("qty", width=80, anchor="center")
        self.tree_cart.column("rate", width=100, anchor="e")
        self.tree_cart.column("total", width=110, anchor="e")
        self.tree_cart.pack(fill=tk.BOTH, expand=True, pady=5)

        # Checkout Summary & Action
        bot_frame = ttk.Frame(container)
        bot_frame.pack(fill=tk.X, pady=10)

        self.lbl_bill_summary = ttk.Label(bot_frame, text="Subtotal: Rs.0.00 | GST (5%): Rs.0.00 | Net Payable: Rs.0.00", font=("Segoe UI", 12, "bold"), foreground="#0d6efd")
        self.lbl_bill_summary.pack(side=tk.LEFT, padx=10)

        ttk.Button(bot_frame, text="Clear Cart", command=self._clear_cart).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bot_frame, text="CONFIRM & GENERATE BILL", style="Action.TButton", command=self._process_checkout).pack(side=tk.RIGHT, padx=10)

        self.refresh_billing_selectors()

    def refresh_billing_selectors(self):
        # Customers
        custs = models.list_customers()
        cust_vals = ["0: Walk-in Customer"] + [f"{c['customer_id']}: {c['full_name']} ({c['phone_number']})" for c in custs]
        self.cb_bill_cust["values"] = cust_vals
        self.cb_bill_cust.current(0)

        # Prescriptions
        rxs = models.list_prescriptions()
        rx_vals = ["0: None (OTC Sale)"] + [f"{r['prescription_id']}: {r['prescription_code']} - {r['doctor_name']} ({r['customer_name']})" for r in rxs]
        self.cb_bill_rx["values"] = rx_vals
        self.cb_bill_rx.current(0)

        # Batches
        batches = models.list_batches(active_only=True)
        batch_vals = [f"{b['batch_id']}: {b['brand_name']} [Lot:{b['batch_number']}] Stock:{b['current_stock']} MRP:Rs.{b['unit_sale_price']:.2f}" for b in batches]
        self.cb_bill_batch["values"] = batch_vals
        if batch_vals:
            self.cb_bill_batch.current(0)

    def _add_item_to_cart(self):
        if not self.cb_bill_batch.get():
            messagebox.showwarning("Warning", "Please select a medicine batch!")
            return
        try:
            b_id = int(self.cb_bill_batch.get().split(":")[0])
            qty = int(self.ent_bill_qty.get().strip())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero!")
                return

            # Fetch batch details
            batch_data = [b for b in models.list_batches(active_only=True) if b["batch_id"] == b_id]
            if not batch_data:
                messagebox.showerror("Error", "Selected batch is no longer available.")
                return
            b = batch_data[0]

            # Expiry validation
            if str(b["expiry_date"]) < date.today().isoformat():
                messagebox.showerror("CRITICAL ERROR", f"BATCH IS EXPIRED ({b['expiry_date']})!\nDispensation strictly prohibited by law.")
                return

            if b["current_stock"] < qty:
                messagebox.showerror("Stock Shortage", f"Batch only has {b['current_stock']} units available!")
                return

            total_val = qty * b["unit_sale_price"]
            self.cart_items.append({
                "batch_id": b_id,
                "batch_number": b["batch_number"],
                "medicine": b["brand_name"],
                "expiry": b["expiry_date"],
                "quantity": qty,
                "unit_price": b["unit_sale_price"],
                "line_total": total_val,
                "requires_prescription": b["requires_prescription"]
            })

            self._update_cart_tree()
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity!")

    def _update_cart_tree(self):
        for i in self.tree_cart.get_children():
            self.tree_cart.delete(i)
        subtotal = 0.0
        for item in self.cart_items:
            subtotal += item["line_total"]
            self.tree_cart.insert("", tk.END, values=(
                item["batch_id"],
                item["batch_number"],
                item["medicine"],
                item["expiry"],
                item["quantity"],
                f"Rs.{item['unit_price']:.2f}",
                f"Rs.{item['line_total']:.2f}"
            ))
        tax = round(subtotal * 0.05, 2)
        net = round(subtotal + tax, 2)
        self.lbl_bill_summary.config(text=f"Subtotal: Rs.{subtotal:.2f} | GST (5%): Rs.{tax:.2f} | Net Payable: Rs.{net:.2f}")

    def _clear_cart(self):
        self.cart_items.clear()
        self._update_cart_tree()

    def _process_checkout(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return

        cust_str = self.cb_bill_cust.get()
        cust_id = int(cust_str.split(":")[0]) if cust_str and not cust_str.startswith("0") else None

        rx_str = self.cb_bill_rx.get()
        rx_id = int(rx_str.split(":")[0]) if rx_str and not rx_str.startswith("0") else None

        # Check if restricted prescription drugs are present without Rx
        for item in self.cart_items:
            if item["requires_prescription"] and not rx_id:
                messagebox.showerror(
                    "Prescription Required",
                    f"'{item['medicine']}' is a restricted Schedule H medicine!\nA valid Prescription ID must be selected before billing."
                )
                return

        inv_number = f"BILL-{date.today().strftime('%Y%m%d')}-{abs(hash(str(self.cart_items))) % 10000:04d}"
        pay_method = self.cb_bill_pay.get()

        try:
            sale_id, net_amt = models.process_sale_transaction(
                inv_number, cust_id, rx_id, self.cart_items, payment_method=pay_method
            )
            messagebox.showinfo(
                "Billing Complete",
                f"INVOICE GENERATED SUCCESSFULLY!\n\nInvoice No: {inv_number}\nSale ID: {sale_id}\nTotal Paid: Rs.{net_amt:.2f}\nPayment Mode: {pay_method}\n\nInventory updated & movement logs saved."
            )
            self._clear_cart()
            self.refresh_billing_selectors()
            self.load_batches()
            self.load_medicines()
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Checkout Error", str(e))

    # -------------------------------------------------------------------------
    # TAB 6: PURCHASES
    # -------------------------------------------------------------------------
    def _build_purchases_tab(self):
        container = ttk.Frame(self.tab_purchases, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        box = ttk.LabelFrame(container, text="Inward Stock Entry (Purchase Order & Batch Lot Intake)", padding=15)
        box.pack(fill=tk.BOTH, expand=True)

        suppliers = models.list_suppliers()
        meds = models.list_medicines()

        ttk.Label(box, text="Supplier:").grid(row=0, column=0, sticky="w", pady=5)
        self.cb_p_supp = ttk.Combobox(box, values=[f"{s['supplier_id']}: {s['supplier_name']}" for s in suppliers], width=35, state="readonly")
        if suppliers:
            self.cb_p_supp.current(0)
        self.cb_p_supp.grid(row=0, column=1, pady=5)

        ttk.Label(box, text="Supplier Invoice Number:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_p_inv = ttk.Entry(box, width=35)
        self.ent_p_inv.insert(0, f"SUP-INV-{date.today().strftime('%Y%m%d')}-01")
        self.ent_p_inv.grid(row=1, column=1, pady=5)

        ttk.Label(box, text="Medicine:").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_p_med = ttk.Combobox(box, values=[f"{m['medicine_id']}: {m['brand_name']} ({m['strength']})" for m in meds], width=35, state="readonly")
        if meds:
            self.cb_p_med.current(0)
        self.cb_p_med.grid(row=2, column=1, pady=5)

        ttk.Label(box, text="Batch Lot Number:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_p_batch = ttk.Entry(box, width=35)
        self.ent_p_batch.grid(row=3, column=1, pady=5)

        ttk.Label(box, text="Manufacture Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_p_mfg = ttk.Entry(box, width=35)
        self.ent_p_mfg.insert(0, date.today().isoformat())
        self.ent_p_mfg.grid(row=4, column=1, pady=5)

        ttk.Label(box, text="Expiry Date (YYYY-MM-DD):").grid(row=5, column=0, sticky="w", pady=5)
        self.ent_p_exp = ttk.Entry(box, width=35)
        self.ent_p_exp.grid(row=5, column=1, pady=5)

        ttk.Label(box, text="Unit Cost Price (Rs):").grid(row=6, column=0, sticky="w", pady=5)
        self.ent_p_cost = ttk.Entry(box, width=35)
        self.ent_p_cost.grid(row=6, column=1, pady=5)

        ttk.Label(box, text="Unit Sale / MRP Price (Rs):").grid(row=7, column=0, sticky="w", pady=5)
        self.ent_p_mrp = ttk.Entry(box, width=35)
        self.ent_p_mrp.grid(row=7, column=1, pady=5)

        ttk.Label(box, text="Inward Quantity (Units):").grid(row=8, column=0, sticky="w", pady=5)
        self.ent_p_qty = ttk.Entry(box, width=35)
        self.ent_p_qty.grid(row=8, column=1, pady=5)

        def save_purchase():
            try:
                supp_id = int(self.cb_p_supp.get().split(":")[0])
                inv = self.ent_p_inv.get().strip()
                med_id = int(self.cb_p_med.get().split(":")[0])
                b_no = self.ent_p_batch.get().strip()
                mfg = self.ent_p_mfg.get().strip()
                exp = self.ent_p_exp.get().strip()
                cost = float(self.ent_p_cost.get().strip())
                mrp = float(self.ent_p_mrp.get().strip())
                qty = int(self.ent_p_qty.get().strip())

                if not b_no or not exp:
                    messagebox.showerror("Error", "Batch number and expiry date are required!")
                    return
                if mrp < cost:
                    messagebox.showerror("Validation", "Sale MRP must be greater than or equal to Cost Price!")
                    return

                p_id, b_id = models.add_purchase_and_batch(
                    inv, supp_id, date.today().isoformat(), med_id, b_no, mfg, exp, cost, mrp, qty
                )
                messagebox.showinfo("Success", f"Stock Received!\nPurchase ID: {p_id}\nNew Batch ID: {b_id}\nAdded {qty} units.")
                self.load_batches()
                self.load_medicines()
                self.refresh_dashboard()
                self.refresh_billing_selectors()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(box, text="Receive & Inward Stock", style="Action.TButton", command=save_purchase).grid(row=9, column=0, columnspan=2, pady=15)

    # -------------------------------------------------------------------------
    # TAB 7: REPORTS & ANALYTICS
    # -------------------------------------------------------------------------
    def _build_reports_tab(self):
        container = ttk.Frame(self.tab_reports, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_bar, text="Select Analytics Report:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        self.report_selector = ttk.Combobox(
            top_bar,
            values=[
                "1. Current Stock & Reorder Thresholds",
                "2. Near-Expiry & Expired Batches Warning (<90 Days)",
                "3. Fast-Moving Medicines (Volume Ranking)",
                "4. Gross Profit & Revenue Margins",
                "5. Prescription Compliance Sales Audit",
                "6. Supplier Procurement Summaries"
            ],
            width=45,
            state="readonly"
        )
        self.report_selector.current(0)
        self.report_selector.pack(side=tk.LEFT, padx=5)

        ttk.Button(top_bar, text="Generate Report", style="Action.TButton", command=self.load_selected_report).pack(side=tk.LEFT, padx=10)

        # Dynamic Treeview for reports
        self.tree_report = ttk.Treeview(container, show="headings")
        sb_y = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree_report.yview)
        sb_x = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.tree_report.xview)
        self.tree_report.configure(yscroll=sb_y.set, xscroll=sb_x.set)

        self.tree_report.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)
        sb_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_selected_report()

    def load_selected_report(self):
        idx = self.report_selector.current()

        # Reset Treeview columns
        for item in self.tree_report.get_children():
            self.tree_report.delete(item)

        if idx == 0:
            # Current stock
            cols = ("brand", "generic", "category", "form", "stock", "reorder", "status")
            self.tree_report["columns"] = cols
            self.tree_report.heading("brand", text="Brand Name")
            self.tree_report.heading("generic", text="Generic Molecule")
            self.tree_report.heading("category", text="Category")
            self.tree_report.heading("form", text="Form")
            self.tree_report.heading("stock", text="Stock")
            self.tree_report.heading("reorder", text="Reorder Level")
            self.tree_report.heading("status", text="Stock Status")

            for r in models.report_current_stock():
                self.tree_report.insert("", tk.END, values=(
                    r["brand_name"], r["generic_name"], r["category_name"], f"{r['dosage_form']} ({r['strength']})",
                    r["current_stock"], r["reorder_level"], r["status"]
                ))

        elif idx == 1:
            # Near Expiry
            cols = ("batch_no", "medicine", "category", "expiry", "stock", "risk", "status")
            self.tree_report["columns"] = cols
            self.tree_report.heading("batch_no", text="Batch #")
            self.tree_report.heading("medicine", text="Medicine")
            self.tree_report.heading("category", text="Category")
            self.tree_report.heading("expiry", text="Expiry Date")
            self.tree_report.heading("stock", text="Stock Units")
            self.tree_report.heading("risk", text="Capital at Risk")
            self.tree_report.heading("status", text="Alert Level")

            for r in models.report_near_expiry_batches():
                self.tree_report.insert("", tk.END, values=(
                    r["batch_number"], r["brand_name"], r["category_name"], r["expiry_date"],
                    r["current_stock"], f"Rs.{r['capital_at_risk']:.2f}", r["alert_status"]
                ))

        elif idx == 2:
            # Fast Moving
            cols = ("brand", "generic", "category", "sold", "revenue")
            self.tree_report["columns"] = cols
            self.tree_report.heading("brand", text="Brand Name")
            self.tree_report.heading("generic", text="Generic Molecule")
            self.tree_report.heading("category", text="Category")
            self.tree_report.heading("sold", text="Units Sold")
            self.tree_report.heading("revenue", text="Gross Revenue")

            for r in models.report_fast_moving_items():
                self.tree_report.insert("", tk.END, values=(
                    r["brand_name"], r["generic_name"], r["category_name"],
                    r["total_units_sold"], f"Rs.{r['gross_revenue']:.2f}"
                ))

        elif idx == 3:
            # Profit Analysis
            cols = ("brand", "category", "qty", "cogs", "rev", "profit", "margin")
            self.tree_report["columns"] = cols
            self.tree_report.heading("brand", text="Brand Name")
            self.tree_report.heading("category", text="Category")
            self.tree_report.heading("qty", text="Units Sold")
            self.tree_report.heading("cogs", text="Cost of Goods (Rs)")
            self.tree_report.heading("rev", text="Total Revenue (Rs)")
            self.tree_report.heading("profit", text="Gross Profit (Rs)")
            self.tree_report.heading("margin", text="Profit Margin %")

            for r in models.report_profit_analysis():
                self.tree_report.insert("", tk.END, values=(
                    r["brand_name"], r["category_name"], r["units_sold"],
                    f"Rs.{r['total_cost']:.2f}", f"Rs.{r['total_revenue']:.2f}",
                    f"Rs.{r['gross_profit']:.2f}", f"{r['margin_pct']}%"
                ))

        elif idx == 4:
            # Prescription Sales Audit
            cols = ("inv", "date", "patient", "code", "doctor", "medicine", "qty", "total")
            self.tree_report["columns"] = cols
            self.tree_report.heading("inv", text="Invoice #")
            self.tree_report.heading("date", text="Date")
            self.tree_report.heading("patient", text="Patient")
            self.tree_report.heading("code", text="Rx Code")
            self.tree_report.heading("doctor", text="Prescribing Doctor")
            self.tree_report.heading("medicine", text="Medicine Dispensed")
            self.tree_report.heading("qty", text="Quantity")
            self.tree_report.heading("total", text="Amount (Rs)")

            for r in models.report_prescription_sales():
                self.tree_report.insert("", tk.END, values=(
                    r["invoice_number"], r["sale_date"], r["patient"], r["prescription_code"],
                    r["doctor_name"], r["medicine"], r["quantity"], f"Rs.{r['total_price']:.2f}"
                ))

        elif idx == 5:
            # Supplier Purchases
            cols = ("supplier", "gst", "phone", "orders", "total_val", "last_order")
            self.tree_report["columns"] = cols
            self.tree_report.heading("supplier", text="Supplier Name")
            self.tree_report.heading("gst", text="GST Number")
            self.tree_report.heading("phone", text="Phone")
            self.tree_report.heading("orders", text="Orders Count")
            self.tree_report.heading("total_val", text="Procurement Value (Rs)")
            self.tree_report.heading("last_order", text="Last Order Date")

            for r in models.report_supplier_purchases():
                self.tree_report.insert("", tk.END, values=(
                    r["supplier_name"], r["gst_number"], r["phone"],
                    r["total_orders"], f"Rs.{r['total_procurement_val']:.2f}", r["last_purchase_date"]
                ))


def run_gui():
    app = PharmacyApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
