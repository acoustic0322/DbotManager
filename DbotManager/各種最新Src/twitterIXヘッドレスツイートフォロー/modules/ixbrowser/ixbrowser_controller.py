import time
import os
import sys
import subprocess
import requests
import sqlite3
from loguru import logger
from .ixbrowser_local_api import IXBrowserClient, Consts, Profile

class IXBrowserController:
    # Global lock to ensure only one thread hits the open/close/reset API at a time
    _api_lock = None

    def __init__(self, target='127.0.0.1', port=53200):
        self.client = IXBrowserClient(target=target, port=port)
        self.client.timeout = 45 # Increased timeout
        self._profile_cache = None # [NEW] Memory cache for profiles
        import threading
        if IXBrowserController._api_lock is None:
            IXBrowserController._api_lock = threading.Lock()
        self._lock = IXBrowserController._api_lock
        
    def wait_until_api_ready(self, timeout=60):
        """Waits until the ixBrowser Local API is responsive and ready, and the internet connection is active."""
        logger.info("Waiting for ixBrowser Local API and internet connection to become ready...")
        time.sleep(3.0)  # Settle buffer for Windows DHCP / RNDIS adapter binding
        start_time = time.time()
        while time.time() - start_time < timeout:
            api_ok = False
            internet_ok = False
            
            # 1. Test local API
            try:
                self.client.get_profile_list(limit=1)
                if self.client.code == 0:
                    api_ok = True
                else:
                    if self.client.code in [1007, 1004]:
                        logger.error(f"❌ [CRITICAL] ixBrowser is LOGGED OUT on this PC (Code {self.client.code}: {self.client.message}). Please open ixBrowser desktop app and log in again. (別のPCでログインしたため、このPCからログアウトされた可能性があります)")
                    else:
                        logger.warning(f"ixBrowser API responded but returned code {self.client.code}: {self.client.message}. Waiting for reconnection...")
            except Exception as e:
                logger.warning(f"ixBrowser API connection failed: {e}. Waiting for server...")
            
            # 2. Test internet connection to ixBrowser cloud server
            if api_ok:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3.0)
                    sock.connect(("www.ixbrowser.com", 443))
                    sock.close()
                    internet_ok = True
                except Exception as e:
                    logger.warning(f"Internet connection to www.ixbrowser.com is NOT ready yet: {e}. Waiting for network to stabilize...")
            
            if api_ok and internet_ok:
                logger.success("ixBrowser Local API is ready and internet connection is active.")
                # Give a small extra buffer for network interfaces to stabilize fully
                time.sleep(3)
                return True
                
            time.sleep(5)
            
        logger.error(f"ixBrowser API and internet connection did not become ready within {timeout} seconds.")
        return False
        
    def _load_profile_cache(self):
        """Loads all profiles into a memory cache to avoid repeated API calls."""
        with self._lock:
            if self._profile_cache is not None:
                return
            logger.info("Loading all ixbrowser profiles into memory cache (First time only)...")
            all_profiles = []
            page = 1
            limit = 200
            while True:
                try:
                    batch = self.client.get_profile_list(limit=limit, page=page)
                    if batch is None: # API failure
                        if "Connection refused" in self.client.message or "10061" in self.client.message:
                            raise ConnectionError("IXBrowserが起動していないか、API(53200)が有効ではありません。IXBrowserを起動してください。")
                        break
                    all_profiles.extend(batch)
                    if len(batch) < limit:
                        break
                    page += 1
                except ConnectionError as e:
                    logger.error(f"❌ {e}")
                    raise e
                except Exception as e:
                    logger.error(f"❌ プロファイルリストの取得中にエラーが発生しました: {e}")
                    break
            
            # Cache by lowercase name for fast lookup
            self._profile_cache = {}
            for p in all_profiles:
                name = str(p.get("name", "")).strip().lower()
                if name:
                    self._profile_cache[name] = p
            
            if not self._profile_cache and all_profiles:
                 logger.warning("No profiles were cached even though API returned results.")
            
            logger.info(f"Memory cache loaded with {len(self._profile_cache)} profiles.")

    def get_or_create_profile(self, screen_name, group_id=None, allow_create=False):
        """Retrieves an existing profile. Creates new only if allow_create=True."""
        from modules.mutual_follow.db_manager import DBManager
        import threading
        
        if not hasattr(IXBrowserController, '_creation_lock'):
            IXBrowserController._creation_lock = threading.Lock()
            
        with IXBrowserController._creation_lock:
            logger.info(f"Checking for existing ixbrowser profile: {screen_name}")
            
            # 1. データベースから検索
            db = DBManager()
            p_id = None
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                p = db._placeholder()
                cursor.execute(f"SELECT profile_id FROM accounts WHERE username = {p}", (screen_name,))
                row = cursor.fetchone()
                if row:
                    p_id = row['profile_id'] if isinstance(row, dict) else row[0]
                    
                if p_id and str(p_id).strip() and str(p_id).strip().lower() != 'nan':
                    detail = self.client.get_profile_detail(p_id)
                    if detail:
                        return p_id
            except Exception as e:
                logger.warning(f"DB lookup failed: {e}")

            # 2. メモリキャッシュ & API全件検索
            if self._profile_cache is None:
                self._load_profile_cache()
                
            clean_name = screen_name.strip().lower()
            found_p = self._profile_cache.get(clean_name)
            
            if not found_p:
                profiles = self.client.get_profile_list(keyword=screen_name, limit=50)
                if profiles:
                    for p in profiles:
                        if str(p.get("name", "")).strip().lower() == clean_name:
                            found_p = p
                            self._profile_cache[clean_name] = p
                            break

            if found_p:
                p_id = found_p.get("profile_id")
                logger.info(f"Found existing profile ID: {p_id}")
                try: db.update_profile_id(screen_name, p_id)
                except: pass
                return p_id

            # 3. 本当にない場合 & 許可されている場合のみ新規作成
            if not allow_create:
                logger.warning(f"Profile NOT FOUND for: {screen_name}. Creation skipped (allow_create=False).")
                return None

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Creating new profile for: {screen_name} (Attempt {attempt+1})")
                    p_obj = Profile(name=screen_name, group_id=group_id)
                    p_id = self.client.create_profile(p_obj)
                    if p_id:
                        logger.success(f"Created profile ID: {p_id}")
                        try:
                            db.update_profile_id(screen_name, p_id)
                            self._profile_cache[clean_name] = {"profile_id": p_id, "name": screen_name}
                        except: pass
                        return p_id
                    else:
                        raise Exception(f"API failed: {self.client.message}")
                except Exception as e:
                    logger.error(f"Failed to create profile: {e}")
                    if "busy" in str(e).lower():
                        time.sleep(10)
                    elif attempt < max_retries - 1:
                        time.sleep(3)
                    else:
                        return None

    def _force_kill_profile_process(self, profile_id, screen_name=None):
        """Kill browser processes started by IXBrowser for this profile using psutil."""
        try:
            import psutil
            killed = 0
            pid_str = str(profile_id)
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name']
                    # 通常、ブラウザは chrome.exe などなので "chrome" のみを対象にして安全性を高める
                    if name and "chrome" in name.lower():
                        cmdline = proc.cmdline()
                        if cmdline:
                            match = False
                            for arg in cmdline:
                                arg_lower = arg.lower()
                                # 1. --profile-directory=48 などの厳密な引数判定
                                if arg.startswith(f"--profile-directory={pid_str}"):
                                    match = True
                                    break
                                # 2. パス中のプロファイルディレクトリ名としての一致 (例: ...\profiles\48\...)
                                if f"profiles\\{pid_str}" in arg_lower or f"profiles/{pid_str}" in arg_lower or arg.endswith(f"\\{pid_str}") or arg.endswith(f"/{pid_str}"):
                                    match = True
                                    break
                                # 3. screen_name が指定されており、かつ十分に長い場合のみ一致を許容
                                if screen_name and len(screen_name) >= 4 and screen_name.lower() in arg_lower:
                                    match = True
                                    break
                            
                            if match:
                                proc.kill()
                                logger.info(f"Force killed PID {proc.info['pid']} for profile {profile_id} ({screen_name or ''})")
                                killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return killed > 0
        except Exception as e:
            logger.warning(f"Force kill via psutil failed: {e}")
            return False

    def _try_attach_open_profile(self, profile_id):
        """Query IXBrowser's open profile list and return debugging_address if found."""
        logger.info(f"Querying IXBrowser open list for profile {profile_id}...")
        open_profiles = self.client.get_open_profiles()
        if open_profiles:
            logger.info(f"Open profiles from IXBrowser: {open_profiles}")
        pid_int = int(profile_id)
        for p in (open_profiles or []):
            if not isinstance(p, dict): continue
            if int(p.get('profile_id', p.get('id', -1))) == pid_int:
                addr = p.get('debugging_address') or p.get('debug_address')
                if addr:
                    logger.info(f"Found open profile {profile_id} at {addr}")
                    return addr
        return None

    def _cleanup_profile_cache(self, profile_id):
        """Clean up local browser cache files for a specific profile to save disk space."""
        try:
            appdata = os.environ.get('APPDATA')
            if appdata and profile_id:
                browser_data_dir = os.path.join(appdata, 'ixBrowser', 'Browser Data')
                p_dir = os.path.join(browser_data_dir, str(profile_id))
                if os.path.exists(p_dir):
                    import shutil
                    target_subdirs = ["", "Default"]
                    target_names = ["Cache", "Code Cache", "GPUCache", "Service Worker", "DawnWebGPUCache", "DawnGraphiteCache"]
                    for subdir in target_subdirs:
                        base_path = os.path.join(p_dir, subdir) if subdir else p_dir
                        if os.path.exists(base_path):
                            for name in target_names:
                                t_path = os.path.join(base_path, name)
                                if os.path.exists(t_path):
                                    shutil.rmtree(t_path, ignore_errors=True)
                    logger.info(f"Cleaned up browser cache for profile: {profile_id}")
        except Exception as e:
            logger.warning(f"Failed to clean browser cache for profile {profile_id}: {e}")

    def open_browser_dp(self, profile_id, screen_name=None, headless=False, max_open_retries=5):
        """Open the profile and return a DrissionPage ChromiumPage. Default headless is now False."""
        """Open the profile and return a DrissionPage ChromiumPage."""
        
        def is_port_open(target_ip, target_port):
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex((target_ip, int(target_port))) == 0
        
        # Standard args
        launch_args = [
            '--no-sandbox',
            '--disable-gpu',
            '--mute-audio',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=CalculateWindowOcclusion'
        ]
        # Randomize window size
        import random as _random
        resolutions = [
            (1280, 720), (1366, 768), (1440, 900), (1600, 900), (1920, 1080),
            (1280, 800), (1536, 864), (1024, 768)
        ]
        w, h = _random.choice(resolutions)
        launch_args.append(f"--window-size={w},{h}")

        if headless:
            launch_args.append('--headless=new')
            # Avoid extreme position if possible
            launch_args.append('--window-position=-2000,-2000')

        debugging_address = None
        
        # [SERIALIZED LAUNCHING] Keep lock held until the port is open and ready
        for attempt in range(max_open_retries):
            logger.info(f"  🔒 [LOCK] {profile_id} waiting for API slot (Attempt {attempt+1})...")
            with IXBrowserController._api_lock:
                logger.info(f"  🚀 [LOCK] {profile_id} sending open command...")
                
                # 起動前には必ず古いプロセスを終了させ、オープン状態をクリアする（1回目から実施！）
                logger.info(f"  ⚠️ Cleaning up existing states for profile {profile_id} before launch...")
                self.client.close_profile(profile_id)
                self._force_kill_profile_process(profile_id, screen_name=screen_name)
                self.client.reset_open_state(profile_id)
                self._cleanup_profile_cache(profile_id)
                
                # 段階的な待機時間を設けてプロキシとIX側の処理時間を確保する
                time.sleep(2.0 + attempt * 2.0)
                
                open_result = self.client.open_profile(
                    profile_id, 
                    cookies_backup=True,
                    load_profile_info_page=False, 
                    args=launch_args
                )
                
                if open_result:
                    debugging_address = open_result.get('debugging_address')
                    if debugging_address:
                        addr = debugging_address.replace("http://", "")
                        ip, port = addr.split(":")
                        
                        logger.info(f"  ⏳ [CONNECT] Waiting for port {port} to open (inside Lock)...")
                        port_ready = False
                        for _ in range(10): # Max 10 seconds wait
                            if is_port_open(ip, port):
                                port_ready = True
                                break
                            time.sleep(1)
                            
                        if port_ready:
                            logger.info(f"  🚀 [CONNECT] Port {port} is open. Cool down buffer (inside Lock)...")
                            time.sleep(3.0) # ロック解放前に待機
                            break
                        else:
                            logger.warning(f"  ❌ Port {port} did not open in time. Retrying opening...")
                            open_result = None
                            debugging_address = None
            
                if not open_result:
                    msg = self.client.message or "Unknown Error"
                    logger.warning(f"Profile open failed (Code {self.client.code}): {msg}")
                    
                    if self.client.code == 1004:
                        logger.error("👉 [Code 1004 - Unknown Internal Error] Usually indicates ixBrowser is logged out on this PC, the Local API is disabled, or the profile's proxy is offline. Please verify the ixBrowser desktop app status.")
        
                    if self.client.code in [1008, 1004, 2012, 10000, 10001, -1, 111003, 2007]:
                        if self.client.code == 2007:
                            logger.error(f"Profile {profile_id} does not exist in IXBrowser. Returning MISSING_PROFILE.")
                            return "MISSING_PROFILE"
                        
                        # Clean up processes for retry
                        self._force_kill_profile_process(profile_id, screen_name=screen_name)
                        self.client.reset_open_state(profile_id)
                        
                        # 2012 (Syncing) の場合は少し長めに待つが、それ以外は早めに回す
                        wait_time = 5 + (attempt * 2)
                        if self.client.code == 2012: wait_time += 5
                        
                        time.sleep(wait_time)
                        continue
                    
                    time.sleep(3)

        if not debugging_address:
            logger.error(f"Failed to open profile {profile_id}. Skipping.")
            return None

        try:
            from DrissionPage import ChromiumPage, ChromiumOptions
            addr = debugging_address.replace("http://", "")
            ip, port = addr.split(":")
            co = ChromiumOptions()
            co.set_local_port(int(port))
            # Critical: Use true headless mode and fix 404 connection error with allow-origins
            if headless:
                co.set_argument('--headless=new')
            co.set_argument('--remote-allow-origins=*')
            if headless:
                co.set_argument('--window-position=-2000,-2000') 
            co.set_argument('--window-size=1280,720')
            co.set_argument('--disable-gpu')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-background-timer-throttling')
            co.set_argument('--disable-backgrounding-occluded-windows')
            co.set_argument('--disable-renderer-backgrounding')
            co.set_argument('--disable-features=CalculateWindowOcclusion')
            
            page = ChromiumPage(co)
            page.set.load_mode('none')
            logger.success(f"  ✅ [CONNECT] Successfully attached (Profile: {profile_id})")
            return page
        except Exception as e:
            logger.error(f"  ❌ [FATAL] Critical error in open_browser_dp: {e}")
            return None

    def close_browser(self, profile_id, screen_name=None):
        """Close the ixbrowser profile, verify via local processes, and reset state."""
        if not profile_id:
            logger.info(f"Skipping close_browser because profile_id is None (Target: {screen_name})")
            return True
            
        logger.info(f"Closing ixbrowser profile: {profile_id} (Target: {screen_name or 'Unknown'}). Waiting for API lock...")
        
        with self._lock:
            logger.info(f"🔒 [LOCK] {profile_id} close command sending...")
            # 1. API 経由でクローズを指示 (これにより ixBrowser が終了処理とクラウド同期を行う)
            self.client.close_profile(profile_id)
            
            # 2. ローカルプロセスが終了するのを待機 (psutil を使用して API コールを回避)
            import psutil
            closed_gracefully = False
            search_terms = [f"--profile-directory={profile_id}", str(profile_id)]
            if screen_name:
                search_terms.append(screen_name)
                
            # 最大5秒間、プロセスが消えるのを監視
            for _ in range(5):
                time.sleep(1.0)
                still_running = False
                try:
                    for proc in psutil.process_iter(['name']):
                        try:
                            name = proc.info['name']
                            if name and ("chrome" in name.lower() or "ixbrowser" in name.lower()):
                                cmdline = proc.cmdline()
                                if cmdline and any(term in " ".join(cmdline) for term in search_terms):
                                    still_running = True
                                    break
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                except Exception:
                    pass
                    
                if not still_running:
                    closed_gracefully = True
                    logger.success(f"Successfully closed profile {profile_id} (Process terminated gracefully).")
                    break
                    
            # 3. 5秒経ってもプロセスが残っている場合は強制終了
            if not closed_gracefully:
                logger.warning(f"Profile {profile_id} process did not terminate. Force killing...")
                self._force_kill_profile_process(profile_id, screen_name=screen_name)
                time.sleep(1.0)
                
            # 4. [FAILSAFE] 状態強制リセット (get_open_profiles でのチェックを省き、毎回安全のために投げる)
            logger.info(f"Applying [Open State Reset] for session: {profile_id}")
            self.client.reset_open_state(profile_id)
            
            # 5. [NEW] キャッシュフォルダの自動削除 (空き容量の確保)
            self._cleanup_profile_cache(profile_id)

            # 6. クラウド同期のための最終待機 (IXBrowserの画面フリーズ防止のため長めに設定)
            time.sleep(2.0) 
            
        return True
    
    def full_profile_reset(self, profile_id, screen_name):
        """プロファイルを削除→再作成でリセットする (グループは引き継ぐ)"""
        logger.warning(f"🛑 {screen_name}: プロファイルを削除して再作成します...")
        
        # 0. 元のプロファイル情報を取得 (グループIDを保持するため)
        old_profile_data = self.client.get_profile_detail(profile_id)
        group_id = old_profile_data.get('group_id') if old_profile_data else None
        if group_id:
            logger.info(f"📁 元のグループID: {group_id} を引き継ぎます")

        # 1. クローズ
        self.client.close_profile(profile_id)
        time.sleep(2)
        # 2. 残留プロセス強制終了
        self._force_kill_profile_process(profile_id, screen_name=screen_name)
        time.sleep(3)
        # 3. 削除
        try:
            res_del = self.client._post("/v2/profile-delete", {"profile_id": int(profile_id)})
            if self.client.code == 0:
                logger.info(f"🗑️ プロファイル {profile_id} を削除しました")
            elif self.client.code == 2007:
                logger.info(f"🗑️ プロファイル {profile_id} は既に存在しません。削除をスキップします")
            else:
                logger.error(f"削除エラー: {self.client.message}")
        except Exception as e:
            logger.error(f"削除例外: {e}")
            return None
        time.sleep(3)
        
        # 4. 新規作成（Cloudflare回避設定を含む）
        # DBからアカウント情報を取得
        try:
            conn = sqlite3.connect('system.db')
            cursor = conn.cursor()
            cursor.execute('SELECT password, totp_secret, auth_token, ct0, group_id FROM accounts WHERE username = ?', (screen_name,))
            row = cursor.fetchone()
            conn.close()
        except Exception as e:
            logger.error(f"DB取得エラー: {e}")
            row = None

        db_password = row[0] if row else ''
        db_totp = row[1] if row else ''
        db_group_id = row[4] if row and len(row) > 4 else None
        
        # もしAPIから取得できなかった場合、DBの情報を優先
        if not group_id and db_group_id:
            group_id = db_group_id
            logger.info(f"📁 DBからグループID: {group_id} を取得しました")
        
        p_obj = Profile(name=screen_name, group_id=group_id)
        p_obj.username = screen_name
        p_obj.password = db_password
        
        # Custom fingerprinting for creation (some parameters might need direct dict if Profile class doesn't support)
        # But we can modify create_profile to accept extra args or just do it here for now if needed.
        # Let's stick to the client's create_profile but maybe it needs more flexibility.
        
        # The original code used a custom payload for fingerprinting. 
        # Let's adjust create_profile in local_api to accept optional fingerprint_config.
        
        # Actually, let's just use the client._post here for the complex payload since it's specific.
        payload = {
            "site_url": "https://x.com",
            "name": screen_name,
            "username": screen_name,
            "password": db_password,
            "tfa_secret": db_totp,
            "group_id": int(group_id) if group_id else None,
            "fingerprint_config": {
                "cloudflare_challenge_bypassing": "1",
                "platform": "Windows",
            }
        }
        res = self.client._post("/v2/profile-create", payload)
        new_pid = res.get("data") if self.client.code == 0 else None
        
        if new_pid:
            logger.success(f"✅ {screen_name}: 再作成完了 (新ID: {new_pid}, Group: {group_id})")
            return new_pid
        logger.error(f"❌ {screen_name}: 再作成失敗 - {self.client.message}")
        return None

    def reset_profile_default_optimized(self, profile_id, screen_name):
        """Delete and recreate a profile with default settings and optimized Cloudflare verification."""
        logger.warning(f"[{screen_name}] JF form error detected. Recreating IXBrowser profile with default settings.")

        group_id = None
        if profile_id:
            try:
                old_profile_data = self.client.get_profile_detail(profile_id)
                if old_profile_data:
                    group_id = old_profile_data.get("group_id")
            except Exception as e:
                logger.warning(f"[{screen_name}] Failed to read old profile detail: {e}")

        if not group_id:
            try:
                from modules.mutual_follow.db_manager import DBManager
                db = DBManager()
                conn = db.get_connection()
                cursor = conn.cursor()
                p = db._placeholder()
                cursor.execute(f"SELECT group_id FROM accounts WHERE username = {p}", (screen_name,))
                row = cursor.fetchone()
                if row:
                    group_id = row["group_id"] if isinstance(row, dict) else row[0]
            except Exception as e:
                logger.warning(f"[{screen_name}] Failed to read group_id from DB: {e}")

        if profile_id:
            try:
                self.close_browser(profile_id, screen_name=screen_name)
            except Exception as e:
                logger.warning(f"[{screen_name}] Close before reset failed: {e}")
            try:
                self._force_kill_profile_process(profile_id, screen_name=screen_name)
                self.client.reset_open_state(profile_id)
            except Exception:
                pass
            try:
                self.client._post("/v2/profile-delete", {"profile_id": int(profile_id)})
                if self.client.code == 0:
                    logger.info(f"[{screen_name}] Deleted old profile {profile_id}.")
                elif self.client.code == 2007:
                    logger.info(f"[{screen_name}] Old profile {profile_id} did not exist. Continuing.")
                else:
                    logger.warning(f"[{screen_name}] Profile delete returned code {self.client.code}: {self.client.message}")
            except Exception as e:
                logger.error(f"[{screen_name}] Failed to delete old profile {profile_id}: {e}")
                return None

        time.sleep(3)
        payload = {
            "site_url": "https://x.com",
            "name": screen_name,
            "fingerprint_config": {
                "cloudflare_challenge_bypassing": "1",
                "platform": "Windows",
            },
        }
        if group_id:
            try:
                payload["group_id"] = int(group_id)
            except Exception:
                payload["group_id"] = group_id

        res = self.client._post("/v2/profile-create", payload)
        new_pid = res.get("data") if self.client.code == 0 else None
        if not new_pid:
            logger.error(f"[{screen_name}] Failed to recreate profile: {self.client.message}")
            return None

        try:
            from modules.mutual_follow.db_manager import DBManager
            DBManager().update_profile_id(screen_name, new_pid)
        except Exception as e:
            logger.warning(f"[{screen_name}] Failed to save new profile_id {new_pid}: {e}")

        clean_name = screen_name.strip().lower()
        if self._profile_cache is not None:
            self._profile_cache[clean_name] = {"profile_id": new_pid, "name": screen_name}

        logger.success(f"[{screen_name}] Recreated profile with Cloudflare Verification Optimized. New ID: {new_pid}")
        return new_pid

    def get_all_accounts(self, group_id=None):
        """Fetch all profiles and sync with local DB."""
        logger.info("Fetching profiles from IXBrowser API...")
        
        all_profiles_raw = []
        page = 1
        limit = 100
        while True:
            batch = self.client.get_profile_list(limit=limit, page=page, group_id=group_id)
            if not batch:
                break
            all_profiles_raw.extend(batch)
            if len(batch) < limit:
                break
            page += 1
            
        profiles = all_profiles_raw
        all_profiles = []
        
        if profiles:
            from modules.mutual_follow.db_manager import DBManager, DB_PATH
            db = DBManager()
            
            # DBから情報を取得するための準備
            db_info = {}
            try:
                # DBManagerが提供する接続を使用する（MySQL/Postgres/SQLiteすべてに対応）
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT username, selected, is_alive, display_name FROM accounts')
                rows = cursor.fetchall()
                for r in rows:
                    # DictRow or tuple handling
                    if isinstance(r, dict):
                        db_info[r['username']] = r
                    else:
                        db_info[r[0]] = {'selected': r[1], 'is_alive': r[2], 'display_name': r[3]}
                
                # SQLiteの場合のみ個別にUPDATE（既存の挙動維持のため）
                if db.db_type == 'sqlite':
                    for p in profiles:
                        p_id = p.get("profile_id")
                        screen_name = p.get("name")
                        cursor.execute('UPDATE accounts SET profile_id = ? WHERE username = ?', (p_id, screen_name))
                    conn.commit()
            except Exception as e:
                logger.warning(f"DB Sync Warning: {e}")

            # プロファイルリストの作成（DB情報の有無に関わらず実行）
            for p in profiles:
                p_id = p.get("profile_id")
                screen_name = p.get("name")
                
                info = db_info.get(screen_name, {})
                is_selected = bool(info.get('selected', False))
                is_alive = bool(info.get('is_alive', True))
                stored_display_name = info.get('display_name', "")
                
                all_profiles.append({
                    "screen_name": screen_name,
                    "assigned_name": stored_display_name if stored_display_name else screen_name,
                    "profile_id": p_id,
                    "username": p.get("username", ""),
                    "password": p.get("password", ""),
                    "totp_secret": p.get("tfa_secret", ""),
                    "proxy": p.get("proxy_data", {}).get("proxy_address", "") if p.get("proxy_data") else "",
                    "status": "Active" if is_alive else "Suspended",
                    "is_suspended": not is_alive,
                    "Select": is_selected,
                    "group_id": p.get("group_id")
                })
        return all_profiles

    def get_all_groups(self):
        """Fetch profile groups."""
        groups = self.client.get_group_list()
        group_list = [{"id": None, "title": "すべて"}]
        if groups:
            for g in groups:
                group_list.append({"id": g.get("id"), "title": g.get("title")})
        return group_list

    def update_profile(self, profile_id, data):
        data['profile_id'] = int(profile_id)
        # Wrap in a Profile dummy for compatibility with our client logic
        from .ixbrowser_local_api import Profile as ProfileObj
        p = ProfileObj(profile_id=profile_id)
        p.name = data.get('name')
        return self.client.update_profile(p)
