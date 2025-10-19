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
import re

from mysql import get_comment_by_id
from mysql import get_account_master_for_update_refresh
from mysql import update_refresh_token
from mysql import save_tweet_history
from mysql import get_user_id_from_db
from mysql import update_user_id_from_db
from mysql import get_last_tweet_id_from_check_account_list
from mysql import update_last_tweet_id_from_check_account_list
from mysql import update_search_list
from mysql import insert_tweet_history_monomane
from mysql import insert_search_history
from mysql import update_account_master_by_twitter_user_id
from mysql import update_account_master_by_check_rep_datetime
from mysql import get_trend_list_keyword
from mysql import get_check_tweet_account_list_by_tweet_id


from search_chat import get_tweet_text_from_yahoo_trend
from search_chat import get_tweet_text_from_yahoo_btc
from search_chat import get_tweet_text_from_yahoo_pair  # レート取得できないため、未対応
from search_chat import get_tweet_text_from_yahoo_gold  # レート取得できないため、未対応


import config
from config import convert_tweet_datetime
from config import convert_tweet_datetime2
from config import outputLog

import tweepy
from datetime import datetime, timezone

#chatgpt フォルダを Python のパスに追加
sys.path.append(os.path.abspath("chatgpt"))

from chatgpt_reply import generate_reply
#from chatgpt_tweet import generate_tweet,refine_tweet,generate_trend_tweet_by_keyword
from chatgpt_tweet import generate_tweet

# 2025.10.15 追加
from prompt import PROMPT1
from prompt import past_tweets_1


def createClient(credentials):
    try:
        client = tweepy.Client(
            bearer_token=credentials['bearer_token']
        )

        if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
            outputLog(f"proxy_url={credentials['proxy_url']}")
            client.session.proxies = {"http": credentials['proxy_url'],"https": credentials['proxy_url']}        

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

   

def get_user_id(credentials , username):

    access_token = credentials['bearer_token']

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/json"
    }

    # ユーザーIDを取得するURL
    url = f"https://api.twitter.com/2/users/by/username/{username}"

    outputLog(f"credentials['proxy_enable']  {credentials['proxy_enable'] }")    
    outputLog(f"credentials['proxy_url']  {credentials['proxy_url']}")    

    # POSTリクエストを送信
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
#        response = requests.get(url, headers=headers ,proxies=proxies)
        response = requests.get(url, headers=headers)
    else:
        outputLog(f"proxy_url None")
        response = requests.get(url, headers=headers)

#    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()

        # "data" がない場合（ユーザーが存在しない）
        if "data" not in user_data:
            error_msg = user_data.get("errors", [{"detail": "ユーザーが見つかりません。"}])[0].get("detail")
            outputLog(f"get_user_idエラー: {error_msg}")
            print(f"get_user_idエラー: {error_msg}")
            return None, False, error_msg

        user_id = user_data["data"]["id"]
        outputLog(f"get_user_id {username}のユーザーID: {user_id}")
        return user_id , True , None
    else:
        outputLog(f"get_user_idエラー: {response.status_code}, {response.text}")
        return None , False , response.text

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
    outputLog(f"credentials_list={credentials_list}")
    for credentials in credentials_list:
#        outputLog(f"target={credentials['id']}")
        result , access_token , refresh_token = refresh_access_token(credentials)

        save_tweet_history(credentials['id'], '' , 'check_refresh' , '' , result , f"refresh:{refresh_token} access:{access_token}")


def refresh_access_token(credentials):
    try:
        client_id = credentials['client_id']
        client_secret = credentials['client_secret']
        refresh_token = credentials['refresh_token']

        outputLog(f"id={credentials['id']}")
        outputLog(f"client_id={client_id}")
        outputLog(f"client_secret={client_secret}")
        outputLog(f"refresh_token={refresh_token}")

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

        # POSTリクエストを送信
#        if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
#            outputLog(f"proxy_url={credentials['proxy_url']}")
#            proxies = {
#                "http": credentials['proxy_url'],
#                "https": credentials['proxy_url']
#            }
#            response = requests.post(url, headers=headers, json=data, proxies=proxies)
#        else:
#            response = requests.post(url, headers=headers, json=data)
        response = requests.post(url, headers=headers, data=data)

        outputLog(f"response={response}")


        # HTTPエラーの場合の処理
        if response.status_code == 200:
            response_data = response.json()  # JSONデータを取得
#            outputLog(f"response.json()={response_data}")

            # access_token を抜き出す
            access_token = response_data.get("access_token")
#            outputLog(f"access_token={access_token}")

            refresh_token = response_data.get("refresh_token")
#            outputLog(f"refresh_token={refresh_token}")

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
            outputLog(f"refresh_access_tokenエラー:ID {credentials['id']} {response.status_code}, {response.text}")
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

def proc_post_v2(credentials ,comment_id, reply_to_tweet_id ):

    outputLog("proc_post_v2 Start")
    outputLog(f"comment_id={comment_id}")
    outputLog(f"reply_to_tweet_id={reply_to_tweet_id}")
    outputLog(f"GROQ_API_KEY={credentials['GROQ_API_KEY']}")
    outputLog(f"OPENAI_API_KEY={credentials['OPENAI_API_KEY']}")
    ai_mode = credentials['ai_mode']
    ai_post_enable = credentials['ai_post_enable']
    ai_reply_enable = credentials['ai_reply_enable']
    outputLog(f"ai_mode={ai_mode}")
    outputLog(f"ai_reply_enable={ai_reply_enable}")
    outputLog(f"ai_post_prompt={credentials['ai_post_prompt']}")
    outputLog(f"ai_reply_example={credentials['ai_reply_example']}")

    ai_flag = False

    # リプライモード
    if reply_to_tweet_id:
        # 2025.09.02 AIの判定はpython側にシフトする
        if ai_reply_enable == 0 or ai_mode == 0:
            outputLog("固定コメント")
            comment = get_comment_by_id(comment_id)
        else:
            outputLog("AIコメント")
            ai_flag = True

            # reply_to_tweet_id からツイート内容を取得
            target_check_tweet_account_list = get_check_tweet_account_list_by_tweet_id(reply_to_tweet_id)
            tweet_text = target_check_tweet_account_list['tweet_text']

            comment = generate_reply(credentials['GROQ_API_KEY'],credentials['ai_post_prompt'],credentials['ai_reply_example'],tweet_text)  #コメント内容

            # 裏垢女子モード時は文章を整形
#            if ai_mode == 2:
#                outputLog("裏垢女子")
#                comment = refine_tweet(credentials['OPENAI_API_KEY'],comment)

            outputLog(f"ツイート文:{tweet_text}")           
            outputLog(f"リプライコメント:{comment}")           

    # ポストモード
    else:

        if ai_post_enable == 0 or ai_mode == 0:
            outputLog("固定コメント")
            if comment_id != 0:
                comment = get_comment_by_id(comment_id)
            else:
                outputLog("固定コメントがありません(comment_id=0です)")
        else:

            # 裏垢女子モード
#            if ai_mode == 1 or ai_mode == 2:
            if ai_mode == 1:
                ai_flag = True
                outputLog("AIコメント")

                # ai_post_promptが未設定ならFalseを返す
                if not credentials.get('ai_post_prompt'):
                    outputLog("ai_post_promptが未設定のため中止")
                    return False, "ai_post_prompt未設定"                

                # ai_post_exampleが未設定ならFalseを返す
                if not credentials.get('ai_post_example'):
                    outputLog("ai_post_exampleが未設定のため中止")
                    return False, "ai_post_example未設定"                

#                comment = generate_tweet(credentials['GROQ_API_KEY'],credentials['ai_post_prompt'],credentials['ai_post_example'])
                comment = generate_tweet(credentials['GROQ_API_KEY'],PROMPT1,past_tweets_1)

#                # 裏垢女子モード時は文章を整形
#                if ai_mode == 2:
#                    outputLog("裏垢女子")
#                    comment = refine_tweet(credentials['OPENAI_API_KEY'],comment)

            # yahooトレンドモード
            elif ai_mode == 2:
                comment = get_tweet_text_from_yahoo_trend(credentials['GROQ_API_KEY'])
            # BTC為替レートツイートモード
            elif ai_mode == 3:
                comment = get_tweet_text_from_yahoo_btc(credentials['GROQ_API_KEY'])
            # GOLD為替レートツイートモード(未対応)
            elif ai_mode == 4:
                comment = get_tweet_text_from_yahoo_gold(credentials['GROQ_API_KEY'])
            # 他通貨為替レートツイートモード(未対応)
            elif ai_mode == 5:
                comment = get_tweet_text_from_yahoo_pair(credentials['GROQ_API_KEY'])
            else:
                kw1 , kw2 = get_trend_list_keyword()
                outputLog(f"kw1={kw1}")
                outputLog(f"kw2={kw2}")

                # ai_trend_promptが未設定ならFalseを返す
                if not credentials.get('ai_trend_prompt'):
                    outputLog("ai_trend_promptが未設定のため中止")
                    return False, "ai_trend_prompt未設定"                

                comment = generate_trend_tweet_by_keyword(credentials['OPENAI_API_KEY'],credentials['ai_trend_prompt'],kw1,kw2)


    outputLog(f"comment={comment}")

    # コメントが取得できなかった場合、処理を終了
    if comment is None:
        outputLog("comment is None")
        return False , ""

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

#    if 1==1:
#        return False , False


    # POSTリクエストを送信
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
    else:
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

    if ai_flag == True:
        return response.status_code in (200, 201), 'ai_post'

    return response.status_code in (200, 201), response_str

def proc_post_v2_monomane(credentials ,tweet_text):

    outputLog("proc_post_v2 Start")
    outputLog(f"GROQ_API_KEY={credentials['GROQ_API_KEY']}")
    outputLog(f"OPENAI_API_KEY={credentials['OPENAI_API_KEY']}")

    access_token = credentials['bearer_token']

    # エンドポイントURL
    url = "https://api.twitter.com/2/tweets"
    
    # 投稿するデータ
    data = {
        "text": tweet_text
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # POSTリクエストを送信
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
    else:
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

    response_str = json.dumps(response_data)  # json.dumps を使用

    return response.status_code in (200, 201), response_str



def proc_like_v2(credentials, tweet_id):
    """
    指定されたツイートに「いいね」を付ける関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: いいねする対象のツイートID
    """
    access_token = credentials['bearer_token']
    user_id , result , contents = get_user_id(credentials ,  credentials['login_id'])
    if result == False:
        return False , contents        

    outputLog(f"user_id={user_id}")

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

    outputLog(f"client_id={credentials['client_id']}")

    # POSTリクエストを送信
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }

        # 2025.05.16  一旦プロキシ無効
#        response = requests.post(url, headers=headers, json=data)
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
    else:
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

def proc_search_v2(credentials):

    # 検索したいキーワード（複数可）
    keywords = ["FX", "為替", "傾向"]
    query = " OR ".join(keywords)  # OR でキーワードを連結

    # Twitter API v2 のエンドポイント
    url = "https://api.twitter.com/2/tweets/search/recent"

    # リクエストヘッダー
    headers = {
        "Authorization": f"Bearer {credentials['bearer_token']}",
        "Content-Type": "application/json"
    }

    # クエリパラメータ設定
    params = {
        "query": query,         # 検索ワード
        "max_results": 10,      # 取得件数（最大100）
        "tweet.fields": "created_at,author_id,text"  # 必要なデータを指定
    }

    # APIリクエスト
    response = requests.get(url, headers=headers, params=params)

    # レスポンスの確認
    if response.status_code == 200:
        tweets = response.json()
#        outputLog(f"tweets={tweets}")

        for tweet in tweets.get("data", []):
#            print(f"{tweet['created_at']} - {tweet['text']}\n")
            outputLog(f"検索結果：{tweet['text']}")
        return True , tweets
    else:
        print(f"Error: {response.status_code}, {response.text}")    

    return response.status_code == 200, response_str


def proc_bookmark_v2(credentials, tweet_id):
    """
    指定されたツイートをブックマークする関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: ブックマークする対象のツイートID
    """

#    outputLog("login_id:",credentials['login_id'])

    access_token = credentials['bearer_token']

    user_id , result , contents = get_user_id(credentials ,  credentials['login_id'])
    if result == False:
        return False , contents        


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
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
    else:
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

def post_reply_v2(credentials, tweet_id, username, message):
    """
    OAuth 2.0 を使用して指定されたツイートにリプライを送信する

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: リプライを送る対象のツイートID
    :param username: リプライ先のユーザー名
    :param message: 返信メッセージ
    :return: APIレスポンスのJSONデータ
    """
    access_token = credentials['bearer_token']

    # リプライのエンドポイント
    url = "https://api.twitter.com/2/tweets"

    # リプライの内容を設定
    payload = {
        "text": f"@{username} {message}",  # リプライ内容
        "reply": {
            "in_reply_to_tweet_id": tweet_id  # 返信対象のツイートID
        }
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # APIリクエストを送信
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # レスポンスを解析
    if response.status_code == 201:
        outputLog(f"返信成功: {response.json()}")
        return response.json()
    else:
        outputLog(f"返信失敗: {response.status_code} - {response.text}")
        return None
    

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

    user_id , result , contents = get_user_id(credentials ,  credentials['login_id'])
    if result == False:
        return False , contents        

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
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
    else:
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

def get_replies_to_user(search_account, reply_account, user_id, max_results=10):

    outputLog(f"user_id={user_id}")

    """ 指定ユーザー (user_id) にリプライされたツイートを取得 """
    url = "https://api.twitter.com/2/tweets/search/recent"  # 検索エンドポイントを使用
    
    headers = {
        "Authorization": f"Bearer {search_account['bearer_token']}",
        "Content-Type": "application/json"
    }

    params = {
        "query": f"to:{user_id}",  # 自分宛のリプライを検索
        "max_results": max_results,
        "tweet.fields": "id,created_at,author_id,text,in_reply_to_user_id" ,
        "expansions": "author_id",  # ユーザー情報を取得するために必要
        "user.fields": "username"  # ユーザーの `username` を取得        
    }

    dt = reply_account['check_rep_datetime']
#    if not dt:  # dt が None または 空文字なら現在時刻に置き換え
#        dt = datetime.now(timezone.utc)

    if dt is None:
        outputLog("dt is none")
        dt = datetime.now(timezone.utc)  # dt が空なら現在時刻
    elif isinstance(dt, str):  
        # 文字列なら datetime に変換し、Asia/Tokyo から UTC へ変換
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('Asia/Tokyo'))
        dt = dt.astimezone(timezone.utc)
    elif isinstance(dt, datetime):
        # datetime 型なら UTC に変換
        dt = dt.astimezone(timezone.utc)

    outputLog("datetime")
    outputLog(dt)

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        
        # ユーザー情報を辞書にマッピング
        users = {user["id"]: user["username"] for user in data.get("includes", {}).get("users", [])}

        replies = []
        for tweet in data.get("data", []):
            created_at = convert_tweet_datetime2(tweet["created_at"])  # 日時変換
            outputLog(created_at)
            if created_at > dt:  # 条件を満たす場合のみ追加
#            if True:  # 条件を満たす場合のみ追加
                author_id = tweet.get("author_id", "")
                username = users.get(author_id, "")  # author_id に対応する username を取得
                replies.append({
                    "tweet_id": tweet["id"],
                    "text": tweet["text"],
                    "username": username,
                    "created_at": created_at
                })
#                outputLog(f"reply_text={tweet["text"]}")
                outputLog(f"reply_text={tweet}")
        
        return replies
    else:
        outputLog(f"❌ APIエラー: {response.status_code} - {response.text}")
        return []

def check_replies(search_account , reply_account):

    user_id = reply_account['twitter_user_id']

    if user_id is None or user_id == "":
        user_id , result , contents = get_user_id(reply_account ,  reply_account['login_id'])
        if result == False:
            return False , contents        

        outputLog(f"user_id={user_id}")
        update_account_master_by_twitter_user_id(reply_account['id'] , user_id)

    # リプチェック日時を更新
    update_account_master_by_check_rep_datetime(reply_account['id'])

    """ 指定ユーザーの全ポストに対するリプライをチェック """
    reply_tweets = get_replies_to_user(search_account, reply_account , user_id)


    if not reply_tweets:
        outputLog("新着リプはありませんでした")
        return False, ''
    
    outputLog(f"reply_tweets={reply_tweets}")

    for reply_tweet in reply_tweets:
        outputLog(f"リプライ: {reply_tweet}")  # ここで各リプライを処理

        #ユーザー情報の取得（usernameを使う）
#        tweet_id = reply_tweet.get("id")
#        username = reply_tweet.get("includes", {}).get("users", [{}])[0].get("username", "")
#        text = reply_tweet.get("text", "")
        tweet_id = reply_tweet["tweet_id"]
        username = reply_tweet["username"]
        text = reply_tweet["text"]

        outputLog(tweet_id)
        outputLog(username)
        outputLog(text)

        if not username or not tweet_id:
            outputLog("ツイートIDまたはユーザー名が取得できませんでした")
            return

        outputLog(f"新しいリプライ: @{username}: {text}")  #ログ出力

        #ChatGPT で返信を生成
        reply_message = generate_reply(
            reply_account['GROQ_API_KEY'],
            reply_account['ai_reply_prompt'],
            reply_account['ai_reply_example'],
            text
            )

#        refined_tweet = refine_tweet(
#            reply_account['OPENAI_API_KEY'],
#            reply_message
#            )

        #Twitter に返信
        post_reply_v2(reply_account, tweet_id, username, refined_tweet)


    return True, ''

def get_username_from_tweet_id_v2(credentials,tweet_id):
    url = f"https://api.twitter.com/2/tweets/{tweet_id}?expansions=author_id&user.fields=username"
    headers = {"Authorization": f"Bearer {credentials['bearer_token']}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'includes' in data and 'users' in data['includes']:
            outputLog(f"username = {data['includes']['users'][0]['username']}")
            return data['includes']['users'][0]['username']
    
    return None  # 取得失敗時


def monitor_replies(credentials, user_id, interval=60):
    """ 定期的にリプライを監視 """
    seen_replies = set()

    while True:
        success, new_replies = check_replies(credentials, user_id)

        if success:
            for reply_id in new_replies:
                if reply_id not in seen_replies:
                    outputLog(f"新しいリプライ検出: {reply_id}")
                    seen_replies.add(reply_id)

        time.sleep(interval)  # 指定秒数待機（例: 60秒）
        

def proc_following_v2(credentials, target_user):
    """
    指定されたユーザーをフォローする関数。

    """
    access_token = credentials['bearer_token']
    user_id , result , contents = get_user_id(credentials ,  credentials['login_id'])
    if result == False:
        return False , contents    
    target_user_id , result , contents = get_user_id(credentials , target_user)

    # フォローエンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/following"

    # 投稿するデータ（対象USER IDを指定）
    data = {
        "target_user_id": target_user_id
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    outputLog(f"client_id={credentials['client_id']}")
    outputLog(f"access_token={access_token}")
    outputLog(f"user_id={user_id}")
    outputLog(f"target_user_id={target_user_id}")

    # POSTリクエストを送信
    if False:
#    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }

#        response = requests.post(url, headers=headers, json=data, proxies=proxies)
        response = requests.delete(url, headers=headers, json=data, proxies=proxies)

    else:
        response = requests.post(url, headers=headers, json=data)
#        response = requests.delete(url, headers=headers, json=data)

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code == 200, response_str

def proc_following_v1(credentials, target_user):
    """
    指定されたユーザーをフォローする関数。

    """

    CONSUMER_KEY = credentials['api_key']
    CONSUMER_SECRET = credentials['api_key_secret']
    ACCESS_TOKEN = credentials['access_token']
    ACCESS_SECRET = credentials['access_token_secret']

    import tweepy

    #twitter認証
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    target_user_id , result , contents = get_user_id(credentials , target_user)

    try:
#        api.create_favorite(user_key) #いいね
        api.create_friendship(user_id=target_user_id) #フォロー
    except Exception as e:
        # すでに「いいね」、フォロー済みだとこれが出力。
        print('　【失敗】' + str(e))

#    response_str = json.dumps(response.json())  # json.dumps を使用
#    return response.status_code == 200, response_str

def proc_unfollowing_v2(credentials, target_user):
    """
    指定されたユーザーをアンフォローする関数。
    """

    access_token = credentials['bearer_token']
    user_id , result , contents = get_user_id(credentials ,  credentials['login_id'])
    if result == False:
        return False , contents

    target_user_id , result , contents = get_user_id(credentials , target_user)
    if result == False:
        return False , contents        


    # フォロー解除エンドポイント
    url = f"https://api.twitter.com/2/users/{user_id}/following/{target_user_id}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    outputLog(f"client_id={credentials['client_id']}")

    # プロキシ設定あり
    if credentials['proxy_enable'] and credentials['proxy_url']:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
        response = requests.delete(url, headers=headers, proxies=proxies)
    else:
        response = requests.delete(url, headers=headers)

    response_str = json.dumps(response.json())
    return response.status_code == 200, response_str
