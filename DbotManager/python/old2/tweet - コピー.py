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
            sql = "SELECT client_id, client_secret, access_token, access_secret , bearer_token FROM account_master WHERE id = %s"
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
        return True
    except tweepy.errors.Unauthorized:
        print("認証エラー")
        return False
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

# コマンドライン引数の解析関数
def parse_arguments(args):
    params = {}
    for arg in args:
        key, value = arg.split('=')
        params[key] = value
    return params

# ツイートにいいねをする関数
def like_tweet(client, tweet_id):
    try:
        # いいねをする
        client.like(tweet_id)
        print("ツイートにいいねしました。")
    except tweepy.errors.Unauthorized:
        print("認証に失敗しました：認証情報を確認してください。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# ツイートをブックマークに追加する関数
def bookmark_tweet(client, tweet_id):
    try:
        # 仮のエンドポイント
        client.bookmark(tweet_id)
        print("ツイートをブックマークに追加しました。")
    except tweepy.errors.Unauthorized:
        print("認証に失敗しました：認証情報を確認してください。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

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
    # 認証を確認
    if verify_credentials(account_master):
        # 認証が成功した場合、Tweepyクライアントを作成していいねを実行
        client = tweepy.Client(
            consumer_key=account_master['client_id'],
            consumer_secret=account_master['client_secret'],
            access_token=account_master['access_token'],
            access_token_secret=account_master['access_secret'],
            bearer_token=account_master['bearer_token']
        )

        # tweet_mode が "like" の場合、ツイートにいいね
        if tweet_mode == "like":
            like_tweet(client, tweet_id)
        elif tweet_mode == "bookmark":
            bookmark_tweet(client, tweet_id)
        else:
            print(f"サポートされていないtweet_mode: {tweet_mode}")
else:
    print(f"ID {credential_id} の認証情報が見つかりませんでした。")
