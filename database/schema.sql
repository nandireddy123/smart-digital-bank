-- ============================================================
-- Smart Digital Banking Platform - MySQL Schema
-- Run this in MySQL Workbench (or `mysql -u root -p < schema.sql`)
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_banking
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smart_banking;

-- ------------------------------------------------------------
-- BRANCHES
-- ------------------------------------------------------------
CREATE TABLE branches (
    branch_id       INT AUTO_INCREMENT PRIMARY KEY,
    branch_name     VARCHAR(100) NOT NULL,
    branch_code     VARCHAR(20) NOT NULL UNIQUE,
    address         VARCHAR(255),
    city            VARCHAR(100),
    ifsc_code       VARCHAR(20),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- USERS  (base identity table -- maps to the Person concept)
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('CUSTOMER','EMPLOYEE','MANAGER') NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- OTP table (used for email verification + forgot password)
-- ------------------------------------------------------------
CREATE TABLE otp_codes (
    otp_id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    otp_code        VARCHAR(10) NOT NULL,
    purpose         ENUM('EMAIL_VERIFICATION','PASSWORD_RESET') NOT NULL,
    is_used         BOOLEAN DEFAULT FALSE,
    expires_at      DATETIME NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- CUSTOMERS (extends users -> 1:1, "IS-A" relationship at DB level)
-- ------------------------------------------------------------
CREATE TABLE customers (
    customer_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    date_of_birth   DATE,
    address         VARCHAR(255),
    kyc_verified    BOOLEAN DEFAULT FALSE,
    verified_by_employee_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- EMPLOYEES (extends users, created only by a Manager)
-- ------------------------------------------------------------
CREATE TABLE employees (
    employee_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    branch_id       INT,
    designation     VARCHAR(100) DEFAULT 'Bank Employee',
    created_by_manager_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- ------------------------------------------------------------
-- MANAGERS (extends users)
-- ------------------------------------------------------------
CREATE TABLE managers (
    manager_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    branch_id       INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- add FK back from customers.verified_by_employee_id now employees exists
ALTER TABLE customers
    ADD CONSTRAINT fk_customer_verified_by
    FOREIGN KEY (verified_by_employee_id) REFERENCES employees(employee_id);

ALTER TABLE employees
    ADD CONSTRAINT fk_employee_created_by
    FOREIGN KEY (created_by_manager_id) REFERENCES managers(manager_id);

-- ------------------------------------------------------------
-- ACCOUNTS  (single table, account_type = polymorphic discriminator)
-- ------------------------------------------------------------
CREATE TABLE accounts (
    account_id      INT AUTO_INCREMENT PRIMARY KEY,
    account_number  VARCHAR(20) NOT NULL UNIQUE,
    customer_id     INT NOT NULL,
    branch_id       INT,
    account_type    ENUM('SAVINGS','CURRENT','STUDENT') NOT NULL,
    balance         DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    status          ENUM('PENDING','ACTIVE','FROZEN','CLOSED') DEFAULT 'PENDING',
    approved_by_employee_id INT NULL,
    interest_rate   DECIMAL(5,2) DEFAULT 0.00,
    min_balance     DECIMAL(15,2) DEFAULT 0.00,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    FOREIGN KEY (approved_by_employee_id) REFERENCES employees(employee_id)
);

-- ------------------------------------------------------------
-- TRANSACTIONS
-- ------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id  INT AUTO_INCREMENT PRIMARY KEY,
    reference_no    VARCHAR(40) NOT NULL UNIQUE,
    account_id      INT NOT NULL,
    related_account_id INT NULL,
    transaction_type ENUM('DEPOSIT','WITHDRAW','TRANSFER_OUT','TRANSFER_IN') NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    balance_after   DECIMAL(15,2) NOT NULL,
    description     VARCHAR(255),
    status          ENUM('SUCCESS','FAILED','PENDING') DEFAULT 'SUCCESS',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (related_account_id) REFERENCES accounts(account_id)
);

-- ------------------------------------------------------------
-- CARDS
-- ------------------------------------------------------------
CREATE TABLE cards (
    card_id         INT AUTO_INCREMENT PRIMARY KEY,
    account_id      INT NOT NULL,
    card_number     VARCHAR(20) NOT NULL UNIQUE,
    card_type       ENUM('DEBIT') DEFAULT 'DEBIT',
    expiry_date     DATE NOT NULL,
    cvv_hash        VARCHAR(255) NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- LOANS
-- ------------------------------------------------------------
CREATE TABLE loans (
    loan_id         INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    account_id      INT NOT NULL,
    loan_type       VARCHAR(50) NOT NULL,
    principal_amount DECIMAL(15,2) NOT NULL,
    interest_rate   DECIMAL(5,2) NOT NULL,
    tenure_months   INT NOT NULL,
    status          ENUM('PENDING','APPROVED','REJECTED','CLOSED') DEFAULT 'PENDING',
    approved_by_manager_id INT NULL,
    applied_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    decided_at      DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (approved_by_manager_id) REFERENCES managers(manager_id)
);

-- ------------------------------------------------------------
-- NOTIFICATIONS
-- ------------------------------------------------------------
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    title           VARCHAR(150) NOT NULL,
    message         VARCHAR(500) NOT NULL,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- AUDIT LOGS
-- ------------------------------------------------------------
CREATE TABLE audit_logs (
    audit_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NULL,
    action          VARCHAR(150) NOT NULL,
    details         VARCHAR(500),
    ip_address      VARCHAR(50),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- SUPPORT TICKETS (Contact Support feature)
-- ------------------------------------------------------------
CREATE TABLE support_tickets (
    ticket_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    subject         VARCHAR(150) NOT NULL,
    message         VARCHAR(1000) NOT NULL,
    status          ENUM('OPEN','IN_PROGRESS','RESOLVED') DEFAULT 'OPEN',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Helpful indexes
-- ------------------------------------------------------------
CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_otp_user ON otp_codes(user_id);

-- ------------------------------------------------------------
-- Seed: one branch + one manager login (password = Manager@123)
-- Password hash below is a bcrypt hash generated by the backend's
-- own hashing utility -- see docs/README.md "Seeding the first Manager"
-- ------------------------------------------------------------
INSERT INTO branches (branch_name, branch_code, address, city, ifsc_code)
VALUES ('Main Branch', 'BR001', '123 MG Road', 'Hyderabad', 'SBIN0000001');
