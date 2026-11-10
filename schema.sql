CREATE DATABASE IF NOT EXISTS clinic_db;
USE clinic_db;

DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Prescription;
DROP TABLE IF EXISTS Appointment;
DROP TABLE IF EXISTS Doctor;
DROP TABLE IF EXISTS Patient;

CREATE TABLE Patient (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    age INT NOT NULL CHECK (age BETWEEN 0 AND 120),
    gender VARCHAR(10) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE
);

CREATE TABLE Doctor (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    specialization VARCHAR(60) NOT NULL,
    phone VARCHAR(15) UNIQUE
);

CREATE TABLE Appointment (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(15) NOT NULL DEFAULT 'Booked',
    CONSTRAINT fk_appointment_patient FOREIGN KEY (patient_id)
        REFERENCES Patient(patient_id),
    CONSTRAINT fk_appointment_doctor FOREIGN KEY (doctor_id)
        REFERENCES Doctor(doctor_id),
    CONSTRAINT chk_appointment_status
        CHECK (status IN ('Booked', 'Completed', 'Cancelled')),
    CONSTRAINT uq_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time)
);

CREATE TABLE Prescription (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    medicines VARCHAR(500) NOT NULL,
    notes VARCHAR(500),
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id)
);

CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    payment_status VARCHAR(15) NOT NULL DEFAULT 'Paid',
    paid_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id)
);

-- Indexes: speed up common searches and joins.
CREATE INDEX idx_patient_name ON Patient(name);
CREATE INDEX idx_appointment_date ON Appointment(appointment_date);
CREATE INDEX idx_appointment_patient ON Appointment(patient_id);

-- Trigger: a simple audit example for appointment insertion.
CREATE TABLE Appointment_Audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT,
    action_text VARCHAR(30),
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //
CREATE TRIGGER trg_appointment_insert
AFTER INSERT ON Appointment
FOR EACH ROW
BEGIN
    INSERT INTO Appointment_Audit(appointment_id, action_text)
    VALUES (NEW.appointment_id, 'APPOINTMENT CREATED');
END//
DELIMITER ;

-- Sample records
INSERT INTO Patient(name, age, gender, phone) VALUES
('Aarav Sharma', 21, 'Male', '9876500001'),
('Sara Khan', 24, 'Female', '9876500002'),
('Rohan Gupta', 35, 'Male', '9876500003');

INSERT INTO Doctor(name, specialization, phone) VALUES
('Dr. Meera', 'General Physician', '9000000001'),
('Dr. Arjun', 'Cardiologist', '9000000002'),
('Dr. Zoya', 'Dermatologist', '9000000003');

INSERT INTO Appointment(patient_id, doctor_id, appointment_date, appointment_time, status) VALUES
(1, 1, CURDATE(), '10:00:00', 'Booked'),
(2, 2, CURDATE(), '11:00:00', 'Booked'),
(3, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '12:00:00', 'Booked');

-- Useful syllabus demonstration queries
-- Selection + projection
-- SELECT name, phone FROM Patient WHERE age > 20;

-- JOIN
-- SELECT p.name, d.name, a.appointment_date
-- FROM Appointment a JOIN Patient p ON a.patient_id=p.patient_id
-- JOIN Doctor d ON a.doctor_id=d.doctor_id;

-- Aggregate + GROUP BY
-- SELECT status, COUNT(*) FROM Appointment GROUP BY status;

-- Subquery
-- SELECT name FROM Patient
-- WHERE patient_id IN (SELECT patient_id FROM Appointment);

-- UNION
-- SELECT name FROM Patient UNION SELECT name FROM Doctor;

-- EXISTS
-- SELECT p.name FROM Patient p
-- WHERE EXISTS (SELECT 1 FROM Appointment a WHERE a.patient_id=p.patient_id);

-- TCL demonstration (run manually)
-- START TRANSACTION;
-- UPDATE Appointment SET status='Cancelled' WHERE appointment_id=1;
-- SAVEPOINT after_update;
-- DELETE FROM Appointment_Audit WHERE appointment_id=1;
-- ROLLBACK TO after_update;
-- ROLLBACK; -- or COMMIT;
