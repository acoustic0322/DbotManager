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

PROFILES_TXT_PATH = Path("profiles.txt")
USERNAMES_TXT_PATH = Path("usernames.txt")
RESULTS_TXT = Path("results.txt")
CHUNK_SIZE = 5  # 1プロファイルで処理するアカウント数
HEADLESS_MODE = False
WAIT_TIMEOUT = 15
DELAY_BETWEEN_USERS = 3
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

def get_latest_tweets_info(driver, limit: int = MAX_TWEETS_PER_USER) -> List[Tuple[str, str]]:
    tweets = []
    try:
        articles = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.XPATH, "//article"))
        )
        for article in articles:
            try:
                time_el = article.find_element(By.XPATH, ".//time")
                tweet_time_str = time_el.get_attribute("datetime")
                tweet_time = datetime.fromisoformat(tweet_time_str.replace("Z", "+00:00"))

                text_el = article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                tweet_text = text_el.text.strip()

                tweets.append((tweet_time.isoformat(), tweet_text))

                if len(tweets) >= limit:
                    break
            except NoSuchElementException:
                continue
        return tweets
    except TimeoutException as e:
        print(f"[ERR] ツイート取得タイムアウト: {e}")
        return []


def get_latest_tweet_info(driver) -> Optional[Tuple[str, str]]:
    try:
        articles = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_all_elements_located((By.XPATH, "//article"))
        )
        latest_time = None
        latest_text = None
        for article in articles:
            try:
                time_el = article.find_element(By.XPATH, ".//time")
                tweet_time_str = time_el.get_attribute("datetime")
                tweet_time = datetime.fromisoformat(tweet_time_str.replace("Z", "+00:00"))
                text_el = article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                tweet_text = text_el.text.strip()
                if latest_time is None or tweet_time > latest_time:
                    latest_time = tweet_time
                    latest_text = tweet_text
            except NoSuchElementException:
                continue
        if latest_time and latest_text:
            return latest_time.isoformat(), latest_text
        return None
    except TimeoutException as e:
        print(f"[ERR] ツイート取得タイムアウト: {e}")
        return None

def append_result(username: str, tweet_time: str, tweet_text: str):
    try:
        with RESULTS_TXT.open("a", encoding="utf-8") as f:
            f.write(f"@{username}\n📅 {tweet_time}\n📝 {normalize(tweet_text)}\n\n")
    except Exception as e:
        print(f"[ERR] 書き込み失敗: {e}")

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

def process_chunk(driver, usernames: List[str], processed_keys: Set[Tuple[str, str]]):
    for uname in usernames:
        url = f"https://x.com/{uname}"
        print(f"[INFO] 移動中: {url}")
        try:
            driver.get(url)
            time.sleep(3)

            results = get_latest_tweets_info(driver)
            if not results:
                print(f"[WARN] @{uname} のツイートが取得できませんでした")
                continue

            for tweet_time, tweet_text in results:
                tweet_key = (tweet_time, normalize(tweet_text))
                if tweet_key in processed_keys:
                    print(f"[SKIP] @{uname} のツイートは既に記録済み: {tweet_time}")
                    continue

                print(f"[TWEET] @{uname}")
                print(f"  📅 {tweet_time}")
                print(f"  📝 {tweet_text}")
                append_result(uname, tweet_time, tweet_text)
                processed_keys.add(tweet_key)

#            result = get_latest_tweet_info(driver)
#            if result:
#                tweet_time, tweet_text = result
#                tweet_key = (tweet_time, normalize(tweet_text))
#                if tweet_key in processed_keys:
#                    print(f"[SKIP] @{uname} は既に記録済み")
#                    continue
#                print(f"[TWEET] @{uname}")
#                print(f"  📅 {tweet_time}")
#                print(f"  📝 {tweet_text}")
#                append_result(uname, tweet_time, tweet_text)
#                processed_keys.add(tweet_key)
#            else:
#                print(f"[WARN] @{uname} の最新ツイート取得失敗")
        except Exception as e:
            print(f"[ERR] @{uname} エラー: {e}")
        time.sleep(DELAY_BETWEEN_USERS)

def main():
    profiles = find_existing_profiles(PROFILES_TXT_PATH)
    if not profiles:
        print("[ERR] 有効なFirefoxプロファイルが見つかりません")
        return

    if not USERNAMES_TXT_PATH.exists():
        print("[ERR] usernames.txt が見つかりません")
        return

    usernames = read_lines(USERNAMES_TXT_PATH)
    if not usernames:
        print("[ERR] 監視対象ユーザーが空です")
        return

    chunks = chunk_list(usernames, CHUNK_SIZE)
    processed_keys = load_existing_tweet_keys(RESULTS_TXT)

    for i, chunk in enumerate(chunks):
        if i >= len(profiles):
            print(f"[WARN] プロファイルが不足しています。必要数: {len(chunks)} / 用意: {len(profiles)}")
            break
        profile_path = profiles[i]
        print(f"[INFO] プロファイル切替: {profile_path}")
        try:
            driver = open_firefox_with_profile(profile_path, headless=HEADLESS_MODE)
            process_chunk(driver, chunk, processed_keys)
            driver.quit()
        except Exception as e:
            print(f"[ERR] Firefox起動失敗: {e}")

    print("[INFO] 全処理完了")

if __name__ == "__main__":
    main()
