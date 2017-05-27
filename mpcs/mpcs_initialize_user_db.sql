# mpcs_initialize_user_db.sql
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
##

DROP DATABASE IF EXISTS meyermt_accounts;
CREATE DATABASE meyermt_accounts;

USE meyermt_accounts;

DROP TABLE IF EXISTS register;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
	`role` varchar(128) NOT NULL, 
	`level` integer(11) NOT NULL, 
	PRIMARY KEY (role)
);

CREATE TABLE users (
	`username` varchar(128) NOT NULL,
  `role` varchar(128) DEFAULT NULL,
  `hash` varchar(256) NOT NULL,
  `email_addr` varchar(128) DEFAULT NULL,
  `desc` varchar(128) DEFAULT NULL,
  `billing_id` varchar(128) DEFAULT NULL,
  `creation_date` varchar(128) NOT NULL,
  `last_login` varchar(128) NOT NULL,
  PRIMARY KEY (`username`),
  KEY `role` (`role`),
  CONSTRAINT users_ibfk_1 FOREIGN KEY (`role`) REFERENCES roles (`role`)
 );

CREATE TABLE register (
  `code` varchar(128) NOT NULL,
  `username` varchar(128) NOT NULL,
  `role` varchar(128) DEFAULT NULL,
  `hash` varchar(256) NOT NULL,
  `email_addr` varchar(128) DEFAULT NULL,
  `desc` varchar(128) DEFAULT NULL,
  `creation_date` varchar(128) NOT NULL,
  PRIMARY KEY (`code`),
  KEY `role` (`role`),
  CONSTRAINT register_ibfk_1 FOREIGN KEY (`role`) REFERENCES roles (`role`)
);

INSERT INTO roles (role, level) VALUES ('free_user', 10);
INSERT INTO roles (role, level) VALUES ('premium_user', 20);
INSERT INTO roles (role, level) VALUES ('admin_user', 200);
INSERT INTO roles (role, level) VALUES ('super_user', 500);
