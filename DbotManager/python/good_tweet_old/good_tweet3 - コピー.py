import tweepy
import pymysql

# MySQLから認証情報を取得する関数
def get_twitter_credentials(id):
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


# 取得したい認証情報のIDを指定
credential_id = 1  # 例: id = 1 の認証情報を取得

# 認証情報を取得
credentials = get_twitter_credentials(credential_id)

# OAuth 1.0aで認証するための設定
auth = tweepy.OAuth1UserHandler(
    credentials['client_id'],
    credentials['client_secret'],
    credentials['access_token'],
    credentials['access_secret']
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
    consumer_key=credentials['client_id'],
    consumer_secret=credentials['client_secret'],
    access_token=credentials['access_token'],
    access_token_secret=credentials['access_secret']
)

# ツイートのID
#tweet_id = '1854085562485129666'#args[1]  # ここに対象のツイートのIDを入力してください
tweet_id = '1854359368776462422'#args[1]  # ここに対象のツイートのIDを入力してください

try:
    # いいねをする
    client.like(tweet_id)
except tweepy.errors.Unauthorized:
    print("認証に失敗しました：認証情報を確認してください。")
except Exception as e:
    print(f"エラーが発生しました: {e}")

