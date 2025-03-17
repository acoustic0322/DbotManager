

import tweepy
import time
import random
import requests
import re 
import schedule 


from prompt import PROMPT1
from prompt import past_tweets_1
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
OPENAI_API_KEY = ""

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)



# 過去のツイート
# 過去のツイート

def generate_tweet(api_key,prompt):
    """Groqのmixtral-8x7b-32768を使ってツイートを生成する関数"""

    USEPROMPT = prompt
    # 過去のツイートをランダムに2つ選択
    random_past_tweets = random.sample(past_tweets_1, 2)
    # 改行で結合して、自然な文章にする
    random_past_tweets = "\n".join(random_past_tweets)


    # `messages` を先に定義する
    messages = [
        {"role": "system", "content": "あなたは20歳の女性です。普段の生活で感じたエッチな気持ちを、カジュアルなツイートとして1つのみ出力してください。詩的な表現は使わず、英語は禁止（すべての単語を日本語で記述すること）自然でツイートしてください。"},
        {"role": "user", "content": f"{USEPROMPT}\n\n以下は過去のツイートの一例です。参考にしてください。\n\n{random_past_tweets}"}
    ]
        
        # APIリクエスト用のデータ
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.7  # ランダム性
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
            "ちょっと、",
            "エロティックなツイート:",
            "秘Share",
            "🔞 本日のツイート:",
            "新しいツイート:",    
            "あなた",
            "どうしても安心できるんだ", "私らの間", "似通う", "になる",
            "（改行を入れた形で出力しています）"
        ]

        for phrase in unwanted_phrases:
            if content.startswith(phrase):
                content = content[len(phrase):].strip()

            # ハッシュタグ（`#〇〇`）を削除
        content = re.sub(r"#\S+", "", content).strip()
        content = re.sub(r"僕", "私", content)

        return content  #成功したらツイートを返す


    else:
        outputLog(f"⚠️ エラー: {response.status_code}, {response.text}")
        return f"エラー: {response.status_code}, {response.text}"




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
        outputLog(f"エラー: {response.status_code}, {response.text}")
        return tweet  # 修正できなかった場合は元のツイートを返す

def post_tweet(tweet_content):
    """指定した内容のツイートを投稿"""
    try:
        response = api.update_status(tweet_content)
        outputLog(f"ツイート成功: {response.id} - {tweet_content}")
        return response
    except tweepy.TweepyException as e:
        outputLog(f"ツイート失敗: {e}")
        return None





def generate_trend_tweet():
    """ChatGPT (OpenAI API) を使ってトレンドに沿ったツイートを生成して一つのみ生成してください"""

    prompt = f"""
    あなたはSNSの投稿を作成するAIです。
    以下の条件を満たすツイートを作成してください。

    - 最新のトレンドに沿った内容にする（トレンド: ）
    - 140文字以内
    - カジュアルな口調で、ユーザーが興味を持ちそうな内容
    - 日本語で自然な文章にする

    生成例:
    - WBC決勝戦がアツすぎる🔥 日本代表の活躍に感動した！
    - 新型iPhoneのデザインやばい… これ絶対買うやつ！📱

    では、トレンド【】に沿ったツイートを作成してください。ツイートの中身のみ出力してください。
    """


    messages = [
        {"role": "system", "content": "あなたはツイートを作成するAIです。"}, 
        {"role": "user", "content": prompt}
    ]


    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.7
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"].strip()

        # 余計な前置きを削除
        unwanted_phrases = [
            "今日のトレンド:",
            "今日のツイート:",
            "新しいツイート:",
            "話題のトピック:",
            "トレンドに関連したツイート:"
        ]

        for phrase in unwanted_phrases:
            if content.startswith(phrase):
                content = content[len(phrase):].strip()

        return content

    else:
        outputLog(f"ChatGPT API エラー: {response.status_code}")
        return "エラーが発生しました"




#定期的にツイートをLLMで実行
def auto_post_tweet():
    retry_count = 0
    while retry_count < 3:  # 最大再試行回数
        try:
             # 5回に1回の確率でハッシュタグを追加
            tweet_content = generate_tweet(GROQ_API_KEY,PROMPT1)
            refined_tweet = refine_tweet(OPENAI_API_KEY,tweet_content)

            if random.randint(1, 5) == 1:  # 1, 2, 3 4 5のうち 1 の場合に追加
                refined_tweet += "\n#裏垢女子 #DMでいいね" #改行してハッシュタグ

            post_tweet(refined_tweet)  # ツイート生成 & 投稿
            outputLog("ツイートを投稿しました: ", refined_tweet)
        except Exception as e:
            outputLog("ツイートの投稿に失敗しました: ", e)
            retry_count += 1
            time.sleep(300)  # 5分後に再試行
    
        # 再試行回数を超えた場合の処理
    outputLog("再試行回数を超えました。終了します。")
    return  # 再試行回数を超えたら終了

      
# スケジュール設定
def schedule_tasks():
    schedule.every().hour.do(auto_post_tweet)  # 1時間ごとにツイート
    while True:
        schedule.run_pending()
        time.sleep(10)  # 10秒ごとにスケジュールをチェック


def main():
    """ツイート自動投稿のメイン処理"""
    outputLog("ツイート自動投稿を開始します...")
    schedule_tasks()


#generate_trend_tweet()はmain処理にまだ追加していません。プロンプトの中身等を可変にすることでどんなツイートも作成することができるシステムです。組み込み方は今後考えていきたいと考えています。
