# -*- coding: utf-8 -*-
"""
login_no_proxy.py (完全版: 統合済み)
- 使用:
    python login_no_proxy.py --profiles profiles.txt
    python login_no_proxy.py --profile "C:\path\to\profile"
- 機能:
  1) profiles.txt の最初の有効プロファイルを使って Firefox を起動
  2) https://x.com/explore を開く（ログインはプロファイルの状態に依存）
  3) 指定基点 div の following から class に 'css-1jxf684' を含む span を上から列挙
  4) 列挙した list のうち 1始まりで [2,5,8,11,14,17,20,23,26,29,32] 番目の要素だけ抽出
  5) 抽出した要素の先頭3件のみを output.txt に上書き保存（スクリプトと同じフォルダ）
  6) ログは stdout に出力（bat と併用しやすい）
"""
import sys
import argparse
import time
import os
from pathlib import Path
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from mysql import insert_trend
from mysql import delete_trend

# ---------------------------
# 設定（必要ならここを変える）
# ---------------------------
BASE_DIV_SELECTOR = 'div.css-175oi2r.r-l00any.r-109y4c4.r-1sw30gj'
SPAN_CLASS_SUBSTR = 'css-1jxf684'   # 取得対象 span に含まれるクラスの一部
INDEX_LIST_1BASED = [2,5,8,11,14,17,20,23,26,29,32]  # 1始まりのインデックス群
OUTPUT_FILENAME_DEFAULT = "output.txt"
WAIT_BODY_TIMEOUT = 25
WAIT_FOR_SPANS_SEC = 6   # 最初のページ安定待ち（動的ロードに応じて増やす）
MAX_WAIT_FOR_ENOUGH_SPANS = 12  # 待機ループ回数（WAIT_FOR_SPANS_SEC 秒ずつ）
# ---------------------------

def read_profiles_file(path: Path) -> List[str]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = []
    for line in text.splitlines():
        s = line.strip().strip('"').replace("\u3000", " ")
        if not s or s.startswith("#") or s.lower().startswith("rem "):
            continue
        if "," in s:
            s = s.split(",", 1)[0].strip().strip('"')
        if s:
            lines.append(s)
    return lines

def find_first_existing_profile_from_list(profiles_path: Path, explicit_profile: Optional[Path]) -> Optional[Path]:
    if explicit_profile:
        if explicit_profile.exists():
            return explicit_profile
        return None
    if not profiles_path.exists():
        return None
    for line in read_profiles_file(profiles_path):
        cand = Path(line)
        if cand.exists():
            return cand
    return None

def open_firefox_with_profile(profile_path: Path, headless: bool=False):
    opts = FirefoxOptions()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("-profile")
    opts.add_argument(str(profile_path))
    opts.add_argument("-no-remote")
    opts.add_argument("-new-instance")
    service = FirefoxService()  # assumes geckodriver is in PATH
    driver = webdriver.Firefox(service=service, options=opts)
    return driver

def wait_for_body(driver, timeout=WAIT_BODY_TIMEOUT):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

def collect_target_spans_after_div(driver, base_div_selector: str, span_class_substr: str) -> List[str]:
    """
    base_div_selector の要素を見つけ、その following:: にある span 要素のうち
    class 属性に span_class_substr を含むものを上から順に列挙してテキストを返す。
    空テキストは無視する。
    """
    texts = []
    try:
        base = driver.find_element(By.CSS_SELECTOR, base_div_selector)
    except Exception as e:
        print(f"[ERR] base div not found by selector '{base_div_selector}': {e}", file=sys.stderr)
        return texts

    # following::span[contains(@class, '...')]
    xpath = f"following::span[contains(@class, '{span_class_substr}')]"
    try:
        elems = base.find_elements(By.XPATH, xpath)
    except Exception as e:
        print("[ERR] find_elements XPath failed:", e, file=sys.stderr)
        return texts

    for el in elems:
        try:
            t = (el.text or "").strip()
        except Exception:
            t = ""
        if t:
            texts.append(t)
    return texts

def select_by_indices(texts: List[str], indices_1based: List[int]) -> List[str]:
    selected = []
    n = len(texts)
    for idx in indices_1based:
        if idx <= 0:
            continue
        zero_idx = idx - 1
        if zero_idx < n:
            selected.append(texts[zero_idx])
        else:
            # 存在しないインデックスは無視
            pass
    return selected

def write_output_file(script_dir: Path, filename: str, words: List[str]) -> None:
    outpath = script_dir / filename
    # ensure directory exists (script_dir should exist)
    try:
        with outpath.open("w", encoding="utf-8") as f:
            for w in words:
                f.write(w + "\n")
        print(f"[OK] Wrote {len(words)} lines to {outpath}")
    except Exception as e:
        print(f"[ERR] Failed to write output file: {e}", file=sys.stderr)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", help="profiles.txt path (use first valid line)")
    ap.add_argument("--profile", help="explicit profile folder path")
    ap.add_argument("--output", help="output filename (default output.txt)", default=OUTPUT_FILENAME_DEFAULT)
    ap.add_argument("--headless", help="run headless", action="store_true")
    args = ap.parse_args()

    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    profiles_arg = Path(args.profiles) if args.profiles else None
    explicit_profile = Path(args.profile) if args.profile else None

    if not profiles_arg and not explicit_profile:
        print("[ERR] --profiles or --profile required", file=sys.stderr)
        sys.exit(2)

    if profiles_arg and not profiles_arg.exists():
        print(f"[ERR] profiles file not found: {profiles_arg}", file=sys.stderr)
        sys.exit(2)

    profile_path = find_first_existing_profile_from_list(profiles_arg if profiles_arg else Path(""), explicit_profile)
    if not profile_path:
        print("[ERR] No valid Firefox profile found", file=sys.stderr)
        sys.exit(3)

    print(f"[INFO] Launching Firefox with profile: {profile_path}")

    try:
        driver = open_firefox_with_profile(profile_path, headless=args.headless)
    except WebDriverException as e:
        print(f"[ERR] Failed to launch Firefox: {e}", file=sys.stderr)
        sys.exit(4)

    try:
        try:
            driver.get("https://x.com/explore")
        except Exception as e:
            print(f"[WARN] driver.get failed: {e}")

        try:
            wait_for_body(driver, timeout=WAIT_BODY_TIMEOUT)
        except TimeoutException:
            print("[WARN] Wait for body timed out, continuing...")

        print("[OK] Moved to https://x.com/explore")
        # 初期待ち（動的ロード対策）
        time.sleep(WAIT_FOR_SPANS_SEC)

        # ループで待って、少なくとも一つは span が見つかる or タイムアウト
        attempts = 0
        gathered = []
        while attempts < MAX_WAIT_FOR_ENOUGH_SPANS:
            gathered = collect_target_spans_after_div(driver, BASE_DIV_SELECTOR, SPAN_CLASS_SUBSTR)
            if gathered:
                # got at least one; but we may want more - break for now
                break
            attempts += 1
            print(f"[STEP] no spans found yet, wait {WAIT_FOR_SPANS_SEC}s (attempt {attempts}/{MAX_WAIT_FOR_ENOUGH_SPANS})")
            time.sleep(WAIT_FOR_SPANS_SEC)

        if not gathered:
            print("[ERR] No candidate spans found after waiting.", file=sys.stderr)
            driver.quit()
            sys.exit(5)

        print(f"[STEP] Collected {len(gathered)} span texts (sample): {gathered[:6]}")

        # 指定インデックス群で選択（1始まり）
        selected = select_by_indices(gathered, INDEX_LIST_1BASED)
        print(f"[STEP] Selected {len(selected)} items from the index list (before trim): {selected}")

        delete_trend("test_profile")

        # selected の各要素を処理（rankを1から順に付与）
        for rank, item in enumerate(selected, start=1):
            insert_trend("test_profile", rank, "trend", item, 0)

        # その中の先頭3件だけを最終ワードにする
        final = selected[:3]

        print(f"final : {final}")

        if not final:
            print("[WARN] No items selected after index filtering.")
            driver.quit()
            sys.exit(6)

        # ファイルへ書き込み（スクリプトフォルダに確実に保存）
        write_output_file(script_dir, args.output, final)

        driver.quit()
        sys.exit(0)

    except Exception as e:
        print(f"[ERR] unexpected exception: {e}", file=sys.stderr)
        try:
            driver.quit()
        except Exception:
            pass
        sys.exit(7)

if __name__ == "__main__":
    main()
