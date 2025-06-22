from read_sheet import get_monitor_ids
from playwright.sync_api import sync_playwright
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Discord通知関数
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1384164749578735686/eDLxTaXT5wX94GwZx5-jJWMnBZUcrOEJlnN7xV_nJDkDvx9V5YaMZOmTpHtrBn4gNrSW"
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print("✅ Discord通知完了")
    else:
        print(f"⚠️ Discord通知失敗: {response.status_code}")

# 🔐 Google認証・スプレッドシート準備
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("aolasamaproject-d8b2350f0ada.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1hEpXLyJOQ2Jd0NE8iVpyCjCo-gA_qIDAKlgRPhyDsk8/edit").sheet1

# 🧾 アカウント取得
tweet_accounts, reply_to_accounts, reply_from_accounts = get_monitor_ids()

# 💬 判定結果を保存するリスト
reply_results = []

# 🔍 リプライをチェックする関数
def check_replies(target_username, reply_by_username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://twitter.com/{reply_by_username}"
        page.goto(url)
        page.wait_for_timeout(4000)

        articles = page.locator("article")
        for i in range(articles.count()):
            inner = articles.nth(i).inner_text()
            if f"@{target_username}" in inner:
                print(f"✅ @{reply_by_username} replied to @{target_username}")
                browser.close()
                return True

        print(f"❌ @{reply_by_username} did not reply to @{target_username}")
        browser.close()
        return False

# ▶ 判定処理
for i in range(len(reply_to_accounts)):
    target = reply_to_accounts[i]
    reply_by = reply_from_accounts[i]

    print(f"\n🔍 チェック中: @{reply_by} → @{target}")
    try:
        result = check_replies(target, reply_by)
        reply_results.append("✅" if result else "❌")
        if not result:
            send_discord_alert(f"⚠️ 監視失敗: @{reply_by} → @{target}")
    except Exception as e:
        print(f"⚠️ エラー: {e}")
        reply_results.append("❌")
        send_discord_alert(f"⚠️ 監視エラー: @{reply_by} → @{target}")

    time.sleep(2)

# 📊 スプレッドシートに書き込み（D列に）
for row_index, result in enumerate(reply_results):
    sheet.update_cell(row_index + 2, 4, result)  # D列が4番目（1始まり）

print("✅ すべてのリプライ監視が完了しました")
