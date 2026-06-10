import json
import os

def debug_diving_error():
    # 判定エンジンのシミュレーション
    name = "ダイビング垢"
    bio = "AOW取得 | 沖縄/セブ | 海の中の世界が好き"
    combined = f"{name} {bio}".lower()
    
    matrix_path = 'data/keyword_matrix.json'
    if not os.path.exists(matrix_path):
        print("Matrix not found")
        return
        
    with open(matrix_path, 'r', encoding='utf-8') as f:
        matrix = json.load(f)
    
    scores = {}
    for cat, kws in matrix.items():
        matches = [kw for kw in kws if kw.lower() in combined]
        if matches:
            scores[cat] = len(matches)
            print(f"DEBUG: Category '{cat}' matched: {matches}")

    if scores:
        winner = max(scores, key=scores.get)
        print(f"WINNER: {winner}")

if __name__ == "__main__":
    debug_diving_error()
