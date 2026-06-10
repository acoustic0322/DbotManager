import sqlite3

def main():
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()
    
    # Check table schema first
    cursor.execute("PRAGMA table_info(accounts)")
    cols = [col[1] for col in cursor.fetchall()]
    print("Columns:", cols)
    
    targets = ['OnisukaBes2932', 'huang27548', 'u7218310725896', 'Langsingtahes', 'Samurais_Plays', 'IngratasDeFede']
    
    for t in targets:
        cursor.execute("SELECT username, profile_id, category, group_name FROM accounts WHERE LOWER(username) = LOWER(?)", (t,))
        row = cursor.fetchone()
        print(f"Account: {t} -> Row: {row}")
        
    conn.close()

if __name__ == '__main__':
    main()
