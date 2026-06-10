import sqlite3
import os
import sys

def main():
    db_path = 'system.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return
        
    print("=== Checking database for ViralManu (Safe Encoding) ===")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    target_username = 'ViralManu'
    
    cursor.execute("SELECT * FROM accounts WHERE LOWER(username) = LOWER(?)", (target_username,))
    rows = cursor.fetchall()
    
    if rows:
        print(f"\nFound {len(rows)} matching account(s) in 'accounts' table:")
        for row in rows:
            row_dict = dict(row)
            # Remove highly sensitive information
            for key in list(row_dict.keys()):
                if any(x in key.lower() for x in ['pass', 'secret', 'token', 'cookie']):
                    row_dict[key] = "[MASKED]"
            
            # Print each field safely
            for k, v in row_dict.items():
                try:
                    safe_v = str(v).encode('utf-8', errors='replace').decode('utf-8')
                    # Safe print to terminal
                    sys.stdout.buffer.write(f"  {k}: {safe_v}\n".encode('utf-8', errors='replace'))
                except Exception as e:
                    print(f"  {k}: [Encoding Error: {e}]")
    else:
        print("No matching account found in 'accounts' table.")
        
    conn.close()

if __name__ == '__main__':
    main()
