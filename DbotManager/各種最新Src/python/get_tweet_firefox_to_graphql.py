# proc_get_tweet をこの固定プロファイル版に
from get_x_cookies import get_x_cookies

import config
import os
from config import outputLog
import configparser

from GraphQL import get_tweet
from GraphQL import get_tweets

from mysql import get_tweet_profile_by_display_name
from mysql import update_get_tweet_profile
from mysql import add_check_tweet_account_master_by_account_name
from mysql import get_check_tweet_account_master_by_account_name
from mysql import update_check_tweet_account_master
from mysql import get_check_tweet_account_list_by_user_id
from mysql import update_check_tweet_account_list
from twitter_api_v2 import get_user_id

from datetime import datetime

# 先頭付近：固定したいプロファイル名をここで設定
PROFILE_NAME = "Profile 27"   # ← 好きなフォルダ名に変更可（例: "Default", "Profile 207" など）

def proc_get_tweet(credentials):

    record = get_tweet_profile_by_display_name("twitter")
    profile_path = record['path']

    if profile_path is None or profile_path == '':
        profile_path = get_firefox_profile_path("twitter")
        print("from os profile_path=",profile_path)
        record['path'] = profile_path
        update_get_tweet_profile(record)
    else:
        print("from db profile_path=",profile_path)

    user_name = "OnSounds"
#    user_name = "MANGA549764083"

    check_record = get_check_tweet_account_master_by_account_name(user_name)

    # レコードなしの場合はマスターに追加
    if check_record is None:
        add_check_tweet_account_master_by_account_name(user_name)
        check_record = get_check_tweet_account_master_by_account_name(user_name)

    user_id = check_record['user_id']


    if user_id is None or user_id == '':
        user_row = get_user_id(credentials,check_record['account_name'])

        if user_row[0] is None or user_row[0] == "":
            print("Twitter APIでユーザー名が見つかりませんでした")
            return

        user_id = user_row[0]
        print("from api user_id=",user_id)
        check_record['user_id'] = user_id
        update_check_tweet_account_master(check_record)
    else:
        print("from db user_id=",user_id)

    tweets = get_tweets(profile_path , user_id)
    if tweets is None:
        return False , ""

    for tweet in tweets:
        print(tweet["tweet_id"], tweet["text"], tweet["created_at_jst"])
        tweet['account_name'] = user_name
        tweet['user_id'] = user_id
        tweet['check_time'] = datetime.now()
        update_check_tweet_account_list(tweet)


#    ret = get_tweet(profile_path , user_id)
#    if ret is None:
#        return False , ""
#    ret['user_id'] = user_id
#    ret['check_time'] = datetime.now()
#    update_check_tweet_account_list(ret)

    return True , ""

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