file_path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\modules\mutual_follow\db_manager.py'
with open(file_path, 'rb') as f:
    content = f.read()

# Search for the start of bulk_clear_sync_status
target = b"def bulk_clear_sync_status"
idx = content.find(target)
if idx != -1:
    print(content[idx:idx+500].decode('utf-8', errors='replace'))
else:
    print("Not found")
