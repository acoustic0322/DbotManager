import sqlite3

ids = [
    'bazubazu1021', 'iz_iced', 'M__MJ42', 'gacchan_men', 
    'vodka012_3o6', 'Luna_05310', 'sa_ku3150', 'clover4281s4'
]

conn = sqlite3.connect('system.db')
cursor = conn.cursor()
placeholders = ','.join(['?'] * len(ids))
cursor.execute(f'UPDATE accounts SET is_alive = 1, sync_status = "" WHERE username IN ({placeholders})', ids)
conn.commit()
print(f"Successfully restored {cursor.rowcount} accounts to ALIVE status.")
conn.close()
