import requests
import json
import time
import sys
#import tweepy
#import pymysql
import os
import base64
import pymysql

def get_user_id(credentials):

    access_token = credentials['bearer_token']
    username = credentials['login_id']    

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/json"
    }

    # ユーザーIDを取得するURL
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data["data"]["id"]
        print(f"get_user_id {username}のユーザーID: {user_id}")
        return user_id
    else:
        print(f"get_user_idエラー: {response.status_code}, {response.text}")
        return None

def check_access_token(credentials):

    bearer_token = credentials['bearer_token']
    refresh_token = credentials['refresh_token']

    status_code , contents = check_access_token_validity(credentials['bearer_token'])

    if status_code == 401:
        bearer_token , refresh_token = refresh_access_token(credentials)

#    check_access_token_oauth_type(bearer_token)

    return bearer_token , refresh_token 

def refresh_access_token(credentials):

#    account_id = credentials['id']
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    refresh_token = credentials['refresh_token']
#    account_id = credentials['id']

    print("refresh_token=",refresh_token)

    url = "https://api.twitter.com/2/oauth2/token"

    # Base64エンコードされたAuthorizationヘッダーを作成
    client_credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"  # Authorizationヘッダーを追加
    }

    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()  # JSONデータを取得
        print("response.json()=", response_data)

        # access_token を抜き出す
        access_token = response_data.get("access_token")
        print("access_token=", access_token)

        refresh_token = response_data.get("refresh_token")
        print("refresh_token=", refresh_token)

        # スコープを確認する
        scope = response_data.get("scope")
        if scope:
            print("付与されたスコープ=", scope)
        else:
            print("スコープ情報が返されていません")

        credentials['refresh_token'] = refresh_token
        credentials['bearer_token'] = access_token

        return access_token , refresh_token
    else:
        print(f"refresh_access_tokenエラー: {response.status_code}, {response.text}")
        return None , None  

def check_access_token_oauth_type(access_token):

    print("check_access_token_oauth_type access_token=",access_token)

    url = "https://api.twitter.com/2/users/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("check_access_token_oauth_type 認証成功: User Context アクセストークンを使用しています")
        print("check_access_token_oauth_type レスポンス:", response.json())
    elif response.status_code == 403:
        print("check_access_token_oauth_type 認証失敗: Application-Only アクセストークンを使用している可能性があります")
    else:
        print(f"check_access_token_oauth_type エラー: {response.status_code}, {response.json()}")

    return response.status_code , json.dumps(response.json())

def check_access_token_validity(access_token):
    url = "https://api.twitter.com/2/users/me"  # ユーザー情報を取得
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # リクエストを送信してアクセストークンの有効性を確認
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("check_access_token_validity アクセストークンは有効です。")
        return response.status_code , ""
    elif response.status_code == 401:
        print("check_access_token_validity アクセストークンが無効です。再認証が必要です。")
        return response.status_code , json.dumps(response.json())
    else:
        print(f"check_access_token_validity エラー: {response.status_code}")
        print(response.json())  # エラーメッセージを表示
        return response.status_code , json.dumps(response.json())

def check_rate_limit(headers):
    limit = int(headers.get('x-rate-limit-limit', 0))  # リクエスト制限数
    remaining = int(headers.get('x-rate-limit-remaining', 0))  # 残りリクエスト数
    reset = int(headers.get('x-rate-limit-reset', 0))  # リセットまでのタイムスタンプ

    # 残りリクエスト数が0の場合、制限に達している
    if remaining == 0:
        reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(reset))  # リセット時間を表示
        print(f"レートリミットに達しました。次のリセット時刻: {reset_time}")
        return False
    else:
        print(f"現在の残りリクエスト数: {remaining}")
        return True

def check_rate_limit2(credentials):

    access_token= credentials['bearer_token']

    print("check_rate_limit2")
    # Twitter APIのエンドポイント（例: ユーザー情報取得）
    url = "https://api.twitter.com/2/users/by/username/TwitterDev"
    headers = {
        "Authorization": "Bearer {access_token}"
    }

    # APIリクエストを送信
    response = requests.get(url, headers=headers)

    # レスポンスのヘッダーからx-rate-limit-resetを取得
    reset_timestamp = response.headers.get('x-rate-limit-reset')

    if reset_timestamp:
        reset_time = datetime.utcfromtimestamp(int(reset_timestamp))
        print(f"次のリセット時刻: {reset_time}")
    else:
        print("x-rate-limit-resetヘッダーが見つかりませんでした")

def check_rate_limit3(access_token):
    # Twitter APIのレートリミットステータス確認用エンドポイント
    url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
    headers = {
        "Authorization": "Bearer {access_token}"
    }

    # APIリクエストを送信
    response = requests.get(url, headers=headers)

    # レスポンスの確認
    if response.status_code == 200:
        rate_limit_data = response.json()
    
        # 例として、"users"エンドポイントのレートリミットを表示
        limit_info = rate_limit_data['resources']['users']['/users/show']
        reset_timestamp = limit_info['reset']
    
        # リセット時刻を変換
        reset_time = datetime.utcfromtimestamp(reset_timestamp)
        print(f"check_rate_limit3 次のリセット時刻: {reset_time}")
    else:
        print(f"check_rate_limit3 エラー: {response.status_code}")
        print(response.json())

def proc_post_v2(credentials):
#    check_access_token(credentials)

#    credentials = refresh_access_token(credentials)

    access_token = credentials['bearer_token']

#    check_rate_limit3(access_token)

#    # アクセストークンの検証
#    if check_access_token(credentials) == False:
#        return

    # エンドポイントURL
    url = "https://api.twitter.com/2/tweets"
    # 投稿するデータ
    data = {
        "text": "[test]Twitter APIを使って投稿しています！"
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)
    # レスポンスを確認
    if response.status_code == 201:
        print("ツイートが成功しました:")
        print(response.json())  # 投稿成功時のレスポンス
    else:
        print(f"エラー: {response.status_code}")
        print(response.json())    
    return True , ""

def proc_like_v2(credentials, tweet_id):
    """
    指定されたツイートに「いいね」を付ける関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: いいねする対象のツイートID
    """

    print("proc_like_v2")

    access_token = credentials['bearer_token']

#    credentials = refresh_access_token(credentials)

    # アクセストークンの検証
#    res  = check_access_token(credentials)
#    if res == False:
#        return

    user_id = get_user_id(credentials)

    # 「いいね」エンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/likes"

    # 投稿するデータ（ツイートIDを指定）
    data = {
        "tweet_id": tweet_id
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

    # レートリミットの判定
#    if not check_rate_limit3(access_token):
#        return False, "Rate limit exceeded."
#    if not check_rate_limit(response.headers):
#        return False, "Rate limit exceeded."

    # レスポンスを確認
    if response.status_code == 200:
        print("proc_like_v2 ツイートにいいねを付けました:")
        print(response.json())  # 成功時のレスポンス
    else:
        print(f"proc_like_v2 エラー: {response.status_code}")
        print(response.json())

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code == 200, response_str


def proc_bookmark_v2(credentials, tweet_id):
    """
    指定されたツイートをブックマークする関数。

    :param credentials: Twitter APIの認証情報を含む辞書
    :param tweet_id: ブックマークする対象のツイートID
    """

    print("login_id:",credentials['login_id'])

    access_token = credentials['bearer_token']

    user_id = get_user_id(credentials)

    # ブックマーク用エンドポイントURL
    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"

    # 投稿するデータ（ツイートIDを指定）
    data = {
        "tweet_id": tweet_id
    }

    # ヘッダー
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=data)

    # レスポンスを確認
    if response.status_code == 200:
        print("ツイートをブックマークしました:")
        print(response.json())  # 成功時のレスポンス
    else:
        print(f"エラー: {response.status_code}")
        print(response.json())

    response_str = json.dumps(response.json())  # json.dumps を使用

    return response.status_code == 200, response_str
