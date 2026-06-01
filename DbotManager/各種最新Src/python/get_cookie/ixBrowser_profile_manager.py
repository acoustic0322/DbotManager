import requests
import time
import random
import threading
from .ix_lock import ix_api_lock

# Thread Lock and Cache
print_lock = threading.Lock()
PROFILE_CACHE = {}  # {name: profile_id}
PROFILE_CACHE_LOCK = threading.Lock()
profile_creation_lock = threading.Lock()

def safe_print(*args, **kwargs):
    """スレッドセーフなprint関数"""
    with print_lock:
        print(*args, **kwargs)

def generate_chrome_140_ua(platform="Windows"):
    """
    Chrome 140.0.0.0〜145.0.0.0 の範囲でランダムなUser-Agentを生成する
    """
    chrome_ver = f"{random.randint(140, 145)}.0.{random.randint(0, 9999)}.{random.randint(0, 99)}"
    if platform == "Macos":
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
    else:
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"

def find_profile_by_name(api_base, username):
    """
    profile-list APIを使用してプロファイル名で直接検索する。
    ページネーションに対応し、取得した全プロファイルをキャッシュに保存して以降の検索を高速化する。
    """
    try:
        username_clean = str(username).strip()
        page = 1
        limit = 100
        
        while True:
            payload = {"title": username_clean, "page": page, "limit": limit}
            
            print(payload)

            res_raw = None
            for retry in range(3):
                try:
                    with ix_api_lock:
                        res_raw = requests.post(f"{api_base}/profile-list", json=payload, timeout=20)
                    if res_raw.status_code == 200: break
                except Exception as e:
                    if retry == 2: safe_print(f"[{username}] ⚠️ API接続エラー (profile-list): {e}")
                    time.sleep(2)
            
            if not res_raw: return None
            res = res_raw.json()
            
            data = res.get("data")
            if not data:
                safe_print(f"[{username}] ⚠️ API応答異常 (dataなし): {res}")
                return None
                
            profiles = data.get("data", [])
            total_count = data.get("total", 0)
            
            if not profiles:
                if page == 1:
                    safe_print(f"[{username}] 🔎 検索結果 0 件 (Total: {total_count})")
                break
            
            # 取得した全プロファイルをループしつつキャッシュを更新
            found_id = None
            with PROFILE_CACHE_LOCK:
                for p in profiles:
                    p_name = str(p.get("name", "")).strip()
                    p_title = str(p.get("title", "")).strip()
                    p_id = p.get("profile_id")
                    
                    if p_name: PROFILE_CACHE[p_name] = p_id
                    if p_title: PROFILE_CACHE[p_title] = p_id
                    
                    if not found_id and (p_name == username_clean or p_title == username_clean):
                        found_id = p_id
                        
            if found_id:
                return found_id
                
            # 次のページがあるか判定
            if page * limit >= total_count:
                safe_print(f"[{username}] 🔎 全ページ({total_count}件)をチェックしましたが一致するプロファイルはありませんでした。")
                break
                
            page += 1
            
    except Exception as e:
        safe_print(f"[{username}] ⚠️ 直接検索中にエラー: {e}")

    return None

def create_ix_profile(api_base, username, password, tfa_key="", group_id=250972, site_url="https://x.com"):

    """
    ixBrowserで新しいプロファイルを作成する
    """
    print("create_ix_profile : start")

    with profile_creation_lock:
        # 再度チェック (Lock待ちの間に他スレッドが作った可能性)
        with PROFILE_CACHE_LOCK:
            profile_id = PROFILE_CACHE.get(username)
        
        if profile_id:
            safe_print(f"[{username}] ℹ️ プロファイルは既に存在します (ID: {profile_id})")
            return profile_id
            
        safe_print(f"[{username}] ✨ プロファイルを新規作成します")
        
        # プロキシ設定 (常にダイレクト接続に固定)
        proxy_payload = {
            "proxy_mode": 2,
            "proxy_type": "direct"
        }

        create_payload = {
            "name": username,
            "group_id": group_id,
            "site_id": 21,                    
            "site_url": site_url,
            "username": username,
            "password": password,
            "tfa_secret": tfa_key,
            "proxy_config": proxy_payload,
            "preference_config": {
                "block_restore_pages": "1",
                "show_profile_name": "1",
                "block_password_pages": "1",
                "load_profile_info_page": "0",
                "show_proxy_ip": "1",
                "block_image": "0" 
            }
        }
        
        try:
            with ix_api_lock:
                res_create = requests.post(f"{api_base}/profile-create", json=create_payload).json()
                
            if res_create.get("data"):
                profile_id = res_create.get("data")
                safe_print(f"[{username}] ✅ プロファイル新規作成成功 (ID: {profile_id})")
                
                with PROFILE_CACHE_LOCK:
                    PROFILE_CACHE[username] = profile_id
                return profile_id
            else:
                safe_print(f"[{username}] ⚠️ プロファイル作成に失敗しました: {res_create}")
                safe_print(f"[{username}] 🔄 最終手段として再検索を試みます...")
                profile_id = find_profile_by_name(api_base, username)
                if profile_id:
                    safe_print(f"[{username}] ✅ 再検索でIDを救出しました (ID: {profile_id})")
                    return profile_id
        except Exception as e:
            safe_print(f"[{username}] ❌ プロファイル作成中にエラー: {e}")
            
    return None

def get_or_create_profile(api_base, username, password, tfa_key="", group_id=250972):
    """
    既存のプロファイルがあればそれを返し、なければ新規作成するフロー
    """
    print("get_or_create_profile : start")


    # 1. まず既存のプロファイルが存在するか検索する
    existing_id = find_profile_by_name(api_base, username)
    if existing_id:
        safe_print(f"[{username}] ℹ️ 既存のプロファイル({existing_id})が見つかりました。これを使用します。")
        # キャッシュに保存
        with PROFILE_CACHE_LOCK:
            PROFILE_CACHE[username.strip()] = existing_id
        return existing_id

    # 2. 存在しない場合は新規作成する
    profile_id = create_ix_profile(api_base, username, password, tfa_key, group_id)
    
    # 3. 新しく作ったものをキャッシュに保存
    if profile_id:
        with PROFILE_CACHE_LOCK:
            PROFILE_CACHE[username.strip()] = profile_id
            
    return profile_id

def delete_profile_and_clear_cache(api_base, username, profile_id):
    """
    古い・破損したプロファイルを削除し、キャッシュをクリアする
    """
    safe_print(f"[{username}] 🗑️ 古いプロファイル({profile_id})を削除しています...")
    try:
        with ix_api_lock:
            requests.post(f"{api_base}/profile-delete", json={"profile_id": profile_id}, timeout=15)
        with PROFILE_CACHE_LOCK:
            if username in PROFILE_CACHE:
                del PROFILE_CACHE[username]
    except Exception as e:
        safe_print(f"[{username}] ⚠️ プロファイル削除エラー: {e}")

# 簡単なテスト用 (モジュールとしてインポートされた場合は実行されない)
if __name__ == "__main__":
    API_BASE = "http://127.0.0.1:53200/api/v2"
    test_user = "test_user_001"
    test_pass = "TestPass123!"
    
    print(f"--- Testing Profile Manager for {test_user} ---")
    pid = get_or_create_profile(API_BASE, test_user, test_pass)
    print(f"Result Profile ID: {pid}")
