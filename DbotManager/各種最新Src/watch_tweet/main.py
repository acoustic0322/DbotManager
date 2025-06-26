from read_sheet import get_monitor_ids
from playwright.sync_api import sync_playwright
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import requests
import time

# 🧾 アカウント一覧の取得
tweet_accounts, reply_to_accounts, reply_from_accounts = get_monitor_ids()

# ✅ 確認出力
print("✅ ツイート監視ID:", tweet_accounts)
print("✅ リプライされたか監視ID:", reply_to_accounts)
print("✅ リプライしたか監視ID:", reply_from_accounts)

# 🔗 Discord通知関数
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1384164749578735686/eDLxTaXT5wX94GwZx5-jJWMnBZUcrOEJlnN7xV_nJDkDvx9V5YaMZOmTpHtrBn4gNrSW"
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print("✅ Discordに通知を送信しました")
    else:
        print(f"⚠️ Discord通知失敗: {response.status_code}")

# 📄 スプレッドシート接続（書き込み用）
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "aolasamaproject-d8b2350f0ada.json", scope
)
client = gspread.authorize(creds)
sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1hEpXLyJOQ2Jd0NE8iVpyCjCo-gA_qIDAKlgRPhyDsk8/edit"
).sheet1

# 🕵️‍♂️ Playwrightで投稿取得＆スプレッドシート更新
def fetch_latest_tweet(username, row_index):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(f"https://twitter.com/{username}")
            page.wait_for_timeout(5000)
            tweet = page.locator("article").first.inner_text()
            print(f"📝 @{username} のツイート取得成功")
            # 📥 シートのE列（5列目）にツイート記録（先頭200文字まで）
            sheet.update_cell(row_index + 2, 5, tweet[:200])
        except Exception as e:
            print(f"⚠️ @{username} のツイート取得失敗: {e}")
            sheet.update_cell(row_index + 2, 5, "取得失敗")
            send_discord_alert(f"⚠️ ツイート取得失敗: @{username}")
        finally:
            browser.close()

# ▶ 各アカウントを監視（1秒間隔で実行）
for idx, account in enumerate(tweet_accounts):
    fetch_latest_tweet(account, idx)
    time.sleep(1)
