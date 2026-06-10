import json
import re

# 250人格のライブラリ(persona_library.json)から、
# すべての人格の「ジャンル名」と「設定テキスト」を解析し、
# 250項目すべてに対応するキーワードマトリックスを自動生成します。

def build_complete_persona_matrix():
    # 既存の250人格ライブラリを読み込む
    lib_path = 'data/persona_library.json'
    try:
        with open(lib_path, 'r', encoding='utf-8') as f:
            library = json.load(f)
    except Exception as e:
        print(f"Error loading library: {e}")
        return

    matrix = {}
    for entry in library:
        category = entry.get('category')
        group = entry.get('group', '')
        text = entry.get('text', '')
        
        # 1. 基本的なキーワード抽出（名詞、カタカナ、英単語）
        keywords = re.findall(r'[A-Za-z0-9]+|[ア-ンー]+|[一-龠]{2,}', category + " " + text)
        
        # 2. ジャンルを象徴する言葉を強制追加 (網羅性を極限まで高める)
        forced_kws = []
        if "ゲーム" in group or "勢" in category: 
            forced_kws.extend(["ゲーム", "対戦", "募集", "フレンド", "エンジョイ", "ランク", "アプデ", "攻略", "配信"])
        if "趣味" in group or "一般" in group: 
            # 生活・レジャー
            forced_kws.extend(["趣味", "日常", "呟き", "写真", "カメラ", "散歩", "サウナ", "キャンプ", "温泉", "スパ", "癒し"])
            # プロフェッショナル・クリエイティブ
            forced_kws.extend(["デザイナー", "ui", "ux", "figma", "デザイン", "クリエイティブ", "アート", "スケッチ", "イラスト"])
            forced_kws.extend(["エンジニア", "プログラミング", "it", "web", "開発", "技術", "アーカイブ"])
            forced_kws.extend(["広報", "pr", "マーケ", "仕事", "副業", "収支", "起業", "フリーランス", "ランサー"])
            # 音楽・サブカル
            forced_kws.extend(["ギター", "バンド", "ライブ", "歌ってみた", "音楽", "弾き語り", "ロック", "ベース", "ドラム"])
            forced_kws.extend(["アニメ", "漫画", "マンガ", "映画", "ドラマ", "推し", "同担"])
            # 美容・ライフスタイル
            forced_kws.extend(["料理", "自炊", "レシピ", "グルメ", "スイーツ", "カフェ", "ランチ"])
            forced_kws.extend(["美容", "コスメ", "メイク", "スキンケア", "ダイエット", "筋トレ", "ヨガ"])

        unique_kws = list(set([kw for kw in keywords if len(kw) >= 1] + forced_kws))
        
        # 3. 特定ジャンルの具体的・専門用語補強
        if "ポケモン" in category: unique_kws.extend(["厳選", "色違い", "ランクマ", "レイド", "ポケカ"])
        if "フォートナイト" in category: unique_kws.extend(["フォトナ", "ビクロイ", "建築", "アリーナ"])
        
        matrix[category] = [str(k).lower() for k in unique_kws]

    # 250人格分をすべて書き出し
    with open('data/keyword_matrix.json', 'w', encoding='utf-8') as f:
        json.dump(matrix, f, ensure_ascii=False, indent=4)
    
    print(f"Complete Matrix for {len(matrix)} personas built successfully.")

if __name__ == "__main__":
    build_complete_persona_matrix()
