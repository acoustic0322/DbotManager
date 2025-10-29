import os
import configparser
from datetime import datetime, timezone

import pytz
import inspect

import pytz
#from dateutil import parser  # dateutilを使用

def convert_tweet_datetime(value, assume_tz="UTC", return_tz="Asia/Tokyo"):
    """
    value: str or datetime
      例1: '2025-09-12T10:30:45.123Z' (UTC)
      例2: '2025-09-12T10:30:45Z'     (UTC)
      例3: '2025-01-02 17:15:49'      (TZなし → assume_tz を適用)
      例4: datetime(…)(naive/aware)
    assume_tz: value が naive のときに仮定する元タイムゾーン（'UTC' か 'Asia/Tokyo' など）
    return_tz: 返却するタイムゾーン（既定: JST）
    戻り値: return_tz の aware datetime
    """
    if value is None:
        return None

    tz_assume = pytz.timezone(assume_tz)
    tz_return = pytz.timezone(return_tz)

    # 1) datetime ならそのまま
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip()

        # Z(UTC) 付き ISO
        msec_z = re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$", s)
        sec_z  = re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", s)

        if msec_z:
            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        elif sec_z:
            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        else:
            # 'YYYY-MM-DD HH:MM:SS'（TZなし）想定
            try:
                dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # 他フォーマットに対応したければここで追加
                raise

    # 2) naive なら assume_tz を付与
    if dt.tzinfo is None:
        dt = tz_assume.localize(dt)

    # 3) 返却TZへ変換（JST既定）
    return dt.astimezone(tz_return)

def convert_tweet_datetime2(tweet_datetime_str):
    """ツイートの created_at (ISO8601形式の文字列) を UTC の datetime に変換"""
    dt_jst = datetime.fromisoformat(tweet_datetime_str.replace("Z", "+00:00"))  # ISO8601をパース
    return dt_jst.astimezone(timezone.utc)  # UTC に変換

def get_ip_address():
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    outputLog(f"ローカルIP:{ip}") 
    return ip

#def outputLog(message, log_dir=None):
def outputLog(message):
#    print("log_dir")

#    print(log_dir)

    # log_dir が指定されてなければ Documents 配下を使う
#    if log_dir is None:
    home = os.path.expanduser("~")
    log_dir = os.path.join(home, "Documents", "DBotManager", "log")

    # ログフォルダを作成（存在しなければ作成）
    os.makedirs(log_dir, exist_ok=True)

    # 日付ごとのログファイル名
    today_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{mode}_{today_str}.log")

    # 呼び出し元の情報を取得
    caller_frame = inspect.currentframe().f_back
    caller_info = inspect.getframeinfo(caller_frame)
    
    file_name = os.path.basename(caller_info.filename)
    function_name = caller_info.function
    line_number = caller_info.lineno

    # ログメッセージを整形
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{current_time}][{file_name} - {function_name} - Line {line_number}] {message}"

    # debug=True のときだけコンソールに出力
    if debug:
        print(log_message)

    # ファイルに追記
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def outputLog_bk(message):

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

debug = True
mode = 'search_tweet'

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

