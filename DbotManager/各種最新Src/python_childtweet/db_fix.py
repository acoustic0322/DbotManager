import pymysql

# あなたの環境に合わせた接続設定
DB_CONFIG = {
    "host": "localhost",       # config.db_host が localhost の場合
    "user": "root",
    "password": "abcd1234",    # 送信いただいたパスワード
    "db_name": "d_bot"         # データベース名
}

def fix_database():
    print("データベースの修正を開始します...")
    try:
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["db_name"],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # トークンの保存箱を「TEXT型（約6万文字）」に広げる
            print("refresh_token の容量を拡大中...")
            cursor.execute("ALTER TABLE account_master MODIFY refresh_token TEXT;")
            
            print("bearer_token の容量を拡大中...")
            cursor.execute("ALTER TABLE account_master MODIFY bearer_token TEXT;")
            
        connection.commit()
        connection.close()
        print("\n✅ 完了しました！データベースの制限が解除されました。")
        print("-" * 50)
        print("【次の作業】")
        print("今DBに入っているトークンは既に壊れているため、")
        print("一度だけブラウザで各アカウントの連携をやり直してください。")
        print("次からは長いトークンも正常に保存され、エラーが消えます。")
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    fix_database()