import tweepy
import requests
import random
from prompt import REPLY_PROMPT1_FIX1
from prompt import REPLY_PROMPT1_FIX2
from prompt import REPLY_PROMPT1_FREE

from prompt import past_tweets_2

from prompt import payload_generate_tweet
from prompt import payload_generate_reply
from prompt import payload_refine_tweet
from prompt import payload_generate_trend_tweet

import json
import time
import re

from config import outputLog
#config.debug = False


# Twitter API 認証
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
BEARER_TOKEN = ""
TWITTER_USERNAME = ""

GROQ_API_KEY = ""
OPENAI_API_KEY = "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"


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)




def call_api_with_retry(url, payload, headers, retries=5, delay=2):
    """503エラー時に指数バックオフでリトライするAPI呼び出し関数"""
    for attempt in range(retries):
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:  # 成功
            return response.json()

        elif response.status_code == 503:  # サーバー負荷エラー
            wait_time = delay * (2 ** attempt)  # 2, 4, 8, 16秒...
            print(f"503エラー発生: (試行 {attempt+1}/{retries}) - {wait_time}秒後に再試行")
            time.sleep(wait_time)

        else:  # その他のエラーは即終了
            print(f"APIエラー: {response.status_code}, {response.text}")
            break

    print("最大リトライ回数を超えました。")
    return None

def generate_reply(open_ai_api_key, prompt, past_tweets, original_tweet):
    """OpenAI GPTで自然なツイートリプライを生成する関数"""


    USEPROMPT = prompt


    # 過去のツイートをランダムに2つ選択
    random_past_tweets = random.sample(past_tweets, 2)
    # 改行で結合して、自然な文章にする
    random_past_tweets = "\n".join(random_past_tweets)

    payload = {
        "model": "gpt-3.5-turbo",  # または "gpt-4"
        "messages": [
            {"role": "system", "content": "あなたはTwitterで自然な日本語のリプライを作成するAIです。以下のルールに従ってください：\
                ・英語表現はすべて自然な日本語に翻訳する\
                ・詩的すぎる表現は避ける\
                ・カジュアルでフレンドリーな口調\
                ・140文字以内"},
            {"role": "user", "content": f"このツイートに対して返信を作ってください: {original_tweet}"},
            {"role": "user", "content": f"{USEPROMPT}\n\n以下は過去のツイートの一例です。参考にしてください：\n{random_past_tweets}"}
        ],
        "temperature": 0.7
    }



    headers = {
        "Authorization": f"Bearer {open_ai_api_key}",
        "Content-Type": "application/json"
    }

    url = "https://api.openai.com/v1/chat/completions"


    # APIリクエスト（503エラー時は自動リトライ）
    response_data = call_api_with_retry(url, payload_generate_reply, headers)

    if response_data:
        content = response_data["choices"][0]["message"]["content"].strip()

        # 余計な前置きを削除
        unwanted_phrases = [
            "あなたのために、新しいツイートを作成します。",
            "あなたのために、新しいえっちなツイートを作成します。",
            "今日のえっちなツイート:",
            "今日のツイート:",
            "本日のツイート:",
            "えっちなツイート:",
            "エロティックなツイート:",
            "🔞 本日のツイート:",
            "新しいツイート:"
        ]

        for phrase in unwanted_phrases:
            if content.startswith(phrase):
                content = content[len(phrase):].strip()

        # 余計な文字やフレーズを削除する
        content = re.sub(r"#\S+", "", content).strip()  # ハッシュタグを削除
        content = re.sub(r"僕", "私", content)  # 「僕」を「私」に変換
        content = re.sub(r'["\']', "", content).strip()  # ダブルクォートとシングルクォートを削除

        return True , content

    outputLog("最大リトライ回数を超えました。リプライ生成をスキップします。")
    return False , "リプライ生成エラー"

    



#AutoReplyStream クラス（リアルタイムリプライ監視 & 自動返信）
class AutoReplyStream(tweepy.StreamingClient):
    def __init__(self, bearer_token):
        super().__init__(bearer_token)
        
    def on_tweet(self, raw_data):
        """リプライを取得し、自動返信を実行"""
        try:
            tweet = json.loads(raw_data)

            #リプライであることを確認
            referenced_tweets = tweet.get("referenced_tweets", [])
            if not referenced_tweets or referenced_tweets[0].get("type") != "replied_to":
                return  # リプライでない場合はスキップ

            #ユーザー情報の取得（usernameを使う）
            tweet_id = tweet.get("id")
            username = tweet.get("includes", {}).get("users", [{}])[0].get("username", "")

            text = tweet.get("text", "")

            if not username or not tweet_id:
                outputLog("ツイートIDまたはユーザー名が取得できませんでした")
                return

            outputLog(f"新しいリプライ: @{username}: {text}")  #ログ出力

            #ChatGPT で返信を生成
            reply_message = generate_reply(
                GROQ_API_KEY,
                REPLY_PROMPT1_FIX1 + REPLY_PROMPT1_FREE + REPLY_PROMPT1_FIX2,
                past_tweets_2,
                text
                )

            #Twitter に返信
            post_reply(tweet_id, username, reply_message)
            outputLog(f"自動返信: {reply_message}")  #ログ出力

        except json.JSONDecodeError as e:
            outputLog(f"JSONデコードエラー: {e}")
        except Exception as e:
            outputLog(f"エラー発生: {str(e)}")


# `start_reply_stream()`（リプライ監視 & 自動返信を開始）
def start_reply_stream():
    """リアルタイムでリプライを監視し、自動返信"""
    while True:  #永続ループでエラー時に自動再接続
        try:
            stream = AutoReplyStream(BEARER_TOKEN)  #AutoReplyStream のインスタンス作成

            # 既存ルールを取得して削除
            existing_rules = stream.get_rules()
            if existing_rules and existing_rules.data:
                rule_ids = [rule.id for rule in existing_rules.data if rule.id]  # None の可能性を考慮
                if rule_ids:
                    stream.delete_rules(rule_ids)

            # 新しいルールを追加（自分宛のリプライを取得）
            stream.add_rules(tweepy.StreamRule(f"to:{TWITTER_USERNAME}"))

            outputLog("リアルタイムリプライ監視を開始しました")
            stream.filter()  #ここでリアルタイム監視開始

        except Exception as e:
            outputLog(f"ストリームエラー発生: {e}")
            outputLog("5秒後に再接続します...")
            time.sleep(5)  # 5秒待機して再接続
            continue  # **エラー発生時にループを再開**

            
def post_reply(tweet_id, username, message):
    """ツイートIDを指定してリプライを送信する"""
    try:
        #返信のテキストに `@username` を含める
        reply_text = f"@{username} {message}"

        #Twitter API を使ってリプライを送信
        response = api.update_status(
            status=reply_text,  # 返信内容
            in_reply_to_status_id=tweet_id,  # 返信対象のツイートID
            auto_populate_reply_metadata=True  # メンションを自動的に設定
        )

        outputLog(f"返信成功: {response.id} - {reply_text}")
        return response

    except tweepy.TweepyException as e:
        outputLog(f"返信失敗: {e}")
        return None
    
def main():
    outputLog("リプライ監視を開始します...")
    start_reply_stream()

# メイン処理
if __name__ == "__main__":
    outputLog("リプライ監視を開始します...")
    start_reply_stream()
