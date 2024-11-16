# ライブラリ
import tweepy
import sys
import os
import re
import requests
import csv
from operator import itemgetter
import time
import re
import random
import string
from urllib.parse import urlparse, parse_qs
import urllib.parse
import configparser

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

def isint(s):  # 整数値を表しているかどうかを判定
    try:
        int(s)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False
    else:
        return True

# ini読込
ini = "setting.ini"
waittime = 60*20
if os.path.exists(ini):
    config = configparser.ConfigParser()
    config.read(ini)
    waittime = int(config['CODEINFO']['WAITSECONDTIME']) if isint(config['CODEINFO']['WAITSECONDTIME']) else 60*20

args = sys.argv

if len(args) < 4:
    sys.exit()

# ファイルのパスを指定
file_path = os.path.join(args[2],'key.txt')  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

if len(lines) < 8:
    sys.exit()

screen_names = args[1].replace("\r\n","\n").split("\n")
folder = args[2]

# Twitter Developer Portalから取得したキーを設定
ck = lines[0]
cs = lines[1]
at = lines[2]
ats = lines[3]
bearer_token = lines[4]
refresh_token = lines[5]
client_id = lines[6]
client_secret = lines[7]

proxy_url = args[3]

dmmid = args[4]

# セッションを作成

if proxy_url:
    # プロキシ設定がある場合のみ設定
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

# ユーザ名からid取得
try:
    # 認証情報を設定する
    # raise # デバグ用
    client = tweepy.Client(bearer_token=bearer_token, consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
    if proxy_url!="":
        client.session.proxies = proxies
    user = client.get_user(username=screen_names[0].replace("@",""))
except Exception as ex1:
    print(ex1)
    try:
        new_bearer_token,new_refresh_token = refresh_access_token(client_id,client_secret,refresh_token)
        if new_bearer_token != None and new_refresh_token != None:
            c = [ck,cs,at,ats,str(new_bearer_token),str(new_refresh_token),client_id,client_secret]
            d = "\n".join(c)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(d)
            print("更新完了")
            # 認証情報を設定する
            client = tweepy.Client(bearer_token=str(new_bearer_token), consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
            if proxy_url!="":
                client.session.proxies = proxies
    except Exception as ex:
        print(ex)
        sys.exit()

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

    # 取得したツイートを表示する
    # print(tweets.data)
    if result_data is not None and len(result_data) > 0:
        # 認証
        auth = tweepy.OAuthHandler(ck, cs)
        auth.set_access_token(at, ats)
        if proxy_url!="":
            api = tweepy.API(auth, proxy=proxy_url)
        else:
            api = tweepy.API(auth)
        
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
            in_reply_to_tweet_id = str(tweet.referenced_tweets[0]['id']) if tweet.referenced_tweets else ''
            if in_reply_to_tweet_id != "" and str(tweet.author_id) != userid:
                continue
            # print(in_reply_to_tweet_id)

            # print(tweet_data)
            try:
                # print(tweet_data['attachments'])
                if 'attachments' in tweet_data:
                    media_keys = tweet_data['attachments']['media_keys']
                    media = {m.media_key: m for m in tweets.includes['media']}
                    
                    for key in media_keys:
                        media_type = media[key].type
                        if media_type == 'photo':
                            print(f"Image URL: {media[key].url}")
                            file = download_url(media_type,media[key].url)
                            if os.path.isfile(file):
                                media_files.append(file)
                        elif media_type == 'video':
                            video_url = None
                            for variant in media[key].variants:
                                if variant.get('content_type') == 'video/mp4':
                                    video_url = variant.get('url')
                                    if video_url:
                                        print(f"Video URL: {video_url}")
                                        file = download_url(media_type,video_url)
                                        if os.path.isfile(file):
                                            media_files.append(file)
                                            break
                            else:
                                print("Video URL not found.")

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
                print(ex)
            finally:
                # ダウンロードしたファイルを削除
                for file in media_files:
                    try:
                        os.remove(file)
                    except:
                        pass
                
                time.sleep(5)
                if since_id=="":
                    break

        if len(tweeted_ids)>0:
            with open(os.path.join(folder, f"{path_tmp_screen_name}_sinceid3.txt"), 'w', encoding='utf-8') as file:
                for tweet in tweets.data:
                    file.write(f"{tweet.id}\n")
            with open(os.path.join(folder, f"{path_tmp_screen_name}_tweeted3.csv"), 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for tweet in tweeted_ids:
                    writer.writerow(tweet)
    
    time.sleep(waittime)
        
