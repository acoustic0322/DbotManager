import sqlite3
import pandas as pd

def check_sync_status():
    conn = sqlite3.connect('system.db')
    df = pd.read_sql_query("SELECT screen_name, sync_status FROM accounts WHERE sync_status != ''", conn)
    print("\n--- Current Active Statuses ---")
    if df.empty:
        print("No accounts have active sync_status.")
    else:
        print(df)
    conn.close()

if __name__ == "__main__":
    check_sync_status()
