import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import ixBrowser_profile_manager
import x_login_manager
import threading
from concurrent.futures import ThreadPoolExecutor

# 設定ファイルのパス（ローカルフォルダ内のものを優先的に参照）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")
CREDS_PATH = os.path.join(CURRENT_DIR, "credentials.json")
# フォールバック (ドライブ上の設定が存在すればそちらも許容)
DRIVE_CONFIG_PATH = r"H:\マイドライブ\ixBrowser自動\config.json"
DRIVE_CREDS_PATH = r"H:\マイドライブ\ixBrowser自動\credentials.json"
if not os.path.exists(CONFIG_PATH) and os.path.exists(DRIVE_CONFIG_PATH):
    CONFIG_PATH = DRIVE_CONFIG_PATH
if not os.path.exists(CREDS_PATH) and os.path.exists(DRIVE_CREDS_PATH):
    CREDS_PATH = DRIVE_CREDS_PATH
API_BASE = "http://127.0.0.1:53200/api/v2"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    print("--- 新システム起動: スプレッドシートからのプロファイル読み込み ---")
    
    # 1. 設定の読み込み
    config = load_config()
    sheet_id = config.get("SHEET_ID")
    
    if not sheet_id:
        print("❌ config.json に SHEET_ID が設定されていません。")
        return

    # 対象のシート名を「非公式API情報」に固定
    worksheet_name = "非公式API情報"

    # 2. スプレッドシートへの接続
    print(f"🔗 スプレッドシートに接続中... (シート名: {worksheet_name})")
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
        all_rows = sheet.get_all_values()
    except Exception as e:
        print(f"❌ スプレッドシートの取得に失敗しました: {e}")
        return

    if not all_rows:
        print("⚠️ シートにデータがありません。")
        return

    # データ行の開始判定 (1行目がヘッダー文字列なら飛ばす)
    start_idx = 0
    if len(all_rows) > 0 and all_rows[0][0].lower() in ["username", "user", "アカウント"]:
        start_idx = 1
        print("ℹ️ 1行目はヘッダーと判定し、2行目から処理します。")
    
    data_rows = all_rows[start_idx:]
    print(f"✅ シート取得完了: {len(data_rows)}件のアカウントを処理します。")

    # 3. 各アカウントのプロファイルを検索・作成用のワーカー関数定義
    sheet_lock = threading.Lock()
    browser_launch_lock = threading.Lock()

    def process_row(i, row):
        row_num = i + 1 + start_idx
        
        # シートの列構成:
        # A(0): Username, B(1): Password, C(2): 2FA Key, D(3): auth_token, E(4): cookies, F(5): proxy, G(6): user_agent, H(7): sec_ch_ua, I(8): impersonate, J(9): status
        username   = row[0].strip() if len(row) > 0 else ""
        password   = row[1].strip() if len(row) > 1 else ""
        tfa_key    = row[2].strip() if len(row) > 2 else ""
        auth_token = row[3].strip() if len(row) > 3 else ""
        email      = "" # Emailカラムはないため空にします
        
        # グループIDはデフォルトを使用
        group_id = 250972
        
        # J列(9): ステータス
        status_j = row[9].strip() if len(row) > 9 else ""
        
        if not username:
            return
            
        # ステータスが成功/OKの場合はスキップ
        if status_j.upper() in ["OK", "成功", "SUCCESS"]:
            print(f"[{username}] 行:{row_num} ⏭️ J列が '{status_j}' のためスキップします。")
            return
            
        print(f"\n[{username}] 行:{row_num} の処理を開始...")
        print(f"  - Password: {'セット済' if password else 'なし'}")
        print(f"  - 2FA Key: {'セット済' if tfa_key else 'なし'}")
        print(f"  - auth_token: {'セット済' if auth_token else 'なし'}")
        
        try:
            # プロファイルの準備とブラウザの起動までをロックし、ixBrowser APIの同時呼び出し衝突を防群
            profile_id = None
            with browser_launch_lock:
                # ixBrowser_profile_managerを使用してプロファイルを取得または作成
                profile_id = ixBrowser_profile_manager.get_or_create_profile(
                    api_base=API_BASE,
                    username=username,
                    password=password,
                    tfa_key=tfa_key,
                    group_id=group_id
                )
                
                page = None
                if profile_id:
                    print(f"[{username}] プロファイル準備完了: {profile_id}")
                    
                    # --- ログイン処理の開始 ---
                    page, err_code = x_login_manager.open_ix_browser(API_BASE, profile_id)
                    
                    if not page:
                        print(f"[{username}] ❌ 起動失敗(エラー: {err_code})のため、処理を中断します。キャッシュ維持のためプロファイルは削除しません。")
                else:
                    print(f"[{username}] プロファイルの準備に失敗したためスキップします。")
                    try:
                        with sheet_lock:
                            sheet.update_cell(row_num, 10, "失敗")
                    except Exception:
                        pass
                    return

            # ロック解除後、ブラウザ自動操作は完全に並列で実行される
            success = False
            if page:
                success, new_cookies = x_login_manager.login_to_x(
                    page=page, 
                    username=username, 
                    password=password, 
                    tfa_key=tfa_key, 
                    email=email,
                    auth_token=auth_token
                )
                
                # スプレッドシートの更新 (D列 = 4列目: auth_token カラム, E列 = 5列目: cookies カラム)
                if success and new_cookies:
                    new_auth_token = new_cookies.get('auth_token', '')
                    cookie_json = json.dumps(new_cookies, ensure_ascii=False)
                    
                    # ブラウザのUser-Agentとimpersonateターゲットの自動検出
                    ua = ""
                    try:
                        ua = page.user_agent
                    except Exception:
                        pass
                    
                    # impersonate判定 (Chromeバージョンから)
                    imp = "chrome142"
                    ch = ""
                    if ua:
                        ua_lower = ua.lower()
                        if "chrome" in ua_lower:
                            import re
                            match = re.search(r'chrome/(\d+)', ua_lower)
                            if match:
                                ver_str = match.group(1)
                                ver = int(ver_str)
                                # バージョンに近い対応済みのimpersonateを選択
                                if ver >= 142:
                                    imp = "chrome142"
                                elif ver >= 136:
                                    imp = "chrome136"
                                elif ver >= 133:
                                    imp = "chrome133a"
                                elif ver >= 131:
                                    imp = "chrome131"
                                else:
                                    imp = "chrome142"  # 古すぎる場合は最新に合わせる
                                ch = f'"Chromium";v="{ver_str}", "Google Chrome";v="{ver_str}", "Not-A.Brand";v="99"'
                    
                    print(f"[{username}] 📝 クッキー、UA、impersonate情報をシートに保存します...")
                    try:
                        with sheet_lock:
                            sheet.update_cell(row_num, 4, new_auth_token)
                            sheet.update_cell(row_num, 5, cookie_json)
                            if ua:
                                sheet.update_cell(row_num, 7, ua)
                            if ch:
                                sheet.update_cell(row_num, 8, ch)
                            if imp:
                                sheet.update_cell(row_num, 9, imp)
                            sheet.update_cell(row_num, 10, "成功")
                    except Exception as e:
                        print(f"[{username}] ⚠️ シートのクッキー更新に失敗しました: {e}")
                else:
                    print(f"[{username}] ❌ ログイン処理に失敗しました。")
                    try:
                        with sheet_lock:
                            sheet.update_cell(row_num, 10, "失敗")
                    except Exception as e:
                        print(f"[{username}] ⚠️ シートの更新に失敗しました: {e}")
                
                # ブラウザを閉じる
                x_login_manager.close_ix_browser(API_BASE, profile_id, page)
            else:
                print(f"[{username}] ❌ ブラウザの起動に失敗したため処理を中断します。")
                try:
                    with sheet_lock:
                        sheet.update_cell(row_num, 10, "失敗")
                except Exception:
                    pass
        except Exception as e:
            print(f"[{username}] ❌ 例外エラーが発生しました: {e}")
            try:
                with sheet_lock:
                    sheet.update_cell(row_num, 10, "失敗")
            except Exception as e_sheet:
                print(f"[{username}] ⚠️ 例外発生時のシート更新に失敗しました: {e_sheet}")
            if 'profile_id' in locals() and profile_id:
                try:
                    x_login_manager.close_ix_browser(API_BASE, profile_id)
                except Exception:
                    pass

    # ThreadPoolExecutorによる並列実行
    max_workers = int(config.get("MAX_WORKERS", 2))
    print(f"🚀 並列数 {max_workers} で処理を開始します...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_row, i, row) for i, row in enumerate(data_rows)]
        # すべてのスレッドの終了を待つ
        for future in futures:
            future.result()

if __name__ == "__main__":
    main()
