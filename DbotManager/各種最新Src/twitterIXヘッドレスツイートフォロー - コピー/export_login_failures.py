import gspread
from google.oauth2.service_account import Credentials
import os
import sys
import argparse
import pandas as pd
from modules.mutual_follow.db_manager import DBManager

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
# スプレッドシートID
SPREADSHEET_ID = "1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw"
TARGET_SHEET = "ロック解除"

def export_failed_accounts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, default='all', help='fail, lock, or frozen')
    args = parser.parse_args()

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found.")
        return

    # 1. DBManagerを使用して最新のアカウント情報を取得
    db = DBManager()
    df = db.get_all_accounts_df()

    if df.empty:
        print("No accounts found in database.")
        return

    # 2. 種類に応じてフィルタリング
    if args.type == 'login_fail':
        df_target = df[df['sync_status'] == 'ログイン失敗']
        msg = "login failure"
    elif args.type == 'lock':
        df_target = df[df['sync_status'].str.contains('ロック', na=False)]
        msg = "locked"
    elif args.type == 'frozen':
        # app.pyの表示ロジックと一致させる
        frozen_keywords = '凍結|Suspended|不在|Unavailable|UserUnavailable'
        df_target = df[
            (df.get('is_suspended', False) == True) | 
            (df['sync_status'].str.contains(frozen_keywords, case=False, na=False))
        ]
        msg = "frozen/suspended"
    elif args.type == 'fail':
        # 実行失敗
        df_target = df[df['sync_status'].str.contains('失敗|エラー|Error', na=False)]
        msg = "execution failed"
    else:
        # デフォルト: ログイン失敗またはロック
        df_target = df[df['sync_status'].str.contains('ログイン失敗|ロック', na=False)]
        msg = "failed/locked"

    if df_target.empty:
        print(f"No {msg} accounts found.")
        return

    print(f"Found {len(df_target)} {msg} accounts. Exporting to Google Sheet...")

    # 3. Google Sheetへの書き込み
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
            ws = sh.add_worksheet(title=TARGET_SHEET, rows="1000", cols="5")

        # A列にID、B列にステータスを出力
        data_to_write = []
        for _, row in df_target.iterrows():
            data_to_write.append([row['screen_name'], row.get('sync_status', '')]) 

        ws.update('A1', data_to_write)
        print(f"Successfully exported {len(data_to_write)} accounts.")
        
    except Exception as e:
        print(f"Error during export: {e}")

if __name__ == "__main__":
    export_failed_accounts()
