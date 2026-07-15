# proc_get_tweet をこの固定プロファイル版に
from get_x_cookies import get_x_cookies

import config
import os
from config import outputLog
import configparser

from GraphQL import get_tweets
from GraphQL import get_replies

#from mysql import get_tweet_profile_by_display_name
from mysql import get_tweet_profile_by_vps_id
from mysql import update_get_tweet_profile
from mysql import add_check_tweet_account_master_by_account_name
#from mysql import get_check_tweet_account_master_by_account_name
from mysql import get_check_tweet_account_masters_by_vps_id
from mysql import update_check_tweet_account_master
from mysql import get_check_tweet_account_list_by_user_id
from mysql import update_check_tweet_account_list
from mysql import get_vps_master_by_ip_address
from twitter_api_v2 import get_user_id
from datetime import datetime

from config import get_ip_address

def proc_get_tweet(credentials):

    # VPS IDの特定
    myIp = get_ip_address()
    vps_record = get_vps_master_by_ip_address(myIp)
    outputLog(f"vps_record={vps_record}")

    if vps_record is None:
        return
    vps_id = vps_record['id']

    outputLog(f"vps_id={vps_id}")

    profile_record = get_tweet_profile_by_vps_id(vps_id)
#    profile_record = get_tweet_profile_by_display_name("twitter")
    profile_path = profile_record['path']

    if profile_path is None or profile_path == '':
        profile_path = get_firefox_profile_path(profile_record['display_name'])
        outputLog(f"from os profile_path={profile_path}")
        profile_record['path'] = profile_path
        update_get_tweet_profile(profile_record)
    else:
        outputLog(f"from db profile_path={profile_path}")

#    vps_id = 0

    check_records = get_check_tweet_account_masters_by_vps_id(vps_id)

#    check_record = get_check_tweet_account_master_by_account_name(user_name)

    # 複数レコードをループ処理

    for check_record in check_records:
        outputLog(f"監視アカウント：{check_record['account_name']}")

    any_success = False
    errors = []

    for check_record in check_records:

        user_name = check_record['account_name']

        # レコードなしの場合はマスターに追加
        if check_record is None:
            add_check_tweet_account_master_by_account_name(user_name)
            check_record = get_check_tweet_account_master_by_account_name(user_name)

        user_id = check_record['user_id']

        if user_id is None or user_id == '':
            user_row = get_user_id(credentials,check_record['account_name'])

            if user_row[0] is None or user_row[0] == "":
                user_id = ''
                check_record['result'] = "ユーザーIDを取得できませんでした"
                check_record['user_id'] = user_id
                update_check_tweet_account_master(check_record)
                continue
            else:
                user_id = user_row[0]
                check_record['result'] = "ユーザーID 取得OK"
                check_record['user_id'] = user_id
                update_check_tweet_account_master(check_record)

            outputLog(f"from api user_id={user_id}")
        else:
            outputLog(f"from db user_id={user_id}")



        # 既存: 通常ツイート
        if check_record.get('tweet_enable', 0) == 1:
            outputLog(f"tweet_enable")
            tweets = get_tweets(profile_path, user_id, user_name)  # 既存関数（通常ツイのみ）
            if tweets:
                for tweet in tweets:
                    tweet['account_name'] = user_name
                    tweet['user_id'] = user_id
                    tweet['check_time'] = datetime.now()
                    update_check_tweet_account_list(tweet)
                    any_success = True

        # 追加: 自分が送ったリプ（outgoing）
#        if check_record.get('reply_enable', 0) == 1:
#            rows = get_items(profile_path, user_id, user_name, kind="replies_outgoing", limit=10)
#            if rows:
#                for tw in rows:
#                    tw['account_name'] = user_name
#                    tw['user_id'] = user_id
#                    tw['check_time'] = datetime.now()
#                    # tw['type'] は "reply"、tw['reply_to_tweet_id'] も入っている
#                    update_check_tweet_account_list(tw)
#                    any_success = True

        # 追加: 自分宛のリプ（incoming）
        if check_record.get('reply_enable', 0) == 1:
            outputLog("reply_enable")

            replies = get_replies(profile_path, user_id, user_name, kind="replies_incoming", limit=10)
            if replies:
                for reply in replies:

                    outputLog("reply=")
                    outputLog(reply)

                    reply['account_name'] = user_name
                    reply['user_id'] = user_id
                    reply['check_time'] = datetime.now()

                    # ★ 追加: リプ先の情報も保持
#                    reply['reply_to_tweet_id']   = reply.get("reply_to_tweet_id")
#                    reply['reply_to_user_id']    = reply.get("reply_to_user_id")
#                    reply['reply_to_screen_name']= reply.get("reply_to_screen_name")

                    # tw['type'] は "reply_to_me"
                    update_check_tweet_account_list(reply)
                    any_success = True

    # 最後に全体の成否を返す（1件でも成功していれば True）
    if errors:
        outputLog(f"[SUMMARY] Errors:{ errors}")

    return (any_success, "OK" if any_success else "NO_SUCCESS")

def get_firefox_profile_path(profile_name):
    """
    指定されたFirefoxプロファイル名からプロファイルフォルダの絶対パスを返す
    """
    ini_path = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'profiles.ini')
    
    if not os.path.exists(ini_path):
        raise FileNotFoundError(f"profiles.ini が見つかりません: {ini_path}")
    
    parser = configparser.ConfigParser()
    parser.read(ini_path, encoding="utf-8")
    
    for section in parser.sections():
        if section.startswith("Profile"):
            if parser.has_option(section, "Name") and parser.get(section, "Name") == profile_name:
                path = parser.get(section, "Path")
                is_relative = parser.get(section, "IsRelative", fallback="1") == "1"
                if is_relative:
                    return os.path.abspath(os.path.join(os.path.dirname(ini_path), path))
                else:
                    return os.path.abspath(path)
    
    raise ValueError(f"指定されたプロファイル名 '{profile_name}' が見つかりませんでした。")