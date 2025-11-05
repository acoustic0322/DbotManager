import tweepy
import time
import random
import requests
import re 
import schedule 

# 2025.10.15 コメントアウト
#from prompt import PROMPT1_FIX1
#from prompt import PROMPT1_FIX2
#from prompt import PROMPT1_FREE

from prompt import PROMPT1
from prompt import past_tweets_1


from prompt import payload_generate_tweet
from prompt import payload_generate_reply
from prompt import payload_refine_tweet
from prompt import payload_generate_trend_tweet


from config import outputLog
#config.debug = False

# Twitter API 認証
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
BEARER_TOKEN = ""
TWITTER_USERNAME = ""
OPENAI_API_KEY = ""

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


# 過去のツイート
def generate_tweet(GROQ_API_KEY,prompt,past_tweets):

    outputLog(past_tweets)


    """GPTを使ってツイートを生成する関数"""

    # --- 改行で分割してリスト化（空行除去＋strip()）---
    lines = [line.strip() for line in past_tweets.splitlines() if line.strip()]

    # --- 要素数が1以上ならランダムに1行選ぶ ---
    if len(lines) >= 1:
        random_past_tweets = random.sample(lines, 1)
    else:
        random_past_tweets = []

    # --- 改行で結合して自然な文章に（1行でもjoin()でOK）---
    random_past_tweets = "\n".join(random_past_tweets)

#    print("lines:", lines)
#    print("random_past_tweets:", random_past_tweets)    

    # `messages` を先に定義する
    payload_generate_tweet["messages"] = [ 
        {"role": "system", "content": "あなたは20歳の女性です。普段の生活で感じたエッチな気持ちを、カジュアルなツイートとして1つのみ出力してください。詩的な表現は使わず、英語は禁止（すべての単語を日本語で記述すること）自然でツイートしてください。"},
        {"role": "user", "content": f"{prompt}\n\n以下は過去のツイートの一例です。参考にしてください。\n\n{random_past_tweets}"}
    ]
        
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    url = "https://api.groq.com/openai/v1/chat/completions"
    response_data = call_api_with_retry(url, payload_generate_tweet, headers)

    ##########ここを追加しました
    response_data = call_api_with_retry(url, payload_generate_tweet, headers) 
    ##########ここを追加しました
    
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

        return True , content  # 成功したツイートを返す

    outputLog("ツイート生成に失敗しました。")
    return False , "ツイート生成エラー"




def post_tweet(tweet_content):
    """指定した内容のツイートを投稿"""
    try:
        response = api.update_status(tweet_content)
        outputLog(f"ツイート成功: {response.id} - {tweet_content}")
        return response
    except tweepy.TweepyException as e:
        outputLog(f"ツイート失敗: {e}")
        return None

def generate_trend_tweet(open_ai_api_key,prompt):
    """ChatGPT (OpenAI API) を使ってトレンドに沿ったツイートを生成して一つのみ生成してください"""

#    prompt = f"""
#    あなたはSNSの投稿を作成するAIです。
#    以下の条件を満たすツイートを作成してください。
#
#    - 最新のトレンドに沿った内容にする（トレンド: ）
#    - 140文字以内
#    - カジュアルな口調で、ユーザーが興味を持ちそうな内容
#    - 日本語で自然な文章にする
#
#    生成例:
#    - WBC決勝戦がアツすぎる🔥 日本代表の活躍に感動した！
#    - 新型iPhoneのデザインやばい… これ絶対買うやつ！📱
#
#    では、トレンド【】に沿ったツイートを作成してください。ツイートの中身のみ出力してください。
#    """

    payload_generate_trend_tweet["messages"] = [ 
        {"role": "system", "content": "あなたはツイートを作成するAIです。"}, 
        {"role": "user", "content": prompt}
    ]


    headers = {
        "Authorization": f"Bearer {open_ai_api_key}",
        "Content-Type": "application/json"
    }

    url = "https://api.openai.com/v1/chat/completions"

    # APIリクエスト（503エラー時は自動リトライ）
    response_data = call_api_with_retry(url, payload_generate_trend_tweet, headers)

    if response_data:
        content = response_data["choices"][0]["message"]["content"].strip()

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

        return True , content  # 成功した場合、ツイートを返す

    outputLog("最大リトライ回数を超えました。ツイート生成をスキップします。")
    return False , "エラーが発生しました"
    
#定期的にツイートをLLMで実行
def auto_post_tweet():
    retry_count = 0
    while retry_count < 3:  # 最大再試行回数
        try:
             # 5回に1回の確率でハッシュタグを追加
            tweet_content = generate_tweet(
                GROQ_API_KEY,
#                PROMPT1_FIX1 + PROMPT1_FREE + PROMPT1_FIX2,
                PROMPT1,
                past_tweets_1
                )

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
