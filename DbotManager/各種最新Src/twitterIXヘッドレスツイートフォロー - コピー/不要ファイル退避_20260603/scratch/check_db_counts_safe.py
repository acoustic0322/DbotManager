import sqlite3
import os

def main():
    db_path = 'system.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, display_name, following_count, followers_count FROM accounts")
    rows = cursor.fetchall()
    
    total = len(rows)
    non_zero = 0
    non_zero_list = []
    
    for row in rows:
        fol = row['following_count'] or 0
        fer = row['followers_count'] or 0
        if fol > 0 or fer > 0:
            non_zero += 1
            non_zero_list.append((row['username'], fol, fer))
            
    print(f"Total accounts in DB: {total}")
    print(f"Accounts with non-zero follow/follower count: {non_zero}")
    
    print("\nSome accounts with non-zero stats:")
    for idx, (username, fol, fer) in enumerate(non_zero_list[:20]):
        print(f"{idx+1}. @{username}: following={fol}, followers={fer}")
        
    conn.close()

if __name__ == '__main__':
    main()
