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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

account_id = 1
credentials = get_account_master(account_id)

CONSUMER_KEY = 'TobPKwhKLbt7yaM2Ty1KBFZNV'
CONSUMER_SECRET = 'WzYRSurjfXSC2XmDzrtl3hEB0l6C4ymmnn4VyflEBjWWnYyByl'

client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=credentials['access_token'],
    access_token_secret=credentials['access_token_secret']
)

# Create Tweet

# The app and the corresponding credentials must have the Write permission

# Check the App permissions section of the Settings tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps

# Make sure to reauthorize your app / regenerate your access token and secret 
# after setting the Write permission

response = client.create_tweet(
    text="This Tweet was Tweeted using Tweepy and Twitter API v2!"
)
print(f"https://twitter.com/user/status/{response.data['id']}")