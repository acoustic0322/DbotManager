from modules.mutual_follow.db_manager import DBManager
import pandas as pd
from datetime import datetime

db = DBManager()
df = db.get_all_accounts_df()

if not df.empty:
    print("Recent status checks:")
    if 'last_full_check' in df.columns:
        # Show accounts checked today
        today = datetime.now().strftime('%Y-%m-%d')
        checked_today = df[df['last_full_check'].astype(str).str.contains(today, na=False)]
        print(f"Accounts checked today: {len(checked_today)}")
        if not checked_today.empty:
            print(checked_today[['username', 'last_full_check', 'sync_status', 'is_alive']].head(10))
    else:
        print("Column 'last_full_check' missing.")
