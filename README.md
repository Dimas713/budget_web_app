# budget web app

## Overview

This flask application allows the user to connect to their bank account and aquire transaction information. This information generates a budget and a visiual representation of the data is presented.

## Dependencies 

* Ubuntu 20.4 or Ubuntu 22.04
* Run command in CMD
    - sudo apt update -y && sudo apt upgrade -y
    - sudo apt install python3-pip -y
    - sudo apt install postgresql postgresql-contrib
    - pip3 install flask, flask_login, flask_sqlalchemy, flask_sqlalchemy, flask_mail, itsdangerous==2.0.1, flask_wtf, email_validator, tabula, pdfplumber, pandas, psycopg2-binary
    
## PostgreSQL Configuration

* Log into psql using the default username "postgres"
    - sudo -i -u postgres
* Create a new user with superuser access 
    - createuser --interactive
* Create new password for new user 
    - \password <nameofuser>
* Create a new DB 
    - createdb <nameofDB>

## Set Enviromental Variables

The require enviromental variables are SQLALCHEMY_DATABASE_URI, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, SECRET_KEY.

* Below is an example of the varaiblae that need to be set:
    - SQLALCHEMY_DATABASE_URI="postgresql://DBuser:DBpassword@localhost:5432/nameofDB"
    - MAIL_SERVER="smtp.googlemail.com"
    - MAIL_PORT=587
    - MAIL_USE_TLS=True
    - MAIL_USERNAME="yourEmailaddress@gmail.com"
    - MAIL_PASSWORD="yourEmailPWorToken"
    - SECRET_KEY="somerandomstring123cdcvfvf"

## Create tables for Database

To create the tables the flask application uses run the following application
- python3 createDB/app.py

To Delete all tables in the database run the following application
- python3 createDB/app.py delete

## How to run the Budget web application 

The current budget application is in development and not ready for production. For this reason the application is being run in debug mode and using a developmental server.

To run budget app run the below command and log in using rhe default credentials email= user1@gmail.com and password= 1234
- python3 run.py