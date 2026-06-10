import sys
import os
sys.path.append(os.getcwd())
from modules.mutual_follow.db_manager import DBManager
import pandas as pd

db = DBManager()
df = db.get_all_accounts_df()
print(f"Total: {len(df)}")
print("Unique Groups:", df['group_name'].unique())
print("Unique Categories:", df['category'].unique())
print("Sample group_name values:", df['group_name'].head(10).tolist())
print("Sample category values:", df['category'].head(10).tolist())
