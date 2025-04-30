-- create database
CREATE DATABASE IF NOT EXISTS vuln_platform;

-- set vuln_platform as active database
use vuln_platform;

-- create users table
CREATE TABLE IF NOT EXISTS users (
	id INT AUTO_INCREMENT PRIMARY KEY,
	first_name VARCHAR(255) NOT NULL,
	last_name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL,
	user_hash VARCHAR(255) NOT NULL,
	phone_number VARCHAR(255),
	address VARCHAR(255),
	access_token VARCHAR(255),
	birth_place VARCHAR(255),
	posts_count INT,
	joined_at VARCHAR(255)
);

-- insert test data for proof-of-concept

-- first user
INSERT INTO users (first_name, last_name, email, password, user_hash, phone_number, address, access_token, birth_place, posts_count, joined_at) VALUES ("Leonhard", "Euler", "eulerThis@gmail.com", "b7a875fc1ea228b9061041b7cec4bd3c52ab3ce3", "de7834ea8e5d46f324f8ebd90fc0e4ce087ce819f2a1143aa8fb415975466523", "+00112233445566778899", "Russian Academy of Sciences", "3UL3R_SUP3R_S3CR37_4CC355_70K3N", "St. Petersburg", 1, "2023");
-- second user
INSERT INTO users (first_name, last_name, email, password, user_hash, phone_number, address, access_token, birth_place, posts_count, joined_at) VALUES ("Blaise", "Pascal", "theRealPascal@gmail.com", "cbfdac6008f9cab4083784cbd1874f76618d2a97", "5c95aaabe6051f31545a38077844f0d5f2315f06aa6b15d1760b0c2a1dc5f273", "+99887766554433221100", "N/A", "P4SC4L_SUP3R_S3CR37_4CC355_70K3N", "Paris", 1, "2024");
-- third user
INSERT INTO users (first_name, last_name, email, password, user_hash, phone_number, address, access_token, birth_place, posts_count, joined_at) VALUES ("Alan", "Turing", "alanT1912@gmail.com", "e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4", "d0e7bb27977618cc72847d7647e666bac69d8fef42033b0022b6db5ae56a0c24", "+01233210456654789987", "2 Forest Road", "TUR1NG_SUP3R_S3CR37_4CC355_70K3N", "Hampshire", 1, "2025");