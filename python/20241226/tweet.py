import sys
import tweepy
import pymysql
import os
import requests
import time
from datetime import datetime
import pyperclip
import json
from requests_oauthlib import OAuth1Session
from datetime import datetime, timezone, timedelta

from twitter_api_v2 import proc_like_v2
from twitter_api_v2 import proc_bookmark_v2
from twitter_api_v2 import proc_post_v2
from twitter_api_v2 import check_rate_limit2
from twitter_api_v2 import check_access_token
from twitter_api_v2 import refresh_access_token


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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id , id FROM account_master WHERE id = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
#            credentials['id'] = id

            #access_tokenの有効判定を行い、古かったら更新
            credentials['bearer_token'] , credentials['refresh_token'] = check_access_token(credentials)

            return credentials
    finally:
        connection.close()

def get_check_account_list(id):
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
            sql = "SELECT id, enable, mode, check_account , since_id , since_datetime , since_comment FROM check_account_list  WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

# ツイート履歴をデータベースに保存する関数
def save_tweet_history(account_id, comment_id, mode, target_tweet_id , result , error_log):
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
                INSERT INTO tweet_history (account_id, comment_id, mode, target_tweet_id, updatetime , result , error_log)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (account_id, comment_id, mode, target_tweet_id, datetime.now(), result , error_log))
            connection.commit()
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
        outputLog("認証成功")
        return True , "認証成功"
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー")
        return False , "認証エラー"
    except Exception as e:
        outputLog(f"エラーが発生しました: {e}")
        return False , f"エラーが発生しました: {e}"

def verify_credentials_v2(account_master):

    # ここでaccount_master辞書にclient_idとclient_secretが正しく設定されているか確認してください
    client_id = account_master.get('client_id')
    client_secret = account_master.get('client_secret')
    access_token = account_master.get('access_token')

    if not client_id or not client_secret or not access_token:
        outputLog("認証情報が不足しています。client_id, client_secret, access_token, redirect_uri を確認してください。")
        return False, "認証情報が不足しています"

    auth = tweepy.OAuth2UserHandler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="https://d-bot.happywinds.net/d-bot/callback.php",
        scope=["tweet.read", "users.read"]  # 必要なスコープを指定
    )
    
    # アクセストークンを直接設定
    auth.access_token = account_master['access_token']  # アクセストークンを設定
    
    try:
        # `OAuth2UserHandler` を使って `tweepy.Client` を作成
        client = tweepy.Client(
            bearer_token=auth.access_token  # Bearer Tokenとして設定
        )
        
        # ユーザー情報の取得
        user = client.get_me()  # ユーザー情報の取得
        outputLog(f"認証成功: ユーザー名={user.data['username']}")
        print(f"認証成功: ユーザー名={user.data['username']}")
        return True, f"認証成功: ユーザー名={user.data['username']}"
    
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー: アクセストークンが無効です")
        return False, "認証エラー: アクセストークンが無効です"
    
    except Exception as e:
        outputLog(f"verify_credentials_v2エラーが発生しました: {e}")
        return False, f"エラーが発生しました: {e}"


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

def print_id(text):
    print("account_id=",account_id, " " , text)
    return 


def check_bearer_token(credentials):
    # トークン取得時のレスポンス例
    response = {
        "access_token": credentials['bearer_token'],
        "expires_in": 7200,  # 秒単位で有効期限（2時間）
    }

    # 現在時刻（UNIXタイムスタンプ）
    token_acquired_time = time.time()
    
    # トークンの有効期限（UNIXタイムスタンプ）
    token_expiry_time = token_acquired_time + response["expires_in"]

    # UNIXタイムスタンプを見やすい日時形式に変換
    acquired_datetime = datetime.fromtimestamp(token_acquired_time).strftime('%Y-%m-%d %H:%M:%S')
    expiry_datetime = datetime.fromtimestamp(token_expiry_time).strftime('%Y-%m-%d %H:%M:%S')

    # 結果を表示
    print(f"トークン取得時刻: {acquired_datetime}")
    print(f"トークン有効期限: {expiry_datetime}")


def get_twitter_useid(access_token):
    # アクセストークン
#    access_token = "YOUR_ACCESS_TOKEN"

    # APIエンドポイントとヘッダー
    endpoint = "https://api.twitter.com/2/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # リクエスト送信
    response = requests.get(endpoint, headers=headers)

    # レスポンスの処理
    if response.status_code == 200:
        user_data = response.json()
        print("ユーザー情報:", user_data)
        print("user_id:", user_data["data"]["id"])  # user_id を取得
    else:
        print("エラーが発生しました:", response.status_code, response.json())

    return user_data["data"]["id"]



# ツイートにいいねをする関数
def proc_like_oauth20(credentials, tweet_id):
    try:
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']

        new_bearer_token,new_refresh_token = refresh_access_token(client_id,client_secret,refresh_token)

        # 必要な変数を設定
#        access_token = credentials['bearer_token']  # トークン取得時に得られたアクセストークン
        access_token = new_bearer_token#credentials['bearer_token']  # トークン取得時に得られたアクセストークン
#        like_endpoint = "https://provider.com/api/like"  # 「いいね」を行うAPIのエンドポイント
        like_endpoint = "https://api.twitter.com/2/tweets"  # 「いいね」を行うAPIのエンドポイント
        post_id = tweet_id  # 「いいね」する投稿のID
        # ヘッダーを設定
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        # リクエストデータを作成
        data = {
            "post_id": post_id
        }
        # APIリクエストを送信
        response = requests.post(like_endpoint, json=data, headers=headers)
        # レスポンスを確認
        if response.status_code == 200:
            print("Successfully liked the post!")
#            print("Response:", response.json())
            return True , ""
        else:
            print("Failed to like the post.")
            print("Status Code:", response.status_code)
            print("Response:", response.text)
            return False , response.text
    except tweepy.errors.TweepyException as e:
        outputLog(f"その他エラー({e})")
        return False , f"その他エラー({e})"

# 認証
def authenticate_twitter(credentials):
    auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret']  )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

# 認証
def authenticate_twitter2(credentials):
    auth = tweepy.OAuthHandler(credentials['client_id'], credentials['client_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret']  )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api




def is_image_file(file_path):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in image_extensions

def is_video_file(file_path):
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in video_extensions
    
def outputLog(message):
    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#    full_message = f"[{current_time}] [account_id={account_id}] {message}"
    full_message = f"[{current_time}] {message}"
    
    # 標準出力にメッセージを出力
    print(full_message)

def fetch_user_with_retry(client, username, retries=3):
    for attempt in range(retries):
        try:
            user = client.get_user(username=username)
            return user
        except tweepy.errors.TooManyRequests as e:
            print("Rate limit exceeded. Retrying...")
            time.sleep(15 * 60)  # 15分間待機
        except Exception as e:
            print(f"Error fetching user {username}: {e}")
            break
    return None

def truncate_by_byte_length(s, max_bytes, encoding="utf-8"):

    """
    文字列を指定したバイト数で切り詰める関数。
    :param s: 対象の文字列
    :param max_bytes: 最大バイト数
    :param encoding: エンコーディング (デフォルトは UTF-8)
    :return: 切り詰めた文字列
    """

    encoded = s.encode(encoding)  # 文字列をバイト列にエンコード
    if len(encoded) <= max_bytes:
        return s  # バイト数が上限以下ならそのまま返す

    # バイト列を指定バイト数まで切り詰め
    truncated = encoded[:max_bytes]

    print(truncated.decode(encoding, errors="ignore"))

    # 無効なバイトシーケンスが含まれる場合を防ぐためデコードする
    return truncated.decode(encoding, errors="ignore")

def update_check_account_list(id, since_id, datetime):
    print("update_check_account_list")
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
                UPDATE check_account_list set since_id = %s , since_datetime = %s  where id = %s
            """
            cursor.execute(sql, (since_id , datetime , id))
#            sql = """
#                UPDATE check_account_list set since_id = %s , since_datetime = %s , since_comment = %s where id = %s
#            """
#            cursor.execute(sql, (since_id , datetime , truncate_by_byte_length(since_comment, 100), id))
            connection.commit()
    finally:
        connection.close()   

def ConvJstTimeZone(dt_utc):
#    # 日本時間 (UTC+9) のタイムゾーンを定義
#    jst = timezone(timedelta(hours=9))

#    # UTC から JST に変換
#    dt_jst = dt_utc.astimezone(jst)

#    print('Jst:',dt_jst)

    # タイムゾーン情報を削除
    dt_utc_naive = dt_utc.replace(tzinfo=None)    
    print('ConvJstTimeZone:',dt_utc_naive)

#    return dt_jst
    return dt_utc_naive

args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id","0"))
account_id2 = int(args.get("account_id2","0"))
tweet_id = args.get("tweet_id","")
mode = args.get("mode","")
#tweet_text = args.get("text")
comment_id = args.get("comment_id","")
photo_id = args.get("photo_id","")
video_id = args.get("video_id","")
check_list_id = args.get("check_list_id","")
check_account_name = args.get("check_account_name","")
outputLog(args)


# 認証情報を取得
credentials = get_account_master(account_id)

#if True:
#	credentials['bearer_token'] , credentials['refresh_token']   =  refresh_access_token4(credentials,account_id)


if credentials:
    # 認証を確認
#    verify_result , verify_message = verify_credentials(credentials)
#    verify_result , verify_message = verify_credentials_v2(credentials)

#    if verify_result:
    if True:
        client = create_client(credentials)

        if client:
            error_log = ""
            if mode == "post":
                success , error_log = proc_post_v2(credentials)
            elif mode == "reply":
                success , error_log = True , "" #未実装
            elif mode == "repost":
                success , error_log = True , "" #未実装
            elif mode == "like":
                success , error_log = proc_like_v2(credentials, tweet_id)
            elif mode == "bookmark":
                success , error_log = proc_bookmark_v2(credentials, tweet_id)
            elif mode == "refresh":
                success , error_log = refresh_access_token(credentials)
            else:
                # エラーメッセージを標準エラーに出力
                outputLog(f"サポートされていないmode: {mode}")
                # 終了コードを1にして異常終了を示す
                sys.exit(1)

            outputLog(success)

            if success == True:
                save_tweet_history(account_id, comment_id , mode , tweet_id , True , error_log)
                print(json.dumps({"success": True, "error_log": error_log}))
                sys.exit(0)
            else:
#                outputLog(f"エラーが発生しました: {result}", file=sys.stderr)
                save_tweet_history(account_id, comment_id , mode , tweet_id , False , error_log)
                print(json.dumps({"success": False, "error_log": error_log}))
                sys.exit(1)
#    else:
#        save_tweet_history(account_id, comment_id , mode , tweet_id , False , verify_message)

else:
    outputLog(f"エラーが発生しました: ID {credential_id} の認証情報が見つかりませんでした。", file=sys.stderr)
    sys.exit(1)
