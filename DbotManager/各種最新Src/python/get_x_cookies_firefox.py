# -*- coding: utf-8 -*-
from typing import Tuple, Optional, Dict, List
import os, sqlite3, tempfile, shutil, configparser

def get_firefox_profiles(target_names: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """profiles.ini から Firefox プロファイルの (絶対パス, 表示名) を列挙"""
    appdata = os.getenv("APPDATA") or ""
    profiles_ini = os.path.join(appdata, "Mozilla", "Firefox", "profiles.ini")
    if not os.path.exists(profiles_ini):
        return []
    cfg = configparser.ConfigParser()
    cfg.read(profiles_ini, encoding="utf-8")
    found: List[Tuple[str, str]] = []
    for sec in cfg.sections():
        if not sec.lower().startswith("profile"):
            continue
        name = cfg[sec].get("Name") or cfg[sec].get("Path", "")
        is_rel = cfg[sec].get("IsRelative", "1") == "1"
        path  = cfg[sec].get("Path", "")
        if not path:
            continue
        abs_path = os.path.join(appdata, "Mozilla", "Firefox", path) if is_rel else path
        if not os.path.isdir(abs_path):
            continue
        if target_names and all(tn.lower() not in name.lower() for tn in target_names):
            continue
        found.append((abs_path, name))
    return found

def _copy_sqlite_with_wal(db_path: str) -> str:
    """cookies.sqlite を tmp にコピー（-wal/-shm あれば一緒に）してパスを返す"""
    tmpdir = tempfile.mkdtemp(prefix="ff_cookies_")
    base = os.path.join(tmpdir, "cookies.sqlite")
    shutil.copy2(db_path, base)
    # WAL/SHM を同名で配置
    for ext_src, ext_dst in ((".sqlite-wal", ".sqlite-wal"), (".sqlite-shm", ".sqlite-shm")):
        src = db_path.replace(".sqlite", ext_src)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tmpdir, "cookies" + ext_dst))
    return base

def get_x_cookies_from_firefox(profile_dir: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Firefox プロファイルの cookies.sqlite から auth_token / ct0 を読む。戻り値: (auth_token, ct0, error)"""
    db = os.path.join(profile_dir, "cookies.sqlite")
    if not os.path.exists(db):
        return None, None, f"[not found] {db}"
    tmp_db = None
    try:
        tmp_db = _copy_sqlite_with_wal(db)
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute(
            '''
            SELECT name, value
            FROM moz_cookies
            WHERE (host LIKE '%x.com' OR host LIKE '%.x.com'
                   OR host LIKE '%twitter.com' OR host LIKE '%.twitter.com')
              AND name IN ('auth_token','ct0')
            ORDER BY lastAccessed DESC
            '''
        )
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
        if tmp_db:
            try:
                shutil.rmtree(os.path.dirname(tmp_db), ignore_errors=True)
            except Exception:
                pass

def get_x_cookies(target_folders: Optional[List[str]] = None,
                  target_names: Optional[List[str]] = None) -> Dict[str, Dict[str, Optional[str]]]:
    """指定条件の Firefox プロファイルから X の auth_token / ct0 をまとめて取得"""
    if target_folders:
        profiles = [(f, os.path.basename(f.rstrip('\\/'))) for f in target_folders]
    else:
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
            "error": e,
        }
    return results

if __name__ == "__main__":
    profs = get_firefox_profiles(target_names=["twitter"])
    if not profs:
        profs = get_firefox_profiles()
    for p, name in profs:
        a, c, e = get_x_cookies_from_firefox(p)
        print(f"[{name}] auth={{}} ct0={{}} err={{}}".format(bool(a), bool(c), e))