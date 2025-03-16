import requests
from bs4 import BeautifulSoup
import re
import json
from config import outputLog
import os

def download_video(video_url, filename="video"):

    filename = f"media/{filename}.mp4"

    """動画をダウンロード"""
    outputLog("download_video")
    response = requests.get(video_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    file_path = os.path.abspath(filename)
    outputLog(f"動画を {file_path} に保存しました。")
    return file_path  # ダウンロードしたファイルの絶対パスを返す    

def download_photo(photo_url, filename="photo"):

    """画像をダウンロード"""
    filename = f"media/photo/{filename}.jpeg"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    outputLog("download_photo")
    response = requests.get(photo_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    file_path = os.path.abspath(filename)
    outputLog(f"画像を {file_path} に保存しました。")
    return file_path

def get_tweet_data(bearer_token , tweet_id):
    """ツイートのメディアURLを取得"""
    url = f"https://api.twitter.com/2/tweets/{tweet_id}?expansions=attachments.media_keys&media.fields=variants,url"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    response = requests.get(url, headers=headers)

    # レスポンスを確認
    outputLog(f"Response Status:{response.status_code}")
    outputLog(f"Response JSON:{response.json()}")    

    if response.status_code == 200:
        data = response.json()
        media = data.get("includes", {}).get("media", [])
        
        for item in media:
            if "variants" in item:
                for variant in item["variants"]:
                    if variant["content_type"] == "video/mp4":
                        outputLog(f"variant[url]={variant['url']}")
                        return variant["url"]
            elif "url" in item:  # 画像
                return item["url"]

    outputLog("return None")    
    return None

def download_media(media_type , tweet_id , bearer_token):
    
    outputLog("")

    try:
        media_url = get_tweet_data(bearer_token, tweet_id)
        if not media_url:
            return None        

        if media_type == "video":
            return download_video(media_url , tweet_id)

        elif media_type == "photo":
            return download_photo(media_url, tweet_id)        

    except Exception as ex:
        outputLog(str(ex))

    return None
