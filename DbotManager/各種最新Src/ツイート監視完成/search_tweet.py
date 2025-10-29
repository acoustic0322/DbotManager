# -*- coding: utf-8 -*-
import os
import time
from pathlib import Path
from typing import List, Optional, Tuple, Set
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# DBOT用追加 
import config
import os
from config import outputLog
import configparser

from config import get_ip_address
from mysql import get_vps_master_by_ip_address
from mysql import get_check_tweet_account_masters_by_vps_id
from mysql import add_check_tweet_account_master_by_account_name
#from twitter_api_v2 import get_user_id
from mysql import update_check_tweet_account_master
from mysql import update_check_tweet_account_list
from mysql import get_account_master
from mysql import get_tweet_profile_by_vps_id
from datetime import datetime, timedelta

from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict
import re

RESULTS_TXT = Path("results.txt")
HEADLESS_MODE = False
WAIT_TIMEOUT = 15
MAX_TWEETS_PER_USER = 5  # 各アカウントで取得する最大ツイート数

def normalize(text: str) -> str:
    return text.strip().replace("　", "").replace("\n", "").replace("\r", "").replace(" ", "")

def read_lines(path: Path) -> List[str]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    return [line.strip().strip("@") for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]

def chunk_list(lst: List[str], chunk_size: int) -> List[List[str]]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def find_existing_profiles(profiles_path: Path) -> List[Path]:
    return [Path(p) for p in read_lines(profiles_path) if Path(p).exists()]

def open_firefox_with_profile(profile_path: Path, headless: bool = False):
    opts = FirefoxOptions()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("-profile")
    opts.add_argument(str(profile_path))
    opts.add_argument("-no-remote")
    opts.add_argument("-new-instance")
    service = FirefoxService()
    return webdriver.Firefox(service=service, options=opts)

def append_result(username: str, tweet_time: str, tweet_text: str, tweet_url: str):
    try:
        with RESULTS_TXT.open("a", encoding="utf-8") as f:
            f.write(f"@{username}\n📅 {tweet_time}\n📝 {normalize(tweet_text)}\n🔗 {tweet_url}\n\n")
    except Exception as e:
        outputLog(f"[ERR] 書き込み失敗: {e}")


def load_existing_tweet_keys(path: Path) -> Set[Tuple[str, str]]:
    if not path.exists():
        return set()
    lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    keys = set()
    current_time = ""
    current_text = ""
    for line in lines:
        if line.startswith("📅"):
            current_time = line[2:].strip()
        elif line.startswith("📝"):
            current_text = normalize(line[2:].strip())
            keys.add((current_time, current_text))
    return keys

def proc_get_tweet(credentials):

    # VPS IDの特定
    myIp = get_ip_address()

    # debug
#    myIp = "192.168.1.101"

    vps_record = get_vps_master_by_ip_address(myIp)
    outputLog(f"vps_record={vps_record}")

    if vps_record is None:
        return
    vps_id = vps_record['id']
    outputLog(f"vps_id={vps_id}")

    profile_record = get_tweet_profile_by_vps_id(vps_id)
    profile_path = profile_record['path']
    check_records = get_check_tweet_account_masters_by_vps_id(vps_id)        

    # 複数レコードをループ処理
    for check_record in check_records:
        outputLog(f"監視アカウント：{check_record['account_name']}")

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

        tweet_enable = check_record.get('tweet_enable', 0)
        reply_enable = check_record.get('reply_enable', 0)

        # 既存: 通常ツイート
        if tweet_enable == 1 or reply_enable == 1:
            check_tweets(profile_path, user_name, user_id , tweet_enable , reply_enable)  # 既存関数（通常ツイのみ）

def get_user_id(credentials , username):

    access_token = credentials['bearer_token']

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/json"
    }

    # ユーザーIDを取得するURL
    url = f"https://api.twitter.com/2/users/by/username/{username}"

    outputLog(f"credentials['proxy_enable']  {credentials['proxy_enable'] }")    
    outputLog(f"credentials['proxy_url']  {credentials['proxy_url']}")    

    # POSTリクエストを送信
    if credentials['proxy_enable'] == True and credentials['proxy_url'] is not None:
        outputLog(f"proxy_url={credentials['proxy_url']}")
        proxies = {
            "http": credentials['proxy_url'],
            "https": credentials['proxy_url']
        }
#        response = requests.get(url, headers=headers ,proxies=proxies)
        response = requests.get(url, headers=headers)
    else:
        outputLog(f"proxy_url None")
        response = requests.get(url, headers=headers)

#    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()

        # "data" がない場合（ユーザーが存在しない）
        if "data" not in user_data:
            error_msg = user_data.get("errors", [{"detail": "ユーザーが見つかりません。"}])[0].get("detail")
            outputLog(f"get_user_idエラー: {error_msg}")
            return None, False, error_msg

        user_id = user_data["data"]["id"]
        outputLog(f"get_user_id {username}のユーザーID: {user_id}")
        return user_id , True , None
    else:
        outputLog(f"get_user_idエラー: {response.status_code}, {response.text}")
        return None , False , response.text

def check_tweets(profile_path, user_name, user_id , tweet_enable , reply_enable):

    outputLog(f"[INFO] プロファイル切替: {profile_path}")

    try:
        url = f"https://x.com/{user_name}"
        outputLog(f"[INFO] 移動中: {url}")
        # Firefox起動
        driver = open_firefox_with_profile(profile_path, headless=HEADLESS_MODE)
        driver.get(url)
        time.sleep(3)

        try:
            #最新ツイートの検索
            tweets = get_latest_tweets_info_scroll(driver, user_name, user_id)

            if tweets:
                for tweet in tweets:

                    # ツイート検索有効時のみDBに反映
                    if tweet_enable == 1:
                        tweet['account_name'] = user_name
                        tweet['user_id'] = user_id
                        tweet['check_time'] = datetime.now()
                        update_check_tweet_account_list(tweet)
                        any_success = True   

                    # リプ検索有効時
                    if reply_enable == 1:

                        # ツイートに対するリプを取得
                        replies = get_replies_to_my_post_scroll(driver, user_name, tweet['tweet_id'], user_id)

                        # リプをDBに反映
                        if replies:
                            for reply in replies:
                                reply['account_name'] = user_name
                                reply['user_id'] = user_id
                                reply['check_time'] = datetime.now()
                                update_check_tweet_account_list(reply)
                                any_success = True   

            else:     
                outputLog(f"[WARN] @{user_name} のツイートが取得できませんでした")
        except Exception as e:
            outputLog(f"[ERR] @{user_name} エラー: {e}")

        driver.quit()
    except Exception as e:
        outputLog(f"[ERR] Firefox起動失敗: {e}")

def get_latest_tweets_info_scroll(driver, username: str, user_id: str, limit: int = MAX_TWEETS_PER_USER) -> List[dict]:
    tweets = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pause = 2  # 秒

    while True:
        articles = driver.find_elements(By.XPATH, "//article")
        for article in articles[len(tweets):]:  # すでに処理済みのものを除く
            try:
                time_el = article.find_element(By.XPATH, ".//time")
                tweet_time_str = time_el.get_attribute("datetime")
                tweet_time_utc = datetime.fromisoformat(tweet_time_str.replace("Z", "+00:00"))
                tweet_time_jst = tweet_time_utc + timedelta(hours=9)

                text_el = article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                tweet_text = text_el.text.strip()

                link_el = article.find_element(By.XPATH, f".//a[contains(@href, '/{username}/status/')]")
                href = link_el.get_attribute("href")
                tweet_id = href.split("/")[-1]

                if any(t["tweet_id"] == tweet_id for t in tweets):
                    continue

                tweets.append({
                    "tweet_id": tweet_id,
                    "text": tweet_text,
                    "created_at_raw": tweet_time_str,
                    "created_at_utc": tweet_time_utc.isoformat(),
                    "created_at_jst": tweet_time_jst.isoformat(),
                    "user_id": user_id,
                    "check_time": datetime.now().isoformat(),
                    "type": "tweet",
                    "reply_to_tweet_id": ""
                })

                if len(tweets) >= limit:
                    return tweets

            except NoSuchElementException:
                continue

        # --- スクロールして追加ツイートを読み込む ---
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # もう読み込めない
        last_height = new_height

    return tweets

def get_replies_to_my_post_scroll(driver, username: str, tweet_id: str, user_id: str, limit: int = 0) -> List[Dict]:
    """
    自分のポスト(tweet_id)に対する他ユーザーのリプライをできるだけ多く取得する
    limit=0 の場合は上限なし（読み込めるまで）
    """
    replies = []
    url = f"https://x.com/{username}/status/{tweet_id}"
    outputLog(f"[INFO] リプライ取得開始: {url}")

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//article")))

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_pause = 2
        same_count = 0

        while True:
            articles = driver.find_elements(By.XPATH, "//article")
            for i, article in enumerate(articles):
                try:
                    # --- 投稿者名 ---
                    name_el = article.find_element(By.XPATH, ".//div[@dir='ltr']//span")
                    author_name = name_el.text.strip().replace("@", "")
                    if author_name.lower() == username.lower():
                        continue

                    # --- 本文 ---
                    text_el = article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                    tweet_text = text_el.text.strip()

                    # --- 投稿日時 ---
                    time_el = article.find_element(By.XPATH, ".//time")
                    tweet_time_str = time_el.get_attribute("datetime")
                    tweet_time_utc = datetime.fromisoformat(tweet_time_str.replace("Z", "+00:00"))
                    tweet_time_jst = tweet_time_utc + timedelta(hours=9)

                    # --- URLとID ---

                    link_el = article.find_element(By.XPATH, ".//a[contains(@href, '/status/')]")
                    href = link_el.get_attribute("href")

                    # 写真(tweetID/photo/1)を除外する
                    match = re.search(r"/status/(\d+)", href)
                    if not match:
                        continue  # ツイートURLじゃない

                    outputLog(f"href:{href}")

                    reply_id = href.split("/")[-1]
                    reply_id = match.group(1)                                     

                    # --- reply_to_screen_name を抽出 ---
                    # 形式: https://x.com/<screen_name>/status/<tweet_id>
                    match = re.search(r"https://x\.com/([^/]+)/status/(\d{15,20})", href)
                    if not match:
                        continue
                    reply_to_screen_name = match.group(1)  # ← ここがPUwfoVoDyC8517になる

                    # 数字以外が混ざっていたら除外
                    if not reply_id.isdigit():
                        continue                    

                    # --- 重複チェック ---
                    if any(r["tweet_id"] == reply_id for r in replies):
                        continue

                    # ポストをリプライと判定しているケースがある。
                    # 暫定対策として、リプ先IDとツイートIDが一致している場合は除外
                    if reply_id == tweet_id:
                        continue

                    replies.append({
                        "tweet_id": reply_id,
                        "text": tweet_text,
                        "author": author_name,
                        "created_at_raw": tweet_time_str,
                        "created_at_utc": tweet_time_utc.isoformat(),
                        "created_at_jst": tweet_time_jst.isoformat(),
                        "reply_to_tweet_id": tweet_id,
                        "reply_to_screen_name": reply_to_screen_name,
                        "check_time": datetime.now().isoformat(),
                        "type": "reply_to_me"
                    })

                    outputLog(f"[{len(replies)}] @{author_name}: {tweet_text[:50]}")

                    if limit and len(replies) >= limit:
                        return replies

                except NoSuchElementException:
                    continue

            # --- スクロールして追加読み込みを待つ ---
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")

            # ページの高さが変わらなければ、これ以上読み込めない
            if new_height == last_height:
                same_count += 1
                if same_count >= 3:  # 3回連続変化なしなら終了
                    break
            else:
                same_count = 0
                last_height = new_height

        return replies

    except TimeoutException:
        outputLog(f"[ERR] {url} の取得タイムアウト")
        return []

if __name__ == "__main__":
    # 認証情報を取得
    account_id = 1
    credentials = get_account_master(account_id)
    proc_get_tweet(credentials)
