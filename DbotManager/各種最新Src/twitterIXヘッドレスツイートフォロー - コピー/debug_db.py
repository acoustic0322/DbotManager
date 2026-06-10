import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "system.db")

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM accounts WHERE is_alive = 0 OR sync_status LIKE '%凍結%'")
    count = cursor.fetchone()[0]
    print(f"Total frozen: {count}")
    
    # Check first 5
    cursor.execute("SELECT username, sync_status, is_alive FROM accounts WHERE is_alive = 0 OR sync_status LIKE '%凍結%' LIMIT 5")
    for r in cursor.fetchall():
        print(r)
    conn.close()
else:
    print("DB not found")
