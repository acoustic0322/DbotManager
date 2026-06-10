import sqlite3
import os
import sys

# Ensure UTF-8 output for console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

db_path = 'system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT category, COUNT(*) FROM accounts GROUP BY category')
    results = cursor.fetchall()
    print("Categories in DB:")
    for cat, count in results:
        print(f"[{cat}] : {count} accounts")
    conn.close()
