import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\modules\mutual_follow\db_manager.py'
if not os.path.exists(path):
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# get_all_accounts_from_db を SQL側での整形版に差し替え
old_fetch = """    def get_all_accounts_from_db(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT username, screen_name, display_name, sync_status, is_alive, selected, category, last_active_date, last_tweet_at FROM accounts ORDER BY screen_name ASC')
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Fetch Error: {e}")
            return []"""

new_fetch = """    def get_all_accounts_from_db(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # SQL側で文字列整形（@の除去など）を済ませることで、Python側の負担を激減させる
            sql = \"\"\"
                SELECT 
                    username, 
                    TRIM(REPLACE(COALESCE(screen_name, username), '@', '')) as screen_name, 
                    display_name, 
                    sync_status, 
                    is_alive, 
                    selected, 
                    category, 
                    last_active_date, 
                    last_tweet_at 
                FROM accounts 
                ORDER BY screen_name ASC
            \"\"\"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Fetch Error: {e}")
            return []"""

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)

# get_all_accounts_df のループ処理を軽量化
old_df = """    def get_all_accounts_df(self):
        accounts_list = self.get_all_accounts_from_db()
        essential_cols = ['username', 'screen_name', 'sync_status', 'is_alive', 'is_suspended', 'Select']
        if not accounts_list: return pd.DataFrame(columns=essential_cols)
        df = pd.DataFrame(accounts_list)
        df.columns = [c.lower() for c in df.columns]
        if 'username' not in df.columns and not df.empty: df = df.rename(columns={df.columns[0]: 'username'})
        if 'screen_name' not in df.columns: df['screen_name'] = df['username']
        df['screen_name'] = df['screen_name'].fillna(df['username']).astype(str).str.replace('@', '', regex=False).str.strip()
        if 'selected' in df.columns: df = df.rename(columns={'selected': 'Select'})
        df['Select'] = df.get('select', False) if 'select' in df.columns else df.get('Select', True)
        df['Select'] = df['Select'].apply(lambda x: True if str(x).lower() in ['1', 'true', 'true'] else False)
        df['is_suspended'] = df['is_alive'].apply(lambda x: False if str(x).lower() in ['1', 'true'] else True)
        return df"""

new_df = """    def get_all_accounts_df(self):
        accounts_list = self.get_all_accounts_from_db()
        if not accounts_list: return pd.DataFrame()
        df = pd.DataFrame(accounts_list)
        # SQL側で整形済みなので、カラム名の調整とフラグ変換のみに絞る
        df.columns = [c.lower() for c in df.columns]
        df = df.rename(columns={'selected': 'Select'})
        df['Select'] = df['Select'].apply(lambda x: True if str(x) in ['1', 'True', 'true'] else False)
        df['is_suspended'] = df['is_alive'].apply(lambda x: False if str(x) in ['1', 'True', 'true'] else True)
        return df"""

if old_df in content:
    content = content.replace(old_df, new_df)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("DBManager optimized for speed.")
