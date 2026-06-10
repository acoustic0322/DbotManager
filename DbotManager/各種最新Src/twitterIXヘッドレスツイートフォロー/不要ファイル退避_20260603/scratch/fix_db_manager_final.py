# -*- coding: utf-8 -*-
import os

file_path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\modules\mutual_follow\db_manager.py'

# UTF-8 Hex strings
login_fail_hex = "e383ade382b0e382a4e383b3e5a4b1e69597"
lock_hex = "e383ade38383e382af"
fail_hex = "e5a4b1e69597"
limit_hex = "e588b6e99990"
error_hex = "e382a8e383aae383bc"
daily_life_hex = "e697a5e5b8b8e7949fe6b4bb"

login_fail = bytes.fromhex(login_fail_hex).decode('utf-8')
lock = bytes.fromhex(lock_hex).decode('utf-8')
fail = bytes.fromhex(fail_hex).decode('utf-8')
limit = bytes.fromhex(limit_hex).decode('utf-8')
error = bytes.fromhex(error_hex).decode('utf-8')
daily_life = bytes.fromhex(daily_life_hex).decode('utf-8')

# Reconstruct the file content with placeholders
code_template = r"""import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
import os
from loguru import logger
import json
import pymysql
import platform
import socket
import psycopg2
import psycopg2.extras
import time

DB_PATH = 'system.db'
CONFIG_PATH = 'db_config.json'

class DBManager:
    _initialized = False # Class-level flag to prevent redundant init_db
    _shared_conn = None  # Shared connection to prevent 'max clients reached'
    
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self._conn = None # Persistent connection for this instance
        
        # Determine PC_NAME based on hostname and PC_MAP in root config.json
        hostname = socket.gethostname()
        self.pc_name = hostname # Default fallback
        
        root_config_path = 'config.json'
        if os.path.exists(root_config_path):
            try:
                with open(root_config_path, 'r', encoding='utf-8') as f:
                    root_cfg = json.load(f)
                    # Use PC_MAP if available
                    pc_map = root_cfg.get('PC_MAP', {})
                    if hostname in pc_map:
                        self.pc_name = pc_map[hostname]
                        logger.info(f"PC Identified via MAP: {hostname} -> {self.pc_name}")
                    elif 'PC_NAME' in root_cfg:
                        # Backward compatibility
                        self.pc_name = root_cfg['PC_NAME']
            except Exception as e:
                logger.warning(f"Failed to load PC identification from config: {e}")
                
        self.load_config()
        if not DBManager._initialized:
            self.init_db()
            DBManager._initialized = True
        else:
            logger.debug("Database already initialized in this process, skipping init_db.")

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {"db_type": "sqlite"}
        self.db_type = self.config.get("db_type", "sqlite")
        self.mysql_config = self.config.get("mysql", {})
        self.postgres_config = self.config.get("postgres", {})

    def get_connection(self):
        # Reuse SHARED connection across all instances in the same process
        if DBManager._shared_conn:
            try:
                if self.db_type == "sqlite":
                    return DBManager._shared_conn
                elif self.db_type == "postgres":
                    if DBManager._shared_conn.closed == 0:
                        return DBManager._shared_conn
                elif self.db_type == "mysql":
                    if DBManager._shared_conn.open:
                        return DBManager._shared_conn
            except:
                DBManager._shared_conn = None

        if self.db_type == "mysql":
            conf = self.mysql_config
            DBManager._shared_conn = pymysql.connect(
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
            timeout = 10 # Reduced timeout for faster failure
            try:
                if 'uri' in conf:
                    DBManager._shared_conn = psycopg2.connect(conf['uri'], cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=timeout)
                else:
                    DBManager._shared_conn = psycopg2.connect(
                        host=conf.get("host", "localhost"),
                        port=conf.get("port", 5432),
                        user=conf.get("user", "postgres"),
                        password=conf.get("password", ""),
                        dbname=conf.get("database", "postgres"),
                        cursor_factory=psycopg2.extras.RealDictCursor,
                        connect_timeout=timeout
                    )
                DBManager._shared_conn.autocommit = True
                logger.success("Shared Postgres connection established.")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                raise e
        else:
            DBManager._shared_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            DBManager._shared_conn.row_factory = sqlite3.Row
            
        return DBManager._shared_conn

    def init_db(self):
        try:
            logger.info("Initializing database...")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.db_type in ["mysql", "postgres"]:
                logger.debug(f"Ensuring tables exist in {self.db_type}...")
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
                logger.debug("Accounts table verified.")
                
                # Relationships Table
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS relationships (
                    from_user {text_type},
                    to_user {text_type},
                    timestamp {time_type} DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (from_user, to_user)
                )
                ''')
                # Daily Stats
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    username {text_type},
                    date DATE,
                    action_type {text_type},
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (username, date, action_type)
                )
                ''')
                # System Commands
                try:
                    # Check if id column exists
                    cursor.execute("SELECT id FROM system_commands LIMIT 1")
                except:
                    # If not, drop and recreate for clean migration
                    logger.warning("Upgrading system_commands table schema...")
                    cursor.execute("DROP TABLE IF EXISTS system_commands")

                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS system_commands (
                    id SERIAL PRIMARY KEY,
                    command {text_type},
                    params TEXT,
                    created_at {time_type} DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                logger.debug(f"{self.db_type} tables verified.")
            else:
                # SQLite Implementation
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    username TEXT PRIMARY KEY,
                    auth_token TEXT NOT NULL,
                    ct0 TEXT,
                    password TEXT,
                    email TEXT,
                    totp_secret TEXT,
                    profile_id TEXT,
                    is_alive INTEGER DEFAULT 1,
                    daily_follow_count INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 10,
                    last_active_date TEXT,
                    selected INTEGER DEFAULT 1,
                    display_name TEXT,
                    sync_status TEXT,
                    category TEXT DEFAULT '',
                    group_id TEXT,
                    group_name TEXT,
                    following_count INTEGER DEFAULT 0,
                    followers_count INTEGER DEFAULT 0,
                    reach_status TEXT DEFAULT 'OK',
                    last_full_check TEXT,
                    last_tweet_at TEXT,
                    claimed_by TEXT,
                    claimed_at DATETIME,
                    assigned_pc TEXT,
                    in_use INTEGER DEFAULT 0,
                    biography TEXT
                )
                ''')
                # Relationships
                cursor.execute('CREATE TABLE IF NOT EXISTS relationships (from_user TEXT, to_user TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(from_user, to_user))')
                # Daily Stats
                cursor.execute('CREATE TABLE IF NOT EXISTS daily_stats (username TEXT, date TEXT, action_type TEXT, count INTEGER DEFAULT 0, PRIMARY KEY (username, date, action_type))')
                # System Commands
                try:
                    cursor.execute("SELECT id FROM system_commands LIMIT 1")
                except:
                    cursor.execute("DROP TABLE IF EXISTS system_commands")
                cursor.execute('CREATE TABLE IF NOT EXISTS system_commands (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, params TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)')

                # SQLite Migration logic (Check columns)
                cursor.execute("PRAGMA table_info(accounts)")
                columns = [info[1] for info in cursor.fetchall()]
                migration_cols = {
                    'selected': 'INTEGER DEFAULT 1',
                    'daily_limit': 'INTEGER DEFAULT 10',
                    'ct0': 'TEXT',
                    'display_name': 'TEXT',
                    'sync_status': 'TEXT',
                    'profile_id': 'TEXT',
                    'password': 'TEXT',
                    'email': 'TEXT',
                    'totp_secret': 'TEXT',
                    'category': "TEXT DEFAULT 'REPLACE_ME_DAILY_LIFE'",
                    'group_id': 'TEXT',
                    'group_name': 'TEXT',
                    'following_count': 'INTEGER DEFAULT 0',
                    'followers_count': 'INTEGER DEFAULT 0',
                    'reach_status': 'TEXT DEFAULT \'OK\'',
                    'last_full_check': 'TEXT',
                    'last_tweet_at': 'TEXT',
                    'claimed_by': 'TEXT',
                    'claimed_at': 'DATETIME',
                    'assigned_pc': 'TEXT',
                    'in_use': 'INTEGER DEFAULT 0',
                    'biography': 'TEXT'
                }
                for col, col_type in migration_cols.items():
                    if col not in columns:
                        try:
                            cursor.execute(f"ALTER TABLE accounts ADD COLUMN {col} {col_type}")
                            conn.commit()
                        except: pass
                logger.debug("SQLite tables and migrations verified.")
        
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise e
        finally:
            pass # Keep shared connection open

    def _placeholder(self):
        return "%s" if self.db_type in ["mysql", "postgres"] else "?"

    def claim_account(self, action_type="any"):
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        timeout = now - timedelta(minutes=15) # 15分以上前の占有はタイムアウトとみなす
        p = self._placeholder()
        
        # 1. すでに自分が占有しているものを探す
        cursor.execute(f"SELECT * FROM accounts WHERE claimed_by = {p} AND is_alive = 1 AND selected = 1 LIMIT 1", (self.pc_name,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)

        # 2. 空いているアカウント、または期限切れの占有を1件確保する
        # かつ、このPCに割り当てられている(assigned_pc IS NULL または assigned_pc = 自分)ものに限定
        if self.db_type in ["mysql", "postgres"]:
            # MySQL/Postgres atomic update
            cursor.execute(f'''
                UPDATE accounts 
                SET claimed_by = {p}, claimed_at = {p} 
                WHERE (claimed_by IS NULL OR claimed_at < {p}) 
                AND (assigned_pc IS NULL OR assigned_pc = {p})
                AND is_alive = 1 AND selected = 1 
                LIMIT 1
            ''', (self.pc_name, now, timeout, self.pc_name))
            
            if cursor.rowcount > 0:
                cursor.execute(f"SELECT * FROM accounts WHERE claimed_by = {p} LIMIT 1", (self.pc_name,))
                row = cursor.fetchone()
        else:
            # SQLite
            cursor.execute(f'''
                SELECT username FROM accounts 
                WHERE (claimed_by IS NULL OR claimed_at < {p}) 
                AND (assigned_pc IS NULL OR assigned_pc = {p})
                AND is_alive = 1 AND selected = 1 
                ORDER BY RANDOM() LIMIT 1
            ''', (timeout.strftime('%Y-%m-%d %H:%M:%S'), self.pc_name))
            target = cursor.fetchone()
            if target:
                username = target[0]
                cursor.execute(f"UPDATE accounts SET claimed_by = {p}, claimed_at = {p} WHERE username = {p}", (self.pc_name, now.strftime('%Y-%m-%d %H:%M:%S'), username))
                conn.commit()
                cursor.execute(f"SELECT * FROM accounts WHERE username = {p}", (username,))
                row = cursor.fetchone()

        return dict(row) if row else None

    def release_account(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        cursor.execute(f"UPDATE accounts SET claimed_by = NULL, claimed_at = NULL WHERE username = {p}", (username,))
        if self.db_type not in ["mysql", "postgres"]: conn.commit()

    def get_next_account(self, exclude_usernames=None):
        return self.claim_account()

    def reset_daily_limits(self):
        today = datetime.now().strftime('%Y-%m-%d')
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        
        cursor.execute(f'SELECT username FROM accounts WHERE last_active_date != {p} OR last_active_date IS NULL', (today,))
            
        users_to_reset = [r['username'] if self.db_type in ["mysql", "postgres"] else r[0] for r in cursor.fetchall()]
        
        for user in users_to_reset:
            new_limit = random.randint(8, 12)
            cursor.execute(f'UPDATE accounts SET daily_follow_count = 0, daily_limit = {p} WHERE username = {p}', (new_limit, user))
            
        if self.db_type != "mysql": conn.commit()

    def update_sync_status(self, username, status):
        clean_username = str(username).replace('@', '').strip()
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        try:
            cursor.execute(f'UPDATE accounts SET sync_status = {p} WHERE username = {p}', (status, clean_username))
            if self.db_type not in ["mysql", "postgres"]: conn.commit()
        except Exception as e:
            logger.error(f"Failed to update sync_status for {clean_username}: {e}")
        finally:
            pass

    def get_all_accounts_from_db(self):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM accounts')
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            except Exception as e:
                logger.warning(f"Fetch accounts attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch accounts after {max_retries} attempts: {e}")
                    return []
                time.sleep(1)

    def save_display_name(self, username, display_name):
        if not display_name: return
        clean_username = str(username).replace('@', '').strip()
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        try:
            cursor.execute(f'UPDATE accounts SET display_name = {p} WHERE username = {p}', (display_name, clean_username))
            if self.db_type not in ["mysql", "postgres"]: conn.commit()
        except Exception as e:
            logger.error(f"Failed to save display_name for {clean_username}: {e}")
        finally:
            pass

    def update_last_tweet_at(self, username):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        clean_username = str(username).replace('@', '').strip()
        conn = self.get_connection()
        p = self._placeholder()
        conn.cursor().execute(f'UPDATE accounts SET last_tweet_at = {p} WHERE username = {p}', (now, clean_username))
        if self.db_type != "mysql": conn.commit()

    def delete_account(self, username):
        try:
            conn = self.get_connection()
            p = self._placeholder()
            conn.cursor().execute(f'DELETE FROM accounts WHERE username = {p}', (username,))
            if self.db_type not in ["mysql", "postgres"]: conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete account {username}: {e}")
            return False

    def bulk_clear_sync_status(self, status_to_clear):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            if status_to_clear == 'REPLACE_ME_LOGIN_FAIL':
                cursor.execute(f"UPDATE accounts SET sync_status = '' WHERE sync_status = {p}", ('REPLACE_ME_LOGIN_FAIL',))
            elif status_to_clear == 'REPLACE_ME_LOCK':
                cursor.execute(f"UPDATE accounts SET sync_status = '' WHERE sync_status LIKE {p}", (f'%REPLACE_ME_LOCK%',))
            elif status_to_clear == 'REPLACE_ME_FAIL':
                cursor.execute(f'''
                    UPDATE accounts SET sync_status = '' 
                    WHERE sync_status LIKE {p} OR sync_status LIKE '%Error%' OR sync_status LIKE '%Fail%' 
                       OR sync_status LIKE '%Timeout%' OR sync_status LIKE {p} OR sync_status LIKE {p}
                ''', (f'%REPLACE_ME_FAIL%', f'%REPLACE_ME_LIMIT%', f'%REPLACE_ME_ERROR%'))
            else:
                cursor.execute(f"UPDATE accounts SET sync_status = '' WHERE sync_status = {p}", (status_to_clear,))
            if self.db_type not in ["mysql", "postgres"]: conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to bulk clear sync status: {e}")
            return False

    def get_all_accounts_df(self):
        accounts_list = self.get_all_accounts_from_db()
        if not accounts_list: return pd.DataFrame()
        df = pd.DataFrame(accounts_list)
        
        # カラム名をすべて小文字に統一（Postgres/SQLiteの差異を吸収）
        df.columns = [c.lower() for c in df.columns]
        
        # 内部で使う名前を再定義
        if 'username' not in df.columns:
            # 万が一usernameがない場合（ありえないはずですが）、最初のカラムを使う
            df = df.rename(columns={df.columns[0]: 'username'})

        # screen_nameの作成
        if 'screen_name' not in df.columns:
            df['screen_name'] = df['username']
        else:
            # NULLや空文字をusernameで埋める
            df['screen_name'] = df['screen_name'].fillna(df['username'])
            df.loc[df['screen_name'] == '', 'screen_name'] = df['username']
            # それでもNoneならusername
            df['screen_name'] = df['screen_name'].replace('None', None).fillna(df['username'])

        # @の除去と文字列化
        df['screen_name'] = df['screen_name'].astype(str).str.replace('@', '', regex=False).str.strip()
        
        # app.pyが期待するカラム名（一部大文字など）に合わせる
        if 'selected' in df.columns:
            df = df.rename(columns={'selected': 'Select'})
            
        if 'display_name' in df.columns:
            df['assigned_name'] = df['display_name'].fillna('')
            df.loc[df['assigned_name'] == '', 'assigned_name'] = df['screen_name']
        else:
            df['assigned_name'] = df['screen_name']

        # 型の変換
        if 'Select' in df.columns:
            df['Select'] = df['Select'].apply(lambda x: True if x in [1, True, "1", "true"] else False)
        
        for col in ['following_count', 'followers_count']:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        if 'is_alive' in df.columns:
            df['is_suspended'] = df['is_alive'].apply(lambda x: False if str(x) in ['1', 'True', 'true'] else True)
        else:
            df['is_suspended'] = False
            
        return df

    def save_accounts_df(self, df):
        # Retry mechanism for DB errors (especially for remote postgres)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                p = self._placeholder()
                for _, row in df.iterrows():
                    username = row.get('screen_name') or row.get('username')
                    if not username: continue
                    is_sel = 1 if row.get('Select') else 0
                    is_alive = 0 if row.get('is_suspended', False) else 1
                    cursor.execute(f"UPDATE accounts SET selected={p}, is_alive={p} WHERE username={p}", (is_sel, is_alive, username))
                
                if self.db_type not in ["mysql", "postgres"]: 
                    conn.commit()
                else:
                    # postgres/mysql with autocommit=True still sometimes needs explicit sync or just closing
                    pass
                
                return True
            except Exception as e:
                logger.warning(f"DF Save attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"DF Save error after {max_retries} attempts: {e}")
                    return False
                time.sleep(1) # Wait a bit before retry

    def get_daily_stats(self):
        today = datetime.now().strftime('%Y-%m-%d')
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        cursor.execute(f"SELECT * FROM daily_stats WHERE date = {p}", (today,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def record_daily_action(self, username, action_type, count=1):
        today = datetime.now().strftime('%Y-%m-%d')
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        try:
            cursor.execute(f"SELECT count FROM daily_stats WHERE username={p} AND date={p} AND action_type={p}", (username, today, action_type))
            row = cursor.fetchone()
            if row:
                cursor.execute(f"UPDATE daily_stats SET count = count + {p} WHERE username={p} AND date={p} AND action_type={p}", (count, username, today, action_type))
            else:
                cursor.execute(f"INSERT INTO daily_stats (username, date, action_type, count) VALUES ({p}, {p}, {p}, {p})", (username, today, action_type, count))
            cursor.execute(f"UPDATE accounts SET last_active_date={p} WHERE username={p}", (today, username))
            if self.db_type not in ["mysql", "postgres"]: conn.commit()
        finally:
            pass

    def update_account_selection(self, username, selected):
        conn = self.get_connection()
        p = self._placeholder()
        conn.cursor().execute(f"UPDATE accounts SET selected={p} WHERE username={p}", (1 if selected else 0, username))
        if self.db_type != "mysql": conn.commit()

    def update_all_selection_status(self, selected, screen_names=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        status_val = 1 if selected else 0
        
        try:
            if screen_names:
                # Update specific subset (e.g. current filtered view)
                logger.info(f"Bulk updating selection for {len(screen_names)} accounts to {selected}...")
                # We use chunks to avoid SQL limit issues if there are thousands
                chunk_size = 500
                names_list = list(screen_names)
                for i in range(0, len(names_list), chunk_size):
                    chunk = names_list[i:i + chunk_size]
                    placeholders = ",".join([p] * len(chunk))
                    cursor.execute(f"UPDATE accounts SET selected={status_val} WHERE username IN ({placeholders})", chunk)
            else:
                # Update ALL accounts in the DB
                logger.info(f"Bulk updating selection for ALL accounts to {selected}...")
                cursor.execute(f"UPDATE accounts SET selected={status_val}")
            
            if self.db_type != "mysql": conn.commit()
            logger.success("Bulk selection update complete.")
        except Exception as e:
            logger.error(f"Bulk selection update failed: {e}")
        finally:
            pass

    def set_global_command(self, command, params=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            params_json = json.dumps(params) if params else "{}"
            
            # Clear old commands first
            cursor.execute("DELETE FROM system_commands")
            cursor.execute(f"INSERT INTO system_commands (command, params, created_at) VALUES ({p}, {p}, {p})", 
                           (command, params_json, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            if self.db_type != "mysql": conn.commit()
            logger.info(f"Global command set in DB: {command}")
        except Exception as e:
            logger.error(f"Failed to set global command: {e}")
            raise e
        finally:
            pass

    def get_global_command(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM system_commands ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_next_account(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        p = self._placeholder()
        
        try:
            # PostgreSQL/MySQL/SQLite compatible approach: 
            # 1. Find a candidate
            query = "SELECT username FROM accounts WHERE selected=1 AND is_alive=1 AND in_use=0 LIMIT 1"
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                username = row[0] if isinstance(row, (tuple, list)) else row['username']
                # 2. Mark it as in use
                cursor.execute(f"UPDATE accounts SET in_use=1, last_active_date={p} WHERE username={p}", 
                               (datetime.now().strftime('%Y-%m-%d'), username))
                if self.db_type not in ["mysql", "postgres"]: conn.commit()
                
                # 3. Fetch full details
                cursor.execute(f"SELECT * FROM accounts WHERE username={p}", (username,))
                full_row = cursor.fetchone()
                return dict(full_row)
            return None
        except Exception as e:
            logger.error(f"Error in get_next_account: {e}")
            return None
        finally:
            pass

    def release_account(self, username):
        conn = self.get_connection()
        p = self._placeholder()
        conn.cursor().execute(f"UPDATE accounts SET in_use=0 WHERE username={p}", (username,))
        if self.db_type not in ["mysql", "postgres"]: conn.commit()

    def reset_all_in_use(self):
        conn = self.get_connection()
        conn.cursor().execute("UPDATE accounts SET in_use=0")
        if self.db_type != "mysql": conn.commit()
        logger.info("All in_use flags reset to 0.")

    def clear_global_command(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self.db_type in ["mysql", "postgres"]:
                cursor.execute("TRUNCATE TABLE system_commands")
            else:
                cursor.execute("DELETE FROM system_commands")
            if self.db_type not in ["mysql", "postgres"]: conn.commit()
            logger.info("Global command queue cleared.")
        except Exception as e:
            logger.error(f"Failed to clear commands: {e}")
        finally:
            pass
"""

code_template = code_template.replace('REPLACE_ME_LOGIN_FAIL', login_fail)
code_template = code_template.replace('REPLACE_ME_LOCK', lock)
code_template = code_template.replace('REPLACE_ME_FAIL', fail)
code_template = code_template.replace('REPLACE_ME_LIMIT', limit)
code_template = code_template.replace('REPLACE_ME_ERROR', error)
code_template = code_template.replace('REPLACE_ME_DAILY_LIFE', daily_life)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code_template)

print("DBManager fixed with safe escape sequences and no IndentationError.")
