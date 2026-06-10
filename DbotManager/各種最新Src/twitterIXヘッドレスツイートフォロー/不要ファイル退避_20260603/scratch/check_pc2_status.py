import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

def main():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("--- PC_02 Accounts with non-empty sync_status ---")
    try:
        cursor.execute("SELECT username, last_active_date, last_tweet_at, sync_status FROM accounts WHERE assigned_pc='PC_02' AND (sync_status IS NOT NULL AND sync_status != '')")
        rows = cursor.fetchall()
        print(f"Total: {len(rows)}")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
