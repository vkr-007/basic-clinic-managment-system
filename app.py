from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clinic-demo-secret")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "VKR@bcse25044"),
    "database": os.getenv("DB_NAME", "clinic_db"),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def query(sql, params=(), fetch=True):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = cur.fetchall() if fetch else None
        conn.commit()
        return result
    finally:
        cur.close()
        conn.close()

@app.route("/")
def index():
    try:
        stats = query("""
            SELECT
              (SELECT COUNT(*) FROM Patient) AS patients,
              (SELECT COUNT(*) FROM Doctor) AS doctors,
              (SELECT COUNT(*) FROM Appointment) AS appointments,
              (SELECT COUNT(*) FROM Appointment WHERE status='Booked') AS booked
        """)[0]

        patients = query("SELECT * FROM Patient ORDER BY patient_id DESC")
        doctors = query("SELECT * FROM Doctor ORDER BY doctor_id")
        appointments = query("""
            SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status,
                   p.name AS patient_name, d.name AS doctor_name, d.specialization
            FROM Appointment a
            JOIN Patient p ON a.patient_id = p.patient_id
            JOIN Doctor d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """)
        payments = query("""
            SELECT pay.payment_id, pay.amount, pay.payment_status, pay.paid_on,
                   a.appointment_id, p.name AS patient_name
            FROM Payment pay
            JOIN Appointment a ON pay.appointment_id = a.appointment_id
            JOIN Patient p ON a.patient_id = p.patient_id
            ORDER BY pay.payment_id DESC
        """)
        return render_template("index.html", stats=stats, patients=patients,
                               doctors=doctors, appointments=appointments, payments=payments)
    except Error as e:
        return render_template("index.html", db_error=str(e), stats={}, patients=[],
                               doctors=[], appointments=[], payments=[])

@app.route("/patient", methods=["POST"])
def add_patient():
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "")
    phone = request.form.get("phone", "").strip()
    if not name or not age or not phone:
        flash("Please fill in all patient fields.", "error")
        return redirect(url_for("index"))
    try:
        query("INSERT INTO Patient(name, age, gender, phone) VALUES(%s,%s,%s,%s)",
              (name, int(age), gender, phone), fetch=False)
        flash("Patient added successfully.", "success")
    except (Error, ValueError) as e:
        flash(f"Could not add patient: {e}", "error")
    return redirect(url_for("index"))

@app.route("/appointment", methods=["POST"])
def add_appointment():
    try:
        query("""INSERT INTO Appointment(patient_id, doctor_id, appointment_date,
                  appointment_time, status) VALUES(%s,%s,%s,%s,'Booked')""",
              (request.form["patient_id"], request.form["doctor_id"],
               request.form["appointment_date"], request.form["appointment_time"]),
              fetch=False)
        flash("Appointment booked successfully.", "success")
    except Error as e:
        flash(f"Could not book appointment: {e}", "error")
    return redirect(url_for("index"))

@app.route("/complete-payment/<int:appointment_id>", methods=["POST"])
def complete_payment(appointment_id):
    # One transaction: update appointment + insert payment.
    # Both operations succeed together, or both are rolled back.
    conn = get_db()
    cur = conn.cursor()
    try:
        conn.start_transaction()
        cur.execute("SELECT status FROM Appointment WHERE appointment_id=%s FOR UPDATE",
                    (appointment_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Appointment not found.")
        cur.execute("SELECT payment_id FROM Payment WHERE appointment_id=%s",
                    (appointment_id,))
        if cur.fetchone():
            raise ValueError("Payment already exists for this appointment.")
        cur.execute("UPDATE Appointment SET status='Completed' WHERE appointment_id=%s",
                    (appointment_id,))
        cur.execute("""INSERT INTO Payment(appointment_id, amount, payment_status)
                       VALUES(%s, %s, 'Paid')""",
                    (appointment_id, request.form.get("amount", "500")))
        conn.commit()
        flash("Payment recorded and appointment completed (COMMIT).", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Transaction failed; changes rolled back: {e}", "error")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("index"))

@app.route("/cancel/<int:appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):
    try:
        query("UPDATE Appointment SET status='Cancelled' WHERE appointment_id=%s",
              (appointment_id,), fetch=False)
        flash("Appointment cancelled.", "success")
    except Error as e:
        flash(f"Could not cancel appointment: {e}", "error")
    return redirect(url_for("index"))

@app.route("/search")
def search():
    term = request.args.get("q", "").strip()
    try:
        results = query("""
            SELECT patient_id, name, age, gender, phone
            FROM Patient
            WHERE name LIKE %s OR phone LIKE %s
            ORDER BY name
        """, (f"%{term}%", f"%{term}%"))
        return render_template("search.html", results=results, term=term)
    except Error as e:
        flash(str(e), "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
