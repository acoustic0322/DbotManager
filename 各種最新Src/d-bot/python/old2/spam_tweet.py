# ライブラリ
import tweepy
import sys
import os
import requests

args = sys.argv

if len(args) < 4:
    sys.exit()

# ファイルのパスを指定
file_path = os.path.join(args[2],'key.txt')  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

if len(lines) < 4:
    sys.exit()

# Twitter Developer Portalから取得したキーを設定
ck = lines[0]
cs = lines[1]
at = lines[2]
ats = lines[3]

proxy_url = args[3]

# 認証
auth = tweepy.OAuthHandler(ck, cs)
auth.set_access_token(at, ats)
if proxy_url:
    api = tweepy.API(auth, proxy=proxy_url)
else:
    api = tweepy.API(auth)

# アカウントのID
id = args[1]

# 通報をする
response = api.report_spam(screen_name=id)
print(f"{id}の通報が完了しました")
