import sqlite3

def list_columns():
    conn = sqlite3.connect('system.db')
    cursor = conn.execute("PRAGMA table_info(accounts)")
    columns = cursor.fetchall()
    print("\n--- Accounts Table Columns ---")
    for col in columns:
        print(f"ID: {col[0]}, Name: {col[1]}, Type: {col[2]}")
    conn.close()

if __name__ == "__main__":
    list_columns()
