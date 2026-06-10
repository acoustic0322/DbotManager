import sqlite3
import random
from curl_cffi import requests
import json
import re
import time
import os
import gspread
from google.oauth2.service_account import Credentials
import sys
import io
from concurrent.futures import ThreadPoolExecutor
import threading
from modules.mutual_follow.db_manager import DBManager

# Windowsでの文字化け・絵文字エラー対策
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.json")
SPREADSHEET_ID = "1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw"
TARGET_SHEET = "総チェック"
BATCH_SIZE = 15  # Googleシートの制限を回避するため、15件ずつまとめて更新
ICON_DIR = os.path.join(BASE_DIR, "data", "icons")

if not os.path.exists(ICON_DIR):
    os.makedirs(ICON_DIR, exist_ok=True)

def download_icon(screen_name, url):
    path = os.path.join(ICON_DIR, f"{screen_name}.jpg")
    # すでに画像がある場合はスキップして高速化
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
        
    try:
        from curl_cffi import requests as curl_requests
        response = curl_requests.get(url, timeout=15, impersonate="chrome")
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return path
    except Exception as e:
        print(f"Error downloading icon for {screen_name}: {e}")
    return None

class XRotatingScannerV410:
    def __init__(self):
        self.impersonate = "chrome"
        self.bearer = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        self.query_id = "IGgvgiOx4QZndDHuD3x9TQ"
        self.accounts = self._load_cookies()
        self.current_idx = 0
        self.lock = threading.Lock()

    def _load_cookies(self):
        scanner_pool = []
        seen_usernames = set()

        # 1. 外部ファイル(cookies.json)から読み込み
        if os.path.exists(COOKIES_FILE):
            try:
                with open(COOKIES_FILE, "r") as f:
                    file_accs = json.load(f)
                    for acc in file_accs:
                        twid = acc.get("twid") or acc.get("username")
                        if twid:
                            seen_usernames.add(twid)
                        scanner_pool.append(acc)
                print(f"Loaded {len(file_accs)} scanners from cookies.json")
            except Exception as e:
                print(f"Error loading cookies.json: {e}")
        
        # 2. システムDBからスキャナー用アカウントを補充
        try:
            db = DBManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # 「凍結チェック用」グループのアカウントのみを取得
            cursor.execute("SELECT auth_token, ct0, username FROM accounts WHERE group_name = '凍結チェック用' AND auth_token != '' AND ct0 != ''")
            frozen_rows = cursor.fetchall()
            
            added_special = 0
            for r in frozen_rows:
                # DBManagerがdict形式で返す場合とtupleで返す場合の両方に対応
                if isinstance(r, dict):
                    auth_token = r.get('auth_token')
                    ct0 = r.get('ct0')
                    uname = r.get('username')
                else:
                    auth_token = r[0]
                    ct0 = r[1]
                    uname = r[2]
                
                if uname and uname not in seen_usernames:
                    scanner_pool.append({"auth_token": auth_token, "ct0": ct0, "twid": uname})
                    seen_usernames.add(uname)
                    added_special += 1
            if added_special > 0:
                print(f"Added {added_special} scanners from '凍結チェック用' group")
        except Exception as e:
            print(f"Error loading from DB: {e}")
        
        print(f"Final scanner pool size: {len(scanner_pool)}")
        
        if not scanner_pool:
            raise Exception("有効なクッキー(cookies.json)または「凍結チェック用」グループのアカウントが見つかりませんでした。")
            
        return scanner_pool

    def _get_next_session(self):
        with self.lock:
            for _ in range(len(self.accounts)):
                acc = self.accounts[self.current_idx]
                self.current_idx = (self.current_idx + 1) % len(self.accounts)
                
                auth_token = acc.get("auth_token")
                ct0 = acc.get("ct0")
                twid = acc.get("twid", "")
                
                if not auth_token or not ct0:
                    continue
                    
                session = requests.Session()
                session.headers.update({
                    'authorization': f'Bearer {self.bearer}',
                    'cookie': f'auth_token={auth_token}; ct0={ct0}; twid={twid}',
                    'x-csrf-token': ct0,
                    'x-twitter-active-user': 'yes',
                    'x-twitter-client-language': 'ja',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'referer': 'https://x.com/',
                })
                return session
        raise Exception("有効なセッションが作成できません。")

    def check_user(self, username, retry=0):
        # 短い待機を入れて一斉アクセスを防ぐ
        if retry == 0:
            time.sleep(random.uniform(0.3, 0.8))
            
        session = self._get_next_session()
        variables = {"screen_name": username, "withGrokTranslatedBio": True}
        features = {"hidden_profile_subscriptions_enabled":True,"profile_label_improvements_pcf_label_in_post_enabled":True,"responsive_web_profile_redirect_enabled":False,"rweb_tipjar_consumption_enabled":False,"verified_phone_label_enabled":False,"subscriptions_verification_info_is_identity_verified_enabled":True,"subscriptions_verification_info_verified_since_enabled":True,"highlights_tweets_tab_ui_enabled":True,"responsive_web_twitter_article_notes_tab_enabled":True,"subscriptions_feature_can_gift_premium":True,"creator_subscriptions_tweet_preview_api_enabled":True,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,"responsive_web_graphql_timeline_navigation_enabled":True}
        fieldToggles = {"withPayments":False,"withAuxiliaryUserLabels":True}
        url = f"https://x.com/i/api/graphql/{self.query_id}/UserByScreenName?variables={json.dumps(variables)}&features={json.dumps(features)}&fieldToggles={json.dumps(fieldToggles)}"
        
        try:
            r = session.get(url, impersonate=self.impersonate, timeout=15)
            if r.status_code == 429:
                if retry < len(self.accounts):
                    time.sleep(2)
                    return self.check_user(username, retry + 1)
                return [username, "制限中", "-", "待機中", "0", "0", "0", "WAIT", None]
            
            if r.status_code != 200:
                return [username, "Error", r.status_code, "Auth Error", "0", "0", "0", "ERR", None]
            
            data = r.json()
            errors = data.get("errors", [])
            for err in errors:
                msg = err.get("message", "").lower()
                if "suspended" in msg:
                    return [username, "凍結", "-", "凍結済", "0", "0", "0", "OK", None]
                if "not found" in msg or "could not find" in msg:
                    return [username, "不在", "-", "不在", "0", "0", "0", "OK", None]

            user_res = data.get("data", {}).get("user", {}).get("result", {})
            typename = user_res.get("__typename")
            
            if typename == "UserUnavailable" or not user_res:
                reason = user_res.get("unavailable_reason", "") if user_res else ""
                if reason == "Suspended" or "suspended" in str(user_res).lower():
                    return [username, "凍結", "-", "凍結済", "0", "0", "0", "OK", None]
                return [username, "不在", "-", "不在", "0", "0", "0", "OK", None]

            legacy = user_res.get("legacy", {})
            core = user_res.get("core", {})
            
            hga = user_res.get("has_graduated_access", user_res.get("is_graduated_access", True))
            it = legacy.get("profile_interstitial_type", "")
            ps = legacy.get("possibly_sensitive", False)
            
            reach, overall = "OK", "OK"
            if hga is False: reach = "おすすめNG"
            if it == "fake_account": overall = "ロック中"
            
            # センシティブ判定
            if ps or it in ["sensitive_media", "offensive_profile_content"]:
                if reach == "OK": reach = "センシティブ🚩"
                else: reach += "/センシティブ🚩"

            # 名前取得 (core.name を優先)
            name = core.get("name") or legacy.get("name")
            if not name:
                name_match = re.search(r'"name"\s*:\s*"([^"]+)"', r.text)
                name = name_match.group(1) if name_match else "不明"

            # アイコンURL取得 (avatar.image_url を優先)
            avatar_url = user_res.get("avatar", {}).get("image_url") or legacy.get("profile_image_url_https", "")
            avatar_url = avatar_url.replace("_normal.", "_400x400.")
            
            return [name, overall, reach, "ALIVE", str(legacy.get("statuses_count", 0)), str(legacy.get("friends_count", 0)), str(legacy.get("followers_count", 0)), "OK", avatar_url]
        except Exception as e:
            return [username, "例外エラー", "-", str(e)[:15], "0", "0", "0", "ERR", None]

def run_from_sheet():
    """Googleスプレッドシートから読み込んでチェックする"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found.")
        return

    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(TARGET_SHEET)
    
    print("--- Sheet Loading... ---", flush=True)
    all_rows = ws.get_all_values()
    if len(all_rows) <= 1: 
        print("No accounts found in sheet.", flush=True)
        return

    scanner = XRotatingScannerV410()
    to_process = [(i, row[0].strip()) for i, row in enumerate(all_rows) if i > 0 and row[0].strip() and (row[8] != "OK" if len(row) > 8 else True)]

    print(f"--- Starting Fast Batch Rotating Scan ({len(to_process)} accounts remaining) ---", flush=True)
    
    for i in range(0, len(to_process), BATCH_SIZE):
        batch_slice = to_process[i:i+BATCH_SIZE]
        with ThreadPoolExecutor(max_workers=5) as executor:
            batch_results = list(executor.map(lambda x: (x[0], scanner.check_user(x[1])), batch_slice))
        
        update_data = []
        for row_idx, result in batch_results:
            # シート表示用に "ALIVE" -> "生存" に変換
            display_result = list(result)
            if display_result[3] == "ALIVE":
                display_result[3] = "生存"
            
            print(f"[{row_idx}] {display_result[1]} / {display_result[2]}", flush=True)
            update_data.append({
                'range': f'B{row_idx + 1}:I{row_idx + 1}',
                'values': [display_result[:-1]]
            })
        
        if update_data:
            ws.batch_update(update_data)
            print(f"Batch updated: {len(update_data)} rows.", flush=True)
        
        time.sleep(1.2)

def run_for_usernames(usernames):
    """指定されたユーザー名のみをチェックしてDBに反映する"""
    db = DBManager()
    
    from datetime import datetime
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    p = db._placeholder()

    # マイグレーション: カラムがなければ追加
    try:
        if db.db_type == "sqlite":
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [info[1] for info in cursor.fetchall()]
        else:
            cursor.execute(f"SELECT * FROM accounts LIMIT 1")
            columns = [desc[0] for desc in cursor.description]
            
        if 'last_full_check' not in [c.lower() for c in columns]:
            print("DB Migration: Adding 'last_full_check' column.")
            cursor.execute("ALTER TABLE accounts ADD COLUMN last_full_check TEXT")
            if db.db_type not in ["mysql", "postgres"]: conn.commit()
    except Exception as e:
        print(f"Migration notice: {e}")
    
    print(f"--- Starting Targeted Scan for {len(usernames)} accounts ---")
    scanner = XRotatingScannerV410()
    
    for i in range(0, len(usernames), BATCH_SIZE):
        batch_slice = usernames[i:i+BATCH_SIZE]
        with ThreadPoolExecutor(max_workers=5) as executor:
            batch_results = list(executor.map(lambda u: (u, scanner.check_user(u)), batch_slice))
            
        for username, result in batch_results:
            name, overall, reach, status_text, tweet_cnt, friend_cnt, follower_cnt, ok_flag, avatar_url = result
            
            if status_text in ["凍結済", "不在"]:
                is_alive = 0
            else:
                is_alive = 1
            
            if status_text != "ALIVE":
                new_status = status_text
            elif overall != "OK":
                new_status = overall
            elif reach != "OK":
                new_status = reach
            else:
                new_status = "正常"

            if status_text not in ["待機中", "Auth Error", "例外エラー", "WAIT"]:
                last_check_time = now_str
            else:
                last_check_time = None

            # 表示用に名前を整形
            display_info = f"{name} (@{username})" if name and name != username else f"@{username}"
            print(f"[{display_info}] -> {new_status} ({status_text}) | Reach: {reach}")
            
            if avatar_url:
                download_icon(username, avatar_url)
            
            try:
                if last_check_time:
                    cursor.execute(f'''
                        UPDATE accounts 
                        SET is_alive = {p}, sync_status = {p}, display_name = {p}, 
                            following_count = {p}, followers_count = {p}, reach_status = {p},
                            last_full_check = {p}
                        WHERE username = {p}
                    ''', (is_alive, new_status, name, int(friend_cnt), int(follower_cnt), reach, last_check_time, username))
                else:
                    cursor.execute(f'''
                        UPDATE accounts 
                        SET is_alive = {p}, sync_status = {p}, display_name = {p}, 
                            following_count = {p}, followers_count = {p}, reach_status = {p}
                        WHERE username = {p}
                    ''', (is_alive, new_status, name, int(friend_cnt), int(follower_cnt), reach, username))
                
                if db.db_type not in ["mysql", "postgres"]: conn.commit()
            except Exception as e:
                print(f"Failed to update DB for {username}: {e}")
        
        time.sleep(2)
        
    print("--- Targeted Scan Completed ---")

def run_from_db(force=False):
    """システムDBから読み込んでチェックし、結果をDBに反映する"""
    db = DBManager()
    
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    p = db._placeholder()

    if force:
        cursor.execute("SELECT username FROM accounts")
    elif db.db_type == "postgres":
        cursor.execute("SELECT username FROM accounts WHERE last_full_check IS NULL OR last_full_check::date != current_date")
    elif db.db_type == "mysql":
        cursor.execute("SELECT username FROM accounts WHERE DATE(last_full_check) != CURDATE() OR last_full_check IS NULL")
    else:
        cursor.execute("SELECT username FROM accounts WHERE last_full_check NOT LIKE ? OR last_full_check IS NULL", (f"{today}%",))
    
    rows = cursor.fetchall()
    usernames = [r[0] if isinstance(r, (tuple, list)) else r['username'] for r in rows]
    
    if usernames:
        print(f"Found {len(usernames)} accounts to check for today.")
        run_for_usernames(usernames)
    else:
        print("All accounts have been checked for today.")

def export_all_to_sheet():
    """DBの全アカウントをスプレッドシートのA列に書き出し、チェックの準備をする"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found.")
        return []

    try:
        db = DBManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM accounts ORDER BY username")
        rows = cursor.fetchall()
        usernames = [[r[0] if isinstance(r, (tuple, list)) else r['username']] for r in rows]
    except Exception as e:
        print(f"Error reading from DB: {e}")
        return []

    if not usernames:
        print("No accounts in DB to export.")
        return []

    # スプレッドシート準備
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(TARGET_SHEET)
    
    # A列を一度クリアして書き込み（ヘッダー行は残すために A2 から）
    ws.update('A2:A' + str(len(usernames) + 1), usernames)
    print(f"Exported {len(usernames)} usernames to {TARGET_SHEET} sheet (Column A).")
    return [u[0] for u in usernames]

if __name__ == "__main__":
    import argparse
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--db", action="store_true", help="Scan all accounts in DB")
        parser.add_argument("--force", action="store_true", help="Force scan even if checked today")
        parser.add_argument("--usernames", help="Comma separated usernames to scan")
        parser.add_argument("--full-export", action="store_true", help="Export all DB usernames to sheet A column then check")
        args = parser.parse_args()

        if args.full_export:
            export_all_to_sheet()
            run_from_sheet()
        elif args.usernames:
            user_list = [u.strip() for u in args.usernames.split(",") if u.strip()]
            run_for_usernames(user_list)
        elif args.db:
            run_from_db(force=args.force)
        else:
            run_from_sheet()
            
        print("\n--- All tasks completed successfully ---")
    except Exception as e:
        import traceback
        print("\n" + "!"*50)
        print(f"FATAL ERROR during execution:\n{e}")
        print("!"*50)
        traceback.print_exc()
    
    print("\nPress Enter to exit...")
    input()
