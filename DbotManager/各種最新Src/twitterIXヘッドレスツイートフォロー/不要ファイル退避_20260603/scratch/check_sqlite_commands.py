import sqlite3
import os

DB_PATH = 'system.db'
if os.path.exists(DB_PATH):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_commands'")
        table_exists = cursor.fetchone()
        print("Table system_commands exists in local SQLite:", table_exists is not None)
        
        if table_exists:
            cursor.execute("SELECT * FROM system_commands ORDER BY id DESC LIMIT 5")
            commands = cursor.fetchall()
            print("Latest Local SQLite Commands:", commands)
            
            cursor.execute("SELECT count(*) FROM accounts")
            acc_count = cursor.fetchone()[0]
            print("Local accounts count:", acc_count)
            
        conn.close()
    except Exception as e:
        print("SQLite Error:", e)
else:
    print("Local system.db does not exist.")
