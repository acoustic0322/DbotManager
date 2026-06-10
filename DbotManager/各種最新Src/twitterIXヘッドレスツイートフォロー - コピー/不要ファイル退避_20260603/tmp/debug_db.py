import sqlite3
import os

db_path = 'system.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT username, name, biography, category FROM accounts LIMIT 5')
    rows = c.fetchall()
    print("--- Database Sample ---")
    for r in rows:
        print(f"User: {r[0]}, Name: {r[1]}, Bio: {r[2][:30]}..., Cat: {r[3]}")
    conn.close()
