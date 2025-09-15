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
from twitter_api_v2 import refresh_access_token
from twitter_api_v1 import proc_post_v10a
from twitter_api_v2 import check_replies
from twitter_api_v2 import get_username_from_tweet_id_v2
from twitter_api_v2 import proc_search_v2
from twitter_api_v1 import proc_monomane_v1
from other import proc_profile_image
from other import update_profile_image

from jap_api import proc_like_jap
from jap_api import proc_bookmark_jap
from jap_api import proc_repost_jap

from twitter_api_v2 import proc_following_v2
from twitter_api_v2 import proc_unfollowing_v2
from twitter_api_v2 import proc_following_v1

from mysql import get_account_master
from mysql import get_check_account_list
from mysql import save_tweet_history
from mysql import get_search_list
from twitter_api_v2 import proc_update_refresh_token
#from twitter_api_v2 import proc_check_latest_tweet
from mysql import insert_tweet_history_monomane
from mysql import getOwnTweetId
from mysql import get_search_history
from mysql import init_check_tweet_account_master_by_search_list

from tweet_copy_dmm import tweet_copy_dmm

import config
from config import outputLog

#from tweet_watch import fetch_latest_tweet

from get_tweet_firefox_to_graphql import proc_get_tweet

# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

def print_id(text):
    outputLog(f"account_id={account_id} {text}")
    return   



#debug
#search_row = get_search_list(1)
#getOwnTweetId(search_row['monomane_account_id'] , 1886917519824576564)
#sys.exit(0)

args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id","0"))
account_id2 = int(args.get("account_id2","0"))
tweet_id = args.get("tweet_id","")
tweet_name = args.get("tweet_name","")
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

quantity = args.get("quantity","")

# 2025.09.02 コメントアウト
#ai_enable = False if args.get("ai_enable","") == "False" else True

jap_api_key = args.get("jap_api_key","")

#debug
#search_row={'id': 1, 'search_user_name': 'MANGA549764083', 'search_user_id': '2', 'post_account_id': 239, 'post_enable': 0, 'last_post_id': '1886501259601174542', 'last_post_time': '2025-02-04 04:45:24', 'reply_account_id': 239, 'reply_enable': 0, 'last_reply_id': '1886385085647040800', 'last_reply_time': '2025-02-03 21:03:46', 'monomane_account_id': '239', 'monomane_enable': 1, 'last_monomane_id': '1886498846538338658', 'last_monomane_time': '2025-02-04 04:35:49'}
#tweet_data={'text': 'テストツイート6', 'author_id': '1688693290630369284', 'edit_history_tweet_ids': ['1886501614158238016'], 'id': '1886501614158238016', 'created_at': '2025-02-03T19:46:48.000Z'}
##response = "Response(data={'text': 'あ', 'id': '1886524389145108625', 'edit_history_tweet_ids': ['1886524389145108625']}, includes={}, errors=[], meta={})"
#response={'edit_history_tweet_ids': ['1886501674849853944'], 'id': '1886501674849853944', 'text': 'テストツイート6'}
#insert_tweet_history_monomane(search_row , tweet_data , response)
#sys.exit(0)

#outputLog(args)

result1 = False
result2 = False
contents1 = None
contents2 = None

outputLog(" ")
outputLog("----- 指示受信 -----")
outputLog(args)

if mode ==  "check_refresh":
    outputLog("check_refresh")
    proc_update_refresh_token()
    sys.exit(0)

if mode ==  "update_profiles":
    outputLog("update_profiles")
    update_profile_image()
    sys.exit(0)

elif mode == "get_search_history":
    result1 , list1 = get_search_history("post")
    outputLog(list1)
    sys.exit(0)
elif mode == "init_check_tweet_account_master":
    init_check_tweet_account_master_by_search_list()
    sys.exit(0)

# 認証情報を取得
credentials = get_account_master(account_id)

if credentials:
    if mode == "post":
        if media_type != '':
            result1 , contents1 = proc_post_v10a(credentials , comment_id , media_type , media_id , tweet_id )               
        else:
            result1 , contents1 = proc_post_v2(credentials , comment_id , "" )               
    elif mode == "monomane":
        result1 , contents1 = proc_monomane_v1(credentials , tweet_id)
    elif mode == "reply":
        result1 , contents1 = proc_post_v2(credentials , comment_id , tweet_id )               
#        result1 , contents1 = True , "" #未実装
    elif mode == "repost":
        result1 , contents1 = proc_repost_v2(credentials, tweet_id)
    elif mode == "like":
        result1 , contents1 = proc_like_v2(credentials, tweet_id)
    elif mode == "jap_like":
        if not tweet_name:  # None または空文字列のときにTrue
            tweet_name = get_username_from_tweet_id_v2(credentials, tweet_id)
        result1 , contents1 = proc_like_jap(tweet_name, tweet_id , jap_api_key , quantity)
    elif mode == "jap_bookmark":
        if not tweet_name:  # None または空文字列のときにTrue
            tweet_name = get_username_from_tweet_id_v2(credentials, tweet_id)
        result1 , contents1 = proc_bookmark_jap(tweet_name, tweet_id , jap_api_key , quantity)
    elif mode == "jap_repost":
        if not tweet_name:  # None または空文字列のときにTrue
            tweet_name = get_username_from_tweet_id_v2(credentials, tweet_id)
        result1 , contents1 = proc_repost_jap(tweet_name, tweet_id , jap_api_key , quantity)
    elif mode == "search":
        result1 , contents1 = proc_search_v2(credentials)
    elif mode == "bookmark":
        result1 , contents1 = proc_bookmark_v2(credentials, tweet_id)
    elif mode == "follow":
#        result1 , contents1 = proc_following_v1(credentials, tweet_name)
        result1 , contents1 = proc_following_v2(credentials, tweet_name)
    elif mode == "unfollow":
        result1 , contents1 = proc_unfollowing_v2(credentials, tweet_name)

    elif mode == "refresh":
        result1 , contents1 , contents2= refresh_access_token(credentials)

    elif mode == "checkairep":
        result1 , contents1 = check_replies(credentials , get_account_master(account_id2))
    elif mode == "get_profile":
        proc_profile_image(account_id , credentials['login_id'])

    elif mode == "get_tweet":
        result1 , contents1 = proc_get_tweet(credentials)

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
    outputLog(f"エラーが発生しました: ID {credentials} の認証情報が見つかりませんでした。")
    sys.exit(1)


