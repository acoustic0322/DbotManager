# ライブラリ
import tweepy
import sys
import requests
import os
# リフレッシュトークンで新たなベアラトークンを取得
def refresh_access_token(client_id, client_secret, refresh_token):
    # ヘッダーを設定
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # データを設定
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_id': client_id,
    }

    # リクエストを送信
    response = requests.post(
        'https://api.twitter.com/2/oauth2/token',
        headers=headers,
        data=data,
        auth=(client_id, client_secret)
    )
    
    # レスポンスのステータスコードを確認
    if response.status_code != 200:
        # print(f"Error: {response.status_code}")
        # print(response.json())
        return None, None

    response_json = response.json()
    
    print(response_json)  # デバッグ用出力
    # print("access_token："+response_json.get('access_token'))
    # print("refresh_token："+response_json.get('refresh_token'))
    # input()
    
    return response_json.get('access_token'), response_json.get('refresh_token')


# # Twitter Developer Portalから取得したキーを設定
ck = "SBd4tiZXE2w65cquDEWHLuqHi"
cs = "K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC"
at = "1730390380116627456-Xe51uSHfnVr5YcwqBH7rDG3T44Trry"
ats = "rEa5y4BgUFgZdDxzAQRSsj2pqm0KsWN0WvkRkx9Dey3Fp"
bearer_token = "Ri1BZTJSLVZRdjk5OTZDV1hWaDIwcC1kdDNoRDUyNExaZGg1SjhLeEFsV19yOjE3MjE2OTA4MzYzMTU6MToxOmF0OjE"

refresh_token = "Sk1pTmdQNHpYZHBJMGpLRFpTTjRITjlQeHFWUlA1c0NRS1hqRnpOTjB4NDN4OjE3MzE2MTM0MTAxNDc6MTowOmFjOjE"
client_id = "S0o0T2dOU3ZESDByR0ZTcW9vcE86MTpjaQ"
client_secret = "is6iQmgF4k29fEQiKX8TzEXGlThSg9Wo3pPt4Eu5UM6nB3QgBR"
#client_id = "YUZDcUhJclBPWmNTSTlSOFNSYUs6MTpjaQ"
#client_secret = "IMX3NPYqOY7mrmKdskHnKrmfbxkic9BmflBCAtU-lWDGzkkH5w"

#https://twitter.com/i/oauth2/authorize?response_type=code&client_id=YUZDcUhJclBPWmNTSTlSOFNSYUs6MTpjaQ&redirect_uri=https://x.com&scope=tweet.read%20users.read%20tweet.write%20bookmark.read%20bookmark.write%20offline.access&state=state&code_challenge=challenge&code_challenge_method=plain
#Sk1pTmdQNHpYZHBJMGpLRFpTTjRITjlQeHFWUlA1c0NRS1hqRnpOTjB4NDN4OjE3MzE2MTM0MTAxNDc6MTowOmFjOjE


# ツイートのID
tweet_id = "1856523237208797221"  # ここに対象のツイートのIDを入力してください


try:
    client = tweepy.Client(bearer_token=bearer_token, consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
#    if proxy_url!="":
#        client.session.proxies = proxies
    client.bookmark(tweet_id=tweet_id)
except:
    print("bookmark exce")

    try:
        new_bearer_token,new_refresh_token = refresh_access_token(client_id,client_secret,refresh_token)
        print("new_bearer_token=",new_bearer_token)
        print("new_refresh_token=",new_refresh_token)

        if new_bearer_token != None and new_refresh_token != None:
            c = [ck,cs,at,ats,str(new_bearer_token),str(new_refresh_token),client_id,client_secret]
            d = "\n".join(c)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(d)
            # 認証情報を設定する
            client = tweepy.Client(bearer_token=str(new_bearer_token), consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
            if proxy_url!="":
                client.session.proxies = proxies
            client.bookmark(tweet_id=tweet_id)
    except:
        sys.exit()