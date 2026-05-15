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

# 親フォルダを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from config import convert_tweet_datetime
from config import convert_tweet_datetime2
from config import outputLog

from mysql import update_account_master_by_check_full_status

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.json")
SPREADSHEET_ID = "1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw"
TARGET_SHEET = "総チェック"
BATCH_SIZE = 15  # Googleシートの制限を回避するため、15件ずつまとめて更新

class XRotatingScannerV410:
    def __init__(self):
        self.impersonate = "chrome"
        self.bearer = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        self.query_id = "IGgvgiOx4QZndDHuD3x9TQ"

        self.accounts = self._load_cookies()
#        self.accounts = [
#            {
#                "auth_token": "7bff203088ea82e787873b0e3ba1d716a85d075e",
#                "ct0": "8125b12baccca9b0e3f1698ce234f1de725977123bb0b4703951c8861a7beaddb5255106d9b0da2adac35930e8769974a7eed057fc05166188eeac61dd71ff7ca07f9fa328a9425aa83be38204e39618",
#                "twid": "u=123456789"
#            }
#        ]
        self.current_idx = 0



    def _load_cookies(self):
        with open(COOKIES_FILE, "r") as f:
            return json.load(f)

    def _get_next_session(self):
        # 11垢を安全にローテーション。データ不備があれば飛ばして次を試す。
        for _ in range(len(self.accounts)):
            acc = self.accounts[self.current_idx]
            self.current_idx = (self.current_idx + 1) % len(self.accounts)
            
            auth_token = acc.get("auth_token")
            ct0 = acc.get("ct0")
            twid = acc.get("twid", "")
            
            if not auth_token or not ct0:
                continue # 不完全なデータはスキップ
                
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
        raise Exception("有効なクッキーが一つも見つかりません！cookies.jsonを確認してください。")

    def check_user(self, username, retry=0):
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
                return ["-", "制限中", "-", "待機中", "0", "0", "0", "WAIT",True]
            
            if r.status_code != 200:
                return [username, "Error", r.status_code, "Auth Error", "0", "0", "0", "ERR",False]
            
            data = r.json()
            # GraphQLのエラーメッセージを確認 (凍結検知の強化)
            errors = data.get("errors", [])
            for err in errors:
                msg = err.get("message", "").lower()
                if "suspended" in msg:
                    return [username, "凍結", "-", "凍結済", "0", "0", "0", "OK", True]
                if "not found" in msg or "could not find" in msg:
                    return [username, "不在", "-", "不在", "0", "0", "0", "OK", True]

            user_res = data.get("data", {}).get("user", {}).get("result", {})
            typename = user_res.get("__typename")
            
            # 凍結・不在アカウントの判定
            if typename == "UserUnavailable" or not user_res:
                reason = user_res.get("unavailable_reason", "") if user_res else ""
                if reason == "Suspended" or "suspended" in str(user_res).lower():
                    return [username, "凍結", "-", "凍結済", "0", "0", "0", "OK", True]
                return [username, "不在", "-", "不在", "0", "0", "0", "OK", True]

            legacy = user_res.get("legacy", {})
            if legacy.get("suspended"):
                return [username, "凍結", "-", "凍結済", "0", "0", "0", "OK", True]

            hga = user_res.get("has_graduated_access", user_res.get("is_graduated_access", True))
            it = legacy.get("profile_interstitial_type", "")
            ps = legacy.get("possibly_sensitive", False)
            
            reach, overall = "OK", "OK"
            if hga is False: reach = "おすすめNG"
            if it == "fake_account": overall = "ロック中"
            
            # センシティブ / シャドウバン判定
            if ps or it in ["sensitive_media", "offensive_profile_content"]:
                if reach == "OK":
                    reach = "センシティブ🚩"
                else:
                    reach += "/センシティブ🚩"

            name = legacy.get("name")
            if not name:
                name_match = re.search(r'"name"\s*:\s*"([^"]+)"', r.text)
                name = name_match.group(1) if name_match else "不明"

            return [name, overall, reach, "生存", str(legacy.get("statuses_count", 0)), str(legacy.get("friends_count", 0)), str(legacy.get("followers_count", 0)), "OK" , True]
        except Exception as e:
            return [username, "例外エラー", "-", str(e)[:15], "0", "0", "0", "ERR", True]

def run_test():
    scanner = XRotatingScannerV410()
    scanner.check_user("OnSounds")

def run_all():
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
    # 未完了の行のみを抽出
    to_process = [(i, row[0].strip()) for i, row in enumerate(all_rows) if i > 0 and row[0].strip() and (row[8] != "OK" if len(row) > 8 else True)]

    print(f"--- Starting Fast Batch Rotating Scan ({len(to_process)} accounts remaining) ---", flush=True)
    
    for i in range(0, len(to_process), BATCH_SIZE):
        batch_slice = to_process[i:i+BATCH_SIZE]
        
        # 2並列で実行
        print(f"Checking batch with 2 threads...", flush=True)
        with ThreadPoolExecutor(max_workers=2) as executor:
            # check_userはクラスメソッドなのでlambdaでラップ
            batch_results = list(executor.map(lambda x: (x[0], scanner.check_user(x[1])), batch_slice))
        
        # 結果を整理して表示
        results = []
        update_data = []
        for row_idx, result in batch_results:
            results.append(result)
            print(f"[{row_idx}] {result[1]} / {result[2]}", flush=True)
            
            update_data.append({
                'range': f'B{row_idx + 1}:I{row_idx + 1}',
                'values': [result]
            })
        
        if update_data:
            ws.batch_update(update_data)
            print(f"Batch updated: {len(update_data)} rows.", flush=True)
        
        time.sleep(1.2)

#if __name__ == "__main__":
#    run_all()
#    run_test()

def check_full_status(id,username):
    scanner = XRotatingScannerV410()

#    result = scanner.check_user("OnSounds")
    name, overall, reach, status, follow_count, friends_count, followers_count, ok_status , check_full_status_enable  = scanner.check_user(username)

    follow_count = int(follow_count)
    followers_count = int(followers_count)

    outputLog(f"reach={reach}")    
    outputLog(f"follow_count={follow_count}")    
    outputLog(f"followers_count={followers_count}")    
    outputLog(f"check_full_status_enable={check_full_status_enable}")    

    update_account_master_by_check_full_status(id,follow_count,followers_count,reach,check_full_status_enable)

#if __name__ == "__main__":
#    scanner = XRotatingScannerV410()

#    result = scanner.check_user("OnSounds")
#    result = scanner.check_user("Ginevrasmiles")

#    print(result)