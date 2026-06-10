import sqlite3
import os

def main():
    db_path = 'system.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    target_username = 'ViralManu'
    
    # Check if exists
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE LOWER(username) = LOWER(?)", (target_username,))
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Deleting '{target_username}' from database...")
        cursor.execute("DELETE FROM accounts WHERE LOWER(username) = LOWER(?)", (target_username,))
        conn.commit()
        print("Successfully deleted.")
    else:
        print(f"'{target_username}' was not found in the database.")
        
    conn.close()

if __name__ == '__main__':
    main()
