import os

db_path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\modules\mutual_follow\db_manager.py'
app_path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\app.py'

# 1. Update db_manager.py: Make get_next_account order by last_tweet_at
with open(db_path, 'r', encoding='utf-8') as f:
    db_content = f.read()

old_query = 'f"SELECT * FROM accounts WHERE selected=1 AND is_alive=1 AND in_use=0 LIMIT 1"'
new_query = 'f"SELECT * FROM accounts WHERE selected=1 AND is_alive=1 AND in_use=0 ORDER BY COALESCE(last_tweet_at, \'1970-01-01\') ASC LIMIT 1"'
db_content = db_content.replace(old_query, new_query)

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(db_content)


# 2. Update app.py: Add db.reset_all_in_use() to START button
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

old_start = """                db.set_global_command("START_ENGAGEMENT", params)
                st.success("全PCへ開始指示を送信しました。")"""
new_start = """                db.reset_all_in_use()
                db.set_global_command("START_ENGAGEMENT", params)
                st.success("全PCへ開始指示を送信し、ロックを初期化しました。")"""
app_content = app_content.replace(old_start, new_start)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Patch applied successfully.")
