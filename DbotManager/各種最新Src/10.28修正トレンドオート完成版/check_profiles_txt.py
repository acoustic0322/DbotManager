# -*- coding: utf-8 -*-
"""
check_profiles_txt.py
- profiles.txt の各行を「そのままのバイト」「repr表示」「存在チェック」で可視化する診断ツール
- 文字コード/BOM/ゼロ幅文字/全角スペース/見えない記号の混入をあぶり出します
使い方:
  python check_profiles_txt.py --profiles profiles.txt
"""
import sys, argparse, os, codecs
from pathlib import Path

def read_bytes(p: Path) -> bytes:
    return p.read_bytes()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", default="profiles.txt")
    args = ap.parse_args()

    p = Path(args.profiles)
    if not p.exists():
        print(f"[ERR] not found: {p}")
        sys.exit(2)

    b = read_bytes(p)
    print(f"[INFO] file bytes length = {len(b)}")
    # 代表的エンコーディングでの読み
    for enc in ["utf-8-sig","utf-16","utf-16-le","utf-16-be","cp932","mbcs","latin-1"]:
        try:
            s = b.decode(enc)
            print(f"\n--- decode ok: {enc} ---")
            lines = s.splitlines()
            for i, line in enumerate(lines, 1):
                raw = line
                # 可視化: repr + Unicodeコードポイント列
                codepoints = " ".join(f"U+{ord(ch):04X}" for ch in raw)
                print(f"[{i:02d}] exists={os.path.exists(raw)}")
                print(f" repr: {raw!r}")
                print(f"  cps: {codepoints}")
        except Exception as e:
            print(f"\n--- decode fail: {enc}: {e} ---")

if __name__ == "__main__":
    main()
