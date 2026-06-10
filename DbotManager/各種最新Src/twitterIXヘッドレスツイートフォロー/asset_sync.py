import pandas as pd
import os
import sys
import time
import requests
from loguru import logger
# from utils.csv_manager import load_all_accounts, update_account_csv
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.ixbrowser.bot_logic_dp import IXBrowserBotLogicDP
from modules.mutual_follow.db_manager import DBManager
from androidIP自動変更.androidIP_autochange import reset_mobile_data
from concurrent.futures import ThreadPoolExecutor, TimeoutError

ICON_DIR = 'data/icons'
if not os.path.exists(ICON_DIR):
    os.makedirs(ICON_DIR)

def download_icon(screen_name, url):
    path = os.path.join(ICON_DIR, f"{screen_name}.jpg")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return path
    except Exception as e:
        logger.error(f"Error downloading icon for {screen_name}: {e}")
    return None



def sync_single_account(row, controller, db):
    """Worker for individual account asset syncing."""
    username = row.get('username') or row.get('screen_name') # Support both DB and legacy mapping
    profile_id = row.get('profile_id')
    
    if not username or not profile_id:
        logger.warning(f"Skipping account with missing Info: {username} (ID: {profile_id})")
        return False
    
    # アイコンが既に存在する場合はスキップ
    icon_path = os.path.join(ICON_DIR, f"{username}.jpg")
    if os.path.exists(icon_path):
        logger.info(f"  Icon already exists for @{username}. Skipping.")
        return True

    logger.info(f"--- [Thread] Processing @{username} (ID: {profile_id}) ---")
    db.update_sync_status(username, "実行中...")
    
    # Open browser (Headless mode for background execution)
    page = controller.open_browser_dp(profile_id, screen_name=username, headless=True)
    if not page:
        logger.error(f"Profile {profile_id} could not be opened. Skipping.")
        db.update_sync_status(username, "失敗")
        return False
        
    try:
        # Navigate to Profile Page to ensure we see the "Name"
        profile_url = f"https://x.com/{username}"
        logger.info(f"  Navigating to profile: {profile_url}")
        
        # Increase reliability with explicit wait mode
        page.set.load_mode.normal()
        page.get(profile_url, timeout=20)
        time.sleep(3) # Wait for page load
        
        # Extract assets...
        live_name = None
        # Main Selector: Profile Name
        name_ele = page.ele('xpath://div[@data-testid="UserName"]//span[1]', timeout=10)
        if name_ele:
            parts = name_ele.text.split('\n')
            if parts:
                live_name = parts[0].strip()
        
        # Fallback Selector: Side Nav
        if not live_name:
            switcher = page.ele('css:[data-testid="SideNav_AccountSwitcher_Button"]', timeout=3)
            if switcher and switcher.text:
                live_name = switcher.text.split('\n')[0].strip()

        if live_name:
            logger.success(f"  ✨ [SUCCESS] @{username} -> {live_name}")
            db.save_display_name(username, live_name)
        else:
            logger.warning(f"  ⚠️ [WARN] Real Name not found for @{username}.")
            db.save_display_name(username, username) 
        
        # Profile Icon
        img_ele = page.ele('css:a[href$="/photo"] img', timeout=5)
        if not img_ele:
            img_ele = page.ele('xpath://div[@data-testid="primaryColumn"]//img[contains(@src, "/profile_images/")]', timeout=3)
        
        if img_ele:
            src = img_ele.attr('src')
            if src:
                src = src.replace('_normal.', '_400x400.').replace('_bigger.', '_400x400.')
                local_path = download_icon(username, src)
                if local_path:
                    logger.success(f"  ✅ [SUCCESS] Icon Updated for @{username}.")
        
        db.update_sync_status(username, "完了")
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Error for {username}: {e}")
        db.update_sync_status(username, f"失敗")
        return False
    finally:
        try:
            page.quit()
        except: pass
        controller.close_browser(profile_id)

def sync_assets(only_selected=False, rotate_ip=False, missing_only=False):
    logger.info("🎨 アセット（名前・アイコン）同期プロセスを開始します...")
    
    db = DBManager()
    controller = IXBrowserController()
    
    # [NEW] Check DB status
    accounts_list = db.get_all_accounts_from_db()
    
    if not accounts_list:
        logger.error("データベースにアカウントが見つかりません。")
        return

    # [NEW] Pre-fetch profile IDs once if any are missing
    has_missing_id = any(not acc.get('profile_id') for acc in accounts_list)
    if has_missing_id:
        logger.info("Some accounts are missing profile_id. Fetching all profiles from IXBrowser API once to resolve...")
        try:
            all_p = controller.get_all_accounts()
            p_map = {p['screen_name']: p['profile_id'] for p in all_p if p.get('screen_name') and p.get('profile_id')}
            for acc in accounts_list:
                username = acc.get('username') or acc.get('screen_name')
                if not acc.get('profile_id') and username in p_map:
                    acc['profile_id'] = p_map[username]
        except Exception as e_api:
            logger.error(f"Failed to fetch profiles from API during pre-sync: {e_api}")

    if only_selected:
        targets = [acc for acc in accounts_list if acc.get('selected') == 1]
        if not targets:
            logger.warning("対象アカウントが選択されていません。")
            return
    else:
        targets = accounts_list
    
    if missing_only:
        targets = [acc for acc in targets if not os.path.exists(
            os.path.join(ICON_DIR, f"{acc.get('username') or acc.get('screen_name')}.jpg")
        )]
        logger.info(f"画像未設定のアカウント: {len(targets)} 件")

    success_count = 0
    batch_size = 5
    try:
        if os.path.exists('config.json'):
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                batch_size = cfg.get("MAX_WORKERS", 5)
    except:
        pass

    for i in range(0, len(targets), batch_size):
        chunk = targets[i:i + batch_size]
        
        # IP Rotation per Batch
        if rotate_ip:
            logger.info(f"--- [SYSTEM] Starting Batch IP Rotation ({i//batch_size + 1}) ---")
            reset_mobile_data()
            controller.wait_until_api_ready(timeout=60)
            
        logger.info(f"Processing batch of {len(chunk)} accounts in parallel...")
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(sync_single_account, row, controller, db) for row in chunk]
            for future in futures:
                try:
                    if future.result(timeout=300): # 5 min timeout
                        success_count += 1
                except Exception as e:
                    logger.error(f"Thread sync error: {e}")

        # バッチ終了後に一括クローズ
        chunk_ids = [row.get('profile_id') for row in chunk if row.get('profile_id')]
        if chunk_ids:
            controller.client.close_profiles_batch(chunk_ids)
                    
    logger.success(f"🏁 同期完了。 {success_count} アカウントのアセットを更新しました。")
            
    logger.success(f"🏁 同期完了。 {success_count} アカウントのアセットを更新しました。")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--selected', action='store_true', help='Sync only selected')
    parser.add_argument('--rotate-ip', action='store_true', help='Rotate IP during sync')
    parser.add_argument('--missing-only', action='store_true')
    args = parser.parse_args()
    
    sync_assets(only_selected=args.selected, rotate_ip=args.rotate_ip, missing_only=args.missing_only)
