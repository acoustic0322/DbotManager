#2025.01.31 処理順をID単位でまとめてlike,bookmark,repost,replyするように修正

import subprocess
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

def process_list(item_list, mode , tweet_id):
    # カンマ区切りの文字列をリストに変換
    items = item_list.split(",") if isinstance(item_list, str) else item_list
    for item in items:
        # 空の要素をスキップ
        if item.strip():
            print(f"Processing {mode}: {item.strip()}")
            tweet_task(item.strip(), mode, tweet_id)
        else:
            print(f"Skipping empty {mode} item.")

def background_task(tweet_id, like_list, bookmark_list, repost_list, reply_list):
    # 各リストを処理
    print(f"Processing tweet_id: {tweet_id}")

    # 全ての tweet_id を取得
    all_tweet_ids = sorted(set(like_list) | set(bookmark_list) | set(repost_list) | set(reply_list))

    for tweet_id in all_tweet_ids:
        print(f"Processing tweet_id: {tweet_id}")
        
        if tweet_id in like_list:
            process_list([tweet_id], "like", tweet_id)
        
        if tweet_id in bookmark_list:
            process_list([tweet_id], "bookmark", tweet_id)

        if tweet_id in repost_list:
            process_list([tweet_id], "repost", tweet_id)

        if tweet_id in reply_list:
            process_list([tweet_id], "reply", tweet_id)

def tweet_task(account_id, mode, tweet_id):
    try:
        # サブプロセスでPythonスクリプトを実行
        command = [
            "python", "tweet.py",
            f"account_id={account_id}",
            f"mode={mode}",
            f"tweet_id={tweet_id}",
            f"debug=False",
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        # 実行結果を表示（必要に応じてログに記録）
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
    except Exception as e:
        print(f"Error while executing background task: {e}")

@app.route('/run', methods=['POST'])
def run_script():
    try:
        # リクエストのJSONデータを取得
        data = request.json
        tweet_id = data.get("tweet_id")
        like_list = data.get("like_list")
        bookmark_list = data.get("bookmark_list")
        repost_list = data.get("repost_list")
        reply_list = data.get("reply_list")
        
        # レスポンスを即座に返す
        response = {"status": "success", "message": "Request received"}
        threading.Thread(target=background_task, args=(tweet_id, like_list, bookmark_list, repost_list, reply_list)).start()
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
