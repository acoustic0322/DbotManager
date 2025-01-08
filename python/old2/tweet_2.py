import sys
import tweepy
import pymysql
import requests

# MySQLから認証情報を取得する関数
def get_account_master(id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host='localhost',      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT login_id , client_id, client_secret, access_token, access_secret, bearer_token FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

# 認証を確認する関数
def verify_credentials(account_master):
    auth = tweepy.OAuth1UserHandler(
        account_master['client_id'],
        account_master['client_secret'],
        account_master['access_token'],
        account_master['access_secret']
    )
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        print("認証成功")
        return api  # 認証成功したAPIオブジェクトを返す
    except tweepy.errors.Unauthorized:
        print("認証エラー")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# OAuth2の認証を行い、User ContextでBearer Tokenを取得する関数
def authenticate_user_oauth2(client_id, client_secret, access_token, access_secret):
    # OAuth 1.0aで認証
    auth = tweepy.OAuth1UserHandler(
        client_id,
        client_secret,
        access_token,
        access_secret
    )
    
    # Tweepy APIクライアントを作成
    api = tweepy.API(auth)
    
    # OAuth 2.0 User Contextで認証するためのBearer Tokenを取得
    access_token = api.auth.access_token
    return access_token

# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

# ツイートにいいねをする関数
def like_tweet(api, tweet_id):
    try:
        # いいねをする
        api.create_favorite(tweet_id)  # create_favorite() はいいねを実行するAPI
        print("ツイートにいいねしました。")
    except tweepy.errors.Unauthorized:
        print("認証に失敗しました：認証情報を確認してください。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# ツイートをブックマークに追加する関数
#def bookmark_tweet(api, tweet_id):
#    try:
#        # 仮のエンドポイント（本番ではTwitter APIでの正式な実装を待つ）
#        api.bookmark(tweet_id)  # 現状ブックマークは正式にはサポートされていない
#        print("ツイートをブックマークに追加しました。")
#    except tweepy.errors.Unauthorized:
#        print("認証に失敗しました：認証情報を確認してください。")
#    except Exception as e:
#        print(f"エラーが発生しました: {e}")

# ツイートをブックマークに追加する関数
#def bookmark_tweet(client, tweet_id):
#    try:
#        # ツイートをブックマークに追加
#        client.create_bookmark(tweet_id)
#        print("ツイートをブックマークに追加しました。")
#    except tweepy.errors.Unauthorized:
#        print("認証に失敗しました：認証情報を確認してください。")
#    except Exception as e:
#        print(f"エラーが発生しました: {e}")   

def bookmark_tweet(bearer_token, tweet_id):
    url = f"https://api.twitter.com/2/users/me/bookmarks"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    data = {
        "status": "added",
        "tweet_id": tweet_id
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"ツイート {tweet_id} をブックマークに追加しました。")
    else:
        print(f"エラーが発生しました: {response.status_code} - {response.text}")             

def bookmark_tweet_v2(user_id, bearer_token, tweet_id):
    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
    }
    data = {
        "status": "Bookmarked",
        "tweet_id": tweet_id
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("ツイートをブックマークに追加しました。")
    else:
        print(f"エラーが発生しました: {response.status_code} {response.text}")

# コマンドライン引数を解析
if len(sys.argv) < 4:
    print("使用方法: python good_tweet3.py account_id=<ID> tweet_id=<TWEET_ID> tweet_mode=<MODE>")
    sys.exit(1)

args = parse_arguments(sys.argv[1:])
account_id = int(args.get("account_id"))
tweet_id = args.get("tweet_id")
tweet_mode = args.get("tweet_mode")

# 認証情報を取得
account_master = get_account_master(account_id)

if account_master:

    # ユーザーの認証情報を使用してOAuth2を通じて認証
    bearer_token = authenticate_user_oauth2(
        account_master['client_id'],
        account_master['client_secret'],
        account_master['access_token'],
        account_master['access_secret']
    )


    if bearer_token:
        # tweet_mode が "bookmark" の場合、ツイートをブックマーク
        if tweet_mode == "bookmark":
            bookmark_tweet(bearer_token, tweet_id)
        else:
            print(f"サポートされていないtweet_mode: {tweet_mode}")
    else:
        print("Bearer Tokenが見つかりませんでした。")

#    # 認証を確認
#    if verify_credentials(account_master):

#        # 認証が成功した場合、Tweepyクライアントを作成していいねを実行
#        auth = tweepy.OAuth1UserHandler(
#            account_master['client_id'],
#            account_master['client_secret'],
#            account_master['access_token'],
#            account_master['access_secret']
#        )
#        api = tweepy.API(auth)

#        # 認証が成功した場合、ツイート操作を実行
#        if tweet_mode == "like":
#            like_tweet(api, tweet_id)
#        elif tweet_mode == "bookmark":
#            bookmark_tweet(api, tweet_id)
#            bookmark_tweet_v2(account_master['login_id'], account_master['bearer_token'], tweet_id)
#        else:
#            print(f"サポートされていないtweet_mode: {tweet_mode}")
else:
    print(f"ID {account_id} の認証情報が見つかりませんでした。")
