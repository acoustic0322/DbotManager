import re

filepath = r"h:\マイドライブ\twitterIXヘッドレスツイートフォロー\engagement_handler.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace everything from the LOCKED check up to execute_engagement call
pattern = r'(\s+)if login_success == "LOCKED":.*?\1action_success, status = execute_engagement\('

replacement = """        if login_success == "LOCKED":
            logger.warning(f"[{username}] アカウントロック検知。スキップします。")
            db.update_sync_status(username, "ロック")
            return False
        if login_success == "SUSPENDED":
            logger.error(f"[{username}] アカウント凍結検知。")
            db.update_account_status(username, is_suspended=True)
            db.update_sync_status(username, "凍結検知")
            return False

        if not login_success:
            logger.error(f"[{username}] Token login failed (Token is invalid or expired). Aborting engagement.")
            db.update_sync_status(username, "ログイン失敗")
            return False

        action_success, status = execute_engagement("""

# Using re.DOTALL to let .* match across newlines
new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

if count > 0:
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)
    print(f"SUCCESS: Successfully cleaned up engagement_handler.py and simplified login. Count={count}")
else:
    print("ERROR: Pattern not matched!")
