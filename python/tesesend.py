import requests

# 送信先のURL
url = "http://203.137.53.205:5000/run"

# 送信データ
data = {
    "mode": "like",
    "id": [1, 3, 5, 6, 8, 10, 11]
}

try:
    # POSTリクエストを送信
    response = requests.post(url, json=data)
    
    # レスポンスを取得して表示
    if response.status_code == 200:
        print("成功:", response.json())
    else:
        print("エラー:", response.status_code, response.text)
except requests.exceptions.RequestException as e:
    print("リクエストエラー:", e)
