import sqlite3
import os

db_path = r"e:\twitterIXヘッドレスツイートフォロー\system.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check auth_token and profile_id for reach_status = '-'
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE reach_status = '-' AND auth_token IS NOT NULL AND auth_token != ''")
        has_token = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE reach_status = '-' AND profile_id IS NOT NULL AND profile_id != ''")
        has_profile = cursor.fetchone()[0]
        
        print(f"Accounts with reach_status = '-': 111")
        print(f"- Has auth_token: {has_token}")
        print(f"- Has profile_id: {has_profile}")
        
        # Check if they have category
        cursor.execute("SELECT category, COUNT(*) FROM accounts WHERE reach_status = '-' GROUP BY category")
        cats = cursor.fetchall()
        print("\nCategories of these accounts:")
        for cat, count in cats:
            print(f"- {cat}: {count}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")
