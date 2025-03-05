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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token FROM account_master WHERE id = %s"
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
#tweet_id = '1837331936194482673'  # ここに対象のツイートのIDを入力してください
tweet_id = '1855254362643460139'  # ここに対象のツイートのIDを入力してください

#print(credentials['client_id'])
        
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

#client = tweepy.Client(
#    consumer_key=credentials['client_id'],
#    consumer_secret=credentials['client_secret'],
#    access_token=credentials['access_token'],
#    access_token_secret=credentials['access_secret']
#)

client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=credentials['access_token'],
    access_token_secret=credentials['access_token_secret']
)

print("consumer_key="+credentials['api_key'])
print("consumer_secret="+credentials['api_key_secret'])
print("access_token="+credentials['access_token'])
print("access_token_secret="+credentials['access_token_secret'])
print("bearer_token="+credentials['bearer_token'])  

def like_tweet_with_retry(client, tweet_id, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            print("いいねを試みています…")
            client.like(tweet_id)
            print("いいねをつけました")
            return
        except tweepy.errors.TooManyRequests as e:
            reset_time = int(e.response.headers.get("x-rate-limit-reset"))
            reset_datetime = datetime.fromtimestamp(reset_time)
            wait_time = (reset_datetime - datetime.now()).total_seconds()
            
            print(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
            time.sleep(wait_time + 10)  # 余裕をもって10秒追加で待機
            retries += 1
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return
    print("リトライ回数の上限に達しました。操作を終了します。")

# いいね処理の実行
like_tweet_with_retry(client, tweet_id)