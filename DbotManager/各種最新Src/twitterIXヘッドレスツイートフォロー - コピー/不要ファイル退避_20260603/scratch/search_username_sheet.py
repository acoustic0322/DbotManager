import os
import gspread
from google.oauth2.service_account import Credentials

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
        targets = ['aefk009', 'AnnaBenjam13220']
        for row in rows:
            if not row:
                continue
            username = str(row[0]).strip().replace('@', '')
            if username in targets:
                print(f"Found in sheet: {row[:8]}")
    else:
        print("Worksheet not found.")
