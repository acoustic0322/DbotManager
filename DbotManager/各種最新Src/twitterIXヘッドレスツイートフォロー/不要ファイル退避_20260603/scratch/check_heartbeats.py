import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

db = DBManager()
conn = db.get_connection()
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM system_status")
    rows = cursor.fetchall()
    print("PC Heartbeat Statuses:")
    for r in rows:
        print(dict(r) if hasattr(r, 'keys') else r)
except Exception as e:
    print("Error querying system_status:", e)

conn.close()
