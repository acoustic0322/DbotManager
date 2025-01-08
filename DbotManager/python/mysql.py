import pymysql
import config

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
            sql = "SELECT api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id , id ,dmm_id FROM account_master WHERE id = %s"
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


def get_search_list(id):
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
            sql = "SELECT id, search_user_name, search_user_id , search_account_id , post_account_id, post_enable , last_post_id , last_post_time , reply_account_id , reply_enable , last_reply_id , last_reply_time , monomane_account_id , monomane_enable , last_monomane_id , last_monomane_time FROM search_list  WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
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
def save_tweet_history(account_id, comment_id, mode, target_tweet_id , result , error_log , result2 , error_log2):
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
                INSERT INTO tweet_history (account_id, comment_id, mode, target_tweet_id, updatetime , result , error_log , result2 , error_log2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (account_id, comment_id, mode, target_tweet_id, datetime.now(), result , error_log , result2 , error_log2  ))
            connection.commit()
    finally:
        connection.close() 

def update_check_account_list(id, since_id, datetime):
    outputLog("update_check_account_list")
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

def update_search_list(id, tweet_id, datetime, mode):
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

            if mode == "post":
                sql = """
                    UPDATE search_list set last_post_id = %s , last_post_time = %s  where id = %s
                """
            elif mode == "reply":
                sql = """
                    UPDATE search_list set last_reply_id = %s , last_reply_time = %s  where id = %s
                """
            elif mode == "monomane":
                sql = """
                    UPDATE search_list set last_monomane_id = %s , last_monomane_time = %s  where id = %s
                """

#            print(sql)
#            print(id)
#            print(tweet_id)
#            print(datetime)

            cursor.execute(sql, (tweet_id , datetime , id))
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
 
def get_user_id_from_db(check_list_id):
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
            sql = "SELECT target_user_id FROM check_account_list WHERE id = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (check_list_id,))
            credentials = cursor.fetchone()

            # データが取得できなかった場合はNoneを返す
            if credentials is None:
#                print(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None

            return credentials['target_user_id']
    finally:
        connection.close()

def get_slice_id_from_db(user_name , search_replies):
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
            sql = "SELECT since_id , since_reply_id FROM check_user_master WHERE user_name = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (user_name,))
            credentials = cursor.fetchone()

            # データが取得できなかった場合はNoneを返す
            if credentials is None:
#                print(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None

            if search_replies == True:
                return credentials['since_reply_id']

            return credentials['since_id']
    finally:
        connection.close()

    return None

def get_last_tweet_id_from_check_account_list(id , search_replies):
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
            sql = "SELECT last_tweet_id , last_tweet_datetime,last_reply_id , last_reply_datetime FROM check_account_list WHERE id = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()

            # データが取得できなかった場合はNoneを返す
            if credentials is None:
                print(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None , None

            if search_replies == True:
                if config.debug == True:
                    print("credentials['last_reply_id'] =",credentials['last_reply_id'] )
                    print("credentials['last_reply_datetime'] =",credentials['last_reply_datetime'] )
                return credentials['last_reply_id'] , credentials['last_reply_datetime']
            if config.debug == True:
                print("credentials['last_tweet_id'] =",credentials['last_tweet_id'] )
                print("credentials['last_tweet_datetime'] =",credentials['last_tweet_datetime'] )
            return credentials['last_tweet_id'] , credentials['last_tweet_datetime']
    finally:
        connection.close()

    return None


def update_user_id_from_db(id , target_user_id):
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
                UPDATE check_account_list set target_user_id = %s where id = %s
            """
            cursor.execute(sql, (target_user_id , id ))
            connection.commit()
    finally:
        connection.close()      


def update_last_tweet_id_from_check_account_list(id , latest_tweet_id , latest_tweet_datetime, search_reply):
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

            if search_reply == True:
                sql = """
                    UPDATE check_account_list set last_reply_id = %s , last_reply_datetime = %s where id = %s
                """
            else:
                sql = """
                    UPDATE check_account_list set last_tweet_id = %s , last_tweet_datetime = %s where id = %s
                """

#            print(sql)
#            print("id=",id)
#            print("latest_tweet_id=",latest_tweet_id)
#            print("latest_tweet_dt=",latest_tweet_datetime)
            cursor.execute(sql, (latest_tweet_id , latest_tweet_datetime , id ))
            connection.commit()
    finally:
        connection.close()              