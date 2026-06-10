import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager

db = DBManager()
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("SELECT sync_status, COUNT(*) FROM accounts GROUP BY sync_status")
rows = cursor.fetchall()
print("Distinct sync_status counts:")
for r in rows:
    row_dict = dict(r) if hasattr(r, 'keys') else r
    # Safely convert to a string using utf-8 representing byte representation if print fails
    for k, v in list(row_dict.items()):
        if isinstance(v, str):
            try:
                v.encode('ascii')
            except UnicodeEncodeError:
                row_dict[k] = v.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    try:
        # Convert entire line to utf-8 safe printing on windows CP932 console
        sys.stdout.buffer.write((str(row_dict) + "\n").encode('utf-8'))
    except Exception as e:
        print(f"Print error: {e}")

conn.close()
