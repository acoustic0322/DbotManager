import sqlite3
import pandas as pd
import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# DBManagerと同様のロジックでDataFrameを作成
db_path = 'system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts')
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        df = df.rename(columns={'username': 'screen_name', 'selected': 'Select'})
        
        # screen_name の中に 'data/' を含むものがないか再チェック
        bad_rows = df[df['screen_name'].str.contains('data/', na=False)]
        if not bad_rows.empty:
            print(f"Found {len(bad_rows)} rows where screen_name contains 'data/':")
            print(bad_rows[['screen_name', 'display_name']].head())
        else:
            print("No 'data/' found in screen_name column in the DataFrame.")
            
        # 他のカラムに 'data/' が入っていないか
        for col in df.columns:
            count = df[df[col].astype(str).str.contains('data/', na=False)].shape[0]
            if count > 0:
                print(f"Column '{col}' has {count} entries containing 'data/'.")
    else:
        print("DB is empty.")
