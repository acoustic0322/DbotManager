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


def check_bearer_token(credentials):
    # トークン取得時のレスポンス例
    response = {
        "access_token": credentials['bearer_token'],
        "expires_in": 7200,  # 秒単位で有効期限（2時間）
    }

    # 現在時刻（UNIXタイムスタンプ）
    token_acquired_time = time.time()
    
    # トークンの有効期限（UNIXタイムスタンプ）
    token_expiry_time = token_acquired_time + response["expires_in"]

    # UNIXタイムスタンプを見やすい日時形式に変換
    acquired_datetime = datetime.fromtimestamp(token_acquired_time).strftime('%Y-%m-%d %H:%M:%S')
    expiry_datetime = datetime.fromtimestamp(token_expiry_time).strftime('%Y-%m-%d %H:%M:%S')

    # 結果を表示
    print(f"トークン取得時刻: {acquired_datetime}")
    print(f"トークン有効期限: {expiry_datetime}")


def get_twitter_useid(access_token):
    # アクセストークン
#    access_token = "YOUR_ACCESS_TOKEN"

    # APIエンドポイントとヘッダー
    endpoint = "https://api.twitter.com/2/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # リクエスト送信
    response = requests.get(endpoint, headers=headers)

    # レスポンスの処理
    if response.status_code == 200:
        user_data = response.json()
        print("ユーザー情報:", user_data)
        print("user_id:", user_data["data"]["id"])  # user_id を取得
    else:
        print("エラーが発生しました:", response.status_code, response.json())

    return user_data["data"]["id"]


    
# 認証を確認する関数 (APIオブジェクトを返す)
def create_api(credentials):
    auth = tweepy.OAuth1UserHandler(
        credentials['api_key'],
        credentials['api_key_secret'],
        credentials['access_token'],
        credentials['access_token_secret']
    )
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        outputLog("認証成功 (API)")
        return api
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー (API)")
        return Nonev


# APIオブジェクトを返す関数 (OAuth 1.0a User Context)
def create_api(credentials):
    auth = tweepy.OAuth1UserHandler(
        credentials['api_key'],
        credentials['api_key_secret'],
        credentials['access_token'],
        credentials['access_token_secret']
    )
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        outputLog("認証成功 (API)")
        return api
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー (API)")
        return None

# 認証
def authenticate_twitter(credentials):
    auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret']  )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

# 認証
def authenticate_twitter2(credentials):
    auth = tweepy.OAuthHandler(credentials['client_id'], credentials['client_secret'])
    auth.set_access_token(credentials['access_token'], credentials['access_token_secret']  )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

def is_image_file(file_path):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in image_extensions

def is_video_file(file_path):
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}
    _, ext = os.path.splitext(file_path)
    return ext.lower() in video_extensions

    def truncate_by_byte_length(s, max_bytes, encoding="utf-8"):

    """
    文字列を指定したバイト数で切り詰める関数。
    :param s: 対象の文字列
    :param max_bytes: 最大バイト数
    :param encoding: エンコーディング (デフォルトは UTF-8)
    :return: 切り詰めた文字列
    """

    encoded = s.encode(encoding)  # 文字列をバイト列にエンコード
    if len(encoded) <= max_bytes:
        return s  # バイト数が上限以下ならそのまま返す

    # バイト列を指定バイト数まで切り詰め
    truncated = encoded[:max_bytes]

    print(truncated.decode(encoding, errors="ignore"))

    # 無効なバイトシーケンスが含まれる場合を防ぐためデコードする
    return truncated.decode(encoding, errors="ignore")

    
def fetch_user_with_retry(client, username, retries=3):
    for attempt in range(retries):
        try:
            user = client.get_user(username=username)
            return user
        except tweepy.errors.TooManyRequests as e:
            print("Rate limit exceeded. Retrying...")
            time.sleep(15 * 60)  # 15分間待機
        except Exception as e:
            print(f"Error fetching user {username}: {e}")
            break
    return None

    # 認証を確認する関数 (Clientオブジェクトを返す)
def create_client(credentials):
    client = tweepy.Client(
        consumer_key=credentials['api_key'],
        consumer_secret=credentials['api_key_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret'],
        bearer_token=credentials['bearer_token']
    )
    return client

    def verify_credentials_v2(account_master):

    # ここでaccount_master辞書にclient_idとclient_secretが正しく設定されているか確認してください
    client_id = account_master.get('client_id')
    client_secret = account_master.get('client_secret')
    access_token = account_master.get('access_token')

    if not client_id or not client_secret or not access_token:
        outputLog("認証情報が不足しています。client_id, client_secret, access_token, redirect_uri を確認してください。")
        return False, "認証情報が不足しています"

    auth = tweepy.OAuth2UserHandler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="https://d-bot.happywinds.net/d-bot/callback.php",
        scope=["tweet.read", "users.read"]  # 必要なスコープを指定
    )
    
    # アクセストークンを直接設定
    auth.access_token = account_master['access_token']  # アクセストークンを設定
    
    try:
        # `OAuth2UserHandler` を使って `tweepy.Client` を作成
        client = tweepy.Client(
            bearer_token=auth.access_token  # Bearer Tokenとして設定
        )
        
        # ユーザー情報の取得
        user = client.get_me()  # ユーザー情報の取得
        outputLog(f"認証成功: ユーザー名={user.data['username']}")
        print(f"認証成功: ユーザー名={user.data['username']}")
        return True, f"認証成功: ユーザー名={user.data['username']}"
    
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー: アクセストークンが無効です")
        return False, "認証エラー: アクセストークンが無効です"
    
    except Exception as e:
        outputLog(f"verify_credentials_v2エラーが発生しました: {e}")
        return False, f"エラーが発生しました: {e}"

# 認証を確認する関数
def verify_credentials(account_master):
    auth = tweepy.OAuth1UserHandler(
        account_master['api_key'],
        account_master['api_key_secret'],
        account_master['access_token'],
        account_master['access_token_secret']
    )
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        outputLog("認証成功")
        return True , "認証成功"
    except tweepy.errors.Unauthorized:
        outputLog("認証エラー")
        return False , "認証エラー"
    except Exception as e:
        outputLog(f"エラーが発生しました: {e}")
        return False , f"エラーが発生しました: {e}"