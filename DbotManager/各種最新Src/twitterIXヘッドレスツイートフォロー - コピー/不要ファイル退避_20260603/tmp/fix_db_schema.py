import sqlite3
import os

db_path = 'system.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# columns to add
columns = [
    ('name', 'TEXT DEFAULT ""'),
    ('biography', 'TEXT DEFAULT ""'),
    ('category', 'TEXT DEFAULT ""')
]

for col_name, col_type in columns:
    try:
        c.execute(f'ALTER TABLE accounts ADD COLUMN {col_name} {col_type}')
        print(f"Column added: {col_name}")
    except sqlite3.OperationalError:
        print(f"Column already exists: {col_name}")

conn.commit()
conn.close()
print("Database schema synchronization complete.")
