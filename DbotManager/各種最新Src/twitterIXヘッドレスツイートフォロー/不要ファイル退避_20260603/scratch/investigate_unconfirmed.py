import sqlite3
import os

db_path = r"e:\twitterIXヘッドレスツイートフォロー\system.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Select some accounts with reach_status = '-'
        cursor.execute("SELECT username, is_alive, group_name, sync_status, profile_id FROM accounts WHERE reach_status = '-' LIMIT 10")
        samples = cursor.fetchall()
        
        print("Sample accounts with reach_status = '-':")
        for s in samples:
            print(f"User: {s[0]}, Alive: {s[1]}, Group: {s[2]}, Sync: {s[3]}, ProfileID: {s[4]}")
            
        # Check if they have a common sync_status or group
        cursor.execute("SELECT sync_status, COUNT(*) FROM accounts WHERE reach_status = '-' GROUP BY sync_status")
        sync_stats = cursor.fetchall()
        print("\nSync Status of these accounts:")
        for sync, count in sync_stats:
            print(f"- {sync}: {count}")

        cursor.execute("SELECT group_name, COUNT(*) FROM accounts WHERE reach_status = '-' GROUP BY group_name")
        group_stats = cursor.fetchall()
        print("\nGroup Name of these accounts:")
        for group, count in group_stats:
            print(f"- {group}: {count}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")
