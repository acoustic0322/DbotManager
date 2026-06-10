import sqlite3
import os
import sys
from loguru import logger

# Add root to sys.path
sys.path.append(os.getcwd())

from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.mutual_follow.db_manager import DBManager

def repair_groups():
    logger.info("Connecting to IXBrowser to fetch latest group info...")
    ix = IXBrowserController()
    db = DBManager()
    
    try:
        # 1. Fetch all groups and profiles from IXBrowser
        all_groups = ix.get_all_groups()
        group_map = {str(g['id']): g['title'] for g in all_groups}
        
        profiles = ix.client.get_profile_list(limit=2000)
        if not profiles:
            logger.error("No profiles fetched from IXBrowser.")
            return

        # 2. Load DB accounts
        df = db.get_all_accounts_df()
        logger.info(f"Loaded {len(df)} accounts from DB.")
        
        count = 0
        for p in profiles:
            username = p.get('name') # screen_name
            gid = str(p.get('group_id', ''))
            gname = group_map.get(gid, '')
            
            if not username or not gname:
                continue
                
            if username in df['screen_name'].tolist():
                idx = df[df['screen_name'] == username].index[0]
                # Update group info
                df.at[idx, 'group_id'] = gid
                df.at[idx, 'group_name'] = gname
                # Also set category if it was missing or generic
                if not df.at[idx, 'category'] or df.at[idx, 'category'] == '日常生活':
                    df.at[idx, 'category'] = gname
                count += 1

        # 3. Save back to DB
        db.save_accounts_df(df)
        logger.success(f"✅ Repaired {count} accounts with correct group names.")
        
    except Exception as e:
        logger.exception(f"Failed to repair groups: {e}")

if __name__ == "__main__":
    repair_groups()
