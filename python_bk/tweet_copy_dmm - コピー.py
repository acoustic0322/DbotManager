import sys
import tweepy
import pymysql
import os
import requests
import time
import pyperclip
import json
from requests_oauthlib import OAuth1Session
from datetime import datetime, timezone, timedelta

from mysql import get_search_list
from mysql import update_search_list

import config
import re
from urllib.parse import urlparse, parse_qs
import urllib.parse



from config import outputLog
from config import convert_tweet_datetime



def download_url(media_type,media_url):
    try:
        filename = f"{generate_random_string(10)}.{media_url.split('.')[-1].split('?')[0]}"
        r = requests.get(media_url, stream=True)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return filename
    except:
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


# コマンドライン引数の解析関数
def tweet_copy_dmm(credentials , search_id , dmmid):

    # データベースから履歴検索
    search_row = get_search_list(search_id)

    print(search_row['search_user_name'])

    search_user_name = search_row['search_user_name']

    client = tweepy.Client(
        bearer_token=credentials['bearer_token'], 
        consumer_key=credentials['api_key'], 
        consumer_secret=credentials['api_key_secret'], 
        access_token=credentials['access_token'], 
        access_token_secret=credentials['access_token_secret']
        )

    tweets = client.search_recent_tweets(
        f'from:{search_user_name} -is:retweet',
        tweet_fields=["id","text", "author_id", "created_at","attachments","referenced_tweets","in_reply_to_user_id"],
        expansions = ['attachments.media_keys'],
        media_fields = ['url', 'type','variants']
    )

    if tweets is None or len(tweets) == 0 or tweets.data is None:
        return False , None

    result_data = tweets.data

#    print("result_data")
#    print(result_data)
    print("tweets")
    print(tweets)


    # 取得したツイートを表示する
    # print(tweets.data)
    if result_data is not None and len(result_data) > 0:
        # 認証
        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
        auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])

        api = tweepy.API(auth)
#        if proxy_url!="":
#            api = tweepy.API(auth, proxy=proxy_url)
#        else:
#            api = tweepy.API(auth)
        
        # 監視アカウントのidを取得
        # user2 = client.get_user(username=tmp_screen_name,user_auth=True)
        # userid=str(user2.data['id'])
        # user = api.get_user(screen_name=tmp_screen_name)
        # userid = user.id_str
        # print(userid)

        includes_users = {user.id: user for user in tweets.includes['users']} if 'users' in tweets.includes else {}
        
        for tweet in result_data:
            # print(result_data)
            # input()
            media_files = []
            tweeted_ids = []
            tweet_data = tweet.data

            # リプ、かつ監視アカウントでないなら処理しない
            userid = str(tweet.in_reply_to_user_id)
            # print(tweet.in_reply_to_user_id)
            # input()

            # リプライを除外する
            in_reply_to_tweet_id = str(tweet.referenced_tweets[0]['id']) if tweet.referenced_tweets else ''
            if in_reply_to_tweet_id != "" and str(tweet.author_id) != userid:
                continue

            outputLog("tweet_data")
            outputLog(tweet_data)

            # created_at を取得
            created_at_str = convert_tweet_datetime(tweet_data['created_at'])

            # データベースから履歴検索
            search_row = get_search_list(search_id)

            # 古いツイートに関しては処理しない
            if search_row['last_monomane_time'] is not None and search_row['last_monomane_time'] >= created_at_str:
                continue

            outputLog("last_monomane_time")
            outputLog(search_row['last_monomane_time'])

            outputLog("created_at_str")
            outputLog(created_at_str)

            update_search_list(search_id , "monomane" , tweet_data['id'] , created_at_str)

            continue

            try:
                # print(tweet_data['attachments'])
                if 'attachments' in tweet_data:
                    media_keys = tweet_data['attachments']['media_keys']
                    media = {m.media_key: m for m in tweets.includes['media']}
                    
                    for key in media_keys:
                        media_type = media[key].type
                        if media_type == 'photo':
                            outputLog(f"Image URL: {media[key].url}")
                            file = download_url(media_type,media[key].url)
                            if os.path.isfile(file):
                                media_files.append(file)
                        elif media_type == 'video':
                            video_url = None
                            for variant in media[key].variants:
                                if variant.get('content_type') == 'video/mp4':
                                    video_url = variant.get('url')
                                    if video_url:
                                        outputLog(tweet_data)
                                        outputLog(f"Video URL: {video_url}")
                                        file = download_url(media_type,video_url)
                                        outputLog("video file=",file)
                                        if os.path.isfile(file):
                                            media_files.append(file)
                                            break
                            else:
                                outputLog("Video URL not found.")

                # スペースで分割して配列に変換
                words = tweet.text.replace("\n","【改行】").split(' ')

                # 最後の配列要素を削除
                if len(media_files)>0:
                    words.pop()

                # 配列をスペースで結合して文字列に戻す
                result = " ".join(words).replace("【改行】","\n")
                result = dmmurl変換(result, dmmid)
                # print(result)
                # input()
                # print(media_files)
                # print(f"{tweet.id}:{result}:{tweet.created_at}")
                # input()
                # ツイートの再投稿
                # print("in_reply_to_tweet_id:"+in_reply_to_tweet_id)
                if in_reply_to_tweet_id != "":
                    # 自分の投稿したどのtweetidか取得、ないなら無視
                    referenced_tweet_id = in_reply_to_tweet_id
                    # print(tweeted)
                    for data in tweeted:
                        # print(data[0])
                        # print(in_reply_to_tweet_id)
                        if str(data[0]) == in_reply_to_tweet_id:
                            referenced_tweet_id = str(data[1])
                            break

                    # print(referenced_tweet_id)
                    if media_files:
                        media_ids = [api.media_upload(file).media_id for file in media_files]
                        response = client.create_tweet(text=result, media_ids=media_ids, in_reply_to_tweet_id=referenced_tweet_id)
                        tweeted_ids.append([tweet.id,response.data['id']])
                        tweeted.append([tweet.id,response.data['id']])
                    else:
                        response = client.create_tweet(text=result, in_reply_to_tweet_id=referenced_tweet_id)
                        tweeted_ids.append([tweet.id,response.data['id']])
                        tweeted.append([tweet.id,response.data['id']])
                else:
                    for data in tweeted:
                        if str(data[0]) != tweet.id:
                            if media_files:
                                media_ids = [api.media_upload(file).media_id for file in media_files]
                                response = client.create_tweet(text=result, media_ids=media_ids)
                                tweeted_ids.append([tweet.id,response.data['id']])
                                tweeted.append([tweet.id,response.data['id']])
                            else:
                                response = client.create_tweet(text=result)
                                tweeted_ids.append([tweet.id,response.data['id']])
                                tweeted.append([tweet.id,response.data['id']])
            except Exception as ex:
                outputLog(ex)
            finally:
                # ダウンロードしたファイルを削除
                for file in media_files:
                    try:
                        os.remove(file)
                    except:
                        pass
                
                time.sleep(5)
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
        
