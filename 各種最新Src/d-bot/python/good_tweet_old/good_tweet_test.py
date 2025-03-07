# ライブラリ
import tweepy
import sys
import os
import requests

#args = sys.argv

#if len(args) < 4:
#    sys.exit()

# ファイルのパスを指定
#file_path = os.path.join(args[2],'key.txt')  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
#with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
#    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

#if len(lines) < 4:
#    sys.exit()

#        private static string ck = "SBd4tiZXE2w65cquDEWHLuqHi";
#        private static string cs = "K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC";
#        private static string ct = "S0o0T2dOU3ZESDByR0ZTcW9vcE86MTpjaQ";
#        private static string ctk = "is6iQmgF4k29fEQiKX8TzEXGlThSg9Wo3pPt4Eu5UM6nB3QgBR";


# Twitter Developer Portalから取得したキーを設定
ck = "SBd4tiZXE2w65cquDEWHLuqHi"
cs = "K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC"
at = "1777348550851956736-GUi9D959N3oMP7ZcJPCiZCA5PaZgsC"
ats = "RNfWGPFVn5czTyvMxu3luIg4HHGbTzXM6w1daghpFi4Il"

#proxy_url = args[3]

#if proxy_url:
#    # プロキシ設定がある場合のみ設定
#    proxies = {
#        "http": proxy_url,
#        "https": proxy_url
#    }

# 認証情報を設定する
client = tweepy.Client(
    consumer_key=ck,
    consumer_secret=cs,
    access_token=at,
    access_token_secret=ats
)
#if proxy_url!="":
#    client.session.proxies = proxies

# ツイートのID
tweet_id = 1842391298260738190#args[1]  # ここに対象のツイートのIDを入力してください

# いいねをする
client.like(tweet_id)
