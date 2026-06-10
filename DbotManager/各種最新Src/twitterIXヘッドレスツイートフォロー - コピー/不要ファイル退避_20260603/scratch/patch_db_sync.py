import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\modules\mutual_follow\db_manager.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_method = """    def update_sync_status(self, username, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            p = self._placeholder()
            cursor.execute(f"UPDATE accounts SET sync_status = {p} WHERE username = {p}", (status, username))
            if self.db_type == "postgres": conn.commit()
        except Exception as e:
            logger.error(f"DB Error update_sync_status: {e}")

    def bulk_clear_sync_status"""

if 'def update_sync_status' not in content:
    content = content.replace('    def bulk_clear_sync_status', new_method)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added update_sync_status to db_manager.py")
else:
    print("Already exists")
