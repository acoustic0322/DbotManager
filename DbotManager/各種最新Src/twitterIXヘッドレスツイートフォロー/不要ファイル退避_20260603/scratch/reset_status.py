import sys
import os
sys.path.append(os.getcwd())
from modules.mutual_follow.db_manager import DBManager
db = DBManager()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("UPDATE accounts SET in_use=0")
cursor.execute("UPDATE accounts SET sync_status='待機中' WHERE sync_status='実行中'")
conn.commit()
conn.close()
print("Successfully reset all accounts to idle state.")
