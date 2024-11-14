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

#args = sys.argv

#if len(args) < 3:
#    sys.exit()

# ファイルのパスを指定
#file_path = os.path.join(args[2],'key.txt')  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
#with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
#    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

#if len(lines) < 8:
#    sys.exit()


ck = "SBd4tiZXE2w65cquDEWHLuqHi"
cs = "K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC"
at = "880773299885625344-ydL3qpYkcOKmz4sats2Y08bgsm17up1"
ats = "R0KNblcAaGuxZNfqszFUDZ4Zgkn5fJm9K2KYBOcjcebnL"
bearer_token = "QlhlcFZLdHJOc3RYUUwxaFMyTDhiRlR6RFN6b01TVERPRGIyX1AxQVBTY1M2OjE3MzE1NjM4NTg0NjY6MTowOmF0OjE"
refresh_token = "aFd2M2VmaFM0RTR4Qm4tNVYySGw4UE5uY1V4aHgtUXdSbjJSRlNjWldRYjVjOjE3MzE1NjM4NTg0NjY6MToxOnJ0OjE"
client_id = "S0o0T2dOU3ZESDByR0ZTcW9vcE86MTpjaQ"
client_secret = "is6iQmgF4k29fEQiKX8TzEXGlThSg9Wo3pPt4Eu5UM6nB3QgBR"

bearer_token = "OHFDX1FrR1dRMDBqRk9JOVdvNHJqUkszYmtUNjdSNHk0c0ZydGlnQ3I2bWVuOjE3MzE2MTQwMzQ4Mzg6MToxOmF0OjE"
refresh_token = "Z0hJT3ZBYS1Hd3dKMTFPZmZObzJVaUlobnpRSTdNenV5MUtwVjVxTDU5c2VBOjE3MzE2MTQwMzQ4Mzg6MToxOnJ0OjE"


# # Twitter Developer Portalから取得したキーを設定
#ck = lines[0]
#cs = lines[1]
#at = lines[2]
#ats = lines[3]
#bearer_token = lines[4]
#refresh_token = lines[5]
#client_id = lines[6]
#client_secret = lines[7]

# ツイートのID
tweet_id = "1856811778942120181"#args[1]  # ここに対象のツイートのIDを入力してください

#proxy_url = args[3]
#if proxy_url!="":
#    # プロキシ設定がある場合のみ設定
#    proxies = {
#        "http": proxy_url,
#        "https": proxy_url
#    }

try:
    client = tweepy.Client(bearer_token=bearer_token, consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
#    if proxy_url!="":
#        client.session.proxies = proxies
    client.bookmark(tweet_id=tweet_id)
except:
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