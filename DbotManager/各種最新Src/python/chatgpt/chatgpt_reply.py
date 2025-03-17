import tweepy
import requests
import random
from prompt import REPLY_PROMPT1
from prompt import past_tweets_2
import json
import time
import re

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

def generate_reply(api_key,prompt,original_tweet):

    """Groqのmixtral-8x7b-32768を使ってツイートを生成する関数"""
    # ランダムなプロンプトを選択

    USEPROMPT = prompt


    # 過去のツイートをランダムに2つ選択
    random_past_tweets = random.sample(past_tweets_2, 2)
    # 改行で結合して、自然な文章にする
    random_past_tweets = "\n".join(random_past_tweets)

    messages = [
        {"role": "system", "content": "あなたはTwitterでお礼のリプライを作成するAIです。"},
        {"role": "user", "content": f"このツイートに対してリプライを作成してください: {original_tweet}"},
        {"role": "user", "content": f"{USEPROMPT}\n\n以下は過去のツイートの一例です。参考にしてください。\n\n{random_past_tweets}"}
    ]

        # APIリクエスト用のデータ
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.6  # ランダム性
    }

    #Groq の API にアクセスするための認証情報を送信
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"#APIに送るフォーマット指定
    }

        # APIリクエスト送信
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)

    # 結果を取得
    if response.status_code in [200, 201]:
        content = response.json()["choices"][0]["message"]["content"].strip()
        # 余計な前置きを削除（複数パターン対応）
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

        return content
    else:
        print(f"⚠️ エラー: {response.status_code}, {response.text}")
        return # 修正できなかった場合は元のツイートを返す
    

def refine_tweet(api_key,tweet):
    """ツイートを再度AIにかけて、英語を日本語に、詩的な表現を抑えて自然にする"""

    messages = [
        {"role": "system", "content": "あなたはツイートを修正するAIです。以下のルールを守ってツイートを自然な日本語に修正してください。\
            ・**英語の単語があれば、すべて自然な日本語に翻訳する。**\
            ・**詩的な表現を排除し、カジュアルな話し言葉に変換する。**\
            ・**140字以内に抑える。**\
            ・**敬語は禁止し、カジュアルな口調にする。**"},
        {"role": "user", "content": f"修正してください: {tweet}"}
    ]

    payload = {
        "model": "gpt-3.5-turbo", 
        "messages": messages,
        "max_tokens": 140,
        "temperature": 0.5 
    }

    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code in [200, 201]:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print(f"エラー: {response.status_code}, {response.text}")
        return tweet  # 修正できなかった場合は元のツイートを返す





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
                print("ツイートIDまたはユーザー名が取得できませんでした")
                return

            print(f"新しいリプライ: @{username}: {text}")  #ログ出力

            #ChatGPT で返信を生成
            reply_message = generate_reply(GROQ_API_KEY,REPLY_PROMPT1,text)
            refined_tweet = refine_tweet(OPENAI_API_KEY,reply_message)


            #Twitter に返信
            post_reply(tweet_id, username, refined_tweet)
            print(f"自動返信: {refined_tweet}")  #ログ出力

        except json.JSONDecodeError as e:
            print(f"JSONデコードエラー: {e}")
        except Exception as e:
            print(f"エラー発生: {str(e)}")


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

            print("リアルタイムリプライ監視を開始しました")
            stream.filter()  #ここでリアルタイム監視開始

        except Exception as e:
            print(f"ストリームエラー発生: {e}")
            print("5秒後に再接続します...")
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

        print(f"返信成功: {response.id} - {reply_text}")
        return response

    except tweepy.TweepyException as e:
        print(f"返信失敗: {e}")
        return None
    
def main():
    print("リプライ監視を開始します...")
    start_reply_stream()

# メイン処理
if __name__ == "__main__":
    print("リプライ監視を開始します...")
    start_reply_stream()
