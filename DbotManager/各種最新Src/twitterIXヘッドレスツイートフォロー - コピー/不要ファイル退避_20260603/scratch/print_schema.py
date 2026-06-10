import sqlite3
import os

def main():
    db_path = 'system.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(accounts)")
    columns = cursor.fetchall()
    
    print("Columns in accounts table:")
    for col in columns:
        print(f"Index: {col[0]}, Name: {col[1]}, Type: {col[2]}")
        
    conn.close()

if __name__ == '__main__':
    main()
