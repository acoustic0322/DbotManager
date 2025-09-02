import os
import requests

#GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/models"

PREFERRED_MODELS = [
    "llama-3.3-70b-versatile",   # Meta最新・128K対応・高精度・多用途
    "llama3-70b-8192",           # Meta安定版・高精度
    "mixtral-8x7b-instruct",     # 高性能で安定、処理も早い
    "gemma2-9b-it",              # Google製、instruction特化・比較的安定
    "llama-3.1-8b-instant",      # 軽量・高速（精度はやや落ちる）
    "llama3-8b-8192",            # 軽量・安定（処理優先向け）
    "llama-guard-3-8b",          # モデレーション特化（特殊用途）
]

def select_available_model():
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    response = requests.get(GROQ_API_URL, headers=headers)
    available_models = [m["id"] for m in response.json().get("data", [])]

    for model in PREFERRED_MODELS:
        if model in available_models:
            print(model)
            return model
    raise Exception("使用可能なモデルが見つかりません。")


select_available_model()