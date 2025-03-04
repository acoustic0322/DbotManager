import tweepy
import json
import sys
import os

# ファイルのパスを指定
file_path = 'first_accesskey.txt'  # ここに実際のファイルパスを指定します

# ファイルを開いて内容を読み込み、行ごとに配列に格納
with open(file_path, 'r', encoding='utf-8') as file:  # UTF-8エンコーディングを使用
    lines = [line.strip() for line in file.readlines()]  # 行ごとに読み込み、リストに格納

if len(lines) < 4:
    sys.exit()

# # Twitter Developer Portalから取得したキーを設定
ck = lines[0]
cs = lines[1]
ci = lines[2]
cis = lines[3]

# 認証オブジェクトの作成
auth = tweepy.OAuthHandler(ck, cs)

# 認可URLの取得
redirect_url = auth.get_authorization_url()

print(f"右のURLにツイートしたいアカウントでアクセスする: {redirect_url}")

oauth_token = input("oauth_tokenを入力: ")
oauth_verifier = input("oauth_verifierを入力: ")
os.system('cls')

# アクセストークンとアクセストークンシークレットを取得
try:
    auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}
    auth.get_access_token(oauth_verifier)
    access_token = auth.access_token
    access_token_secret = auth.access_token_secret
    print("アクセストークン："+access_token)
    print("アクセスシークレットトークン："+access_token_secret)

    input("保存ができたらエンター")
    os.system('cls')
except Exception as e:
    print(f"エラー: {e}")
    input()

# スコープのリスト（できるだけ多く指定）
scopes = [
    "tweet.read",
    "tweet.write",
    "users.read",
    "offline.access",
    "bookmark.read",
    "bookmark.write"
]

auth = tweepy.OAuth2UserHandler(
    client_id=ci,
    client_secret=cis,
    redirect_uri='https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec',
    scope=scopes
)

# 認証URLを取得する
authorization_url = auth.get_authorization_url()
print(f"右のURLにツイートしたいアカウントでアクセスする: {authorization_url}")

# 認証後のコールバックURLからコードを取得し、アクセストークンを交換する
code = input("ブラウザで認証後に表示されるコードを入力してください: ")
os.system('cls')

try:
    token = auth.fetch_token(code)

    # アクセストークンとリフレッシュトークンを取得する
    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")
    # expires_in = token.get("expires_in")

    print(f"Bearer Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    # print(f"Expires In: {expires_in}")

    input("保存ができたらエンター")
except Exception as e:
    print(f"エラー: {e}")
    input()