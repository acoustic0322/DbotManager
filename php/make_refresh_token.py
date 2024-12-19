import secrets
import string
import hashlib
import base64
import requests

# 1. CODE_VERIFIERの生成
def generate_code_verifier():
    characters = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(characters) for _ in range(64))  # 64文字のランダム文字列を生成

# 2. CODE_CHALLENGEの生成 (S256メソッド)
def generate_code_challenge(code_verifier):
    sha256_hash = hashlib.sha256(code_verifier.encode('ascii')).digest()
    return base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('ascii')

# 生成
code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

print("CODE_VERIFIER:", code_verifier)
print("CODE_CHALLENGE:", code_challenge)

# 3. リフレッシュトークン取得のリクエスト
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

# 必要な情報
CLIENT_ID = '72Wzr0E71pUGiokxQZ0whs5Kf'#"YOUR_CLIENT_ID"  # Twitter Developer Portalで取得
REDIRECT_URI = 'https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec'
#"YOUR_CALLBACK_URL"  # コールバックURL
AUTHORIZATION_CODE = 'a1YtZVdFU1NobUEyb2E0NnBDS1Z3UUVVd2VPaWN4X2o0WXBpbFJkVVJETnptOjE3MzM4Njc4OTMzNDk6MTowOmFjOjE'#"YOUR_AUTHORIZATION_CODE"  # 認証URLで取得

# リクエストデータ
data = {
    "grant_type": "authorization_code",
    "code": AUTHORIZATION_CODE,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "code_verifier": code_verifier,
}

# トークン取得リクエスト
try:
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()  # エラー時に例外を発生させる

    # レスポンスの内容を表示
    token_response = response.json()
    print("Access Token:", token_response.get("access_token"))
    print("Refresh Token:", token_response.get("refresh_token"))
    print("Token Scope:", token_response.get("scope"))
    print("Expires In:", token_response.get("expires_in"))

except requests.exceptions.RequestException as e:
    print("エラーが発生しました:", e)
