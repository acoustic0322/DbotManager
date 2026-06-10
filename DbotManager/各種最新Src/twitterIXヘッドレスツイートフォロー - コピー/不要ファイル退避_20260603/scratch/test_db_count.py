import sys
import os
import traceback
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

try:
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    p = db._placeholder()
    
    print(f"PC Name: {db.pc_name}")
    print(f"DB Type: {db.db_type}")
    print(f"Placeholder: {p}")
    
    query = f"SELECT COUNT(*) FROM accounts WHERE selected=1 AND is_alive=1 AND (assigned_pc IS NULL OR assigned_pc = '' OR assigned_pc = {p})"
    print(f"Executing query: {query} with param: {db.pc_name}")
    
    cursor.execute(query, (db.pc_name,))
    count = cursor.fetchone()
    if isinstance(count, dict):
        count_val = list(count.values())[0]
    else:
        count_val = count[0]
    print(f"Successfully counted target accounts! Count: {count_val}")
    conn.close()
except Exception as e:
    print("Error executing database count:")
    traceback.print_exc()
