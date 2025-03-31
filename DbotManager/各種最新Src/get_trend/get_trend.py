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

print(chrome_user_data_dir)
print(chrome_profile)

# Chromeドライバーのセットアップ
options = webdriver.ChromeOptions()

# 設定ファイルから値を適用
if chrome_user_data_dir:
    options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
options.add_argument(f"--profile-directory={chrome_profile}")

#options.add_argument("--headless")  # ヘッドレスモード（ブラウザを開かず実行）
#options.add_argument("--headless=new")  # ヘッドレスモード（新しい実装）
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

# 追加のオプション（必要に応じて）
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriverの設定（service引数なし）
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Twitterの「話題を検索」ページへ移動
#url = "https://twitter.com/explore/tabs/trending"
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
delete_trend()

# 取得データをデータベースに登録
for rank, category, keyword, post_count in trend_data:
    print(f"rank={rank} category={category} keyword={keyword} post_count={post_count}")
    insert_trend(rank, category, keyword, post_count)

# ユーザーのキー入力を待つ
#nput("続行するには Enter を押してください...")

## ブラウザを閉じる
driver.quit()