import sqlite3
import json

def export_raw_accounts():
    db_path = 'data/accounts.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 判定が必要なアカウントを抽出
    cursor.execute("""
        SELECT screen_name, display_name, biography, category 
        FROM accounts 
        WHERE category IS NULL 
           OR category = '日常・一般' 
           OR category = '日常生活'
           OR category = '未分類(要確認)'
        LIMIT 50
    """)
    rows = cursor.fetchall()
    
    data = []
    for r in rows:
        data.append({
            "screen_name": r[0],
            "display_name": r[1],
            "biography": r[2],
            "current_category": r[3]
        })
    
    with open('data/raw_accounts_for_ai.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Exported {len(data)} accounts to data/raw_accounts_for_ai.json")
    conn.close()

if __name__ == "__main__":
    export_raw_accounts()
