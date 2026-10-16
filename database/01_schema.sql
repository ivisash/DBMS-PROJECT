DROP DATABASE IF EXISTS pharmacy_db;
CREATE DATABASE pharmacy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pharmacy_db;

-- 1. CATEGORIES TABLE
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. MANUFACTURERS TABLE
CREATE TABLE manufacturers (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL UNIQUE,
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. SUPPLIERS TABLE
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    gst_number VARCHAR(20) NOT NULL UNIQUE,
    contact_person VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(255),
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. MEDICINES TABLE
CREATE TABLE medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL,
    generic_name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    manufacturer_id INT NOT NULL,
    dosage_form ENUM('Tablet', 'Capsule', 'Syrup', 'Injection', 'Ointment', 'Drops', 'Inhaler') NOT NULL,
    strength VARCHAR(50) NOT NULL,
    reorder_level INT NOT NULL DEFAULT 20,
    requires_prescription TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_med_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT,
    CONSTRAINT fk_med_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id) ON DELETE RESTRICT,
    CONSTRAINT chk_med_reorder CHECK (reorder_level >= 0),
    CONSTRAINT uq_brand_strength UNIQUE (brand_name, strength, dosage_form)
) ENGINE=InnoDB;

-- 5. PURCHASES TABLE
CREATE TABLE purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    supplier_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status ENUM('PAID', 'PENDING', 'PARTIAL') NOT NULL DEFAULT 'PAID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_purchase_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT,
    CONSTRAINT chk_purchase_total CHECK (total_amount >= 0.00)
) ENGINE=InnoDB;

-- 6. BATCHES TABLE (Core Inventory Unit)
CREATE TABLE batches (
    batch_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_number VARCHAR(50) NOT NULL,
    medicine_id INT NOT NULL,
    purchase_id INT,
    manufacture_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    unit_cost_price DECIMAL(10, 2) NOT NULL,
    unit_sale_price DECIMAL(10, 2) NOT NULL,
    initial_quantity INT NOT NULL,
    current_stock INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_batch_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE RESTRICT,
    CONSTRAINT fk_batch_purchase FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE SET NULL,
    CONSTRAINT uq_medicine_batch UNIQUE (medicine_id, batch_number),
    CONSTRAINT chk_batch_expiry CHECK (expiry_date > manufacture_date),
    CONSTRAINT chk_cost_price CHECK (unit_cost_price > 0.00),
    CONSTRAINT chk_sale_price CHECK (unit_sale_price >= unit_cost_price),
    CONSTRAINT chk_initial_qty CHECK (initial_quantity > 0),
    CONSTRAINT chk_stock_positive CHECK (current_stock >= 0)
) ENGINE=InnoDB;

-- 7. CUSTOMERS TABLE
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100),
    gender ENUM('Male', 'Female', 'Other'),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. PRESCRIPTIONS TABLE
CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_code VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    doctor_name VARCHAR(100) NOT NULL,
    doctor_reg_no VARCHAR(50) NOT NULL,
    clinic_name VARCHAR(120),
    issue_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rx_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 9. SALES TABLE
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT,
    prescription_id INT NULL,
    sale_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    net_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_method ENUM('CASH', 'CARD', 'UPI', 'NET_BANKING') NOT NULL DEFAULT 'CASH',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sale_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    CONSTRAINT fk_sale_prescription FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE RESTRICT,
    CONSTRAINT chk_subtotal CHECK (subtotal >= 0.00),
    CONSTRAINT chk_discount CHECK (discount_amount >= 0.00),
    CONSTRAINT chk_tax CHECK (tax_amount >= 0.00),
    CONSTRAINT chk_net CHECK (net_amount >= 0.00)
) ENGINE=InnoDB;

-- 10. SALE ITEMS TABLE
CREATE TABLE sale_items (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    batch_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_item_sale FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    CONSTRAINT fk_item_batch FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE RESTRICT,
    CONSTRAINT chk_item_quantity CHECK (quantity > 0),
    CONSTRAINT chk_item_unit_price CHECK (unit_price >= 0.00),
    CONSTRAINT chk_item_total CHECK (total_price >= 0.00)
) ENGINE=InnoDB;

-- 11. STOCK MOVEMENTS (AUDIT TRAIL)
CREATE TABLE stock_movements (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    movement_type ENUM('PURCHASE_IN', 'SALE_OUT', 'RETURN_IN', 'EXPIRED_DISPOSAL') NOT NULL,
    quantity INT NOT NULL,
    movement_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reference_id INT,
    remarks VARCHAR(255),
    CONSTRAINT fk_mov_batch FOREIGN KEY (batch_id) REFERENCES batches(batch_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 12. PAYMENTS TABLE
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_type ENUM('SALE_COLLECTION', 'SUPPLIER_PAYMENT') NOT NULL,
    reference_id INT NOT NULL,
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    payment_mode ENUM('CASH', 'CARD', 'UPI', 'BANK_TRANSFER', 'CHEQUE') NOT NULL,
    transaction_status ENUM('SUCCESS', 'PENDING', 'FAILED') NOT NULL DEFAULT 'SUCCESS',
    CONSTRAINT chk_pay_amount CHECK (amount > 0.00)
) ENGINE=InnoDB;

-- INDEXES FOR FREQUENTLY SEARCHED ATTRIBUTES (Performance Optimization)
CREATE INDEX idx_med_brand ON medicines(brand_name);
CREATE INDEX idx_med_generic ON medicines(generic_name);
CREATE INDEX idx_batch_expiry ON batches(expiry_date);
CREATE INDEX idx_batch_stock ON batches(current_stock);
CREATE INDEX idx_sale_date ON sales(sale_date);
CREATE INDEX idx_cust_phone ON customers(phone_number);

-- DATABASE TRIGGERS ENFORCING INTEGRITY RULES
DELIMITER $$

-- Rule 1: No sale of expired medicines
-- Rule 2: Cannot sell more than available batch stock
-- Rule 3: Automatically reduce batch stock and log audit trail
CREATE TRIGGER trg_validate_and_deduct_stock
BEFORE INSERT ON sale_items
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;
    DECLARE v_expiry DATE;
    DECLARE v_is_rx INT;

    -- Fetch batch details
    SELECT current_stock, expiry_date 
    INTO v_stock, v_expiry
    FROM batches
    WHERE batch_id = NEW.batch_id;

    -- Enforce: Expiry date check
    IF v_expiry < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ERROR: Cannot dispense medicine from an EXPIRED batch!';
    END IF;

    -- Enforce: Stock limit check
    IF v_stock < NEW.quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ERROR: Insufficient stock in this batch for the requested quantity!';
    END IF;
END$$

-- After sale item insertion: update stock balance & write movement log
CREATE TRIGGER trg_after_sale_item_insert
AFTER INSERT ON sale_items
FOR EACH ROW
BEGIN
    -- Deduct current stock
    UPDATE batches
    SET current_stock = current_stock - NEW.quantity
    WHERE batch_id = NEW.batch_id;
    INSERT INTO stock_movements (batch_id, movement_type, quantity, reference_id, remarks)
    VALUES (NEW.batch_id, 'SALE_OUT', NEW.quantity, NEW.sale_id, 'Dispensed via retail invoice');
END$$

DELIMITER ;
