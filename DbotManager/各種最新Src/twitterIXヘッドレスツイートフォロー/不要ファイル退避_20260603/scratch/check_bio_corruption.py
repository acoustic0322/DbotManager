import sqlite3
import os

db_path = 'system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # biography や display_name にパスっぽいものが紛れ込んでいないか
    cursor.execute("SELECT username, display_name, biography FROM accounts WHERE biography LIKE 'data/%' OR display_name LIKE 'data/%'")
    rows = cursor.fetchall()
    
    if rows:
        print(f"Found {len(rows)} accounts with path-like data in biography/display_name:")
        for r in rows:
            print(f"User: {r[0]} | DisplayName: {r[1]} | Bio: {r[2]}")
    else:
        print("No accounts with path-like data found in biography/display_name.")
    
    conn.close()
