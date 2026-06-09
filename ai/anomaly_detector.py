from database import get_db
from datetime import datetime, timedelta


def check_high_activity():

    conn = get_db()
    cur = conn.cursor()

    ten_minutes_ago = (
        datetime.now() - timedelta(minutes=10)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT COUNT(*) as count
        FROM activity_log
        WHERE timestamp >= ?
    """, (ten_minutes_ago,))

    count = cur.fetchone()['count']

    alert_generated = False

   
    if count > 20:

        cur.execute("""
            INSERT INTO anomaly_alerts
            (alert_type, description, timestamp)
            VALUES (?, ?, ?)
        """, (
            "HIGH_ACTIVITY",
            "More than 3 actions detected in 10 minutes",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        alert_generated = True

    conn.commit()
    conn.close()

    return alert_generated

def check_suspicious_user(user):

    conn = get_db()
    cur = conn.cursor()

    ten_minutes_ago = (
        datetime.now() - timedelta(minutes=10)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT COUNT(*) as count
        FROM activity_log
        WHERE user = ?
        AND timestamp >= ?
    """, (user, ten_minutes_ago))

    count = cur.fetchone()['count']

    alert_generated = False

    if count > 10:

        cur.execute("""
            INSERT INTO anomaly_alerts
            (alert_type, description, timestamp)
            VALUES (?, ?, ?)
        """, (
            "SUSPICIOUS_USER",
            f"User {user} performed {count} actions in 10 minutes.",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        alert_generated = True

    conn.commit()
    conn.close()

    return alert_generated

def check_unusual_access(user):

    hour = datetime.now().hour

    if hour < 8 or hour > 20:

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO anomaly_alerts
            (alert_type, description, timestamp)
            VALUES (?, ?, ?)
        """, (
            "UNUSUAL_ACCESS",
            f"{user} accessed the system at {hour}:00.",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return True

    return False