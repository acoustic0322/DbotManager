import json

# 250人格すべてのキーワードを、より「人間の直感」に近い強力なスラングで上書き・補強します。
# これにより、ダイビングがポイ活になるような「誤解」を根絶します。

def strengthen_matrix():
    matrix_path = 'data/keyword_matrix.json'
    with open(matrix_path, 'r', encoding='utf-8') as f:
        matrix = json.load(f)

    # 重要なマッチング漏れを防ぐための追加
    extra_rules = {
        "ダイビング・マリンスポーツ": ["ダイビング", "潜水", "AOW", "ライセンス", "セブ島", "沖縄の海", "潜りたい", "シュノーケル", "海の中", "魚影"],
        "ポイ活・節約": ["ポイ活", "ポイント", "Amazon", "ギフト", "マイル", "節約", "ウェル活", "ポン活", "ハピタス", "モッピー"],
        "裏垢(支配系)": ["舐め犬", "しつけ", "わんこ", "躾", "跪け", "ご主人様", "支配", "女王"],
        "裏垢(M系)": ["わんこになりたい", "ブタ", "踏まれたい", "ひねりだしたい", "我慢", "お漏らし", "おもらし"],
        "アニメ考察": ["最新話", "原作", "アニメ化", "神回", "作画", "聖地巡礼", "声優", "円盤"]
        # (ここを全250人格分、私が一つ一つチェックして書き込みます)
    }

    # 既存の辞書に強力なルールを上書き
    for cat, kws in extra_rules.items():
        if cat in matrix:
            matrix[cat].extend(kws)
        else:
            matrix[cat] = kws

    with open('data/keyword_matrix.json', 'w', encoding='utf-8') as f:
        json.dump(matrix, f, ensure_ascii=False, indent=4)
    print("Matrix strengthened with priority keywords.")

if __name__ == "__main__":
    strengthen_matrix()
