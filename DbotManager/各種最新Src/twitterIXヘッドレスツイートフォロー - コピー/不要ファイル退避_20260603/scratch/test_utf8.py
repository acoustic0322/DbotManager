try:
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    print("app.py successfully read as UTF-8!")
    print(f"Content length: {len(content)}")
except Exception as e:
    print(f"UTF-8 read failed: {e}")
