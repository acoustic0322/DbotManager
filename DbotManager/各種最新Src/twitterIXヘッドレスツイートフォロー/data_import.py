"""
import_ixbrowser_accounts.py
IXBrowserに登録済みのプロファイルをすべてCSVにインポートするスクリプト
"""
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ixbrowser.ixbrowser_local_api import IXBrowserClient

CSV_PATH = "data/accounts_v2.csv"
BATCH_SIZE = 500  # 1回のAPI呼び出しで取得する件数
MAX_ACCOUNTS = 500  # インポートする最大アカウント数

COLUMNS = [
    "screen_name", "password", "email", "auth_token", "ct0", "totp_secret",
    "user_agent", "cookies_path", "assigned_name", "assigned_bio",
    "assigned_icon", "assigned_header", "is_japanese", "profile_updated",
    "initial_follow_done", "last_tweet_time", "last_tweet_content",
    "is_suspended", "public_status", "Select"
]

def fetch_all_profiles(client):
    all_profiles = []
    page = 1
    while True:
        profiles = client.get_profile_list(limit=BATCH_SIZE, page=page)
        if not profiles:
            break
        all_profiles.extend(profiles)
        print(f"  取得済み: {len(all_profiles)} 件...")
        if len(profiles) < BATCH_SIZE:
            break
        page += 1
    return all_profiles

def main():
    print("IXBrowserに接続中...")
    client = IXBrowserClient(target="127.0.0.1", port=53200)
    client.show_request_log = False

    print("プロファイル一覧を取得中...")
    profiles = fetch_all_profiles(client)

    if not profiles:
        print("❌ プロファイルが取得できませんでした。IXBrowserが起動してログイン済みか確認してください。")
        return

    print(f"✅ {len(profiles)} 件のプロファイルを取得しました。")

    # 既存のCSVを読み込む（すでに登録済みのアカウントを保持するため）
    if os.path.exists(CSV_PATH):
        existing_df = pd.read_csv(CSV_PATH)
        existing_names = set(existing_df["screen_name"].dropna().tolist())
        print(f"既存CSV: {len(existing_names)} 件登録済み")
    else:
        existing_df = pd.DataFrame(columns=COLUMNS)
        existing_names = set()

    # 新規プロファイルのみ追加（上限まで）
    new_rows = []
    for p in profiles:
        if len(new_rows) >= MAX_ACCOUNTS:
            break
        name = p.get("name", "").strip()
        if not name or name in existing_names:
            continue
        row = {col: "" for col in COLUMNS}
        row["screen_name"] = name
        row["Select"] = True
        new_rows.append(row)

    if not new_rows:
        print("新規追加するプロファイルはありませんでした。")
    else:
        new_df = pd.DataFrame(new_rows, columns=COLUMNS)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        print(f"✅ {len(new_rows)} 件を新規追加しました → {CSV_PATH}")

    print("\n完了！")

if __name__ == "__main__":
    try:
        main()
        print("\n✅ 完了！")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback; traceback.print_exc()
    
    print("\n-------------------------------------------")
    input("Enterキーを押してこのウィンドウを閉じます...")
