import sys
import tweepy
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

# 認証を確認する関数
def verify_credentials(account_master):
    auth = tweepy.OAuth1UserHandler(
        account_master['api_key'],
        account_master['api_key_secret'],
        account_master['access_token'],
        account_master['access_token_secret']
    )
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        print("認証成功")
        return True
    except tweepy.errors.Unauthorized:
        print("認証エラー")
        return False
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

# 認証を確認する関数 (APIオブジェクトを返す)
def create_api(credentials):
    auth = tweepy.OAuth1UserHandler(
        credentials['api_key'],
        credentials['api_key_secret'],
        credentials['access_token'],
        credentials['access_token_secret']
    )
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        print("認証成功 (API)")
        return api
    except tweepy.errors.Unauthorized:
        print("認証エラー (API)")
        return Nonev

# 認証を確認する関数 (Clientオブジェクトを返す)
def create_client(credentials):
    client = tweepy.Client(
        consumer_key=credentials['api_key'],
        consumer_secret=credentials['api_key_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret'],
        bearer_token=credentials['bearer_token']
    )
    print("認証成功 (Client)")
    return client

# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

# ツイートにいいねをする関数
def like_tweet(api, tweet_id):
    try:
        api.create_favorite(tweet_id)
        print("ツイートにいいねしました。")
    except tweepy.errors.TweepyException as e:
        print(f"いいねエラー: {e}")
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        print(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")

# ツイートにいいねをする関数
def like_tweet_cli(client, tweet_id):
    try:
        # 実行したい操作 (例: 特定のツイートにいいねをつける)
        client.like(tweet_id)
        print("いいねをつけました")
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        print(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
    except tweepy.errors.TweepyException as e:
        print(f"いいねエラー: {e}")


# ツイートをブックマークに追加する関数
def bookmark_tweet(client, tweet_id):
    try:
        client.bookmark(tweet_id=tweet_id)
        print("ツイートをブックマークに追加しました。")
    except tweepy.errors.TweepyException as e:
        print(f"ブックマークエラー: {e}")

# コマンドライン引数を解析
if len(sys.argv) < 4:
    print("使用方法: python good_tweet3.py account_id=<ID> tweet_id=<TWEET_ID> tweet_mode=<MODE>")
    sys.exit(1)

args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id"))
tweet_id = args.get("tweet_id")
tweet_mode = args.get("tweet_mode")

# 認証情報を取得
credentials = get_account_master(account_id)

if credentials:
    # 認証を確認
    if verify_credentials(credentials):
        if tweet_mode == "like":
#            # APIを利用して「いいね」を実行
#            api = create_api(credentials)
#            if api:
#                like_tweet(api, tweet_id)
            client = create_client(credentials)
            like_tweet_cli(client, tweet_id)
        elif tweet_mode == "bookmark":
            # Clientを利用して「ブックマーク」を実行
            client = create_client(credentials)
            if client:
                bookmark_tweet(client, tweet_id)
        else:
            print(f"サポートされていないtweet_mode: {tweet_mode}")
else:
    print(f"ID {credential_id} の認証情報が見つかりませんでした。")
