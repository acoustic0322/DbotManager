import sys
import tweepy
import pymysql
import os
import requests
import time
from datetime import datetime
import pyperclip
import json
from requests_oauthlib import OAuth1Session
from datetime import datetime, timezone, timedelta

from twitter_api_v2 import proc_like_v2
from twitter_api_v2 import proc_bookmark_v2
from twitter_api_v2 import proc_post_v2_old
from twitter_api_v2 import proc_post_v2
from twitter_api_v2 import proc_repost_v2

from mysql import get_account_master
from mysql import get_check_account_list
from mysql import save_tweet_history
from twitter_api_v2 import proc_update_refresh_token


# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

def print_id(text):
    print("account_id=",account_id, " " , text)
    return 

    
def outputLog(message):
    # 現在時刻を取得してメッセージに追加
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#    full_message = f"[{current_time}] [account_id={account_id}] {message}"
    full_message = f"[{current_time}] {message}"
    
    # 標準出力にメッセージを出力
    print(full_message)

args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id","0"))
account_id2 = int(args.get("account_id2","0"))
tweet_id = args.get("tweet_id","")
mode = args.get("mode","")
#tweet_text = args.get("text")
comment_id = args.get("comment_id","")

media_type = args.get("media_type","")
media_id = args.get("media_id","")
#photo_id = args.get("photo_id","")
#video_id = args.get("video_id","")
check_list_id = args.get("check_list_id","")
check_account_name = args.get("check_account_name","")
outputLog(args)

if mode ==  "check_refresh":
    proc_update_refresh_token()
    sys.exit(0)

# 認証情報を取得
credentials = get_account_master(account_id)
#access_tokenの有効判定を行い、古かったら更新
#credentials['bearer_token'] , credentials['refresh_token'] = check_access_token(credentials)

if credentials:
    error_log = ""
    if mode == "post":
#                success , error_log = proc_post_v2(credentials)
        success , error_log = proc_post_v2(credentials , comment_id , media_type , media_id , "")               
    elif mode == "reply":
        success , error_log = proc_post_v2(credentials , comment_id , media_type , media_id , tweet_id)               
#        success , error_log = True , "" #未実装
    elif mode == "repost":
        success , error_log = proc_repost_v2(credentials, tweet_id)
    elif mode == "like":
        success , error_log = proc_like_v2(credentials, tweet_id)
    elif mode == "bookmark":
        success , error_log = proc_bookmark_v2(credentials, tweet_id)

    else:
        # エラーメッセージを標準エラーに出力
        outputLog(f"サポートされていないmode: {mode}")
        # 終了コードを1にして異常終了を示す
        sys.exit(1)

    outputLog(f"success={success}")
    outputLog(f"error_log={error_log}")

    if success == True:
        save_tweet_history(account_id, comment_id , mode , tweet_id , True , error_log)
        print(json.dumps({"success": True, "error_log": error_log}))
        sys.exit(0)
    else:
#                outputLog(f"エラーが発生しました: {result}", file=sys.stderr)
        save_tweet_history(account_id, comment_id , mode , tweet_id , False , error_log)
        print(json.dumps({"success": False, "error_log": error_log}))
        sys.exit(1)

else:
    outputLog(f"エラーが発生しました: ID {credential_id} の認証情報が見つかりませんでした。", file=sys.stderr)
    sys.exit(1)
