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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

def fetch_tokens(credentials, code):
    scopes = [
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access",
        "bookmark.read",
        "bookmark.write"
    ]

    auth = tweepy.OAuth2UserHandler(
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        redirect_uri='https://your-php-server-url/receive-code.php',  # PHPのエンドポイント
        scope=scopes
    )

    # トークンを取得
    token = auth.fetch_token(code)
    print("Access Token:", token.get("access_token"))
    print("Refresh Token:", token.get("refresh_token"))

def parse_arguments(args):
    parsed_args = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)  # 最初の1つ目の = だけで分割
            parsed_args[key] = value
        else:
            raise ValueError(f"Invalid argument format: {arg}")
    return parsed_args

if __name__ == "__main__":
    # 認証コードを引数として受け取る
    args = parse_arguments(sys.argv[1:])
    code = sys.argv[1]
    account_id = int(args.get("account_id","0"))

    # 認証情報を取得
    credentials = get_account_master(account_id)

    credentials = {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret"
    }
    fetch_tokens(credentials, code)
