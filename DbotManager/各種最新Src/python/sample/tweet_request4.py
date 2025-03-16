import requests

client_id = "YUZDcUhJclBPWmNTSTlSOFNSYUs6MTpjaQ"
client_secret = "IMX3NPYqOY7mrmKdskHnKrmfbxkic9BmflBCAtU-lWDGzkkH5w"
redirect_uri = "https://x.com"
authorization_code = "SFFNUUY1SFE1S216QlBMOW1USi1uQzlaYlh5NWhWQXZwcW9BeEcyQUQ2Y29DOjE3MzE2MTMwNDkzODA6MToxOmFjOjE"  # ここに取得した認証コードを入力
code_verifier = "challenge"  # `code_challenge`と同じ値

#https://twitter.com/i/oauth2/authorize?response_type=code&client_id=YUZDcUhJclBPWmNTSTlSOFNSYUs6MTpjaQ&redirect_uri=https://x.com&scope=tweet.read%20users.read%20tweet.write%20bookmark.read%20bookmark.write%20offline.access&state=state&code_challenge=challenge&code_challenge_method=plain
#Sk1pTmdQNHpYZHBJMGpLRFpTTjRITjlQeHFWUlA1c0NRS1hqRnpOTjB4NDN4OjE3MzE2MTM0MTAxNDc6MTowOmFjOjE

token_url = "https://api.twitter.com/2/oauth2/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "code": authorization_code,
    "grant_type": "authorization_code",
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "code_verifier": code_verifier
}

response = requests.post(token_url, headers=headers, data=data, auth=(client_id, client_secret))

if response.status_code == 200:
    tokens = response.json()
    print("Access Token:", tokens["access_token"])
    print("Refresh Token:", tokens["refresh_token"])
else:
    print("Error:", response.status_code, response.json())
