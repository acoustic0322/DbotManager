import os

file_path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\modules\mutual_follow\db_manager.py'

# Try multiple encodings
for encoding in ['utf-8', 'cp932', 'shift-jis']:
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        print(f"Read successful with {encoding}")
        break
    except UnicodeDecodeError:
        continue
else:
    print("Failed to read with all attempted encodings.")
    exit(1)

# 1. Fix imports
if 'import time' not in content:
    content = content.replace('import psycopg2.extras', 'import psycopg2.extras\nimport time')

# 2. Add _shared_conn
if '_shared_conn = None' not in content:
    content = content.replace('_initialized = False # Class-level flag to prevent redundant init_db', 
                              '_initialized = False # Class-level flag to prevent redundant init_db\n    _shared_conn = None  # Shared connection to prevent "max clients reached"')

# 3. Replace get_connection
old_get_conn_lines = [
    '    def get_connection(self):',
    '        # Reuse existing connection if healthy',
    '        if self._conn:',
    '            try:',
    '                if self.db_type == "sqlite":',
    '                    return self._conn',
    '                elif self.db_type == "postgres":',
    '                    if self._conn.closed == 0:',
    '                        return self._conn',
    '                elif self.db_type == "mysql":',
    '                    if self._conn.open:',
    '                        return self._conn',
    '            except:',
    '                self._conn = None',
    '',
    '        if self.db_type == "mysql":',
    '            conf = self.mysql_config',
    '            self._conn = pymysql.connect(',
    '                host=conf.get("host", "localhost"),',
    '                user=conf.get("user", "root"),',
    '                password=conf.get("password", ""),',
    '                database=conf.get("database", "twitter_ix"),',
    '                port=conf.get("port", 3306),',
    '                charset=\'utf8mb4\',',
    '                cursorclass=pymysql.cursors.DictCursor,',
    '                autocommit=True',
    '            )',
    '        elif self.db_type == "postgres":',
    '            conf = self.postgres_config',
    '            timeout = 15',
    '            try:',
    '                if \'uri\' in conf:',
    '                    self._conn = psycopg2.connect(conf[\'uri\'], cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=timeout)',
    '                else:',
    '                    self._conn = psycopg2.connect(',
    '                        host=conf.get("host", "localhost"),',
    '                        port=conf.get("port", 5432),',
    '                        user=conf.get("user", "postgres"),',
    '                        password=conf.get("password", ""),',
    '                        dbname=conf.get("database", "postgres"),',
    '                        cursor_factory=psycopg2.extras.RealDictCursor,',
    '                        connect_timeout=timeout',
    '                    )',
    '                self._conn.autocommit = True',
    '                logger.success("Postgres connection established and reused.")',
    '            except Exception as e:',
    '                logger.error(f"Database connection failed: {e}")',
    '                raise e',
    '        else:',
    '            self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)',
    '            self._conn.row_factory = sqlite3.Row',
    '            ',
    '        return self._conn'
]

new_get_conn = """    def get_connection(self):
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
            timeout = 10 
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
            
        return DBManager._shared_conn"""

old_get_conn = "\n".join(old_get_conn_lines)

if old_get_conn in content:
    content = content.replace(old_get_conn, new_get_conn)
    print("Replaced get_connection (LF)")
elif old_get_conn.replace('\n', '\r\n') in content:
    content = content.replace(old_get_conn.replace('\n', '\r\n'), new_get_conn.replace('\n', '\r\n'))
    print("Replaced get_connection (CRLF)")
else:
    print("Could not find old get_connection block.")

# 4. Remove all conn.close() calls that are not in init_db
import re
# Look for 'conn.close()' at the end of functions
content = re.sub(r'        conn\.close\(\)\n', '', content)

with open(file_path, 'w', encoding=encoding) as f:
    f.write(content)

print("DBManager updated successfully.")
