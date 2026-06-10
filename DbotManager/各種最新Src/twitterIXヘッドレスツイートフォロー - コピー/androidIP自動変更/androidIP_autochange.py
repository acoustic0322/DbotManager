import subprocess
import time

# --- 設定：ADB.exeのフルパス (実行ファイルの場所から相対取得) ---
import os
ADB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "abc", "adb.exe")

def ensure_adb_server_running(adb_path):
    """Starts the ADB server daemon without capturing output to avoid pipe hangs on Windows."""
    try:
        subprocess.run([adb_path, "start-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
    except Exception as e:
        print(f"[WARNING] Failed to pre-start ADB server: {e}")

def adb_check(adb_path):
    """Checks if ADB is responding, devices are connected, and authorized."""
    ensure_adb_server_running(adb_path)
    try:
        res = subprocess.run([adb_path, "devices"], timeout=10, capture_output=True, text=True, check=True)
        output = res.stdout
        
        # Parse adb devices output
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        # Filter out header and daemon start lines
        device_lines = []
        for line in lines:
            if line.startswith("List of devices attached") or line.startswith("*"):
                continue
            device_lines.append(line)
            
        if not device_lines:
            print("[ERROR] Android端末が検出されませんでした。")
            print("[TIP] スマホがUSBケーブルでPCに正しく接続されているか、および「USBデバッグ」が有効になっているか確認してください。")
            return False
            
        unauthorized_found = False
        authorized_found = False
        for line in device_lines:
            parts = line.split()
            if len(parts) >= 2:
                status = parts[1]
                if status == "unauthorized":
                    unauthorized_found = True
                elif status == "device":
                    authorized_found = True
                    
        if unauthorized_found and not authorized_found:
            print("[ERROR] Android端末が認証されていません (device unauthorized)。")
            print("[TIP] スマホのロックを解除し、画面に表示されている『USBデバッグを許可しますか？』のダイアログで許可（常に許可を推奨）を押してください。")
            # Try restarting adb server to prompt the dialog
            print("[INFO] 認証ダイアログの表示を促すため、ADBサーバーを再起動します...")
            try:
                subprocess.run([adb_path, "kill-server"], timeout=10, check=False)
                subprocess.run([adb_path, "start-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=True)
            except:
                pass
            return False
        elif not authorized_found:
            print("[ERROR] 接続されているAndroid端末にアクセスできません（ステータスが不正です）。")
            return False
            
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"[WARNING] ADB not responding ({e}). Restarting server...")
        try:
            subprocess.run([adb_path, "kill-server"], timeout=10, check=False)
            subprocess.run([adb_path, "start-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=True)
            
            # Recheck after restart
            res = subprocess.run([adb_path, "devices"], timeout=10, capture_output=True, text=True, check=True)
            if "unauthorized" in res.stdout:
                print("[ERROR] Android端末が認証されていません。")
                print("[TIP] スマホのロックを解除し、画面に表示されている『USBデバッグを許可しますか？』のダイアログで許可を押してください。")
                return False
            return True
        except Exception as ex:
            print(f"[ERROR] ADBサーバーの起動または接続チェックに失敗しました: {ex}")
            print("[TIP] スマホのロックを解除し、画面に『USBデバッグを許可しますか？』と表示されていないか確認してください。")
            return False

def get_current_ip(adb_path):
    """ADB経由で現在のパブリックIPアドレスを取得する"""
    ensure_adb_server_running(adb_path)
    try:
        # curl または wget を試行
        for cmd in [["curl", "-s", "https://ifconfig.me"], ["wget", "-qO-", "https://ifconfig.me"]]:
            try:
                res = subprocess.run([adb_path, "shell"] + cmd, timeout=12, capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    ip = res.stdout.strip()
                    if "." in ip or ":" in ip: # Valid IP check
                        return ip
            except:
                continue
    except:
        pass
    return None

def reset_mobile_data(wait_seconds=5, adb_path_override=None):
    """
    AndroidのモバイルデータをON/OFFしてIPを確実にリセット・検証する
    """
    adb_path = adb_path_override if adb_path_override else ADB_PATH
    
    # 0. 事前チェック
    if not adb_check(adb_path):
        return False
    
    old_ip = get_current_ip(adb_path)
    if old_ip:
        print(f"[INFO] 現在のIP: {old_ip}")
    else:
        print("[WARNING] 現在のIPを取得できませんでした。続行します。")

    try:
        # 1. 機内モード ON
        print("[INFO] 機内モードをONに設定中（切断開始）...")
        subprocess.run([adb_path, "shell", "cmd", "connectivity", "airplane-mode", "enable"], timeout=20, check=True)

        # 待機
        print(f"[INFO] {wait_seconds}秒間待機（切断中）...")
        time.sleep(wait_seconds)

        # 2. 機内モード OFF
        print("[INFO] 機内モードをOFFに設定中（再接続開始）...")
        subprocess.run([adb_path, "shell", "cmd", "connectivity", "airplane-mode", "disable"], timeout=20, check=True)

        # 3. USBテザリング再有効化 (機内モード操作でUSBテザリングがOFFになる仕様への対策)
        print("[INFO] USBテザリング（RNDIS）を再有効化中...")
        try:
            subprocess.run([adb_path, "shell", "svc", "usb", "setFunctions", "rndis"], timeout=20, check=True)
            time.sleep(3)
        except Exception as e:
            print(f"[WARNING] USBテザリングの再有効化に失敗しました (スキップします): {e}")

        # 4. ネットワーク復旧とIP変更の検証（最大60秒）
        print("[INFO] ネットワークの復旧と新しいIPを確認中...")
        new_ip = None
        for i in range(30): # 2秒おきに30回 = 最大60秒
            time.sleep(2)
            new_ip = get_current_ip(adb_path)
            if new_ip:
                if new_ip != old_ip:
                    print(f"[SUCCESS] IPが新しくなりました: {new_ip}")
                    # PCプロキシとテザリング接続の安定化のために追加待機
                    print("[INFO] PCプロキシ接続の安定化を待機中 (5秒)...")
                    time.sleep(5)
                    return True
                else:
                    # まだ古いIPのまま（またはIPが変わらなかった）
                    print(f"  ({i+1}/30) 通信復旧しましたがIPは未変更です...")
            else:
                print(f"  ({i+1}/30) 通信復旧を待機中...")
        
        if new_ip == old_ip and old_ip is not None:
            print("[WARNING] 60秒経過しましたが、IPアドレスが変わりませんでした。")
            return False
            
        if new_ip:
            print(f"[SUCCESS] 通信が復旧しました（IP: {new_ip}）")
            # PCプロキシとテザリング接続の安定化のために追加待機
            print("[INFO] PCプロキシ接続の安定化を待機中 (5秒)...")
            time.sleep(5)
            return True
            
        print("[ERROR] 60秒待機しましたが、ネットワークが復旧しませんでした。")
        return False

    except subprocess.TimeoutExpired:
        print("[ERROR] ADBコマンドがタイムアウトしました。")
        return False
    except Exception as e:
        print(f"[ERROR] 実行中にエラーが発生しました: {e}")
        return False




if __name__ == "__main__":
    reset_mobile_data()