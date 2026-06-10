import sys
import os
import time
import json
import sqlite3
import subprocess
from loguru import logger
from modules.mutual_follow.db_manager import DBManager
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.ixbrowser.bot_logic_dp import IXBrowserBotLogicDP
from androidIP自動変更.androidIP_autochange import reset_mobile_data
from concurrent.futures import ThreadPoolExecutor

# engagement_handler.py の一部ロジックを利用するためにパスを通す
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("logs/bulk_login.log", rotation="1 day", encoding='utf-8')

def clear_task_progress_failure(username):
    progress_path = os.path.join('data', 'task_progress.json')
    if not os.path.exists(progress_path):
        return
    try:
        with open(progress_path, 'r', encoding='utf-8') as f:
            progress = json.load(f)

        fail_list = progress.get('fail_list', [])
        filtered = [
            item for item in fail_list
            if str(item.get('name', '')).lstrip('@') != str(username).lstrip('@')
        ]
        removed_count = len(fail_list) - len(filtered)
        if removed_count <= 0:
            return

        progress['fail_list'] = filtered
        if isinstance(progress.get('fail'), int):
            progress['fail'] = max(0, progress.get('fail', 0) - removed_count)

        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False)
        logger.info(f"[{username}] Removed from task_progress fail_list.")
    except Exception as e:
        logger.warning(f"[{username}] Failed to clear task_progress fail_list: {e}")

def process_login_only(username, controller, db):
    logger.info(f"--- Processing Login for: @{username} ---")
    profile_id = None
    page = None
    reset_profile_after_close = False
    reset_reason = None
    
    try:
        db = DBManager()
        # DBから最新情報を取得
        conn = db.get_connection()
        cursor = conn.cursor()
        p = db._placeholder()
        cursor.execute(f'SELECT * FROM accounts WHERE username = {p}', (username,))
        row = cursor.fetchone()
        acc = dict(row) if row else {}

        profile_id = controller.get_or_create_profile(username)
        if not profile_id:
            logger.error(f"[{username}] Could not prepare profile.")
            return False

        # ヘッドレスだとログインの様子が見えないため、ユーザーの要望により可視モード（headless=False）に変更
        page = controller.open_browser_dp(profile_id, screen_name=username, headless=False)
        if not page:
            logger.error(f"[{username}] Could not open browser.")
            return False

        bot = IXBrowserBotLogicDP(page)
        auth_token = acc.get('auth_token')
        ct0 = acc.get('ct0')
        password = acc.get('password', '')
        email = acc.get('email')
        totp_secret = acc.get('totp_secret')

        # __B__プレフィックスの処理
        use_b_column = str(password).startswith('__B__')
        if use_b_column:
            password = str(password)[5:]

        logger.info(f"[{username}] Attempting login...")
        login_success = False
        new_cookies = None
        token_attempted = False
        has_auth_token = auth_token and str(auth_token).strip().lower() not in ("", "none", "nan")
        has_ct0 = ct0 and str(ct0).strip().lower() not in ("", "none", "nan")
        if has_auth_token and has_ct0:
            token_attempted = True
            login_success, new_cookies = bot.login_with_token(
                auth_token, ct0=ct0, username=username,
                password=password, email=email, totp_secret=totp_secret
            )
        else:
            logger.warning(f"[{username}] auth_token/ct0 missing. Skipping token login.")

        if not login_success:
            if token_attempted:
                logger.warning(f"[{username}] Token login failed. Trying password login...")
            else:
                logger.info(f"[{username}] Trying password login...")
            if password and (email or username):
                result = bot.login_with_password(
                    username=username,
                    password=password,
                    email=email,
                    totp_secret=totp_secret
                )
                if isinstance(result, tuple):
                    login_success, new_cookies = result
                elif result is True:
                    login_success = True
                elif isinstance(result, str):
                    logger.warning(f"[{username}] Password login returned status: {result}")
                    db.update_sync_status(username, result)
                    if result.startswith("JF_ERROR") or result == "TEMP_LOGIN_LIMIT":
                        reset_profile_after_close = True
                        reset_reason = result
                    login_success = False
                else:
                    login_success = False
                
                # B列使用時のみ042210を付けて再試行
                if not login_success and use_b_column and password and not password.endswith('042210'):
                    logger.info(f"[{username}] Retrying with password suffix...")
                    result2 = bot.login_with_password(
                        username=username,
                        password=password + '042210',
                        email=email,
                        totp_secret=totp_secret
                    )
                    if isinstance(result2, tuple):
                        login_success, new_cookies = result2
                    elif result2 is True:
                        login_success = True
                    elif isinstance(result2, str):
                        logger.warning(f"[{username}] Password retry returned status: {result2}")
                        db.update_sync_status(username, result2)
                        if result2.startswith("JF_ERROR") or result2 == "TEMP_LOGIN_LIMIT":
                            reset_profile_after_close = True
                            reset_reason = result2
                        login_success = False
                    else:
                        login_success = False
            
        if login_success:
            if isinstance(new_cookies, dict) and new_cookies.get("auth_token") and new_cookies.get("ct0"):
                db.update_cookies(username, new_cookies.get("auth_token"), new_cookies.get("ct0"))
                logger.success(f"[{username}] Saved refreshed cookies to DB.")
            status, msg = bot.check_account_status()
            logger.success(f"[{username}] Login Success! Status: {status} ({msg})")
            
            # ステータス更新 & 失敗リストからの自動削除
            is_alive = 0 if status == "SUSPENDED" else 1
            
            if status == "OK":
                db.clear_failure_states(username)
                clear_task_progress_failure(username)
            else:
                db.update_sync_status(username, msg)
            
            cursor.execute(f'UPDATE accounts SET is_alive = {p} WHERE username = {p}', (is_alive, username))
            if db.db_type not in ["mysql", "postgres"]: conn.commit()
        else:
            logger.error(f"[{username}] Login failed after all attempts.")
            if reset_reason:
                db.update_sync_status(username, f"{reset_reason} | PROFILE_RESET_PENDING")
                return False
            db.update_sync_status(username, "ログイン失敗")

        return login_success

    except Exception as e:
        logger.error(f"[{username}] Login process error: {e}")
        return False
    finally:
        if page:
            try:
                page.quit()
            except Exception:
                pass
        if profile_id:
            try:
                controller.close_browser(profile_id, screen_name=username)
            except Exception as close_err:
                logger.warning(f"[{username}] Failed to close browser cleanly: {close_err}")
        if reset_profile_after_close and profile_id:
            try:
                new_profile_id = controller.reset_profile_default_optimized(profile_id, username)
                if new_profile_id:
                    db.update_sync_status(username, f"{reset_reason} | PROFILE_RECREATED:{new_profile_id}")
                else:
                    db.update_sync_status(username, f"{reset_reason} | PROFILE_RECREATE_FAILED")
            except Exception as reset_err:
                logger.error(f"[{username}] Profile recreate after JF error failed: {reset_err}")
                try:
                    db.update_sync_status(username, f"{reset_reason} | PROFILE_RECREATE_ERROR")
                except Exception:
                    pass

def run_login_failure_accounts(db, cursor, p):
    cursor.execute(
        f"""
        SELECT username FROM accounts
        WHERE COALESCE(sync_status, '') LIKE {p}
           OR COALESCE(sync_status, '') LIKE {p}
           OR COALESCE(sync_status, '') LIKE {p}
           OR COALESCE(sync_status, '') LIKE {p}
        ORDER BY username ASC
        """,
        ('%ログイン失敗%', '%繝ｭ繧ｰ繧､繝ｳ螟ｱ謨%', '%実行失敗%', '%Error%')
    )
    rows = cursor.fetchall()
    failed_accounts = [r[0] if isinstance(r, (tuple, list)) else r['username'] for r in rows]

    if not failed_accounts:
        logger.info("No login failure accounts found.")
        return

    total_needed = len(failed_accounts)
    success_count = 0
    fail_count = 0

    logger.info(f"Starting Bulk Login for {total_needed} accounts...")
    
    if reset_mobile_data():
        logger.success("IP Rotated.")

    controller = IXBrowserController()
    controller.wait_until_api_ready(timeout=60)
    
    max_workers = 2
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                max_workers = cfg.get("MAX_WORKERS", 2)
    except Exception:
        pass

    if sys.platform == 'win32':
        os.system(f'title D-BOT [Bulk login running... Total:{total_needed}]')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_login_only, u, controller, db): u for u in failed_accounts}
        for future in futures:
            try:
                if future.result():
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                logger.error(f"Error: {e}")
                fail_count += 1
            
            if sys.platform == 'win32':
                os.system(f'title D-BOT [Bulk login Total:{total_needed} OK:{success_count} Fail:{fail_count}]')

    logger.info("\n" + "=" * 30)
    logger.success("Bulk login finished.")
    logger.info(f"  Target accounts: {total_needed}")
    logger.info(f"  Login success: {success_count}")
    logger.info(f"  Login failed: {fail_count}")
    logger.info("=" * 30 + "\n")

def main():
    db = DBManager()
    
    # ログイン失敗アカウントを抽出
    conn = db.get_connection()
    cursor = conn.cursor()
    p = db._placeholder()
    return run_login_failure_accounts(db, cursor, p)
    cursor.execute(f"SELECT username FROM accounts WHERE sync_status = {p}", ('ログイン失敗',))
    rows = cursor.fetchall()
    failed_accounts = [r[0] if isinstance(r, (tuple, list)) else r['username'] for r in rows]

    if not failed_accounts:
        logger.info("No login failure accounts found.")
        return

    total_needed = len(failed_accounts)
    success_count = 0
    fail_count = 0

    logger.info(f"Starting Bulk Login for {total_needed} accounts...")
    
    # IP回転
    if reset_mobile_data():
        logger.success("IP Rotated.")

    controller = IXBrowserController()
    controller.wait_until_api_ready(timeout=60)
    
    # 並列実行数は設定から取得（デフォルト2）
    max_workers = 2
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                max_workers = cfg.get("MAX_WORKERS", 2)
    except: pass

    # コンソールタイトルに進捗を表示
    if sys.platform == 'win32':
        os.system(f'title D-BOT [再ログイン実行中... 全:{total_needed}]')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_login_only, u, controller, db): u for u in failed_accounts}
        for future in futures:
            try:
                if future.result():
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                logger.error(f"Error: {e}")
                fail_count += 1
            
            # タイトル更新
            if sys.platform == 'win32':
                os.system(f'title D-BOT [再ログイン 全:{total_needed} 完了:{success_count} 失敗:{fail_count}]')

    logger.info("\n" + "★"*30)
    logger.success("再ログイン処理が終了しました。")
    logger.info(f"  ● 対象アカウント数: {total_needed}")
    logger.info(f"  ● ログイン成功: {success_count}")
    logger.info(f"  ● ログイン失敗: {fail_count}")
    logger.info("★"*30 + "\n")

if __name__ == "__main__":
    main()
