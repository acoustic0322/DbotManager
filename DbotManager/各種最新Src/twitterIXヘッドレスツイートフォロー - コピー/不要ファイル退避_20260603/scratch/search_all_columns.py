from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
df = db.get_all_accounts_df()

if not df.empty:
    for col in df.columns:
        try:
            matches = df[df[col].astype(str).str.contains('凍結|Suspended', case=False, na=False)]
            if not matches.empty:
                print(f"Found {len(matches)} matches in column '{col}':")
                print(matches[['username', col]].head())
        except:
            pass
