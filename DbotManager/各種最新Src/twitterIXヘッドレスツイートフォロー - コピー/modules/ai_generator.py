import os
import json
import random
import time
import requests
import google.generativeai as genai
from loguru import logger
import re

class AIGenerator:
    def __init__(self, api_keys=None, openai_keys=None):
        # APIキーの読み込み（Gemini優先）
        self.api_keys = []
        if isinstance(api_keys, list):
            self.api_keys = [k.strip() for k in api_keys if k.strip()]
        
        self.openai_keys = []
        if isinstance(openai_keys, list):
            self.openai_keys = [k.strip() for k in openai_keys if k.strip()]
        
        # もしコンストラクタで渡されなかった場合、config.jsonからGeminiキーを読み込む
        if not self.api_keys:
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(base_dir, 'config.json')
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if not self.api_keys:
                        self.api_keys = config.get("GEMINI_API_KEYS", [])
                    if not self.openai_keys:
                        ok = config.get("OPENAI_API_KEY")
                        if ok: self.openai_keys = [ok] if isinstance(ok, str) else ok
            except:
                pass

        self.current_key_idx = 0
        self.model_name = "gemini-1.5-flash-latest" # 高速・軽量モデル
        logger.info(f"AIGenerator initialized with {len(self.api_keys)} Gemini keys and {len(self.openai_keys)} OpenAI keys.")

    def _safe_generate(self, prompt, retries=None):
        # [REMOVED] Gemini is disabled per user request
        
        # 1. Try ChatGPT (Now Primary)
        logger.info("Triggering AI Generation (OpenAI)...")
        try:
            # Use provided openai_keys if available
            key_to_use = random.choice(self.openai_keys) if self.openai_keys else None
            if not key_to_use:
                # Last resort: env var
                key_to_use = os.getenv("OPENAI_API_KEY")
            
            if not key_to_use:
                raise Exception("No OpenAI API key found.")
            
            base_url = "https://api.openai.com/v1"
            model = "gpt-4o-mini"
            
            headers = {
                "Authorization": f"Bearer {key_to_use}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9
            }
            response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                res_json = response.json()
                content = res_json['choices'][0]['message']['content']
                if content:
                    return content.strip()
            else:
                logger.warning(f"ChatGPT API Error: {response.status_code} - {response.text}")
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            err_msg = str(e).lower()
            logger.warning(f"ChatGPT failed: {err_msg}")
            # If the error is due to restriction or quota, we might want to disable OpenAI temporarily
            if "insufficient_quota" in err_msg or "restricted" in err_msg or "organization" in err_msg:
                logger.error("OpenAI account is restricted or out of quota. Switching to free fallbacks.")

        # 3. Try Free AI (Pollinations.ai) - No Key Required
        logger.info("Triggering Free AI Fallback (Pollinations)...")
        try:
            from requests.utils import quote
            seed = random.randint(1, 100000)
            url = f"https://text.pollinations.ai/{quote(prompt)}?seed={seed}&model=openai"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                text = resp.text.strip()
                if text:
                    logger.success("Free AI successfully generated text.")
                    return text
        except Exception as e:
            logger.error(f"Free AI Fallback failed: {e}")

        return None

    def _save_to_history(self, category, text):
        """成功したツイートをカテゴリー別に保存する"""
        try:
            history_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tweet_history')
            os.makedirs(history_dir, exist_ok=True)
            
            # カテゴリー名をファイル名に安全な形式に変換
            safe_cat = re.sub(r'[\\/*?:"<>|]', '_', category)
            file_path = os.path.join(history_dir, f"{safe_cat}.txt")
            
            # 重複チェックをしてから追記
            existing_tweets = set()
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        t = line.strip()
                        if t: existing_tweets.add(t)
            
            if text not in existing_tweets:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(text + "\n")
        except Exception as e:
            logger.warning(f"Failed to save tweet to history: {e}")

    def _load_from_history(self, category):
        """過去に成功したツイートからランダムに取得する"""
        try:
            history_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tweet_history')
            safe_cat = re.sub(r'[\\/*?:"<>|]', '_', category)
            file_path = os.path.join(history_dir, f"{safe_cat}.txt")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    tweets = [line.strip() for line in f if line.strip()]
                if tweets:
                    return random.choice(tweets)
        except Exception as e:
            logger.warning(f"Failed to load from history: {e}")
        return None

    def determine_theme(self, account_name="", bio=""):
        """アカウント名と自己紹介からテーマを判定する"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        matrix_path = os.path.join(base_dir, 'data', 'keyword_matrix.json')
        
        if os.path.exists(matrix_path):
            try:
                with open(matrix_path, 'r', encoding='utf-8') as f:
                    persona_shields = json.load(f)
            except:
                persona_shields = {}
        else:
            persona_shields = {}

        combined = f"{str(account_name or '').lower()} {str(bio or '').lower()}"
        
        # 裏垢・女子系は除外
        persona_shields = {k: v for k, v in persona_shields.items() if "裏垢" not in k and "女子" not in k}
        
        matches = []
        for cat, kws in persona_shields.items():
            score = sum(1 for kw in kws if str(kw).lower() in combined)
            if score > 0:
                matches.append({"category": cat, "score": score})

        if matches:
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches[0]['category']
        
        return "日常生活"

    def generate_tweet_text(self, username="", category="日常生活"):
        # カテゴリ名からType-○などを除去
        clean_category = re.sub(r'\s*Type-\d+', '', category).strip()
        clean_category = re.sub(r'\s*タイプ-\d+', '', clean_category).strip()
        
        # 1. 多様なシチュエーション（きっかけ）
        situations = [
            "最近の気づき・学んだこと",
            "今日嬉しかった小さな出来事",
            "ふと頭に浮かんだ疑問やアイデア",
            "最近特にハマっていること・熱中していること",
            "ちょっとした失敗やクスッと笑えるやらかし話",
            "日々のささやかな幸せ・癒やしの瞬間",
            "今考えているリアルな悩みや感想",
            "朝/昼/夜の日常ルーティンの中での一コマ",
            "週末や休日のリアルな過ごし方や過ごしたい妄想",
            "過去の自分と今の自分の比較や成長実感",
            "これだけは譲れないというマニアックなこだわり",
            "ふと昔を思い出してノスタルジックになったこと",
            "最近買って本当によかったお気に入りアイテムの紹介",
            "周りの人やネットで見かけた面白い会話・出来事",
            "モチベーションが上がった瞬間",
            "季節の移り変わりや今日の天気・気温について感じたこと"
        ]
        
        # 2. 多様な切り口（アングル）
        angles = [
            "具体的な数字や時間、回数などを入れてリアルさを演出して",
            "まだまだ勉強中の初心者目線で等身大に",
            "少しだけドヤ顔で（ちょっと得意げに）知識や経験をアピールして",
            "新鮮な驚きや感動をそのまま伝えるように",
            "ユーモアや自虐を交えて、クスッと笑えるように",
            "読者に「これってあるある？」と共感を誘うような問いかけ風に",
            "自分自身にセルフツッコミを入れる形でコメディカルに",
            "少しだけ深掘りして、哲学的なアプローチで",
            "あえて語数を削り、極めてシンプルかつエモい一言で",
            "オタク特有の熱量を感じさせるような語り口で",
            "しみじみと余韻に浸り、感謝するようなトーンで",
            "「なぜなんだろう？」と素直な疑問を投げかける形で",
            "日常生活で今すぐ役立つような、ちょっとしたコツやライフハックとして",
            "「これから〜するぞ！」と直近の目標を楽しく宣言する形で",
            "ネガティブにならない程度の、愛嬌のある「ゆるい本音」を吐露して"
        ]
        
        # 3. 文体や口調のバリエーション
        tones = [
            "「〜だなぁ」「〜かも」「〜だ」といった、飾り気のないラフなタメ口・独り言風で",
            "「〜です」「〜ます」「〜ですね」といった、丁寧で人当たりの良い親しみやすい口調で",
            "体言止め（〜の瞬間。〜の秋。など）や、極めて短い言葉をテンポよく繋げたスッキリした文体で",
            "「〜じゃん？」「〜だし」「〜なんだよね」といった、親しい友人に話しかけるようなくだけた話し言葉で",
            "「〜したい…」「〜しよう！」といった、未来の行動に対する前向きな希望や決意を込めた口調で",
            "「〜かな？」「〜どう思う？」といった、ゆるくフォロワーに語りかけるような距離感で"
        ]
        
        # 4. カテゴリーと組み合わせる「日常のサブテーマ」（これによってツイートの内容が毎回全く異なるものになる）
        sub_themes = [
            "コーヒーやお茶、お気に入りの飲み物の話",
            "睡眠不足、二度寝、あるいはすっきり目覚めた睡眠の話",
            "今日の天気や気温、雨の日の過ごし方の話",
            "お腹が空いたこと、今日食べた美味しいご飯やオヤツの話",
            "やることが多くて忙しい、あるいはやることがなくて暇な時間の話",
            "週末の予定や、どこかに行きたいというお出かけ欲の話",
            "デスク周りや部屋の片付け、模様替えの話",
            "ネットショッピングでの物欲や、カートに入れたまま悩んでいる話",
            "軽い運動、ストレッチ、散歩、あるいは健康・肩こりの話",
            "作業用BGM、最近リピートしている音楽やポッドキャストの話",
            "スマホやガジェットの便利機能、またはデジタルデトックスの話",
            "コンビニで見つけた新作スイーツや、自分へのちょっとしたご褒美の話"
        ]
        
        situation = random.choice(situations)
        angle = random.choice(angles)
        tone = random.choice(tones)
        sub_theme = random.choice(sub_themes)
        
        # 40%の確率で、サブテーマを絡めてツイートに日常のスパイスを加える
        use_sub_theme = random.random() < 0.4
        
        if use_sub_theme:
            theme_instruction = f"【{clean_category}】の話題をベースにしつつ、日常のスパイスとして【{sub_theme}】の要素も自然に絡めてください。"
        else:
            theme_instruction = f"【{clean_category}】に関するリアルな日常のつぶやきにしてください。"

        prompt = f"""
        あなたは【{clean_category}】が趣味の、実在する日本人Twitterユーザー（一般人アカウント）です。
        以下の設定と制約に厳密に従い、思わずタイムラインをスクロールする手が止まるような、人間味に溢れた自然な日本語のツイート（100文字以内）を「1つだけ」作成してください。

        【今回のツイートの設定】
        - 主なテーマ：{theme_instruction}
        - 出来事・きっかけ：{situation}
        - 切り口・視点：{angle}
        - 文体・口調：{tone}

        【厳格な制約（必ず守ってください）】
        1. 「ハッシュタグ（#）」の記述は一切禁止です。
        2. 「絵文字」は0個〜最大2個までに抑えてください。絵文字を並べすぎるとAI感が出るため、極力控えめにし、全く使わなくても構いません。
        3. 「こんにちは！」「皆さんこんにちは」といった定型的な挨拶や、AIが生成しがちな不自然な呼びかけは絶対に書かないでください。
        4. 「〜を頑張りましょう！」「〜ですね！」「〜だな」といった同じ語尾や言い回しのツイートばかりを量産するのを防ぐため、今回の口調指定（{tone}）に沿って、独創的で自然な語尾にしてください。
        5. 英語やアルファベットの乱用は避け、日本人が普段使う日常的な言葉（カタカナ含む）を使用してください。
        6. 株、FX、仮想通貨などの投資関連の話題（カテゴリーが投資の場合）においては、具体的な『銘柄価格（〇〇円など）』『為替レート数値』『日経平均株価などの指数数値』は絶対に含めないでください。情報の鮮度が落ちるのを防ぐため、抽象的な値動きへの感情や感想のみを記述してください。
        7. 宣伝や営業活動のようにはせず、あくまで一個人の趣味のつぶやき・独り言に徹底してください。

        ツイート本文のみを出力してください。余計な説明や装飾、カギカッコ等は一切不要です。
        """
        result = self._safe_generate(prompt)
        
        if result:
            final_text = result.replace('"', '').replace('「', '').replace('」', '')
            self._save_to_history(clean_category, final_text)
            return final_text
        else:
            # AI失敗時は履歴から
            history_tweet = self._load_from_history(clean_category)
            if history_tweet:
                logger.success(f"Loaded tweet from history for {clean_category}.")
                return history_tweet

            # 履歴もなければテンプレート
            templates = {
                "ゲーム": ["最近このゲームにハマってる！", "今日の戦績はなかなか良かった", "レベル上げ頑張るぞ！"],
                "料理": ["今日のご飯、美味しくできた！", "隠し味を入れたら最高になった", "料理って奥が深いね"],
                "投資": ["今日もお疲れ様でした！", "天気が良くて気分がいいね", "明日もいい日になりますように"],
                "日常生活": ["今日もお疲れ様でした！", "天気が良くて気分がいいね", "明日もいい日になりますように"]
            }
            
            texts = templates.get("日常生活")
            for k in templates:
                if k in clean_category:
                    texts = templates[k]
                    break
            return random.choice(texts)

    def generate_image(self, tweet_text, prefix="gen"):
        """Pollinationsを使用して画像を生成する"""
        prompt_trans = f"Convert this tweet to a high-quality photo prompt: {tweet_text}. Style: smartphone photo, Japanese lifestyle."
        image_prompt = self._safe_generate(prompt_trans)
        if not image_prompt: image_prompt = "A peaceful Japanese daily life scene, photo"

        try:
            from requests.utils import quote
            image_url = f"https://image.pollinations.ai/prompt/{quote(image_prompt)}?width=1024&height=1024&seed={random.randint(1,9999)}&nologo=true&model=flux"
            response = requests.get(image_url, timeout=60)
            if response.status_code == 200:
                os.makedirs('data/generated_images', exist_ok=True)
                file_path = f"data/generated_images/{prefix}_{int(time.time())}.jpg"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logger.success(f"Generated AI Image: {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
        return None
