import sqlite3
import os
import json

BASE_DIR = r"e:\twitterIXヘッドレスツイートフォロー"
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.json")
DB_PATH = os.path.join(BASE_DIR, "system.db")

def test_load():
    scanner_pool = []
    seen_usernames = set()

    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            file_accs = json.load(f)
            for acc in file_accs:
                twid = acc.get("twid") or acc.get("username")
                if twid:
                    seen_usernames.add(twid)
                scanner_pool.append(acc)
        print(f"Loaded {len(file_accs)} scanners from cookies.json")

    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT auth_token, ct0, username FROM accounts WHERE auth_token != '' AND ct0 != '' AND is_alive = 1")
        rows = cursor.fetchall()
        conn.close()
        
        added_from_db = 0
        for r in rows:
            if r[2] not in seen_usernames:
                scanner_pool.append({"auth_token": r[0], "ct0": r[1], "twid": r[2]})
                seen_usernames.add(r[2])
                added_from_db += 1
        print(f"Added {added_from_db} scanners from system.db (Total pool: {len(scanner_pool)})")

test_load()
