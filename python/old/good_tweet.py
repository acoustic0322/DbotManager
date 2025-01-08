# ライブラリ
import tweepy
import sys
import os
import requests

import pymysql

import time
from datetime import datetime

# MySQLから認証情報を取得する関数
def get_account_master(id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host='localhost',      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT client_id, client_secret, access_token, access_secret , bearer_token FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

args = sys.argv
#
#if len(args) < 4:
#    sys.exit()

# ファイルのパスを指定
#file_path = os.path.join(args[2],'key.txt')  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
#with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
#    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

#if len(lines) < 4:
#    sys.exit()

# Twitter Developer Portalから取得したキーを設定
#ck = lines[0]
#cs = lines[1]
#at = lines[2]
#ats = lines[3]
account_id = 1
credentials = get_account_master(account_id)

# ツイートのID
#tweet_id = args[1]  # ここに対象のツイートのIDを入力してください
tweet_id = '1837331936194482673'  # ここに対象のツイートのIDを入力してください

#ID=3
ck = "eGRLTjBiazNiaGN6SVpxeFdRa2M6MTpjaQ"
cs = "AXdv6In3YIZv8lGVKRMZGBtLmsKCjWm-3FRJrIwIl_g3uA1Gug"
at = "1734332897417408512-ZDT1dwfwrPBeCFFyMzhhVX9BRUeXWv"
ats = "lHnzF48YqCa5ZEcX3OwIGjcZFUdiMfejUQpKhqqHVoJ0r"

#ID=2
ck = "toDBZDCcVqoAZllXBZ6JXWvrV"
cs = "hUbUiMg7fho2s1mkim2AWdVLaOyCz8rluXonD62pdn3Ev4hpEb"
at = "1777348550851956736-g96VOzyzewtNTg0aCBGbkii1VVhh3w"
ats = "VSpiRRZnWX9C3qvesCeL94qHDHQ9qfFFIPWdHw3iYkBVQ"

print(credentials['client_id'])
        
#proxy_url = args[3]

#if proxy_url:
#    # プロキシ設定がある場合のみ設定
#    proxies = {
#        "http": proxy_url,
#        "https": proxy_url
#    }

# 認証情報を設定する
#client = tweepy.Client(
#    consumer_key=credentials['client_id'],
#    consumer_secret=credentials['client_secret'],
#    access_token=credentials['access_token'],
#    access_token_secret=credentials['access_secret']
#)

CONSUMER_KEY = 'TobPKwhKLbt7yaM2Ty1KBFZNV'
CONSUMER_SECRET = 'WzYRSurjfXSC2XmDzrtl3hEB0l6C4ymmnn4VyflEBjWWnYyByl'
#

#client = tweepy.Client(
#    consumer_key=credentials['client_id'],
#    consumer_secret=credentials['client_secret'],
#    access_token=credentials['access_token'],
#    access_token_secret=credentials['access_secret']
#)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(credentials['access_token'], credentials['access_secret'])
api = tweepy.API(auth)

try:
    api.create_favorite(tweet_id)
except Exception as e:
    print(e)

