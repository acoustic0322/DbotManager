import sqlite3
import gspread
from google.oauth2.service_account import Credentials
import os
import sys

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
DB_PATH = os.path.join(BASE_DIR, "system.db")
SPREADSHEET_ID = "1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw"
TARGET_SHEET = "IXBROWSERプロファイル削除"

def export_frozen_accounts():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found.")
        return

    # 1. 凍結アカウントをDBから取得
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # is_alive=0 または sync_statusに'凍結'が含まれるもの
    cursor.execute("SELECT username, display_name, sync_status, following_count, followers_count FROM accounts WHERE is_alive = 0 OR sync_status LIKE '%凍結%'")
    frozen_list = cursor.fetchall()
    conn.close()

    if not frozen_list:
        print("No frozen accounts found.")
        return

    print(f"Found {len(frozen_list)} frozen accounts. Exporting to Google Sheet...")

    # 2. Google Sheetへの書き込み
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # シートの存在確認、なければ作成
        try:
            ws = sh.worksheet(TARGET_SHEET)
            ws.clear() # 既存の内容をクリア
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title=TARGET_SHEET, rows="100", cols="10")

        # A列にID、B列にステータス（凍結、不在等）を出力
        data_to_write = []
        for row in frozen_list:
            # row = (username, display_name, sync_status, following_count, followers_count)
            data_to_write.append([row[0], row[2]]) 

        ws.update('A1', data_to_write)
        print("Export completed successfully.")
        
    except Exception as e:
        print(f"Error during export: {e}")

if __name__ == "__main__":
    export_frozen_accounts()
