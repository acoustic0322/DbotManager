import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

def main():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("--- Selected Accounts in Database ---")
    try:
        cursor.execute("SELECT username, selected, is_alive, assigned_pc, sync_status FROM accounts WHERE selected=1")
        rows = cursor.fetchall()
        print(f"Total selected: {len(rows)}")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error querying accounts: {e}")

if __name__ == "__main__":
    main()
