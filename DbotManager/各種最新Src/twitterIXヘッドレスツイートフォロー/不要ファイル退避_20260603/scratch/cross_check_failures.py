import sqlite3
import json
import os

def cross_check():
    # 1. Load progress monitor failures
    fail_names = []
    if os.path.exists('data/task_progress.json'):
        with open('data/task_progress.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            fail_names = [item['name'] for item in data.get('fail_list', [])]
    
    print(f"Monitor Failure Names: {fail_names}")
    
    # 2. Check these names in DB
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()
    
    print("\n--- DB Check for Monitor Failures ---")
    for name in fail_names:
        # Try screen_name and username mapping
        cursor.execute("SELECT username, sync_status, is_alive FROM accounts WHERE username = ? OR name = ?", (name, name))
        results = cursor.fetchall()
        if not results:
            print(f"[{name}]: NOT FOUND IN DB")
        else:
            for r in results:
                print(f"[{name}] in DB: username={r[0]}, sync_status={repr(r[1])}, is_suspended={r[2]}")
    
    conn.close()

if __name__ == "__main__":
    cross_check()
