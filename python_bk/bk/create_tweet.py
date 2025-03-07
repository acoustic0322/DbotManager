#ライブラリ
import tweepy
import sys
import urllib.parse
import os

def is_image_file(file_path):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in image_extensions

def is_video_file(file_path):
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in video_extensions

args = sys.argv

if len(args) < 6:
    sys.exit()

# ファイルのパスを指定
file_path = os.path.join(args[1],'key.txt')  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

if len(lines) < 4:
    sys.exit()

# Twitter Developer Portalから取得したキーを設定
ck = lines[0]
cs = lines[1]
at = lines[2]
ats = lines[3]

# print(content)
# input()

proxy_url = args[6]

if proxy_url!="":
    # プロキシ設定がある場合のみ設定
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

#認証
client = tweepy.Client(
    consumer_key=ck,
    consumer_secret=cs,
    access_token=at,
    access_token_secret=ats
)

if proxy_url!="":
    client.session.proxies = proxies

#ツイート内容
content = urllib.parse.unquote(args[2])
# 認証
auth = tweepy.OAuthHandler(ck, cs)
auth.set_access_token(at, ats)
if proxy_url!="":
    api = tweepy.API(auth, proxy=proxy_url)
else:
    api = tweepy.API(auth)

# rate_limit_status = api.rate_limit_status()
# print(rate_limit_status)
# input()

photo_path = args[3]
video_path = args[4]
tweet_id = args[5]
media_ids =[]
if os.path.exists(photo_path) and is_image_file(photo_path):
    # 画像をアップロード
    media = api.media_upload(filename=photo_path)
    media_ids.append(media.media_id)
if os.path.exists(video_path) and is_video_file(video_path):
    # 動画をアップロード
    media = api.media_upload(video_path, media_category='tweet_video')
    media_ids.append(media.media_id)
    
if len(media_ids)>0 and tweet_id != "":
    client.create_tweet(text=content, in_reply_to_tweet_id=tweet_id, media_ids=media_ids)
elif len(media_ids)>0 and tweet_id == "":
    client.create_tweet(text=content, media_ids=media_ids)
elif len(media_ids)==0 and tweet_id != "":
    client.create_tweet(text=content, in_reply_to_tweet_id=tweet_id)
else:
    client.create_tweet(text=content)

print("ツイート完了")

