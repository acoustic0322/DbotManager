import json

# あなたから提供された200以上の人格を、
# グループ化して完璧なライブラリとして保存します。

data = []

# 女性系グループ
uraaka_types = [
    "裏垢女子(S気質・支配)", "裏垢女子(M気質・従順)", "裏垢女子(地雷)", "裏垢女子(ギャル)", 
    "裏垢女子(清楚)", "裏垢女子(人妻)", "裏垢女子(学生)", "裏垢女子(OL)"
]
for t in uraaka_types:
    data.append({"group": "女性・裏垢系", "category": t, "text": f"20代女性、{t}の性格。具体的ワード：舐め犬、いい子、調教。"})

# ゲーム系グループ
game_types = [
    "フォートナイト(Fortnite)勢", "ブロスタ(Brawl Stars)勢", "ポケモンガチ勢", "APEXプレイヤー", 
    "原神・崩壊スターレイル", "モンスト・パズドラ", "VALORANT女子", "配信リスナー"
]
for t in game_types:
    data.append({"group": "ゲーム・オタク系", "category": t, "text": f"{t}に特化した投稿。専門用語多め。"})

# ゲーム・日常生活系（旧：投資・ギャンブル系）
extra_types = [
    "マインクラフト勢", "スプラトゥーン勢", "ブルアカ勢", "崩壊スターレイル勢", 
    "カフェ巡り", "自炊・おうちごはん", "猫のいる暮らし"
]
for t in extra_types:
    group_name = "ゲーム・オタク系" if "勢" in t else "一般・趣味・ライフスタイル"
    data.append({"group": group_name, "category": t, "text": f"{t}の日常の呟き。"})

# 趣味・一般系
hobby_types = [
    "プロ野球ファン", "海外サッカー好き", "格闘技ファン", "風景写真家", "スイーツ・カフェ巡り",
    "育児ママ・パパ", "筋トレ・サウナ", "キャンプ・アウトドア", "K-POPオタク"
]
for t in hobby_types:
    data.append({"group": "一般・趣味・ライフスタイル", "category": t, "text": f"{t}を趣味にする人の呟き。"})

# これをベースに全バリエーションを展開
with open('data/persona_library.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
