import sys
import tweepy
import pyperclip
import os

def fetch_tokens(client_id,client_secret,auth_code):

    try:
        scopes = [
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access",
        "bookmark.read",
        "bookmark.write"
        ]

        # 事前にクライアントIDとシークレットを環境変数や別ファイルで管理
        auth = tweepy.OAuth2UserHandler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri='https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec',
        scope=scopes
        )

        # 認証URLを取得する
        authorization_url = auth.get_authorization_url()
#        print(f"右のURLにツイートしたいアカウントでアクセスする: {authorization_url}")
        print(f"以下のURLをクリップボードにコピーしました。ブラウザを開いてアクセスしてください: ")
        print(f"{authorization_url}")

        # クリップボードにコピー
        pyperclip.copy(authorization_url)

        # 認証後のコールバックURLからコードを取得し、アクセストークンを交換する
        code = input("ブラウザで認証後に表示されるコードを入力してください: ")
        os.system('cls')        

        token = auth.fetch_token(code)
        return token
    except Exception as e:
        print(f"Error fetching token: {e}")
        raise

if __name__ == "__main__":
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    auth_code = sys.argv[3]

    print(f"client_id={client_id}")
    print(f"client_secret={client_secret}")
    print(f"auth_code={auth_code}")

    tokens = fetch_tokens(client_id,client_secret,auth_code)
    print(f"Access Token: {tokens.get('access_token')}\nRefresh Token: {tokens.get('refresh_token')}")
