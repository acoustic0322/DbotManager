import requests

# Twitter APIクライアントIDとクライアントシークレット
client_id = "YUZDcUhJclBPWmNTSTlSOFNSYUs6MTpjaQ"
client_secret = "IMX3NPYqOY7mrmKdskHnKrmfbxkic9BmflBCAtU-lWDGzkkH5w"
redirect_uri = "https://x.com"

token_url = "https://api.twitter.com/2/oauth2/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "code": "al92amNLaXRqRE1YLTlmak1tR3Z4WGxTeDdDQlYxeUJBdGdQNkJPR0VxY2JJOjE3MzE2MTI2ODc2OTY6MToxOmFjOjE",  # 上記で取得した認証コード
    "grant_type": "authorization_code",
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "code_verifier": "challenge"
}

response = requests.post(token_url, headers=headers, data=data, auth=(client_id, client_secret))

if response.status_code == 200:
    tokens = response.json()
    print("Access Token:", tokens["access_token"])
    print("Refresh Token:", tokens["refresh_token"])
else:
    print("Error:", response.status_code, response.json())
