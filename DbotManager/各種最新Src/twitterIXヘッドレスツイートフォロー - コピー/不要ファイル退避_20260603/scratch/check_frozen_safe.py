from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
df = db.get_all_accounts_df()

if not df.empty:
    # Filter for anything that looks frozen but NOT currently showing up
    # Current UI filter: (is_suspended == True) | (sync_status contains '凍結')
    
    mask_frozen_keywords = df['sync_status'].str.contains('凍結|Suspended|Unavailable', case=False, na=False)
    mask_is_alive_0 = (df['is_alive'] == 0) | (df['is_alive'] == False) | (df['is_alive'].isna())
    
    combined = mask_frozen_keywords | mask_is_alive_0
    
    print(f"Total potential frozen: {len(df[combined])}")
    # Print without emojis to avoid encoding errors
    for idx, row in df[combined].iterrows():
        status = str(row['sync_status']).replace('🚩', '[flag]')
        print(f"U: {row['username']} | Alive: {row['is_alive']} | Status: {status}")
