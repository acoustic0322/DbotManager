import sqlite3

ids = [
    'bazubazu1021', 'iz_iced', 'M__MJ42', 'gacchan_men', 
    'vodka012_3o6', 'Luna_05310', 'sa_ku3150', 'clover4281s4'
]

conn = sqlite3.connect('system.db')
cursor = conn.cursor()
placeholders = ','.join(['?'] * len(ids))
cursor.execute(f'UPDATE accounts SET is_alive = 0, sync_status = "凍結" WHERE username IN ({placeholders})', ids)
conn.commit()
print(f"Reverted {cursor.rowcount} accounts back to FROZEN status.")
conn.close()
