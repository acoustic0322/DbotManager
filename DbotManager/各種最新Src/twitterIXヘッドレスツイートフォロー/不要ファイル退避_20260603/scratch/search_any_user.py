import os
import sys

# Add working directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gspread
from google.oauth2.service_account import Credentials
from modules.mutual_follow.db_manager import DBManager

target_user = '98337171'

# 1. Search DB
db = DBManager()
df = db.get_all_accounts_df()
mask = df['screen_name'] == target_user
if mask.any():
    row = df[mask].iloc[0]
    print(f"Found in DB: username={row.get('username')}, screen_name={row.get('screen_name')}, password={row.get('password')}, email={row.get('email')}, totp={row.get('totp_secret')}")
else:
    print(f"Not found in DB: {target_user}")

# 2. Search Google Sheets
SPREADSHEET_ID = '1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw'
SHEET_GID = 188292514
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

if not os.path.exists('data/google_credentials.json'):
    print("Google credentials file not found.")
else:
    creds = Credentials.from_service_account_file('data/google_credentials.json', scopes=scopes)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    
    worksheet = None
    for sheet in spreadsheet.worksheets():
        if sheet.id == SHEET_GID:
            worksheet = sheet
            break
            
    if worksheet:
        rows = worksheet.get_all_values()
        found = False
        for row in rows:
            if not row:
                continue
            username = str(row[0]).strip().replace('@', '')
            if username == target_user:
                print(f"Found in Sheet: {row[:8]}")
                found = True
        if not found:
            print(f"Not found in Sheet: {target_user}")
    else:
        print("Worksheet not found.")
