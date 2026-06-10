import sqlite3
import os

db_path = 'system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # usernameがファイルパスっぽいものを探す
    cursor.execute("SELECT username, display_name, category FROM accounts WHERE username LIKE 'data/%' OR username LIKE '%/%'")
    rows = cursor.fetchall()
    
    if rows:
        print(f"Found {len(rows)} corrupted records:")
        for r in rows:
            print(f"Username: {r[0]} | DisplayName: {r[1]} | Category: {r[2]}")
    else:
        print("No corrupted records found in username column.")
    
    conn.close()
