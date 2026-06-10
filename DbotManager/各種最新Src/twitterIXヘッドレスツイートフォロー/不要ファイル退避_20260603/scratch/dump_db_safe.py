import sqlite3
import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

db_path = 'system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    # Use Row factory to see column names clearly
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM accounts LIMIT 50")
    rows = cursor.fetchall()
    
    print("Columns:", rows[0].keys() if rows else "No rows")
    for i, row in enumerate(rows):
        print(f"--- Row {i} ---")
        for key in row.keys():
            print(f"{key}: {row[key]}")
    
    conn.close()
