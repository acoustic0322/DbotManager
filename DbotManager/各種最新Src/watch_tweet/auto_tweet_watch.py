import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
from read_sheet import get_monitor_ids

# ✅ Discord通知関数
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1384164749578735686/eDLxTaXT5wX94GwZx5-jJWMnBZUcrOEJlnN7xV_nJDkDvx9V5YaMZOmTpHtrBn4gNrSW"
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print("[通知成功] Discord通知完了")
    else:
        print(f"[通知失敗] Discord通知失敗: {response.status_code}")

# 🔐 Google認証・スプレッドシート準備
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("aolasamaproject-d8b2350f0ada.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1hEpXLyJOQ2Jd0NE8iVpyCjCo-gA_qIDAKlgRPhyDsk8/edit").sheet1

# 📥 ツイート取得関数
def fetch_latest_tweet(username):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://twitter.com/{username}")
            page.wait_for_timeout(4000)
            article = page.locator("article").first
            tweet = article.inner_text()
            browser.close()
            print(f"[成功] @{username}: {tweet[:80]}...")
            return tweet
    except Exception as e:
        print(f"[警告] ツイート取得失敗: @{username} - {e}")
        return None

# ▶ 実行ループ
def run_loop():
    while True:
        print("\n[開始] ツイート監視スクリプトを実行します...")
        tweet_accounts, _, _ = get_monitor_ids()
        for row_index, username in enumerate(tweet_accounts):
            tweet = fetch_latest_tweet(username)
            if tweet:
                sheet.update_cell(row_index + 2, 5, tweet)  # E列が5番目（1始まり）
            else:
                send_discord_alert(f"[警告] ツイート取得失敗: @{username}")
            time.sleep(2)

        print("[完了] 実行完了。10分待機します。\n")
        time.sleep(600)

if __name__ == "__main__":
    run_loop()
