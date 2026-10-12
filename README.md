# Pharmacy Prescription and Medicine Stock Management System
**Course:** Database Management Systems (PBL)  
**Project Topic 04**  

---

## 📌 Project Overview
An end-to-end relational database management system (RDBMS) paired with an interactive Python desktop application (Tkinter GUI & CLI) to manage retail pharmacy operations, batch-wise inventory, expiry dates, doctor prescriptions, customer billing, and analytics.

---

## 📁 Repository Structure
```
pharmacy_dbms/
├── database/
│   ├── 01_schema.sql             # MySQL 8.0 DDL scripts (constraints, triggers, indexes)
│   ├── 02_seed_data.sql          # Realistic pharmaceutical sample data
│   ├── 03_queries_and_views.sql  # Complex queries, views, profit & stock reports
│   └── 04_schema_sqlite.sql      # Portable SQLite schema & seed data
├── docs/
│   ├── REVIEW_1_CONCEPTUAL_DESIGN.md # Review 1: ER diagram, entities, relational schema
│   ├── REVIEW_2_NORMALIZATION_DDL.md  # Review 2: 3NF normalization, FDs, data dictionary
│   └── REVIEW_3_FINAL_REPORT.md       # Review 3: Final report & Viva-Voce Q&A
├── app/
│   ├── config.py                 # Configuration settings (SQLite / MySQL)
│   ├── db.py                     # Database connection & execution engine
│   ├── models.py                 # Business logic, validation, reports
│   ├── cli.py                    # Interactive terminal CLI application
│   └── gui.py                    # Modern Tkinter desktop GUI application
├── pharmacy.db                   # Auto-generated embedded database (ready to run)
└── README.md                     # Setup and usage guide
```

---

## 🚀 Quick Start (Running the Application)

### Option 1: Modern Desktop GUI Application (Recommended for Demonstration)
Run the following command in PowerShell:
```powershell
cd C:\Users\games\.gemini\antigravity\scratch\pharmacy_dbms
python -m app.gui
```
- Opens a clean desktop GUI with tabs for **Dashboard**, **Medicines**, **Batches & Stock**, **Prescriptions**, **POS & Billing**, **Purchases**, and **Reports & Analytics**.

### Option 2: Interactive Terminal CLI
Run the following command:
```powershell
cd C:\Users\games\.gemini\antigravity\scratch\pharmacy_dbms
python -m app.cli
```

---

## 🗄️ Running on MySQL Server 8.0
1. Open MySQL Workbench or MySQL Command Line Client.
2. Execute the scripts in sequence:
   ```sql
   SOURCE database/01_schema.sql;
   SOURCE database/02_seed_data.sql;
   SOURCE database/03_queries_and_views.sql;
   ```
3. To connect the Python application to your MySQL instance, set the environment variable:
   ```powershell
   $env:PHARMACY_DB_ENGINE = "mysql"
   $env:MYSQL_PASSWORD = "your_mysql_root_password"
   ```

---

## 📊 Evaluation Deliverables Checklist

### Review 1 (Week 7 — 5 Marks)
- [x] Problem identification, scope, and objectives (`docs/REVIEW_1_CONCEPTUAL_DESIGN.md`)
- [x] Entity-Relationship (ER) diagram with 12 principal entities
- [x] Initial relational schema with primary and foreign keys

### Review 2 (Week 11 — 5 Marks)
- [x] Normalization proofs up to 3NF with Functional Dependencies (`docs/REVIEW_2_NORMALIZATION_DDL.md`)
- [x] Data Dictionary covering all tables, columns, data types, and constraints
- [x] DDL Scripts with constraints (`database/01_schema.sql`)
- [x] SQL queries and views for Current Stock, Near Expiry, Supplier Purchases, Fast-Moving Items, and Gross Profit (`database/03_queries_and_views.sql`)

### Review 3 (Week 16 — 5 Marks)
- [x] Working Python application (`app/gui.py` and `app/cli.py`)
- [x] Validation rules (preventing expired sales, stock limit enforcement, prescription checks)
- [x] Final project report and complete Viva-Voce preparation Q&A (`docs/REVIEW_3_FINAL_REPORT.md`)
