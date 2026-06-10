import json
import os
import sqlite3

BASE_DIR = r"e:\twitterIXヘッドレスツイートフォロー"
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.json")
DB_PATH = os.path.join(BASE_DIR, "system.db")

def check_scanner_count():
    count_from_file = 0
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, "r") as f:
                data = json.load(f)
                count_from_file = len(data)
        except:
            pass
            
    count_from_db = 0
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE auth_token != '' AND ct0 != '' AND is_alive = 1")
            count_from_db = cursor.fetchone()[0]
            conn.close()
        except:
            pass
            
    print(f"Scanner accounts in cookies.json: {count_from_file}")
    print(f"Alive accounts in DB: {count_from_db}")
    
    # check_full_status.py logic limits DB accounts to 20 if cookies.json is missing
    limit = 20
    effective_count = count_from_file if count_from_file > 0 else min(count_from_db, limit)
    print(f"Effective scanner pool size: {effective_count}")

if __name__ == "__main__":
    check_scanner_count()
