import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

db = DBManager()
conn = db.get_connection()
cursor = conn.cursor()

try:
    p = db._placeholder()
    
    # 1. Strict query used in get_next_account()
    query_strict = f"""
        SELECT COUNT(*) FROM accounts 
        WHERE selected=1 AND is_alive=1 AND in_use=0 
        AND (assigned_pc IS NULL OR assigned_pc = '' OR assigned_pc = {p})
        AND (sync_status IS NULL OR sync_status = '' OR sync_status = '実行中')
    """
    cursor.execute(query_strict, (db.pc_name,))
    strict_count = cursor.fetchone()
    strict_val = list(strict_count.values())[0] if isinstance(strict_count, dict) else strict_count[0]
    print(f"Strict eligible accounts count (what get_next_account sees): {strict_val}")
    
    # 2. Total active selected accounts
    query_active = f"""
        SELECT COUNT(*) FROM accounts 
        WHERE selected=1 AND is_alive=1
    """
    cursor.execute(query_active)
    active_count = cursor.fetchone()
    active_val = list(active_count.values())[0] if isinstance(active_count, dict) else active_count[0]
    print(f"Total selected + alive accounts in DB: {active_val}")
    
except Exception as e:
    print("Error querying database count:", e)

conn.close()
