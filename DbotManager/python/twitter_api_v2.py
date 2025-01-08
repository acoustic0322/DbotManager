import requests
import json
import time
import sys
#import tweepy
#import pymysql
import os
import base64
import pymysql
from datetime import datetime  # datetime モジュールをインポート

from mysql import get_comment_by_id
from mysql import get_account_master_for_update_refresh
from mysql import update_refresh_token
from mysql import save_tweet_history
from mysql import get_user_id_from_db
from mysql import update_user_id_from_db
from mysql import get_last_tweet_id_from_check_account_list
from mysql import update_last_tweet_id_from_check_account_list
from mysql import update_search_list

import config
from config import convert_tweet_datetime
from config import outputLog

import tweepy

def createClient(credentials):
    try:
        client = tweepy.Client(
            bearer_token=credentials['bearer_token']
        )

#        client = tweepy.Client(
#            bearer_token=credentials['bearer_token'], 
#            consumer_key=credentials['api_key'], 
#            consumer_secret=credentials['api_key_secret'], 
#            access_token=credentials['access_token'], 
#            access_token_secret=credentials['access_token_secret']
#            )

        outputLog("Tweepy Client を正常に作成しました")

        return client

    except tweepy.errors.TweepyException as e:
        outputLog("Tweepy Client 作成中にエラーが発生しました:")
        outputLog(e)
    except KeyError as ke:
        outputLog("認証情報 (credentials) のキーが不足しています:")
        outputLog(ke)
    except Exception as ex:
        outputLog("予期しないエラーが発生しました:")
        outputLog(ex)    

    return None

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
#        outputLog(f"get_user_id {username}のユーザーID: {user_id}")
        return user_id
    else:
#        outputLog(f"get_user_idエラー: {response.status_code}, {response.text}")
        return None

def check_access_token(credentials):

    bearer_token = credentials['bearer_token']
    refresh_token = credentials['refresh_token']

    status_code , contents = check_access_token_validity(credentials['bearer_token'])

    if status_code == 401:
        bearer_token , refresh_token = refresh_access_token(credentials)

    return bearer_token , refresh_token 

def proc_update_refresh_token():
    outputLog("proc_update_refresh_token")
    credentials_list = get_account_master_for_update_refresh()
    for credentials in credentials_list:
#        outputLog("target=",credentials['id'])
        result , access_token , refresh_token = refresh_access_token(credentials)

        save_tweet_history(credentials['id'], '' , 'check_refresh' , '' , result , f"refresh:{refresh_token} access:{access_token}")


def refresh_access_token(credentials):
    try:
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']

#        outputLog("refresh_token=", refresh_token)

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
            outputLog(f"response.json()={response_data}")

            # access_token を抜き出す
            access_token = response_data.get("access_token")
            outputLog(f"access_token={access_token}")

            refresh_token = response_data.get("refresh_token")
            outputLog(f"refresh_token={refresh_token}")

            # スコープを確認する
            scope = response_data.get("scope")
            if scope:
                outputLog(f"付与されたスコープ={scope}")
            else:
                outputLog("スコープ情報が返されていません")

            credentials['refresh_token'] = refresh_token
            credentials['bearer_token'] = access_token

            update_refresh_token(credentials['id'], access_token, refresh_token)

            return True, access_token, refresh_token
        else:
            outputLog(f"refresh_access_tokenエラー: {response.status_code}, {response.text}")
            return False, None, None

    except requests.exceptions.RequestException as req_err:
        outputLog(f"リクエストエラーが発生しました: {req_err}")
        return False, None, None

    except KeyError as key_err:
        outputLog(f"キーエラーが発生しました: 必要なキーが見つかりません: {key_err}")
        return False, None, None

    except Exception as e:
        outputLog(f"予期しないエラーが発生しました: {e}")
        return False, None, None


def check_access_token_validity(access_token):
    url = "https://api.twitter.com/2/users/me"  # ユーザー情報を取得
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # リクエストを送信してアクセストークンの有効性を確認
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        outputLog("check_access_token_validity アクセストークンは有効です。")
        return response.status_code , ""
    elif response.status_code == 401:
        outputLog("check_access_token_validity アクセストークンが無効です。再認証が必要です。")
        return response.status_code , json.dumps(response.json())
    else:
        outputLog(f"check_access_token_validity エラー: {response.status_code}")
        outputLog(response.json())  # エラーメッセージを表示
        return response.status_code , json.dumps(response.json())

def proc_post_v2(credentials ,comment_id, reply_to_tweet_id):

    if config.debug == True:
        outputLog("proc_post_v2 Start")
        outputLog(f"comment_id={comment_id}")
        outputLog(f"reply_to_tweet_id={reply_to_tweet_id}")

    # コメントの取得
    comment = get_comment_by_id(comment_id)

#    outputLog("comment=",comment)

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
        outputLog(headers)
        outputLog(data)
        outputLog(comment)

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

    if config.debug == True:
        outputLog(response.json())

    try:
        # レスポンスを JSON としてパース
        response_data = response.json()
    except ValueError as e:
        if config.debug == True:
        # JSON パースエラー時の処理
            outputLog(f"JSON パースエラー:{ str(e)}")
            outputLog(f"Raw response text:{response.text}")  # 生データを確認
        return False, f"JSON パースエラー: {str(e)}"

#    # レスポンスコードを確認
#    if response.status_code == 201:
#        outputLog("ツイートが成功しました:", response_data)
#    else:
#        outputLog(f"エラー: {response.status_code}")
#        outputLog(response_data)

    # レスポンスを確認
#    if response.status_code == 201:
#        outputLog("proc_post_v2 ポスト/リプライしました:")
#        outputLog(response_data)  # 成功時のレスポンス
#    else:
#        outputLog(f"proc_post_v2 エラー: {response.status_code}")
#        outputLog(response_data)


    response_str = json.dumps(response_data)  # json.dumps を使用
    return response.status_code in (200, 201), response_str


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
#        outputLog("proc_like_v2 ツイートにいいねを付けました:")
#        outputLog(response.json())  # 成功時のレスポンス
#    else:
#        outputLog(f"proc_like_v2 エラー: {response.status_code}")
#        outputLog(response.json())

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code == 200, response_str


def proc_bookmark_v2(credentials, tweet_id):
    """
    指定されたツイートをブックマークする関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: ブックマークする対象のツイートID
    """

#    outputLog("login_id:",credentials['login_id'])

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
#        outputLog("ツイートをブックマークしました:")
#        outputLog(response.json())  # 成功時のレスポンス
#    else:
#        outputLog(f"エラー: {response.status_code}")
#        outputLog(response.json())

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
#        outputLog("リポストが成功しました:")
#        outputLog(response.json())  # 投稿成功時のレスポンス
#    else:
#        outputLog(f"エラー: {response.status_code}")
#        outputLog(response.json())  # エラー時のレスポンス

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code in (200, 201), response_str


def proc_check_v2(credentials , search_row , mode):

    if mode == 'post':
        datetime_column = 'last_post_time'
        serach_reply = False
    elif mode == 'reply':
        datetime_column = 'last_reply_time'
        serach_reply = True
    elif mode == 'monomane':
        datetime_column = 'last_monomane_time'
        serach_reply = False

    search_user_name = search_row['search_user_name']
    search_id = search_row['search_account_id']

    client = createClient(credentials)
    if client is None:
        return False , None,None,None

    result , tweet , tweets = get_latest_tweet(client , search_row['search_user_name'] , serach_reply)

    if result == False:
        return False , tweet,None,None

    if tweet is None:
        return False , None,None,None

    latest_tweet_datetime = convert_tweet_datetime(tweet.data['created_at'])

    # 古いツイートに関しては処理しない
    if datetime_column in search_row and search_row[datetime_column] is not None:
        if search_row[datetime_column] >= latest_tweet_datetime:
            return False , tweet.data['id'] , tweet.data , tweets
#            return True , tweet.data['id'] , tweet.data , tweets

    update_search_list(search_row['id'] , tweet.data['id'] , latest_tweet_datetime , mode)
    
    return True , tweet.data['id'] , tweet.data , tweets


def get_latest_tweet(client , search_user_name , search_replies=True):
    try:
        tweets = client.search_recent_tweets(
            f'from:{search_user_name} -is:retweet',
            tweet_fields=["id", "text", "author_id", "created_at", "attachments", "referenced_tweets", "in_reply_to_user_id"],
            expansions=['attachments.media_keys'],
            media_fields=['url', 'type', 'variants'],
            max_results=100  
        )
        if 'errors' in tweets:
            outputLog("エラーが発生しました:")
            outputLog(tweets['errors'])
        else:
#            outputLog("ツイートを取得しました:")
#            outputLog(tweets.data)

            for tweet in tweets.data:

                #リプライツイート判定
                in_reply_to_tweet_id = str(tweet.referenced_tweets[0]['id']) if tweet.referenced_tweets else ''

#                if in_reply_to_tweet_id != "" and str(tweet.author_id) != userid:
                if in_reply_to_tweet_id != "":
                    if search_replies == True:
                        outputLog(f"tweet.data={tweet.data}")
                        return True , tweet , tweets
                else:
                    if search_replies == False:
                        outputLog(f"tweet.data={tweet.data}")
                        return True , tweet , tweets

            return False , None , None
    except Exception as e:
        outputLog("例外が発生しました:")
        outputLog(e)  
        outputLog(e)  
        return False , e , None

    return False , None , None

def proc_check_v2_2(credentials , search_row):

    check_post = True
    check_reply = True

    client = createClient(credentials)

    tweets = get_latest_tweets(client , search_row['search_user_name'])

    if tweets is None:
        outputLog(f"tweets={tweets}")
        return False , None ,False ,None


    tweet_post = get_latest_tweet2(tweets , False)
    outputLog(f"tweet_post={tweet_post}")
    if tweet_post is not None:
        latest_tweet_datetime = convert_tweet_datetime(tweet_post.data['created_at'])

        # 古いツイートに関しては処理しない
        if 'last_post_time' in search_row and search_row['last_post_time'] is not None:
            if search_row['last_post_time'] >= latest_tweet_datetime:
                check_post = False

        if check_post == True:
            update_search_list(search_row['id'] , tweet_post.data['id'] , latest_tweet_datetime , 'post')

    tweet_reply = get_latest_tweet2(tweets , True)
    if tweet_reply is not None:
        latest_tweet_datetime = convert_tweet_datetime(tweet_reply.data['created_at'])

        # 古いツイートに関しては処理しない
        if 'last_reply_time' in search_row and search_row['last_reply_time'] is not None:
            if search_row['last_reply_time'] >= latest_tweet_datetime:
                check_reply = False
    
        if check_reply == True:
            update_search_list(search_row['id'] , tweet_reply.data['id'] , latest_tweet_datetime , 'reply')

    return check_post , tweet_post , check_reply , tweet_reply


def get_latest_tweets(client , search_user_name):
    try:
        tweets = client.search_recent_tweets(
            f'from:{search_user_name} -is:retweet',
            tweet_fields=["id", "text", "author_id", "created_at", "attachments", "referenced_tweets", "in_reply_to_user_id"],
            expansions=['attachments.media_keys'],
            media_fields=['url', 'type', 'variants'],
            max_results=100  
        )
        if 'errors' in tweets:
            outputLog("エラーが発生しました:")
            outputLog(tweets['errors'])
        else:
            return tweets
    except Exception as e:
        outputLog("例外が発生しました:")
        outputLog(e)  
        outputLog(e)  
        return None

    return None 

def get_latest_tweet2(tweets , search_replies):
    try:
        for tweet in tweets.data:
            #リプライツイート判定
            in_reply_to_tweet_id = str(tweet.referenced_tweets[0]['id']) if tweet.referenced_tweets else ''

#           if in_reply_to_tweet_id != "" and str(tweet.author_id) != userid:
            if in_reply_to_tweet_id != "":
                if search_replies == True:
                    outputLog(f"tweet.data={tweet.data}")
                    return tweet
            else:
                if search_replies == False:
                    outputLog(f"tweet.data={tweet.data}")
                    return tweet

        return None
    except Exception as e:
        outputLog("例外が発生しました:")
        outputLog(e)  
        outputLog(e)  
        return e

    return None
