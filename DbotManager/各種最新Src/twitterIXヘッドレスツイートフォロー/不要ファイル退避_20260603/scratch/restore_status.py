import sys
import os
sys.path.append(os.getcwd())
from modules.mutual_follow.db_manager import DBManager

def restore_ng_status():
    db = DBManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # reach_status が NG系のものを sync_status に書き戻す
    # Postgresの構文に合わせてシングルクォートを適切に処理
    targets = ['おすすめNG', 'センシティブ🚩', 'おすすめNG/センシティブ🚩']
    
    query = "UPDATE accounts SET sync_status = reach_status WHERE reach_status IN (%s, %s, %s)"
    cursor.execute(query, targets)
    
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    print(f"Restore complete. {rows_updated} accounts updated back to NG status.")

if __name__ == "__main__":
    restore_ng_status()
