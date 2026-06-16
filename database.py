import sqlite3
from config import DATABASE


# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =========================
# INITIALIZE DATABASE
# =========================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # PATIENT TABLE (UPDATED: keeps disease + adds phone_number)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        disease TEXT,
        phone_number TEXT
    )
    ''')

    # BILLING TABLE (UNCHANGED - CORRECT)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        amount REAL NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
    ''')

    conn.commit()
    conn.close()


# =========================
# ADD PATIENT
# =========================
def add_patient(name, age, phone_number):
    conn = get_db()
    cur = conn.cursor()

    # NOTE: disease is NOT handled here (Flask handles full insert)
    cur.execute('''
        INSERT INTO patients (name, age, phone_number)
        VALUES (?, ?, ?)
    ''', (name, age, phone_number))

    conn.commit()
    conn.close()


# =========================
# CREATE BILL (AUTO bill_id)
# =========================
def create_bill(patient_id, amount, description, status='pending'):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO billing (patient_id, amount, description, status)
        VALUES (?, ?, ?, ?)
    ''', (patient_id, amount, description, status))

    conn.commit()
    conn.close()


# =========================
# GET BILLS FOR PATIENT
# =========================
def get_bills_by_patient(patient_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        SELECT * FROM billing WHERE patient_id = ?
    ''', (patient_id,))

    rows = cur.fetchall()
    conn.close()
    return rows