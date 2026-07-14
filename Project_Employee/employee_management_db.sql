CREATE database employee_management_db;
USE employee_management_db;

CREATE TABLE login(
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL
);

INSERT INTO login (username, password) VALUES ('admin','admin123');

CREATE TABLE employee(
id INT AUTO_INCREMENT PRIMARY KEY,
emp_code VARCHAR(20) NOT NULL UNIQUE,
name VARCHAR(100) NOT NULL,
email VARCHAR(100),
department VARCHAR(100),
designation VARCHAR(100),
joining_date DATE,
basic_salary DECIMAL(10,2) DEFAULT 0.00,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
CREATE TABLE attendance(
id INT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
attendance_date DATE NOT NULL,
status ENUM ('Present','Absent') NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_attendance_employee
FOREIGN KEY(employee_id)
REFERENCES employee(id)
ON DELETE CASCADE
);

CREATE TABLE payroll(
id INT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
pay_month VARCHAR(30) NOT NULL,
bonus DECIMAL(10,2) DEFAULT 0.00,
deduction DECIMAL(10,2) DEFAULT 0.00,
net_salary DECIMAL(10,2) DEFAULT 0.00,
status ENUM('Paid','Pending') DEFAULT 'Pending',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_payroll_employee
FOREIGN KEY(employee_id)
REFERENCES employee(id)
ON DELETE CASCADE
);

INSERT INTO employee(emp_code, name, email, department, designation, joining_date, basic_salary)
VALUES('EMP001','John Smith','john@gmail.com','IT','Manager','2025-01-10',50000),
('EMP002','Liza','liza@rediffmail.com','HR','HR Manager','2025-02-20',40000);

INSERT INTO attendance(employee_id, attendance_date, status) VALUES 
(1, CURDATE(),'Present'),
(2, CURDATE(), 'Present'),
(3, CURDATE(), 'Absent');

INSERT INTO payroll (employee_id, pay_month, bonus, deduction, net_salary, status)
VALUES(1, 'June 2026', 5000, 1000, 54000, 'Paid'),
(2, 'June 2026', 4000, 2000, 42000, 'Pending')
