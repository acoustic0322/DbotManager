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

# ツイート履歴をデータベースに保存する関数
def save_tweet_history(account_id, comment_id, tweet_mode, target_tweet_id):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:

        with connection.cursor() as cursor:
            sql = """
                INSERT INTO tweet_history (account_id, comment_id, tweet_mode, target_tweet_id, updatetime)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (account_id, comment_id, tweet_mode, target_tweet_id, datetime.now()))
            connection.commit()
            print("ツイート履歴を保存しました。")
    finally:
        connection.close()        

def get_comment_by_id(comment_id):

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
            sql = "SELECT comment FROM comment_master WHERE id=%s"
            print("comment_id=",comment_id)
            cursor.execute(sql, (comment_id,))
            result = cursor.fetchone()
    finally:
        connection.close()

    if result is None:
        print("エラー: 指定したコメントIDに対応するレコードが見つかりません。")
        return None
    
    return result["comment"]  # コメントを返す


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

    print("consumer_key="+credentials['api_key'])
    print("consumer_secret="+credentials['api_key_secret'])
    print("access_token="+credentials['access_token'])
    print("access_token_secret="+credentials['access_token_secret'])
    print("bearer_token="+credentials['bearer_token'])    
    print("認証成功 (Client)")

    return client

def create_client2(credentials):
    client = tweepy.Client(
        consumer_key=credentials['api_key'],
        consumer_secret=credentials['api_key_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret']
    )

    print("consumer_key="+credentials['api_key'])
    print("consumer_secret="+credentials['api_key_secret'])
    print("access_token="+credentials['access_token'])
    print("access_token_secret="+credentials['access_token_secret'])
    print("認証成功 (Client)")

    return client    

# APIオブジェクトを返す関数 (OAuth 1.0a User Context)
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
        return None

# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

# ツイートにいいねをする関数
def proc_like_tweet_cli(credentials, tweet_id):
    try:

        client = create_client(credentials)
#        consumer_secret=credentials['api_key_secret'],
#        access_token=credentials['access_token'],
#        access_token_secret=credentials['access_token_secret'],
#        bearer_token=credentials['bearer_token']
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
#def proc_bookmark_tweet(client, tweet_id):
#    try:
#        client.bookmark(tweet_id=tweet_id)
#        print("ツイートをブックマークに追加しました。")
#    except tweepy.errors.TweepyException as e:
#        print(f"ブックマークエラー: {e}")

def proc_bookmark_tweet(api, tweet_id):
    try:
        api.create_favorite(tweet_id)
        print("いいねをつけました")
    except tweepy.errors.TweepyException as e:
        print(f"いいねエラー: {e}")

def proc_create_tweet(credentials ,comment_id):

    try:

        # コメントの取得
        value = get_comment_by_id(comment_id)

        # コメントが取得できなかった場合、処理を終了
        if value is None:
            return False        

        client = create_client(credentials)
        response = client.create_tweet(
            text=value
        )
        print(f"https://twitter.com/user/status/{response.data['id']}")   
    except tweepy.errors.Forbidden as e:
        if "You are not allowed to create a Tweet with duplicate content." in str(e):
            print("エラー: 重複ツイートは許可されていません。内容を変更してください。")
        else:
            print(f"その他のエラーが発生しました: {e}")    
        return False

    return True


# コマンドライン引数を解析
if len(sys.argv) < 4:
    print("使用方法: python good_tweet3.py account_id=<ID> tweet_id=<TWEET_ID> tweet_mode=<MODE>")
    sys.exit(1)

args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id"))
tweet_id = args.get("tweet_id")
tweet_mode = args.get("tweet_mode")
#tweet_text = args.get("text")
comment_id = args.get("comment_id")
print("test comment_id=",comment_id)

# 認証情報を取得
credentials = get_account_master(account_id)

if credentials:
    # 認証を確認
    if verify_credentials(credentials):
        client = create_client(credentials)
        if client:
            result = False
            if tweet_mode == "tweet":
                result = proc_create_tweet(credentials, comment_id)
            elif tweet_mode == "like":  #動かない
                result = proc_like_tweet_cli(credentials, tweet_id)
            elif tweet_mode == "bookmark":
                # API認証を確認
                api = create_api(credentials)
                result = proc_bookmark_tweet(api, tweet_id)
            else:
                print(f"サポートされていないtweet_mode: {tweet_mode}")

            if result:
                save_tweet_history(account_id, '1' , tweet_mode , tweet_id)

else:
    print(f"ID {credential_id} の認証情報が見つかりませんでした。")
