import os
import configparser
from datetime import datetime, timezone

import pytz
import inspect

import pytz
#from dateutil import parser  # dateutilを使用

import inspect

def convert_tweet_datetime(iso_format_date):

#    try:
#        # 文字列をパースし、タイムゾーン付きのdatetimeオブジェクトに変換
#        parsed_date = parser.parse(iso_format_date)

#        # 日本時間に変換 (UTC +9)
#        japan_zone = pytz.timezone('Asia/Tokyo')
#        japan_time = parsed_date.astimezone(japan_zone)

#        # フォーマット変更
#        return japan_time.strftime("%Y-%m-%d %H:%M:%S")

#    except ValueError as e:
#        return None

    # iso_format_date がすでに datetime オブジェクトの場合は、そのまま処理
    if isinstance(iso_format_date, datetime):
        parsed_date = iso_format_date
    else:
        try:
            # ミリ秒部分とZを無視してパース
            parsed_date = datetime.strptime(iso_format_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError as e:
            try:
                # ミリ秒が無い場合の処理
                parsed_date = datetime.strptime(iso_format_date, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError as e:
                print(f"ミリ秒なしのパースエラー: {e}")
                return None

#    try:
#        # ミリ秒部分とZを無視してパース
#        parsed_date = datetime.strptime(iso_format_date, "%Y-%m-%dT%H:%M:%S.%fZ")
#    except ValueError as e:
##        print(f"ミリ秒ありのパースエラー: {e}")
#        try:
#            # ミリ秒が無い場合の処理
#            parsed_date = datetime.strptime(iso_format_date, "%Y-%m-%dT%H:%M:%SZ")
#        except ValueError as e:
#            print(f"ミリ秒なしのパースエラー: {e}")
#            return None

    # UTCタイムゾーンを指定
#    utc_zone = pytz.utc
#    parsed_date = utc_zone.localize(parsed_date)

    # 日本時間に変換 (UTC + 9)
    japan_zone = pytz.timezone('Asia/Tokyo')
    japan_time = parsed_date.astimezone(japan_zone)

    # フォーマット変更
#    return japan_time.strftime("%Y-%m-%d %H:%M:%S")  
    return japan_time

def convert_tweet_datetime2(tweet_datetime_str):
    """ツイートの created_at (ISO8601形式の文字列) を UTC の datetime に変換"""
    dt_jst = datetime.fromisoformat(tweet_datetime_str.replace("Z", "+00:00"))  # ISO8601をパース
    return dt_jst.astimezone(timezone.utc)  # UTC に変換

def outputLog(message):

    # 呼び出し元情報
    caller_frame = inspect.currentframe().f_back
    caller_info = inspect.getframeinfo(caller_frame)

    file_name = os.path.basename(caller_info.filename)
    function_name = caller_info.function
    line_number = caller_info.lineno

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_message = (
        f"[{current_time}]"
        f"[{file_name} - {function_name} - Line {line_number}] "
        f"{message}"
    )

    # ログフォルダ作成
    os.makedirs(log_dir, exist_ok=True)

    # 日付ごとのログファイル
    log_file = os.path.join(
        log_dir,
        f"pylog_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # ファイルへ追記
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(str(log_message) + "\n")

    if debug == False:
        return

    # 呼び出し元の情報を取得
    caller_frame = inspect.currentframe().f_back
    caller_info = inspect.getframeinfo(caller_frame)
    
    # ファイル名、関数名、行番号を取得
    file_name = os.path.basename(caller_info.filename)
    function_name = caller_info.function    
    line_number = caller_info.lineno    

    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#    full_message = f"[{current_time}] [account_id={account_id}] {message}"
#    full_message = f"[{current_time}] {message}"
    
    # ログを整形して出力
    print(f"[{current_time}][{file_name} - {function_name} - Line {line_number}] {message}")    
#    # 標準出力にメッセージを出力
#    print(full_message)

# INIファイルのパス
config_file = "config.ini"

# ConfigParserを使ってINIファイルを読み込む
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")

# INIファイルからmedia_dirを取得 (デフォルトは現在のスクリプトの場所)
media_dir = config.get("Paths", "media_dir", fallback=os.path.dirname(os.path.abspath(__file__)))
#media_dir = "D:\DbotManager\DbotManager\bin\Debug\python\upload"
#print("media_dir=",media_dir)
log_dir = config.get("Paths", "log_dir", fallback=os.path.dirname(os.path.abspath(__file__)))

debug = True

db_host = "203.137.53.205"



#※親
#ユーザー名:Hashidai00
#パスワード:@Hashidai00
#API: 7f7dc877aadbc0b7c996d6e48e95f1bf 
#----------------------------------------------- 
#just anotherログイン情報
#※子供1
#ユーザー名:Hashidai0531
#パスワード:@Hashidai00
#API: 026e7a18d6426b6bad09801b5e203883
#D — 昨日 16:05
#こちらを使用する
#just anotherログイン情報
#※子供2
#ユーザー名:Hashidai042210
#パスワード:@Hashidai00
#API: 58215aa1068f63c788c2cc2f49288be5

# リリース用API
#jap_api_key = '7f7dc877aadbc0b7c996d6e48e95f1bf'
#jap_api_key = '58215aa1068f63c788c2cc2f49288be5'

# デバッグ用API
#jap_api_key = '58215aa1068f63c788c2cc2f49288be5'

