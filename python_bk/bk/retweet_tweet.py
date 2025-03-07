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

if proxy_url:
    # プロキシ設定がある場合のみ設定
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

# 認証
client = tweepy.Client(consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
if proxy_url!="":
    client.session.proxies = proxies

# ツイートのID
tweet_id = args[1]  # ここに対象のツイートのIDを入力してください

# リツイートをする
client.retweet(tweet_id)
