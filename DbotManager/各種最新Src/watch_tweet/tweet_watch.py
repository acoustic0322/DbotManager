from read_sheet import get_monitor_ids
from playwright.sync_api import sync_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import requests

# 🔔 Discord通知関数
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1384164749578735686/eDLxTaXT5wX94GwZx5-jJWMnBZUcrOEJlnN7xV_nJDkDvx9V5YaMZOmTpHtrBn4gNrSW"
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print("✅ Discord通知完了")
    else:
        print(f"⚠️ Discord通知失敗: {response.status_code}")

# 📊 Google認証・スプレッドシート準備
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("aolasamaproject-d8b2350f0ada.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1hEpXLyJOQ2Jd0NE8iVpyCjCo-gA_qIDAKlgRPhyDsk8/edit").sheet1

# 🧾 アカウント取得
tweet_accounts, _, _ = get_monitor_ids()

# 🕵️‍♂️ Playwrightでツイート取得
def fetch_latest_tweet(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://twitter.com/{username}")
        page.wait_for_timeout(4000)

        try:
            tweet = page.locator("article").first.inner_text()
            print(f"✅ @{username}: {tweet[:80]}...")
            return tweet
        except Exception as e:
            print(f"⚠️ ツイート取得失敗: @{username} - {e}")
            send_discord_alert(f"⚠️ ツイート取得失敗: @{username}")
            return ""
        finally:
            browser.close()

# 📥 各ユーザーの最新ツイート取得し、D列に記録
for i, username in enumerate(tweet_accounts):
    tweet = fetch_latest_tweet(username)
    sheet.update_cell(i + 2, 4, tweet)
    time.sleep(1)

print("✅ 全ユーザーの最新ツイート取得完了")