import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\app.py'
if not os.path.exists(path):
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# load_accounts にキャッシュを導入
old_load = """    def load_accounts():
        db = DBManager()
        return db.get_all_accounts_from_db()"""

new_load = """    @st.cache_data(ttl=600)
    def load_accounts():
        db = DBManager()
        return db.get_all_accounts_df()"""

if old_load in content:
    content = content.replace(old_load, new_load)

# 全選択ボタンのあとにキャッシュクリアを追加
target_sel = 'db.update_all_selection_status(True)'
if target_sel in content:
    content = content.replace(target_sel, target_sel + '\n        st.cache_data.clear()')

target_unsel = 'db.update_all_selection_status(False)'
if target_unsel in content:
    content = content.replace(target_unsel, target_unsel + '\n        st.cache_data.clear()')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("app.py optimized with caching.")
