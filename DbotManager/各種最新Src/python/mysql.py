import pymysql
import config

from datetime import datetime  # datetime モジュールをインポート
from config import outputLog
from config import convert_tweet_datetime
import random
from typing import Optional

def get_comment_by_id(comment_id):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
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

def get_media_file_name_by_id(media_id):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT name FROM media_master WHERE media_id=%s"
            cursor.execute(sql, (media_id,))
            result = cursor.fetchone()
    finally:
        connection.close()

    if result is None:
        outputLog("エラー: 指定したコメントIDに対応するレコードが見つかりません。")
        return None
    
    return result["name"]  # コメントを返す

def get_random_comment_id(account_id , mode):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    outputLog("mode:",mode)

    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT id FROM comment_master WHERE account_id=%s and mode=%s ORDER BY RAND() LIMIT 1"
            cursor.execute(sql, (account_id,mode))
            result = cursor.fetchone()
    finally:
        connection.close()

    if result is None:
        outputLog("エラー: 指定したコメントIDに対応するレコードが見つかりません。")
        return None

    outputLog(result)
    
    return result["id"]  # コメントを返す
   
def get_all_account_master():
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = """SELECT 
            *
            FROM 
            account_master 
            """
            cursor.execute(sql)
            credentials = cursor.fetchall()
            return credentials
    finally:
        connection.close()


def get_account_master(id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = """SELECT 
            am.api_key, 
            am.api_key_secret, 
            am.access_token, 
            am.access_token_secret , 
            am.bearer_token , 
            case am.api_master_id when '0' then am.client_id 
            else api.client_id end as client_id,
            case am.api_master_id when '0' then am.client_secret 
            else api.client_secret end as client_secret,           
            am.refresh_token , 
            am.login_id , 
            am.id ,
            am.dmm_id , 
            am.search_enable , 
            am.proxy_enable , 
            am.proxy_url ,
            am.api_master_id,
            am.twitter_user_id,
            am.check_rep_datetime,
            am.user_id,
            um.GROQ_API_KEY,
            um.OPENAI_API_KEY,
            am.ai_mode,
            am.ai_post_enable,
            am.ai_reply_enable,
            am.ai_post_prompt,
            am.ai_reply_prompt,
            am.ai_trend_prompt,
            am.reserve1_ai,
            am.reserve2_ai,
            am.reserve3_ai,
            am.reserve4_ai,
            am.ai_post_example,
            am.ai_reply_example,
            um.jap_api_key
            ,am.ai_uraaka_prompt
            ,am.ai_uraaka_prompt_rep
            ,am.ai_uraaka_past_tweet
            ,am.ai_uraaka_past_rep
            ,am.ai_trend_prompt_yahoo
            ,am.ai_trend_prompt_x
            ,am.ai_btc_prompt
            ,am.ai_free_prompt
            ,am.ai_free_prompt_rep
            ,am.ai_free_past_rep
            FROM 
            account_master am
            left join api_master api on api.id = am.api_master_id
            left join user_master um on um.id = am.user_id
            WHERE am.id = %s"""

#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
#            credentials['id'] = id
            return credentials
    finally:
        connection.close()

def update_account_master_by_twitter_user_id(id , twitter_user_id ):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:

            sql = """
                UPDATE account_master set twitter_user_id = %s where id = %s
            """

#            outputLog(sql)
#            outputLog("id=",id)
#            outputLog("latest_tweet_id=",latest_tweet_id)
#            outputLog("latest_tweet_dt=",latest_tweet_datetime)
            cursor.execute(sql, (twitter_user_id , id ))
            connection.commit()
    finally:
        connection.close()         

def update_account_master_by_check_rep_datetime(id ):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:

            sql = """
                UPDATE account_master set check_rep_datetime = NOW() where id = %s
            """

            outputLog(sql)
            outputLog(f"id={id}")
            cursor.execute(sql, ( id ))
            connection.commit()
    finally:
        connection.close()          

def update_account_master_by_update_profile_datetime(id ):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:

            sql = """
                UPDATE account_master set update_profile_datetime = NOW() where id = %s
            """

            outputLog(sql)
            outputLog(f"id={id}")
            cursor.execute(sql, ( id ))
            connection.commit()
    finally:
        connection.close()                  

def get_account_master_for_update_refresh(num):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 30分以上経過したデータを取得
            if num == 0:

                sql = """
                SELECT 
                    am.id, 
                    CASE am.api_master_id
                        WHEN '0' THEN am.client_id 
                        ELSE api.client_id
                    END AS client_id,

                    CASE am.api_master_id
                        WHEN '0' THEN am.client_secret 
                        ELSE api.client_secret
                    END AS client_secret,

                    am.refresh_token,
                    am.proxy_enable,
                    am.proxy_url

                FROM account_master am

                LEFT JOIN api_master api
                    ON api.id = am.api_master_id

                WHERE
                    am.refresh_token IS NOT NULL
                    AND am.refresh_updatetime IS NOT NULL
                    AND TIMESTAMPDIFF(
                        MINUTE,
                        am.refresh_updatetime,
                        NOW()
                    ) > 60
                    AND am.is_locked = 0
                    AND am.is_suspended = 0
                    AND am.is_unauthorized = 0
                """

            elif num == 1:

                sql = """
                SELECT 
                    am.id,

                    ugm.client_id_1 AS client_id,
                    ugm.client_secret_1 AS client_secret,

                    am.refresh_token_1 AS refresh_token,

                    am.proxy_enable,
                    am.proxy_url

                FROM account_master am

                LEFT JOIN user_group_master ugm
                    ON ugm.id = am.user_id

                WHERE
                    am.refresh_token_1 IS NOT NULL
                    AND am.refresh_updatetime_1 IS NOT NULL
                    AND TIMESTAMPDIFF(
                        MINUTE,
                        am.refresh_updatetime_1,
                        NOW()
                    ) > 60
                    AND am.is_locked = 0
                    AND am.is_suspended = 0
                    AND am.is_unauthorized = 0
                """

            elif num == 2:

                sql = """
                SELECT 
                    am.id,

                    ugm.client_id_2 AS client_id,
                    ugm.client_secret_2 AS client_secret,

                    am.refresh_token_2 AS refresh_token,

                    am.proxy_enable,
                    am.proxy_url

                FROM account_master am

                LEFT JOIN user_group_master ugm
                    ON ugm.id = am.user_id

                WHERE
                    am.refresh_token_2 IS NOT NULL
                    AND am.refresh_updatetime_2 IS NOT NULL
                    AND TIMESTAMPDIFF(
                        MINUTE,
                        am.refresh_updatetime_2,
                        NOW()
                    ) > 60
                    AND am.is_locked = 0
                    AND am.is_suspended = 0
                    AND am.is_unauthorized = 0
                """

            elif num == 3:

                sql = """
                SELECT 
                    am.id,

                    ugm.client_id_3 AS client_id,
                    ugm.client_secret_3 AS client_secret,

                    am.refresh_token_3 AS refresh_token,

                    am.proxy_enable,
                    am.proxy_url

                FROM account_master am

                LEFT JOIN user_group_master ugm
                    ON ugm.id = am.user_id

                WHERE
                    am.refresh_token_3 IS NOT NULL
                    AND am.refresh_updatetime_3 IS NOT NULL
                    AND TIMESTAMPDIFF(
                        MINUTE,
                        am.refresh_updatetime_3,
                        NOW()
                    ) > 60
                    AND am.is_locked = 0
                    AND am.is_suspended = 0
                    AND am.is_unauthorized = 0
                """
            else:
                return []    

            cursor.execute(sql)
            result = cursor.fetchall()

            # credentialsのリストを作成
            credentials_list = [
                {
                    'id': row['id'],
                    'client_id': row['client_id'],
                    'client_secret': row['client_secret'],
                    'refresh_token': row['refresh_token'],
                    'proxy_enable': row['proxy_enable'],
                    'proxy_url': row['proxy_url']
                }
                for row in result
            ]

            return credentials_list
    finally:
        connection.close()

def get_search_list(id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT id, search_user_name, account_id, post_enable , reply_enable , monomane_enable FROM search_list  WHERE id = %s"
            cursor.execute(sql, (id,))
            credentials = cursor.fetchone()
            return credentials
    finally:
        connection.close()

def get_check_account_list(id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
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
def save_tweet_history(account_id, comment_id, mode, target_tweet_id , result , error_log , result2 = None , error_log2 = None):
    connection = None
    try:
        connection = pymysql.connect(
            host=config.db_host,
            user='root',
            password='abcd1234',
            database='d_bot',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor         
        )
        
        # --- 修正ポイント1：安全に文字列化して判定 ---
        error_type = ""
        log_text = str(error_log) if error_log else ""

        outputLog(f"log_text={log_text}")

        if "Your account is temporarily locked" in log_text:
            error_type = "lock"
        elif "The user used for authentication is suspended" in log_text:
            error_type = "suspention"
        elif '"status": 401' in log_text or "Could not authenticate you" in log_text:
            error_type = "unauthorized"

        outputLog(f"error_type={error_type}")

        with connection.cursor() as cursor:
            # 1. 履歴の保存
            sql = """
                INSERT INTO tweet_history (account_id, comment_id, mode, target_tweet_id, updatetime , result , error_log , result2 , error_log2 , error_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (account_id, comment_id, mode, target_tweet_id, datetime.now(), result , error_log , result2 , error_log2 , error_type ))
            connection.commit()

            # --- 修正ポイント2：INSERT ... ON DUPLICATE KEY UPDATE を使用 ---
            if error_type in ('lock', 'suspention', 'unauthorized'):
                error_sql = """
                    INSERT INTO account_error_log (account_id, user_id, error_type, error_log, updatetime)
                    SELECT %s, am.user_id, %s, %s, NOW()
                    FROM account_master am WHERE am.id = %s
                    ON DUPLICATE KEY UPDATE 
                        user_id = VALUES(user_id),
                        error_type = VALUES(error_type), 
                        error_log = VALUES(error_log), 
                        updatetime = NOW()
                """
                cursor.execute(error_sql, (account_id, error_type, error_log, account_id))
                connection.commit()

	    # 2026.04.04 Start account_masterのフラグ更新
            if error_type == 'lock':
                outputLog(f"lock account_id={account_id}")
                error_sql = """ UPDATE account_master SET is_locked = 1 WHERE id = %s """
                cursor.execute(error_sql, (account_id,))
                connection.commit()

            if error_type == 'suspention':
                outputLog(f"suspention account_id={account_id}")
                error_sql = """ UPDATE account_master SET is_suspended = 1 WHERE id = %s """
                cursor.execute(error_sql, (account_id,))
                connection.commit()

            if error_type == 'unauthorized':
                outputLog(f"unauthorized account_id={account_id}")
                error_sql = """ UPDATE account_master SET is_unauthorized = 1 WHERE id = %s """
                cursor.execute(error_sql, (account_id,))
                connection.commit()
	    # 2026.04.04 End account_masterのフラグ更新

    except Exception as ex:
        # DB周りでエラーが起きてもプログラム全体を落とさない
        outputLog(f"save_tweet_history DB Error: {str(ex)}")
    finally:
        if connection:
            connection.close()

def update_check_account_list(id, since_id, datetime):
    outputLog("update_check_account_list")
    connection = pymysql.connect(
        host=config.db_host,
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
        host=config.db_host,
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

#            outputLog(sql)
#            outputLog(id)
#            outputLog(tweet_id)
#            outputLog(datetime)

            cursor.execute(sql, (tweet_id , datetime , id))
#            sql = """
#                UPDATE check_account_list set since_id = %s , since_datetime = %s , since_comment = %s where id = %s
#            """
#            cursor.execute(sql, (since_id , datetime , truncate_by_byte_length(since_comment, 100), id))
            connection.commit()
    finally:
        connection.close()   


def update_refresh_token(account_id, bearer_token, refresh_token, num):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            if num == 0:
                sql = """
                    UPDATE account_master set bearer_token = %s , refresh_token = %s , refresh_updatetime = NOW() where id = %s
                """
            elif num == 1:
                sql = """
                    UPDATE account_master set bearer_token_1 = %s , refresh_token_1 = %s , refresh_updatetime_1 = NOW() where id = %s
                """
            elif num == 2:
                sql = """
                    UPDATE account_master set bearer_token_2 = %s , refresh_token_2 = %s , refresh_updatetime_2 = NOW() where id = %s
                """
            elif num == 3:
                sql = """
                    UPDATE account_master set bearer_token_3 = %s , refresh_token_3 = %s , refresh_updatetime_3 = NOW() where id = %s
                """
            cursor.execute(sql, (bearer_token , refresh_token , account_id))
            connection.commit()
    finally:
        connection.close()        
 
def get_user_id_from_db(check_list_id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
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
#                outputLog(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None

            return credentials['target_user_id']
    finally:
        connection.close()

def get_slice_id_from_db(user_name , search_replies):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
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
#                outputLog(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
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
        host=config.db_host,      # ホスト名
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
#                outputLog(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                return None , None

            if search_replies == True:
                if config.debug == True:
                    outputLog(f"credentials['last_reply_id'] ={credentials['last_reply_id']}" )
                    outputLog(f"credentials['last_reply_datetime'] ={credentials['last_reply_datetime']}" )
                return credentials['last_reply_id'] , credentials['last_reply_datetime']
            if config.debug == True:
                outputLog(f"credentials['last_tweet_id'] ={credentials['last_tweet_id']}" )
                outputLog(f"credentials['last_tweet_datetime'] ={credentials['last_tweet_datetime']}" )
            return credentials['last_tweet_id'] , credentials['last_tweet_datetime']
    finally:
        connection.close()

    return None


def update_user_id_from_db(id , target_user_id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,
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
        host=config.db_host,
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

#            outputLog(sql)
#            outputLog("id=",id)
#            outputLog("latest_tweet_id=",latest_tweet_id)
#            outputLog("latest_tweet_dt=",latest_tweet_datetime)
            cursor.execute(sql, (latest_tweet_id , latest_tweet_datetime , id ))
            connection.commit()
    finally:
        connection.close()              

def insert_tweet_history_monomane(search_row , ref_tweet , own_tweet):

    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        outputLog(f"ref_tweet={ref_tweet}")
        outputLog(f"own_tweet={own_tweet}")
#        outputLog(f"ref_tweet={ref_tweet.data}")

        account_id = search_row.get('monomane_account_id',None)

        ref_created_at = convert_tweet_datetime(ref_tweet.get('created_at',None))
#        ref_created_at = convert_tweet_datetime(ref_tweet['created_at'])


    except Exception as ex:
        outputLog("予期しないエラーが発生しました:")
        outputLog(str(ex)) 

    try:        

        ref_tweet_id = ref_tweet.get('id',None)
        ref_author_id = ref_tweet.get('author_id',None)
        ref_text = ref_tweet.get('text',None)
#       ref_edit_history_tweet_ids = ref_tweet.get('edit_history_tweet_ids',None)
        ref_in_reply_to_user_id = ref_tweet.get('in_reply_to_user_id',None)


#        outputLog(f"account_id={account_id}")

        # 'referenced_tweets' の最初の要素から id と type を取得
        referenced_tweets = ref_tweet.get('referenced_tweets',None)  # 存在しない場合はNone

        if referenced_tweets:  # 'referenced_tweets' が存在し、リストが空でない場合
            first_ref = referenced_tweets[0]  # 最初の要素
            ref_target_tweet_id = first_ref.get('id', None)  # 'id'がない場合はNone
            ref_tweet_type = first_ref.get('type', None)  # 'type'がない場合はNone
        else:
            ref_target_tweet_id = None
            ref_tweet_type = None


        if own_tweet:

#            created_at = convert_tweet_datetime(own_tweet.get('created_at',None))
#            created_at = convert_tweet_datetime(own_tweet['created_at'])
            created_at = None

            tweet_id = own_tweet.get('id',None)
            text = own_tweet.get('text',None)
        else:
            created_at = None
            tweet_id = None
            text = None

        outputLog(f"account_id={account_id}")
        outputLog(f"ref_created_at={ref_created_at}")
        outputLog(f"ref_tweet_id={ref_tweet_id}")
        outputLog(f"ref_author_id={ref_author_id}")
        outputLog(f"ref_text={ref_text}")
        outputLog(f"ref_in_reply_to_user_id={ref_in_reply_to_user_id}")
        outputLog(f"ref_target_tweet_id={ref_target_tweet_id}")
        outputLog(f"ref_tweet_type={ref_tweet_type}")
        outputLog(f"created_at={created_at}")
        outputLog(f"tweet_id={tweet_id}")
        outputLog(f"text={text}")

        with connection.cursor() as cursor:
            sql = """
                INSERT INTO tweet_history_monomane (
                    account_id,
                    ref_created_at,
                    ref_tweet_id,
                    ref_author_id,
                    ref_text,
                    ref_in_reply_to_user_id,
                    ref_tweet_type,
                    ref_target_tweet_id,
                    created_at,
                    tweet_id,
                    text
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                account_id,
                ref_created_at,
                ref_tweet_id,
                ref_author_id,
                ref_text,
                ref_in_reply_to_user_id,
                ref_tweet_type,
                ref_target_tweet_id,
                created_at,
                tweet_id,
                text
            ))
            connection.commit()
    except Exception as ex:
        outputLog("予期しないエラーが発生しました:")
        outputLog(str(ex))                
    finally:
        connection.close() 


def getOwnTweetId(account_id , reply_target_tweet_id):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            outputLog(f"saccount_id={account_id}")    
            outputLog(f"reply_target_tweet_id={reply_target_tweet_id}")    
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT tweet_id FROM tweet_history_monomane WHERE account_id = %s and ref_tweet_id = %s"
#            sql = "SELECT id , api_key, api_key_secret, access_token, access_token_secret , bearer_token , client_id , client_secret , refresh_token , login_id FROM account_master WHERE id = %s"
            cursor.execute(sql, (account_id,reply_target_tweet_id))
            credentials = cursor.fetchone()

            # データが取得できなかった場合はNoneを返す
            if credentials is None:
#                outputLog(f"ユーザー名 '{user_name}' に対応するデータが見つかりませんでした。")
                outputLog(f"credentials is None")
                return False , None

            outputLog(f"credentials['tweet_id']={credentials['tweet_id']}")
            return True , credentials['tweet_id']

    finally:
        connection.close()

    return False , None


def insert_search_history(search_row , tweet_data , mode):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        outputLog(f"search_row={search_row}")
        outputLog(f"tweet_data={tweet_data}")

        search_id = search_row['id']
        search_user_name = search_row['search_user_name']
        search_user_id = search_row['search_user_id']
        tweet_id = tweet_data['id']
        created_at = tweet_data['created_at']
        contents = tweet_data['text']

        outputLog(f"search_id={search_id}")
        outputLog(f"search_user_name={search_user_name}")
        outputLog(f"created_at={created_at}")

        with connection.cursor() as cursor:
            sql = """
                INSERT INTO search_history (
                `search_id`,
                `search_user_name`,
                `search_user_id`,
                `mode`,
                `tweet_id`,
                `created_at`,
                `contents`)
                 VALUES (%s, %s, %s, %s, %s, %s, %s )
            """
            cursor.execute(sql, (
                search_id,
                search_user_name,
                search_user_id,
                mode,
                tweet_id,
                created_at,
                contents
            ))
            connection.commit()

    except Exception as ex:
        outputLog("予期しないエラーが発生しました:")
        outputLog(str(ex))                
    finally:
        connection.close() 



def get_search_history(mode):
    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )
    try:
        with connection.cursor() as cursor:
            # 認証情報を格納しているテーブルからデータを取得
            sql = "SELECT * FROM search_history WHERE mode = %s"
            cursor.execute(sql, (mode))
            records = cursor.fetchall()  # すべてのレコードを取得
            credentials = cursor.fetchone()
            
            # データが取得できなかった場合は空リストを返す
            if not records:
                outputLog(f"mode '{mode}' に対応するデータが見つかりませんでした。")
                return False, []

            outputLog(f"取得したレコード数: {len(records)}")
            return True, records  # すべてのレコードを返す

    finally:
        connection.close()

    return False , None


def get_trend_list_keyword():

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',           # ユーザー名
        password='abcd1234',   # パスワード
        database='d_bot',      # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # 1時間以内のユニークなキーワードを取得（ポスト・フォローを除外）
            sql = """
                SELECT DISTINCT keyword
                FROM trend_list
                WHERE retrieved_at >= NOW() - INTERVAL 1 HOUR
                  AND keyword NOT LIKE '%ポスト%'
                  AND keyword NOT LIKE '%フォロー%'
            """
            cursor.execute(sql)
            results = cursor.fetchall()
    finally:
        connection.close()

    if not results:
        outputLog("エラー: トレンドキーワードが見つかりません。")
        return None

    # キーワードだけのリストにする
    keywords = [row["keyword"] for row in results]

    if len(keywords) < 2:
        outputLog("エラー: キーワードが2つ未満です。")
        return None

    # ランダムに2つ選ぶ
    return random.sample(keywords, 2)

def get_tweet_profile_by_display_name(display_name):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # display_name に一致する path を取得
            sql = "SELECT * FROM get_tweet_profile WHERE display_name = %s"
            cursor.execute(sql, (display_name,))  # ← tuple にするためカンマが必要
            record = cursor.fetchone()            # record は {"path": "..."} の形で返る
    finally:
        connection.close()

    if not record:  # ← result → record に修正
        outputLog("エラー: 該当するプロファイルが見つかりません。")
        return None

    return record

def get_tweet_profile_by_vps_id(vps_id):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT *
                FROM get_tweet_profile
                WHERE vps_id = %s
                ORDER BY (check_time IS NOT NULL), check_time ASC
                LIMIT 1
            """
            cursor.execute(sql, (vps_id,))  # ← tuple にするためカンマが必要
            record = cursor.fetchone()            # record は {"path": "..."} の形で返る
    finally:
        connection.close()

    if not record:  # ← result → record に修正
        outputLog("エラー: 該当するプロファイルが見つかりません。")
        return None

    return record


def update_get_tweet_profile(record):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:

            sql = """
                UPDATE get_tweet_profile set display_name = %s , path = %s where id = %s
            """
            cursor.execute(sql, (record['display_name'] , record['path'] , record['id'] ))
            connection.commit()
    finally:
        connection.close()   

    if not record:  # ← result → record に修正
        outputLog("エラー: 該当するプロファイルが見つかりません。")
        return None

    return record


def add_check_tweet_account_master_by_account_name(account_name):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO check_tweet_account_master (account_name)
                VALUES (%s)
            """
            cursor.execute(sql, (account_name))
            connection.commit() 
    finally:
        connection.close()

def get_check_tweet_account_master_by_account_name(account_name):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # display_name に一致する path を取得
            sql = "SELECT * FROM check_tweet_account_master WHERE account_name = %s"
            cursor.execute(sql, (account_name,))  # ← tuple にするためカンマが必要
            record = cursor.fetchone()            # record は {"path": "..."} の形で返る
    finally:
        connection.close()

    if not record:  
        outputLog("エラー: 該当するレコードが見つかりません。")
        return None

    return record

def get_check_tweet_account_masters_by_vps_id(vps_id):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # display_name に一致する path を取得
            sql = "SELECT * FROM check_tweet_account_master WHERE vps_id = %s"
            cursor.execute(sql, (vps_id,))  # ← tuple にするためカンマが必要
            record = cursor.fetchall()     
    finally:
        connection.close()

    if not record:  
        outputLog("エラー: 該当するレコードが見つかりません。")
        return None

    return record


def update_check_tweet_account_master(record):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    print(record)

    try:
        with connection.cursor() as cursor:

            sql = """
                UPDATE check_tweet_account_master set account_name = %s , user_id = %s , result = %s where id = %s
            """
            cursor.execute(sql, (record['account_name'] , record['user_id'] , record['result'] , record['id'] ))
            connection.commit()
    finally:
        connection.close()   

    if not record:  # ← result → record に修正
        outputLog("エラー: 該当するプロファイルが見つかりません。")
        return None

    return record

def get_check_tweet_account_list_by_user_id(user_id):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # display_name に一致する path を取得
            sql = "SELECT * FROM check_tweet_account_list WHERE user_id = %s"
            cursor.execute(sql, (user_id,))  # ← tuple にするためカンマが必要
            record = cursor.fetchone()            # record は {"path": "..."} の形で返る
    finally:
        connection.close()

    if not record:  
        outputLog("エラー: 該当するレコードが見つかりません。")
        return None

    return record

def get_check_tweet_account_list_by_tweet_id(tweet_id):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            # display_name に一致する path を取得
            sql = "SELECT * FROM check_tweet_account_list WHERE tweet_id = %s"
            cursor.execute(sql, (tweet_id,))  # ← tuple にするためカンマが必要
            record = cursor.fetchone()            # record は {"path": "..."} の形で返る
    finally:
        connection.close()

    if not record:  
        outputLog("エラー: 該当するレコードが見つかりません。")
        return None

    return record    

def update_check_tweet_account_list(record):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

#    outputLog("update_check_tweet_account_list record =", record)

    if not record:
        outputLog("エラー: record が空です。")
        return None


    try:
        with connection.cursor() as cursor:
            # user_id が PRIMARY（または UNIQUE）前提の UPSERT
            sql = """
                INSERT INTO check_tweet_account_list
                    (account_name, user_id, tweet_id, tweet_text,
                     check_time, update_time, type,
                     reply_to_tweet_id, reply_to_user_id, reply_to_screen_name)
                VALUES
                    (%s, %s, %s, %s,
                     %s, %s, %s,
                     %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    account_name       = VALUES(account_name),
                    tweet_id           = VALUES(tweet_id),
                    tweet_text         = VALUES(tweet_text),
                    check_time         = VALUES(check_time),
                    update_time        = VALUES(update_time),
                    type               = VALUES(type),
                    reply_to_tweet_id  = VALUES(reply_to_tweet_id),
                    reply_to_user_id   = VALUES(reply_to_user_id),
                    reply_to_screen_name = VALUES(reply_to_screen_name)
            """
            cursor.execute(sql, (
                record['account_name'],
                record['user_id'],
                record['tweet_id'],
                record['text'],
                record['check_time'],
                record['created_at_jst'],
                record['type'],
                record.get('reply_to_tweet_id'),
                record.get('reply_to_user_id'),
                record.get('reply_to_screen_name'),
            ))
            connection.commit()
    finally:
        connection.close()

    return record

def update_check_tweet_account_list_bk(record):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    outputLog("update_check_tweet_account_list record = ",record)

    try:
        with connection.cursor() as cursor:

            sql = """
                UPDATE check_tweet_account_list set check_time = %s , update_time = %s , user_id = %s , tweet_text = %s where tweet_id = %s
            """
            cursor.execute(sql, (record['check_time'] , record['created_at_jst'] , record['user_id'] , record['text'] , record['tweet_id'] ))
            connection.commit()
    finally:
        connection.close()   

    if not record:  # ← result → record に修正
        outputLog("エラー: 該当するプロファイルが見つかりません。")
        return None

    return record    


    
def get_vps_master_by_ip_address(ip_address):

    # MySQLデータベースに接続
    connection = pymysql.connect(
        host=config.db_host,      # ホスト名
        user='root',              # ユーザー名
        password='abcd1234',      # パスワード
        database='d_bot',         # データベース名
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor        
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM vps_master WHERE ip_address = %s"
            cursor.execute(sql, (ip_address,))  # ← tuple にするためカンマが必要
            record = cursor.fetchone()            # record は {"path": "..."} の形で返る
    finally:
        connection.close()

    if not record:  
        outputLog("エラー: 該当するレコードが見つかりません。")
        return None

    return record


def init_check_tweet_account_master_by_search_list():
    def sync_flags():
        conn = pymysql.connect(
            host=config.db_host,
            user="root",
            password="abcd1234",
            database="d_bot",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        try:
            with conn.cursor() as cur:
                # 集約して1アカウント1行にする
                cur.execute("""
                    CREATE TEMPORARY TABLE active_accounts (
                        account_key   VARCHAR(255) PRIMARY KEY,
                        account_name  VARCHAR(255),
                        tweet_flag    TINYINT(1),
                        reply_flag    TINYINT(1)
                    ) AS
                    SELECT
                        REPLACE(LOWER(TRIM(sl.search_user_name)),'@','') AS account_key,
                        TRIM(sl.search_user_name)                         AS account_name,
                        MAX(
                            CASE 
                            WHEN sl.post_enable = 1 OR sl.monomane_enable = 1 
                                THEN 1 ELSE 0 
                            END
                        ) AS tweet_flag,                        
                        MAX(sl.reply_enable)                              AS reply_flag
                    FROM search_list sl
                    LEFT JOIN ACCOUNT_MASTER am on am.id = sl.account_id
                    LEFT JOIN USER_MASTER um on um.id = am.user_id
                    WHERE TRIM(sl.search_user_name) <> ''
                      AND sl.search_user_name IS NOT NULL
                      AND sl.enable = '1'
                      AND um.enable = '1'
                      AND am.enable = '1'
                    GROUP BY REPLACE(LOWER(TRIM(sl.search_user_name)),'@',''),
                             TRIM(sl.search_user_name)
                """)

                # UPSERTで反映
                cur.execute("""
                    INSERT INTO check_tweet_account_master (account_name, tweet_enable, reply_enable)
                    SELECT a.account_name, a.tweet_flag, a.reply_flag
                    FROM active_accounts a
                    ON DUPLICATE KEY UPDATE
                        tweet_enable = VALUES(tweet_enable),
                        reply_enable = VALUES(reply_enable),
                        account_name = VALUES(account_name)
                """)

                # search_listに存在しないアカウントは両方0にする
                cur.execute("""
                    UPDATE check_tweet_account_master t
                    LEFT JOIN active_accounts a
                      ON a.account_key = REPLACE(LOWER(TRIM(t.account_name)),'@','')
                    SET t.tweet_enable = 0,
                        t.reply_enable = 0
                    WHERE a.account_key IS NULL
                """)

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # 実行
    sync_flags()
    update_check_tweet_account_master_on_vps_id()

def init_check_tweet_account_master_by_search_list_gomi():
    conn = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

    try:
        with conn.cursor() as cur:
            # 1) 有効アカウントの一時テーブル（NULL/空文字は除外、重複除去）
            cur.execute("""
                CREATE TEMPORARY TABLE active_accounts (
                  account_name VARCHAR(255) PRIMARY KEY
                ) AS
                SELECT DISTINCT TRIM(search_user_name) AS account_name
                FROM search_list
                WHERE (post_enable = 1 OR monomane_enable = 1)
                  AND TRIM(search_user_name) <> ''
                  AND search_user_name IS NOT NULL
            """)

            # 2) 有効アカウントをUPSERTで反映（なければINSERT、あればtweet_enable=1に更新）
            #    ※ account_name に UNIQUE もしくは PRIMARY KEY がある前提
            cur.execute("""
                INSERT INTO check_tweet_account_master (account_name, tweet_enable)
                SELECT account_name, 1
                FROM active_accounts
                ON DUPLICATE KEY UPDATE tweet_enable = 1
            """)

            # 3) 集合に含まれない既存は tweet_enable=0 へ
            cur.execute("""
                UPDATE check_tweet_account_master AS t
                LEFT JOIN active_accounts AS a
                  ON a.account_name = t.account_name
                SET t.tweet_enable = 0
                WHERE a.account_name IS NULL
            """)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    conn = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    try:
        with conn.cursor() as cur:
            # 1) 有効アカウントの一時テーブル（NULL/空文字は除外、重複除去）
            cur.execute("""
                CREATE TEMPORARY TABLE active_accounts (
                  account_name VARCHAR(255) PRIMARY KEY
                ) AS
                SELECT DISTINCT TRIM(search_user_name) AS account_name
                FROM search_list
                WHERE (reply_enable = 1)
                  AND TRIM(search_user_name) <> ''
                  AND search_user_name IS NOT NULL
            """)

            # 2) 有効アカウントをUPSERTで反映（なければINSERT、あればtweet_enable=1に更新）
            #    ※ account_name に UNIQUE もしくは PRIMARY KEY がある前提
            cur.execute("""
                INSERT INTO check_tweet_account_master (account_name, reply_enable)
                SELECT account_name, 1
                FROM active_accounts
                ON DUPLICATE KEY UPDATE reply_enable = 1
            """)

            # 3) 集合に含まれない既存は tweet_enable=0 へ
            cur.execute("""
                UPDATE check_tweet_account_master AS t
                LEFT JOIN active_accounts AS a
                  ON a.account_name = t.account_name
                SET t.reply_enable = 0
                WHERE a.account_name IS NULL
            """)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    update_check_tweet_account_master_on_vps_id()



def update_check_tweet_account_master_on_vps_id(seed: int = None):
    """
    VPS_MASTER の check_enable=1 の id を取り出し、
    check_tweet_account_master の tweet_enable または reply_enable が 1 のレコードに
    VPS_ID を均等かつランダムに割り振る処理。
    """

    # === DB接続（あなたの get_connection() を呼ぶ場合は置き換え） ===
    conn = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 1. 有効な VPS を取得
    cur.execute("SELECT id FROM VPS_MASTER WHERE check_enable = 1")
    vps_list = [row["id"] for row in cur.fetchall()]
    if not vps_list:
        outputLog("有効なVPSがありません")
        return

    # 2. 割り当て対象のアカウントを取得
    cur.execute("""
        SELECT id
        FROM check_tweet_account_master
        WHERE tweet_enable = 1 OR reply_enable = 1
    """)
    accounts = [row["id"] for row in cur.fetchall()]
    if not accounts:
        outputLog("対象アカウントがありません")
        return

    # 3. ランダム化
    if seed is not None:
        random.seed(seed)
    random.shuffle(accounts)

    # 4. 均等に割り振り
    assignments = []
    for i, acc_id in enumerate(accounts):
        vps_id = vps_list[i % len(vps_list)]
        assignments.append((vps_id, acc_id))

    # 5. DB更新
    cur.executemany("""
        UPDATE check_tweet_account_master
        SET vps_id = %s
        WHERE id = %s
    """, assignments)

    conn.commit()
    cur.close()
    conn.close()
    outputLog(f"{len(assignments)} 件を割り振りました")

def save_token_usage(proc_name, model_name, prompt_tokens, completion_tokens, total_tokens, cost_usd):
    conn = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO token_usage_log 
                (proc_name, model_name, prompt_tokens, completion_tokens, total_tokens, cost_usd)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                proc_name,
                model_name,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost_usd
            ))
            conn.commit()
    finally:
        conn.close()

def delete_account_error_log(account_id):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM account_error_log WHERE account_id = %s"
            cursor.execute(sql, (account_id,))
            connection.commit()
    finally:
        connection.close()

def unlock_unauthorized(account_id):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:

            sql = "UPDATE account_master set is_unauthorized = 0 WHERE account_id = %s"
            cursor.execute(sql, (account_id,))
            connection.commit()

    finally:
        connection.close()

def get_refresh_queue():
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, account_id FROM refresh_queue WHERE status = 'pending'"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def update_refresh_queue_status(queue_id, status):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE refresh_queue SET status = %s, updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (status, queue_id))
            connection.commit()
    finally:
        connection.close()        

def get_account_error_log_type(account_id):
    connection = pymysql.connect(
        host=config.db_host,
        user='root',
        password='abcd1234',
        database='d_bot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT error_type FROM account_error_log WHERE account_id = %s", (account_id,))
            row = cursor.fetchone()
            return row['error_type'] if row else None
    finally:
        connection.close()