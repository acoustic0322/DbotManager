import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
import os
from loguru import logger
import json
import pymysql
import socket
import psycopg2
import psycopg2.extras
import time
import threading

# --- VERSION INFO ---
VERSION = "2.1.1"
# --------------------

DB_PATH = 'system.db'
CONFIG_PATH = 'db_config.json'

class DBManager:
    _initialized = False # Class-level flag to prevent redundant init_db
    _thread_local = threading.local()
    
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self._conn = None
        
        # Identify PC
        hostname = socket.gethostname()
        self.pc_name = hostname
        root_config_path = 'config.json'
        if os.path.exists(root_config_path):
            try:
                with open(root_config_path, 'r', encoding='utf-8') as f:
                    root_cfg = json.load(f)
                    pc_map = root_cfg.get('PC_MAP', {})
                    if hostname in pc_map:
                        self.pc_name = pc_map[hostname]
            except: pass
        
        self.load_config()
        if not DBManager._initialized:
            logger.info(f"Database Manager v{VERSION} Initialized. PC: {self.pc_name}")
            self.init_db()
            DBManager._initialized = True

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.db_type = self.config.get("db_type", "postgres")
            except:
                self.db_type = "sqlite"
                self.config = {}
        else:
            self.db_type = "sqlite"
            self.config = {}
        
        self.mysql_config = self.config.get("mysql", {})
        self.postgres_config = self.config.get("postgres", {})

    def get_connection(self):
        conn = getattr(DBManager._thread_local, "conn", None)
        if conn:
            try:
                if self.db_type == "postgres":
                    # Postgresの生存確認をより確実に（SELECT 1を投げる）
                    if conn.closed != 0:
                        raise Exception("Postgres Connection Closed")
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                elif self.db_type == "mysql":
                    conn.ping(reconnect=False)
            except Exception:
                logger.warning("DB connection is dead. Reconnecting...")
                DBManager._thread_local.conn = None
                conn = None

        if conn:
            return conn

        if self.db_type == "mysql":
            conf = self.mysql_config
            conn = pymysql.connect(
                host=conf.get("host", "localhost"),
                user=conf.get("user", "root"),
                password=conf.get("password", ""),
                database=conf.get("database", "twitter_ix"),
                port=conf.get("port", 3306),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        elif self.db_type == "postgres":
            conf = self.postgres_config
            # Port optimization for Supabase
            if 'uri' in conf and 'pooler.supabase.com' in conf['uri'] and ':5432' in conf['uri']:
                conf['uri'] = conf['uri'].replace(':5432', ':6543')
            
            timeout = 20
            max_retries = 3 # 試行回数を少し減らして早めに切り替える
            for attempt in range(max_retries):
                try:
                    if 'uri' in conf:
                        conn = psycopg2.connect(conf['uri'], cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=timeout)
                    else:
                        conn = psycopg2.connect(
                            host=conf.get("host", "localhost"),
                            port=conf.get("port", 6543),
                            user=conf.get("user", "postgres"),
                            password=conf.get("password", ""),
                            dbname=conf.get("database", "postgres"),
                            cursor_factory=psycopg2.extras.RealDictCursor,
                            connect_timeout=timeout
                        )
                    conn.autocommit = True
                    DBManager._thread_local.conn = conn
                    logger.success(f"Connected to Cloud DB (Attempt {attempt+1}).")
                    return conn
                except Exception as e:
                    logger.warning(f"Cloud DB Connection Attempt {attempt+1} failed: {e}")
                    if attempt == max_retries - 1: 
                        logger.error("❌ Cloud DB is unreachable. Falling back to LOCAL SQLite to keep the system running.")
                        self.db_type = "sqlite" # [FAILSAFE] SQLiteに切り替え
                        return self.get_connection()
                    time.sleep(2)
        else:
            # SQLite Connection
            try:
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                DBManager._thread_local.conn = conn
                logger.info(f"Using Local SQLite Database: {DB_PATH}")
            except Exception as e:
                logger.error(f"Critical: Failed to even open SQLite: {e}")
                raise e
            
        return DBManager._thread_local.conn

    def get_connection_dbot(self):
        conn = getattr(DBManager._thread_local, "conn", None)
        if conn:
            try:
                conn.ping(reconnect=False)
            except Exception:
                logger.warning("DB connection is dead. Reconnecting...")
                DBManager._thread_local.conn = None
                conn = None

        if conn:
            return conn

        conf = self.mysql_config
        conn = pymysql.connect(               
            host=conf.get("host", "203.137.53.205"),
            user=conf.get("user", "root"),
            password=conf.get("password", "abcd1234"),
            database=conf.get("database", "d_bot"),
            port=conf.get("port", 3306),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True                
        )
            
        return DBManager._thread_local.conn
        
    def init_db(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.db_type in ["mysql", "postgres"]:
                text_type = "VARCHAR(255)" if self.db_type == 'mysql' else "TEXT"
                time_type = "DATETIME" if self.db_type == 'mysql' else "TIMESTAMP"
                
                # Accounts Table
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS accounts (
                    username {text_type} PRIMARY KEY,
                    screen_name {text_type},
                    password TEXT,
                    email TEXT,
                    auth_token TEXT,
                    ct0 TEXT,
                    cookies TEXT,
                    user_agent TEXT,
                    sec_ch_ua TEXT,
                    impersonate TEXT,
                    totp_secret TEXT,
                    profile_id TEXT,
                    group_id TEXT,
                    group_name TEXT,
                    category TEXT,
                    assigned_name TEXT,
                    profile_updated BOOLEAN DEFAULT FALSE,
                    sync_status TEXT,
                    selected INTEGER DEFAULT 1,
                    is_alive INTEGER DEFAULT 1,
                    daily_follow_count INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 10,
                    last_active_date TEXT,
                    display_name TEXT,
                    name TEXT,
                    biography TEXT,
                    last_tweet_at {time_type},
                    last_full_check {time_type},
                    claimed_by TEXT,
                    claimed_at {time_type},
                    assigned_pc TEXT,
                    in_use INTEGER DEFAULT 0,
                    following_count INTEGER DEFAULT 0,
                    followers_count INTEGER DEFAULT 0,
                    reach_status TEXT DEFAULT 'OK'
                )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_screen_name ON accounts (screen_name)")
                
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    username {text_type},
                    date DATE,
                    action_type {text_type},
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (username, date, action_type)
                )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats (date)")
                
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS system_commands (
                    id SERIAL PRIMARY KEY,
                    command {text_type},
                    params TEXT,
                    created_at {time_type} DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                if self.db_type == "postgres": conn.commit()
            else:
                # SQLite Implementation
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    username TEXT PRIMARY KEY,
                    screen_name TEXT,
                    password TEXT,
                    email TEXT,
                    auth_token TEXT,
                    ct0 TEXT,
                    cookies TEXT,
                    user_agent TEXT,
                    sec_ch_ua TEXT,
                    impersonate TEXT,
                    totp_secret TEXT,
                    profile_id TEXT,
                    group_id TEXT,
                    group_name TEXT,
                    category TEXT,
                    assigned_name TEXT,
                    profile_updated BOOLEAN DEFAULT FALSE,
                    sync_status TEXT,
                    selected INTEGER DEFAULT 1,
                    is_alive INTEGER DEFAULT 1,
                    daily_follow_count INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 10,
                    last_active_date TEXT,
                    display_name TEXT,
                    name TEXT,
                    biography TEXT,
                    last_tweet_at TEXT,
                    last_full_check TEXT,
                    claimed_by TEXT,
                    claimed_at TEXT,
                    assigned_pc TEXT,
                    in_use INTEGER DEFAULT 0,
                    following_count INTEGER DEFAULT 0,
                    followers_count INTEGER DEFAULT 0,
                    reach_status TEXT DEFAULT 'OK'
                )
                ''')
                cursor.execute('CREATE TABLE IF NOT EXISTS system_commands (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, params TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
                conn.commit()
            
            # --- Column Migrations ---
            try:
                if self.db_type == "sqlite":
                    cursor.execute("PRAGMA table_info(accounts)")
                    columns = [info[1].lower() for info in cursor.fetchall()]
                else:
                    cursor.execute("SELECT * FROM accounts LIMIT 1")
                    columns = [desc[0].lower() for desc in cursor.description]
                
                migration_cols = {
                    'screen_name': 'TEXT',
                    'password': 'TEXT',
                    'email': 'TEXT',
                    'auth_token': 'TEXT',
                    'ct0': 'TEXT',
                    'cookies': 'TEXT',
                    'user_agent': 'TEXT',
                    'sec_ch_ua': 'TEXT',
                    'impersonate': 'TEXT',
                    'totp_secret': 'TEXT',
                    'profile_id': 'TEXT',
                    'group_id': 'TEXT',
                    'group_name': 'TEXT',
                    'category': 'TEXT',
                    'assigned_name': 'TEXT',
                    'profile_updated': 'BOOLEAN DEFAULT FALSE',
                    'sync_status': 'TEXT',
                    'selected': 'INTEGER DEFAULT 1',
                    'is_alive': 'INTEGER DEFAULT 1',
                    'daily_follow_count': 'INTEGER DEFAULT 0',
                    'daily_limit': 'INTEGER DEFAULT 10',
                    'last_active_date': 'TEXT',
                    'display_name': 'TEXT',
                    'name': 'TEXT',
                    'biography': 'TEXT',
                    'last_tweet_at': 'TEXT',
                    'last_full_check': 'TEXT',
                    'claimed_by': 'TEXT',
                    'claimed_at': 'TEXT',
                    'assigned_pc': 'TEXT',
                    'in_use': 'INTEGER DEFAULT 0',
                    'following_count': 'INTEGER DEFAULT 0',
                    'followers_count': 'INTEGER DEFAULT 0',
                    'reach_status': "TEXT DEFAULT 'OK'"
                }
                
                for col_name, col_type in migration_cols.items():
                    if col_name.lower() not in columns:
                        logger.info(f"Adding '{col_name}' column to accounts table...")
                        t = "VARCHAR(255)" if self.db_type == "mysql" and "TEXT" in col_type else col_type
                        cursor.execute(f"ALTER TABLE accounts ADD COLUMN {col_name} {t}")
                
                if self.db_type in ["postgres", "sqlite"]: conn.commit()
            except Exception as e:
                logger.warning(f"Migration error: {e}")

            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"DB Init Error: {e}")
            raise e

    def _placeholder(self):
        return "%s" if self.db_type in ["mysql", "postgres"] else "?"

    def get_all_accounts_from_db(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # SQL側で文字列整形（@の除去など）を済ませることで、Python側の負担を激減させる
            sql = """
                SELECT 
                    username, 
                    TRIM(REPLACE(COALESCE(screen_name, username), '@', '')) as screen_name, 
                    display_name, 
                    sync_status, 
                    is_alive, 
                    selected, 
                    category, 
                    last_active_date, 
                    last_tweet_at,
                    group_name,
                    auth_token,
                    ct0,
                    cookies,
                    user_agent,
                    sec_ch_ua,
                    impersonate,
                    password,
                    email,
                    totp_secret,
                    profile_id,
                    assigned_pc,
                    following_count,
                    followers_count
                FROM accounts 
                ORDER BY screen_name ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Fetch Error: {e}")
            return []

    def get_all_accounts_df(self):
        # 期待されるカラムリスト（KeyError防止用）
        expected_cols = [
            'username', 'screen_name', 'display_name', 'sync_status', 
            'is_alive', 'selected', 'category', 'last_active_date', 'last_tweet_at', 
            'group_name', 'auth_token', 'ct0', 'cookies', 'user_agent', 'sec_ch_ua', 'impersonate',
            'password', 'email', 'totp_secret', 'profile_id', 'assigned_pc',
            'following_count', 'followers_count'
        ]
        accounts_list = self.get_all_accounts_from_db()
        if not accounts_list: 
            return pd.DataFrame(columns=expected_cols)
            
        df = pd.DataFrame(accounts_list)
        # SQL側で整形済みなので、カラム名の調整とフラグ変換のみに絞る
        df.columns = [c.lower() for c in df.columns]
        
        # 不足しているカラムがあれば補完
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        df = df.rename(columns={'selected': 'Select'})
        df['Select'] = df['Select'].apply(lambda x: True if str(x) in ['1', 'True', 'true'] else False)
        df['is_suspended'] = df['is_alive'].apply(lambda x: False if str(x) in ['1', 'True', 'true'] else True)
        return df

    def save_accounts_df(self, df):
        if df.empty: return True
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            
            # 保存対象のカラム定義
            core_cols = [
                'auth_token', 'ct0', 'cookies', 'user_agent', 'sec_ch_ua', 'impersonate',
                'password', 'email', 'totp_secret', 'profile_id', 'group_id', 'group_name',
                'category', 'display_name', 'assigned_pc'
            ]
            existing_core_cols = [c for c in core_cols if c in df.columns]
            
            # 全カラムリスト（UPSERT用）
            all_cols = ['username', 'selected', 'is_alive'] + existing_core_cols
            
            data_to_save = []
            for _, row in df.iterrows():
                username = str(row.get('username') or row.get('screen_name', '')).replace('@', '').strip()
                if not username: continue
                is_sel = 1 if row.get('Select') or row.get('selected') else 0
                is_alive = 0 if row.get('is_suspended', False) else 1
                
                vals = [username, is_sel, is_alive]
                for col in existing_core_cols:
                    val = row.get(col, "")
                    # NaN または NULL の場合は空文字にする
                    if pd.isna(val) or str(val).lower() == 'nan':
                        val = ""
                    vals.append(str(val))
                data_to_save.append(tuple(vals))

            # データベースごとのUPSERT構文（新規追加と更新を同時に行う）
            if self.db_type == "postgres":
                cols_str = ", ".join(all_cols)
                placeholders = ", ".join([p] * len(all_cols))
                update_parts = ", ".join([f"{c} = EXCLUDED.{c}" for c in all_cols if c != 'username'])
                sql = f"INSERT INTO accounts ({cols_str}) VALUES ({placeholders}) ON CONFLICT (username) DO UPDATE SET {update_parts}"
                from psycopg2.extras import execute_batch
                execute_batch(cursor, sql, data_to_save, page_size=100)
                conn.commit()
            elif self.db_type == "mysql":
                cols_str = ", ".join(all_cols)
                placeholders = ", ".join([p] * len(all_cols))
                update_parts = ", ".join([f"{c} = VALUES({c})" for c in all_cols if c != 'username'])
                sql = f"INSERT INTO accounts ({cols_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_parts}"
                cursor.executemany(sql, data_to_save)
                conn.commit()
            else: # SQLite
                cols_str = ", ".join(all_cols)
                placeholders = ", ".join([p] * len(all_cols))
                sql = f"INSERT OR REPLACE INTO accounts ({cols_str}) VALUES ({placeholders})"
                cursor.executemany(sql, data_to_save)
                conn.commit()
            
    	    self.save_accounts_df_for_dbot(self, df)

            return True
        except Exception as e:
            logger.error(f"Save DF Error (UPSERT): {e}")
            return False

    def save_accounts_df_for_dbot(self, df):
        if df.empty: return True
        try:
            conn = self.get_connection_dbot()
            cursor = conn.cursor()
            p = self._placeholder()
            
            # 保存対象のカラム定義
#            core_cols = [
#                'auth_token', 'ct0', 'cookies', 'user_agent', 'sec_ch_ua', 'impersonate',
#                'password', 'email', 'totp_secret', 'profile_id', 'group_id', 'group_name',
#                'category', 'display_name', 'assigned_pc'
#            ]
            core_cols = [
                'auth_token', 'ct0', 'cookies', 'user_agent', 'sec_ch_ua', 'inpersonate',
                'login_password', 'email', 'totp_secret', 'twitter_user_id', 'group_id', 'group_name',
                'category', 'display_name', 'assigned_pc'
            ]
            existing_core_cols = [c for c in core_cols if c in df.columns]
            
            # 全カラムリスト（UPSERT用）
#            all_cols = ['username', 'selected', 'is_alive'] + existing_core_cols
            all_cols = ['name', 'selected', 'is_alive'] + existing_core_cols
            
            data_to_save = []
            for _, row in df.iterrows():
                username = str(row.get('username') or row.get('screen_name', '')).replace('@', '').strip()
                if not username: continue
                is_sel = 1 if row.get('Select') or row.get('selected') else 0
                is_alive = 0 if row.get('is_suspended', False) else 1
                
                vals = [username, is_sel, is_alive]
                for col in existing_core_cols:
                    val = row.get(col, "")
                    # NaN または NULL の場合は空文字にする
                    if pd.isna(val) or str(val).lower() == 'nan':
                        val = ""
                    vals.append(str(val))
                data_to_save.append(tuple(vals))

            if True:
                cols_str = ", ".join(all_cols)
                placeholders = ", ".join([p] * len(all_cols))
                update_parts = ", ".join([f"{c} = VALUES({c})" for c in all_cols if c != 'username'])
                sql = f"INSERT INTO account_master ({cols_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_parts}"
                cursor.executemany(sql, data_to_save)
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Save DF Error (UPSERT): {e}")
            return False


    def get_daily_stats(self):
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"SELECT * FROM daily_stats WHERE date = {p}", (today,))
            return cursor.fetchall()
        except: return []

    def record_daily_action(self, username, action_type, count=1):
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"SELECT count FROM daily_stats WHERE username={p} AND date={p} AND action_type={p}", (username, today, action_type))
            if cursor.fetchone():
                cursor.execute(f"UPDATE daily_stats SET count = count + {p} WHERE username={p} AND date={p} AND action_type={p}", (count, username, today, action_type))
            else:
                cursor.execute(f"INSERT INTO daily_stats (username, date, action_type, count) VALUES ({p}, {p}, {p}, {p})", (username, today, action_type, count))
            cursor.execute(f"UPDATE accounts SET last_active_date={p} WHERE username={p}", (today, username))
            if self.db_type == "postgres": conn.commit()
        except: pass

    def update_account_selection(self, username, selected):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET selected={p} WHERE username={p}", (1 if selected else 0, username))
            if self.db_type == "postgres": conn.commit()
        except: pass

    def update_all_selection_status(self, selected, screen_names=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            val = 1 if selected else 0
            if screen_names:
                if not screen_names: return
                chunk_size = 200
                for k in range(0, len(screen_names), chunk_size):
                    chunk = screen_names[k:k+chunk_size]
                    placeholders = ", ".join([p] * len(chunk))
                    cursor.execute(f"UPDATE accounts SET selected={val} WHERE username IN ({placeholders})", tuple(chunk))
            else:
                cursor.execute(f"UPDATE accounts SET selected={val}")
            if self.db_type not in ["mysql", "postgres"]:
                conn.commit()
            elif self.db_type == "postgres": 
                conn.commit()
        except: pass

    def update_sync_status(self, username, status, retry=True):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET sync_status = {p} WHERE username = {p}", (status, username))
            if self.db_type == "postgres": conn.commit()
        except Exception as e:
            if retry:
                logger.warning(f"Connection lost during update_sync_status. Retrying once... ({e})")
                DBManager._thread_local.conn = None
                self.update_sync_status(username, status, retry=False)
            else:
                logger.error(f"DB Error update_sync_status (Permanent): {e}")

    def clear_failure_states(self, username):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(
                f"UPDATE accounts SET sync_status='', is_alive=1, in_use=0 WHERE username={p}",
                (username,)
            )
            DBManager._thread_local.conn = conn
            if self.db_type == "postgres":
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"DB Error clear_failure_states: {e}")
            return False

    def bulk_clear_sync_status(self, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            
            # ステータスが "|" で区切られた複数条件の場合への対応（簡易的な正規表現風）
            # is_alive=1 に戻すことで画面から確実に消す
            if '|' in status:
                conditions = status.split('|')
                for cond in conditions:
                    if cond.strip():
                        cursor.execute(f"UPDATE accounts SET sync_status = '', is_alive = 1 WHERE sync_status LIKE {p}", (f"%{cond.strip()}%",))
            else:
                cursor.execute(f"UPDATE accounts SET sync_status = '', is_alive = 1 WHERE sync_status LIKE {p}", (f"%{status}%",))
                
            if self.db_type == "postgres": conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error bulk_clear_sync_status: {e}")
            return False

    def set_global_command(self, command, params=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            params_json = json.dumps(params) if params else "{}"
            cursor.execute("DELETE FROM system_commands")
            cursor.execute(f"INSERT INTO system_commands (command, params) VALUES ({p}, {p})", (command, params_json))
            if self.db_type == "postgres": conn.commit()
            logger.info(f"Command Sent: {command}")
        except: pass

    def get_global_command(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM system_commands ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
        except: return None

    def clear_global_command(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM system_commands")
            if self.db_type == "postgres": conn.commit()
            logger.info("Global command table cleared.")
        except: pass

    def reset_all_in_use(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"UPDATE accounts SET in_use=0")
            if self.db_type == "postgres": conn.commit()
            logger.info("All accounts reset from in_use state.")
        except: pass

    def get_next_account(self, target_usernames=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            
            # NG判定: ロック・凍結・実行失敗・ログイン失敗は除外。完了・正常・その他は再実行OK
            like_percent = "%%" if self.db_type in ["mysql", "postgres"] else "%"
            
            if target_usernames is not None:
                if not target_usernames:
                    return None
                # IN句用のプレースホルダーを生成
                placeholders = ", ".join([p] * len(target_usernames))
                query = f"""
                    SELECT * FROM accounts 
                    WHERE username IN ({placeholders}) AND is_alive=1 AND in_use=0 
                    AND (assigned_pc IS NULL OR assigned_pc = '' OR assigned_pc = {p})
                    AND COALESCE(sync_status, '') NOT IN ('COMPLETED', 'SUSPENDED', 'LOCKED')
                    AND COALESCE(sync_status, '') NOT LIKE {p}
                    AND COALESCE(sync_status, '') NOT LIKE {p}
                    AND COALESCE(sync_status, '') NOT LIKE {p}
                    AND (sync_status IS NULL OR sync_status = '' OR sync_status NOT LIKE '{like_percent}ロック{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}凍結{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}実行失敗{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}ログイン失敗{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}プロファイル{like_percent}')
                    ORDER BY COALESCE(last_tweet_at, '1970-01-01') ASC LIMIT 1
                """
                params = tuple(target_usernames) + (self.pc_name, 'EXEC_FAIL%', 'LOGIN_FAILED%', 'ERROR:%')
            else:
                query = f"""
                    SELECT * FROM accounts 
                    WHERE selected=1 AND is_alive=1 AND in_use=0 
                    AND (assigned_pc IS NULL OR assigned_pc = '' OR assigned_pc = {p})
                    AND COALESCE(sync_status, '') NOT IN ('COMPLETED', 'SUSPENDED', 'LOCKED')
                    AND COALESCE(sync_status, '') NOT LIKE {p}
                    AND COALESCE(sync_status, '') NOT LIKE {p}
                    AND COALESCE(sync_status, '') NOT LIKE {p}
                    AND (sync_status IS NULL OR sync_status = '' OR sync_status NOT LIKE '{like_percent}ロック{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}凍結{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}実行失敗{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}ログイン失敗{like_percent}'
                         AND sync_status NOT LIKE '{like_percent}プロファイル{like_percent}')
                    ORDER BY COALESCE(last_tweet_at, '1970-01-01') ASC LIMIT 1
                """
                params = (self.pc_name, 'EXEC_FAIL%', 'LOGIN_FAILED%', 'ERROR:%')
                
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                result = dict(row) if isinstance(row, dict) else dict(row)
                username = row['username'] if isinstance(row, dict) else row[0]
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    f"UPDATE accounts SET in_use=1, claimed_by={p}, claimed_at={p} WHERE username={p}", 
                    (self.pc_name, now, username)
                )
                if self.db_type == "postgres": conn.commit()
                return result
            return None
        except Exception as e:
            logger.error(f"Error in get_next_account: {e}")
            return None

    def release_account(self, username):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET in_use=0 WHERE username={p}", (username,))
            if self.db_type == "postgres": conn.commit()
        except: pass

    def update_last_tweet_at(self, username):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE accounts SET last_tweet_at={p} WHERE username={p}", (now, username))
            if self.db_type == "postgres": conn.commit()
        except: pass

    def delete_account(self, username):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"DELETE FROM accounts WHERE username={p}", (username,))
            if self.db_type == "postgres": conn.commit()
            return True
        except: return False

    def save_display_name(self, username, display_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET display_name={p} WHERE username={p}", (display_name, username))
            if self.db_type == "postgres": conn.commit()
        except Exception as e:
            logger.error(f"Error save_display_name: {e}")

    def update_category(self, username, category):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET category={p} WHERE username={p}", (category, username))
            if self.db_type == "postgres": conn.commit()
        except Exception as e:
            logger.error(f"Error update_category: {e}")

    def update_account_status(self, username, is_suspended=False):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            val = 0 if is_suspended else 1
            cursor.execute(f"UPDATE accounts SET is_alive={p} WHERE username={p}", (val, username))
            if self.db_type == "postgres": conn.commit()
        except: pass

    def update_follow_counts(self, username, following, followers):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET following_count={p}, followers_count={p} WHERE username={p}", (int(following), int(followers), username))
            if self.db_type == "postgres": conn.commit()
        except Exception as e:
            logger.error(f"Error update_follow_counts: {e}")

    def update_profile_id(self, username, profile_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET profile_id={p} WHERE username={p}", (str(profile_id), username))
            if self.db_type == "postgres": conn.commit()          
        except Exception as e:
            logger.error(f"Error update_profile_id: {e}")

    def update_cookies(self, username, auth_token, ct0, cookies=None, user_agent=None, sec_ch_ua=None, impersonate=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()

            update_values = {
                "auth_token": auth_token,
                "ct0": ct0,
            }
            optional_values = {
                "cookies": cookies,
                "user_agent": user_agent,
                "sec_ch_ua": sec_ch_ua,
                "impersonate": impersonate,
            }
            for col, val in optional_values.items():
                if val is None:
                    continue
                if col == "cookies" and not isinstance(val, str):
                    val = json.dumps(val, ensure_ascii=False)
                update_values[col] = val

            assignments = ", ".join([f"{col}={p}" for col in update_values])
            params = tuple(update_values.values()) + (username,)
            cursor.execute(f"UPDATE accounts SET {assignments} WHERE username={p}", params)
            if self.db_type != "mysql": conn.commit()
            
            update_cookies_dbot(self, username, auth_token, ct0, cookies, user_agent, sec_ch_ua, impersonate)

        except Exception as e:
            logger.error(f"Error update_cookies: {e}")

    def update_cookies_dbot(self, username, auth_token, ct0, cookies=None, user_agent=None, sec_ch_ua=None, impersonate=None):
        try:
            conn = self.get_connection_dbot()
            cursor = conn.cursor()
            p = self._placeholder()

            update_values = {
                "auth_token": auth_token,
                "ct0": ct0,
            }
            optional_values = {
                "cookies": cookies,
                "user_agent": user_agent,
                "sec_ch_ua": sec_ch_ua,
                "inpersonate": impersonate,
            }
            for col, val in optional_values.items():
                if val is None:
                    continue
                if col == "cookies" and not isinstance(val, str):
                    val = json.dumps(val, ensure_ascii=False)
                update_values[col] = val

            assignments = ", ".join([f"{col}={p}" for col in update_values])
            params = tuple(update_values.values()) + (username,)
            cursor.execute(f"UPDATE account_master SET {assignments} WHERE username={p}", params)
        except Exception as e:
            logger.error(f"Error update_cookies: {e}")

    def report_heartbeat(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            t = "VARCHAR(255)" if self.db_type == "mysql" else "TEXT"
            cursor.execute(f"CREATE TABLE IF NOT EXISTS system_status (pc_name {t} PRIMARY KEY, last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            if self.db_type == "postgres":
                cursor.execute(f"INSERT INTO system_status (pc_name, last_seen) VALUES ({p}, CURRENT_TIMESTAMP) ON CONFLICT (pc_name) DO UPDATE SET last_seen = CURRENT_TIMESTAMP", (self.pc_name,))
                conn.commit()
            else:
                cursor.execute(f"INSERT OR REPLACE INTO system_status (pc_name, last_seen) VALUES ({p}, CURRENT_TIMESTAMP)", (self.pc_name,))
                conn.commit()
        except: pass
