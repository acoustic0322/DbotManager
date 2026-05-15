from curl_cffi import requests
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
import random

from mysql import get_comment_by_id
from mysql import get_account_master_for_update_refresh
from mysql import get_account_master_for_check_full_status
from mysql import update_refresh_token
from mysql import save_tweet_history
from mysql import get_user_id_from_db
from mysql import update_user_id_from_db
from mysql import get_last_tweet_id_from_check_account_list
from mysql import update_last_tweet_id_from_check_account_list
from mysql import update_search_list
from mysql import insert_tweet_history_monomane
from mysql import insert_search_history
from mysql import update_account_master_by_account_name
from mysql import update_account_master_by_twitter_user_id
from mysql import update_account_master_by_check_rep_datetime
from mysql import get_trend_list_keyword
from mysql import get_check_tweet_account_list_by_tweet_id
from mysql import update_account_master_by_check_full_status


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
from chatgpt_tweet import generate_trend_tweet

from search_chat import get_tweet_text_from_yahoo_trend
from search_chat import get_tweet_text_from_yahoo_btc
from search_chat import get_tweet_text_from_yahoo_pair  # レート取得できないため、未対応
from search_chat import get_tweet_text_from_yahoo_gold  # レート取得できないため、未対応

# 2025.10.15 追加
from prompt import PROMPT1
from prompt import past_tweets_1
from prompt import TREND_PROMPT

from check_full_status .check_full_status import check_full_status


# --- 2026年最新UAリスト (curl_cffi 0.14.0の指紋に合わせる) ---
# =============================================================================
# 2026年最新版：最強擬装ロジック (curl_cffi 0.14.0 + 100パターン超分散)
# =============================================================================

# --- iOS Safari (iPhone/iPad) 統合リスト ---
IOS_SAFARI_UAS = [
    # iOS 18系 (最新)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    # iOS 17系 (主力)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    # iOS 16/15系 (iPhone 8/X/11)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7.10 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.8.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7_9 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7.9 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
    # iOS 14系以下 (超古い・iPhone 7/6s)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.8 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.8 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 12_5_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.5 Mobile/15E148 Safari/604.1"
]

# --- Android Chrome 統合リスト ---
ANDROID_CHROME_UAS = [
    # Android 15/14 (Pixel 9, Galaxy S24)
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 8a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SH-51E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SO-51E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    # Android 13/12 (Xperia, Galaxy S21, AQUOS sense7)
    "Mozilla/5.0 (Linux; Android 13; SO-52D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SO-53C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SCG13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Android 11/10 (Galaxy S10, Xperia 5, AQUOS sense3)
    "Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SH-41A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SO-01M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SH-02M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    # Android 9/8以下 (超古い名機 Galaxy S9, S8)
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; L-01L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Mobile Safari/537.36",
    # 格安スマホ・中華系 (OPPO, Xiaomi)
    "Mozilla/5.0 (Linux; Android 14; CPH2523) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; 23127PN0CC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
]

# --- Desktop リスト ---
DESKTOP_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
]

def get_action_config(credentials):
    """指紋(target)とUAを完全に一致させ、アカウントごとに固定する"""
    import random
    account_id = int(credentials.get('id', 0))
    mod = account_id % 5
    
    # 1. 指紋の決定
    if mod in [0, 4]: target = "safari_ios"
    elif mod == 1:    target = "chrome_android"
    elif mod == 2:    target = "safari"
    else:             target = "chrome"
    
    # 2. UAの決定 (アカウントごとに固定)
    random.seed(account_id)
    if "safari_ios" in target:
        ua = random.choice(IOS_SAFARI_UAS)
    elif "chrome_android" in target:
        ua = random.choice(ANDROID_CHROME_UAS)
    else:
        ua = random.choice(DESKTOP_UAS)
    random.seed() 
    
    headers = {
        "Authorization": f"Bearer {credentials['bearer_token']}",
        "Content-Type": "application/json",
        "User-Agent": ua,
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "DNT": "1"
    }
    return target, headers

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

   

def get_user_id(credentials, username):
    """ユーザーID取得（擬装通信版）"""
    # 認証用の一時的な設定取得
    target, headers = get_action_config(credentials)

    url = f"https://api.twitter.com/2/users/by/username/{username}"
    
    proxies = {"http": credentials['proxy_url'], "https": credentials['proxy_url']} if credentials.get('proxy_enable') else None

    # impersonateを適用してGETリクエスト
#    response = requests.get(url, headers=headers, proxies=proxies, impersonate=target)
    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            impersonate=target,
            timeout=(5, 10)
        )
    except requests.exceptions.Timeout:
        outputLog("get_user_id:timeout")
        return None, False, "timeout"
    except requests.exceptions.RequestException as e:
        outputLog("get_user_id:exception")
        return None, False, str(e)
    if response.status_code == 200:
        user_data = response.json()
        if "data" not in user_data:
            return None, False, "User not found"
        return user_data["data"]["id"], True, None
    else:
        return None, False, response.text

def check_access_token(credentials):
    bearer_token = credentials['bearer_token']
    refresh_token = credentials['refresh_token']

    # 最新のターゲット取得
    target, _ = get_action_config(credentials)
    status_code , contents = check_access_token_validity(credentials['bearer_token'], target)

    if status_code == 401:
        bearer_token , refresh_token = refresh_access_token(credentials,0)

    return bearer_token , refresh_token

def proc_update_refresh_token():
    outputLog("proc_update_refresh_token")

    # 通常,react1~3をループ
    for i in range(4):

#        if i == 0:
#            continue

        outputLog(f"proc_update_refresh_token:i={i}")

        credentials_list = get_account_master_for_update_refresh(i)
        outputLog(f"credentials_list={credentials_list}")
    
        for credentials in credentials_list:
            # 新しいトークンを取得
            result, access_token, refresh_token = refresh_access_token(credentials,i)

            # 【重要】取得に成功した場合は、メモリ上の credentials も最新にする
            # これをしないと、この後のループ処理で古いトークンを使ってエラーになります
            if result:
                credentials['bearer_token'] = access_token
                credentials['refresh_token'] = refresh_token
                outputLog(f"ID:{credentials['id']} のトークンをメモリ上でも更新しました。")

            # 最新のトークン情報で履歴を保存
            save_tweet_history(
                credentials['id'], 
                '', 
                'check_refresh', 
                '', 
                result, 
                f"refresh:{refresh_token} access:{access_token}",
                i
            )

def proc_update_check_full_status():
    outputLog("proc_update_check_full_status")

    credentials_list = get_account_master_for_check_full_status()
#    outputLog(f"credentials_list={credentials_list}")
    
    for credentials in credentials_list:
        outputLog(f"id:{credentials.get('id')}")

        # アカウント名未取得の場合は取得してからフォロワー取得
        account_name = credentials.get('account_name')

        if not account_name:
            account_name, user_id, success, error = get_my_username(credentials)

            if not success or not account_name:
                outputLog(f"アカウント名取得失敗: {error}")
                update_account_master_by_check_full_status(credentials.get('id'),0,0,'',False)
                continue

        reach , follow_count , followers_count , check_full_status_enable = check_full_status(
            credentials.get('id'),
            account_name
                )         

        update_account_master_by_check_full_status(credentials.get('id'),follow_count,followers_count,reach,check_full_status_enable)



def refresh_access_token(credentials,num):
    try:

        client_id = credentials['client_id']
        client_secret = credentials.get('client_secret')
        refresh_token = credentials['refresh_token']

        outputLog(f"id={credentials['id']} リフレッシュ開始")
        url = "https://api.twitter.com/2/oauth2/token"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # 送信データの基本セット
        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        # 【修正の肝】
        # client_secretがある場合：Authorizationヘッダーのみを使い、ボディにはIDを入れない
        # client_secretがない場合：ヘッダーは使わず、ボディにclient_idを入れる
        if client_secret and client_secret.strip():
            client_credentials = f"{client_id}:{client_secret}"
            encoded_credentials = base64.b64encode(client_credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_credentials}"
        else:
            data["client_id"] = client_id

        # 送信（指紋はデスクトップに固定）
        response = requests.post(url, headers=headers, data=data, impersonate="chrome110")

        outputLog(f"ID:{credentials['id']} response={response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

            update_refresh_token(credentials['id'], access_token, refresh_token, num)
            credentials['refresh_token'] = refresh_token
            credentials['bearer_token'] = access_token

            return True, access_token, refresh_token
        else:
            outputLog(f"リフレッシュ失敗: {response.status_code}, {response.text}")
            return False, None, None

    except Exception as e:
        outputLog(f"エラー: {e}")
        return False, None, None


def check_access_token_validity(access_token, impersonate_target="chrome110"):
    url = "https://api.twitter.com/2/users/me"  # ユーザー情報を取得
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # リクエストを送信してアクセストークンの有効性を確認
    response = requests.get(url, headers=headers, impersonate=impersonate_target)

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

def proc_get_comment_v2(credentials ,comment_id, reply_to_tweet_id , ai_enable):

    outputLog("proc_get_comment_v2 Start")
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
    result = True

    # リプライモード
    if reply_to_tweet_id != "":
        # 2025.09.02 AIの判定はpython側にシフトする
        if ai_reply_enable == 0 or ai_mode == 0 or ai_enable == False:
            outputLog("固定コメント")
            comment = get_comment_by_id(comment_id)
        else:
            outputLog("AIコメント")
            ai_flag = True

            # reply_to_tweet_id からツイート内容を取得
            target_check_tweet_account_list = get_check_tweet_account_list_by_tweet_id(reply_to_tweet_id)
            tweet_text = target_check_tweet_account_list['tweet_text']

            # 裏垢女子モード
            if ai_mode == 1:   
                outputLog(f"裏垢女子")           
                prompt = credentials['ai_uraaka_prompt_rep']
                past_reply = credentials['ai_uraaka_past_rep']

                if not credentials['ai_uraaka_prompt_rep']:
                    outputLog("ai_uraaka_prompt_repが未設定です")
                    return False , "ai_uraaka_prompt_repが未設定です"

                if not credentials['ai_uraaka_past_rep']:
                    outputLog("ai_uraaka_past_repが未設定です")
                    return False , "ai_uraaka_past_repが未設定です"

            else:
                outputLog(f"裏垢女子以外")           
                prompt = credentials['ai_free_prompt_rep']
                past_reply = credentials['ai_free_past_rep']

                if not credentials['ai_free_prompt_rep']:
                    outputLog("ai_free_prompt_repが未設定です")
                    return False , "ai_free_prompt_repが未設定です"

                if not credentials['ai_free_past_rep']:
                    outputLog("ai_free_past_repが未設定です")
                    return False , "ai_free_past_repが未設定です"

            if not credentials['OPENAI_API_KEY']:
                outputLog("OPENAI_API_KEYが未設定です")
                return False , "OPENAI_API_KEYが未設定です"

            outputLog(f"prompt:{prompt}")           
            outputLog(f"past_reply:{past_reply}")           
            outputLog(f"ツイート文:{tweet_text}")           

            result , comment = generate_reply(credentials['OPENAI_API_KEY'],prompt,past_reply,tweet_text)  #コメント内容
#            result , comment = generate_reply(credentials['OPENAI_API_KEY'],credentials['ai_reply_prompt'],credentials['ai_reply_example'],tweet_text)  #コメント内容

            # 裏垢女子モード時は文章を整形
#            if ai_mode == 2:
#                outputLog("裏垢女子")
#                comment = refine_tweet(credentials['OPENAI_API_KEY'],comment)

            outputLog(f"リプライコメント:{comment}")     

    # ポストモード
    else:

        if ai_post_enable == 0 or ai_mode == 0 or ai_enable == False:
            outputLog("固定コメント")
            if comment_id != 0:
                comment = get_comment_by_id(comment_id)
            else:
                outputLog("固定コメントがありません(comment_id=0です)")
                return False , "固定コメントがありません"
        else:

            # 裏垢女子モード
#            if ai_mode == 1 or ai_mode == 2:
            if ai_mode == 1:
                ai_flag = True
                outputLog("AIコメント")

                #プロンプト、past_tweetを固定にするためとりあえずコメントアウト
                # ai_post_promptが未設定ならFalseを返す
#                if not credentials.get('ai_post_prompt'):
#                    outputLog("ai_post_promptが未設定のため中止")
#                    return False, "ai_post_prompt未設定"                
                # ai_post_exampleが未設定ならFalseを返す
#                if not credentials.get('ai_post_example'):
#                    outputLog("ai_post_exampleが未設定のため中止")
#                    return False, "ai_post_example未設定"                


                outputLog("裏垢女子プロンプト：")
                outputLog(credentials['ai_uraaka_prompt'])
                outputLog("裏垢女子PastTweet：")
                outputLog(credentials['ai_uraaka_past_tweet'])

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False , "OPENAI_API_KEYが未設定です"

                if not credentials['ai_uraaka_prompt']:
                    outputLog("ai_uraaka_promptが未設定です")
                    return False , "ai_uraaka_promptが未設定です"

                if not credentials['ai_uraaka_past_tweet']:
                    outputLog("ai_uraaka_past_tweetが未設定です")
                    return False , "ai_uraaka_past_tweetが未設定です"


#                comment = generate_tweet(credentials['GROQ_API_KEY'],credentials['ai_post_prompt'],credentials['ai_post_example'])
#                result , comment = generate_tweet(credentials['GROQ_API_KEY'],credentials['ai_uraaka_prompt'],credentials['ai_uraaka_past_tweet'])
                result , comment = generate_tweet(credentials['OPENAI_API_KEY'],credentials['ai_uraaka_prompt'],credentials['ai_uraaka_past_tweet'])

#                # 裏垢女子モード時は文章を整形
#                if ai_mode == 2:
#                    outputLog("裏垢女子")
#                    comment = refine_tweet(credentials['OPENAI_API_KEY'],comment)

            # yahooトレンドモード
            elif ai_mode == 2:
                outputLog("yahooトレンドプロンプト：")
                outputLog(credentials['ai_trend_prompt_yahoo'])

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False , "OPENAI_API_KEYが未設定です"

                if not credentials['ai_trend_prompt_yahoo']:
                    outputLog("ai_trend_prompt_yahooが未設定です")
                    return False , "ai_trend_prompt_yahooが未設定です"

                result , comment = get_tweet_text_from_yahoo_trend(credentials['OPENAI_API_KEY'],credentials['ai_trend_prompt_yahoo'])
            # BTC為替レートツイートモード
            elif ai_mode == 3:
                outputLog("BTC為替プロンプト：")
                outputLog(credentials['ai_btc_prompt'])

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False , "OPENAI_API_KEYが未設定です"
                if not credentials['ai_btc_prompt']:
                    outputLog("ai_btc_promptが未設定です")
                    return False , "ai_btc_promptが未設定です"

                result , comment = get_tweet_text_from_yahoo_btc(credentials['OPENAI_API_KEY'],credentials['ai_btc_prompt'])
            # GOLD為替レートツイートモード(未対応)
            elif ai_mode == 4:
                outputLog("GOLD為替")
                prompt = f"""
                以下の情報をもとに、金価格に関するX（旧Twitter）投稿文を1つ生成してください。
                ・リアルタイムの価格を含める
                ・140文字以内
                ・自然でカジュアルな日本語
                ・トレーダーや一般人が興味を持つように
                
                金価格情報: 「{gold_info}」
                """

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False , "OPENAI_API_KEYが未設定です"
                    
                result , comment = get_tweet_text_from_yahoo_gold(credentials['OPENAI_API_KEY'],prompt)
            # 他通貨為替レートツイートモード(未対応)
            elif ai_mode == 5:
                outputLog("他為替")
                # --- プロンプト生成とGPT呼び出し ---
                prompt = f"""
                    以下の情報を元に、X（旧Twitter）に投稿するような自然で短いツイートを日本語で1つ作成してください。
                    今のリアルタイムでの値段を含めてお願いします。
                    140文字以内で、カジュアルに。
                    為替情報: 「{rate_info}」
                    """                

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False , "OPENAI_API_KEYが未設定です"

                result , comment = get_tweet_text_from_yahoo_pair(credentials['OPENAI_API_KEY'],prompt)

            # 自由モード
            elif ai_mode == 9:
                outputLog("自由モード")
                if not credentials['GROQ_API_KEY']:
                    outputLog("GROQ_API_KEYが未設定です")
                    return False , "GROQ_API_KEYが未設定です"

                if not credentials['ai_free_prompt']:
                    outputLog("ai_uraaka_promptが未設定です")
                    return False , "ai_uraaka_promptが未設定です"

                if not credentials['ai_uraaka_past_tweet']:
                    outputLog("ai_uraaka_past_tweetが未設定です")
                    return False , "ai_uraaka_past_tweetが未設定です"

                # TBD ai_uraaka_past_tweet は使っちゃダメ
                result , comment = generate_tweet(credentials['GROQ_API_KEY'],credentials['ai_free_prompt'],credentials['ai_uraaka_past_tweet'])

            else: # Xトレンド
                kw1 , kw2 = get_trend_list_keyword()
                outputLog(f"kw1={kw1}")
                outputLog(f"kw2={kw2}")

#                trend_prompt = TREND_PROMPT
#                trend_prompt = credentials.get('ai_trend_prompt')
                template1 = credentials['ai_trend_prompt_x']

                # ai_trend_promptが未設定ならFalseを返す
                if not template1:
                    outputLog("ai_trend_prompt_xが未設定のため中止")
                    return False, "ai_trend_prompt_x未設定"                

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False , "OPENAI_API_KEYが未設定です"

                template2 = """
                    #最新トレンド
                    - [{keyword1}],[{keyword2}]
                    """                
                # 結合
                full_template = template1 + "\n" + template2                    


                # 置き換え実行
                prompt_text = full_template.format(keyword1=kw1, keyword2=kw2)

                outputLog("Xトレンドプロンプト：")
                outputLog(prompt_text)

                result , comment = generate_trend_tweet(credentials['OPENAI_API_KEY'],prompt_text)


    outputLog(f"comment={comment}")

    if result == False:
        outputLog("コメント取得が出来ませんでした")
        return False , "コメント取得が出来ませんでした"

    # コメントが取得できなかった場合、処理を終了
    if comment is None:
        outputLog("comment is None")
        return False , "comment is None"

    return True , comment

def proc_post_v2(credentials, comment, reply_to_tweet_id=None):
    """
    新規ツイートまたはリプライを投稿する関数。
    """
    target, headers = get_action_config(credentials)
    # 投稿は最も重いアクションなので長めに待機
    time.sleep(random.uniform(3.0, 7.0))

    url = "https://api.twitter.com/2/tweets"
    data = {"text": comment}
    
    # リプライの場合の設定
    if reply_to_tweet_id:
        data["reply"] = {"in_reply_to_tweet_id": str(reply_to_tweet_id)}

    proxies = None
    if credentials.get('proxy_enable') == True and credentials.get('proxy_url') is not None:
        p_url = credentials['proxy_url']
        proxies = {"http": p_url, "https": p_url}

    try:
        response = requests.post(
            url, headers=headers, json=data, proxies=proxies, impersonate=target, timeout=20
        )
        return response.status_code in (200, 201), json.dumps(response.json())
    except Exception as e:
        outputLog(f"proc_post_v2 通信エラー: {str(e)}")
        return False, str(e)

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
        response = requests.post(url, headers=headers, json=data, proxies=proxies, impersonate=get_impersonate_target(credentials))
    else:
        response = requests.post(url, headers=headers, json=data, impersonate=get_impersonate_target(credentials))

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



def get_action_config(credentials):
    """指紋(target)とUAを完全に一致させ、アカウントごとに固定する"""
    import random
    account_id = int(credentials.get('id', 0))
    mod = account_id % 5
    
    # 1. 指紋の決定
    if mod in [0, 4]: target = "safari_ios"
    elif mod == 1:    target = "chrome_android"
    elif mod == 2:    target = "safari"
    else:             target = "chrome"
    
    # 2. UAの決定 (アカウントごとに固定)
    random.seed(account_id)
    if "safari_ios" in target:
        ua = random.choice(IOS_SAFARI_UAS)
    elif "chrome_android" in target:
        ua = random.choice(ANDROID_CHROME_UAS)
    else:
        ua = random.choice(DESKTOP_UAS)
    random.seed() 
    
    headers = {
        "Authorization": f"Bearer {credentials['bearer_token']}",
        "Content-Type": "application/json",
        "User-Agent": ua,
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "DNT": "1"
    }
    return target, headers

def proc_like_v2(credentials, tweet_id):
    """
    指定されたツイートに「いいね」を付ける関数。
    （curl_cffi 0.14.0 + プロキシ修正済 + モバイル擬装統合版）
    """
    # 1. 指紋とUAをセットで取得
    target, headers = get_action_config(credentials)
    
    # 2. 人間らしいランダム遅延
    time.sleep(random.uniform(0.5, 1.5))

    # ユーザーIDの取得
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    
    if result == False:
        # ID取得に失敗（凍結・401エラーなど）した場合も、ここで履歴を保存する！
        # これを入れないと PHP管理画面にエラーが飛びません
        save_tweet_history(credentials['id'], '', 'like', str(tweet_id), False, contents)
        return False, contents

    outputLog(f"user_id={user_id} (target={target})")

    # 「いいね」エンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/likes"

    # 3. 投稿データ (必ず文字列に変換)
    data = {
        "tweet_id": str(tweet_id)
    }

    # 4. プロキシ設定 (http/https両方に対応)
    proxies = None
    if credentials.get('proxy_enable') == True and credentials.get('proxy_url') is not None:
        p_url = credentials['proxy_url']
        proxies = {
            "http": p_url,
            "https": p_url
        }

    # 5. curl_cffiによるPOST送信
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            proxies=proxies, 
            impersonate=target,
            timeout=15
        )
        
        # 成功判定とJSON文字列の返却
        response_str = json.dumps(response.json())
        result = response.status_code == 200
        # エラーログ保存
        save_tweet_history(credentials['id'], '', 'like', '', result, response_str)
        
        return response.status_code == 200, response_str

        
        
    except Exception as e:
        outputLog(f"proc_like_v2 通信エラー: {str(e)}")
        return False, str(e)

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
    response = requests.get(url, headers=headers, params=params, impersonate=get_impersonate_target(credentials))

    # レスポンスの確認
    if response.status_code == 200:
        tweets = response.json()
#        outputLog(f"tweets={tweets}")

        for tweet in tweets.get("data", []):
#            print(f"{tweet['created_at']} - {tweet['text']}\n")
            outputLog(f"検索結果：{tweet['text']}")
        return True , tweets
    else:
        outputLog(f"Error: {response.status_code}, {response.text}")    

    return response.status_code == 200, response_str


def proc_bookmark_v2(credentials, tweet_id):
    """
    指定されたツイートをブックマークする関数。
    """
    target, headers = get_action_config(credentials)
    time.sleep(random.uniform(0.5, 1.5))

    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"
    data = {"tweet_id": str(tweet_id)}

    proxies = None
    if credentials.get('proxy_enable') == True and credentials.get('proxy_url') is not None:
        p_url = credentials['proxy_url']
        proxies = {"http": p_url, "https": p_url}

    try:
        response = requests.post(
            url, headers=headers, json=data, proxies=proxies, impersonate=target, timeout=15
        )
        return response.status_code == 200, json.dumps(response.json())
    except Exception as e:
        outputLog(f"proc_bookmark_v2 通信エラー: {str(e)}")
        return False, str(e)
    

def proc_repost_v2(credentials, tweet_id):
    """
    リポスト実行（モバイル擬装 + プロキシ修正版）
    """
    # 1. 100パターン超のリストからターゲットとヘッダーを取得
    target, headers = get_action_config(credentials)
    
    # 2. リポストは重要アクションなので慎重に待機
    time.sleep(random.uniform(2.0, 5.0))

    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False: return False, contents

    url = f"https://api.twitter.com/2/users/{user_id}/retweets"
    data = {"tweet_id": str(tweet_id)}

    # 3. プロキシ設定の確実な記述（http/httpsの両方を指定）
    proxies = None
    if credentials.get('proxy_enable') and credentials.get('proxy_url'):
        p_url = credentials['proxy_url']
        proxies = {
            "http": p_url,
            "https": p_url
        }

    # 4. curl_cffi で擬装して送信
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            proxies=proxies, 
            impersonate=target,
            timeout=15
        )
        # 成功時は 200 または 201 が返ります
        return response.status_code in (200, 201), json.dumps(response.json())
    except Exception as e:
        outputLog(f"Repost Error: {str(e)}")
        return False, str(e)
    
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

    # ターゲットのみ取得（ヘッダーは別途構築済みのため）
    target, _ = get_action_config(search_account)
    response = requests.get(url, headers=headers, params=params, impersonate=target)

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

    target, _ = get_action_config(credentials)
    response = requests.get(url, headers=headers, impersonate=target)

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
    （curl_cffi 0.14.0 + 100パターン擬装 + プロキシ修正版）
    """
    # 1. 100パターンのリストからターゲットとヘッダーを取得 (共通関数へ外出し)
    target_fingerprint, headers = get_action_config(credentials)
    
    # 2. 人間らしいランダム待機
    time.sleep(random.uniform(1.0, 2.5))

    # 自分のユーザーIDを取得
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    # フォロー対象のユーザーIDを取得
    target_user_id, result, contents = get_user_id(credentials, target_user)
    if result == False:
        return False, contents

    # ログ出力（デバッグ用）
    outputLog(f"FOLLOW実行: from_user_id={user_id} -> to_user={target_user}({target_user_id})")
    outputLog(f"使用デバイス指紋: {target_fingerprint}")

    # フォローエンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/following"

    # 投稿するデータ（対象USER IDを指定）
    data = {
        "target_user_id": str(target_user_id) # IDは文字列化
    }

    # 3. プロキシ設定の確実な記述（http/httpsの両方を指定）
    proxies = None
    if credentials.get('proxy_enable') == True and credentials.get('proxy_url') is not None:
        p_url = credentials['proxy_url']
        outputLog(f"使用プロキシ: {p_url}")
        proxies = {
            "http": p_url,
            "https": p_url
        }

    # 4. curl_cffi によるPOST送信
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            proxies=proxies, 
            impersonate=target_fingerprint,
            timeout=30
        )
        
        # 成功時は 200 OK で {"data": {"following": true, ...}} が返る
        response_str = json.dumps(response.json())
        return response.status_code == 200, response_str

    except Exception as e:
        outputLog(f"proc_following_v2 通信エラー: {str(e)}")
        return False, str(e)

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
        outputLog('　【失敗】' + str(e))

#    response_str = json.dumps(response.json())  # json.dumps を使用
#    return response.status_code == 200, response_str

def proc_unfollowing_v2(credentials, target_user):
    """
    指定されたユーザーをアンフォロー（フォロー解除）する関数。
    （curl_cffi 0.14.0 + 100パターン擬装 + プロキシ修正版）
    """
    # 1. 最新の指紋(target)とヘッダー(UA)をセットで取得
    target_fingerprint, headers = get_action_config(credentials)
    
    # 2. 人間らしいランダム待機（解除は少し慎重に）
    time.sleep(random.uniform(1.0, 3.0))

    # 自分のユーザーIDを取得
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    # 解除対象のユーザーIDを取得
    target_user_id, result, contents = get_user_id(credentials, target_user)
    if result == False:
        return False, contents

    outputLog(f"UNFOLLOW実行: from={user_id} -> target={target_user}({target_user_id})")
    outputLog(f"client_id={credentials['client_id']}")

    # フォロー解除エンドポイントURL（API v2仕様）
    url = f"https://api.twitter.com/2/users/{user_id}/following/{target_user_id}"

    # 3. プロキシ設定の確実な記述
    proxies = None
    if credentials.get('proxy_enable') == True and credentials.get('proxy_url') is not None:
        p_url = credentials['proxy_url']
        outputLog(f"proxy_url={p_url}")
        proxies = {
            "http": p_url,
            "https": p_url
        }

    # 4. curl_cffi による DELETE 送信 (impersonateを適用)
    try:
        response = requests.delete(
            url, 
            headers=headers, 
            proxies=proxies, 
            impersonate=target_fingerprint,
            timeout=15
        )
        
        # 成功時は 200 OK で {"data": {"following": false}} が返る
        response_str = json.dumps(response.json())
        return response.status_code == 200, response_str

    except Exception as e:
        outputLog(f"proc_unfollowing_v2 通信エラー: {str(e)}")
        return False, str(e)

def proc_refresh_queue():
    from mysql import get_refresh_queue, update_refresh_queue_status, get_account_master, delete_account_error_log
    
    outputLog("proc_refresh_queue start")
    queue_list = get_refresh_queue()
    
    if not queue_list:
        outputLog("キューなし")
        return
    
    for queue in queue_list:
        queue_id = queue['id']
        account_id = queue['account_id']
        
        # 処理中に更新
        update_refresh_queue_status(queue_id, 'processing')
        
        credentials = get_account_master(account_id)
        if not credentials:
            update_refresh_queue_status(queue_id, 'error')
            continue
        
        result, access_token, refresh_token = refresh_access_token(credentials,0)
        
        if result:
            from mysql import get_account_error_log_type
            error_type = get_account_error_log_type(account_id)
            if error_type in ('unauthorized', 'lock'):  # ← lockも追加
                delete_account_error_log(account_id)
            update_refresh_queue_status(queue_id, 'done')
            outputLog(f"ID:{account_id} トークン更新成功")

def get_my_username(credentials):

    if credentials.get('account_name'):
        outputLog(f"アカウント名取得済み:{credentials.get('account_name')}")
        return credentials.get('account_name'), credentials.get('twitter_user_id'), True, None

    """
    BearerTokenから、自分自身のusernameを取得
    """
    url = "https://api.twitter.com/2/users/me?user.fields=username"


#    outputLog(f"credentials={credentials}")
    target, headers = get_action_config(credentials)

    proxies = None
    if credentials.get('proxy_enable') and credentials.get('proxy_url'):
        p_url = credentials['proxy_url']
        proxies = {
            "http": p_url,
            "https": p_url
        }

    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            impersonate=target,
            timeout=15
        )

        outputLog(f"get_my_username status={response.status_code}")

        if response.status_code == 200:
            data = response.json()

            username = data.get("data", {}).get("username")
            user_id = data.get("data", {}).get("id")

            outputLog(f"username={username}")
            outputLog(f"user_id={user_id}")

            update_account_master_by_account_name(credentials.get('id'),username)
            update_account_master_by_twitter_user_id(credentials.get('id'),user_id)

            return username, user_id, True, None

        return None, None, False, response.text

    except Exception as e:
        outputLog(f"get_my_username error:{e}")
        return None, None, False, str(e)