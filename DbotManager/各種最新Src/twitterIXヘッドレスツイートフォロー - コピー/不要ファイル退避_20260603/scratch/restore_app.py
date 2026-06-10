import shutil
import os

src = r"h:\マイドライブ\twitterIXヘッドレスツイートフォロー - コピー (2)\app.py"
dst = r"app.py"

if os.path.exists(src):
    shutil.copy2(src, dst)
    print("Restore successful!")
else:
    print(f"Source path does not exist: {src}")
