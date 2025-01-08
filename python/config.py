import os
import configparser
from datetime import datetime

import pytz


def convert_tweet_datetime(iso_format_date):
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

def outputLog(message):

    if debug == True:

        # 現在時刻を取得してメッセージに追加
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#       full_message = f"[{current_time}] [account_id={account_id}] {message}"
        full_message = f"[{current_time}] {message}"
    
        # 標準出力にメッセージを出力
        print(full_message)

# INIファイルのパス
config_file = "config.ini"

# ConfigParserを使ってINIファイルを読み込む
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")

# INIファイルからmedia_dirを取得 (デフォルトは現在のスクリプトの場所)
media_dir = config.get("Paths", "media_dir", fallback=os.path.dirname(os.path.abspath(__file__)))
#media_dir = "D:\DbotManager\DbotManager\bin\Debug\python\upload"
#print("media_dir=",media_dir)

debug = True

