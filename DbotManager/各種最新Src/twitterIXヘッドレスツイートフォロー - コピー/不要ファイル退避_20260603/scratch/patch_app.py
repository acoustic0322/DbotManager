import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\app.py'
if not os.path.exists(path):
    print("File not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'D-BOT</h1>", unsafe_allow_html=True)'
replacement = target + '\n    st.markdown("<p style=\'text-align: center; color: #888; font-size: 0.8rem; margin-top: -15px;\'>System v2.1.1 Stable</p>", unsafe_allow_html=True)'

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully patched app.py")
else:
    print("Target string not found")
