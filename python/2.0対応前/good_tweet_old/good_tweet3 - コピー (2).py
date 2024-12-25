import sys
import tweepy
import pymysql

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
            sql = "SELECT client_id, client_secret, access_token, access_secret FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

# コマンドライン引数からcredential_idとtweet_idを取得
if len(sys.argv) != 3:
    print("使用方法: python good_tweet3.py <credential_id> <tweet_id>")
    sys.exit(1)

credential_id = int(sys.argv[1])
tweet_id = sys.argv[2]

# 認証情報を取得
account_master = get_account_master(credential_id)

if account_master:

    # OAuth 1.0aで認証するための設定
    auth = tweepy.OAuth1UserHandler(
        account_master['client_id'],
        account_master['client_secret'],
        account_master['access_token'],
        account_master['access_secret']
    )

    # 認証をクライアントに適用
    api = tweepy.API(auth)

    # アクセス権限の確認
    try:
        api.verify_credentials()
        print("認証成功")
    except tweepy.errors.Unauthorized:
        print("認証エラー")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    # 認証情報を設定する
    client = tweepy.Client(
        consumer_key=account_master['client_id'],
        consumer_secret=account_master['client_secret'],
        access_token=account_master['access_token'],
        access_token_secret=account_master['access_secret']
    )

    try:
        # いいねをする
        client.like(tweet_id)
    except tweepy.errors.Unauthorized:
        print("認証に失敗しました：認証情報を確認してください。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

