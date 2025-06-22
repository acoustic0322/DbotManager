from read_sheet import get_monitor_ids
from playwright.sync_api import sync_playwright
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Discord通知機能
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1384164749578735686/eDLxTaXT5wX94GwZx5-jJWMnBZUcrOEJlnN7xV_nJDkDvx9V5YaMZOmTpHtrBn4gNrSW"  # ←ここは本番URLに戻してね
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 204:
        print("✅ Discord通知完了")
    else:
        print(f"⚠️ Discord通知失敗: {response.status_code}")

# Google認証・スプレッドシート準備
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("aolasamaproject-d8b2350f0ada.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1hEpXLyJOQ2Jd0NE8iVpyCjCo-gA_qIDAKlgRPhyDsk8/edit").sheet1

# アカウント取得
tweet_accounts, reply_to_accounts, reply_from_accounts = get_monitor_ids()

# Playwrightで監視処理
def check_replies():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for i in range(len(tweet_accounts)):
            target = reply_to_accounts[i]
            reply_by = reply_from_accounts[i]

            print(f"\nチェック中: @{reply_by} → @{target}")

            try:
                page.goto(f"https://twitter.com/{reply_by}/with_replies", timeout=60000)
                time.sleep(3)
                page_content = page.content()

                if f"@{target}" in page_content:
                    print(f"✅ @{reply_by} replied to @{target}")
                else:
                    print(f"❌ @{reply_by} did not reply to @{target}")
                    send_discord_alert(f"❌ @{reply_by} did not reply to @{target}")
            except Exception as e:
                print(f"⚠️ 監視中にエラー発生: {e}")
                send_discord_alert(f"⚠️ 監視中にエラー発生: @{reply_by} → @{target}")

        browser.close()

# 10分ごとの自動実行ループ
if __name__ == "__main__":
    while True:
        print("\nリプライ監視スクリプトを実行します...")
        try:
            check_replies()
        except Exception as e:
            print(f"❌ スクリプトエラー: {e}")
            send_discord_alert(f"❌ リプライ監視スクリプトにエラー発生: {e}")

        print("✅ 実行完了。10分待機します。\n")
        time.sleep(600)
