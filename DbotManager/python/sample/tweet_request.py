import requests

# Twitter APIのエンドポイント
url = "https://api.twitter.com/2/tweets"

# 取得済みのBearerトークン（アクセストークン）をセット
access_token = "1730390380116627456-Xe51uSHfnVr5YcwqBH7rDG3T44Trry"

# ヘッダーを設定
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# ツイート内容を設定
data = {
    "text": "Hello World!"
}

# POSTリクエストを送信してツイート
response = requests.post(url, headers=headers, json=data)

# レスポンスを確認
if response.status_code == 201:
    print("ツイートが成功しました!")
    print("ツイートの詳細:", response.json())
else:
    print(f"エラーが発生しました: {response.status_code}")
    print("エラーメッセージ:", response.json())
