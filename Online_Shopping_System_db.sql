CREATE DATABASE Online_Shopping_System_db;
USE Online_Shopping_System_db;

CREATE TABLE users(
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(100) NOT NULL,
email VARCHAR(100) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL,
phone VARCHAR(15),
address TEXT,
role ENUM('user','admin') DEFAULT 'user',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);
INSERT INTO users (username, email, password, role) VALUES ('Admin', 'admin@gmail.com', 'admin123', 'admin');

CREATE TABLE products(
id INT AUTO_INCREMENT PRIMARY KEY,
category_id INT,
name VARCHAR(100) NOT NULL,
description TEXT,
price DECIMAL (10,2) NOT NULL,
stock INT NOT NULL,
image VARCHAR(250),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (category_id)
REFERENCES categories(id)
ON DELETE SET NULL
);

INSERT INTO products(category_id, name, description, price, stock, image) VALUES (1, 'Laptop', 'HP Core i5 Laptop', 40000, 10, 'laptop.jpg'),
(2, 'Shirt', 'Pure Cotton', 2000, 10, 'shirt.jpg');

CREATE TABLE wishlist(
id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
product_id INT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE,

FOREIGN KEY(product_id)
REFERENCES products(id)
ON DELETE CASCADE,

UNIQUE(user_id, product_id)
);

CREATE TABLE orders(
id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
total DECIMAL(10,2),
status ENUM('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled')
DEFAULT 'Pending',
shipping_address TEXT,
phone VARCHAR(15),
payment_method VARCHAR(50),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

FOREIGN KEY(user_id)
REFERENCES users(id)
ON DELETE CASCADE
);

CREATE TABLE order_items(
id INT AUTO_INCREMENT PRIMARY KEY,
order_id INT,
product_id INT,
quantity INT,
price DECIMAL(10,2),

FOREIGN KEY(order_id)
REFERENCES orders(id)
ON DELETE CASCADE,

FOREIGN KEY(product_id)
REFERENCES products(id)
ON DELETE CASCADE
);
DESCRIBE categories;
SELECT * FROM categories;
SHOW TABLES;