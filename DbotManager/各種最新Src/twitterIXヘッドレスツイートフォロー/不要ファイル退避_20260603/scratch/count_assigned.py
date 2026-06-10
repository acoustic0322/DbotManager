import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

def main():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("--- Account Counts by assigned_pc where selected=1 ---")
    try:
        if db.db_type == "postgres":
            cursor.execute("SELECT assigned_pc, count(*) FROM accounts WHERE selected=1 GROUP BY assigned_pc")
        else:
            cursor.execute("SELECT assigned_pc, count(*) FROM accounts WHERE selected=1 GROUP BY assigned_pc")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
