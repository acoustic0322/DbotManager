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
            outputLog("ツイート履歴を保存しました。")
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
            cursor.execute(sql, (comment_id,))
            result = cursor.fetchone()
    finally:
        connection.close()

    if result is None:
        outputLog("エラー: 指定したコメントIDに対応するレコードが見つかりません。")
        return None
    
    return result["comment"]  # コメントを返す


# 認証を確認する関数
def verify_credentials(account_master):
#    auth = tweepy.OAuth1UserHandler(
#        'SBd4tiZXE2w65cquDEWHLuqHi',#account_master['api_key'],
#        'K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC',#account_master['api_key_secret'],
#        '1784746395192242176-nuN8bdYBp7NHjYXXQwwo5gn6BUxXwd',#account_master['access_token'],
#        'fJAFIbVZiIDOJwnhFKm2uTo4pmSFAS6CEgGjEaeVC1uaH'#account_master['access_token_secret']
#    )

    auth = tweepy.OAuth1UserHandler(
        'KvW6WlyCmfyCBMRPhzvsQx2pW',#account_master['api_key'],
        'q2HZ3vQd3IX3chkwvO74Nhi4NFUDCvL0yuOrEkMGjnibnle44z',#account_master['api_key_secret'],
        '1737035338269458432-aRxFxngxyewfin23MonoY32nbq3ilM',#account_master['access_token'],
        'lJ4ETUbQTokCv7U0b84rpUoa9peescsaUTPWNlIP5Ea33'#account_master['access_token_secret']
    )

    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        outputLog("認証成功")
        return True
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー")
        return False
    except Exception as e:
        outputLog(f"エラーが発生しました: {e}")
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
        outputLog("認証成功 (API)")
        return api
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー (API)")
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

#    print("consumer_key="+credentials['api_key'])
#    print("consumer_secret="+credentials['api_key_secret'])
#    print("access_token="+credentials['access_token'])
#    print("access_token_secret="+credentials['access_token_secret'])
#    print("bearer_token="+credentials['bearer_token'])    
#    print("認証成功 (Client)")

    return client

def create_client2(credentials):
    client = tweepy.Client(
        consumer_key=credentials['api_key'],
        consumer_secret=credentials['api_key_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret']
    )

#    print("consumer_key="+credentials['api_key'])
#    print("consumer_secret="+credentials['api_key_secret'])
#    print("access_token="+credentials['access_token'])
#    print("access_token_secret="+credentials['access_token_secret'])
#    print("認証成功 (Client)")

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
        outputLog("認証成功 (API)")
        return api
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー (API)")
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
        return f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）"
    except tweepy.errors.TweepyException as e:
        return f"その他エラー({e})"


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
            return outputLog("重複ツイート")
        else:
            return f"その他エラー({e})"
    return ""  # 空文字列を返すことで成功を示す

def outputLog(message):
    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{current_time}] {message}"
    
    # 標準出力にメッセージを出力
    print(full_message)

# コマンドライン引数を解析
#if len(sys.argv) < 4:
#    print("使用方法: python good_tweet3.py account_id=<ID> tweet_id=<TWEET_ID> tweet_mode=<MODE>")
#    sys.exit(1)

args = parse_arguments(sys.argv[1:])
outputLog(args)

account_id = int(args.get("account_id"))
tweet_id = args.get("tweet_id")
tweet_mode = args.get("tweet_mode")
#tweet_text = args.get("text")
comment_id = args.get("comment_id")

# 認証情報を取得
credentials = get_account_master(account_id)

if credentials:
    # 認証を確認
    if verify_credentials(credentials):
        client = create_client(credentials)
        if False:
#        if client:
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
                # エラーメッセージを標準エラーに出力
                print(f"サポートされていないtweet_mode: {tweet_mode}", file=sys.stderr)
#                print(f"エラーが発生しました: ", file=sys.stderr)
                # 終了コードを1にして異常終了を示す
                sys.exit(1)


            if result == "":
                save_tweet_history(account_id, '1' , tweet_mode , tweet_id)
                sys.exit(0)
            else:
                print(f"エラーが発生しました: {result}", file=sys.stderr)
                sys.exit(1)

else:
    print(f"エラーが発生しました: ID {credential_id} の認証情報が見つかりませんでした。", file=sys.stderr)
    sys.exit(1)
