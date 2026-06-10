import sqlite3
conn = sqlite3.connect('system.db')
cursor = conn.cursor()
cursor.execute("""
    UPDATE accounts 
    SET is_alive = 1 
    WHERE sync_status NOT IN ('凍結', '不在', '例外エラー', '待機中', '凍結済') 
    AND sync_status IS NOT NULL
""")
print(f"Fixed {cursor.rowcount} accounts")
conn.commit()
conn.close()
