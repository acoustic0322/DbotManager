import sqlite3
import pymysql
import json
import os
import sys

def migrate():
    # 1. 設定の読み込み
    config_path = 'db_config.json'
    if not os.path.exists(config_path):
        print("Error: db_config.json not found.")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if config['db_type'] != 'mysql':
        print("Error: Please set db_type to 'mysql' in db_config.json before migration.")
        return

    mysql_conf = config['mysql']
    
    # 2. MySQL初期化 (データベース作成 & テーブル作成)
    from modules.mutual_follow.db_manager import DBManager
    
    # データベースが存在しない可能性を考慮し、まずはDB指定なしで接続して作成を試みる
    try:
        root_conn = pymysql.connect(
            host=mysql_conf['host'],
            port=mysql_conf['port'],
            user=mysql_conf['user'],
            password=mysql_conf['password']
        )
        root_conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {mysql_conf['database']}")
        root_conn.close()
        print(f"Database '{mysql_conf['database']}' ensured.")
    except Exception as e:
        print(f"Warning during DB creation: {e}")

    db = DBManager()
    try:
        db.init_db()
        print("MySQL tables initialized.")
    except Exception as e:
        print(f"Failed to initialize MySQL tables: {e}")
        return

    # 3. SQLite接続
    sqlite_path = 'system.db'
    if not os.path.exists(sqlite_path):
        print(f"Error: {sqlite_path} not found.")
        return
    
    sl_conn = sqlite3.connect(sqlite_path)
    sl_conn.row_factory = sqlite3.Row
    sl_cursor = sl_conn.cursor()

    # 3. MySQL接続
    try:
        my_conn = pymysql.connect(
            host=mysql_conf['host'],
            port=mysql_conf['port'],
            user=mysql_conf['user'],
            password=mysql_conf['password'],
            database=mysql_conf['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        my_cursor = my_conn.cursor()
        print("Connected to MySQL successfully.")
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return

    # 4. データの移行 (accountsテーブル)
    print("Migrating 'accounts' table...")
    sl_cursor.execute("SELECT * FROM accounts")
    rows = sl_cursor.fetchall()
    
    if rows:
        # MySQL側のテーブルが空であることを確認（またはクリア）
        my_cursor.execute("DELETE FROM accounts")
        
        # 動的にカラム名とプレースホルダーを作成
        columns = rows[0].keys()
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO accounts ({', '.join(columns)}) VALUES ({placeholders})"
        
        data = [tuple(row) for row in rows]
        my_cursor.executemany(sql, data)
        my_conn.commit()
        print(f"Migrated {len(rows)} accounts.")

    # 5. 他のテーブルも同様に移行 (daily_stats, relationships等)
    for table in ['daily_stats', 'relationships', 'system_commands']:
        try:
            print(f"Migrating '{table}' table...")
            sl_cursor.execute(f"SELECT * FROM {table}")
            rows = sl_cursor.fetchall()
            if rows:
                my_cursor.execute(f"DELETE FROM {table}")
                columns = rows[0].keys()
                placeholders = ", ".join(["%s"] * len(columns))
                sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                data = [tuple(row) for row in rows]
                my_cursor.executemany(sql, data)
                my_conn.commit()
                print(f"Migrated {len(rows)} rows from {table}.")
        except Exception as e:
            print(f"Skip table {table}: {e}")

    sl_conn.close()
    my_conn.close()
    print("\n--- Migration Completed! ---")
    print("Now you can run app.py or worker_service.py using MySQL.")

if __name__ == "__main__":
    migrate()
