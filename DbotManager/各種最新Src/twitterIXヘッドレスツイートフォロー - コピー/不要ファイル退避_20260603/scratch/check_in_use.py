import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

def main():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("--- Accounts with in_use = 1 ---")
    try:
        cursor.execute("SELECT username, assigned_pc, sync_status, in_use FROM accounts WHERE in_use = 1")
        rows = cursor.fetchall()
        print(f"Total in_use = 1: {len(rows)}")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error checking in_use: {e}")

    print("\n--- Accounts with sync_status containing '実行中' ---")
    try:
        cursor.execute("SELECT username, assigned_pc, sync_status, in_use FROM accounts WHERE sync_status LIKE '%実行中%'")
        rows = cursor.fetchall()
        print(f"Total: {len(rows)}")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error checking sync_status: {e}")

if __name__ == "__main__":
    main()
