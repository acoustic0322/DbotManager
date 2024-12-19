import sys
import tweepy
import pymysql
import os
import requests
import time
from datetime import datetime
import pyperclip
import json

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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
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


def update_access_token(account_id, access_token, access_token_secret):
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
                UPDATE account_master set access_token = %s , access_token_secret = %s where id = %s
            """
            cursor.execute(sql, (access_token , access_token_secret , account_id))
            connection.commit()
    finally:
        connection.close()    

def update_refresh_token(account_id, bearer_token, refresh_token):
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
                UPDATE account_master set bearer_token = %s , refresh_token = %s where id = %s
            """
            cursor.execute(sql, (bearer_token , refresh_token , account_id))
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
#def parse_arguments(args):
#    params = {}
#    for arg in args:
#        key, value = arg.split('=')
#        params[key] = value
#    return params

def parse_arguments(args):
    parsed_args = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)  # 最初の1つ目の = だけで分割
            parsed_args[key] = value
        else:
            raise ValueError(f"Invalid argument format: {arg}")
    return parsed_args

def print_id(text):
    print("account_id=",account_id, " " , text)
    return 

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


def proc_get_access_token2(credentials , account_id , oauth_token , oauth_verifier):
    # アクセストークンとアクセストークンシークレットを取得
    try:
#        print("test0")
        # 認証オブジェクトの作成
        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])

#        print("test1")

        auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}
#        print("test2")
        auth.get_access_token(oauth_verifier)
#        print("test3")
        access_token = auth.access_token
#        print("test4")
        access_token_secret = auth.access_token_secret
#        print("AccessToken=")
#        print(access_token)
#        print("AccessTokenSecret=")
#        print(access_token_secret)

        update_access_token(account_id , access_token , access_token_secret)

        # 結果をJSON形式で出力
        result = {
            "status": "success",
            "access_token": access_token,
            "access_token_secret": access_token_secret
        }
        print(result)

#        # 成功した場合の結果を標準出力
#        print(json.dumps({
#            "status": "success",
#            "account_id": account_id,
#            "access_token": access_token,
#            "access_token_secret": access_token_secret
#        }))
        return True  # 成功の終了コード

    except Exception as e:
        # エラーが発生した場合のメッセージを標準出力
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))
        return False  # エラーの終了コード

def proc_get_refresh_token_web(credentials , account_id , code):
    try:

        print(code)

        # スコープのリスト（できるだけ多く指定）
        scopes = [
            "tweet.read",
            "tweet.write",
            "users.read",
            "offline.access",
            "bookmark.read",
            "bookmark.write"
        ]

        print('0')
        print(credentials['client_id'])
        print(credentials['client_secret'])

        auth = tweepy.OAuth2UserHandler(
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            redirect_uri='https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec',
            scope=scopes
        )

        # 認証URLを取得する
        authorization_url = auth.get_authorization_url()
#        print(f"右のURLにツイートしたいアカウントでアクセスする: {authorization_url}")
        print(f"以下のURLをクリップボードにコピーしました。ブラウザを開いてアクセスしてください: ")
        print(f"{authorization_url}")

        # クリップボードにコピー
        pyperclip.copy(authorization_url)

        # 認証後のコールバックURLからコードを取得し、アクセストークンを交換する
        code = input("ブラウザで認証後に表示されるコードを入力してください: ")
        os.system('cls')        

#        # 認証後のコールバックURLからコードを取得し、アクセストークンを交換する
#        code = input("ブラウザで認証後に表示されるコードを入力してください: ")
#        os.system('cls')

        print('00')

        print(code)
        try:
            token = auth.fetch_token(code)
        except Exception as e:
            print(f"エラー: {e}")            

        print('1')

        # アクセストークンとリフレッシュトークンを取得する
        bearer_token = token.get("access_token")
        refresh_token = token.get("refresh_token")
        # expires_in = token.get("expires_in")

#            print(f"Bearer Token: {bearer_token}")
#            print(f"Refresh Token: {refresh_token}")

        print('2')

        update_refresh_token(account_id , bearer_token , refresh_token)

        print('3')
        print(bearer_token)
        print(refresh_token)

        # 結果をJSON形式で出力
        result = {
            "status": "success",
            "bearer_token": bearer_token,
            "refresh_token": refresh_token
        }
        print('4')

        print(result)
        # print(f"Expires In: {expires_in}")

        return True  # 成功の終了コード

    except Exception as e:
        # エラーが発生した場合のメッセージを標準出力
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))
        return False  # エラーの終了コード 
#    return True , ""    


def outputLog(message):
    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{current_time}] [account_id={account_id}] {message}"
    
    # 標準出力にメッセージを出力
    print(full_message)



args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id","0"))
tweet_id = args.get("tweet_id","")
mode = args.get("mode","")
#tweet_text = args.get("text")
comment_id = args.get("comment_id","")
photo_id = args.get("photo_id","")
video_id = args.get("video_id","")
oauth_token = args.get("oauth_token","")
oauth_verifier = args.get("oauth_verifier","")
url = args.get("url","")
#outputLog(args)

# 認証情報を取得
credentials = get_account_master(account_id)

if credentials:
    # 認証を確認
#    verify_result , verify_message = verify_credentials(credentials)

#    if verify_result:
    if True:
        client = create_client(credentials)
        if client:
            error_log = ""
            if mode == "get_access_token2":
                success = proc_get_access_token2(credentials , account_id , oauth_token , oauth_verifier)
            elif mode == "get_refresh_token_web":
                print('test')
                success = proc_get_refresh_token_web(credentials , account_id , url)
            else:
                # エラーメッセージを標準エラーに出力
                outputLog(f"サポートされていないmode: {mode}")
                # 終了コードを1にして異常終了を示す
#                return 0

#            outputLog(success)

            if success == True:
                save_tweet_history(account_id, comment_id , mode , tweet_id , True , error_log)
#                return 1
            else:
#                outputLog(f"エラーが発生しました: {result}", file=sys.stderr)
                save_tweet_history(account_id, comment_id , mode , tweet_id , False , error_log)
#                return 0

#    else:
#        save_tweet_history(account_id, comment_id , mode , tweet_id , False , verify_message)

else:
    outputLog(f"エラーが発生しました: ID {credential_id} の認証情報が見つかりませんでした。", file=sys.stderr)
#    sys.exit(1)
