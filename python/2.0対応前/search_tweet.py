# ライブラリ
import tweepy
import sys
import os
import re
import requests
    
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

args = sys.argv

if len(args) < 3:
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
    # user = client.get_user(username=tmp_screen_name)

    # userid=str(user.data['id'])
    # print(userid)

    since_id=""
    path_tmp_screen_name = sanitize_filename(tmp_screen_name)
    if os.path.exists(os.path.join(folder, f"{path_tmp_screen_name}_sinceid.txt")):
        with open(os.path.join(folder, f"{path_tmp_screen_name}_sinceid.txt"), 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
            since_id = file.read().strip().replace("\r\n","\n").split("\n")[0]

    if since_id!="":
        try:
            tweets = client.search_recent_tweets(
                f'from:{tmp_screen_name} is:reply',
                since_id=since_id,
                max_results=100,
                tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
            )
        except:
            tweets = client.search_recent_tweets(
                f'from:{tmp_screen_name} is:reply',
                max_results=100,
                tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
            )
    else:
        tweets = client.search_recent_tweets(
            f'from:{tmp_screen_name} is:reply',
            tweet_fields=["id","text", "author_id", "created_at","referenced_tweets"]
        )

    # 取得したツイートを表示する
    if tweets.data is not None and len(tweets.data) > 0:
        with open(os.path.join(folder, f"{path_tmp_screen_name}.txt"), 'w', encoding='utf-8') as file:
            for tweet in tweets.data:
                referenced_tweet_id = tweet.referenced_tweets[0]['id'] if tweet.referenced_tweets and len(tweet.referenced_tweets) > 0 else 'N/A'
                file.write(f"{referenced_tweet_id}\n")
        with open(os.path.join(folder, f"{path_tmp_screen_name}_sinceid.txt"), 'w', encoding='utf-8') as file:
            for tweet in tweets.data:
                file.write(f"{tweet.id}\n")
        for tweet in tweets.data:
            referenced_tweet_id = tweet.referenced_tweets[0]['id'] if tweet.referenced_tweets and len(tweet.referenced_tweets) > 0 else 'N/A'
            # print(f"{tweet.id}:{tweet.text}:{tweet.created_at}:{referenced_tweet_id}")
