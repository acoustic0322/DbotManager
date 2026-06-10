import sys
import os
import time
import json
import argparse
import pandas as pd
from loguru import logger
from DrissionPage.common import Keys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.ixbrowser.bot_logic_dp import IXBrowserBotLogicDP
from utils.ip_rotation import ensure_ip_rotated
from modules.router.pixel_rotator import PixelIPRotator
from modules.mutual_follow.db_manager import DBManager

def setup_logger():
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("logs/account_mgmt.log", rotation="1 day", encoding='utf-8', level="DEBUG")

def save_main_account_info(screen_name, password, cookies):
    """
    Saves or updates main account info directly in the DB.
    """
    try:
        db = DBManager()
        auth_token = cookies.get("auth_token", "")
        ct0 = cookies.get("ct0", "")
        
        df = db.get_all_accounts_df()
        
        # Check if already in DB
        if not df.empty and screen_name in df['screen_name'].astype(str).tolist():
            # Update specific fields
            idx = df[df['screen_name'] == screen_name].index[0]
            df.at[idx, 'password'] = password
            df.at[idx, 'auth_token'] = auth_token
            df.at[idx, 'ct0'] = ct0
            db.save_accounts_df(df)
            db.clear_failure_states(screen_name)
            logger.info(f"Updated account @{screen_name} in DB and cleared failure states.")
        else:
            # Add as new entry
            new_row_data = {
                'screen_name': screen_name,
                'username': screen_name,
                'password': password,
                'auth_token': auth_token,
                'ct0': ct0,
                'Select': True,
                'is_suspended': False,
                'sync_status': ''
            }
            new_df = pd.DataFrame([new_row_data])
            combined = pd.concat([df, new_df], ignore_index=True)
            db.save_accounts_df(combined)
            db.clear_failure_states(screen_name)
            logger.info(f"Added new account @{screen_name} to DB and cleared failure states.")
            
        return True
    except Exception as e:
        logger.error(f"Failed to save account info to DB: {e}")
        return False

def main():
    setup_logger()
    
    parser = argparse.ArgumentParser(description="Main Account Manager")
    parser.add_argument("username", help="Twitter Username/ID")
    parser.add_argument("password", help="Twitter Password")
    parser.add_argument("--email", help="Twitter Email (Optional, for verification)")
    parser.add_argument("--rotate-ip", action="store_true", help="Rotate IP before login")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--group-id", help="IXBrowser Group ID to create the profile in")
    
    args = parser.parse_args()
    
    username = args.username
    password = args.password
    
    # 1. IP Rotation
    if args.rotate_ip:
        logger.info("Rotating IP (Android Airplane Mode)...")
        rotator = PixelIPRotator()
        success, new_ip = ensure_ip_rotated(rotator)
        
        if success:
             logger.info(f"IP Rotation completed. New IP: {new_ip}")
        else:
             logger.warning("IP Rotation failed. Proceeding anyway...")
        
        time.sleep(5)

    # 2. IXBrowser Setup
    ix = IXBrowserController()
    logger.info(f"Checking/Creating profile for {username} (Group: {args.group_id})...")
    profile_id = ix.get_or_create_profile(username, group_id=args.group_id)
    
    if not profile_id:
        logger.error("Failed to get IXBrowser profile.")
        return

    logger.info(f"Opening browser for {username} (Headless: {args.headless})...")
    page = ix.open_browser_dp(profile_id, screen_name=username, headless=args.headless)
    
    if not page:
        logger.error("Failed to open browser.")
        return

    try:
        bot = IXBrowserBotLogicDP(page)
        
        # 3. Login
        if bot.login_with_password(username, password, email=args.email):
            # 4. Harvest Cookies (Robust Mode)
            logger.info("Login successful. Waiting for cookies to sync...")
            
            # Sub-function to extract dict from API list
            def get_tokens_from_api(pid):
                try:
                    c_list = ix.client.get_profile_cookies(pid)
                    if not c_list: 
                        logger.debug("API returned empty cookie list.")
                        return {}
                    
                    logger.debug(f"API returned {len(c_list)} cookies.")
                    # Log first few cookies to verify structure if needed (careful with secrets, but names are fine)
                    # logger.debug(f"First cookie keys: {list(c_list[0].keys()) if c_list else 'None'}")
                    
                    token_map = {}
                    for c in c_list:
                         # Normalize keys just in case
                         name = c.get('name')
                         value = c.get('value')
                         if name == 'auth_token': token_map['auth_token'] = value
                         elif name == 'ct0': token_map['ct0'] = value
                    
                    logger.debug(f"Extracted tokens from API: {token_map.keys()}")
                    return token_map
                except Exception as err:
                    logger.warning(f"API Cookie fetch warning: {err}")
                    return {}

            final_cookies = {}
            # Retry loop (Try for up to 15 seconds)
            for attempt in range(5):
                logger.info(f"Cookie fetch attempt {attempt+1}/5...")
                
                # A. Try API (Most Reliable if synced)
                api_tokens = get_tokens_from_api(profile_id)
                if api_tokens.get("auth_token") and api_tokens.get("ct0"):
                    final_cookies = api_tokens
                    logger.success("Got valid tokens from IXBrowser API.")
                    break
                
                # B. Try DOM via Bot Logic
                dom_cookies = bot.get_current_cookies() # Returns dict or empty
                if dom_cookies.get("auth_token") and dom_cookies.get("ct0"):
                    final_cookies = dom_cookies
                    logger.success("Got valid tokens from Browser DOM.")
                    break
                
                # Wait before retry
                time.sleep(3)

            if not final_cookies.get("auth_token"):
                logger.warning("Could not fully retrieve tokens even after retries.")
                # Fallback to whatever we have last (likely empty or partial)
                final_cookies = bot.get_current_cookies()

            logger.success(f"Final Cookies: {final_cookies}")
            
            # 5. Save locally
            save_main_account_info(username, password, final_cookies)
            
            # 6. Output for UI
            # Print JSON to stdout so app.py can capture it
            result = {
                "status": "success",
                "screen_name": username,
                "auth_token": final_cookies.get("auth_token"),
                "ct0": final_cookies.get("ct0")
            }
            print(json.dumps(result))
        else:
            logger.error("Login failed.")
            print(json.dumps({"status": "error", "message": "Login failed"}))

    except Exception as e:
        logger.error(f"process error: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
    finally:
        # Keep open for a bit to debug or close?
        # User might want to keep it open, but usually scripts close or detach.
        # For now, we leave it open or let user close manually?
        # If we return, script ends, but browser stays open if detached.
        # DrissionPage usually stays open unless page.quit()
        logger.info("Script finished.")

if __name__ == "__main__":
    main()
