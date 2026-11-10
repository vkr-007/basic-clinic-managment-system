# Clinic Management System

A single-page clinic dashboard built with Flask and MySQL for managing patient records, doctors, appointments and payments.

## Features
- Add and list patients
- List doctors
- Book appointments
- View appointments using SQL JOIN
- Search patients using LIKE
- Record payment and complete appointment in one ACID transaction
- Cancel appointments
- Database trigger writes to `Appointment_Audit`
- PK, FK, UNIQUE, NOT NULL, CHECK and DEFAULT constraints
- Indexes for common searches

## 1. Requirements
- Python 3.10+
- MySQL Server 8+
- VS Code (optional)

## 2. Create the database
1. Start MySQL.
2. Open MySQL Workbench or the MySQL command line.
3. Run the complete `schema.sql` file.
   It creates `clinic_db`, tables, constraints, indexes, trigger and sample data.

## 3. Install Python packages
Open a terminal in this project folder:

```bash
python -m venv venv
```

Windows:
```bash
venv\\Scripts\\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Then:
```bash
pip install -r requirements.txt
```

## 4. Configure MySQL
Default settings in `app.py` are:
- host: localhost
- user: root
- password: empty
- database: clinic_db

If your MySQL password is not empty, set it before running.

Windows PowerShell:
```powershell
$env:DB_PASSWORD="your_mysql_password"
```

macOS/Linux:
```bash
export DB_PASSWORD="your_mysql_password"
```

You can also edit `DB_CONFIG` in `app.py`.

## 5. Run
```bash
python app.py
```
Open http://127.0.0.1:5000

## Project structure
```text
clinic_management_system/
├── app.py
├── schema.sql
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   └── search.html
└── static/
    └── style.css
```

## Database concepts and queries
1. **ER model:** Patient 1:N Appointment; Doctor 1:N Appointment.
2. **Keys:** patient_id, doctor_id and appointment_id are primary keys; foreign keys connect tables.
3. **Constraints:** try adding the same phone twice or booking the same doctor's same date/time twice.
4. **Normalization:** Patient, Doctor and Appointment data are separated to avoid repeated patient/doctor details.
5. **JOIN:** appointments display patient and doctor names by joining three tables.
6. **Aggregate:** run `SELECT status, COUNT(*) FROM Appointment GROUP BY status;`.
7. **Trigger:** insert an appointment and inspect `SELECT * FROM Appointment_Audit;`.
8. **Index:** use `SHOW INDEX FROM Patient;`.
9. **Transaction:** use the Record Payment button. The route updates Appointment and inserts Payment in one transaction. If either step fails, it executes ROLLBACK.
10. **TCL:** demonstrate `START TRANSACTION`, `SAVEPOINT`, `ROLLBACK TO`, `ROLLBACK`, and `COMMIT` in MySQL Workbench.

## Project scope
This project covers the syllabus up to transaction and concurrency control. Recovery, security, data warehousing and advanced data transformation are intentionally outside the implementation scope.
