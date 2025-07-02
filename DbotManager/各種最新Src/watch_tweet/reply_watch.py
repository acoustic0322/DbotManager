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

# 🧾 スプレッドシートから監視対象を取得（ツイートIDとユーザー名）
tweet_ids = sheet.col_values(2)[1:]     # B列: ツイートID
usernames = sheet.col_values(3)[1:]     # C列: ユーザー名

# 🔁 リプライ取得関数（最大5件）
def check_replies(tweet_id, username):
    url = f"https://twitter.com/{username}/status/{tweet_id}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)

        try:
            articles = page.locator("article").all()
            replies = []
            for article in articles[1:6]:
                try:
                    content = article.inner_text()
                    replies.append(content)
                except:
                    continue

            return replies

        except Exception as e:
            print(f"⚠️ リプライ取得失敗: {e}")
            return []

        finally:
            browser.close()

# 📝 リプライを取得してスプレッドシートに反映
for i in range(len(tweet_ids)):
    tweet_id = tweet_ids[i]
    username = usernames[i]

    print(f"\n🔍 @{username} のツイート {tweet_id} に対するリプライを取得中...")
    replies = check_replies(tweet_id, username)

    if replies:
        sheet.update_cell(i + 2, 5, replies[0])  # E列に最初のリプライを記録
    else:
        sheet.update_cell(i + 2, 5, "❌ No replies")
        send_discord_alert(f"⚠️ リプライなし: @{username} のツイートID {tweet_id}")

    time.sleep(2)

print("✅ すべてのツイートに対するリプライ取得が完了しました")
