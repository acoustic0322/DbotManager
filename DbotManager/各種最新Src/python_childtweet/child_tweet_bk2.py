#2025.01.31 処理順をID単位でまとめてlike,bookmark,repost,replyするように修正

import subprocess
from flask import Flask, request, jsonify
import threading
import random
import time

import datetime
import configparser

from mysql import get_random_comment_id

def get_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

app = Flask(__name__)

# config.iniを読み込み
config = configparser.ConfigParser()
config.read('config.ini')

# 待機時間の設定を取得
min_wait = float(config['WAIT_TIME']['min'])
max_wait = float(config['WAIT_TIME']['max'])

print(min_wait)
print(max_wait)


def background_task(tweet_id, like_list, bookmark_list, repost_list, reply_list, reptorep):
    all_account_ids = sorted(
        set(map(int, like_list)) |
        set(map(int, bookmark_list)) |
        set(map(int, repost_list)) |
        set(int(reply["AccountId"]) for reply in reply_list)
    )
    random.shuffle(all_account_ids)

    for account_id in all_account_ids:
        threading.Thread(target=account_task_bundle, args=(
            account_id, tweet_id, like_list, bookmark_list, repost_list, reply_list, reptorep
        )).start()


def account_task_bundle(account_id, tweet_id, like_list, bookmark_list, repost_list, reply_list, reptorep):
    if account_id in map(int, like_list):
        tweet_task(account_id, "like", tweet_id)
    if account_id in map(int, bookmark_list):
        tweet_task(account_id, "bookmark", tweet_id)
    if account_id in map(int, repost_list):
        tweet_task(account_id, "repost", tweet_id)
    for reply in reply_list:
        if int(reply["AccountId"]) == account_id:
            mode = "replytoreply" if reptorep else "reply"
            tweet_task(account_id, mode, tweet_id, int(reply["CommentId"]))

    wait_time = random.uniform(min_wait, max_wait)
    print(f"[{get_now()}] [account_id={account_id}] Sleeping {wait_time:.2f}s")
    time.sleep(wait_time)


def tweet_task(account_id, mode, tweet_id, comment_id=None):
    try:
        if mode == 'reply' or mode == 'replytoreply':
#            comment_id = get_random_comment_id(account_id , mode)
            # サブプロセスでPythonスクリプトを実行
            command = [
                "python", "tweet.py",
                f"account_id={account_id}",
                f"mode=reply",
                f"comment_id={comment_id}",
                f"tweet_id={tweet_id}",
                f"debug=False",
            ]
        else:
            # サブプロセスでPythonスクリプトを実行
            command = [
                "python", "tweet.py",
                f"account_id={account_id}",
                f"mode={mode}",
                f"tweet_id={tweet_id}",
                f"debug=True",
            ]
        result = subprocess.run(command, capture_output=True, text=True)

        print(command)

        # 実行結果を表示（必要に応じてログに記録）
        print(f"[{get_now()}] tweet_task account_id={account_id} mode={mode}")
        print(f"[{get_now()}] stdout: {result.stdout}")
        print(f"[{get_now()}] stderr: {result.stderr}")

    except Exception as e:
        print(f"Error while executing background task: {e}")

# カンマ区切りの文字列をリストに変換（空文字の場合は空リストにする）
def to_list(list_str):
    return list_str.split(",") if list_str else []

@app.route('/run', methods=['POST'])
def run_script():
    try:
        # リクエストのJSONデータを取得
        data = request.json
        tweet_id = data.get("tweet_id")

#        like_list = to_list(data.get("like_list"))
        like_list = data.get("like_list")

#        bookmark_list = to_list(data.get("bookmark_list"))
        bookmark_list = data.get("bookmark_list")

#        repost_list = to_list(data.get("repost_list"))
        repost_list = data.get("repost_list")

#        reply_list = to_list(data.get("reply_list"))
        reply_list = data.get("reply_list", [])

#        comment_list = to_list(data.get("comment_list"))
        reptorep = bool(data.get("rep_to_rep"))

        print("data",data)
#        print("reptorep",reptorep)
        
        # レスポンスを即座に返す
        response = {"status": "success", "message": "Request received"}

#        threading.Thread(target=background_task, args=(tweet_id, like_list, bookmark_list, repost_list, reply_list, comment_list, reptorep)).start()
        threading.Thread(target=background_task, args=(tweet_id, like_list, bookmark_list, repost_list, reply_list, reptorep)).start()

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def TestTweet():
    data = {'tweet_id': '1885665869982060885', 
    'like_list': '82,235,155,248,18,197,185,293,28,203,206,200,274,350,209,307,116,48,316,149,119,158,139,304,76,122,132,217,334,173,353,167,113,25,301,34,145,31,313,182,164,60,110,39,191,344,356,188,51,337,170,126,161,244,241,85,142,347,79,73,277,310,176,220,57,179,375,45,340,288,213,228,194,13,152,372,136,42,54,129,231', 
    'bookmark_list': '288,293,42,122,164,220,25,344,158,334,301,213,313,353,145,116,316,350,34,113,197,241,179,375,152,48,126,51,337,161,170,136,39,149,191,45,167,73,217,310,235,307,79,356,132,347,142,129,203,188,231,248,209,60,31,244,206,139,228,119,194,340,82,200,277,274,28,176,182,185,76,372,173,304,57,155,85,110,54,18,13', 
    'repost_list': '', 'reply_list': ''}

    # リクエストのJSONデータを取得
    #data = request.json
    tweet_id = data.get("tweet_id")
    like_list = to_list(data.get("like_list"))
    bookmark_list = to_list(data.get("bookmark_list"))
    repost_list = to_list(data.get("repost_list"))
    reply_list = to_list(data.get("reply_list"))

    background_task(tweet_id , like_list , bookmark_list , repost_list , reply_list)

#TestTweet()
if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=5000 )