# get_x_cookies.py  (Python 3.8 compatible)
import os
import json
import base64
import shutil
import sqlite3
import tempfile
from typing import Optional, Tuple, Dict, List

import win32crypt
from Cryptodome.Cipher import AES

import glob


import os, json, base64, win32crypt
from typing import Optional


def _user_data_dir_from_cookie_path(cookie_path: str) -> Optional[str]:
    p = os.path.abspath(cookie_path)
    for _ in range(6):
        p = os.path.dirname(p)
        if os.path.basename(p).lower() == "user data":
            return p
    return None

def _load_key_from_local_state(ls_path: str) -> Optional[bytes]:
    try:
        with open(ls_path, "r", encoding="utf-8") as f:
            st = json.load(f)
        ek = base64.b64decode(st["os_crypt"]["encrypted_key"])
        if ek.startswith(b"DPAPI"):
            ek = ek[5:]
        return win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]
    except Exception:
        return None

def find_working_key_for_db(cookie_db_tmp: str, user_data_dir: str) -> Optional[bytes]:
    # 暗号化cookie1件で鍵検証
    conn = sqlite3.connect(cookie_db_tmp)
    cur = conn.cursor()
    cur.execute("""SELECT encrypted_value FROM cookies
                   WHERE length(encrypted_value)>3
                   ORDER BY last_access_utc DESC LIMIT 1""")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    sample = bytes(row[0])

    # 新しい順に Local State* を試す
    candidates = sorted(
        glob.glob(os.path.join(user_data_dir, "Local State*")),
        key=lambda p: os.path.getmtime(p),
        reverse=True,
    )
    for ls in candidates:
        key = _load_key_from_local_state(ls)
        if not key:
            continue
        try:
            if sample.startswith((b"v10", b"v11", b"v20")):
                nonce, payload = sample[3:15], sample[15:]
                ct, tag = payload[:-16], payload[-16:]
                AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
            else:
                win32crypt.CryptUnprotectData(sample, None, None, None, 0)
            # ここに来たらこの鍵が当たり
            # print("[KEY OK]", ls)
            return key
        except Exception:
            continue
    return None

def _user_data_dir_from_cookie_path(cookie_path: str) -> Optional[str]:
    p = os.path.abspath(cookie_path)
    # 上に最大6段上がって "User Data" を探す（階層ズレに強い）
    for _ in range(6):
        p = os.path.dirname(p)
        if os.path.basename(p).lower() == "user data":
            return p
    return None

def get_browser_key_from_cookie_path(cookie_path: str) -> Optional[bytes]:
    ud = _user_data_dir_from_cookie_path(cookie_path)
    print("[user_data_dir]", ud)  # 一時デバッグ
    if not ud:
        return None
    ls = os.path.join(ud, "Local State")
    print("[local_state]", ls)    # 一時デバッグ
    try:
        with open(ls, "r", encoding="utf-8") as f:
            state = json.load(f)
        ek = base64.b64decode(state["os_crypt"]["encrypted_key"])
        if ek.startswith(b"DPAPI"):
            ek = ek[5:]
        key = win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]
        return key
    except Exception as e:
        print("[get_browser_key_from_cookie_path][ERROR]", e)
        return None

# --- 先頭の import 群に追加 ---
import glob
from typing import Optional
from Cryptodome.Cipher import AES
import win32crypt, json, base64, os, sqlite3

def iter_local_state_candidates(user_data_dir: str):
    import glob, os
    pats = ["Local State", "Local State*", "Local*State*"]
    for pat in pats:
        for p in glob.glob(os.path.join(user_data_dir, pat)):
            if os.path.isfile(p):
                print("[LS candidate]", p)
                yield p  # ← ここはyieldのままでOK（上でnextで1件だけ取り出す）

def load_key_from_local_state(ls_path: str) -> Optional[bytes]:
    import json, base64, win32crypt, traceback
    try:
        print("[LS path]", ls_path)
        with open(ls_path, "r", encoding="utf-8") as f:
            st = json.load(f)
        ek_b64 = st.get("os_crypt", {}).get("encrypted_key")
        if not ek_b64:
            print("[LS] encrypted_key が見つかりません")
            return None
        ek = base64.b64decode(ek_b64)
        print("[LS] has DPAPI prefix?", ek.startswith(b"DPAPI"))
        if ek.startswith(b"DPAPI"):
            ek = ek[5:]
        key = win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]
        print("[LS] master_key_len:", len(key))
        return key
    except Exception as e:
        print("[load_key_from_local_state][ERROR]", type(e).__name__, str(e))
        traceback.print_exc()
        return None

def get_correct_key_for_db(cookie_db_tmp: str, user_data_dir: str) -> Optional[bytes]:
    # DBから暗号化Cookieを1件取って鍵検証
    conn = sqlite3.connect(cookie_db_tmp)
    cur = conn.cursor()
    cur.execute("""SELECT encrypted_value FROM cookies
                   WHERE length(encrypted_value)>3
                   ORDER BY last_access_utc DESC LIMIT 1""")
    row = cur.fetchone()
    conn.close()
    if not row:
        print("[probe] 暗号化CookieがDBにありません")
        return None
    sample = bytes(row[0])

#    ls = iter_local_state_candidates(user_data_dir)
    ls = next(iter_local_state_candidates(user_data_dir), None)
    if not ls:
        print("[probe] Local State が見つかりません")
        return None

    key = load_key_from_local_state(ls)
    if not key:
        print("[probe] Local State から鍵を復号できません")
        return None

    try:
        if sample.startswith((b"v10", b"v11", b"v20")):
            nonce, payload = sample[3:15], sample[15:]
            ct, tag = payload[:-16], payload[-16:]
            AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
        else:
            win32crypt.CryptUnprotectData(sample, None, None, None, 0)
        print("[KEY OK]", ls, "len=", len(key))
        return key
    except Exception as e:
        print("[KEY NG]", ls, type(e).__name__, str(e))
        return None


def iter_local_state_candidates(user_data_dir: str):
    import glob, os
    pats = ["Local State", "Local State*", "Local*State*"]
    seen = set()
    for pat in pats:
        for p in glob.glob(os.path.join(user_data_dir, pat)):
            if os.path.isfile(p) and p not in seen:
                seen.add(p)
                print("[LS candidate]", p)
                yield p

def try_keys_until_ok(cookie_db_tmp: str, user_data_dir: str) -> Optional[bytes]:
    import json, base64, sqlite3, win32crypt
    from Cryptodome.Cipher import AES

    conn = sqlite3.connect(cookie_db_tmp)
    cur = conn.cursor()
    cur.execute("""SELECT encrypted_value FROM cookies
                   WHERE length(encrypted_value)>3
                   ORDER BY last_access_utc DESC LIMIT 1""")
    row = cur.fetchone()
    conn.close()
    if not row:
        print("[probe] no encrypted cookies in DB")
        return None
    sample = bytes(row[0])

    for ls in iter_local_state_candidates(user_data_dir):
        try:
            st = json.load(open(ls, "r", encoding="utf-8"))
            ek = base64.b64decode(st["os_crypt"]["encrypted_key"])
            if ek.startswith(b"DPAPI"): ek = ek[5:]
            key = win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]

            if sample.startswith((b"v10", b"v11", b"v20")):
                nonce, payload = sample[3:15], sample[15:]
                ct, tag = payload[:-16], payload[-16:]
                AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
            else:
                win32crypt.CryptUnprotectData(sample, None, None, None, 0)

            print("[KEY OK]", ls, f"len={len(key)}")
            return key
        except Exception as e:
            print("[KEY NG] ", ls, type(e).__name__)
            continue
    return None

# ===== ブラウザとプロファイル =====
def _browser_base(browser: str) -> str:
    if browser == "chrome":
        return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data")
    elif browser == "edge":
        return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data")
    raise ValueError("unknown browser: " + browser)

def _cookies_db_path(browser: str, profile_folder: str) -> str:
    return os.path.join(_browser_base(browser), profile_folder, "Network", "Cookies")

def get_browser_key(browser: str = "chrome") -> bytes:
    local_state_path = os.path.join(_browser_base(browser), "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encrypted_key_b64)[5:]  # remove "DPAPI" prefix
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

import base64, json, os
from Cryptodome.Cipher import AES
import win32crypt

import os
import sqlite3
from Cryptodome.Cipher import AES
import win32crypt, base64, json

# --- ここを置き換え ---

def _local_state_from_cookie_path(cookie_path: str) -> Optional[str]:
    import os
    p = os.path.abspath(cookie_path)
    # 親を最大5階層まで遡って "Local State" を探す
    for _ in range(5):
        p = os.path.dirname(p)
        candidate = os.path.join(p, "Local State")
        if os.path.isfile(candidate):
            return candidate
    return None

def quick_probe_any_cookie(db_path, key, limit=5):
    import sqlite3
    ok, ng = [], []
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT host_key, name, encrypted_value, value
        FROM cookies
        WHERE length(encrypted_value) > 3
        ORDER BY last_access_utc DESC
        LIMIT ?
    """, (limit,))
    for host, name, enc, plain in cur.fetchall():
        val = None
        if enc:
            val = decrypt_cookie(enc, key, debug=True)
        if val is None and plain:
            val = plain
        (ok if val else ng).append((host, name))
    conn.close()
    return ok, ng

def get_browser_key_from_cookie_path(cookie_path: str) -> Optional[bytes]:
    print("cookie_path=", cookie_path)
    local_state_path = _local_state_from_cookie_path(cookie_path)
    print("local_state_path=", local_state_path)  # デバッグ出力を一時追加
    if not local_state_path:
        return None
    with open(local_state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    ek = base64.b64decode(state["os_crypt"]["encrypted_key"])
    if ek.startswith(b"DPAPI"):
        ek = ek[5:]
    return win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]

def get_chromium_master_key(local_state_path):
    with open(local_state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    ek = base64.b64decode(state["os_crypt"]["encrypted_key"])
    if ek.startswith(b"DPAPI"):
        ek = ek[5:]
    return win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]

def decrypt_cookie(encrypted_value, master_key, *, debug=False):
    try:
        if encrypted_value is None:
            return None
        if isinstance(encrypted_value, memoryview):
            encrypted_value = encrypted_value.tobytes()
        if not isinstance(encrypted_value, (bytes, bytearray)):
            if debug: print("[decrypt_cookie] not bytes:", type(encrypted_value))
            return None

        if encrypted_value.startswith((b"v10", b"v11", b"v20")):
            if not master_key:
                if debug: print("[decrypt_cookie] missing master_key")
                return None
            nonce = encrypted_value[3:15]
            payload = encrypted_value[15:]
            if len(payload) < 16:
                if debug: print("[decrypt_cookie] payload too short:", len(payload))
                return None
            ct, tag = payload[:-16], payload[-16:]
            if debug:
                print("[decrypt_cookie] prefix=v20 len(nonce)=", len(nonce),
                      "len(ct)=", len(ct), "len(tag)=", len(tag))
            pt = AES.new(master_key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
            return pt.decode("utf-8", errors="strict")
        else:
            dec = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1]
            return dec.decode("utf-8", errors="strict")
    except Exception as e:
        if debug:
            print("[decrypt_cookie] ERROR:", type(e).__name__, str(e))
        return None


# ===== Chromeの Local State からプロファイル一覧を返す（任意利用） =====
def get_chrome_profiles(target_folders: Optional[List[str]] = None,
                        target_names: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """
    戻り値: [(folder, display_name), ...]
    """
    local_state_path = os.path.join(_browser_base("chrome"), "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    profiles: List[Tuple[str, str]] = []
    info_cache = data.get("profile", {}).get("info_cache", {})

    for folder, profile_data in info_cache.items():
        name = profile_data.get("name", folder)

        if target_folders and folder not in target_folders:
            continue
        if target_names and not any(keyword.lower() in name.lower() for keyword in target_names):
            continue

        profiles.append((folder, name))

    return profiles

# ===== 1プロファイルから cookie 取得 =====

def get_x_cookies_from_profile(profile_folder: str):

    # 一時デバッグ: 実在するプロフィール一覧を出す
    import glob, os, time
    ud = r"C:\Users\sound\AppData\Local\Google\Chrome\User Data"
    if os.path.isdir(ud):
        profiles = sorted([p for p in glob.glob(os.path.join(ud, "*")) if os.path.isdir(p)])
        print("[User Data]", ud)
        for p in profiles:
            base = os.path.basename(p)
            if base.lower() in ("default",) or base.startswith("Profile"):
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p)))
                print(f"  - {base:10s}  mtime={t}")
    else:
        print("[WARN] User Data not found:", ud)

    for browser in ("chrome",):  # 今はChromeのみ
        cookie_path = _cookies_db_path(browser, profile_folder)
        if not os.path.exists(cookie_path):
            continue

        tmp = tempfile.NamedTemporaryFile(delete=False); tmp.close()
        try:
            shutil.copy2(cookie_path, tmp.name)
        except PermissionError:
            os.remove(tmp.name)
            return None, None, "[コピー失敗: ブラウザが起動中の可能性]"

        # get_x_cookies_from_profile 内、conn=open する直前で
        _debug_list_x_rows(tmp.name)

        conn = None
        try:

            # --- 鍵の用意（ここを最初に！） ---
            user_data_dir = _user_data_dir_from_cookie_path(cookie_path)
            key = find_working_key_for_db(tmp.name, user_data_dir)   # 総当たり

            if not key:
                # フォールバック：現行 Local State から
                key = get_browser_key_from_cookie_path(cookie_path)

            if not key or len(key) not in (16, 24, 32):
                os.remove(tmp.name)
                return None, None, "[復号失敗]"

            # --- ここからDB処理 ---

#            user_data_dir = _user_data_dir_from_cookie_path(cookie_path)
#            print("user_data_dir=",user_data_dir)
#            if not user_data_dir:
#                return None, None, "[復号失敗]"

#            key = find_working_key_for_db(tmp.name, user_data_dir)
#            print("key=",key)
#            if not key or len(key) not in (16, 24, 32):
#                return None, None, "[復号失敗]"

            # ←← ここがポイント：Cookies のパスから User Data を逆算し、その鍵で検証
#            user_data_dir = os.path.normpath(os.path.join(cookie_path, "..", ".."))
#            key = get_correct_key_for_db(tmp.name, user_data_dir)
#            if not key:
#                return None, None, "[復号失敗]"

#            key = get_browser_key_from_cookie_path(cookie_path)
#            print("get_x_cookies_from_profile key=",key)
#            if not key or len(key) not in (16, 24, 32):
#                return None, None, "[復号失敗]"                

            conn = sqlite3.connect(tmp.name)
            cur = conn.cursor()

            print("[DEBUG] try decrypt just two rows")
            print("[DEBUG] master_key_len =", len(key))   # 16/24/32 のはず

            cur.execute("""
              SELECT host_key, name, encrypted_value, value
              FROM cookies
              WHERE name IN ('auth_token','ct0')
                AND (host_key LIKE '%.x.com' OR host_key LIKE '%x.com')
              ORDER BY creation_utc DESC
              LIMIT 2
            """)
            for host, name, enc, plain in cur.fetchall():   
                v = None
                if enc:
                    v = decrypt_cookie(enc, key, debug=True)  # ここは一回だけ debug=True
                if v is None and plain:
                    v = plain
                print(f"[DEBUG] {name} ->", v)

            cur.execute("""
              SELECT host_key, name, length(encrypted_value), DATETIME(creation_utc/1000000-11644473600,'unixepoch')
              FROM cookies
              WHERE name IN ('auth_token','ct0')
                AND (host_key LIKE '%x.com' OR host_key LIKE '%.x.com'
                  OR host_key LIKE '%twitter.com' OR host_key LIKE '%.twitter.com'
                  OR host_key LIKE '%api.twitter.com' OR host_key LIKE '%.api.twitter.com')
              ORDER BY creation_utc DESC
              LIMIT 20
            """)
            print("[auth/ct0 rows]", cur.fetchall())            

            auth_token = None
            ct0 = None
            host_patterns = [
                "%x.com","%.x.com",
                "%twitter.com","%.twitter.com",
                "%api.twitter.com","%.api.twitter.com",
            ]
            for host_like in host_patterns:
                for name in ("auth_token", "ct0"):
                    cur.execute("""
                        SELECT encrypted_value, value
                        FROM cookies
                        WHERE host_key LIKE ? AND name = ?
                        ORDER BY last_access_utc DESC
                    """, (host_like, name))
                    for enc, plain in cur.fetchall():
                        candidate = None
                        if enc:
                            candidate = decrypt_cookie(enc, key, debug=False)
                        if candidate is None and plain:
                            candidate = plain
                        if candidate:
                            if name == "auth_token" and not auth_token:
                                auth_token = candidate
                            elif name == "ct0" and not ct0:
                                ct0 = candidate
                        if auth_token and ct0:
                            break
                    if auth_token and ct0:
                        break
                if auth_token and ct0:
                    break
        finally:
            try:
                if conn: conn.close()
            except Exception:
                pass
            os.remove(tmp.name)

        if auth_token and ct0:
            return auth_token, ct0, None

    return None, None, "[復号失敗]"

# Cookies DB に auth_token / ct0 が存在するかだけ先に確認
def _debug_list_x_rows(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
      SELECT host_key, name, length(encrypted_value)
      FROM cookies
      WHERE name IN ('auth_token','ct0')
        AND (host_key LIKE '%x.com' OR host_key LIKE '%.x.com'
          OR host_key LIKE '%twitter.com' OR host_key LIKE '%.twitter.com'
          OR host_key LIKE '%api.twitter.com' OR host_key LIKE '%.api.twitter.com')
      ORDER BY last_access_utc DESC
      LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()
    print("[auth/ct0 rows]", rows)
    return rows

import os, sqlite3, shutil, tempfile
from typing import Optional, Tuple, Dict

def get_x_cookies_from_firefox(profile_dir: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Firefox プロファイルの cookies.sqlite から auth_token / ct0 を読む
    戻り値: (auth_token, ct0, error)
    """
    db = os.path.join(profile_dir, "cookies.sqlite")
    if not os.path.exists(db):
        return None, None, f"[not found] {db}"

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        shutil.copy2(db, tmp.name)  # ロック回避
        conn = sqlite3.connect(tmp.name)
        cur = conn.cursor()
        cur.execute("""
            SELECT name, value
            FROM moz_cookies
            WHERE (host LIKE '%x.com' OR host LIKE '%.x.com'
                   OR host LIKE '%twitter.com' OR host LIKE '%.twitter.com')
              AND name IN ('auth_token','ct0')
            ORDER BY lastAccessed DESC
        """)
        auth_token = ct0 = None
        for name, value in cur.fetchall():
            if name == "auth_token" and not auth_token:
                auth_token = value
            elif name == "ct0" and not ct0:
                ct0 = value
            if auth_token and ct0:
                break
        conn.close()
        if auth_token and ct0:
            return auth_token, ct0, None
        return None, None, "[not found: auth_token/ct0]"
    except Exception as e:
        return None, None, f"[error] {e}"
    finally:
        try: os.remove(tmp.name)
        except Exception: pass


# ===== 複数プロファイル用の外向けAPI =====
def get_x_cookies(target_folders: Optional[List[str]] = None,
                  target_names: Optional[List[str]] = None) -> Dict[str, Dict[str, Optional[str]]]:
    """
    指定条件の Firefox プロファイルから X の auth_token / ct0 をまとめて取得。
    戻り値: { "ProfileName": {"display_name": "...", "auth_token": "...", "ct0": "...", "error": None}, ... }
    """
    # Firefox のプロファイル一覧を作る
    if target_folders:
        profiles = [(f, os.path.basename(f)) for f in target_folders]
    else:
        # profiles.ini を読んで Firefox プロファイルのパスを列挙する関数を用意する
        profiles = get_firefox_profiles(target_names=target_names)

    results: Dict[str, Dict[str, Optional[str]]] = {}
    for folder, display_name in profiles:
        try:
            a, c, e = get_x_cookies_from_firefox(folder)
        except Exception as ex:
            a, c, e = None, None, f"予期せぬエラー: {ex}"

        results[display_name] = {
            "display_name": display_name,
            "auth_token": a,
            "ct0": c,
            "error": e
        }

    print("results")
    print(results)
    return results


# ===== 複数プロファイル用の外向けAPI =====
def get_x_cookies_chrome(target_folders: Optional[List[str]] = None,
                  target_names: Optional[List[str]] = None) -> Dict[str, Dict[str, Optional[str]]]:
    """
    指定条件のプロファイルから X の auth_token / ct0 をまとめて取得。
    Chrome Local State から名前解決できるときは display_name を付与。
    戻り値: { "Profile 7": {"display_name": "...", "auth_token": "...", "ct0": "...", "error": None}, ... }
    """
    if target_folders:
        profiles = [(f, f) for f in target_folders]  # Local State が無くても動くように
    else:
        profiles = get_chrome_profiles(target_folders=None, target_names=target_names)

    results: Dict[str, Dict[str, Optional[str]]] = {}
    for folder, display_name in profiles:
        try:
            a, c, e = get_x_cookies_from_profile(folder)
        except Exception as ex:
            a, c, e = None, None, "予期せぬエラー: {}".format(ex)

        results[folder] = {
            "display_name": display_name,
            "auth_token": a,
            "ct0": c,
            "error": e
        }

    print("results")
    print(results)
    return results

# ===== 単体診断 =====
if __name__ == "__main__":
    candidates = ["Default"] + ["Profile {}".format(i) for i in range(1, 20)]
    for folder in candidates:
        a, c, e = get_x_cookies_from_profile(folder)
        if a or c:
            print("[HIT] {} auth_token={} ct0={} err={}".format(folder, bool(a), bool(c), e))
