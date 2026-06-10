import subprocess
import time
import requests
import os
from loguru import logger

class PixelIPRotator:
    """
    Google Pixel 4a (5G) をADBコマンドで制御し、
    機内モードON/OFFによるIPアドレスローテーションを行うクラス。
    """
    def __init__(self, adb_path=None):
        """
        :param adb_path: adbコマンドのパス。Noneの場合は自動探索します。
        """
        self.adb_path = adb_path if adb_path else self._find_adb()
        logger.debug(f"Using ADB path: {self.adb_path}")

    def _find_adb(self):
        """ADBコマンドの場所を自動的に探します。"""
        # 1. Check if 'adb' is in PATH
        import shutil
        if shutil.which("adb"):
            return "adb"
        
        # 2. Check known Winget install path
        winget_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe")
        if os.path.exists(winget_path):
            return winget_path
            
        # 3. Check standard SDK path (User might have manually installed)
        sdk_path = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe")
        if os.path.exists(sdk_path):
            return sdk_path

        # 4. Check local project tools path (common layouts)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        check_paths = [
            os.path.join(base_dir, "platform-tools", "adb.exe"),
            os.path.join(base_dir, "tools", "adb", "adb.exe"),
        ]
        for p in check_paths:
            if os.path.exists(p):
                return p

        # Default fallback
        return "adb"

    def execute_adb_command(self, command_args):
        """
        ADBコマンドを実行するヘルパーメソッド。
        :param command_args: コマンド引数のリスト（例: ['shell', 'cmd', ...]）
        :return: 標準出力 (str)
        """
        cmd = [self.adb_path] + command_args
        logger.debug(f"Executing ADB command: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8' 
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # Check for specifically "no devices/emulators found"
            if "no devices/emulators found" in e.stderr.lower():
                logger.warning("📵 ADB Error: No Pixel device found. Please connect your phone and enable USB debugging.")
            else:
                logger.error(f"ADB Command Failed: {e}")
                logger.error(f"Stderr: {e.stderr}")
            raise e
        except FileNotFoundError:
            logger.error(f"ADB command not found at '{self.adb_path}'. Please check your PATH or installation.")
            raise

    def is_device_connected(self):
        """Check if any ADB device is connected and authorized."""
        try:
            output = self.execute_adb_command(['devices'])
            # Valid output has lines like "SERIAL_NUMBER	device"
            device_lines = [l for l in output.splitlines() if "device" in l and not l.startswith("List of")]
            return len(device_lines) > 0
        except Exception:
            return False

    def toggle_airplane_mode(self):
        """
        機内モードをONにし、暫く待機してからOFFにします。
        """
        logger.info("✈️ Toggling Airplane Mode...")
        
        # 1. 機内モード ON
        logger.info("   -> Enabling Airplane Mode")
        self.execute_adb_command(['shell', 'cmd', 'connectivity', 'airplane-mode', 'enable'])
        
        # 2. 待機 (電波を確実に切断するため)
        time.sleep(2)
        
        # 3. 機内モード OFF
        logger.info("   -> Disabling Airplane Mode")
        self.execute_adb_command(['shell', 'cmd', 'connectivity', 'airplane-mode', 'disable'])

    def enable_usb_tethering(self):
        """
        USBテザリングを強制的に有効化します (RNDIS)。
        機内モード操作でUSBテザリングがOFFになる仕様への対策。
        """
        logger.info("🔌 Enabling USB Tethering (rndis)...")
        # Pixel等の場合、svc usb setFunctions rndis でテザリングONにできることが多い
        self.execute_adb_command(['shell', 'svc', 'usb', 'setFunctions', 'rndis'])
        
        # 設定反映待ち
        time.sleep(3)

    def get_external_ip(self):
        """
        現在のグローバルIPアドレスを取得します。
        """
        # "自分でping叩かん勝ったら変わるわけない" -> Explicitly ping to wake up/check
        # Windowsのpingコマンドを実行
        try:
            with open(os.devnull, 'w') as devnull:
                subprocess.run(['ping', '-n', '1', '1.1.1.1'], stdout=devnull, stderr=devnull)
        except Exception:
            pass # ping失敗は許容

        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                # logger.debug(f"Current IP: {ip}") # 多すぎるとうるさいので必要ならdebug
                return ip
        except requests.RequestException:
            pass # 接続不可
        return None

    def check_internet_connection(self, max_retries=20, interval=3):
        """
        インターネット接続が復帰するまで待機します。
        :param max_retries: 最大リトライ回数
        :param interval: リトライ間隔(秒)
        :return: 接続成功ならTrue
        """
        logger.info("Checking Internet Connection...")
        for i in range(max_retries):
            ip = self.get_external_ip()
            if ip:
                logger.info(f"   -> Connected! IP: {ip}")
                return True
            
            logger.debug(f"   ... waiting for connection ({i+1}/{max_retries})")
            time.sleep(interval)
        
        logger.error("❌ Connection Timeout.")
        return False

    def rotate_ip(self, max_rotation_retries=3):
        """
        IPアドレスローテーションのメインロジック。
        IPが変わるまでリトライします。
        
        :param max_rotation_retries: IPが変わらなかった場合に最初からやり直す回数
        :return: (Success: bool, NewIP: str)
        """
        logger.info("🔄 Starting IP Rotation Process (Pixel ADB)...")

        # 0. Check if device is even connected
        if not self.is_device_connected():
            logger.error("❌ IP Rotation aborted: No ADB device connected. Please plug in your Pixel phone.")
            return False, None

        for attempt in range(max_rotation_retries):
            # 1. 現在のIPを取得
            old_ip = self.get_external_ip()
            logger.info(f"Old IP: {old_ip if old_ip else 'Unknown'}")

            # 2. 機内モード ON/OFF
            try:
                self.toggle_airplane_mode()
            except Exception as e:
                logger.error(f"Failed to toggle airplane mode: {e}")
                return False, None

            # 3. 待機 (SIMが電波を掴むまで少し待つ)
            time.sleep(5)

            # 4. USBテザリング再有効化
            try:
                self.enable_usb_tethering()
            except Exception as e:
                logger.error(f"Failed to enable USB tethering: {e}")
                return False, None

            # 5. 回線復帰＆IP確認
            if self.check_internet_connection():
                # IPが変わったか確認するためのループ
                # check_internet_connectionで繋がった瞬間はまだ古いIPのキャッシュかもしれないし、
                # 新しいIPになっているかもしれない。
                # ここでは確実に新しいIPを取得して比較する。
                
                logger.info("Verifying IP change...")
                for _ in range(10): # 最大30秒程度確認
                    new_ip = self.get_external_ip()
                    if new_ip and new_ip != old_ip:
                         logger.success(f"✅ IP Rotation Successful! New IP: {new_ip}")
                         return True, new_ip
                    
                    time.sleep(3)
                
                logger.warning(f"⚠️ IP Address did not change (Attempt {attempt+1}/{max_rotation_retries}). Retrying...")
            else:
                logger.warning(f"⚠️ Failed to reconnect internet (Attempt {attempt+1}/{max_rotation_retries}). Retrying...")
            
            # 失敗時は少し待ってから再試行
            time.sleep(5)

        logger.error("❌ Failed to rotate IP after multiple attempts.")
        return False, None

if __name__ == "__main__":
    # 単体テスト用
    rotator = PixelIPRotator()
    success, new_ip = rotator.rotate_ip()
    if success:
        print(f"Global IP rotated successfully: {new_ip}")
    else:
        print("Failed to rotate IP.")
