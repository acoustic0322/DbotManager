import requests

# 開いているプロファイルを取得する別のエンドポイントを試す
base_url = "http://127.0.0.1:53200/api"

endpoints = [
    "/v2/profile-open-list",
    "/v2/browser-list", 
    "/profile/open-list",
    "/v2/profile-list-open",
]

for ep in endpoints:
    try:
        resp = requests.post(f"{base_url}{ep}", json={}, timeout=5)
        data = resp.json()
        print(f"{ep}: {data}")
    except Exception as e:
        print(f"{ep}: {e}")