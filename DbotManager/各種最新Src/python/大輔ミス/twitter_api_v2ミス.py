import requests
import json
import time
import sys
import os
import base64
import pymysql
import random
import uuid
from datetime import datetime, timezone

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

import config
from config import convert_tweet_datetime
from config import convert_tweet_datetime2
from config import outputLog

import tweepy

# chatgpt フォルダを Python のパスに追加
sys.path.append(os.path.abspath("chatgpt"))

from chatgpt_reply import generate_reply
from chatgpt_tweet import generate_tweet
from chatgpt_tweet import generate_trend_tweet

from search_chat import get_tweet_text_from_yahoo_trend
from search_chat import get_tweet_text_from_yahoo_btc
from search_chat import get_tweet_text_from_yahoo_pair
from search_chat import get_tweet_text_from_yahoo_gold

from prompt import PROMPT1
from prompt import past_tweets_1
from prompt import TREND_PROMPT


# =============================================================================
# ランダムヘッダー用定数
# =============================================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

ACCEPT_LANGUAGES = [
    "ja,en-US;q=0.9,en;q=0.8",
    "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "ja,en;q=0.9",
    "ja-JP,ja;q=0.9,en;q=0.8",
    "en-US,en;q=0.9,ja;q=0.8",
    "ja,en-US;q=0.7,en;q=0.3",
]

ACCEPT_ENCODINGS = [
    "gzip, deflate, br",
    "gzip, deflate",
    "gzip, deflate, br, zstd",
    "br, gzip, deflate",
]

SEC_CH_UA_LIST = [
    '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
    '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
    '"Chromium";v="120", "Not_A Brand";v="24", "Microsoft Edge";v="120"',
]

SEC_CH_UA_PLATFORM_LIST = [
    '"Windows"',
    '"macOS"',
    '"Linux"',
]


# =============================================================================
# ヘルパー関数
# =============================================================================

def get_random_headers(access_token, content_type="application/json"):
    """
    ランダム化されたヘッダーを生成
    
    :param access_token: Bearer トークン
    :param content_type: Content-Type（デフォルト: application/json）
    :return: ヘッダー辞書
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": content_type,
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept-Encoding": random.choice(ACCEPT_ENCODINGS),
        "Connection": "keep-alive",
    }
    
    # ランダムで追加ヘッダーを付与
    if random.random() > 0.3:
        headers["Cache-Control"] = random.choice(["no-cache", "max-age=0", "no-store"])
    
    if random.random() > 0.5:
        headers["sec-ch-ua"] = random.choice(SEC_CH_UA_LIST)
        headers["sec-ch-ua-platform"] = random.choice(SEC_CH_UA_PLATFORM_LIST)
        headers["sec-ch-ua-mobile"] = "?0"
    
    if random.random() > 0.6:
        headers["X-Request-Id"] = str(uuid.uuid4())
    
    if random.random() > 0.7:
        headers["Pragma"] = "no-cache"
    
    return headers


def get_random_headers_form(access_token):
    """
    フォームデータ用のランダム化されたヘッダーを生成
    """
    return get_random_headers(access_token, content_type="application/x-www-form-urlencoded")


def random_delay(min_sec=0.5, max_sec=2.0):
    """
    自然な動作をシミュレートするためのランダム遅延
    
    :param min_sec: 最小待機秒数
    :param max_sec: 最大待機秒数
    """
    delay = random.uniform(min_sec, max_sec)
    outputLog(f"待機中: {delay:.2f}秒")
    time.sleep(delay)


def get_proxies(credentials):
    """
    認証情報からプロキシ設定を取得
    
    :param credentials: 認証情報辞書
    :return: プロキシ辞書またはNone
    """
    if credentials.get('proxy_enable') and credentials.get('proxy_url'):
        outputLog(f"proxy_url={credentials['proxy_url']}")
        return {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
    return None


def get_tweet_by_id(credentials, tweet_id):
    """
    ツイートIDからツイート情報を取得する
    ※システム側でアカウント毎に1回呼び出す用
    
    :param credentials: 認証情報
    :param tweet_id: 取得するツイートID
    :return: (成功フラグ, ツイートデータ or エラーメッセージ)
    """
    access_token = credentials['bearer_token']
    
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    
    params = {
        "tweet.fields": "id,text,created_at,author_id,public_metrics,conversation_id,lang",
        "expansions": "author_id",
        "user.fields": "id,name,username,profile_image_url,verified"
    }
    
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)
    
    try:
        response = requests.get(url, headers=headers, params=params, proxies=proxies)
        response_data = response.json()
        
        if response.status_code == 200:
            tweet_text = response_data.get('data', {}).get('text', '')[:50]
            outputLog(f"ツイート取得成功: {tweet_id} - {tweet_text}...")
            return True, response_data
        else:
            outputLog(f"ツイート取得エラー: {response.status_code}, {response_data}")
            return False, json.dumps(response_data)
            
    except requests.exceptions.RequestException as e:
        outputLog(f"ツイート取得でリクエストエラー: {e}")
        return False, str(e)
    except Exception as e:
        outputLog(f"ツイート取得で予期しないエラー: {e}")
        return False, str(e)


# =============================================================================
# Tweepy クライアント作成
# =============================================================================

def createClient(credentials):
    try:
        client = tweepy.Client(
            bearer_token=credentials['bearer_token']
        )

        if credentials.get('proxy_enable') == True and credentials.get('proxy_url') is not None:
            outputLog(f"proxy_url={credentials['proxy_url']}")
            client.session.proxies = {"http": credentials['proxy_url'], "https": credentials['proxy_url']}

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


# =============================================================================
# ユーザーID取得
# =============================================================================

def get_user_id(credentials, username):
    access_token = credentials['bearer_token']

    headers = get_random_headers(access_token)
    url = f"https://api.twitter.com/2/users/by/username/{username}"

    outputLog(f"credentials['proxy_enable']  {credentials.get('proxy_enable')}")
    outputLog(f"credentials['proxy_url']  {credentials.get('proxy_url')}")

    proxies = get_proxies(credentials)
    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code == 200:
        user_data = response.json()

        if "data" not in user_data:
            error_msg = user_data.get("errors", [{"detail": "ユーザーが見つかりません。"}])[0].get("detail")
            outputLog(f"get_user_idエラー: {error_msg}")
            return None, False, error_msg

        user_id = user_data["data"]["id"]
        outputLog(f"get_user_id {username}のユーザーID: {user_id}")
        return user_id, True, None
    else:
        outputLog(f"get_user_idエラー: {response.status_code}, {response.text}")
        return None, False, response.text


# =============================================================================
# アクセストークン関連
# =============================================================================

def check_access_token(credentials):
    bearer_token = credentials['bearer_token']
    refresh_token = credentials['refresh_token']

    status_code, contents = check_access_token_validity(credentials['bearer_token'])

    if status_code == 401:
        bearer_token, refresh_token = refresh_access_token(credentials)

    return bearer_token, refresh_token


def proc_update_refresh_token():
    outputLog("proc_update_refresh_token")
    credentials_list = get_account_master_for_update_refresh()
    outputLog(f"credentials_list={credentials_list}")
    for credentials in credentials_list:
        result, access_token, refresh_token = refresh_access_token(credentials)
        save_tweet_history(credentials['id'], '', 'check_refresh', '', result, f"refresh:{refresh_token} access:{access_token}")


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

        client_credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}",
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        }

        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, headers=headers, data=data)
        outputLog(f"response={response}")

        if response.status_code == 200:
            response_data = response.json()

            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")

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
    url = "https://api.twitter.com/2/users/me"
    headers = get_random_headers(access_token)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        outputLog("check_access_token_validity アクセストークンは有効です。")
        return response.status_code, ""
    elif response.status_code == 401:
        outputLog("check_access_token_validity アクセストークンが無効です。再認証が必要です。")
        return response.status_code, json.dumps(response.json())
    else:
        outputLog(f"check_access_token_validity エラー: {response.status_code}")
        outputLog(response.json())
        return response.status_code, json.dumps(response.json())


# =============================================================================
# コメント取得（AI連携）
# =============================================================================

def proc_get_comment_v2(credentials, comment_id, reply_to_tweet_id, ai_enable):
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
        if ai_reply_enable == 0 or ai_mode == 0 or ai_enable == False:
            outputLog("固定コメント")
            comment = get_comment_by_id(comment_id)
        else:
            outputLog("AIコメント")
            ai_flag = True

            target_check_tweet_account_list = get_check_tweet_account_list_by_tweet_id(reply_to_tweet_id)
            tweet_text = target_check_tweet_account_list['tweet_text']

            if ai_mode == 1:
                outputLog(f"裏垢女子")
                prompt = credentials['ai_uraaka_prompt_rep']
                past_reply = credentials['ai_uraaka_past_rep']

                if not credentials['ai_uraaka_prompt_rep']:
                    outputLog("ai_uraaka_prompt_repが未設定です")
                    return False, "ai_uraaka_prompt_repが未設定です"

                if not credentials['ai_uraaka_past_rep']:
                    outputLog("ai_uraaka_past_repが未設定です")
                    return False, "ai_uraaka_past_repが未設定です"
            else:
                outputLog(f"裏垢女子以外")
                prompt = credentials['ai_free_prompt_rep']
                past_reply = credentials['ai_free_past_rep']

                if not credentials['ai_free_prompt_rep']:
                    outputLog("ai_free_prompt_repが未設定です")
                    return False, "ai_free_prompt_repが未設定です"

                if not credentials['ai_free_past_rep']:
                    outputLog("ai_free_past_repが未設定です")
                    return False, "ai_free_past_repが未設定です"

            if not credentials['OPENAI_API_KEY']:
                outputLog("OPENAI_API_KEYが未設定です")
                return False, "OPENAI_API_KEYが未設定です"

            outputLog(f"prompt:{prompt}")
            outputLog(f"past_reply:{past_reply}")
            outputLog(f"ツイート文:{tweet_text}")

            result, comment = generate_reply(credentials['OPENAI_API_KEY'], prompt, past_reply, tweet_text)
            outputLog(f"リプライコメント:{comment}")

    # ポストモード
    else:
        if ai_post_enable == 0 or ai_mode == 0 or ai_enable == False:
            outputLog("固定コメント")
            if comment_id != 0:
                comment = get_comment_by_id(comment_id)
            else:
                outputLog("固定コメントがありません(comment_id=0です)")
                return False, "固定コメントがありません"
        else:
            # 裏垢女子モード
            if ai_mode == 1:
                ai_flag = True
                outputLog("AIコメント")

                outputLog("裏垢女子プロンプト：")
                outputLog(credentials['ai_uraaka_prompt'])
                outputLog("裏垢女子PastTweet：")
                outputLog(credentials['ai_uraaka_past_tweet'])

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False, "OPENAI_API_KEYが未設定です"

                if not credentials['ai_uraaka_prompt']:
                    outputLog("ai_uraaka_promptが未設定です")
                    return False, "ai_uraaka_promptが未設定です"

                if not credentials['ai_uraaka_past_tweet']:
                    outputLog("ai_uraaka_past_tweetが未設定です")
                    return False, "ai_uraaka_past_tweetが未設定です"

                result, comment = generate_tweet(credentials['OPENAI_API_KEY'], credentials['ai_uraaka_prompt'], credentials['ai_uraaka_past_tweet'])

            # yahooトレンドモード
            elif ai_mode == 2:
                outputLog("yahooトレンドプロンプト：")
                outputLog(credentials['ai_trend_prompt_yahoo'])

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False, "OPENAI_API_KEYが未設定です"

                if not credentials['ai_trend_prompt_yahoo']:
                    outputLog("ai_trend_prompt_yahooが未設定です")
                    return False, "ai_trend_prompt_yahooが未設定です"

                result, comment = get_tweet_text_from_yahoo_trend(credentials['OPENAI_API_KEY'], credentials['ai_trend_prompt_yahoo'])

            # BTC為替レートツイートモード
            elif ai_mode == 3:
                outputLog("BTC為替プロンプト：")
                outputLog(credentials['ai_btc_prompt'])

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False, "OPENAI_API_KEYが未設定です"
                if not credentials['ai_btc_prompt']:
                    outputLog("ai_btc_promptが未設定です")
                    return False, "ai_btc_promptが未設定です"

                result, comment = get_tweet_text_from_yahoo_btc(credentials['OPENAI_API_KEY'], credentials['ai_btc_prompt'])

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
                    return False, "OPENAI_API_KEYが未設定です"

                result, comment = get_tweet_text_from_yahoo_gold(credentials['OPENAI_API_KEY'], prompt)

            # 他通貨為替レートツイートモード(未対応)
            elif ai_mode == 5:
                outputLog("他為替")
                prompt = f"""
                    以下の情報を元に、X（旧Twitter）に投稿するような自然で短いツイートを日本語で1つ作成してください。
                    今のリアルタイムでの値段を含めてお願いします。
                    140文字以内で、カジュアルに。
                    為替情報: 「{rate_info}」
                    """

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False, "OPENAI_API_KEYが未設定です"

                result, comment = get_tweet_text_from_yahoo_pair(credentials['OPENAI_API_KEY'], prompt)

            # 自由モード
            elif ai_mode == 9:
                outputLog("自由モード")

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False, "OPENAI_API_KEYが未設定です"

                if not credentials['ai_free_prompt']:
                    outputLog("ai_uraaka_promptが未設定です")
                    return False, "ai_uraaka_promptが未設定です"

                if not credentials['ai_uraaka_past_tweet']:
                    outputLog("ai_uraaka_past_tweetが未設定です")
                    return False, "ai_uraaka_past_tweetが未設定です"

                result, comment = generate_tweet(credentials['OPENAI_API_KEY'], credentials['ai_free_prompt'], credentials['ai_uraaka_past_tweet'])

            else:  # Xトレンド
                kw1, kw2 = get_trend_list_keyword()
                outputLog(f"kw1={kw1}")
                outputLog(f"kw2={kw2}")

                template1 = credentials['ai_trend_prompt_x']

                if not template1:
                    outputLog("ai_trend_prompt_xが未設定のため中止")
                    return False, "ai_trend_prompt_x未設定"

                if not credentials['OPENAI_API_KEY']:
                    outputLog("OPENAI_API_KEYが未設定です")
                    return False, "OPENAI_API_KEYが未設定です"

                template2 = """
                    #最新トレンド
                    - [{keyword1}],[{keyword2}]
                    """
                full_template = template1 + "\n" + template2

                prompt_text = full_template.format(keyword1=kw1, keyword2=kw2)

                outputLog("Xトレンドプロンプト：")
                outputLog(prompt_text)

                result, comment = generate_trend_tweet(credentials['OPENAI_API_KEY'], prompt_text)

    outputLog(f"comment={comment}")

    if result == False:
        outputLog("コメント取得が出来ませんでした")
        return False, "コメント取得が出来ませんでした"

    if comment is None:
        outputLog("comment is None")
        return False, "comment is None"

    return True, comment


# =============================================================================
# ツイート投稿
# =============================================================================

def proc_post_v2(credentials, comment, reply_to_tweet_id, ai_enable):
    """
    ツイート/リプライ投稿関数
    ※リプライの場合、ツイート取得はシステム側で実施済みの前提
    """
    # リプライの場合は遅延を入れる（ツイートを読んでいる風）
    if reply_to_tweet_id:
        random_delay(1.0, 3.0)

    access_token = credentials['bearer_token']
    url = "https://api.twitter.com/2/tweets"

    data = {"text": comment}

    if reply_to_tweet_id:
        data["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}

    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    if config.debug == True:
        outputLog(headers)
        outputLog(data)
        outputLog(comment)

    response = requests.post(url, headers=headers, json=data, proxies=proxies)

    if config.debug == True:
        outputLog(response.json())

    try:
        response_data = response.json()
    except ValueError as e:
        if config.debug == True:
            outputLog(f"JSON パースエラー:{ str(e)}")
            outputLog(f"Raw response text:{response.text}")
        return False, f"JSON パースエラー: {str(e)}"

    response_str = json.dumps(response_data)
    return response.status_code in (200, 201), response_str


def proc_post_v2_monomane(credentials, tweet_text):
    outputLog("proc_post_v2 Start")
    outputLog(f"GROQ_API_KEY={credentials['GROQ_API_KEY']}")
    outputLog(f"OPENAI_API_KEY={credentials['OPENAI_API_KEY']}")

    access_token = credentials['bearer_token']
    url = "https://api.twitter.com/2/tweets"

    data = {"text": tweet_text}
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    response = requests.post(url, headers=headers, json=data, proxies=proxies)

    if config.debug == True:
        outputLog(response.json())

    try:
        response_data = response.json()
    except ValueError as e:
        if config.debug == True:
            outputLog(f"JSON パースエラー:{ str(e)}")
            outputLog(f"Raw response text:{response.text}")
        return False, f"JSON パースエラー: {str(e)}"

    response_str = json.dumps(response_data)
    return response.status_code in (200, 201), response_str


# =============================================================================
# いいね
# =============================================================================

def proc_like_v2(credentials, tweet_id):
    """
    指定されたツイートに「いいね」を付ける関数
    ※ツイート取得はシステム側で実施済みの前提
    """
    # ツイートを読んでいる風の遅延
    random_delay(0.5, 1.5)

    access_token = credentials['bearer_token']
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    outputLog(f"user_id={user_id}")

    url = f"https://api.twitter.com/2/users/{user_id}/likes"
    data = {"tweet_id": tweet_id}
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    outputLog(f"client_id={credentials['client_id']}")

    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response_str = json.dumps(response.json())

    return response.status_code == 200, response_str


# =============================================================================
# ブックマーク
# =============================================================================

def proc_bookmark_v2(credentials, tweet_id):
    """
    指定されたツイートをブックマークする関数
    ※ツイート取得はシステム側で実施済みの前提
    """
    # 遅延（いいね等の後に実行される想定）
    random_delay(0.3, 1.0)

    access_token = credentials['bearer_token']
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"
    data = {"tweet_id": tweet_id}
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response_str = json.dumps(response.json())

    return response.status_code == 200, response_str


# =============================================================================
# リポスト（リツイート）
# =============================================================================

def proc_repost_v2(credentials, tweet_id):
    """
    指定されたツイートIDをリツイートする関数
    ※ツイート取得はシステム側で実施済みの前提
    """
    # ツイートを読んでいる風の遅延
    random_delay(0.5, 2.0)

    access_token = credentials['bearer_token']
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    url = f"https://api.twitter.com/2/users/{user_id}/retweets"
    data = {"tweet_id": tweet_id}
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response_str = json.dumps(response.json())

    return response.status_code in (200, 201), response_str


# =============================================================================
# 検索
# =============================================================================

def proc_search_v2(credentials):
    keywords = ["FX", "為替", "傾向"]
    query = " OR ".join(keywords)

    url = "https://api.twitter.com/2/tweets/search/recent"

    headers = get_random_headers(credentials['bearer_token'])

    params = {
        "query": query,
        "max_results": 10,
        "tweet.fields": "created_at,author_id,text"
    }

    proxies = get_proxies(credentials)
    response = requests.get(url, headers=headers, params=params, proxies=proxies)

    if response.status_code == 200:
        tweets = response.json()
        for tweet in tweets.get("data", []):
            outputLog(f"検索結果：{tweet['text']}")
        return True, tweets
    else:
        outputLog(f"検索エラー: {response.status_code}, {response.text}")

    response_str = json.dumps(response.json())
    return response.status_code == 200, response_str


# =============================================================================
# リプライ関連
# =============================================================================

def post_reply_v2(credentials, tweet_id, username, message):
    """
    OAuth 2.0 を使用して指定されたツイートにリプライを送信する
    ※ツイート取得はシステム側で実施済みの前提
    """
    # ツイートを読んでいる風の遅延
    random_delay(1.0, 3.0)

    access_token = credentials['bearer_token']
    url = "https://api.twitter.com/2/tweets"

    payload = {
        "text": f"@{username} {message}",
        "reply": {"in_reply_to_tweet_id": tweet_id}
    }

    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    response = requests.post(url, headers=headers, json=payload, proxies=proxies)

    if response.status_code == 201:
        outputLog(f"返信成功: {response.json()}")
        return response.json()
    else:
        outputLog(f"返信失敗: {response.status_code} - {response.text}")
        return None


def get_replies_to_user(search_account, reply_account, user_id, max_results=10):
    outputLog(f"user_id={user_id}")

    url = "https://api.twitter.com/2/tweets/search/recent"

    headers = get_random_headers(search_account['bearer_token'])

    params = {
        "query": f"to:{user_id}",
        "max_results": max_results,
        "tweet.fields": "id,created_at,author_id,text,in_reply_to_user_id",
        "expansions": "author_id",
        "user.fields": "username"
    }

    dt = reply_account['check_rep_datetime']

    if dt is None:
        outputLog("dt is none")
        dt = datetime.now(timezone.utc)
    elif isinstance(dt, str):
        import pytz
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone('Asia/Tokyo'))
        dt = dt.astimezone(timezone.utc)
    elif isinstance(dt, datetime):
        dt = dt.astimezone(timezone.utc)

    outputLog("datetime")
    outputLog(dt)

    proxies = get_proxies(search_account)
    response = requests.get(url, headers=headers, params=params, proxies=proxies)

    if response.status_code == 200:
        data = response.json()

        users = {user["id"]: user["username"] for user in data.get("includes", {}).get("users", [])}

        replies = []
        for tweet in data.get("data", []):
            created_at = convert_tweet_datetime2(tweet["created_at"])
            outputLog(created_at)
            if created_at > dt:
                author_id = tweet.get("author_id", "")
                username = users.get(author_id, "")
                replies.append({
                    "tweet_id": tweet["id"],
                    "text": tweet["text"],
                    "username": username,
                    "created_at": created_at
                })
                outputLog(f"reply_text={tweet}")

        return replies
    else:
        outputLog(f"❌ APIエラー: {response.status_code} - {response.text}")
        return []


def check_replies(search_account, reply_account):
    user_id = reply_account['twitter_user_id']

    if user_id is None or user_id == "":
        user_id, result, contents = get_user_id(reply_account, reply_account['login_id'])
        if result == False:
            return False, contents

        outputLog(f"user_id={user_id}")
        update_account_master_by_twitter_user_id(reply_account['id'], user_id)

    update_account_master_by_check_rep_datetime(reply_account['id'])

    reply_tweets = get_replies_to_user(search_account, reply_account, user_id)

    if not reply_tweets:
        outputLog("新着リプはありませんでした")
        return False, ''

    outputLog(f"reply_tweets={reply_tweets}")

    for reply_tweet in reply_tweets:
        outputLog(f"リプライ: {reply_tweet}")

        tweet_id = reply_tweet["tweet_id"]
        username = reply_tweet["username"]
        text = reply_tweet["text"]

        outputLog(tweet_id)
        outputLog(username)
        outputLog(text)

        if not username or not tweet_id:
            outputLog("ツイートIDまたはユーザー名が取得できませんでした")
            return

        outputLog(f"新しいリプライ: @{username}: {text}")

        reply_message = generate_reply(
            reply_account['GROQ_API_KEY'],
            reply_account['ai_reply_prompt'],
            reply_account['ai_reply_example'],
            text
        )

        post_reply_v2(reply_account, tweet_id, username, reply_message)

    return True, ''


def get_username_from_tweet_id_v2(credentials, tweet_id):
    url = f"https://api.twitter.com/2/tweets/{tweet_id}?expansions=author_id&user.fields=username"
    headers = get_random_headers(credentials['bearer_token'])
    proxies = get_proxies(credentials)

    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code == 200:
        data = response.json()
        if 'includes' in data and 'users' in data['includes']:
            outputLog(f"username = {data['includes']['users'][0]['username']}")
            return data['includes']['users'][0]['username']

    return None


def monitor_replies(credentials, user_id, interval=60):
    seen_replies = set()

    while True:
        success, new_replies = check_replies(credentials, user_id)

        if success:
            for reply_id in new_replies:
                if reply_id not in seen_replies:
                    outputLog(f"新しいリプライ検出: {reply_id}")
                    seen_replies.add(reply_id)

        time.sleep(interval)


# =============================================================================
# フォロー/アンフォロー
# =============================================================================

def proc_following_v2(credentials, target_user):
    """
    指定されたユーザーをフォローする関数
    """
    access_token = credentials['bearer_token']
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents
    target_user_id, result, contents = get_user_id(credentials, target_user)
    if result == False:
        return False, contents

    url = f"https://api.twitter.com/2/users/{user_id}/following"
    data = {"target_user_id": target_user_id}
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    outputLog(f"client_id={credentials['client_id']}")
    outputLog(f"access_token={access_token}")
    outputLog(f"user_id={user_id}")
    outputLog(f"target_user_id={target_user_id}")

    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response_str = json.dumps(response.json())

    return response.status_code == 200, response_str


def proc_following_v1(credentials, target_user):
    """
    指定されたユーザーをフォローする関数（v1 API）
    """
    CONSUMER_KEY = credentials['api_key']
    CONSUMER_SECRET = credentials['api_key_secret']
    ACCESS_TOKEN = credentials['access_token']
    ACCESS_SECRET = credentials['access_token_secret']

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    target_user_id, result, contents = get_user_id(credentials, target_user)

    try:
        api.create_friendship(user_id=target_user_id)
    except Exception as e:
        outputLog(f'フォロー失敗: {str(e)}')


def proc_unfollowing_v2(credentials, target_user):
    """
    指定されたユーザーをアンフォローする関数
    """
    access_token = credentials['bearer_token']
    user_id, result, contents = get_user_id(credentials, credentials['login_id'])
    if result == False:
        return False, contents

    target_user_id, result, contents = get_user_id(credentials, target_user)
    if result == False:
        return False, contents

    url = f"https://api.twitter.com/2/users/{user_id}/following/{target_user_id}"
    headers = get_random_headers(access_token)
    proxies = get_proxies(credentials)

    outputLog(f"client_id={credentials['client_id']}")

    response = requests.delete(url, headers=headers, proxies=proxies)
    response_str = json.dumps(response.json())

    return response.status_code == 200, response_str
