from database import get_db
from datetime import datetime
import random

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # ---------- USERS ----------
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT CHECK(role IN (
        'admin',
        'doctor',
        'nurse',
        'receptionist',
        'user'
    ))
    )''')

    # ---------- PATIENTS ----------
    cur.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        disease TEXT
    )''')

    # ---------- DOCTORS ----------
    cur.execute('''CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT
    )''')

    # ---------- APPOINTMENTS ----------
    cur.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id)
    )''')

    # ---------- PROVENANCE ----------
    cur.execute('''CREATE TABLE IF NOT EXISTS provenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        action TEXT,
        timestamp TEXT,
        user TEXT,
        details TEXT
    )''')

    # 🔥 NEW: ACTIVITY LOG TABLE
    cur.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        user TEXT,
        timestamp TEXT,
        details TEXT
    )''')

   # ---------- ANOMALY ALERTS ----------
    cur.execute('''CREATE TABLE IF NOT EXISTS anomaly_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT,
        description TEXT,
        timestamp TEXT
    )''')

   # ---------- DEFAULT USERS ----------
    cur.execute("INSERT OR IGNORE INTO users VALUES (1,'admin','admin','admin')")
    cur.execute("INSERT OR IGNORE INTO users VALUES (2,'doctor1','doctor','doctor')")
    cur.execute("INSERT OR IGNORE INTO users VALUES (3,'reception','123','receptionist')")
    cur.execute("INSERT OR IGNORE INTO users VALUES (4,'nurse1','nurse','nurse')")
    cur.execute("INSERT OR IGNORE INTO users VALUES (5,'user1','user','user')")

    # ---------- AUTO RANDOM DOCTORS ----------
    doctor_names = [
        "Dr. Sharma", "Dr. Mehta", "Dr. Patel",
        "Dr. Singh", "Dr. Gupta", "Dr. Verma",
        "Dr. Reddy", "Dr. Khan", "Dr. Das"
    ]

    specializations = [
        "Cardiologist", "Neurologist", "Orthopedic",
        "Dermatologist", "Pediatrician", "General Physician"
    ]

    cur.execute("SELECT COUNT(*) as count FROM doctors")
    count = cur.fetchone()['count']

    if count == 0:
        for i in range(6):
            name = random.choice(doctor_names)
            spec = random.choice(specializations)

            cur.execute("INSERT INTO doctors (name, specialization) VALUES (?,?)",
                        (name, spec))

    conn.commit()
    conn.close()


# ---------- PROVENANCE ----------
def log_provenance(pid, action, user, details=""):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''INSERT INTO provenance 
        (patient_id, action, timestamp, user, details)
        VALUES (?, ?, ?, ?, ?)''',
        (pid, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, details)
    )

    conn.commit()
    conn.close()


# ---------- 🔥 NEW: ACTIVITY LOGGER ----------
def log_activity(action, user, details=""):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''INSERT INTO activity_log 
        (action, user, timestamp, details)
        VALUES (?, ?, ?, ?)''',
        (action, user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details)
    )

    conn.commit()
    conn.close()

