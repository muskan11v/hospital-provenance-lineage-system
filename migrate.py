import sqlite3
from config import DATABASE

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# Add new column safely
cur.execute("ALTER TABLE patients ADD COLUMN phone_number TEXT")

conn.commit()
conn.close()

print("Migration completed successfully")