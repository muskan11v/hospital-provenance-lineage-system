from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from database import get_db
from models import init_db, log_provenance, log_activity
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

init_db()
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

init_db()

# ---------- ROLE BASED ACCESS ----------
def role_required(allowed_roles):

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            if 'user' not in session:
                return redirect('/')

            if session.get('role') not in allowed_roles:
                flash("⛔ Access Denied: You are not authorized")
                return redirect('/dashboard')

            return f(*args, **kwargs)

        return wrapper

    return decorator

# ---------- LOGIN ----------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (request.form['username'], request.form['password']))
        user = cur.fetchone()

        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            flash("Login Successful")
            return redirect('/dashboard')
        else:
            flash("Invalid Credentials")

    return render_template('login.html')


# ---------- REGISTER ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                        (request.form['username'],
                         request.form['password'],
                         request.form['role']))
            conn.commit()
            flash("Account Created Successfully")
            return redirect('/')
        except:
            flash("User already exists")

    return render_template('register.html')


# ---------- DASHBOARD ----------
@app.route('/dashboard')
@role_required(['admin','doctor','nurse','receptionist','user'])
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()

    search = request.args.get('search', '')

    # Patients Search
    if search:
        cur.execute("SELECT * FROM patients WHERE name LIKE ? OR disease LIKE ?",
                    (f'%{search}%', f'%{search}%'))
    else:
        cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()

    # Doctors
    cur.execute("SELECT * FROM doctors")
    doctors = cur.fetchall()

    # Appointments
    cur.execute("""
        SELECT a.id, p.name as patient, d.name as doctor, a.date, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.date DESC
    """)
    appointments = cur.fetchall()

    # Stats
    cur.execute("SELECT COUNT(*) as total FROM patients")
    total_patients = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM doctors")
    total_doctors = cur.fetchone()['total']

    return render_template('dashboard.html',
        patients=patients,
        doctors=doctors,
        appointments=appointments,
        total_patients=total_patients,
        total_doctors=total_doctors,
        search=search
    )


# ---------- PATIENT PROFILE ----------
@app.route('/patient/<int:id>')
def patient_profile(id):
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()

    # Patient
    cur.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cur.fetchone()

    # Appointments
    cur.execute("""
        SELECT a.id, d.name as doctor, a.date, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id=?
        ORDER BY a.date DESC
    """, (id,))
    appointments = cur.fetchall()

    # Lineage
    cur.execute("SELECT * FROM provenance WHERE patient_id=?", (id,))
    logs = cur.fetchall()

    return render_template('patient_profile.html',
                           patient=patient,
                           appointments=appointments,
                           logs=logs)


# ---------- ALL APPOINTMENTS PAGE ----------
@app.route('/appointments')
def appointments_page():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.id, p.name as patient, d.name as doctor, a.date, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.date DESC
    """)
    data = cur.fetchall()

    return render_template('appointments.html', data=data)


# ---------- ADD PATIENT ----------
@app.route('/add', methods=['POST'])
@role_required(['admin','receptionist'])
def add():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO patients (name, age, disease) VALUES (?,?,?)",
                (request.form['name'], request.form['age'], request.form['disease']))
    pid = cur.lastrowid

    conn.commit()

    log_provenance(
    pid,
    "CREATE",
    session['user'],
    f"Created patient {request.form['name']}"
    )

    log_activity(
    "CREATE",
    session['user'],
    f"Added patient {request.form['name']}"
    )
    flash("Patient Added")
    return redirect('/dashboard')


# ---------- ADD DOCTOR ----------
@app.route('/add_doctor', methods=['POST'])
@role_required(['admin'])
def add_doctor():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO doctors (name, specialization) VALUES (?,?)",
                (request.form['name'], request.form['specialization']))

    conn.commit()
    log_activity(
    "CREATE",
    session['user'],
    f"Added doctor {request.form['name']}"
)
    flash("Doctor Added")
    return redirect('/dashboard')


# ---------- ADD APPOINTMENT ----------
@app.route('/add_appointment', methods=['POST'])
@role_required(['admin','nurse','receptionist'])
def add_appointment():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, status)
        VALUES (?,?,?,?)
    """,
    (request.form['patient_id'],
     request.form['doctor_id'],
     request.form['date'],
     "pending"))

    conn.commit()
    log_activity(
    "CREATE",
    session['user'],
    f"Booked appointment for patient ID {request.form['patient_id']}"
)
    flash("Appointment Booked")
    return redirect('/dashboard')


# ---------- UPDATE STATUS ----------
@app.route('/update_status/<int:id>/<status>')
@role_required(['admin','doctor','nurse'])
def update_status(id, status):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("UPDATE appointments SET status=? WHERE id=?", (status, id))
    conn.commit()

    log_activity(
    "UPDATE",
    session['user'],
    f"Updated appointment {id} to {status}"
)

    flash("Status Updated")
    return redirect('/dashboard')


# ---------- UPDATE PATIENT ----------
@app.route('/update/<int:id>', methods=['GET','POST'])
@role_required(['admin','doctor'])
def update(id):

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':

        cur.execute(
            "UPDATE patients SET name=?, age=?, disease=? WHERE id=?",
            (
                request.form['name'],
                request.form['age'],
                request.form['disease'],
                id
            )
        )

        conn.commit()

        log_provenance(
            id,
            "UPDATE",
            session['user'],
            f"Updated patient {request.form['name']}"
        )

        log_activity(
            "UPDATE",
            session['user'],
            f"Updated patient ID {id}"
        )

        flash("Patient Updated")

        return redirect('/dashboard')

    cur.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cur.fetchone()

    return render_template('update.html', p=patient)

# ---------- DELETE ----------
@app.route('/delete/<int:id>')
@role_required(['admin'])
def delete(id):
    if session.get('role') != 'admin':
        flash("Access Denied")
        return redirect('/dashboard')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM appointments WHERE patient_id=?", (id,))

    cur.execute("DELETE FROM patients WHERE id=?", (id,))
    
    conn.commit()

    log_provenance(id, "DELETE", session['user'], "Deleted via UI")
    log_activity("DELETE", session['user'], f"Deleted patient ID {id}")

    flash("Patient Deleted Successfully")
    return redirect('/dashboard')

# ---------- DATA LINEAGE ----------
@app.route('/lineage/<int:id>')
@role_required(['admin','doctor','nurse','receptionist','user'])
def lineage(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM provenance WHERE patient_id=? ORDER BY timestamp DESC",
        (id,)
    )

    logs = cur.fetchall()

    return render_template('lineage.html', logs=logs)

# ---------- ACTIVITY LOGS (BACKEND PROOF PAGE) ----------
@app.route('/activity_logs')
def activity_logs():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM activity_log ORDER BY timestamp DESC")
    logs = cur.fetchall()

    return render_template('activity_logs.html', logs=logs)



# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out")
    return redirect('/')
    

if __name__ == '__main__':
    app.run(debug=True)