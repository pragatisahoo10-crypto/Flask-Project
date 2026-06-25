CREATE DATABASE student_management_db;
USE student_management_db;

CREATE TABLE login (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100),
    password VARCHAR(500)
);

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE teachers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    designation VARCHAR(100)
);

CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100),
    duration VARCHAR(50)
);

CREATE TABLE teacher_course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT,
    course_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE student_course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    course_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

INSERT INTO login (username, password)
VALUES ('admin', '12345');

ALTER TABLE students ADD COLUMN is_deleted TINYINT(1) DEFAULT 0;
ALTER TABLE teachers ADD COLUMN is_deleted TINYINT(1) DEFAULT 0;
ALTER TABLE teachers ADD COLUMN designation VARCHAR(50);
ALTER TABLE courses ADD COLUMN is_deleted TINYINT(1) DEFAULT 0;
ALTER TABLE teachers DROP COLUMN is_deleted;

UPDATE students SET is_deleted=0 WHERE id=3;

TRUNCATE TABLE login;