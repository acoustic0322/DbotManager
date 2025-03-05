import requests
import tweepy
import json

# Twitter APIクライアントIDとクライアントシークレット
client_id = "YUZDcUhJclBPWmNTSTlSOFNSYUs6MTpjaQ"
client_secret = "IMX3NPYqOY7mrmKdskHnKrmfbxkic9BmflBCAtU-lWDGzkkH5w"
redirect_uri = "https://x.com"
refresh_token = "Ri1BZTJSLVZRdjk5OTZDV1hWaDIwcC1kdDNoRDUyNExaZGg1SjhLeEFsV19yOjE3MjE2OTA4MzYzMTU6MToxOmF0OjE"  # 最初に取得したリフレッシュトークンを入力

# ブックマークするツイートのID
tweet_id = "1234567890"  # ここに対象のツイートIDを入力

# リフレッシュトークンで新しいアクセストークンを取得する関数
def refresh_access_token(client_id, client_secret, refresh_token):
    token_url = "https://api.twitter.com/2/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_id": client_id,
    }
    
    response = requests.post(token_url, headers=headers, data=data, auth=(client_id, client_secret))
    if response.status_code == 200:
        response_data = response.json()
        return response_data["access_token"], response_data["refresh_token"]
    else:
        print(f"トークン取得エラー: {response.status_code}")
        print(response.json())
        return None, None

# 新しいアクセストークンでブックマークを試みる
access_token, refresh_token = refresh_access_token(client_id, client_secret, refresh_token)

if access_token:
    try:
        # tweepy.ClientでUser Contextのクライアントを作成
        client = tweepy.Client(bearer_token=access_token)
        
        # ブックマークを実行
        client.bookmark(tweet_id=tweet_id)
        print("ツイートをブックマークしました。")
    except tweepy.TweepyException as e:
        print("エラーが発生しました:", e)
else:
    print("アクセストークンの取得に失敗しました。")
