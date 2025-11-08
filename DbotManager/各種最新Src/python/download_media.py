import requests
from bs4 import BeautifulSoup
import re
import json
from config import outputLog
import os

def download_video(video_url, idx, filename="video"):

    filename = f"media/{filename}_{idx}.mp4"

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

def download_photo(photo_url, idx, filename="photo"):

    """画像をダウンロード"""
    filename = f"media/{filename}_{idx}.jpeg"
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

def download_media_url(media_type , tweet_id, media_url , idx, bearer_token):
    
    try:
        if media_type == "video":
            return download_video(media_url ,idx , tweet_id)

        elif media_type == "photo":
            return download_photo(media_url, idx, tweet_id)        

    except Exception as ex:
        outputLog(str(ex))

    return None

def _pick_best_video_variant(variants):
    """video/mp4 の中から最も高ビットレートを返す。無ければ最初の m3u8 を返す。"""
    mp4s = [v for v in variants if v.get("content_type") == "video/mp4" and "url" in v]
    if mp4s:
        mp4s.sort(key=lambda v: v.get("bit_rate", 0), reverse=True)
        return mp4s[0]["url"]
    # フォールバック（HLS）
    hls = [v for v in variants if v.get("content_type", "").endswith("mpegURL") and "url" in v]
    return hls[0]["url"] if hls else None

def get_tweet_media(bearer_token, tweet_id):
    """
    指定ツイートのメディアを一括取得
    戻り値: {
      "photos": [url, ...],
      "videos": [url, ...],        # 最高ビットレートのMP4（無ければm3u8）
      "gifs":   [url, ...],        # animated_gifのMP4（無ければm3u8）
      "raw":    includes_media     # 必要なら生データも参照用に
    }
    """
    url = (
        f"https://api.twitter.com/2/tweets/{tweet_id}"
        "?expansions=attachments.media_keys"
        "&media.fields=media_key,type,url,variants,preview_image_url,duration_ms,alt_text"
    )
    headers = {"Authorization": f"Bearer {bearer_token}"}

    response = requests.get(url, headers=headers)
    try:
        j = response.json()
    except Exception:
        j = {}

    # ログ（任意）
    try:
        outputLog(f"Response Status:{response.status_code}")
        outputLog(f"Response JSON:{j}")
    except NameError:
        pass  # outputLogが無い環境でも動くように

    result = {"photos": [], "videos": [], "gifs": [], "raw": []}

    if response.status_code != 200:
        return result

    media_list = j.get("includes", {}).get("media", [])
    result["raw"] = media_list

    for m in media_list:
        mtype = m.get("type")
        if mtype == "photo":
            # 静止画
            if m.get("url"):
                result["photos"].append(m["url"])

        elif mtype == "video":
            # 動画：variantsから最適URLを選択
            best = _pick_best_video_variant(m.get("variants", []))
            if best:
                result["videos"].append(best)

        elif mtype == "animated_gif":
            # GIF：基本はvariantsにMP4が入る
            best = _pick_best_video_variant(m.get("variants", []))
            if best:
                result["gifs"].append(best)

    return result