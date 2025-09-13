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
from datetime import datetime, timedelta

import tweepy


from mysql import get_comment_by_id
from mysql import get_account_master_for_update_refresh
from mysql import update_refresh_token
from mysql import save_tweet_history
from mysql import get_user_id_from_db
from mysql import update_user_id_from_db
from mysql import get_last_tweet_id_from_check_account_list
from mysql import update_last_tweet_id_from_check_account_list
from mysql import get_account_master
from mysql import insert_tweet_history_monomane
from mysql import getOwnTweetId
from mysql import get_check_tweet_account_list_by_tweet_id

from download_media import download_media
from download_media import get_tweet_media

import config
from config import convert_tweet_datetime

from config import outputLog

import re
from urllib.parse import urlparse, parse_qs
import urllib.parse
import random
import string

def createClient(credentials):
    try:
#        client = tweepy.Client(
#            bearer_token=credentials['bearer_token']
#        )

        client = tweepy.Client(
            consumer_key=credentials['api_key'], 
            consumer_secret=credentials['api_key_secret'], 
            access_token=credentials['access_token'], 
            access_token_secret=credentials['access_token_secret']
            )

        outputLog("Tweepy Client を正常に作成しました")
        outputLog(f"consumer_key={credentials['api_key']}")
        outputLog(f"consumer_secret={credentials['api_key_secret']}")
        outputLog(f"access_token={credentials['access_token']}")
        outputLog(f"access_token_secret={credentials['access_token_secret']}")

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

def proc_post_v10a(credentials ,comment_id, media_type , media_id, reply_to_tweet_id):

    account_id = credentials['id']

    #認証
    client = tweepy.Client(
        consumer_key=credentials['api_key'],
        consumer_secret=credentials['api_key_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret']
    )

    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        client.session.proxies = {"http": credentials['proxy_url'],"https": credentials['proxy_url']}

    # コメントの取得
    comment = get_comment_by_id(comment_id)

    # 認証
    auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])    

    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        api = tweepy.API(auth, proxy=credentials['proxy_url'])
    else:
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

def get_twitter_video_url(tweet_url):
    outputLog(f"test")
    response = requests.get(tweet_url, allow_redirects=True)
    outputLog(f"test")
    soup = BeautifulSoup(response.text, 'html.parser')
    outputLog(f"test")

    for video in soup.find_all("video"):
        for source in video.find_all("source"):
            video_url = source.get("src")
            if video_url:
                outputLog(f"video_url=f{video_url}")
                return video_url
    return None


def download_url(media_type,media_url):
    try:

        response = requests.get(media_url, allow_redirects=True)
        media_url = response.url 
        outputLog(f"media_url={media_url}")

        outputLog(get_twitter_video_url(media_url))

        # ファイル名生成の処理
        try:
#            filename = f"{generate_random_string(10)}.{media_url.split('.')[-1].split('?')[0]}"
            filename = f"C:/work/{generate_random_string(10)}.{media_url.split('.')[-1].split('?')[0]}"
        except Exception as e:
            outputLog(f"Error in filename generation: {e}")
            raise  # 例外を再送出して外側でキャッチ

        # ディレクトリの存在を確認、なければ作成
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        outputLog(f"Downloading from: {media_url}")
        outputLog(f"filename: {filename}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://twitter.com/"
        }

        r = requests.get(media_url, headers=headers, allow_redirects=True)
#        r = requests.get(media_url, stream=True)
        r.raise_for_status()


        outputLog(f"filename2:{filename}")
        outputLog(f"Response status code: {r.status_code}")

        try:
            with open(filename, 'wb') as f:
                outputLog(f"test")
                for chunk in r.iter_content(chunk_size=1024):
                    outputLog(f"chunk:{chunk}")
                    if chunk:
                        f.write(chunk)
                        f.flush()
        except Exception as e:
            outputLog(str(ex))   

        outputLog(f"Download completed: {filename}")
        return filename
    except:
        outputLog(f"filename:None")
        return ""

def dmmurl変換(input: str, replacement: str) -> str:
    # URLを抜き出すための正規表現パターン
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'

    # URLのパラメータ `af_id` の置換パターン
    # param_pattern = r"(?<=af_id=)[^&]+"

    # 抜き出されたURLを元に戻す関数
    def get_original_url(short_url):
        try:
            # リダイレクトを追跡して元のURLを取得
            response = requests.head(short_url, allow_redirects=True)
            return response.url
        except requests.RequestException:
            # 失敗した場合はそのまま返す
            return short_url

    # URLを抽出して処理
    def replace_urls_in_text(text):
        # 元のテキストから全てのURLを抽出
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            # 短縮URLのリダイレクト先を取得
            original_url = get_original_url(url)

            # URLを解析
            parsed_url = urlparse(original_url)

            # クエリパラメータを取得
            query_params = parse_qs(parsed_url.query)

            # lurlパラメータを取得
            lurl_value = query_params.get('lurl', [None])[0]

            if lurl_value != None:
                # URLデコード
                decoded_str = urllib.parse.unquote(lurl_value)

                modified_url = "https://al.dmm.com/?lurl="+urllib.parse.quote(decoded_str.split("?")[0], safe='')+"&af_id="+replacement

                # af_idパラメータを置換
                # modified_url = re.sub(param_pattern, replacement, original_url)
            
            # 元のテキストのURLを置換されたURLに置き換える
            text = text.replace(url, modified_url)
        
        return text

    # 実行して結果を表示
    result_text = replace_urls_in_text(input)
    return result_text

def sanitize_filename(filename):
    # ファイル名に使えない文字を定義
    forbidden_chars = r'[<>:"/\\|?*]'
    # 正規表現でファイル名から使えない文字を削除
    sanitized = re.sub(forbidden_chars, '', filename)
    return sanitized

def generate_random_string(length):
    # 使用する文字のセットを定義（英数字）
    characters = string.ascii_letters + string.digits
    # 指定された長さのランダムな文字列を生成
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def proc_monomane_v1(credentials , target_tweet_id):
  
    check_tweet_account_record = get_check_tweet_account_list_by_tweet_id(target_tweet_id)

    tweet_text = check_tweet_account_record['tweet_text']
    update_time = convert_tweet_datetime(check_tweet_account_record['update_time'])

    # 現在時刻（UTC）
    now = convert_tweet_datetime(datetime.now(pytz.UTC))

    # 3時間以上前のツイートはモノマネ対象にしないが、search_listのモノマネ履歴には登録する
    if now - update_time >= timedelta(hours=3):
        outputLog(f"ツイートは3時間以上前のためスルーします。 tweet_text={tweet_text}")
        return True , None

    dmmid = credentials['dmm_id']

    medias = get_tweet_media(credentials['bearer_token'] , target_tweet_id)

    media_files = []

    # 画像
    for url in medias["photos"]:
        outputLog(f"photo URL: {url}")
        file = download_media("photo", target_tweet_id, credentials["bearer_token"])
        if os.path.isfile(file):
            media_files.append(file)
        else:
            outputLog("photo URL not found.")

    # 動画
    for url in medias["videos"]:
        outputLog(f"video URL: {url}")
        file = download_media("video", target_tweet_id, credentials["bearer_token"])
        if os.path.isfile(file):
            media_files.append(file)
        else:
            outputLog("video URL not found.")

    # GIF（もし扱うなら）
    for url in medias["gifs"]:
        outputLog(f"gif URL: {url}")
        file = download_media("gif", target_tweet_id, credentials["bearer_token"])
        if os.path.isfile(file):
            media_files.append(file)
        else:
            outputLog("gif URL not found.")            

    # メディアが無かったらv2によるテキストポスト
    try:
        if not media_files:  
            from twitter_api_v2 import proc_post_v2_monomane
            proc_post_v2_monomane(credentials , tweet_text)
        else:
            # スペースで分割して配列に変換
            words = tweet_text.replace("\n","【改行】").split(' ')

            # 最後の配列要素を削除
            if len(media_files)>0:
                words.pop()

            # 配列をスペースで結合して文字列に戻す
            result = " ".join(words).replace("【改行】","\n")
#            outputLog(f"result={result}")
            result = dmmurl変換(result, dmmid)
            response = None
#            outputLog(f"result2={result}")

#            outputLog(f"1")
            client = createClient(credentials)
#            outputLog(f"2")

            # 認証
            auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
            auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
#            outputLog(f"3")

            api = tweepy.API(auth)
#           if proxy_url!="":
#                api = tweepy.API(auth, proxy=proxy_url)
#            else:
#               api = tweepy.API(auth)   

            # モノマネツイート処理(モノマネ処理は行わない)
#            outputLog(f"4")

            media_ids = []  
            for file in media_files:
                try:
                    # ファイルをアップロード
#                    outputLog(f"test1")

                    try:
                        media = api.media_upload(file)
                    except Exception as e:
                        outputLog(str(e))

#                    outputLog(f"test2")
                    media_ids.append(media.media_id)  # media_idをリストに追加
                    outputLog(f"Media uploaded: {file}, Media ID: {media.media_id}")
                except Exception as e:
                    outputLog(f"Error uploading media {file}: {e}")
                    return False, f"Error uploading media: {e}"

            if media_files:
                outputLog(f"media_files={media_files}")
                media_ids = [api.media_upload(file).media_id for file in media_files]
#                outputLog(f"test2")
                outputLog(f"media_ids={media_ids}")
#                outputLog("media tweet")  
                response = client.create_tweet(text=result, media_ids=media_ids)
#                outputLog(f"5")
            else:
                outputLog("media no tweet")  

                response = client.create_tweet(text=result)
                outputLog(f"5")


#        try:
#           outputLog(f"search_row={search_row}")
#           outputLog(f"tweet_data={tweet_data}")
#           outputLog(f"response={response.data}")
#           insert_tweet_history_monomane2(target_tweet_id , check_tweet_account_record )
#        except Exception as ex:
#            outputLog(str(ex))

        time.sleep(5)

#        try:
#           outputLog(f"search_row={search_row}")
#           outputLog(f"tweet_data={tweet_data}")
#           outputLog(f"response={response.data}")
#           insert_tweet_history_monomane(search_row , tweet_data , response.data)
#        except Exception as ex:
#            outputLog(str(ex))

        # レスポンス内容を出力
        outputLog("Response from client.create_tweet:")
        outputLog(response)                

        response_str = json.dumps(response.data)  # JSON 文字列に変換

        outputLog(f"Tweet created successfully:{response.data}")
        outputLog(f"response.errors:{response.errors}")
        outputLog(f"response_str:{response_str}")

        # ステータスコードの代わりにエラーを確認
        return response.errors is None or len(response.errors) == 0, response_str
                
    except Exception as ex:
        outputLog(str(ex))
        return False , str(ex)
    finally:
        # ダウンロードしたファイルを削除
        for file in media_files:
            try:
                outputLog(f"delete file:{file}")
                os.remove(file)
            except:
                pass

    return False,None
