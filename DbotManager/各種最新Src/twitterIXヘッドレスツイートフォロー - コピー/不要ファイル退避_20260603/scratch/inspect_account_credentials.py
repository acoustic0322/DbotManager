import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
conn = db.get_connection()
cursor = conn.cursor()

for user in ['aefk009', 'AnnaBenjam13220']:
    print(f"\n--- Inspecting {user} ---")
    cursor.execute("SELECT username, screen_name, password, email, totp_secret, auth_token, ct0 FROM accounts WHERE username = %s OR screen_name = %s", (user, user))
    rows = cursor.fetchall()
    if not rows:
        print("No records found in database!")
    for r in rows:
        r_dict = dict(r)
        # Mask password and token for display safety
        r_dict['password'] = '***' if r_dict.get('password') else 'EMPTY'
        r_dict['auth_token'] = '***' if r_dict.get('auth_token') else 'EMPTY'
        r_dict['ct0'] = '***' if r_dict.get('ct0') else 'EMPTY'
        print(r_dict)
