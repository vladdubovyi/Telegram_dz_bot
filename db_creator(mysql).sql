CREATE DATABASE Homework;
USE Homework;
CREATE TABLE homework (
	Id INT PRIMARY KEY AUTO_INCREMENT,
    Subject VARCHAR(64) NOT NULL,
    Homework_text VARCHAR(256) NOT NULL,
    Date DATE NOT NULL
);
CREATE TABLE users (
    UserId INT PRIMARY KEY,
    Status INT DEFAULT 0,
    FirstName VARCHAR(256),
    Date_of_registration DATE NOT NULL
);
SELECT * FROM users;
SELECT * FROM homework;
