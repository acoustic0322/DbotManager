import pymysql

from datetime import datetime  # datetime モジュールをインポート


def get_comment_by_id(comment_id):

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
            sql = "SELECT comment FROM comment_master WHERE id=%s"
            cursor.execute(sql, (comment_id,))
            result = cursor.fetchone()
    finally:
        connection.close()

    if result is None:
        outputLog("エラー: 指定したコメントIDに対応するレコードが見つかりません。")
        return None
    
    return result["comment"]  # コメントを返す

  
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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id , id FROM account_master WHERE id = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
#            credentials['id'] = id
            return credentials
    finally:
        connection.close()

def get_account_master_for_update_refresh():
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
            # 30分以上経過したデータを取得
            sql = """
            SELECT id, client_id, client_secret, refresh_token 
            FROM account_master
            WHERE 
                refresh_token IS NOT NULL 
                AND refresh_updatetime IS NOT NULL
                AND TIMESTAMPDIFF(MINUTE, refresh_updatetime, NOW()) > 60
            """
            cursor.execute(sql)
            result = cursor.fetchall()

            # credentialsのリストを作成
            credentials_list = [
                {
                    'id': row['id'],
                    'client_id': row['client_id'],
                    'client_secret': row['client_secret'],
                    'refresh_token': row['refresh_token']
                }
                for row in result
            ]

            return credentials_list
    finally:
        connection.close()


def get_check_account_list(id):
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
            sql = "SELECT id, enable, mode, check_account , since_id , since_datetime , since_comment FROM check_account_list  WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

# ツイート履歴をデータベースに保存する関数
def save_tweet_history(account_id, comment_id, mode, target_tweet_id , result , error_log):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO tweet_history (account_id, comment_id, mode, target_tweet_id, updatetime , result , error_log)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (account_id, comment_id, mode, target_tweet_id, datetime.now(), result , error_log))
            connection.commit()
    finally:
        connection.close() 

def update_check_account_list(id, since_id, datetime):
    print("update_check_account_list")
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE check_account_list set since_id = %s , since_datetime = %s  where id = %s
            """
            cursor.execute(sql, (since_id , datetime , id))
#            sql = """
#                UPDATE check_account_list set since_id = %s , since_datetime = %s , since_comment = %s where id = %s
#            """
#            cursor.execute(sql, (since_id , datetime , truncate_by_byte_length(since_comment, 100), id))
            connection.commit()
    finally:
        connection.close()   

def update_refresh_token(account_id, bearer_token, refresh_token):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE account_master set bearer_token = %s , refresh_token = %s , refresh_updatetime = NOW() where id = %s
            """
            cursor.execute(sql, (bearer_token , refresh_token , account_id))
            connection.commit()
    finally:
        connection.close()        
 
def get_user_id_from_db(user_name):
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
            sql = "SELECT user_id FROM check_user_master WHERE user_name = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (user_name,))
            credentials = cursor.fetchone()

            # データが取得できなかった場合はNoneを返す
            if credentials is None:
#                print(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None

            return credentials['user_id']
    finally:
        connection.close()

def get_slice_id_from_db(user_name):
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
            sql = "SELECT since_id FROM check_user_master WHERE user_name = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (user_name,))
            credentials = cursor.fetchone()

            # データが取得できなかった場合はNoneを返す
            if credentials is None:
#                print(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None

            return credentials['since_id']
    finally:
        connection.close()

def update_user_id_from_db(user_name , user_id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE check_user_master set user_id = %s where user_name = %s
            """
            cursor.execute(sql, (user_id , user_name ))
            connection.commit()
    finally:
        connection.close()      

def update_since_id_from_db(user_name , since_id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE check_user_master set since_id = %s where user_name = %s
            """

#            print(sql)
#            print("since_id=",since_id)
#            print("user_name=",user_name)
            cursor.execute(sql, (since_id , user_name ))
            connection.commit()
    finally:
        connection.close()              