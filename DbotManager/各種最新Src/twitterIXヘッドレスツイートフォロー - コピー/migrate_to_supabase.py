import sqlite3
import psycopg2
import psycopg2.extras
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

    if config['db_type'] != 'postgres':
        print("Error: Please set db_type to 'postgres' in db_config.json before migration.")
        return

    pg_uri = config['postgres'].get('uri')
    if not pg_uri or "[YOUR-PASSWORD]" in pg_uri:
        print("Error: Please replace [YOUR-PASSWORD] in db_config.json with your actual database password.")
        return
    
    # 2. SQLite接続
    sqlite_path = 'system.db'
    if not os.path.exists(sqlite_path):
        print(f"Error: {sqlite_path} not found.")
        return
    
    sl_conn = sqlite3.connect(sqlite_path)
    sl_conn.row_factory = sqlite3.Row
    sl_cursor = sl_conn.cursor()

    # 3. PostgreSQL (Supabase) 接続 & 初期化
    from modules.mutual_follow.db_manager import DBManager
    db = DBManager()
    try:
        # 一旦既存のテーブルを削除して最新の設計図で作り直す
        pg_conn = db.get_connection()
        pg_cursor = pg_conn.cursor()
        for table in ['accounts', 'relationships', 'daily_stats', 'system_commands']:
            pg_cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        pg_conn.commit()
        
        db.init_db() # 最新の設計図でテーブル作成
        print("Connected to Supabase and tables re-initialized.")
    except Exception as e:
        print(f"Failed to connect to Supabase or initialize tables: {e}")
        return

    # 4. データの移行 (accountsテーブル)
    print("Migrating 'accounts' table (FAST MODE)...")
    sl_cursor.execute("SELECT * FROM accounts")
    rows = sl_cursor.fetchall()
    
    if rows:
        pg_cursor.execute("DELETE FROM accounts")
        
        columns = rows[0].keys()
        safe_cols = [f'"{c}"' if c == "Select" else c for c in columns]
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO accounts ({', '.join(safe_cols)}) VALUES ({placeholders})"
        
        data = [tuple(row) for row in rows]
        psycopg2.extras.execute_batch(pg_cursor, sql, data, page_size=500)
        pg_conn.commit()
        print(f"Migrated {len(rows)} accounts.")

    # 5. 他のテーブルも移行
    for table in ['daily_stats', 'relationships', 'system_commands']:
        try:
            print(f"Migrating '{table}' table (FAST MODE)...")
            sl_cursor.execute(f"SELECT * FROM {table}")
            rows = sl_cursor.fetchall()
            if rows:
                pg_cursor.execute(f"DELETE FROM {table}")
                columns = rows[0].keys()
                # postgres reserves "Select", daily_stats might have it? no, but just in case
                safe_cols = [f'"{c}"' if c == "Select" else c for c in columns]
                placeholders = ", ".join(["%s"] * len(columns))
                sql = f"INSERT INTO {table} ({', '.join(safe_cols)}) VALUES ({placeholders})"
                data = [tuple(row) for row in rows]
                psycopg2.extras.execute_batch(pg_cursor, sql, data, page_size=500)
                pg_conn.commit()
                print(f"Migrated {len(rows)} rows from {table}.")
        except Exception as e:
            print(f"Skip table {table}: {e}")

    sl_conn.close()
    pg_conn.close()
    print("\n--- Cloud Migration Completed! ---")
    print("Now you can run distributed tasks across all PCs.")

if __name__ == "__main__":
    migrate()
