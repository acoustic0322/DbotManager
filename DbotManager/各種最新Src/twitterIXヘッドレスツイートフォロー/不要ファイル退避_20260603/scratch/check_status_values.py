from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
df = db.get_all_accounts_df()

if not df.empty:
    print("Unique sync_status values:")
    print(df['sync_status'].value_counts())
    
    print("\nAccounts with 'Suspended' or '凍結' or 'ロック' in sync_status:")
    mask = df['sync_status'].str.contains('凍結|Suspended|Locked|ロック|Unavailable', case=False, na=False)
    print(df[mask][['username', 'is_alive', 'sync_status']])
