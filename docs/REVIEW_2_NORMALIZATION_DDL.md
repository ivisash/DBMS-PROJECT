# REVIEW 2: Database Normalization (3NF), DDL Constraints, and SQL Queries
## Project 04: Pharmacy Prescription and Medicine Stock Management System
**Course:** Database Management Systems (PBL)  
**Evaluation:** Review 2 (Week 11 — 5 Marks)  

---

### 1. Functional Dependencies & Normalization up to 3NF

To eliminate update, insertion, and deletion anomalies and avoid data redundancy, the pharmacy database schema is rigorously decomposed and normalized to Third Normal Form (3NF).

#### 1.1 Unnormalized Form (UNF) Representation
An unnormalized pharmacy record typically bundles medicine, manufacturer, supplier, batch, customer, prescription, and sale line items into a single flat structure:
$$\text{UNF}(\text{InvoiceNo}, \text{SaleDate}, \text{CustID}, \text{CustName}, \text{CustPhone}, \text{DocName}, \text{DocReg}, \text{MedID}, \text{BrandName}, \text{GenericName}, \text{CatName}, \text{MfrName}, \text{MfrPhone}, \text{BatchNo}, \text{ExpDate}, \text{Qty}, \text{UnitPrice}, \text{TotalPrice}, \text{SupplierName}, \dots)$$

- **Anomalies in UNF:**
  - *Redundancy:* Manufacturer and supplier details repeated on every line item.
  - *Insertion Anomaly:* Cannot record a new medicine unless it has an active batch and sale.
  - *Deletion Anomaly:* Deleting a sale bill could delete the only record of a customer or medicine.
  - *Update Anomaly:* Updating a supplier's phone requires modifying thousands of past rows.

---

#### 1.2 First Normal Form (1NF)
> **Definition:** A relation is in 1NF if and only if all attribute values are atomic (no repeating groups, multi-valued attributes, or nested tables), and each table has a defined Primary Key.

- Multi-item sales are split into individual rows.
- Multi-valued attributes like compound address/contact fields are segregated into atomic domains.
- Repeating bill lines are decomposed into `sales` and `sale_items`.

---

#### 1.3 Second Normal Form (2NF)
> **Definition:** A relation is in 2NF if it is in 1NF and **no non-prime attribute is partially dependent** on any candidate key (no Partial Dependency). All non-key attributes must be fully functionally dependent on the entire primary key.

In a composite key relation like `SaleItem(sale_id, batch_id, quantity, unit_price, sale_date, customer_id)`:
- $\text{sale\_id}, \text{batch\_id} \rightarrow \text{quantity}$ (Full dependency)
- $\text{sale\_id} \rightarrow \text{sale\_date}, \text{customer\_id}$ (**Partial dependency!**)
- $\text{batch\_id} \rightarrow \text{expiry\_date}, \text{medicine\_id}$ (**Partial dependency!**)

**Decomposition to achieve 2NF:**
1. $\text{sales}(\underline{\text{sale\_id}}, \text{invoice\_number}, \text{customer\_id}, \text{prescription\_id}, \text{sale\_date}, \text{net\_amount}, \dots)$
2. $\text{sale\_items}(\underline{\text{sale\_item\_id}}, \text{sale\_id}, \text{batch\_id}, \text{quantity}, \text{unit\_price}, \text{total\_price})$
3. $\text{batches}(\underline{\text{batch\_id}}, \text{batch\_number}, \text{medicine\_id}, \text{purchase\_id}, \text{expiry\_date}, \dots)$

Now, every non-key attribute depends on the full primary key.

---

#### 1.4 Third Normal Form (3NF)
> **Definition:** A relation is in 3NF if it is in 2NF and **no non-prime attribute is transitively dependent** on a candidate key ($X \rightarrow Y$ and $Y \rightarrow Z \implies X \rightarrow Z$). Non-key attributes must depend *only* on the key, the whole key, and nothing but the key.

Consider `medicines(medicine_id, brand_name, category_id, category_name, category_desc, manufacturer_id, company_name)`:
- $\text{medicine\_id} \rightarrow \text{category\_id}$
- $\text{category\_id} \rightarrow \text{category\_name}, \text{description}$ (**Transitive Dependency!**)
- $\text{medicine\_id} \rightarrow \text{manufacturer\_id}$
- $\text{manufacturer\_id} \rightarrow \text{company\_name}, \text{contact\_email}$ (**Transitive Dependency!**)

**Decomposition to achieve 3NF:**
1. Separate `categories` table: $\underline{\text{category\_id}} \rightarrow \text{category\_name}, \text{description}$
2. Separate `manufacturers` table: $\underline{\text{manufacturer\_id}} \rightarrow \text{company\_name}, \text{contact\_email}, \text{phone}$
3. Refined `medicines` table: $\underline{\text{medicine\_id}} \rightarrow \text{brand\_name}, \text{generic\_name}, \text{category\_id}, \text{manufacturer\_id}, \dots$

Consider `sales(sale_id, customer_id, customer_name, customer_phone)`:
- $\text{sale\_id} \rightarrow \text{customer\_id} \rightarrow \text{customer\_name}, \text{customer\_phone}$ (**Transitive Dependency!**)
- Resolved by maintaining a distinct `customers` table.

**Conclusion:** All 12 tables in our relational schema satisfy 3NF.

---

### 2. Concise Data Dictionary

| Table Name | Column Name | Data Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`categories`** | `category_id` | INT | PK, AUTO_INCREMENT | Unique identifier for category |
| | `category_name` | VARCHAR(60) | NOT NULL, UNIQUE | Name (e.g. Antibiotic, Analgesic) |
| | `description` | VARCHAR(255) | NULL | Description of category |
| **`manufacturers`** | `manufacturer_id`| INT | PK, AUTO_INCREMENT | Unique identifier for manufacturer |
| | `company_name` | VARCHAR(100) | NOT NULL, UNIQUE | Name of pharmaceutical company |
| | `contact_email` | VARCHAR(100) | NULL | Contact email |
| | `phone` | VARCHAR(20) | NULL | Contact phone number |
| **`suppliers`** | `supplier_id` | INT | PK, AUTO_INCREMENT | Unique identifier for supplier |
| | `supplier_name` | VARCHAR(100) | NOT NULL | Distributor / Supplier firm name |
| | `gst_number` | VARCHAR(20) | UNIQUE, NOT NULL | Tax / GST registration number |
| | `phone` | VARCHAR(20) | NOT NULL | Contact number |
| **`medicines`** | `medicine_id` | INT | PK, AUTO_INCREMENT | Unique identifier for medicine |
| | `brand_name` | VARCHAR(100) | NOT NULL | Commercial brand name (e.g., Augmentin 625) |
| | `generic_name` | VARCHAR(100) | NOT NULL | Active ingredient (e.g., Amoxicillin + Clavulanate) |
| | `category_id` | INT | FK $\rightarrow$ `categories` | Category link |
| | `manufacturer_id`| INT | FK $\rightarrow$ `manufacturers` | Manufacturer link |
| | `dosage_form` | ENUM/VARCHAR | CHECK in ('Tablet','Capsule','Syrup','Injection','Ointment') | Formulation type |
| | `strength` | VARCHAR(50) | NOT NULL | e.g. "500mg", "10ml" |
| | `reorder_level`| INT | DEFAULT 20, CHECK >= 0 | Minimum safe inventory threshold |
| | `requires_prescription`| TINYINT(1)| DEFAULT 0 | 1 = Restricted Schedule H / Rx drug |
| **`purchases`** | `purchase_id` | INT | PK, AUTO_INCREMENT | Unique purchase order ID |
| | `invoice_number`| VARCHAR(50) | UNIQUE, NOT NULL | Supplier invoice/bill number |
| | `supplier_id` | INT | FK $\rightarrow$ `suppliers` | Supplier reference |
| | `purchase_date`| DATE | NOT NULL | Inward date |
| | `total_amount` | DECIMAL(10,2)| NOT NULL, CHECK >= 0 | Total invoice amount |
| **`batches`** | `batch_id` | INT | PK, AUTO_INCREMENT | Internal batch tracking ID |
| | `batch_number` | VARCHAR(50) | NOT NULL | Manufacturer batch lot number |
| | `medicine_id` | INT | FK $\rightarrow$ `medicines` | Medicine link |
| | `purchase_id` | INT | FK $\rightarrow$ `purchases` | Purchase reference |
| | `manufacture_date`| DATE | NOT NULL | Date of production |
| | `expiry_date` | DATE | NOT NULL, CHECK > mfg | Date of expiry |
| | `unit_cost_price`| DECIMAL(10,2)| NOT NULL, CHECK > 0 | Purchase rate per unit |
| | `unit_sale_price`| DECIMAL(10,2)| NOT NULL, CHECK >= cost | MRP / Retail rate per unit |
| | `initial_quantity`| INT | NOT NULL, CHECK > 0 | Inward quantity received |
| | `current_stock` | INT | NOT NULL, CHECK >= 0 | Remaining stock in pharmacy |
| **`customers`** | `customer_id` | INT | PK, AUTO_INCREMENT | Unique customer ID |
| | `full_name` | VARCHAR(100) | NOT NULL | Customer's name |
| | `phone_number` | VARCHAR(20) | UNIQUE, NOT NULL | Mobile number |
| **`prescriptions`**| `prescription_id`| INT | PK, AUTO_INCREMENT | Unique prescription ID |
| | `prescription_code`| VARCHAR(50)| UNIQUE, NOT NULL | Rx code / identifier |
| | `customer_id` | INT | FK $\rightarrow$ `customers` | Patient / Customer |
| | `doctor_name` | VARCHAR(100) | NOT NULL | Prescribing physician |
| | `doctor_reg_no`| VARCHAR(50) | NOT NULL | Medical council registration no. |
| | `clinic_name` | VARCHAR(100) | NULL | Hospital / Clinic name |
| | `issue_date` | DATE | NOT NULL | Date prescription written |
| **`sales`** | `sale_id` | INT | PK, AUTO_INCREMENT | Unique sale invoice ID |
| | `invoice_number`| VARCHAR(50) | UNIQUE, NOT NULL | Retail bill number |
| | `customer_id` | INT | FK $\rightarrow$ `customers` | Customer reference |
| | `prescription_id`| INT | FK $\rightarrow$ `prescriptions` (NULL) | Associated prescription (if Rx) |
| | `sale_date` | DATETIME | NOT NULL, DEFAULT NOW | Timestamp of transaction |
| | `subtotal` | DECIMAL(10,2)| NOT NULL, CHECK >= 0 | Gross item total |
| | `discount_amount`| DECIMAL(10,2)| DEFAULT 0.00, CHECK >= 0| Concession / discount |
| | `tax_amount` | DECIMAL(10,2)| DEFAULT 0.00, CHECK >= 0| GST / tax component |
| | `net_amount` | DECIMAL(10,2)| NOT NULL, CHECK >= 0 | Final payable sum |
| | `payment_method`| VARCHAR(30) | NOT NULL | Cash / UPI / Card |
| **`sale_items`** | `sale_item_id` | INT | PK, AUTO_INCREMENT | Line item ID |
| | `sale_id` | INT | FK $\rightarrow$ `sales` | Sale bill reference |
| | `batch_id` | INT | FK $\rightarrow$ `batches` | Dispensed batch reference |
| | `quantity` | INT | NOT NULL, CHECK > 0 | Units sold |
| | `unit_price` | DECIMAL(10,2)| NOT NULL, CHECK >= 0 | Selling price per unit |
| | `total_price` | DECIMAL(10,2)| NOT NULL, CHECK >= 0 | `quantity * unit_price` |
| **`stock_movements`**| `movement_id`| INT | PK, AUTO_INCREMENT | Movement audit ID |
| | `batch_id` | INT | FK $\rightarrow$ `batches` | Batch affected |
| | `movement_type`| VARCHAR(20) | CHECK in ('IN_PURCHASE','OUT_SALE','IN_RETURN','OUT_EXPIRED') | Cause of inventory change |
| | `quantity` | INT | NOT NULL, CHECK != 0 | Quantity delta |
| | `movement_date`| DATETIME | NOT NULL, DEFAULT NOW | Audit timestamp |
| **`payments`** | `payment_id` | INT | PK, AUTO_INCREMENT | Payment transaction ID |
| | `transaction_type`| VARCHAR(30)| NOT NULL | 'SALE_COLLECTION' / 'SUPPLIER_PAYMENT' |
| | `reference_id` | INT | NOT NULL | `sale_id` or `purchase_id` |
| | `payment_date` | DATETIME | NOT NULL | Date & time of payment |
| | `amount` | DECIMAL(10,2)| NOT NULL, CHECK > 0 | Amount transacted |
| | `payment_mode` | VARCHAR(30) | NOT NULL | Cash / Card / UPI / NetBanking |

---

### 3. Business Rules Enforcement via Constraints & Triggers

1. **Unique Batch Identifier per Medicine:**
   `UNIQUE KEY uq_medicine_batch (medicine_id, batch_number)` ensures that batch numbers are distinct for every medicine.
2. **No Sale of Expired Medicines:**
   Enforced via SQL database trigger `trg_prevent_expired_sale` on `sale_items` which validates `batches.expiry_date >= CURDATE()`.
3. **Positive Quantities and Non-Negative Prices:**
   `CHECK (quantity > 0)`, `CHECK (unit_cost_price > 0)`, `CHECK (unit_sale_price >= unit_cost_price)`.
4. **Prescription Requirement for Restricted Drugs:**
   Validated at checkout: If `medicines.requires_prescription = 1`, `sales.prescription_id` must NOT be NULL.
5. **Stock Limit Protection:**
   Trigger `trg_deduct_stock_on_sale` verifies `current_stock >= NEW.quantity` before allowing a sale item to be inserted, preventing negative stock.
