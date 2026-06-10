import sqlite3
import os

db_path = "system.db"
ids = ['bazubazu1021', 'iz_iced', 'M__MJ42', 'gacchan_men', 'vodka012_3o6', 'Luna_05310', 'sa_ku3150', 'clover4281s4']

print(f"Checking {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
placeholders = ','.join(['?'] * len(ids))
cursor.execute(f"SELECT username, is_alive, sync_status FROM accounts WHERE username IN ({placeholders})", ids)
for r in cursor.fetchall():
    print(r)
conn.close()
