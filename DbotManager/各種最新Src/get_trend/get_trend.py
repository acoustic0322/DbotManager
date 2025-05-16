import configparser
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from mysql import insert_trend
from mysql import delete_trend

import tempfile

# トレンドデータの処理
def parse_trend_text(text):
    """トレンドのテキストを解析し、(category, keyword, post_count) を取得"""
    lines = text.split("\n")
    category = lines[0] if len(lines) > 1 else None
    keyword = lines[1] if len(lines) > 1 else lines[0]
    
    # ポスト件数を抽出（"件のポスト" がある場合のみ）
    post_count_match = re.search(r"(\d{1,3}(,\d{3})*)件のポスト", text)
    post_count = int(post_count_match.group(1).replace(",", "")) if post_count_match else None

    return category, keyword, post_count

# 設定ファイルのパス
config_path = r"C:\work\DbotConfig\config.ini"

# 設定ファイルを読み込む
config = configparser.ConfigParser()
config.read(config_path, encoding="utf-8")

# Chrome設定を取得
chrome_user_data_dir = config.get("Chrome", "user_data_dir", fallback="")
chrome_profile = config.get("Chrome", "profile", fallback="Default")
profile_list_str = config.get("Chrome", "profile_list", fallback="")
profile_path = os.path.join(chrome_user_data_dir, chrome_profile)

# プロファイルリストを分割・整形（空白削除）
profile_list = [f"Profile {p.strip()}" for p in profile_list_str.split(",") if p.strip()]

# 現在のプロファイルのインデックスを取得して次のインデックスを決定
if chrome_profile in profile_list:
    current_index = profile_list.index(chrome_profile)
    next_index = (current_index + 1) % len(profile_list)
    chrome_profile = profile_list[next_index]
else:
    # 一致しない場合は先頭にする
    chrome_profile = profile_list[0] if profile_list else "Default"

# 切り替え後のプロファイルを保存
config.set("Chrome", "profile", chrome_profile)
with open(config_path, "w", encoding="utf-8") as configfile:
    config.write(configfile)

# 結果出力
print("User Data Dir:", chrome_user_data_dir)
print("Using profile:", chrome_profile)
print("profile path:", profile_path)

# Chromeドライバーのセットアップ
options = webdriver.ChromeOptions()

# 必ず1つだけ --user-data-dir を指定
# TEMPディレクトリを使用（安全な一時プロファイル）
#temp_profile_dir = tempfile.mkdtemp()
options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
#options.add_argument(r"--user-data-dir=C:\Users\user\AppData\Local\Google\Chrome\User Data")

options.add_argument(f"--profile-directory={chrome_profile}")
# ✅ プロファイル名を指定（例: Profile 46）
#options.add_argument("--profile-directory=Profile 48")

options.add_argument("--remote-debugging-port=9222")

# GPU関係の無効化（不要なら省略可）
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")

# 任意のプロファイルディレクトリ（本当に使いたいなら temp_profile_dir の代わりに使う）
# if chrome_user_data_dir:
#     options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
#     options.add_argument(f"--profile-directory={chrome_profile}")

# WebDriver起動
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
# Twitterの「話題を検索」ページへ移動
#url = "https://twitter.com/explore/tabs/trending"
#url = "https://x.com"
url = "https://x.com/explore/tabs/for_you"
driver.get(url)

# 読み込み待ち
time.sleep(5)

## おすすめトレンドの要素を取得
trends = driver.find_elements(By.XPATH, '//div[@data-testid="trend"]')

### トレンドのリストを取得
#trend_list = [trend.text for trend in trends]
## トレンドのリストを取得（"件のポスト" を含むもののみ）
#trend_list = [trend.text for trend in trends if "件のポスト" in trend.text]

# トレンドリスト作成 & データベース更新
trend_data = []
for i, trend in enumerate(trends, 1):
    category, keyword, post_count = parse_trend_text(trend.text)
    trend_data.append((i, category, keyword, post_count))
    print(f"{i}. category={category}, keyword={keyword}, post_count={post_count}")

## トレンドデータを削除
delete_trend(chrome_profile)

# 取得データをデータベースに登録
for rank, category, keyword, post_count in trend_data:
    print(f"rank={rank} category={category} keyword={keyword} post_count={post_count}")
    insert_trend(chrome_profile, rank, category, keyword, post_count)

# ユーザーのキー入力を待つ
#nput("続行するには Enter を押してください...")

## ブラウザを閉じる
driver.quit()