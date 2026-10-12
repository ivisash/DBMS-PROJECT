-- ============================================================================
-- PHARMACY PRESCRIPTION AND MEDICINE STOCK MANAGEMENT SYSTEM
-- Review 2: Realistic Seed Data for MySQL
-- ============================================================================

USE pharmacy_db;

-- 1. CATEGORIES
INSERT INTO categories (category_name, description) VALUES
('Antibiotics', 'Antimicrobial medicines used in the treatment and prevention of bacterial infections'),
('Analgesics & Antipyretics', 'Pain relievers and fever reducing medications'),
('Antidiabetics', 'Medications to manage blood glucose levels in diabetes mellitus'),
('Cardiovascular', 'Drugs used for hypertension, angina, and heart conditions'),
('Gastrointestinal', 'Antacids, proton pump inhibitors, and anti-ulcerants'),
('Antihistamines', 'Allergy relief and anti-inflammatory respiratory medications'),
('Vitamins & Supplements', 'Nutritional, mineral, and dietary supplements');

-- 2. MANUFACTURERS
INSERT INTO manufacturers (company_name, contact_email, phone, address) VALUES
('Sun Pharmaceutical Industries Ltd', 'support@sunpharma.com', '+91-22-43244324', 'Goregaon East, Mumbai, Maharashtra'),
('Cipla Limited', 'contact@cipla.com', '+91-22-24826000', 'Cipla House, Peninsula Business Park, Mumbai'),
('Dr. Reddy\'s Laboratories', 'info@drreddys.com', '+91-40-49002900', 'Banjara Hills, Hyderabad, Telangana'),
('GlaxoSmithKline Pharmaceuticals (GSK)', 'india.helpdesk@gsk.com', '+91-22-24959595', 'Worli, Mumbai, Maharashtra'),
('Abbott Healthcare Pvt Ltd', 'contactus@abbott.in', '+91-22-38162000', 'BKC, Bandra East, Mumbai');

-- 3. SUPPLIERS
INSERT INTO suppliers (supplier_name, gst_number, contact_person, phone, email, address) VALUES
('Apex Pharma Wholesalers', '27AABCA1234F1Z1', 'Ramesh Gupta', '+91-9820011223', 'sales@apexpharma.com', 'Dadar West, Mumbai'),
('MedLife Distribution Hub', '27BBBCD5678G2Z4', 'Sunil Mehta', '+91-9821122334', 'orders@medlifehub.in', 'Andheri East, Mumbai'),
('Global Pharma Logistics', '36CCCCE9012H3Z8', 'Venkatesh Rao', '+91-9849033445', 'supply@globalpharma.com', 'Kukatpally, Hyderabad');

-- 4. MEDICINES
-- Brand, Generic, Category, Manufacturer, Dosage, Strength, ReorderLevel, RequiresPrescription
INSERT INTO medicines (brand_name, generic_name, category_id, manufacturer_id, dosage_form, strength, reorder_level, requires_prescription) VALUES
('Augmentin 625 Duo', 'Amoxicillin + Clavulanic Acid', 1, 4, 'Tablet', '625mg', 30, 1),
('Azithral 500', 'Azithromycin', 1, 3, 'Tablet', '500mg', 25, 1),
('Dolo 650', 'Paracetamol', 2, 1, 'Tablet', '650mg', 50, 0),
('Combiflam', 'Ibuprofen + Paracetamol', 2, 5, 'Tablet', '400mg+325mg', 40, 0),
('Glycomet 500 SR', 'Metformin Hydrochloride', 3, 1, 'Tablet', '500mg', 35, 1),
('Januvia 100', 'Sitagliptin', 3, 5, 'Tablet', '100mg', 20, 1),
('Amlong 5', 'Amlodipine Besylate', 4, 1, 'Tablet', '5mg', 30, 1),
('Telma 40', 'Telmisartan', 4, 4, 'Tablet', '40mg', 30, 1),
('Pan 40', 'Pantoprazole Sodium', 5, 5, 'Tablet', '40mg', 40, 0),
('Gelusil MPS', 'Antacid Aluminium/Magnesium', 5, 2, 'Syrup', '200ml', 15, 0),
('Allegra 120', 'Fexofenadine HCl', 6, 5, 'Tablet', '120mg', 20, 0),
('Becosules Z', 'B-Complex Forte + Vitamin C + Zinc', 7, 4, 'Capsule', 'Standard', 50, 0);

-- 5. PURCHASES
INSERT INTO purchases (invoice_number, supplier_id, purchase_date, total_amount, payment_status) VALUES
('INV-APX-2026-001', 1, '2026-08-15', 18500.00, 'PAID'),
('INV-MLH-2026-042', 2, '2026-09-02', 14200.00, 'PAID'),
('INV-GPL-2026-108', 3, '2026-09-20', 22800.00, 'PAID');

-- 6. BATCHES
-- BatchNo, MedicineID, PurchaseID, MfgDate, ExpDate, Cost, Sale, InitialQty, CurrentStock
INSERT INTO batches (batch_number, medicine_id, purchase_id, manufacture_date, expiry_date, unit_cost_price, unit_sale_price, initial_quantity, current_stock) VALUES
-- Augmentin 625 Duo (Active)
('AUG-2401', 1, 1, '2026-01-10', '2027-12-31', 160.00, 210.00, 100, 85),
-- Azithral 500 (Near expiry in ~45 days for alert demonstration)
('AZI-2388', 2, 1, '2025-06-01', '2026-11-20', 95.00, 135.00, 80, 24),
-- Dolo 650 (High stock, OTC)
('DOL-2509', 3, 2, '2026-04-15', '2028-03-31', 22.00, 34.00, 300, 260),
-- Combiflam (Active)
('CMB-2490', 4, 2, '2026-03-01', '2027-10-31', 28.00, 42.00, 150, 130),
-- Glycomet 500 (Active)
('GLY-2512', 5, 2, '2026-05-10', '2028-04-30', 35.00, 52.00, 200, 175),
-- Januvia 100 (Low stock / reorder alert demo)
('JAN-2477', 6, 3, '2025-11-01', '2027-08-31', 320.00, 410.00, 30, 8),
-- Amlong 5 (Active)
('AML-2465', 7, 3, '2026-02-15', '2027-11-30', 25.00, 38.00, 120, 105),
-- Telma 40 (Active)
('TEL-2503', 8, 3, '2026-04-01', '2028-02-28', 55.00, 80.00, 100, 88),
-- Pan 40 (Near expiry in ~25 days)
('PAN-2399', 9, 1, '2025-05-01', '2026-11-05', 68.00, 98.00, 120, 35),
-- Gelusil MPS (Active)
('GEL-2481', 10, 2, '2026-02-01', '2027-07-31', 75.00, 110.00, 60, 52),
-- Allegra 120 (Active)
('ALL-2510', 11, 3, '2026-06-01', '2028-05-31', 140.00, 195.00, 80, 70),
-- Becosules Z (Active)
('BEC-2533', 12, 1, '2026-07-01', '2028-06-30', 30.00, 48.00, 250, 220);

-- 7. CUSTOMERS
INSERT INTO customers (full_name, phone_number, email, gender, address) VALUES
('Rahul Verma', '+91-9876543210', 'rahul.verma@gmail.com', 'Male', 'Flat 402, Green Meadows, Andheri West, Mumbai'),
('Sneha Sharma', '+91-9812345678', 'sneha.sharma@yahoo.com', 'Female', 'B-12, Sun City Apartments, Borivali East, Mumbai'),
('Amitabh Das', '+91-9823456789', 'amitabh.das@rediffmail.com', 'Male', '14, Palm Avenue, Bandra, Mumbai'),
('Pooja Kulkarni', '+91-9834567890', 'pooja.k@outlook.com', 'Female', 'Plot 88, Vashi Sector 17, Navi Mumbai'),
('Vikram Joshi', '+91-9845678901', 'vjoshi99@gmail.com', 'Male', 'C-304, Royal Palms, Goregaon, Mumbai');

-- 8. PRESCRIPTIONS
INSERT INTO prescriptions (prescription_code, customer_id, doctor_name, doctor_reg_no, clinic_name, issue_date, notes) VALUES
('RX-2026-001', 1, 'Dr. Rajesh Deshmukh', 'MCI-MH-45892', 'Deshmukh Chest & Heart Clinic', '2026-10-01', 'Course for bacterial bronchitis. Dispense Augmentin 625 Duo for 7 days.'),
('RX-2026-002', 3, 'Dr. Ananya Sengupta', 'MCI-WB-28114', 'Apollo Diabetes Center', '2026-10-05', 'Metformin maintenance therapy. Check HbA1c in 3 months.'),
('RX-2026-003', 4, 'Dr. Nilesh Parekh', 'MCI-MH-67123', 'Parekh Heart Foundation', '2026-10-08', 'Hypertension regimen: Telma 40 once daily in morning.');

-- 9. SALES & SALE ITEMS
-- Sale 1: Prescription Sale for Rahul Verma
INSERT INTO sales (invoice_number, customer_id, prescription_id, sale_date, subtotal, discount_amount, tax_amount, net_amount, payment_method)
VALUES ('BILL-2026-1001', 1, 1, '2026-10-02 10:15:00', 420.00, 20.00, 20.00, 420.00, 'UPI');

INSERT INTO sale_items (sale_id, batch_id, quantity, unit_price, total_price) VALUES
(1, 1, 2, 210.00, 420.00);

-- Sale 2: OTC Sale for Sneha Sharma (Dolo + Becosules)
INSERT INTO sales (invoice_number, customer_id, prescription_id, sale_date, subtotal, discount_amount, tax_amount, net_amount, payment_method)
VALUES ('BILL-2026-1002', 2, NULL, '2026-10-03 14:30:00', 164.00, 0.00, 8.20, 172.20, 'CASH');

INSERT INTO sale_items (sale_id, batch_id, quantity, unit_price, total_price) VALUES
(2, 3, 2, 34.00, 68.00),
(2, 12, 2, 48.00, 96.00);

-- Sale 3: Prescription Sale for Amitabh Das (Glycomet + Pan 40)
INSERT INTO sales (invoice_number, customer_id, prescription_id, sale_date, subtotal, discount_amount, tax_amount, net_amount, payment_method)
VALUES ('BILL-2026-1003', 3, 2, '2026-10-06 18:45:00', 302.00, 12.00, 15.00, 305.00, 'CARD');

INSERT INTO sale_items (sale_id, batch_id, quantity, unit_price, total_price) VALUES
(3, 5, 3, 52.00, 156.00),
(3, 9, 1, 98.00, 98.00),
(3, 3, 1, 34.00, 34.00);

-- 10. STOCK MOVEMENTS (INITIAL INWARD LOGS)
INSERT INTO stock_movements (batch_id, movement_type, quantity, reference_id, remarks) VALUES
(1, 'PURCHASE_IN', 100, 1, 'Initial shipment received from Apex Pharma'),
(2, 'PURCHASE_IN', 80, 1, 'Initial shipment received from Apex Pharma'),
(3, 'PURCHASE_IN', 300, 2, 'Initial shipment received from MedLife'),
(4, 'PURCHASE_IN', 150, 2, 'Initial shipment received from MedLife'),
(5, 'PURCHASE_IN', 200, 2, 'Initial shipment received from MedLife'),
(6, 'PURCHASE_IN', 30, 3, 'Initial shipment received from Global Pharma'),
(7, 'PURCHASE_IN', 120, 3, 'Initial shipment received from Global Pharma'),
(8, 'PURCHASE_IN', 100, 3, 'Initial shipment received from Global Pharma'),
(9, 'PURCHASE_IN', 120, 1, 'Initial shipment received from Apex Pharma'),
(10, 'PURCHASE_IN', 60, 2, 'Initial shipment received from MedLife'),
(11, 'PURCHASE_IN', 80, 3, 'Initial shipment received from Global Pharma'),
(12, 'PURCHASE_IN', 250, 1, 'Initial shipment received from Apex Pharma');

-- 11. PAYMENTS
INSERT INTO payments (transaction_type, reference_id, payment_date, amount, payment_mode, transaction_status) VALUES
('SALE_COLLECTION', 1, '2026-10-02 10:16:00', 420.00, 'UPI', 'SUCCESS'),
('SALE_COLLECTION', 2, '2026-10-03 14:31:00', 172.20, 'CASH', 'SUCCESS'),
('SALE_COLLECTION', 3, '2026-10-06 18:46:00', 305.00, 'CARD', 'SUCCESS'),
('SUPPLIER_PAYMENT', 1, '2026-08-16 11:00:00', 18500.00, 'BANK_TRANSFER', 'SUCCESS'),
('SUPPLIER_PAYMENT', 2, '2026-09-03 16:30:00', 14200.00, 'BANK_TRANSFER', 'SUCCESS'),
('SUPPLIER_PAYMENT', 3, '2026-09-21 12:15:00', 22800.00, 'BANK_TRANSFER', 'SUCCESS');
