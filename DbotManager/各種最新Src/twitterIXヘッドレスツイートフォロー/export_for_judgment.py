import sqlite3
import json

def export_all_bios_for_judgment():
    db_path = 'system.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ログイン不要の巡回等で取得したすべてのBioを抽出
    cursor.execute("SELECT username, display_name, biography FROM accounts WHERE biography IS NOT NULL AND biography != ''")
    rows = cursor.fetchall()
    
    data = []
    for r in rows:
        data.append({
            "username": r[0],
            "display_name": r[1],
            "biography": r[2]
        })
    
    with open('data/judgment_list.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Ready. {len(data)} accounts exported for judgment.")
    conn.close()

if __name__ == "__main__":
    export_all_bios_for_judgment()
