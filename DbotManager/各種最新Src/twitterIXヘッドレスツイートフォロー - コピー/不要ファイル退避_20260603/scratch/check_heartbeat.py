import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

def main():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("--- Database Type ---")
    print(db.db_type)
    
    print("\n--- system_status Table ---")
    try:
        cursor.execute("SELECT * FROM system_status")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error querying system_status: {e}")
        
    print("\n--- system_commands Table ---")
    try:
        cursor.execute("SELECT * FROM system_commands ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error querying system_commands: {e}")

if __name__ == "__main__":
    main()
