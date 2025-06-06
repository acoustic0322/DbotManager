import requests

def proc_profile_image(username):

    url = f"https://unavatar.io/twitter/{username}"

    response = requests.get(url)

    if response.status_code == 200:
        with open(f"{username}.jpg", "wb") as f:
            f.write(response.content)
        print(f"{username}.jpg を保存しました。")
    else:
        print("取得失敗:", response.status_code)
        