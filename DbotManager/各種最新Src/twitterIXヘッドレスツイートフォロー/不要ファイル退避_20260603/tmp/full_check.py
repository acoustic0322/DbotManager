import os
import json
import sqlite3
import sys

# Add root to path
sys.path.append('.')

def check():
    print("=== System Diagnostic Start ===")
    
    # 1. Check Matrix JSON
    matrix_path = 'data/keyword_matrix.json'
    if os.path.exists(matrix_path):
        try:
            with open(matrix_path, 'r', encoding='utf-8') as f:
                matrix = json.load(f)
            print(f"OK: Matrix found. ({len(matrix)} categories)")
            first_cat = list(matrix.keys())[0]
            print(f"    Sample: {first_cat} (Keywords: {len(matrix[first_cat])})")
        except Exception as e:
            print(f"ERROR: Matrix load failed: {e}")
    else:
        print(f"ERROR: Matrix not found: {matrix_path}")

    # 2. Check Database
    db_path = 'system.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('SELECT username, display_name, biography, category FROM accounts LIMIT 5')
            rows = c.fetchall()
            print(f"OK: Database found. ({len(rows)} accounts sample)")
            for r in rows:
                bio_short = str(r[2]).replace('\n', ' ')[:20] if r[2] else 'None'
                print(f"    @{r[0]} | Name: {r[1]} | Bio: {bio_short} | Cat: {r[3]}")
            conn.close()
        except Exception as e:
            print(f"ERROR: Database access failed: {e}")
    else:
        print(f"ERROR: Database not found: {db_path}")

    # 3. Test Internal Logic
    try:
        from modules.ai_generator import AIGenerator
        ai = AIGenerator()
        test_text = "ダイビングが趣味の裏垢女子です。舐め犬募集"
        res = ai.determine_theme("テスト", test_text)
        if res:
            print(f"OK: Logic test Result: {res}")
        else:
            print(f"WARN: Logic test No Match. (Checking first matrix key: {list(matrix.keys())[0] if matrix else 'N/A'})")
    except Exception as e:
        print(f"ERROR: Logic test crashed: {e}")

    print("=== System Diagnostic End ===")

if __name__ == "__main__":
    check()
