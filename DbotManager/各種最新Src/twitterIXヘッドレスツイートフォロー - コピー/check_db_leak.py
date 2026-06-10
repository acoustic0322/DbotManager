import sqlite3

def check_uraaka():
    db_path = 'system.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for anything suspicious
    cursor.execute("SELECT username, category FROM accounts WHERE category LIKE '%裏垢%' OR category LIKE '%女子%' OR category LIKE '%uraaka%' OR category LIKE '%joshi%'")
    rows = cursor.fetchall()
    
    if rows:
        print(f"Found {len(rows)} suspicious accounts:")
        for u, c in rows:
            print(f"- @{u}: [{c}]")
    else:
        print("No suspicious categories found in DB.")
        
    conn.close()

if __name__ == "__main__":
    check_uraaka()
