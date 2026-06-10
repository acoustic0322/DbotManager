import sys
import os
import time
sys.path.append(os.getcwd())
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.mutual_follow.db_manager import DBManager

db = DBManager()
ctrl = IXBrowserController()

# 1. DBから全アカウント取得
df = db.get_all_accounts_df()
if df.empty:
    print("No accounts in DB.")
    sys.exit(0)

print(f"Total accounts in DB: {len(df)}")

# 2. IXBrowserから全プロファイル情報を取得 (全ページ分)
print("Fetching all profile IDs from IXBrowser...")
all_ix_profiles = []
page = 1
while True:
    profiles = ctrl.client.get_profile_list(page=page, limit=100)
    if not profiles:
        break
    all_ix_profiles.extend(profiles)
    if len(profiles) < 100:
        break
    page += 1
    time.sleep(0.5)

print(f"Total profiles found in IXBrowser: {len(all_ix_profiles)}")
name_to_id = {p.get('name'): p.get('profile_id') for p in all_ix_profiles if p}

# 3. 片っ端からクローズ命令を飛ばす
count = 0
for _, row in df.iterrows():
    name = row['screen_name']
    pid = row.get('profile_id') or name_to_id.get(name)
    
    if pid:
        count += 1
        print(f"[{count}/{len(df)}] FORCE CLOSE: {name} (PID: {pid})")
        ctrl.close_browser(pid, screen_name=name)
        # APIの連打制限を避ける
        time.sleep(0.3)

print("\nFinished sending force close commands to all accounts.")
