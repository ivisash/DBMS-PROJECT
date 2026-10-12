-- ============================================================================
-- PHARMACY PRESCRIPTION AND MEDICINE STOCK MANAGEMENT SYSTEM
-- SQLite Equivalent Schema & Seed Data (Portable Database for Local Execution)
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. CATEGORIES
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. MANUFACTURERS
CREATE TABLE IF NOT EXISTS manufacturers (
    manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    contact_email TEXT,
    phone TEXT,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. SUPPLIERS
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    gst_number TEXT NOT NULL UNIQUE,
    contact_person TEXT,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. MEDICINES
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL,
    generic_name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(manufacturer_id),
    dosage_form TEXT NOT NULL CHECK(dosage_form IN ('Tablet', 'Capsule', 'Syrup', 'Injection', 'Ointment', 'Drops', 'Inhaler')),
    strength TEXT NOT NULL,
    reorder_level INTEGER NOT NULL DEFAULT 20 CHECK(reorder_level >= 0),
    requires_prescription INTEGER NOT NULL DEFAULT 0 CHECK(requires_prescription IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand_name, strength, dosage_form)
);

-- 5. PURCHASES
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT NOT NULL UNIQUE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    purchase_date DATE NOT NULL,
    total_amount REAL NOT NULL DEFAULT 0.0 CHECK(total_amount >= 0.0),
    payment_status TEXT NOT NULL DEFAULT 'PAID' CHECK(payment_status IN ('PAID', 'PENDING', 'PARTIAL')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. BATCHES
CREATE TABLE IF NOT EXISTS batches (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_number TEXT NOT NULL,
    medicine_id INTEGER NOT NULL REFERENCES medicines(medicine_id),
    purchase_id INTEGER REFERENCES purchases(purchase_id),
    manufacture_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    unit_cost_price REAL NOT NULL CHECK(unit_cost_price > 0),
    unit_sale_price REAL NOT NULL CHECK(unit_sale_price >= unit_cost_price),
    initial_quantity INTEGER NOT NULL CHECK(initial_quantity > 0),
    current_stock INTEGER NOT NULL CHECK(current_stock >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(medicine_id, batch_number)
);

-- 7. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    email TEXT,
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. PRESCRIPTIONS
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_code TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    doctor_name TEXT NOT NULL,
    doctor_reg_no TEXT NOT NULL,
    clinic_name TEXT,
    issue_date DATE NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 9. SALES
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT NOT NULL UNIQUE,
    customer_id INTEGER REFERENCES customers(customer_id),
    prescription_id INTEGER REFERENCES prescriptions(prescription_id),
    sale_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal REAL NOT NULL DEFAULT 0.0 CHECK(subtotal >= 0.0),
    discount_amount REAL NOT NULL DEFAULT 0.0 CHECK(discount_amount >= 0.0),
    tax_amount REAL NOT NULL DEFAULT 0.0 CHECK(tax_amount >= 0.0),
    net_amount REAL NOT NULL DEFAULT 0.0 CHECK(net_amount >= 0.0),
    payment_method TEXT NOT NULL DEFAULT 'CASH' CHECK(payment_method IN ('CASH', 'CARD', 'UPI', 'NET_BANKING')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 10. SALE ITEMS
CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(sale_id) ON DELETE CASCADE,
    batch_id INTEGER NOT NULL REFERENCES batches(batch_id),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
    total_price REAL NOT NULL CHECK(total_price >= 0.0)
);

-- 11. STOCK MOVEMENTS
CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL REFERENCES batches(batch_id),
    movement_type TEXT NOT NULL CHECK(movement_type IN ('PURCHASE_IN', 'SALE_OUT', 'RETURN_IN', 'EXPIRED_DISPOSAL')),
    quantity INTEGER NOT NULL,
    movement_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reference_id INTEGER,
    remarks TEXT
);

-- 12. PAYMENTS
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('SALE_COLLECTION', 'SUPPLIER_PAYMENT')),
    reference_id INTEGER NOT NULL,
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount REAL NOT NULL CHECK(amount > 0.0),
    payment_mode TEXT NOT NULL CHECK(payment_mode IN ('CASH', 'CARD', 'UPI', 'BANK_TRANSFER', 'CHEQUE')),
    transaction_status TEXT NOT NULL DEFAULT 'SUCCESS'
);

-- SEED DATA INSERTION
INSERT OR IGNORE INTO categories (category_id, category_name, description) VALUES
(1, 'Antibiotics', 'Antimicrobial medicines used in the treatment and prevention of bacterial infections'),
(2, 'Analgesics & Antipyretics', 'Pain relievers and fever reducing medications'),
(3, 'Antidiabetics', 'Medications to manage blood glucose levels in diabetes mellitus'),
(4, 'Cardiovascular', 'Drugs used for hypertension, angina, and heart conditions'),
(5, 'Gastrointestinal', 'Antacids, proton pump inhibitors, and anti-ulcerants'),
(6, 'Antihistamines', 'Allergy relief and anti-inflammatory respiratory medications'),
(7, 'Vitamins & Supplements', 'Nutritional, mineral, and dietary supplements');

INSERT OR IGNORE INTO manufacturers (manufacturer_id, company_name, contact_email, phone, address) VALUES
(1, 'Sun Pharmaceutical Industries Ltd', 'support@sunpharma.com', '+91-22-43244324', 'Goregaon East, Mumbai, Maharashtra'),
(2, 'Cipla Limited', 'contact@cipla.com', '+91-22-24826000', 'Cipla House, Peninsula Business Park, Mumbai'),
(3, 'Dr. Reddy''s Laboratories', 'info@drreddys.com', '+91-40-49002900', 'Banjara Hills, Hyderabad, Telangana'),
(4, 'GlaxoSmithKline Pharmaceuticals (GSK)', 'india.helpdesk@gsk.com', '+91-22-24959595', 'Worli, Mumbai, Maharashtra'),
(5, 'Abbott Healthcare Pvt Ltd', 'contactus@abbott.in', '+91-22-38162000', 'BKC, Bandra East, Mumbai');

INSERT OR IGNORE INTO suppliers (supplier_id, supplier_name, gst_number, contact_person, phone, email, address) VALUES
(1, 'Apex Pharma Wholesalers', '27AABCA1234F1Z1', 'Ramesh Gupta', '+91-9820011223', 'sales@apexpharma.com', 'Dadar West, Mumbai'),
(2, 'MedLife Distribution Hub', '27BBBCD5678G2Z4', 'Sunil Mehta', '+91-9821122334', 'orders@medlifehub.in', 'Andheri East, Mumbai'),
(3, 'Global Pharma Logistics', '36CCCCE9012H3Z8', 'Venkatesh Rao', '+91-9849033445', 'supply@globalpharma.com', 'Kukatpally, Hyderabad');

INSERT OR IGNORE INTO medicines (medicine_id, brand_name, generic_name, category_id, manufacturer_id, dosage_form, strength, reorder_level, requires_prescription) VALUES
(1, 'Augmentin 625 Duo', 'Amoxicillin + Clavulanic Acid', 1, 4, 'Tablet', '625mg', 30, 1),
(2, 'Azithral 500', 'Azithromycin', 1, 3, 'Tablet', '500mg', 25, 1),
(3, 'Dolo 650', 'Paracetamol', 2, 1, 'Tablet', '650mg', 50, 0),
(4, 'Combiflam', 'Ibuprofen + Paracetamol', 2, 5, 'Tablet', '400mg+325mg', 40, 0),
(5, 'Glycomet 500 SR', 'Metformin Hydrochloride', 3, 1, 'Tablet', '500mg', 35, 1),
(6, 'Januvia 100', 'Sitagliptin', 3, 5, 'Tablet', '100mg', 20, 1),
(7, 'Amlong 5', 'Amlodipine Besylate', 4, 1, 'Tablet', '5mg', 30, 1),
(8, 'Telma 40', 'Telmisartan', 4, 4, 'Tablet', '40mg', 30, 1),
(9, 'Pan 40', 'Pantoprazole Sodium', 5, 5, 'Tablet', '40mg', 40, 0),
(10, 'Gelusil MPS', 'Antacid Aluminium/Magnesium', 5, 2, 'Syrup', '200ml', 15, 0),
(11, 'Allegra 120', 'Fexofenadine HCl', 6, 5, 'Tablet', '120mg', 20, 0),
(12, 'Becosules Z', 'B-Complex Forte + Vitamin C + Zinc', 7, 4, 'Capsule', 'Standard', 50, 0);

INSERT OR IGNORE INTO purchases (purchase_id, invoice_number, supplier_id, purchase_date, total_amount, payment_status) VALUES
(1, 'INV-APX-2026-001', 1, '2026-08-15', 18500.00, 'PAID'),
(2, 'INV-MLH-2026-042', 2, '2026-09-02', 14200.00, 'PAID'),
(3, 'INV-GPL-2026-108', 3, '2026-09-20', 22800.00, 'PAID');

INSERT OR IGNORE INTO batches (batch_id, batch_number, medicine_id, purchase_id, manufacture_date, expiry_date, unit_cost_price, unit_sale_price, initial_quantity, current_stock) VALUES
(1, 'AUG-2401', 1, 1, '2026-01-10', '2027-12-31', 160.00, 210.00, 100, 85),
(2, 'AZI-2388', 2, 1, '2025-06-01', '2026-11-20', 95.00, 135.00, 80, 24),
(3, 'DOL-2509', 3, 2, '2026-04-15', '2028-03-31', 22.00, 34.00, 300, 260),
(4, 'CMB-2490', 4, 2, '2026-03-01', '2027-10-31', 28.00, 42.00, 150, 130),
(5, 'GLY-2512', 5, 2, '2026-05-10', '2028-04-30', 35.00, 52.00, 200, 175),
(6, 'JAN-2477', 6, 3, '2025-11-01', '2027-08-31', 320.00, 410.00, 30, 8),
(7, 'AML-2465', 7, 3, '2026-02-15', '2027-11-30', 25.00, 38.00, 120, 105),
(8, 'TEL-2503', 8, 3, '2026-04-01', '2028-02-28', 55.00, 80.00, 100, 88),
(9, 'PAN-2399', 9, 1, '2025-05-01', '2026-11-05', 68.00, 98.00, 120, 35),
(10, 'GEL-2481', 10, 2, '2026-02-01', '2027-07-31', 75.00, 110.00, 60, 52),
(11, 'ALL-2510', 11, 3, '2026-06-01', '2028-05-31', 140.00, 195.00, 80, 70),
(12, 'BEC-2533', 12, 1, '2026-07-01', '2028-06-30', 30.00, 48.00, 250, 220);

INSERT OR IGNORE INTO customers (customer_id, full_name, phone_number, email, gender, address) VALUES
(1, 'Rahul Verma', '+91-9876543210', 'rahul.verma@gmail.com', 'Male', 'Flat 402, Green Meadows, Andheri West, Mumbai'),
(2, 'Sneha Sharma', '+91-9812345678', 'sneha.sharma@yahoo.com', 'Female', 'B-12, Sun City Apartments, Borivali East, Mumbai'),
(3, 'Amitabh Das', '+91-9823456789', 'amitabh.das@rediffmail.com', 'Male', '14, Palm Avenue, Bandra, Mumbai'),
(4, 'Pooja Kulkarni', '+91-9834567890', 'pooja.k@outlook.com', 'Female', 'Plot 88, Vashi Sector 17, Navi Mumbai'),
(5, 'Vikram Joshi', '+91-9845678901', 'vjoshi99@gmail.com', 'Male', 'C-304, Royal Palms, Goregaon, Mumbai');

INSERT OR IGNORE INTO prescriptions (prescription_id, prescription_code, customer_id, doctor_name, doctor_reg_no, clinic_name, issue_date, notes) VALUES
(1, 'RX-2026-001', 1, 'Dr. Rajesh Deshmukh', 'MCI-MH-45892', 'Deshmukh Chest Clinic', '2026-10-01', 'Augmentin 625 Duo for 7 days'),
(2, 'RX-2026-002', 3, 'Dr. Ananya Sengupta', 'MCI-WB-28114', 'Apollo Diabetes Center', '2026-10-05', 'Metformin maintenance therapy'),
(3, 'RX-2026-003', 4, 'Dr. Nilesh Parekh', 'MCI-MH-67123', 'Parekh Heart Foundation', '2026-10-08', 'Telma 40 once daily');

INSERT OR IGNORE INTO sales (sale_id, invoice_number, customer_id, prescription_id, sale_date, subtotal, discount_amount, tax_amount, net_amount, payment_method) VALUES
(1, 'BILL-2026-1001', 1, 1, '2026-10-02 10:15:00', 420.00, 20.00, 20.00, 420.00, 'UPI'),
(2, 'BILL-2026-1002', 2, NULL, '2026-10-03 14:30:00', 164.00, 0.00, 8.20, 172.20, 'CASH'),
(3, 'BILL-2026-1003', 3, 2, '2026-10-06 18:45:00', 302.00, 12.00, 15.00, 305.00, 'CARD');

INSERT OR IGNORE INTO sale_items (sale_item_id, sale_id, batch_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 2, 210.00, 420.00),
(2, 2, 3, 2, 34.00, 68.00),
(3, 2, 12, 2, 48.00, 96.00),
(4, 3, 5, 3, 52.00, 156.00),
(5, 3, 9, 1, 98.00, 98.00),
(6, 3, 3, 1, 34.00, 34.00);
