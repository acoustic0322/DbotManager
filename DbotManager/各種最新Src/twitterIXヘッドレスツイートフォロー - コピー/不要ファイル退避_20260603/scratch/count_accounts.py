import sqlite3
import os

db_path = r"e:\twitterIXヘッドレスツイートフォロー\system.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM accounts")
        total = cursor.fetchone()[0]
        print(f"Total accounts: {total}")
        
        # Check is_alive
        cursor.execute("SELECT is_alive, COUNT(*) FROM accounts GROUP BY is_alive")
        alive_stats = cursor.fetchall()
        print("\nBreakdown by is_alive:")
        for alive, count in alive_stats:
            status_str = "Alive" if alive == 1 else "Dead/Unknown"
            print(f"- {status_str} ({alive}): {count}")
            
        # Check reach_status
        cursor.execute("SELECT reach_status, COUNT(*) FROM accounts GROUP BY reach_status")
        reach_stats = cursor.fetchall()
        print("\nBreakdown by reach_status:")
        for reach, count in reach_stats:
            print(f"- {reach}: {count}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")
