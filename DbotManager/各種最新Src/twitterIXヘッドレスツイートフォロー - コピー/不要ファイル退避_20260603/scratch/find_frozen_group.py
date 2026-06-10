import sqlite3
import os

db_path = r"e:\twitterIXヘッドレスツイートフォロー\system.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT group_name FROM accounts WHERE group_name LIKE '%凍結%'")
    results = cursor.fetchall()
    print("Groups found in DB:")
    for r in results:
        print(f"- {r[0]}")
    conn.close()
