import sys
import os
sys.path.append(os.getcwd())
from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
df = db.get_all_accounts_df()
print(f"Total accounts: {len(df)}")
if not df.empty:
    print(df.head())
    print(df.columns)
else:
    # Try raw fetch
    raw = db.get_all_accounts_from_db()
    print(f"Raw fetch count: {len(raw)}")
