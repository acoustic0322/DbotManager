import sqlite3
import os

DB_PATH = "system.db"

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    target = "アカウント監視"
    cursor.execute("SELECT count(*) FROM accounts WHERE group_name = ? OR category = ?", (target, target))
    count = cursor.fetchone()[0]
    print(f"Accounts with exactly '{target}': {count}")
    
    cursor.execute("SELECT count(*) FROM accounts WHERE group_name LIKE ? OR category LIKE ?", (f"%{target}%", f"%{target}%"))
    count_like = cursor.fetchone()[0]
    print(f"Accounts with LIKE '{target}': {count_like}")
    
    conn.close()
else:
    print("DB not found")
