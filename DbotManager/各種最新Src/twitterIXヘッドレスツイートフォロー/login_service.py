from utils.ip_rotation import ensure_ip_rotated, create_standard_router
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.ixbrowser.bot_logic_dp import IXBrowserBotLogicDP
from loguru import logger
import sys
import pandas as pd
import time
import os
import json
from modules.mutual_follow.db_manager import DBManager

# Configure Logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
logger.add("logs/auth_session.log", rotation="1 day", encoding='utf-8')

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: manual_login_launcher.py <screen_name>")
        input("Press Enter to exit...")
        return

    target_screen_name = sys.argv[1]
    logger.info(f"🚀 Starting Manual Login Process for: {target_screen_name}")

    # 1. Load Account Data
    try:
        db = DBManager()
        df = db.get_all_accounts_df()
        account = df[df['screen_name'] == target_screen_name].iloc[0]
        auth_token = account.get('auth_token')
        ct0 = account.get('ct0')
        password = account.get('password')
        email = account.get('email')
        totp_secret = account.get('totp_secret')
    except (IndexError, KeyError):
        logger.error(f"Account {target_screen_name} not found in DB.")
        input("Press Enter to exit...")
        return
    except Exception as e:
        logger.error(f"Failed to load account data from DB: {e}")
        input("Press Enter to exit...")
        return

    # 2. IP Rotation
    logger.info("📡 Checking IP Rotation...")
    router = create_standard_router()
    # Manual login usually implies user wants to see it NOW, but safety is requested.
    # User said "Automatically tethering IP switching works".
    
    try:
        success, new_ip = ensure_ip_rotated(router)
        if success:
            logger.success(f"✅ IP Rotated: {new_ip}")
        else:
            logger.warning("⚠️ IP Rotation failed or ignored. Proceeding with caution.")
    except Exception as e:
        logger.error(f"IP Rotation Error: {e}")

    # 3. Open Browser
    logger.info("🌍 Opening IXBrowser...")
    logger.info("🌍 Opening IXBrowser...")
    ix_controller = IXBrowserController()
    # [FIX] 自動作成を無効化 (allow_create=False)
    profile_id = ix_controller.get_or_create_profile(target_screen_name, password=password, email=email, allow_create=False)
    
    if not profile_id:
        logger.error("Failed to get profile ID.")
        logger.error("👉 Check the logs above. You likely need to log into the IXBrowser app.")
        input("Press Enter to exit...")
        return

    # Reverted to headless as requested
    page = ix_controller.open_browser_dp(profile_id, headless=True)
    if not page:
        logger.error("Failed to connect to browser.")
        input("Press Enter to exit...")
        return

    # 4. Token Login
    logger.info("🔑 Performing Token Login...")
    bot = IXBrowserBotLogicDP(page)
    # [FIX] Attach controller and profile_id for API access in monitoring loop
    bot.controller = ix_controller
    bot.profile_id = profile_id
    
    if auth_token and pd.notna(auth_token):
        try:
            logger.info("Attempting login... (If account is suspended, this might fail, but browser will stay open)")
            # Pass ONLY token credentials. 
            # In Manual Login mode, we do NOT want the bot to attempt password login automatically
            # because it confuses the user if the check fails (e.g. slow load) while the user sees verified login.
            success, new_cookies = bot.login_with_token(
                auth_token, 
                ct0=ct0, 
                show_2fa_tab=True
            )
            
            status, msg = bot.check_account_status()
            logger.info(f"📊 Final Check - Status: {status} ({msg})")

            # Update DB Status
            db.update_account_status(target_screen_name, is_suspended=(status == "SUSPENDED"))

            if success and status == "OK":
                logger.success(f"🎉 Login Successful for {target_screen_name}!")
                if new_cookies:
                    logger.success("Note: Token was refreshed via fallback login. You may want to update CSV.")
                logger.info("Browser session verified.")
            else:
                if status != "OK":
                    logger.error(f"❌ Account Problem Detected: {status}")
                else:
                    logger.error("❌ Token Login Failed (Home not detected).")
                logger.warning(f"Message: {msg}")
        except Exception as e:
            logger.error(f"Login process encountered an error: {e}")
            logger.warning("Browser is still open. Please check manually.")
    else:
        logger.warning("⚠️ No auth_token found. Browser opened without auto-login.")

    # 5. Token Monitoring Loop
    logger.info("👀 Starting Token Monitor...")
    logger.info("Waiting for you to log in manually (or auto-login to complete)...")
    
    last_auth_token = auth_token
    last_ct0 = ct0
    
    try:
        while True:
            try:
                # Check if browser is still open
                if not page.driver.is_running:
                    logger.warning("Browser closed by user.")
                    break
                
                # --- Method 1: Check Browser Cookies (Fastest) ---
                cookies_list = page.cookies()
                cookies = {c['name']: c['value'] for c in cookies_list}
                current_auth_token = cookies.get('auth_token')
                current_ct0 = cookies.get('ct0')
                
                # --- Method 2: Check API Cookies (Most Reliable for IXBrowser) ---
                # Sometimes DOM cookies lag or are incomplete. The API pulls from the profile file.
                if bot.profile_id:
                    api_cookies = bot.controller.client.get_profile_cookies(bot.profile_id)
                    if api_cookies:
                        for c in api_cookies:
                            if c['name'] == 'auth_token':
                                current_auth_token = c['value']
                            elif c['name'] == 'ct0':
                                current_ct0 = c['value']

                # Check for changes or new tokens
                param_changed = False
                
                if current_auth_token and current_auth_token != last_auth_token:
                    logger.success(f"New auth_token detected: {current_auth_token[:10]}...")
                    last_auth_token = current_auth_token
                    param_changed = True
                    
                if current_ct0 and current_ct0 != last_ct0:
                    logger.success(f"New ct0 detected: {current_ct0[:10]}...")
                    last_ct0 = current_ct0
                    param_changed = True
                    
                if param_changed:
                    update_db_token(target_screen_name, last_auth_token, last_ct0)
                    
                time.sleep(3)
                
            except Exception as e:
                # If browser is closed, this often raises an error
                logger.warning(f"Browser monitor disconnected: {e}")
                break
                
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")

    print("\n" + "="*50)
    print(f" Session Finished: {target_screen_name}")
    print("="*50 + "\n")

def update_db_token(screen_name, new_auth_token, new_ct0):
    """Updates the DB with the new tokens."""
    try:
        db = DBManager()
        df = db.get_all_accounts_df()
        
        if screen_name in df['screen_name'].astype(str).tolist():
            idx = df[df['screen_name'] == screen_name].index[0]
            df.at[idx, 'auth_token'] = new_auth_token
            df.at[idx, 'ct0'] = new_ct0
            db.save_accounts_df(df)
            logger.success(f"💾 Saved new tokens to DB for @{screen_name}")
        else:
            logger.error(f"User {screen_name} not found in DB during token save.")
    except Exception as e:
        logger.error(f"Failed to save tokens to DB: {e}")

def update_account_status(username, status, message):
    """Updates account is_alive and sync_status in DB."""
    try:
        db = DBManager()
        is_suspended = (status == "SUSPENDED")
        is_alive = 0 if is_suspended else 1
        
        conn = db.get_connection()
        cursor = conn.cursor()
        p = db._placeholder()
        cursor.execute(f'''
            UPDATE accounts 
            SET is_alive = {p}, sync_status = {p} 
            WHERE username = {p}
        ''', (is_alive, message, username))
        if db.db_type not in ["mysql", "postgres"]:
            conn.commit()
        logger.info(f"📊 Updated status for @{username}: {status} ({message})")
        return True
    except Exception as e:
        logger.error(f"Failed to update account status for {username}: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        with open("launcher_crash.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        logger.exception(f"Fatal Error: {e}")
        print(f"FATAL ERROR: {e}")
        print("Check launcher_crash.log for details.")
    
    # Always pause before closing window
    print("\nProcess finished.")
    input("Press Enter to exit...")
