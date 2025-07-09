# Syamala1504_SPM.github.io

Student Personal Manager (SPM) is a lightweight web application designed to help students manage their personal academic tasks with ease. It enables students to create, update, and view their notes, upload important documents, and store everything in one organized place.

This application is especially useful for keeping track of study material, to-do items, lecture notes, and project files. All data is securely stored and personalized to each student through user authentication.

Key features of SPM include:

Secure login & registration with email verification
Note creation, editing, and deletion
File upload and download functionality
Password reset via email link
Beautiful and responsive user interface

Flask Dependencies:
pip install flask Flask-Session mysql-connector-python itsdangerous

SQL tables:
-- 📌 DROP and CREATE DATABASE
DROP DATABASE IF EXISTS spm;
CREATE DATABASE spm;
USE spm;

-- 🧑‍💼 USER TABLE
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

-- Sample Users
INSERT INTO user (name, email, password) VALUES
('Syamala', 'syamaladevi.pitchika@sasi.ac.in', '1234'),
('Priyanka', 'ramya.gudala@sasi.ac.in', '1234'),
('Jhansi', 'jhansi.reddy@sasi.ac.in', '1234');

-- 📝 NOTES TABLE
CREATE TABLE notes (
    notes_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    u_id INT,
    FOREIGN KEY (u_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Sample Notes
INSERT INTO notes (title, description, u_id) VALUES
('CSS', 'Cascading Style Sheets basics', 2),
('Summy', 'Summy is a beautiful girl.', 2);

-- 📂 FILES TABLE
CREATE TABLE files (
    fid INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(100) NOT NULL,
    filedata LONGBLOB,
    u_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (u_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Sample File Entry (dummy file content)
INSERT INTO files (filename, filedata, u_id)
VALUES ('keys.py', 'Sample binary content of keys.py', 2);
