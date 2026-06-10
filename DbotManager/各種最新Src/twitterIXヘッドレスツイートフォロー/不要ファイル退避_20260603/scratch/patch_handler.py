import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\engagement_handler.py'
if not os.path.exists(path):
    print("File not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """    try:
        df = db.get_all_accounts_df()
        targets = df[df['Select'] == True]
    except Exception as e:
        logger.error(f"Failed to load accounts: {e}")
        return

    if targets.empty:
        logger.error("No selected accounts in the active CSV.")
        return"""

replacement = """    try:
        df = db.get_all_accounts_df()
        total_in_db = len(df)
        targets = df[df['Select'] == True]
        selected_count = len(targets)
        logger.info(f"DBから読み込み完了: 合計 {total_in_db}件 / 選択済み {selected_count}件")
    except Exception as e:
        logger.error(f"Failed to load accounts from DB: {e}")
        return

    if targets.empty:
        logger.error(f"実行対象のアカウントが0件です（DB合計: {total_in_db}件）。メインPCのダッシュボードでアカウントを選択してから実行してください。")
        return"""

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully patched engagement_handler.py")
else:
    # Try with slightly different whitespace if it failed
    print("Target string not found, trying fuzzy match...")
    import re
    # Simplistic fuzzy match for the specific block
    new_content = re.sub(r'df = db\.get_all_accounts_df\(\)\s+targets = df\[df\[\'Select\'\] == True\]', 
                         'df = db.get_all_accounts_df()\n        total_in_db = len(df)\n        targets = df[df[\'Select\'] == True]\n        selected_count = len(targets)\n        logger.info(f"DBから読み込み完了: 合計 {total_in_db}件 / 選択済み {selected_count}件")', content)
    new_content = re.sub(r'logger\.error\("No selected accounts in the active CSV\."\)',
                         'logger.error(f"実行対象のアカウントが0件です（DB合計: {total_in_db}件）。メインPCのダッシュボードでアカウントを選択してから実行してください。")', new_content)
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Fuzzy patch applied.")
    else:
        print("Fuzzy patch failed too.")
