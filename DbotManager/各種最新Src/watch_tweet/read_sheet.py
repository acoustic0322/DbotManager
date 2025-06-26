import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 認証設定
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "aolasamaproject-d8b2350f0ada.json", scope
)
client = gspread.authorize(creds)

# 📄 スプレッドシートに接続
sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1hEpXLyJOQ2Jd0NE8iVpyCjCo-gA_qIDAKlgRPhyDsk8/edit"
).sheet1

# 📋 全データ取得
rows = sheet.get_all_values()[1:]  # ヘッダー除去

# 各監視対象リスト
tweet_accounts = []
reply_to_accounts = []
reply_from_accounts = []

for row in rows:
    if len(row) > 0 and row[0].strip():
        tweet_accounts.append(row[0].strip())
    if len(row) > 1 and row[1].strip():
        reply_to_accounts.append(row[1].strip())
    if len(row) > 2 and row[2].strip():
        reply_from_accounts.append(row[2].strip())

# 🆕 関数として提供
def get_monitor_ids():
    return tweet_accounts, reply_to_accounts, reply_from_accounts
