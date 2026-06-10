import os
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = '1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw'
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

if not os.path.exists('data/google_credentials.json'):
    print("Google credentials file not found.")
else:
    creds = Credentials.from_service_account_file('data/google_credentials.json', scopes=scopes)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    print("Opened Spreadsheet. Worksheets:")
    for sheet in spreadsheet.worksheets():
        print(f"Title: {sheet.title}, ID (GID): {sheet.id}")
