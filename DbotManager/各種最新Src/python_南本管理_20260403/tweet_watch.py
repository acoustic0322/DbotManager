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

# 🕵️‍♂️ ツイート取得関数（ID・日時・種別も）
def fetch_latest_tweet(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://twitter.com/{username}")
        page.wait_for_timeout(4000)

        try:
            article = page.locator("article").first
            tweet_text = article.inner_text()
            tweet_url = article.locator("a:has(time)").first.get_attribute("href")
            tweet_id = tweet_url.split("/")[-1] if tweet_url else ""
            tweet_datetime = article.locator("time").first.get_attribute("datetime")

            reply_check = article.inner_text().lower()
            post_type = "リプライ" if "返信先" in reply_check or "replying to" in reply_check else "ポスト"

            print(f"✅ @{username}: {tweet_text[:80]}...")
            return tweet_text, tweet_id, tweet_datetime, post_type
        except Exception as e:
            print(f"⚠️ ツイート取得失敗: @{username} - {e}")
            send_discord_alert(f"⚠️ ツイート取得失敗: @{username}")
            return "", "", "", ""
        finally:
            browser.close()

# 📥 各ユーザーの最新ツイート取得し、スプレッドシートに記録
for i, username in enumerate(tweet_accounts):
    tweet, tweet_id, tweet_datetime, post_type = fetch_latest_tweet(username)
    sheet.update_cell(i + 2, 4, tweet)
    sheet.update_cell(i + 2, 5, tweet_id)
    sheet.update_cell(i + 2, 6, tweet_datetime)
    sheet.update_cell(i + 2, 7, post_type)
    time.sleep(1)

print("✅ 全ユーザーの最新ツイート取得完了")
