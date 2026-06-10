import sqlite3
import pandas as pd

def check_sync_status():
    conn = sqlite3.connect('system.db')
    try:
        df = pd.read_sql_query("SELECT sync_status, COUNT(*) as count FROM accounts GROUP BY sync_status", conn)
        print("--- DB Status Summary ---")
        for idx, row in df.iterrows():
            print(f"{repr(row['sync_status'])}: {row['count']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_sync_status()
