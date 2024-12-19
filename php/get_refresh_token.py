import requests
import secrets
import hashlib
import base64
import webbrowser
import sys
import json

# === PKCE関連関数 ===
def generate_code_verifier():
    """ランダムなcode_verifierを生成"""
    return secrets.token_urlsafe(64)


def generate_code_challenge(verifier):
    """code_verifierからcode_challengeを生成"""
    hashed = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()


# === PKCEの準備 ===
client_id = "NkJGVEtCUkJkRzVIY0NOQTRQbk46MTpjaQ"
client_secret = "7vFoQq5VHKZ7IAsaC385cfQ5wp1yLBwkN07MWQhOsFZ_vxsMJU"
redirect_uri = "https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec"
access_token = "1717907051396071424-nqPoVOvy2z2BLIwHd7Mp39OrI3UgZY"

client_credentials = f"{client_id}:{client_secret}"
client_credentials_base64 = base64.b64encode(client_credentials.encode()).decode()

# PKCE用コード生成
code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

# === 認可コードを取得する ===
def get_url():
    """認可コードを取得"""
    auth_url = (
        "https://twitter.com/i/oauth2/authorize"
        "?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=tweet.read tweet.write offline.access"
        f"&code_challenge={code_challenge}"
        "&code_challenge_method=S256"
        "&state=your_state"  # 任意の文字列（CSRF対策）
    )

    return auth_url

# === 認可コードを取得する ===
def get_authorization_code():
    """認可コードを取得"""
    auth_url = (
        "https://twitter.com/i/oauth2/authorize"
        "?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=tweet.read tweet.write offline.access"
        f"&code_challenge={code_challenge}"
        "&code_challenge_method=S256"
        "&state=your_state"  # 任意の文字列（CSRF対策）
    )

    # 認可URLを開く
    print("以下のURLをブラウザで開いて認可を行ってください:")
    print(auth_url)
    webbrowser.open(auth_url)

    # リダイレクト後のURLを手動で入力
    redirect_response = input("リダイレクトされたURLを入力してください: ")
    # URLから認可コードを抽出
    authorization_code = redirect_response.split("code=")[-1].split("&")[0]

    print(authorization_code)


    return authorization_code


# === トークンを取得する ===
def fetch_tokens(authorization_code):
    """トークンを取得"""
    url = "https://api.twitter.com/2/oauth2/token"

#    headers = {
#        "Content-Type": "application/x-www-form-urlencoded",
#    }

    client_credentials = f"{client_id}:{client_secret}"
    client_credentials_base64 = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {client_credentials_base64}"
    }

    print(headers)

    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
        "client_id": client_id,

        "client_secret": client_secret,
    }

    print(data)

    response = requests.post(url, headers=headers, data=data)

    # レスポンスの内容を確認
    print("ステータスコード:", response.status_code)
    print("レスポンス内容:", response.text)

    try:
        if response.status_code == 200:
            tokens = response.json()
            print("アクセストークン:", tokens["access_token"])
            print("リフレッシュトークン:", tokens["refresh_token"])
            print("新しいアクセストークン:", tokens.get("access_token", "アクセストークンが返されません"))
#            return tokens
            return True
        else:
            print("エラー:", response.json())
#            return None
            return False
    except ValueError:
        print("レスポンスがJSON形式ではありません。")
        return False
#        return None

# === リフレッシュトークンを使用してアクセストークンを更新する ===
def refresh_access_token(refresh_token):
    """リフレッシュトークンでアクセストークンを更新"""
    url = "https://api.twitter.com/2/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {access_token}"  # 必須のAuthorizationヘッダー
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        print("新しいアクセストークン:", tokens["access_token"])
        print("新しいリフレッシュトークン:", tokens["refresh_token"])
#        return tokens
    else:
        print("エラー:", response.json())
#        return None


# === メイン処理 ===
if __name__ == "__main__":

    # 結果を格納する辞書
    result = {}

    mode = sys.argv[1]

    if mode == "get_url":
        client_id = sys.argv[2]
        client_secret = sys.argv[3]

#        print(get_url())
#        print("code_verifier=",code_verifier)
#        print("code_challenge=",code_challenge)

        result['url'] = get_url()
        result['code_verifier'] = code_verifier
        result['code_challenge'] = code_challenge        
        result['client_credentials'] = client_credentials_base64 

        # JSONとして出力
        print(json.dumps(result))

    elif mode == "fetch_tokens":
        client_id = sys.argv[2]
        client_secret = sys.argv[3]
        auth_code = sys.argv[4]
        code_verifier = sys.argv[5]
        code_challenge = sys.argv[6]
        client_credentials_base64 = sys.argv[7]

        print("client_id=",client_id)
        print("client_secret=",client_secret)
        print("auth_code=",auth_code)
        print("code_verifier=",code_verifier)
        print("code_challenge=",code_challenge)
        print("client_credentials_base64=",client_credentials_base64)

        fetch_tokens(auth_code)

    else:
        # 認可コードを取得
        authorization_code = get_authorization_code()

        # トークンを取得
        tokens = fetch_tokens(authorization_code)

#    if tokens:
#        # リフレッシュトークンを使用してアクセストークンを更新
#        refresh_access_token(tokens["refresh_token"])
