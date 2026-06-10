from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
df = db.get_all_accounts_df()

if df.empty:
    print("No accounts found.")
else:
    # Check what columns we have
    print(f"Columns: {df.columns.tolist()}")
    
    # Check accounts that should be in Frozen menu
    frozen_filter = (df['is_suspended'] == True) | (df['sync_status'].str.contains('凍結', na=False))
    frozen_df = df[frozen_filter]
    
    print(f"Total frozen: {len(frozen_df)}")
    if not frozen_df.empty:
        print(frozen_df[['username', 'is_alive', 'is_suspended', 'sync_status']].head(20))
    
    # Check for Suspended in English
    eng_suspended = df[df['sync_status'].str.contains('Suspended', case=False, na=False)]
    print(f"Total 'Suspended' (English): {len(eng_suspended)}")
    if not eng_suspended.empty:
        print(eng_suspended[['username', 'is_alive', 'is_suspended', 'sync_status']].head(10))
