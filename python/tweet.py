import sys
import tweepy
import pymysql
import os
import requests
import time
from datetime import datetime
import pyperclip
from requests_oauthlib import OAuth1Session
from datetime import datetime, timezone, timedelta

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
        return True , ""
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        outputLog(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
        return False , f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）"
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


# ツイートにリポストをする関数
def proc_repost(credentials, tweet_id):
    try:
        client = create_client(credentials)
        # 実行したい操作 (例: 特定のツイートにいいねをつける)
        client.retweet(tweet_id)
        outputLog("リポストしました")
        return True , ""
    except tweepy.errors.TooManyRequests as e:
        # レート制限に引っかかった場合
        reset_time = int(e.response.headers.get("x-rate-limit-reset"))
        reset_datetime = datetime.fromtimestamp(reset_time)
        wait_time = (reset_datetime - datetime.now()).total_seconds()
        outputLog(f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）")
        return False , f"レート制限に達しました。制限解除まで {wait_time // 60} 分待機します（解除時間: {reset_datetime}）"
    except tweepy.errors.TweepyException as e:
        outputLog(f"その他エラー({e})")
        return False , f"その他エラー({e})"

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
        return True , ""
    except Exception as e:
#        return outputLog(f"ブックマークエラー: {e}")
        outputLog(f"ブックマークエラー: {e}")
        return False , f"{e}"


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

def is_image_file(file_path):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in image_extensions

def is_video_file(file_path):
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in video_extensions

def proc_post(credentials ,comment_id, photo_id , video_id, tweet_id):

    try:

        # コメントの取得
        value = get_comment_by_id(comment_id)

        # コメントが取得できなかった場合、処理を終了
        if value is None:
            return False     

        media_ids =[]

        # 現在のスクリプトがあるディレクトリのパスを取得
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(current_dir)

        # 一つ上の階層に移動
        parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
        print(parent_dir)

        print(photo_id)
        print(value)

        if photo_id != '':
            # media/video/1.mp4 のパスを指定
            photo_path = os.path.join(parent_dir, "media", "photo", "1",f"{photo_id}.jpg")
            print(photo_path)
            if os.path.exists(photo_path) and is_image_file(photo_path):

                # 認証オブジェクトの作成
                auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])                
                auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
                api = tweepy.API(auth)

                # 画像をアップロード
                media = api.media_upload(filename=photo_path)
                media_ids.append(media.media_id)           

                client = create_client(credentials)

                if tweet_id == '0':
                    response = client.create_tweet(
                        text=value,
                        media_ids=media_ids
                        )
                else:
                    response = client.create_tweet(
                        text=value,
                        in_reply_to_tweet_id=tweet_id,
                        media_ids=media_ids
                    )                

                print(f"https://twitter.com/user/status/{response.data['id']}")   

                return True , ""  


        elif video_id != '':
            # media/video/1.mp4 のパスを指定
            video_path = os.path.join(parent_dir, "media", "video", "1",f"{video_id}.mp4")
            print(video_path)
            if os.path.exists(video_path) and is_video_file(video_path):

                # 認証オブジェクトの作成
                auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])                
                auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
                api = tweepy.API(auth)

                # 動画をアップロード
                media = api.media_upload(video_path, media_category='tweet_video')
                media_ids.append(media.media_id)           

                client = create_client(credentials)

                if tweet_id == '0':
                    response = client.create_tweet(
                        text=value,
                        media_ids=media_ids
                        )
                else:
                    response = client.create_tweet(
                        text=value,
                        in_reply_to_tweet_id=tweet_id,
                        media_ids=media_ids
                    )                
                print(f"https://twitter.com/user/status/{response.data['id']}") 

                return True , ""  

        else :
            client = create_client(credentials)

            if tweet_id == '0':
                response = client.create_tweet(
                    text=value
                )
            else:
                response = client.create_tweet(
                    text=value,
                    in_reply_to_tweet_id=tweet_id
                )
            print(f"https://twitter.com/user/status/{response.data['id']}")   

            return True , ""  

    except tweepy.errors.Forbidden as e:
        if "You are not allowed to create a Tweet with duplicate content." in str(e):
            return False , outputLog("重複ツイート")
        else:
            return False , outputLog(f"その他エラー({e})")
    return False , ""  # 空文字列を返すことで成功を示す

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

    return True , ""

def proc_get_access_token2(credentials, account_id):
	try:
		# Twitter APIのキーとシークレット
		api_key = credentials['api_key']
		api_secret_key = credentials['api_key_secret']

		# リクエストトークンの取得
		request_token_url = "https://api.twitter.com/oauth/request_token"
		oauth = OAuth1Session(api_key, client_secret=api_secret_key)

		try:
			response = oauth.fetch_request_token(request_token_url)
			oauth_token = response.get("oauth_token")
			oauth_token_secret = response.get("oauth_token_secret")
			print("Request Token取得成功")
			print("OAuth Token:", oauth_token)
			print("OAuth Token Secret:", oauth_token_secret)
		except ValueError as e:
			print("Request Token取得失敗:", e)

		# 認証URLを生成
		base_authorization_url = "https://api.twitter.com/oauth/authorize"
		authorization_url = oauth.authorization_url(base_authorization_url)
		print("次のURLをブラウザで開いて認証してください:", authorization_url)

		# PINコードを入力
		verifier = input("ブラウザで認証後に表示されるPINコードを入力してください: ")

		# アクセストークンの取得
		access_token_url = "https://api.twitter.com/oauth/access_token"
		oauth = OAuth1Session(
			api_key,
			client_secret=api_secret_key,
			resource_owner_key=oauth_token,
			resource_owner_secret=oauth_token_secret,
			verifier=verifier
		)

		try:
			access_token_response = oauth.fetch_access_token(access_token_url)
			access_token = access_token_response.get("oauth_token")
			access_token_secret = access_token_response.get("oauth_token_secret")
			print("Access Token:", access_token)
			print("Access Token Secret:", access_token_secret)
		except ValueError as e:
			print("Access Token取得失敗:", e)

		return True, ""
	except Exception as e:
		print("エラーが発生しました:", e)
		return False, str(e)


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

        try:
            print(f"code: {code}")
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

    return True , ""

    
def outputLog(message):
    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{current_time}] [account_id={account_id}] {message}"
    
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

#search_tweet
def proc_check(credentials , account_id ,account_id2 ,check_account_name, tweet_id ):
    # セッションを作成
    session = requests.Session()
    client = create_client(credentials)
#    check_account = get_check_account_list(check_list_id)

    check_account_name = check_account_name.replace("@","")
#    since_datetime = check_account['since_datetime']

    if tweet_id != None and tweet_id != "":
        tweets = client.search_recent_tweets(
            f'from:{check_account_name} -is:reply',
            since_id=tweet_id,
            max_results=100,
            tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
        )
    else:
        tweets = client.search_recent_tweets(
            f'from:{check_account_name} -is:reply',
            max_results=100,
            tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
        )

    # 取得したツイートを表示する
    if tweets.data is not None and len(tweets.data) > 0:

#        for tweet in tweets.data:
#            print(f"{tweet.id}:{tweet.text}:{ConvJstTimeZone(tweet.created_at)}")

        # ツイートを created_at でソート（降順）
        sorted_tweets = sorted(tweets.data, key=lambda t: t.created_at, reverse=True)
    
        # 一番新しいツイートを取得
        latest_tweet = sorted_tweets[0]
        print(f"Latest Tweet: {latest_tweet.id} - {latest_tweet.text} - {ConvJstTimeZone(latest_tweet.created_at)}")

        if tweet_id != None and tweet_id != "":
            return True , latest_tweet.id
        elif latest_tweet.id != tweet_id:
#        if since_datetime == NoneType or since_datetime < ConvJstTimeZone(latest_tweet.created_at) or since_id == None or since_id == "":
#        if since_datetime < ConvJstTimeZone(latest_tweet.created_at) :
#            update_check_account_list(check_account['id'] , latest_tweet.id , ConvJstTimeZone(latest_tweet.created_at))
            return True , latest_tweet.id

    return False , ""

def proc_check_debug(credentials , check_list_id ):
    # セッションを作成
    session = requests.Session()
    client = create_client(credentials)
    check_account = get_check_account_list(check_list_id)

    print(check_account['check_account'])
    username = check_account['check_account'].replace("@","")
    print(username)

    user = fetch_user_with_retry(client,username)

    check_account_name = check_account['check_account'].replace("@","")
    since_id = check_account['since_id']
    since_datetime = check_account['since_datetime']

    print('since_id:',since_id)
    print('since_datetime:',since_datetime)

    if since_id != None and since_id != "":
        tweets = client.search_recent_tweets(
            f'from:{check_account_name} -is:reply',
            since_id=since_id,
            max_results=100,
            tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
        )
    else:
        tweets = client.search_recent_tweets(
            f'from:{check_account_name} -is:reply',
            max_results=100,
            tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
        )

    # 取得したツイートを表示する
    if tweets.data is not None and len(tweets.data) > 0:

#        for tweet in tweets.data:
#            print(f"{tweet.id}:{tweet.text}:{ConvJstTimeZone(tweet.created_at)}")

        # ツイートを created_at でソート（降順）
        sorted_tweets = sorted(tweets.data, key=lambda t: t.created_at, reverse=True)
    
        # 一番新しいツイートを取得
        latest_tweet = sorted_tweets[0]
        print(f"Latest Tweet: {latest_tweet.id} - {latest_tweet.text} - {ConvJstTimeZone(latest_tweet.created_at)}")

        if since_datetime == NoneType or since_datetime < ConvJstTimeZone(latest_tweet.created_at) or since_id == None or since_id == "":
#        if since_datetime < ConvJstTimeZone(latest_tweet.created_at) :
            update_check_account_list(check_account['id'] , latest_tweet.id , ConvJstTimeZone(latest_tweet.created_at))
            return True , latest_tweet.id

    return False , ""


#search_tweet2
def proc_checkrep(credentials , check_list_id ):
    # セッションを作成
    session = requests.Session()
    client = create_client(credentials)
    check_account = get_check_account_list(check_list_id)

    print(check_account['check_account'])
    username = check_account['check_account'].replace("@","")
    print(username)

    user = fetch_user_with_retry(client,username)

    check_account_name = check_account['check_account'].replace("@","")
    since_id = check_account['since_id']
    since_datetime = check_account['since_datetime']

    print(since_id)
    print(since_datetime)

    if since_id != None and since_id != "":
        tweets = client.search_recent_tweets(
            f'from:{check_account_name} -is:retweet',
            since_id=since_id,
            max_results=100,
            tweet_fields=["id","text", "author_id", "created_at"]
        )
    else:
        tweets = client.search_recent_tweets(
            f'from:{check_account_name} -is:retweet',
            max_results=100,
            tweet_fields=["id","text", "author_id", "created_at"]
        )


    # 取得したツイートを表示する
    if tweets.data is not None and len(tweets.data) > 0:

#        for tweet in tweets.data:
#            print(f"{tweet.id}:{tweet.text}:{ConvJstTimeZone(tweet.created_at)}")

        # ツイートを created_at でソート（降順）
        sorted_tweets = sorted(tweets.data, key=lambda t: t.created_at, reverse=True)
    
        # 一番新しいツイートを取得
        latest_tweet = sorted_tweets[0]
        print(f"Latest Tweet: {latest_tweet.id} - {latest_tweet.text} - {ConvJstTimeZone(latest_tweet.created_at)}")

        if since_datetime == NoneType or since_datetime < ConvJstTimeZone(latest_tweet.created_at) or since_id == None or since_id == "":
#        if since_datetime < ConvJstTimeZone(latest_tweet.created_at) :
            update_check_account_list(check_account['id'] , latest_tweet.id , ConvJstTimeZone(latest_tweet.created_at))
            return True , latest_tweet.id

    return False , ""
            




def proc_monomane(credentials , account_id):

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
    username = "Profile 5"
    print(credentials['login_id'])
    user = client.get_user(username=credentials['login_id'].replace("@",""))
#    user = client.get_user(username=username.replace("@",""))
    print("user=")
    print(user)

    for screen_name in screen_names:
        tmp_screen_name = screen_name.replace("@","")

        since_id=""
        path_tmp_screen_name = sanitize_filename(tmp_screen_name)
        if os.path.exists(os.path.join(folder, f"{path_tmp_screen_name}_sinceid3.txt")):            
            with open(os.path.join(folder, f"{path_tmp_screen_name}_sinceid3.txt"), 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
                since_id = file.read().strip().replace("\r\n","\n").split("\n")[0]
    
        tweeted = []
        if os.path.exists(os.path.join(folder, f"{path_tmp_screen_name}_tweeted3.csv")):            
            with open(os.path.join(folder, f"{path_tmp_screen_name}_tweeted3.csv"), 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for line in reader:
                    tweeted.append(line)

        result_data = None
        if since_id!="":
            try:
                tweets = client.search_recent_tweets(
                    f'from:{tmp_screen_name} -is:retweet',
                    since_id=since_id,
                    max_results=100,
                    tweet_fields=["id","text", "author_id", "created_at","attachments","referenced_tweets","in_reply_to_user_id"],
                    expansions = ['attachments.media_keys'],
                    media_fields = ['url', 'type', 'variants']
                )
            except:
                tweets = client.search_recent_tweets(
                    f'from:{tmp_screen_name} -is:retweet',
                    max_results=100,
                    tweet_fields=["id","text", "author_id", "created_at","attachments","referenced_tweets","in_reply_to_user_id"],
                    expansions = ['attachments.media_keys'],
                    media_fields = ['url', 'type', 'variants']
                )
            if tweets is None or len(tweets) == 0 or tweets.data is None:
                sys.exit()
            result_data = sorted(tweets.data, key=itemgetter('created_at'))
        else:
            tweets = client.search_recent_tweets(
                f'from:{tmp_screen_name} -is:retweet',
                tweet_fields=["id","text", "author_id", "created_at","attachments","referenced_tweets","in_reply_to_user_id"],
                expansions = ['attachments.media_keys'],
                media_fields = ['url', 'type','variants']
            )
            if tweets is None or len(tweets) == 0 or tweets.data is None:
                sys.exit()
            result_data = tweets.data

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

if credentials:
    # 認証を確認
#    verify_result , verify_message = verify_credentials(credentials)

#    if verify_result:
    if True:
        client = create_client(credentials)
        if client:
            error_log = ""
            if mode == "post":
                error_log = proc_post(credentials, comment_id, photo_id , video_id , 0)
#                error_log = proc_post(credentials, comment_id, "1" , "")
#                error_log = proc_post(credentials, comment_id, "" , "1")
            elif mode == "reply":
                success , error_log = proc_post(credentials, comment_id , photo_id, video_id, tweet_id)
            elif mode == "repost":
                success , error_log = proc_repost(credentials, tweet_id)
            elif mode == "like":
                success , error_log = proc_like(credentials, tweet_id)
            elif mode == "bookmark":
                success , error_log = proc_bookmark(credentials, tweet_id, account_id)
            elif mode == "get_refresh_token":
                success , error_log = proc_get_refresh_token(credentials , account_id )
            elif mode == "get_access_token":
#                success , error_log = proc_get_access_token(credentials , account_id )
                success , error_log = proc_get_access_token(credentials , account_id )
            elif mode == "check":
                success , error_log = proc_check(credentials , account_id ,account_id2 ,check_account_name, tweet_id )
            elif mode == "checkrep":
                success , error_log proc_checkrep(credentials , check_list_id )
            elif mode == "monomane":
                success , error_log = proc_monomane(credentials , account_id )
            elif mode == "check_debug":
                success , error_log = proc_check_debug(credentials , check_list_id )
            elif mode == "checkrep_debug":
                success , error_log proc_checkrep_debug(credentials , check_list_id )
            elif mode == "monomane_debug":
                success , error_log = proc_monomane_debug(credentials , account_id )
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
