import sqlite3
import time

ids = [
    'bazubazu1021', 'iz_iced', 'M__MJ42', 'gacchan_men', 
    'vodka012_3o6', 'Luna_05310', 'sa_ku3150', 'clover4281s4'
]

db_path = 'system.db'

for attempt in range(5):
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(ids))
        
        # まず現在の状態を確認
        cursor.execute(f"SELECT username, is_alive FROM accounts WHERE username IN ({placeholders})", ids)
        before = cursor.fetchall()
        print(f"Before update: {before}")
        
        # 更新実行
        cursor.execute(f'UPDATE accounts SET is_alive = 1, sync_status = NULL WHERE username IN ({placeholders})', ids)
        conn.commit()
        
        # 更新後の状態を確認
        cursor.execute(f"SELECT username, is_alive FROM accounts WHERE username IN ({placeholders})", ids)
        after = cursor.fetchall()
        print(f"After update: {after}")
        
        conn.close()
        print("Update process finished.")
        break
    except sqlite3.OperationalError as e:
        print(f"Database locked, retrying... ({e})")
        time.sleep(2)
