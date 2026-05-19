# Hospital Management System with Data Provenance and Lineage Tracking

## Overview
This project is a data provenance and lineage system integrated with Hospital Management System developed using Flask as part of my DBMS and web development learning. The main idea behind this project is not just managing hospital data, but also tracking how the data changes over time using data provenance and lineage concepts.
It simulates basic hospital operations like managing patients, doctors, and appointments, along with keeping a proper record of all changes made to patient data such as creation, updates, and deletions.

## Features
### Patient Management
- Add new patients with basic details like name, age, and disease
- Update patient information when required
- Delete patient records (only allowed for admin)
- Search patients by name or disease

### Doctor Management
- Add doctors with their specialization
- View list of all available doctors

### Appointment System
- Book appointments between patients and doctors
- Update appointment status like pending, completed, or cancelled
- View all appointments in one place

### Data Provenance and Lineage Tracking
- Tracks all changes made to patient records
- Stores details like who made the change, when it was made, and what was changed
- Supports CREATE, UPDATE, and DELETE tracking
- Helps maintain transparency in data handling

### Activity Logs
- Keeps backend logs of important actions happening in the system
- Useful for tracking system activity and debugging

### Role-Based Access
- Admin: full access including delete operations
- Doctor: access to view and manage medical data
- Receptionist: limited access for adding and managing appointments

## Tech Stack Used
- Backend: Flask (Python)
- Frontend: HTML, CSS (Jinja2 templates)
- Database: SQLite
- Language: Python
- Version Control: Git and GitHub

## Database Structure
The project uses SQLite as the database and contains the following tables:
- users
- patients
- doctors
- appointments
- provenance (for tracking data changes)
- activity_log (for system logs)

## About Data Lineage
Data lineage basically means tracking the journey of data. In this project, it helps in understanding how patient records are created, updated, and deleted over time and who performed those actions.
Each change is stored with:
- User details
- Timestamp
- Type of action (CREATE / UPDATE / DELETE)
- Description of the change

## Project Structure
hospital-project/
│
├── app.py
├── config.py
├── database.py
├── models.py
├── hospital.db
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── update.html
│   ├── patient_profile.html
│   ├── appointments.html
│   ├── activity_logs.html
│
├── static/
│   └── style.css

## How to Run the Project

### Install Dependencies
pip install flask

### Run the Application
python app.py

### Open in Browser
http://127.0.0.1:5000/

## Default Login Credentials
Admin: admin / admin  
Doctor: doctor1 / doctor  
Receptionist: reception / 123  

## Future Improvements
- Integration with MySQL or PostgreSQL
- Cloud deployment of the application
- Improved authentication using Flask-Login
- Advanced analytics dashboard
- Real-time notifications system

## Author
This project is developed as a DBMS and Web Development academic project demonstrating hospital management with data provenance and lineage tracking using Flask.

## License
This project is for academic purposes only.
