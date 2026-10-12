# REVIEW 3: Final Project Report & Viva-Voce Guide
## Project 04: Pharmacy Prescription and Medicine Stock Management System
**Course:** Database Management Systems (PBL)  
**Evaluation:** Review 3 (Week 16 — 5 Marks)  

---

### 1. Executive Summary & Architecture
The Pharmacy Prescription and Medicine Stock Management System is an end-to-end relational database solution designed to eliminate manual pharmacy vulnerabilities such as dispensing expired drugs, stock shortages, prescription non-compliance, and inaccurate financial tracking.

```
+-----------------------------------------------------------------------------------+
|                            APPLICATION LAYER (FRONTEND)                           |
|       - Tkinter Desktop GUI (gui.py)   /   Interactive Terminal CLI (cli.py)      |
+-----------------------------------------------------------------------------------+
                                        |  SQL Queries & Transactions
                                        v
+-----------------------------------------------------------------------------------+
|                        BUSINESS LOGIC LAYER (models.py)                           |
|       - Expiry Validation (expiry_date >= CURDATE())                              |
|       - Prescription Enforcement (requires_prescription = 1 => Rx Mandatory)     |
|       - Atomic Stock Deduction & Movement Audit Trail Logging                     |
+-----------------------------------------------------------------------------------+
                                        |  DB API (SQLite3 / MySQL Connector)
                                        v
+-----------------------------------------------------------------------------------+
|                     DATABASE ENGINE (MySQL 8.0 / SQLite 3)                        |
|       - 12 Relational Tables (Normalized up to 3NF)                               |
|       - Integrity Constraints: PK, FK, UNIQUE, NOT NULL, CHECK, Triggers          |
|       - Reusable Views for Real-Time Analytical & Inventory Reports               |
+-----------------------------------------------------------------------------------+
```

---

### 2. Functional Modules & Implementation Details

#### 2.1 Medicine & Category Management (CRUD)
- Categorizes medicines by pharmacological therapeutic classification (Antibiotics, Antidiabetics, Analgesics, etc.).
- Maintains brand names, generic formulations, dosage forms, strength, and reorder levels.
- Flags Schedule H restricted drugs with `requires_prescription = 1`.

#### 2.2 Inward Purchase & Batch Intake
- Integrates supplier invoices with batch intake.
- Records `batch_number`, `manufacture_date`, `expiry_date`, purchase cost, and selling MRP.
- Ensures atomic updates: inserting a purchase order automatically provisions the batch lot and registers an inward stock movement (`PURCHASE_IN`).

#### 2.3 Prescription Management
- Maintains doctor credentials (name, council registration number, clinic/hospital), patient ID, and prescription date.
- Restricts dispensing of controlled antibiotics and diabetic medications unless linked to a valid prescription.

#### 2.4 Point of Sale (POS) Billing & Dispensing Engine
- Handles multi-item transactions.
- Pre-dispensation checks:
  1. **Expiry Check:** Evaluates whether `batches.expiry_date >= CURDATE()`. Completely aborts checkout if an expired batch is selected.
  2. **Quantity Verification:** Verifies `batches.current_stock >= requested_quantity`.
  3. **Prescription Rule:** Validates prescription association for restricted drugs.
- Automatically computes subtotal, itemized line totals, 5% pharmaceutical GST, and net payable.
- Atomically decrements batch stock and records a `SALE_OUT` audit movement.

#### 2.5 Real-Time Analytical Reporting & Business Views
1. **Current Stock & Reorder Report (`view_current_stock`):** Aggregates total units on hand across active batches and marks medicines falling below reorder threshold.
2. **Near-Expiry Warning (`view_near_expiry_batches`):** Classifies inventory expiring within 30, 60, or 90 days, calculating total capital at risk.
3. **Supplier Purchase Summary (`view_supplier_purchases`):** Displays procurement volume, supplier invoices, and total purchase expenditure.
4. **Prescription Compliance Audit (`view_prescription_sales`):** Provides a regulatory audit log linking dispensed drugs to prescribing physicians.
5. **Fast-Moving Medicines (`view_fast_moving_items`):** Ranks medications by units sold and gross sales frequency.
6. **Gross Profit Margin Analysis (`view_profit_analysis`):** Calculates gross margin:
   $$\text{Gross Profit} = \sum (\text{Selling Price} - \text{Cost Price}) \times \text{Units Sold}$$
   $$\text{Profit Margin \%} = \frac{\text{Gross Profit}}{\text{Total Revenue}} \times 100$$

---

### 3. Comprehensive Viva-Voce Preparation Q&A

#### Q1: Why is batch-level tracking necessary instead of tracking stock directly on the medicines table?
**Answer:** A single medicine (e.g., Augmentin 625) is produced across multiple manufacturing lots over time. Each lot has a distinct batch number, manufacture date, expiry date, and often different purchase costs. If stock were stored as a single number in the `medicines` table, it would be impossible to identify which physical pills are about to expire, or calculate accurate cost of goods sold (COGS). Tracking inventory in a separate `batches` table preserves individual lot integrity and enables FEFO (First-Expired, First-Out) inventory dispatch.

#### Q2: How does your database schema achieve Third Normal Form (3NF)?
**Answer:** 
1. **1NF:** All attribute values are atomic; no repeating groups exist. Multi-item sales are split into individual line records in `sale_items`.
2. **2NF:** All non-key attributes are fully functionally dependent on candidate keys. No partial dependencies exist. For example, batch details (`expiry_date`, `unit_cost_price`) are decoupled from sale transaction details.
3. **3NF:** No non-key attribute is transitively dependent on a primary key ($X \rightarrow Y$ and $Y \rightarrow Z$). For instance, manufacturer name and contact details depend on `manufacturer_id`, which is a distinct entity referenced by `medicine_id` via a foreign key, rather than embedding manufacturer data directly inside `medicines`.

#### Q3: How do you enforce that expired medicines are never sold?
**Answer:** We enforce this at two layers for defense-in-depth:
- **Database Layer (Trigger):** In MySQL, a `BEFORE INSERT ON sale_items` trigger compares `batches.expiry_date < CURDATE()`. If expired, it triggers `SIGNAL SQLSTATE '45000'` with a fatal error message, rolling back the transaction.
- **Application Layer:** The Python models (`process_sale_transaction`) inspect batch expiry before building the cart and reject any expired batch with a clear error prompt.

#### Q4: What happens if two customers buy the same batch concurrently? How is concurrency handled?
**Answer:** All stock deductions and invoice creations are wrapped inside ACID database transactions (`conn.commit()` and `conn.rollback()`). When the first sale executes, the relational engine locks the relevant row in the `batches` table. If the remaining quantity is less than requested by the concurrent transaction, the constraint check or trigger raises an error and rolls back the second transaction, preventing negative stock.

#### Q5: What is the purpose of the `stock_movements` table?
**Answer:** The `stock_movements` table is an immutable audit log. Whenever stock is added (via purchase), removed (via sale), returned, or written off due to expiry, a record is added with the movement type, quantity, timestamp, and reference ID. This provides complete forensic auditability for stock reconciliation.

#### Q6: Which indexes did you create and why?
**Answer:**
- `medicines(brand_name)` and `medicines(generic_name)`: Pharmacists frequently search for medicines by brand or generic compound.
- `batches(expiry_date)`: Used heavily by daily expiry warning views and batch rotation routines.
- `batches(current_stock)`: Speeds up queries filtering available inventory (`current_stock > 0`).
- `sales(sale_date)`: Accelerates sales reporting across date ranges.
- `customers(phone_number)`: Enables instant customer identification at the point of billing.
