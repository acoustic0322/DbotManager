import pymysql
import config

from datetime import datetime  # datetime モジュールをインポート
from config import outputLog
from config import convert_tweet_datetime

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
            am.ai_post_enable,
            am.ai_reply_enable,
            am.ai_post_prompt,
            am.ai_reply_prompt,
            am.user_id,
            um.GROQ_API_KEY,
            um.OPENAI_API_KEY
            am.ai_mode,
            am.ai_post_enable
            am.ai_reply_enable,
            am.ai_post_prompt,
            am.ai_reply_prompt,
            am.reserve1_ai,
            am.reserve2_ai,
            am.reserve3_ai,
            am.reserve4_ai
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

def get_account_master_for_update_refresh():
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
            sql = """
            SELECT 
            am.id, 
            case am.api_master_id when '0' then am.client_id 
            else api.client_id end as client_id,
            case am.api_master_id when '0' then am.client_secret 
            else api.client_secret end as client_secret, 
            am.refresh_token , 
            am.proxy_enable , 
            am.proxy_url
            FROM account_master am
            left join api_master api on api.id = am.api_master_id            
            WHERE 
                am.refresh_token IS NOT NULL 
                AND am.refresh_updatetime IS NOT NULL
                AND TIMESTAMPDIFF(MINUTE, am.refresh_updatetime, NOW()) > 60
            """
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
            sql = "SELECT id, search_user_name, search_user_id , post_account_id, post_enable , last_post_id , last_post_time , reply_account_id , reply_enable , last_reply_id , last_reply_time , monomane_account_id , monomane_enable , last_monomane_id , last_monomane_time FROM search_list  WHERE id = %s"
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


def update_refresh_token(account_id, bearer_token, refresh_token):
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
                UPDATE account_master set bearer_token = %s , refresh_token = %s , refresh_updatetime = NOW() where id = %s
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
                    outputLog("credentials['last_reply_id'] =",credentials['last_reply_id'] )
                    outputLog("credentials['last_reply_datetime'] =",credentials['last_reply_datetime'] )
                return credentials['last_reply_id'] , credentials['last_reply_datetime']
            if config.debug == True:
                outputLog("credentials['last_tweet_id'] =",credentials['last_tweet_id'] )
                outputLog("credentials['last_tweet_datetime'] =",credentials['last_tweet_datetime'] )
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