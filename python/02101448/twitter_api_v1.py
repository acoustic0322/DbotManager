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

from download_media import download_media

import config
from config import convert_tweet_datetime

from config import outputLog

import re
from urllib.parse import urlparse, parse_qs
import urllib.parse
import random
import string


#from twitter_api_v2 import createClient

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

def convert_tweet_datetime_gomi(iso_format_date):
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

def proc_monomane(search_row , tweet_data, tweets):

    outputLog(tweet_data)

    # Twitterのcreated_atはUTCなので、パースしてUTCタイムゾーンを適用
#    tweet_time = datetime.strptime(tweet_data['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')
#    tweet_time = tweet_time.replace(tzinfo=pytz.UTC)
    tweet_time = convert_tweet_datetime(tweet_data['created_at'])

    print("tweet_time=",tweet_time)

    # 現在時刻（UTC）
    now = convert_tweet_datetime(datetime.now(pytz.UTC))
    print("now=",now)

    # １時間以上前のツイートはモノマネ対象にしないが、search_listのモノマネ履歴には登録する
    if now - tweet_time >= timedelta(hours=1):
        outputLog(f"ツイートは1時間以上前のためスルーします。 tweet_data={tweet_data}")
        return True , None

    # モノマネ実施のアカウントID取得
    account_id = search_row['monomane_account_id']
    credentials = get_account_master(account_id)

    # リプライツイートの判定
    replyFlag = False
    if 'in_reply_to_user_id' in tweet_data and tweet_data['in_reply_to_user_id'] is not None:
        reply_target_tweet_id = tweet_data['referenced_tweets'][0]['id']
        reply_tweet_id = tweet_data['id']
        own_twweet_result , own_tweet_id = getOwnTweetId(account_id , reply_target_tweet_id)
        outputLog(f"reply_target_tweet_id={reply_target_tweet_id}")
        outputLog(f"reply_tweet_id={reply_tweet_id}")
        outputLog(f"own_tweet_id={own_tweet_id}")
        replyFlag = True

        #履歴にリプ先のツイート情報が無かったらリターン
        if own_twweet_result == False:
            outputLog(f"履歴にリプ先のツイート情報が無かったらリターン")
#            return True , None
            return False , None

    outputLog(account_id)

    credentials = get_account_master(account_id)
    dmmid = credentials['dmm_id']

    client = createClient(credentials)

    # 認証
    auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

    media_files = []

    try:
        # print(tweet_data['attachments'])
        media_files = []
        try:
            # includes からメディア情報を取得する処理
            if 'attachments' in tweet_data and 'media_keys' in tweet_data['attachments']:
                if tweet_data['type'] == 'video' or tweet_data['type'] == 'photo':
                    outputLog(f"{tweet_data['type']} URL: {tweet_data['url']}")

                    outputLog(f"credentials[bearer_token]={credentials['bearer_token']}")
#                    file = download_url(tweet_data['type'],tweet_data['url'])
                    file = download_media(tweet_data['type'],tweet_data['id'],credentials['bearer_token'])

                    if os.path.isfile(file):
                        media_files.append(file)
                    else:
                        outputLog(f"{tweet_data['type']} URL not found.")

        except Exception as ex:
            outputLog(str(ex))   
            return False , str(ex)

        outputLog(f"tweet_data={tweet_data}")
        outputLog(f"media_files={media_files}")

        # スペースで分割して配列に変換
        words = tweet_data['text'].replace("\n","【改行】").split(' ')

        # 最後の配列要素を削除
        if len(media_files)>0:
            words.pop()

        # 配列をスペースで結合して文字列に戻す
        result = " ".join(words).replace("【改行】","\n")
        outputLog(f"result={result}")
        result = dmmurl変換(result, dmmid)
                # print(result)
                # input()
                # print(media_files)
                # print(f"{tweet.id}:{result}:{tweet.created_at}")
                # input()
                # ツイートの再投稿
                # print("in_reply_to_tweet_id:"+in_reply_to_tweet_id)

        response = None

        outputLog(f"result = {result}")  


#        if False:
        try:

            api = tweepy.API(auth)
#           if proxy_url!="":
#                api = tweepy.API(auth, proxy=proxy_url)
#            else:
#               api = tweepy.API(auth)   

            # モノマネツイート処理(モノマネ処理は行わない)

            media_ids = []  
            for file in media_files:
                try:
                    # ファイルをアップロード
                    outputLog(f"test1")

                    try:
                        media = api.media_upload(file)
                    except Exception as e:
                        outputLog(str(e))

                    outputLog(f"test2")
                    media_ids.append(media.media_id)  # media_idをリストに追加
                    outputLog(f"Media uploaded: {file}, Media ID: {media.media_id}")
                except Exception as e:
                    outputLog(f"Error uploading media {file}: {e}")
                    return False, f"Error uploading media: {e}"

            if media_files:
                outputLog(f"media_files={media_files}")
                media_ids = [api.media_upload(file).media_id for file in media_files]
                outputLog(f"test2")
                outputLog(f"media_ids={media_ids}")
                if replyFlag == True:
                    outputLog("media reply")  
                    response = client.create_tweet(
                        text=result,
                        media_ids=media_ids,
                        in_reply_to_tweet_id =own_tweet_id  # 返信先のユーザーIDを指定
                    )
                else:
                    outputLog("media tweet")  
                    response = client.create_tweet(text=result, media_ids=media_ids)
            else:
                
                if replyFlag == True:
                    outputLog("media no reply")  
                    outputLog(f"result={result}")  
                    outputLog(f"own_tweet_id={own_tweet_id}")  

                    response = client.create_tweet(
                        text=result,
                        in_reply_to_tweet_id =own_tweet_id  # 返信先のユーザーIDを指定0
                    )
                else:
                    outputLog("media no tweet")  
                    response = client.create_tweet(text=result)

        except Exception as ex:
            outputLog(str(ex))   
            return False , str(ex)


        time.sleep(5)


        # モノマネツイート処理(モノマネ処理は行わない)
#        if media_files:
#            media_ids = [api.media_upload(file).media_id for file in media_files]
#            response = client.create_tweet(text=result, media_ids=media_ids)
#        else:
#            response = client.create_tweet(text=result)

        try:
           outputLog(f"search_row={search_row}")
           outputLog(f"tweet_data={tweet_data}")
           outputLog(f"response={response.data}")
#           outputLog(f"response[data]={response['data']}")
           insert_tweet_history_monomane(search_row , tweet_data , response.data)
#            insert_tweet_history_monomane(search_row , tweet_data , None)
        except Exception as ex:
            outputLog(str(ex))

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
    finally:
        # ダウンロードしたファイルを削除
        for file in media_files:
            try:
                outputLog(f"delete file:{file}")
                os.remove(file)
            except:
                pass

    return False,None
                
#        
#                if since_id=="":
#                    break

#        if len(tweeted_ids)>0:
#            with open(os.path.join(folder, f"{path_tmp_screen_name}_sinceid3.txt"), 'w', encoding='utf-8') as file:
#                for tweet in tweets.data:
#                    file.write(f"{tweet.id}\n")
#            with open(os.path.join(folder, f"{path_tmp_screen_name}_tweeted3.csv"), 'a', newline='', encoding='utf-8') as file:
#                writer = csv.writer(file)
#                for tweet in tweeted_ids:
#                    writer.writerow(tweet)
    
#    time.sleep(waittime)
