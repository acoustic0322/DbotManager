# search_chat.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  #新しいimport
from langchain_community.tools import DuckDuckGoSearchRun  #新しいimport
from langchain.agents import Tool, initialize_agent
from bs4 import BeautifulSoup

#from langchain.utilities import SerpAPIWrapper
from langchain_community.utilities import SerpAPIWrapper
#from langchain_community.utilities import SerpAPIWrapperimport requests

from config import outputLog


OPENAI_API_KEY = "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"
# --- 通貨ごとのURLマップ ---

# --- 通貨ごとの設定 ---
currency_config = {
    "USD/JPY": {
        "url": "https://finance.yahoo.co.jp/quote/USDJPY=FX",
        "class": "_FxPriceBoardMain__price_qgu28_61"
    },
    "EUR/JPY": {
        "url": "https://finance.yahoo.co.jp/quote/EURJPY=FX",
        "class": "_FxPriceBoardMain__price_qgu28_61"
    },
    "GBP/JPY": {
        "url": "https://finance.yahoo.co.jp/quote/GBPJPY=FX",
        "class": "_FxPriceBoardMain__price_qgu28_61"
    },
    "AUD/JPY": {
        "url": "https://finance.yahoo.co.jp/quote/AUDJPY=FX",
        "class": "_FxPriceBoardMain__price_qgu28_61"
    },
    "CAD/JPY": {
        "url": "https://finance.yahoo.co.jp/quote/CADJPY=FX",
        "class": "_FxPriceBoardMain__price_qgu28_61"
    },
    "CHF/JPY": {
        "url": "https://finance.yahoo.co.jp/quote/CHFJPY=FX",
        "class": "_FxPriceBoardMain__price_qgu28_61"
    },
}


def get_yahoo_trends():
    url = "https://search.yahoo.co.jp/realtime"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"取得失敗: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # トレンドワードのリストを格納する
    trends = []

    try:
        # <ol>内の<li>をすべて取得
        ol_tag = soup.find("ol")
        if not ol_tag:
            return "トレンドデータが見つかりませんでした。"

        li_tags = ol_tag.find_all("li", limit=10)
        for li in li_tags:
            word_tag = li.find("h1")
            if word_tag:
                trends.append(word_tag.text.strip())

    except Exception as e:
        return f"解析中にエラー: {e}"

    return trends


def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd,jpy"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        usd_price = data["bitcoin"]["usd"]
        jpy_price = data["bitcoin"]["jpy"]
        return f"BTC価格: ${usd_price} USD / ¥{jpy_price} JPY"
    except Exception as e:
        return f"BTC価格取得エラー: {e}"

#outputLog(get_bitcoin_price())


def get_gold_price_yahoo():
    url = "https://finance.yahoo.com/quote/BTC-USD/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # 金価格はこのクラスに入っていることが多い
        price_tag = soup.find("fin-streamer", {"data-symbol": "GC=F", "data-field": "regularMarketPrice"})

        if price_tag:
            return f"金価格（GC=F先物）: {price_tag.text.strip()} USD"
        else:
            return "金価格が見つかりませんでした。"

    except Exception as e:
        return f"金価格取得エラー: {e}"


# --- 為替取得関数 ---
def get_currency_bid_rate(currency_code: str) -> str:
    config = currency_config.get(currency_code)
    headers = {"User-Agent": "Mozilla/5.0"}

    if not config:
        return f"{currency_code} は未対応の通貨ペアです。"

    try:
        r = requests.get(config["url"], headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        price_tag = soup.find("span", class_=config["class"])

        if price_tag:
            return f"{currency_code} の現在の売値は {price_tag.text.strip()} 円です。"
        else:
            return f"{currency_code} の価格情報が見つかりませんでした。"
    except Exception as e:
        return f"{currency_code} のレート取得中にエラーが発生しました: {str(e)}"

# --- Toolリストを作る関数 ---
def create_tools():
    tools = [
        Tool(
            name="為替レート取得",
            func=lambda input_text: get_currency_bid_rate(input_text.strip()),
            description="為替レート（USD/JPY, EUR/JPY など）をYahooファイナンスから取得します。通貨ペア名を入力してください。"
        ),
    ]
    return tools


# --- LLM（GPTモデル）を作る関数 ---
def create_llm(openai_api_key: str):
    llm = ChatOpenAI(
        model="gpt-4-turbo",
        openai_api_key=openai_api_key,
        temperature=0.5,
        max_tokens=512,
    )
    return llm


# --- エージェントを作る関数 ---
def create_agent(openai_api_key: str):
    tools = create_tools()
    llm = create_llm(openai_api_key)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        agent_kwargs={
            "prefix": "あなたは日本語で自然に返答する有能なツール活用エージェントです。"
        }
    )

    return agent


# --- mainA 修正版（複数通貨対応） ---
def get_tweet_text_from_yahoo_pair(open_ai_api_key, prompt, target_currency = "USD/JPY"):
    # 対象通貨をここで指定（必要に応じて "EUR/JPY" などに変更可能。他の通貨も可能です。）

	#USD/JPY,EUR/JPY,GBP/JPY,AUD/JPY,CAD/JPY,CHF/JPY
#    target_currency = "GBP/JPY"

    # 設定に含まれているかチェック
    config = currency_config.get(target_currency)
    if not config:
        outputLog(f"{target_currency} は currency_config に存在しません。")
        return False , ""

    # --- レート取得 ---
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(config["url"], headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        price_tag = soup.find("span", class_=config["class"])

        if price_tag:
            rate_info = f"{target_currency} の現在の売値は {price_tag.text.strip()} 円です。"
        else:
            rate_info = f"{target_currency} の価格情報が見つかりませんでした。"

    except Exception as e:
        rate_info = f"{target_currency} のレート取得中にエラーが発生しました: {str(e)}"

    # --- プロンプト生成とGPT呼び出し ---
#    prompt = f"""
#以下の情報を元に、X（旧Twitter）に投稿するような自然で短いツイートを日本語で1つ作成してください。
#今のリアルタイムでの値段を含めてお願いします。
#140文字以内で、カジュアルに。
#為替情報: 「{rate_info}」
#"""
    try:

        prompt = prompt + f"""
        為替情報: 「{rate_info}」
        """

        llm = create_llm(open_ai_api_key)
        result = llm.invoke(prompt)
        outputLog(f"\n💱 {target_currency} のツイート:")
        outputLog(result.content)
        return True , result.content
    except Exception as e:
        outputLog(f"{target_currency} のツイート生成中にエラー: {e}")
        return False , f"{target_currency} のツイート生成中にエラー: {e}"


def get_tweet_text_from_yahoo_trend(open_ai_api_key,prompt):
    trends = get_yahoo_trends()
    if not trends or isinstance(trends, str):
        outputLog(f"トレンド取得失敗: {trends}")
        return

    # トレンドの中からランダムに1つ選ぶ（または1位でも可）
    selected = trends[0]  # トップ1位を使用

#    prompt = f"""
#以下のトレンドワードを使って、X（旧Twitter）に投稿するような自然なツイートを1つ日本語で作成してください。
#・140文字以内
#・話題性を活かしてインパクトのあるカジュアルな文にしてください
#・絵文字を1〜2個入れてもOKです
#
#トレンドワード: 「{selected}」
#"""
    prompt = prompt + f"""
    トレンドワード: 「{selected}」
    """

    try:
        llm = create_llm(open_ai_api_key)
        result = llm.invoke(prompt)
        outputLog(f"\n📈 トレンド: {selected}")
        outputLog(f"{result.content}")
        return True,  result.content
    except Exception as e:
        outputLog(f"エラー: {e}")
        return False , f"エラー: {e}"


# --- メインC（ゴールド価格ツイート） ---
def get_tweet_text_from_yahoo_gold(open_ai_api_key, prompt):
    gold_info = get_gold_price_yahoo()

#    prompt = f"""
#以下の情報をもとに、金価格に関するX（旧Twitter）投稿文を1つ生成してください。
#・リアルタイムの価格を含める
#・140文字以内
#・自然でカジュアルな日本語
#・トレーダーや一般人が興味を持つように
#
#金価格情報: 「{gold_info}」
#"""
    try:

        prompt = prompt + f"""
        金価格情報: 「{gold_info}」
        """

        llm = create_llm(open_ai_api_key)
        result = llm.invoke(prompt)
        outputLog(f"\n🥇 金価格ツイート:\n{result.content}")
        return True,  result.content
    except Exception as e:
        outputLog(f"エラー: {e}")
        return False , f"エラー: {e}"

# --- メインD（BTC価格ツイート） ---
def get_tweet_text_from_yahoo_btc(open_ai_api_key, prompt):
    btc_info = get_bitcoin_price()

#    prompt = f"""
#以下の情報をもとに、ビットコインに関するX（旧Twitter）投稿文を1つ生成してください。
#・リアルタイムの価格を含める
#・140文字以内
#・自然でカジュアルな日本語
#・仮想通貨に興味ある人が食いつくように
#
#BTC価格情報: 「{btc_info}」
#"""
    try:
        prompt = prompt + f"""
        BTC価格情報: 「{btc_info}」
        """
        llm = create_llm(open_ai_api_key)
        result = llm.invoke(prompt)
        outputLog(f"\n₿ ビットコイン価格ツイート:\n{result.content}")
        return True,  result.content
    except Exception as e:
        outputLog(f"エラー: {e}")
        return False , f"エラー: {e}"


if __name__ == "__main__":
#    get_tweet_text_from_yahoo_pair(OPENAI_API_KEY)
#    get_tweet_text_from_yahoo_trend(OPENAI_API_KEY)
#    get_tweet_text_from_yahoo_gold(OPENAI_API_KEY)
    get_tweet_text_from_yahoo_btc(OPENAI_API_KEY)
#    mainB()


