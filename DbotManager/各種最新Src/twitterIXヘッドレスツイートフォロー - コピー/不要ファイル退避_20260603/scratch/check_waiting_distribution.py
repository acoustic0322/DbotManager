import sqlite3
import os

db_path = r"e:\twitterIXヘッドレスツイートフォロー\system.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 全アカウントを順番通りに取得
    cursor.execute("SELECT username, sync_status FROM accounts")
    rows = cursor.fetchall()
    
    total = len(rows)
    waiting_indices = [i for i, r in enumerate(rows) if r[1] == '待機中']
    
    if waiting_indices:
        print(f"Total accounts: {total}")
        print(f"Number of '待機中': {len(waiting_indices)}")
        print(f"First '待機中' at index: {min(waiting_indices)}")
        print(f"Last '待機中' at index: {max(waiting_indices)}")
        
        # どのあたりのレンジに多いか
        ranges = 10
        chunk_size = total // ranges
        for i in range(ranges):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < ranges - 1 else total
            count = sum(1 for idx in waiting_indices if start <= idx < end)
            print(f"Range {start:4} - {end:4}: {count} accounts waiting")
    else:
        print("No accounts are currently in '待機中' state.")
    
    conn.close()
