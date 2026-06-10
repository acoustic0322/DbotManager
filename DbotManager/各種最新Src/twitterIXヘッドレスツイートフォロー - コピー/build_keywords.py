import json
import re

# 250人格のライブラリから、仕分け用のキーワードを自動で抽出・マッピングするスクリプト。
# これにより、AIを使わずにローカルで高速仕分けが可能になります。

def build_keyword_map():
    with open('data/persona_library.json', 'r', encoding='utf-8') as f:
        library = json.load(f)
    
    # カテゴリー名と設定テキストから、その人格を象徴するキーワードを自動生成
    keyword_map = {}
    
    for item in library:
        cat = item['category']
        text = item['text']
        
        # 抽出ルール：カッコ内の言葉、カタカナ語、英単語、設定テキスト内の特定ワード
        found_words = re.findall(r'[A-Za-z]+|[ア-ンー]+', cat + text)
        found_words = [w for w in found_words if len(w) > 1]
        
        # 追加のヒント
        if "裏垢" in cat or "裏垢" in text: found_words.append("裏垢")
        if "支配" in text: found_words.extend(["舐め犬", "調教", "服従"])
        
        keyword_map[cat] = list(set(found_words))

    with open('data/keyword_map.json', 'w', encoding='utf-8') as f:
        json.dump(keyword_map, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    build_keyword_map()
    print("Keyword map generated successfully.")
