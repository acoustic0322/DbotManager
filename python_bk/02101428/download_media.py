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

def get_tweet_data(bearer_token , tweet_id):
    url = f"https://api.twitter.com/2/tweets/{tweet_id}?expansions=attachments.media_keys&media.fields=variants"
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
    return None

def download_media(media_type , tweet_id , bearer_token):
    
    outputLog("")

    try:
        if media_type == "video":
            video_url = get_tweet_data(bearer_token , tweet_id) 
            return download_video(video_url , tweet_id)
    except Exception as ex:
        outputLog(str(ex))

    return None
