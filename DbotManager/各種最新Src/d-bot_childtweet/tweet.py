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
from twitter_api_v2 import proc_post_v2
from twitter_api_v2 import proc_repost_v2
from twitter_api_v2 import proc_check_v2
from twitter_api_v2 import proc_check_v2_2
from twitter_api_v2 import get_latest_tweet
from twitter_api_v1 import proc_post_v10a

from mysql import get_account_master
from mysql import get_check_account_list
from mysql import save_tweet_history
from mysql import get_search_list
from twitter_api_v2 import proc_update_refresh_token
#from twitter_api_v2 import proc_check_latest_tweet

import config
from config import outputLog

# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

def print_id(text):
    outputLog("account_id=",account_id, " " , text)
    return   


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
search_id = args.get("search_id","")

config.debug = args.get("debug","").lower() == "true"
dmmid = args.get("dmmid","")

#outputLog(args)

result1 = False
result2 = False
contents1 = None
contents2 = None

if mode ==  "check_refresh":
    outputLog("check_refresh")
    proc_update_refresh_token()
    sys.exit(0)

# 認証情報を取得
credentials = get_account_master(account_id)

if credentials:
    if mode == "post":
        if media_type != '':
            result1 , contents1 = proc_post_v10a(credentials , comment_id , media_type , media_id , tweet_id)               
        else:
            result1 , contents1 = proc_post_v2(credentials , comment_id , "")               
    elif mode == "reply":
        result1 , contents1 = proc_post_v2(credentials , comment_id , tweet_id)               
#        result1 , contents1 = True , "" #未実装
    elif mode == "repost":
        result1 , contents1 = proc_repost_v2(credentials, tweet_id)
    elif mode == "like":
        result1 , contents1 = proc_like_v2(credentials, tweet_id)
    elif mode == "bookmark":
        result1 , contents1 = proc_bookmark_v2(credentials, tweet_id)
    elif mode == "check":
        search_row = get_search_list(search_id)
        result1 , tweet1 , result2 , tweet2 , tweets , log = proc_check_v2_2(credentials , search_row)
        contents1 = tweet1.data['id'] if tweet1 else None
        contents2 = tweet2.data['id'] if tweet2 else None

        if contents1 is None:
            contents1 = log

#        if search_row['monomane_enable'] == True and result1 == True:
#        if True:
#            outputLog("monomane実行")
#            outputLog(f"tweet1={tweet1.data}")
#            result_wk , contents_wk = proc_monomane(search_row , tweet1.data , tweets)
#            save_tweet_history(search_row['monomane_account_id'], None , 'monomane' , None , result_wk , contents_wk , None , None )

    else:
        # エラーメッセージを標準エラーに出力
        outputLog(f"サポートされていないmode: {mode}")
        # 終了コードを1にして異常終了を示す
        sys.exit(1)

    outputLog(f"result1={result1}")
    outputLog(f"contents1={contents1}")
    outputLog(f"result2={result2}")
    outputLog(f"contents2={contents2}")

    print(json.dumps({"result1": result1, "contents1": contents1 , "result2": result2, "contents2": contents2}))
    save_tweet_history(account_id, comment_id , mode , tweet_id , result1 , contents1 , result2 , contents2)
    sys.exit(0)
#        sys.exit(1)    #false時?

else:
    outputLog(f"エラーが発生しました: ID {credential_id} の認証情報が見つかりませんでした。", file=sys.stderr)
    sys.exit(1)
