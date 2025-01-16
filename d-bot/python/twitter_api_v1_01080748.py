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

import tweepy


from mysql import get_comment_by_id
from mysql import get_account_master_for_update_refresh
from mysql import update_refresh_token
from mysql import save_tweet_history
from mysql import get_user_id_from_db
from mysql import update_user_id_from_db
from mysql import get_last_tweet_id_from_check_account_list
from mysql import update_last_tweet_id_from_check_account_list

import config

def proc_post_v10a(credentials ,comment_id, media_type , media_id, reply_to_tweet_id):

    account_id = credentials['id']

    #認証
    client = tweepy.Client(
        consumer_key=credentials['api_key'],
        consumer_secret=credentials['api_key_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret']
    )

    # コメントの取得
    comment = get_comment_by_id(comment_id)

    # 認証
    auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])    
    api = tweepy.API(auth)

    if config.debug == True:
        print("media_type=",media_type)
        print("media_id=",media_id)
        print("comment_id=",comment_id)
        print("reply_to_tweet_id=",reply_to_tweet_id)
        print("comment=",comment)

    # コメントが取得できなかった場合、処理を終了
    if comment is None:
        return False , None

    if media_type is not None:
        media_ids = get_media_ids(api , account_id , media_type , media_id )

    params = {"text": comment}

    if media_ids is not None:
        params["media_ids"] = media_ids

    if reply_to_tweet_id != "":
        params["in_reply_to_tweet_id"] = reply_to_tweet_id

    response = client.create_tweet(**params)

    if config.debug:
        print(type(response))  # オブジェクトの型を確認
        print(dir(response))   # 使用可能な属性とメソッドを確認

    try:
        # レスポンスからデータを取得
        if response.data is not None:
            response_data = response.data  # ツイートに関する情報
        else:
            response_data = {}  # データがない場合は空の辞書にする

    except Exception as e:
        if config.debug:
            print("Error while processing response:", str(e))
            print("Raw response object:", response)  # レスポンス全体を出力
        return False, f"Error while processing response: {str(e)}"

    response_str = json.dumps(response_data)  # JSON 文字列に変換

    if config.debug:
        print("Tweet created successfully:", response_data)
        print("response.errors:", response.errors)
        print("response_str:", response_str)

    # ステータスコードの代わりにエラーを確認
    return response.errors is None or len(response.errors) == 0, response_str

def get_media_ids(api, account_id, media_type, media_id):
    try:
        media_dir = config.media_dir

        media_ext = "jpg"
        media_head = "p"
        if media_type == "video":
            media_ext = "mp4"
            media_head = "m"

        if config.debug == True:
            print("media_dir=", media_dir)
            print("account_id=", account_id)
            print(f"media_file={media_id}.{media_ext}")

        media_path = os.path.join(media_dir, f"{account_id}", f"{media_head}{media_id}.{media_ext}")

        if config.debug == True:
            print("media_path=", media_path)

        # ファイルの存在確認
        if not os.path.exists(media_path):
            raise FileNotFoundError(f"Media file not found: {media_path}")

        media_ids = []

        if media_type == 'photo':
            media = api.media_upload(filename=media_path)
        elif media_type == 'video':
            media = api.media_upload(media_path, media_category='tweet_video')
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

        media_ids.append(media.media_id)

        return media_ids

    except FileNotFoundError as e:
        if config.debug == True:
            print(f"Error: {e}")
        return []  # ファイルが見つからない場合は空のリストを返す

    except tweepy.errors.TweepyException as e:  # 修正点
        if config.debug == True:
            print(f"Tweepy API error: {e}")
        return []  # Tweepy APIでエラーが発生した場合は空のリストを返す

    except Exception as e:
        if config.debug == True:
            print(f"Unexpected error: {e}")
        return []  # その他の予期しないエラーの場合も空のリストを返す


def proc_post_v10a_gomi(credentials ,comment_id, media_type , media_id, reply_to_tweet_id):

    if config.debug == True:
        print("media_type=",media_type)
        print("media_id=",media_id)
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
#    url = "https://api.twitter.com/2/tweets"
    # エンドポイントURL
    url = "https://api.twitter.com/1.1/statuses/update.json"

    # OAuth1の設定
    auth = OAuth1(
        credentials['consumer_key'],
        credentials['consumer_secret'],
        credentials['access_token'],
        credentials['access_token_secret']
    )    
    
    # メディアが指定されている場合、メディアをアップロード
    upload_id = None
    if media_id != "" and media_type != "":
        upload_id = upload_media(credentials, media_id, media_type)
        if not upload_id:
            return False, "メディアアップロードに失敗しました"

    # 投稿するデータ
    data = {
        "text": comment
    }

    if upload_id:
        data["media"] = {
            "media_ids": [upload_id]
        }

    if reply_to_tweet_id:
        data["reply"] = {
            "in_reply_to_tweet_id": reply_to_tweet_id
        }

    # ヘッダー
    headers = {
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



