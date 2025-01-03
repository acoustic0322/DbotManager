import requests
import json
import time
import sys
#import tweepy
#import pymysql
import os
import base64
import pymysql
import pytz
from datetime import datetime  # datetime モジュールをインポート

from mysql import get_comment_by_id
from mysql import get_account_master_for_update_refresh
from mysql import update_refresh_token
from mysql import save_tweet_history
from mysql import get_user_id_from_db
from mysql import update_user_id_from_db
from mysql import get_last_tweet_id_from_check_account_list
from mysql import update_last_tweet_id_from_check_account_list

import config

def get_user_id(credentials):

    access_token = credentials['bearer_token']
    username = credentials['login_id']    

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/json"
    }

    # ユーザーIDを取得するURL
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data["data"]["id"]
#        print(f"get_user_id {username}のユーザーID: {user_id}")
        return user_id
    else:
#        print(f"get_user_idエラー: {response.status_code}, {response.text}")
        return None

def check_access_token(credentials):

    bearer_token = credentials['bearer_token']
    refresh_token = credentials['refresh_token']

    status_code , contents = check_access_token_validity(credentials['bearer_token'])

    if status_code == 401:
        bearer_token , refresh_token = refresh_access_token(credentials)

    return bearer_token , refresh_token 

def proc_update_refresh_token():
    print("proc_update_refresh_token")
    credentials_list = get_account_master_for_update_refresh()
    for credentials in credentials_list:
#        print("target=",credentials['id'])
        result , access_token , refresh_token = refresh_access_token(credentials)

        save_tweet_history(credentials['id'], '' , 'check_refresh' , '' , result , f"refresh:{refresh_token} access:{access_token}")


def refresh_access_token(credentials):
    try:
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']

#        print("refresh_token=", refresh_token)

        url = "https://api.twitter.com/2/oauth2/token"

        # Base64エンコードされたAuthorizationヘッダーを作成
        client_credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"  # Authorizationヘッダーを追加
        }

        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, headers=headers, data=data)

        # HTTPエラーの場合の処理
        if response.status_code == 200:
            response_data = response.json()  # JSONデータを取得
            print("response.json()=", response_data)

            # access_token を抜き出す
            access_token = response_data.get("access_token")
            print("access_token=", access_token)

            refresh_token = response_data.get("refresh_token")
            print("refresh_token=", refresh_token)

            # スコープを確認する
            scope = response_data.get("scope")
            if scope:
                print("付与されたスコープ=", scope)
            else:
                print("スコープ情報が返されていません")

            credentials['refresh_token'] = refresh_token
            credentials['bearer_token'] = access_token

            update_refresh_token(credentials['id'], access_token, refresh_token)

            return True, access_token, refresh_token
        else:
            print(f"refresh_access_tokenエラー: {response.status_code}, {response.text}")
            return False, None, None

    except requests.exceptions.RequestException as req_err:
        print(f"リクエストエラーが発生しました: {req_err}")
        return False, None, None

    except KeyError as key_err:
        print(f"キーエラーが発生しました: 必要なキーが見つかりません: {key_err}")
        return False, None, None

    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return False, None, None


def check_access_token_validity(access_token):
    url = "https://api.twitter.com/2/users/me"  # ユーザー情報を取得
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # リクエストを送信してアクセストークンの有効性を確認
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("check_access_token_validity アクセストークンは有効です。")
        return response.status_code , ""
    elif response.status_code == 401:
        print("check_access_token_validity アクセストークンが無効です。再認証が必要です。")
        return response.status_code , json.dumps(response.json())
    else:
        print(f"check_access_token_validity エラー: {response.status_code}")
        print(response.json())  # エラーメッセージを表示
        return response.status_code , json.dumps(response.json())

def proc_post_v2(credentials ,comment_id, reply_to_tweet_id):

    if config.debug == True:
        print("proc_post_v2 Start")
        print("comment_id=",comment_id)
        print("reply_to_tweet_id=",reply_to_tweet_id)

    # コメントの取得
    comment = get_comment_by_id(comment_id)

#    print("comment=",comment)

    # コメントが取得できなかった場合、処理を終了
    if comment is None:
        return False       

    access_token = credentials['bearer_token']

    # エンドポイントURL
    url = "https://api.twitter.com/2/tweets"
    
    # 投稿するデータ
    data = {
        "text": comment
    }

    if reply_to_tweet_id:
        data["reply"] = {
            "in_reply_to_tweet_id": reply_to_tweet_id
        }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    if config.debug == True:
        print(headers)
        print(data)
        print(comment)

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

    if config.debug == True:
        print(response.json())

    try:
        # レスポンスを JSON としてパース
        response_data = response.json()
    except ValueError as e:
        if config.debug == True:
        # JSON パースエラー時の処理
            print("JSON パースエラー:", str(e))
            print("Raw response text:", response.text)  # 生データを確認
        return False, f"JSON パースエラー: {str(e)}"

#    # レスポンスコードを確認
#    if response.status_code == 201:
#        print("ツイートが成功しました:", response_data)
#    else:
#        print(f"エラー: {response.status_code}")
#        print(response_data)

    # レスポンスを確認
#    if response.status_code == 201:
#        print("proc_post_v2 ポスト/リプライしました:")
#        print(response_data)  # 成功時のレスポンス
#    else:
#        print(f"proc_post_v2 エラー: {response.status_code}")
#        print(response_data)


    response_str = json.dumps(response_data)  # json.dumps を使用
    return response.status_code in (200, 201), response_str


def upload_media(credentials, media_id, media_type):

    # INIファイルのパス
#    config_file = "config.ini"

#    # ConfigParserを使ってINIファイルを読み込む
##    config = configparser.ConfigParser()
#    config.read(config_file, encoding="utf-8")

    # INIファイルからbase_dirを取得 (デフォルトは現在のスクリプトの場所)
#    base_dir = config.get("Paths", "base_dir", fallback=os.path.dirname(os.path.abspath(__file__)))

    media_dir = config.media_dir

    account_id = credentials['id']

    media_ext = "jpg"
    media_head = "p"
    if media_type == "video":
        media_ext = "mp4"
        media_head = "m"

    # 環境変数からベースディレクトリを取得 (デフォルトは現在のスクリプトの場所)
#    base_dir = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))

    # メディアパスを生成
#    media_path = os.path.join(media_dir, "media", media_type, account_id, f"{media_id}.{media_ext}")

    # メディアパスを生成
#    print("media_dir=",media_dir)
#    print("account_id=",account_id)
#    print(f"media_file={media_id}.{media_ext}")
    media_path = os.path.join(media_dir, f"{account_id}", f"{media_head}{media_id}.{media_ext}")
#    print("media_path=",media_path)

#    # 現在のスクリプトがあるディレクトリのパスを取得
#    current_dir = os.path.dirname(os.path.abspath(__file__))
#    print(current_dir)#

#    # 一つ上の階層に移動
#    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
#    print(parent_dir)

#    media_path = os.path.join(parent_dir, "media", media_type, account_id, f"{media_id}.{media_ext}")


    access_token = credentials['bearer_token']
#    access_token = "AAAAAAAAAAAAAAAAAAAAAMQ7wwEAAAAApBmHlycWMnqn5QYxDDT0XZaVs%2BM%3DetF7QRIb2GbbAsoePpnnLN8E8gCFfmuDR5IK9uJDbazDqOQVYN"

    # エンドポイントURL
    url = "https://upload.twitter.com/1.1/media/upload.json"
    
    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # ファイルをバイナリ形式で開く
    with open(media_path, "rb") as media_file:
        files = {
            "media": media_file
        }
        data = {
            "media_category": "tweet_video" if media_type == "video" else "tweet_image"
        }
        # POSTリクエストを送信
        response = requests.post(url, headers=headers, files=files, data=data)

    # レスポンスを確認
    if response.status_code == 200:
        media_id = response.json().get("media_id_string")
        return media_id
    else:

        print(f"レスポンスコード: {response.status_code}")
        print(f"レスポンス内容: {response.text}")        
#        print(f"メディアアップロードエラー: {response.status_code}")
#        response_str = json.dumps(response.json())  # json.dumps を使用
#        print(response_str)
        return None

def proc_like_v2(credentials, tweet_id):
    """
    指定されたツイートに「いいね」を付ける関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: いいねする対象のツイートID
    """
    access_token = credentials['bearer_token']
    user_id = get_user_id(credentials)

    # 「いいね」エンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/likes"

    # 投稿するデータ（ツイートIDを指定）
    data = {
        "tweet_id": tweet_id
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

    # レスポンスを確認
#    if response.status_code == 200:
#        print("proc_like_v2 ツイートにいいねを付けました:")
#        print(response.json())  # 成功時のレスポンス
#    else:
#        print(f"proc_like_v2 エラー: {response.status_code}")
#        print(response.json())

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code == 200, response_str


def proc_bookmark_v2(credentials, tweet_id):
    """
    指定されたツイートをブックマークする関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: ブックマークする対象のツイートID
    """

#    print("login_id:",credentials['login_id'])

    access_token = credentials['bearer_token']

    user_id = get_user_id(credentials)

    # ブックマーク用エンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"

    # 投稿するデータ（ツイートIDを指定）
    data = {
        "tweet_id": tweet_id
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

#    # レスポンスを確認
#    if response.status_code == 200:
#        print("ツイートをブックマークしました:")
#        print(response.json())  # 成功時のレスポンス
#    else:
#        print(f"エラー: {response.status_code}")
#        print(response.json())

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code == 200, response_str

def proc_repost_v2(credentials, tweet_id):
    """
    指定されたツイートIDをリツイートする関数。

    Args:
        credentials (dict): API認証情報を含む辞書（'bearer_token'が必要）。
        tweet_id (str): リツイート対象のツイートID。

    Returns:
        bool: リツイートが成功した場合はTrue、それ以外はFalse。
        str: レスポンスデータまたはエラーメッセージ。
    """
    access_token = credentials['bearer_token']

    user_id = get_user_id(credentials)

    # エンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/retweets"

    # 投稿するデータ（リツイート対象のツイートIDを指定）
    data = {
        "tweet_id": tweet_id
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

#    # レスポンスを確認
#    if response.status_code in (200, 201):
#        print("リポストが成功しました:")
#        print(response.json())  # 投稿成功時のレスポンス
#    else:
#        print(f"エラー: {response.status_code}")
#        print(response.json())  # エラー時のレスポンス

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code in (200, 201), response_str

def proc_check_v2(credentials, username, check_list_id , search_replies=True):
    """
    特定アカウントのツイートを監視し、新しいツイートをリツイートする関数。

    Args:
        credentials (dict): API認証情報。
        username (str): 監視対象のTwitterユーザー名。
        interval (int): 監視間隔（秒）。
    """

    last_tweet_id , last_tweet_datetime = get_last_tweet_id_from_check_account_list(check_list_id , search_replies)
    try:
        latest_tweet_id ,latest_tweet_datetime , result , error_log = get_latest_tweet(credentials, check_list_id, username, search_replies)

        if config.debug == True:
            print("last_tweet_id=",last_tweet_id)
            print("last_tweet_datetime=",last_tweet_datetime)
            print("latest_tweet_id=",latest_tweet_id)
            print("latest_tweet_datetime=",latest_tweet_datetime)

        if result == False:
            return False , error_log

        if (latest_tweet_id and latest_tweet_id != last_tweet_id ) or last_tweet_id is None or last_tweet_id == "":
            if last_tweet_datetime is None or latest_tweet_datetime > last_tweet_dt:
                update_last_tweet_id_from_check_account_list(check_list_id ,latest_tweet_id , latest_tweet_datetime , search_replies)
                return True , latest_tweet_id

        else:
            if config.debug == True:
                print("新しいツイートはありません。")

        return False , last_tweet_id

    except Exception as e:
        if config.debug == True:
            print(f"エラーが発生しました: {e}")
        return False , last_tweet_id

def get_user_id_by_username(credentials, check_list_id, username):
    """
    ユーザー名からユーザーIDを取得する関数。

    Args:
        credentials (dict): API認証情報。
        username (str): Twitterユーザー名。

    Returns:
        str: ユーザーID（成功時）。
    """


#    print("username=",username)
#    print("check_list_id=",check_list_id)
    username_db = get_user_id_from_db(check_list_id)
#    print("username_db=",username_db)

    if username_db != "" and username_db is not None:
#        print("username_db=",username_db)
        return username_db

    access_token = credentials['bearer_token']
#    url = f"https://api.twitter.com/2/users/by/username/{username.lstrip('@')}"
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
#        print("ユーザーID:",user_data.get("data", {}).get("id"))
        update_user_id_from_db(check_list_id , user_data.get("data", {}).get("id"))
        return user_data.get("data", {}).get("id")
    else:
#        print(f"ユーザーIDの取得に失敗: {response.status_code}, {response.text}")
        return None



def convert_tweet_datetime(iso_format_date):
    try:
        # ミリ秒部分とZを無視してパース
        parsed_date = datetime.strptime(iso_format_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as e:
#        print(f"ミリ秒ありのパースエラー: {e}")
        try:
            # ミリ秒が無い場合の処理
            parsed_date = datetime.strptime(iso_format_date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e:
#            print(f"ミリ秒なしのパースエラー: {e}")
            return None

    # UTCタイムゾーンを指定
    utc_zone = pytz.utc
    parsed_date = utc_zone.localize(parsed_date)

    # 日本時間に変換 (UTC + 9)
    japan_zone = pytz.timezone('Asia/Tokyo')
    japan_time = parsed_date.astimezone(japan_zone)

    # フォーマット変更
    return japan_time.strftime("%Y-%m-%d %H:%M:%S")            

def get_latest_tweet(credentials,check_list_id, username, search_replies=True):
    """
    特定ユーザーの最新ツイートを取得する関数。

    Args:
        credentials (dict): API認証情報。
        user_id (str): ユーザーID。

    Returns:
        str: 最新ツイートのID（成功時）。
    """

    user_id = get_user_id_by_username(credentials,check_list_id,username)

    if not user_id:
        if config.debug == True:
            print("ユーザーIDの取得に失敗しました。終了します。")
        return "" , None , False , "ユーザーIDの取得に失敗"

    if config.debug == True:
        print("user_id=",user_id)

    access_token = credentials['bearer_token']
    url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=20&expansions=in_reply_to_user_id&tweet.fields=created_at"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if config.debug == True:
        print(response.status_code)
        print("response.json")
        print(response.json())

    if response.status_code == 200:
        tweets = response.json().get("data", [])

        # リプライかどうかを判別してフィルタリング
        filtered_tweets = [
            tweet for tweet in tweets
            if ('in_reply_to_user_id' in tweet) == search_replies
        ]

        if config.debug == True:
            print("filtered_tweets=",filtered_tweets)

        if filtered_tweets:
            latest_tweet = filtered_tweets[0]
            tweet_id = latest_tweet["id"]
            iso_format_date = latest_tweet.get("created_at", None)  # ツイート日時
    
#            print("iso_format_date")
#            print(iso_format_date)

            # フォーマット変更
            tweet_date = convert_tweet_datetime(iso_format_date)
#            print("tweet_date")
#            print(tweet_date)

            if config.debug == True:
                print("最新ツイート:",filtered_tweets[0]["id"])
            return tweet_id, tweet_date, True, ""            
#            return filtered_tweets[0]["id"] , True , ""

        return  "" , None , False , response.text
#        return  "" , False, response.text
        
    else:
        if config.debug == True:        
            print(f"ツイートの取得に失敗: {response.status_code}, {response.text}")
#        response_str = json.dumps(response.json())  # json.dumps を使用
#        return "" , False, response.text
        return "" , None , False , response.text


