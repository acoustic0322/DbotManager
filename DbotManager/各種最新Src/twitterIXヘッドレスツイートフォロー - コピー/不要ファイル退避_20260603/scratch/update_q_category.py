from modules.mutual_follow.db_manager import DBManager

def main():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    p = db._placeholder()
    
    # Update category 'q' to '日常生活'
    cursor.execute(f"UPDATE accounts SET category = '日常生活' WHERE category = {p}", ('q',))
    
    if db.db_type == "postgres" or db.db_type == "sqlite":
        conn.commit()
        
    print(f"Updated accounts from 'q' to '日常生活' (rowcount: {cursor.rowcount})")

if __name__ == '__main__':
    main()
