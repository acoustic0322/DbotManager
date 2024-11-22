import sys
import tweepy
import pymysql
import os
import requests
import time
from datetime import datetime
import pyperclip

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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

# ツイート履歴をデータベースに保存する関数
def save_tweet_history(account_id, comment_id, tweet_mode, target_tweet_id , result , error_log):
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
                INSERT INTO tweet_history (account_id, comment_id, tweet_mode, target_tweet_id, updatetime , result , error_log)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (account_id, comment_id, tweet_mode, target_tweet_id, datetime.now(), result , error_log))
            connection.commit()
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
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

def print_id(text):
    print("account_id=",account_id, " " , text)
    return 

# ツイートにいいねをする関数
def proc_like(credentials, tweet_id):
    try:
        client = create_client(credentials)
        # 実行したい操作 (例: 特定のツイートにいいねをつける)
        client.like(tweet_id)
        outputLog("いいねをつけました")
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        return outputLog(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
    except tweepy.errors.TweepyException as e:
        return outputLog(f"その他エラー({e})")

def proc_like_test(credentials, tweet_id):
    try:
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']

        new_bearer_token,new_refresh_token = refresh_access_token(client_id,client_secret,refresh_token)
        outputLog(f"new_bearer_token= {new_bearer_token}")
        outputLog(f"new_refresh_token= {new_refresh_token}")
        update_refresh_token(account_id, new_bearer_token , new_refresh_token)

        client = tweepy.Client(
            bearer_token=new_bearer_token,
            consumer_key=credentials['api_key'],
            consumer_secret=credentials['api_key_secret'],
            access_token=credentials['access_token'],
            access_token_secret=credentials['access_token_secret']             
        )

#        client = create_client(credentials)
        # 実行したい操作 (例: 特定のツイートにいいねをつける)
        client.like(tweet_id)
        outputLog("いいねをつけました")
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        return outputLog(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
    except tweepy.errors.TweepyException as e:
        return outputLog(f"その他エラー({e})")

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

# 特定のツイートにいいねをする
def proc_like_test2(credentials, tweet_id):
    api = authenticate_twitter(credentials)
    try:
        api.create_favorite(tweet_id)
        print(f"ツイートID {tweet_id} にいいねしました！")
    except tweepy.errors.Forbidden as e:
        print(f"権限エラー: {e}")
    except tweepy.errors.HTTPException as e:
        print(f"HTTPエラー: {e}")
    except Exception as e:
        print(f"その他のエラー: {e}")

# ツイートにリプライをする関数
def proc_retweet(credentials, tweet_id):
    try:
        client = create_client(credentials)
        # 実行したい操作 (例: 特定のツイートにいいねをつける)
        client.retweet(tweet_id)
        outputLog("リプライしました")
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        return outputLog(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
    except tweepy.errors.TweepyException as e:
        return outputLog(f"その他エラー({e})")

# ツイートをブックマークに追加する関数
def proc_bookmark(credentials, tweet_id, account_id):
    try:
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']

        new_bearer_token,new_refresh_token = refresh_access_token(client_id,client_secret,refresh_token)
        outputLog(f"new_bearer_token= {new_bearer_token}")
        outputLog(f"new_refresh_token= {new_refresh_token}")
        update_refresh_token(account_id, new_bearer_token , new_refresh_token)

        client = tweepy.Client(
            bearer_token=new_bearer_token,
            consumer_key=credentials['api_key'],
            consumer_secret=credentials['api_key_secret'],
            access_token=credentials['access_token'],
            access_token_secret=credentials['access_token_secret']             
        )
        client.bookmark(tweet_id=tweet_id)
        outputLog("ツイートをブックマークに追加しました。")
    except Exception as e:
        return outputLog(f"ブックマークエラー: {e}")


# リフレッシュトークンで新たなベアラトークンを取得
def refresh_access_token(client_id, client_secret, refresh_token):
    # ヘッダーを設定
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # データを設定
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_id': client_id,
    }

    # リクエストを送信
    response = requests.post(
        'https://api.twitter.com/2/oauth2/token',
        headers=headers,
        data=data,
        auth=(client_id, client_secret)
    )
    
    # レスポンスのステータスコードを確認
    if response.status_code != 200:
        # print(f"Error: {response.status_code}")
        # print(response.json())
        return None, None

    response_json = response.json()
    
    print(response_json)  # デバッグ用出力
    # print("access_token："+response_json.get('access_token'))
    # print("refresh_token："+response_json.get('refresh_token'))
    # input()
    
    return response_json.get('access_token'), response_json.get('refresh_token')


def proc_tweet(credentials ,comment_id):

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
            return outputLog(f"その他エラー({e})")
    return ""  # 空文字列を返すことで成功を示す

def proc_get_access_token(credentials , account_id):
    try:
        # 認証オブジェクトの作成
        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])

        # 認可URLの取得
        redirect_url = auth.get_authorization_url()

#        print(f"右のURLにツイートしたいアカウントでアクセスする: {redirect_url}")
        print(f"以下のURLをクリップボードにコピーしました。ブラウザを開いてアクセスしてください: ")
        print(f"{redirect_url}")

        # クリップボードにコピー
        pyperclip.copy(redirect_url)


        oauth_token = input("oauth_tokenを入力: ")
        oauth_verifier = input("oauth_verifierを入力: ")
        os.system('cls')

        # アクセストークンとアクセストークンシークレットを取得
        try:
            auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}
            auth.get_access_token(oauth_verifier)
            access_token = auth.access_token
            access_token_secret = auth.access_token_secret
            print("アクセストークン：")
            print(access_token)
            print("アクセスシークレットトークン：")
            print(access_token_secret)

            update_access_token(account_id , access_token , access_token_secret)

#            input("アクセストークン,アクセストークンシークレットを更新しました")
#            os.system('cls')
            print("アクセストークン,アクセストークンシークレットを更新しました")
        except Exception as e:
            print(f"エラー: {e}")
            input()
    except Exception as e:
        print(f"エラー: {e}")

    print("何かキーを押すと終了します...")  
    input()  # ユーザーの入力を待機

def proc_get_refresh_token(credentials , account_id):
    try:
        # スコープのリスト（できるだけ多く指定）
        scopes = [
            "tweet.read",
            "tweet.write",
            "users.read",
            "offline.access",
            "bookmark.read",
            "bookmark.write"
        ]

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

        try:
            token = auth.fetch_token(code)

            # アクセストークンとリフレッシュトークンを取得する
            bearer_token = token.get("access_token")
            refresh_token = token.get("refresh_token")
            # expires_in = token.get("expires_in")

            print(f"Bearer Token: {bearer_token}")
            print(f"Refresh Token: {refresh_token}")

            update_refresh_token(account_id , bearer_token , refresh_token)

            # print(f"Expires In: {expires_in}")

#            input("保存ができたらエンター")
#            input("BearerToken,RefreshTokenを更新しました")
            print("BearerToken,RefreshTokenを更新しました")
        except Exception as e:
            print(f"エラー: {e}")
            input()
    except Exception as e:
        print(f"エラー: {e}")
    
def outputLog(message):
    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{current_time}] [account_id={account_id}] {message}"
    
    # 標準出力にメッセージを出力
    print(full_message)



args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id","0"))
tweet_id = args.get("tweet_id","")
tweet_mode = args.get("tweet_mode","")
#tweet_text = args.get("text")
comment_id = args.get("comment_id","")
outputLog(args)


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
            if tweet_mode == "tweet":
                error_log = proc_tweet(credentials, comment_id)
            elif tweet_mode == "retweet":
                error_log = proc_retweet(credentials, tweet_id)
            elif tweet_mode == "like":  #動かない
                error_log = proc_like(credentials, tweet_id)
            elif tweet_mode == "bookmark":
                error_log = proc_bookmark(credentials, tweet_id, account_id)
            elif tweet_mode == "get_refresh_token":
                error_log = proc_get_refresh_token(credentials , account_id )
            elif tweet_mode == "get_access_token":
                error_log = proc_get_access_token(credentials , account_id )
            else:
                # エラーメッセージを標準エラーに出力
                outputLog(f"サポートされていないtweet_mode: {tweet_mode}")
                # 終了コードを1にして異常終了を示す
                sys.exit(1)

            if error_log == None:
                save_tweet_history(account_id, comment_id , tweet_mode , tweet_id , True , "")
                sys.exit(0)
            else:
                save_tweet_history(account_id, comment_id , tweet_mode , tweet_id , False , error_log)
#                print(f"エラーが発生しました: {result}", file=sys.stderr)
                sys.exit(1)
#    else:
#        save_tweet_history(account_id, comment_id , tweet_mode , tweet_id , False , verify_message)

else:
    outputLog(f"エラーが発生しました: ID {credential_id} の認証情報が見つかりませんでした。", file=sys.stderr)
    sys.exit(1)
