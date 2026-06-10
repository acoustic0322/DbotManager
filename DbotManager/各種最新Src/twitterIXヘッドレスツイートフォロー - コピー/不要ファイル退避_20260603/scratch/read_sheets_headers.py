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
        print(f"Opened Worksheet: {worksheet.title}")
        rows = worksheet.get_all_values()
        print(f"Total Rows: {len(rows)}")
        print("Header:")
        print(rows[0] if rows else "No rows")
        print("\nFirst 3 data rows:")
        for r in rows[1:4]:
            # Print row elements securely (hide credentials partly)
            masked = []
            for item in r:
                if len(item) > 4:
                    masked.append(item[:2] + "***" + item[-2:])
                else:
                    masked.append(item)
            print(masked)
    else:
        print(f"Worksheet with GID {SHEET_GID} not found.")
