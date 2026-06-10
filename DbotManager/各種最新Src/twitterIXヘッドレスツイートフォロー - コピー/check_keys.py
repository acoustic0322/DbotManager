from google import genai
import json

with open('data/settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)

keys = settings.get("GEMINI_API_KEYS", [])

for i, key in enumerate(keys[:3]):  # 最初の3つだけ確認
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents='Hi'
        )
        print(f"[OK] Key {i+1}: {key[:20]}...")
    except Exception as e:
        print(f"[NG] Key {i+1}: {key[:20]}... -> {str(e)}")