create database db_project3;
use db_project3;

-- Tables
CREATE TABLE Owner (
    owner_id VARCHAR(50) PRIMARY KEY,
    owner_name VARCHAR(255) NOT NULL,
    contact_no VARCHAR(15) NOT NULL,
    owner_pass VARCHAR(255) NOT NULL DEFAULT '12345678'
);

-- Create Employee Table
CREATE TABLE Employee (
    emp_id VARCHAR(50) PRIMARY KEY,
    emp_name VARCHAR(255) NOT NULL,
    emp_type ENUM('block_admin', 'staff') NOT NULL,
    emp_pass VARCHAR(255) NOT NULL DEFAULT '12345678',
    block_no INT NOT NULL
);

-- Create Block Table
CREATE TABLE Block (
    block_no INT PRIMARY KEY,
    emp_id VARCHAR(50),
    FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
);

-- Create Room Table
CREATE TABLE Room (
    room_no INT PRIMARY KEY,
    type ENUM('1BHK', '2BHK', '3BHK') NOT NULL,
    parking_slot BOOLEAN NOT NULL DEFAULT TRUE,
    rent DECIMAL(10, 2) NOT NULL,
    block_no INT NOT NULL,
    owner_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (block_no) REFERENCES Block(block_no),
    FOREIGN KEY (owner_id) REFERENCES Owner(owner_id)
);

-- Create Tenant Table
CREATE TABLE Tenant (
    tenant_id VARCHAR(50) PRIMARY KEY,
    ten_name VARCHAR(255) NOT NULL,
    ten_pass VARCHAR(255) NOT NULL DEFAULT '12345678',
    rental_agreement_status VARCHAR(50) NOT NULL,
    room_no INT NOT NULL,
    FOREIGN KEY (room_no) REFERENCES Room(room_no)
);
ALTER TABLE Tenant ADD COLUMN agreement_expiration_date DATE;

CREATE TABLE Complaint (
    complain_id INT PRIMARY KEY AUTO_INCREMENT,
    complaint_text TEXT NOT NULL,
    block_no INT NOT NULL,
    room_no INT NOT NULL,
    complaint_status ENUM('pending', 'resolved') default 'pending',
    FOREIGN KEY (block_no) REFERENCES Block(block_no),
    FOREIGN KEY (room_no) REFERENCES Room(room_no)
);

CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id VARCHAR(50) NOT NULL,
    room_no INT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('paid', 'pending') NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES Tenant(tenant_id),
    FOREIGN KEY (room_no) REFERENCES Room(room_no)
);
desc payment;
ALTER TABLE Complaint CHANGE complain_id complaint_id INT AUTO_INCREMENT PRIMARY KEY;

DESCRIBE Complaint;
ALTER TABLE Complaint 
MODIFY COLUMN complaint_id INT AUTO_INCREMENT PRIMARY KEY;

-- Triggers
DELIMITER //

CREATE TRIGGER prevent_duplicate_room_assignment
BEFORE INSERT ON Tenant
FOR EACH ROW
BEGIN
    DECLARE room_occupied INT;

    -- Check if the room is already occupied by another tenant
    SELECT COUNT(*) INTO room_occupied
    FROM Tenant
    WHERE room_no = NEW.room_no;

    -- If the room is occupied, prevent the insertion
    IF room_occupied > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: This room is already occupied by another tenant.';
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER set_payment_amount
BEFORE INSERT ON Payment
FOR EACH ROW
BEGIN
    DECLARE room_rent DECIMAL(10, 2);
    
    -- Get the rent for the room from the Room table
    SELECT rent INTO room_rent
    FROM Room
    WHERE room_no = NEW.room_no;
    
    -- Set the payment amount
    SET NEW.amount = room_rent;
END; //

DELIMITER ;

DELIMITER //

CREATE TRIGGER update_payment_status
BEFORE INSERT ON Payment
FOR EACH ROW
BEGIN
    DECLARE rental_status VARCHAR(50);
    
    -- Get the rental agreement status for the tenant
    SELECT rental_agreement_status INTO rental_status
    FROM Tenant
    WHERE tenant_id = NEW.tenant_id;
    
    -- Set payment status based on rental agreement status
    IF rental_status = 'expired' THEN
        SET NEW.payment_status = 'pending';
    ELSE
        SET NEW.payment_status = 'paid'; -- or any other status logic you prefer
    END IF;
END; //

DELIMITER ;

-- functions and procedures
DELIMITER $$

CREATE PROCEDURE check_tenant_password(IN tenant_id_param VARCHAR(50), IN password_param VARCHAR(255))
BEGIN
    DECLARE tenant_password VARCHAR(255);
    
    -- Get the tenant password from the database
    SELECT ten_pass INTO tenant_password
    FROM Tenant
    WHERE tenant_id = tenant_id_param;

    -- Check if the password matches
    IF tenant_password IS NULL THEN
        SELECT 'Tenant ID not found' AS message;
    ELSEIF tenant_password != password_param THEN
        SELECT 'Invalid password' AS message;
    ELSE
        SELECT 'Login successful' AS message;
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE check_owner_password(IN owner_id_param VARCHAR(50), IN password_param VARCHAR(255))
BEGIN
    DECLARE owner_password VARCHAR(255);
    
    -- Get the owner password from the database
    SELECT owner_pass INTO owner_password
    FROM Owner
    WHERE owner_id = owner_id_param;

    -- Check if the password matches
    IF owner_password IS NULL THEN
        SELECT 'Owner ID not found' AS message;
    ELSEIF owner_password != password_param THEN
        SELECT 'Invalid password' AS message;
    ELSE
        SELECT 'Login successful' AS message;
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE check_employee_password(IN emp_id_param VARCHAR(50), IN password_param VARCHAR(255))
BEGIN
    DECLARE emp_password VARCHAR(255);
    
    -- Get the employee password from the database
    SELECT emp_pass INTO emp_password
    FROM Employee
    WHERE emp_id = emp_id_param;

    -- Check if the password matches
    IF emp_password IS NULL THEN
        SELECT 'Employee ID not found' AS message;
    ELSEIF emp_password != password_param THEN
        SELECT 'Invalid password' AS message;
    ELSE
        SELECT 'Login successful' AS message;
    END IF;
END $$

DELIMITER ;

CALL check_employee_password('wrong_emp', 'mysql123');

INSERT INTO Owner (owner_id, owner_name, contact_no, owner_pass) VALUES
('OWN121', 'Amit Sharma', '9876543210', 'mysql123'),
('OWN131', 'Priya Patel', '8765432109', 'mysql123');

INSERT INTO Employee (emp_id, emp_name, emp_type, emp_pass, block_no) VALUES
('EMPL121', 'Rajesh Kumar', 'block_admin', 'mysql123', 12),
('EMPL122', 'Sneha Verma', 'staff', 'mysql123', 12),
('EMPL131', 'Anil Singh', 'block_admin', 'mysql123', 13),
('EMPL132', 'Nisha Gupta', 'staff', 'mysql123', 13);

INSERT INTO Block (block_no, emp_id) VALUES
(12, 'EMPL121'),
(13, 'EMPL131');

INSERT INTO Room (room_no, type, rent, block_no, owner_id) VALUES
(1201, '2BHK', 15000.00, 12, 'OWN121'),
(1202, '1BHK', 12000.00, 12, 'OWN121'),
(1301, '3BHK', 20000.00, 13, 'OWN131'),
(1302, '2BHK', 18000.00, 13, 'OWN131');

INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) VALUES
('TEN121', 'Suresh Rao', 'mysql123', 'expired', 1201, '2023-10-31'),
('TEN131', 'Geeta Iyer', 'mysql123', 'expired', 1301, '2023-10-31');

INSERT INTO Payment (tenant_id, room_no, payment_date, amount, payment_status) VALUES
('TEN121', 1201, '2022-10-31', 15000.00, 'pending'),
('TEN131', 1301, '2022-10-31', 20000.00, 'pending');

-- Insert Additional Tenants
INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) VALUES
('TEN122', 'Vikram Joshi', 'mysql123', 'renewed', 1202, '2024-10-31'),
('TEN132', 'Kavita Mehta', 'mysql123', 'renewed', 1302, '2024-10-31');

-- Insert Payments for New Tenants
INSERT INTO Payment (tenant_id, room_no, payment_date, amount, payment_status) VALUES
('TEN122', 1202, '2024-10-31', 12000.00, 'paid'),
('TEN132', 1302, '2024-10-31', 18000.00, 'paid');

INSERT INTO Room (room_no, type, rent, block_no, owner_id)
VALUES (1203, '2BHK', 15000.00, 12, 'OWN121');

INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date)
VALUES ('TEN123', 'Rahul Sharma', 'mysql123', 'expired', 1203, '2023-10-31');

INSERT INTO Payment (tenant_id, room_no, payment_date)
VALUES ('TEN123', 1203, '2023-10-31');

-- NEW
INSERT INTO Room (room_no, type, rent, block_no, owner_id)
VALUES (1303, '2BHK', 16000.00, 13, 'OWN131');

INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date)
VALUES ('TEN133', 'Ankit Patel', 'mysql123', 'expired', 1303, '2023-10-30');

INSERT INTO Payment (tenant_id, room_no, payment_date)
VALUES ('TEN133', 1303, '2023-10-30');

select * from Room where room_no = 1303;
select * from Payment where room_no = 1303;
select * from Tenant where room_no = 1303;































-- EXTRA STUFF - IGNORE --
INSERT INTO Owner (owner_id, owner_name, contact_no, owner_pass) VALUES ('OW123', 'John Doe', '1234567890', 'mysql123');
INSERT INTO Owner (owner_id, owner_name, contact_no, owner_pass) VALUES
('OW456', 'Alice Johnson', '1234567890', 'mysql123'),
('OW789', 'Bob Smith', '0987654321', 'mysql123');

INSERT INTO Employee (emp_id, emp_name, emp_type, emp_pass, block_no) VALUES
('EM123', 'Doe Smith', 'block_admin', 'mysql123', 1),
('EM234', 'Jane Smith', 'block_admin', 'mysql123', 2),
('EM345', 'Alice Brown', 'staff', 'mysql123', 1),
('EM456', 'Bob White', 'staff', 'mysql123', 2);

INSERT INTO Block (block_no, emp_id) VALUES
(1, 'EM123'),  -- Block 1, admin is EM123
(2, 'EM234');  -- Block 2, admin is EM234

INSERT INTO Room (room_no, type, parking_slot, rent, block_no, owner_id) VALUES
(101, '1BHK', TRUE, 1000.00, 1, 'OW123'),
(102, '2BHK', TRUE, 1500.00, 1, 'OW456'),
(103, '3BHK', TRUE, 2000.00, 1, 'OW789'),
(104, '1BHK', FALSE, 1100.00, 1, 'OW123'),
(105, '2BHK', TRUE, 1600.00, 1, 'OW456'),
(201, '1BHK', TRUE, 1200.00, 2, 'OW123'),
(202, '2BHK', TRUE, 1700.00, 2, 'OW456'),
(203, '3BHK', FALSE, 2500.00, 2, 'OW789'),
(204, '2BHK', TRUE, 1800.00, 2, 'OW123'),
(205, '1BHK', TRUE, 1300.00, 2, 'OW789');

INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) VALUES
('TE1', 'Michael Green', 'mysql123', 'renewed', 101, '2024-12-31'),
('TE2', 'Sara White', 'mysql123', 'renewed', 102, '2025-06-30'),
('TE3', 'Laura Black', 'mysql123', 'expired', 103, '2024-08-31'),
('TE4', 'David Blue', 'mysql123', 'renewed', 104, '2025-01-15'),
('TE5', 'Emma Gray', 'mysql123', 'renewed', 105, '2025-03-20');



INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) 
VALUES ('TE6', 'John Doe', 'password123', 'renewed', 201, '2024-12-31');

select * from complaint;

use db_project3;

DELIMITER //

CREATE TRIGGER check_duplicate_owner_id
BEFORE INSERT ON Owner
FOR EACH ROW
BEGIN
    DECLARE duplicate_count INT;
    
    -- Check for existing owner_id in the Owner table
    SELECT COUNT(*) INTO duplicate_count 
    FROM Owner 
    WHERE owner_id = NEW.owner_id;
    
    -- If duplicate is found, throw an error
    IF duplicate_count > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Duplicate owner_id found in Owner table';
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER check_duplicate_tenant_id 
BEFORE INSERT ON Tenant 
FOR EACH ROW
BEGIN
    DECLARE duplicate_count INT DEFAULT 0;
    
    -- Check for existing tenant_id in the Tenant table
    SELECT COUNT(*) INTO duplicate_count 
    FROM Tenant 
    WHERE tenant_id = NEW.tenant_id;
    
    -- If duplicate is found, throw an error
    IF duplicate_count > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Duplicate tenant_id found in Tenant table';
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER check_duplicate_employee_id 
BEFORE INSERT ON Employee 
FOR EACH ROW
BEGIN
    DECLARE duplicate_count INT DEFAULT 0;
    
    -- Check for existing emp_id in the Employee table
    SELECT COUNT(*) INTO duplicate_count 
    FROM Employee 
    WHERE emp_id = NEW.emp_id;
    
    -- If duplicate is found, throw an error
    IF duplicate_count > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Duplicate emp_id found in Employee table';
    END IF;
END //

DELIMITER ;

INSERT INTO Payment (tenant_id, room_no, payment_date, amount, payment_status) VALUES
('TE1', 101, '2024-01-15', 1000.00, 'paid'),         -- Rental status: renewed
('TE2', 102, '2024-01-10', 1500.00, 'paid'),         -- Rental status: renewed
('TE3', 103, '2024-01-05', 2000.00, 'pending'),      -- Rental status: expired
('TE4', 104, '2024-01-20', 1100.00, 'paid'),         -- Rental status: renewed
('TE5', 105, '2024-01-25', 1600.00, 'paid'),         -- Rental status: renewed
('TE6', 201, '2024-01-30', 1200.00, 'paid');         -- Rental status: renewed

INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) 
VALUES ('TE7', 'Jane Doe', 'mysql123', 'expired', 202, '2024-10-31');

select * from payment;

INSERT INTO Payment (tenant_id, room_no, payment_date, amount, payment_status)
VALUES ('TE7', 202, '2023-10-31', 2000.00, 'pending');

delete from tenant where tenant_id = 'TE7';



use db_project3;

desc room;

INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) VALUES
('TE12', 'Priya Sharma', 'mysql123', 'expired', 203, '2024-07-31'),
('TE13', 'Raj Patel', 'mysql123', 'expired', 204, '2024-08-15'),
('TE14', 'Neha Verma', 'mysql123', 'expired', 205, '2024-06-20');

INSERT INTO Payment (tenant_id, room_no, payment_date, amount, payment_status) VALUES
('TE12', 203, '2024-02-02', 1300.00, 'pending'),   -- Rental status: expired
('TE13', 204, '2024-02-03', 1400.00, 'pending'),   -- Rental status: expired
('TE14', 205, '2024-02-04', 1500.00, 'pending');   -- Rental status: expired

use db_project3;
-- Inserting a new owner for block 3
INSERT INTO Owner (owner_id, owner_name, contact_no, owner_pass) VALUES 
('OW999', 'Alice Green', '5551234567', 'mysql123');

-- Inserting a new employee for block 3
INSERT INTO Employee (emp_id, emp_name, emp_type, emp_pass, block_no) VALUES 
('EM567', 'Charlie Black', 'block_admin', 'mysql123', 3);

-- Inserting a new room for block 3
INSERT INTO Room (room_no, type, rent, block_no, owner_id) VALUES 
(301, '2BHK', 1800.00, 3, 'OW999');

-- Inserting a new tenant for block 3 with expired rental agreement status
INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) VALUES 
('TE6', 'Tom Brown', 'mysql123', 'expired', 301, '2024-11-04');  -- Assuming today's date as expiration date

-- Deleting the existing block_admin for block 3
DELETE FROM Employee WHERE emp_type = 'block_admin' AND block_no = 3;

-- Inserting a new employee for block 3
INSERT INTO Employee (emp_id, emp_name, emp_type, emp_pass, block_no) VALUES 
('EM567', 'Charlie Black', 'block_admin', 'mysql123', 3);

select * from room, tenant;

-- Inserting a new owner for block 7
INSERT INTO Owner (owner_id, owner_name, contact_no, owner_pass) VALUES 
('OW1001', 'Emily Johnson', '5559876543', 'mysql123');

-- Inserting a new employee for block 7
INSERT INTO Employee (emp_id, emp_name, emp_type, emp_pass, block_no) VALUES 
('EM569', 'Michael Blue', 'block_admin', 'mysql123', 7);

-- Inserting a new block with block number 7 and an employee assigned to it
INSERT INTO Block (block_no, emp_id) VALUES 
(7, 'EM569');  -- Assuming 'EM569' is the ID of the employee you want to assign as the admin


-- Inserting a new room for block 7
INSERT INTO Room (room_no, type, rent, block_no, owner_id) VALUES 
(701, '2BHK', 2000.00, 7, 'OW1001');

-- Inserting a new tenant for block 7 with expired rental agreement status
INSERT INTO Tenant (tenant_id, ten_name, ten_pass, rental_agreement_status, room_no, agreement_expiration_date) VALUES 
('TE8', 'Sarah Green', 'mysql123', 'expired', 701, '2024-11-04');  -- Expired status

-- Inserting a new payment for tenant TE8 with pending status
INSERT INTO Payment (tenant_id, room_no, payment_date, amount, payment_status)
VALUES ('TE8', 701, '2023-10-31', 2000.00, 'pending');  -- Pending status

use db_project3;
select * from tenant;



















