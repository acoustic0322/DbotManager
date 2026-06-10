import time
import random
import requests
import pyotp
from DrissionPage import ChromiumPage, ChromiumOptions
from ix_lock import ix_api_lock

def random_delay(min_sec=2, max_sec=4):
    time.sleep(random.uniform(min_sec, max_sec))

def safe_print(msg):
    print(msg)

def open_ix_browser(api_base, profile_id):
    """
    ixBrowserのプロファイルを起動し、DrissionPageのインスタンスを返す
    """
    safe_print(f"[{profile_id}] 🌐 ブラウザを起動しています...")
    try:
        res = None
        for launch_attempt in range(1, 4):
            with ix_api_lock:
                res = requests.post(f"{api_base}/profile-open", json={"profile_id": profile_id}, timeout=60).json()
            
            error_code = (res.get("error") or {}).get("code")
            # 1004 (Profile Open Failed) or 111003 (Already open) if we get these, force close and retry
            if error_code in [1004, 111003]:
                safe_print(f"[{profile_id}] ⚠️ 起動エラー検知 ({error_code}: {res.get('error', {}).get('message')}) -> クローズを要求して再試行します... ({launch_attempt}/3)")
                with ix_api_lock:
                    requests.post(f"{api_base}/profile-close", json={"profile_id": profile_id}, timeout=15)
                time.sleep(3)
                continue
            elif error_code == 2012:
                safe_print(f"[{profile_id}] ⚠️ クラウド同期中検知 (Error 2012) -> 5秒待機して再試行します... ({launch_attempt}/3)")
                time.sleep(5)
                continue
            else:
                break
        
        # カーネルバージョン不足 (2011) の場合の自動修復リトライ
        if (res.get("error") or {}).get("code") == 2011 or "kernel" in str(res).lower():
            safe_print(f"[{profile_id}] ⚠️ カーネル未検出 (Error 2011) → 強制バージョン(145)に更新してリトライします")
            try:
                with ix_api_lock:
                    requests.post(f"{api_base}/profile-update", json={
                        "profile_id": profile_id,
                        "fingerprint_config": {"kernel_version": 145}
                    }, timeout=20)
            except Exception as e_kernel:
                safe_print(f"[{profile_id}] ⚠️ カーネル更新エラー: {e_kernel}")
            
            time.sleep(2)
            # 再試行
            with ix_api_lock:
                res = requests.post(f"{api_base}/profile-open", json={"profile_id": profile_id}, timeout=60).json()
            
            # 再試行しても2011の場合は修復不可と判断してエラーコードを返す
            if (res.get("error") or {}).get("code") == 2011 or "kernel" in str(res).lower():
                safe_print(f"[{profile_id}] ❌ カーネル更新後も起動失敗 (Error 2011)。プロファイルの再作成が必要です。")
                return None, "KERNEL_2011"

        if not res.get("data"):
            safe_print(f"[{profile_id}] ❌ ブラウザ起動失敗: {res}")
            return None, "LAUNCH_FAILED"
        
        # debugger_addressの取得
        debugger_address = res.get("data", {}).get("ws", "")
        if not debugger_address:
            # IP:Port 形式で返ってくる場合もある
            ws_endpoint = res.get("data", {}).get("ws_endpoint", "")
            if ws_endpoint:
                # ws://127.0.0.1:XXXX/devtools/browser/... から 127.0.0.1:XXXX を抽出
                import re
                match = re.search(r"ws://(127\.0\.0\.1:\d+)", ws_endpoint)
                if match:
                    debugger_address = match.group(1)
            else:
                debugger_address = res.get("data", {}).get("debug_port", "")

        if not debugger_address:
            safe_print(f"[{profile_id}] ❌ Debugger Address が取得できませんでした: {res}")
            return None, "NO_DEBUGGER_ADDR"
            
        do = ChromiumOptions().set_address(debugger_address)
        page = None
        for attempt in range(1, 6):
            try:
                page = ChromiumPage(do)
                break
            except (IndexError, Exception) as e:
                if attempt == 5:
                    safe_print(f"[{profile_id}] ❌ ブラウザ接続試行タイムアウト ({attempt}/5): {e}")
                    raise e
                safe_print(f"[{profile_id}] ⏳ ブラウザの初期化完了を待っています... (試行 {attempt}/5: {e})")
                time.sleep(1.5)
                
        page.set.load_mode.normal()
        return page, None
    except Exception as e:
        safe_print(f"[{profile_id}] ❌ ブラウザ接続エラー: {e}")
        return None, str(e)

def close_ix_browser(api_base, profile_id, page=None):
    """
    ixBrowserのプロファイルを閉じる
    """
    if page:
        try:
            safe_print(f"[{profile_id}] 🌐 DrissionPageのブラウザプロセスを終了しています...")
            page.quit()
        except Exception as e:
            safe_print(f"[{profile_id}] ⚠️ page.quit() エラー: {e}")

    safe_print(f"[{profile_id}] 🛑 ixBrowserプロファイルを閉じています...")
    try:
        with ix_api_lock:
            requests.post(f"{api_base}/profile-close", json={"profile_id": profile_id}, timeout=15)
    except Exception as e:
        safe_print(f"[{profile_id}] ⚠️ ブラウザ終了エラー: {e}")

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def get_all_cookies_dict(page):
    """
    現在のブラウザセッションから全クッキーを辞書形式で取得する
    """
    try:
        cookies = page.cookies()
        if hasattr(cookies, 'as_dict'):
            return cookies.as_dict()
        cookie_dict = {}
        for cookie in cookies:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict
    except Exception as e:
        safe_print(f"⚠️ クッキー辞書取得エラー: {e}")
    return {}

def safe_input(element, text):
    """
    キーボードレイアウト（日本語入力モード等）の影響を受けないよう、
    JavaScriptで値を直接設定し、React等のフレームワーク用のイベントを発火させます。
    貼り付け(paste)イベントによる自動分配に対応するため、ClipboardEventもシミュレートします。
    """
    element.run_js('''
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(this, arguments[0]);
        this.dispatchEvent(new Event('input', {bubbles: true}));
        this.dispatchEvent(new Event('change', {bubbles: true}));
        
        try {
            const dt = new DataTransfer();
            dt.setData('text/plain', arguments[0]);
            const pasteEvent = new ClipboardEvent('paste', {
                bubbles: true,
                cancelable: true,
                clipboardData: dt
            });
            this.dispatchEvent(pasteEvent);
        } catch(e) {}
    ''', text)

def login_to_x(page, username, password, tfa_key, email="", auth_token=""):
    """
    X(Twitter)へのログイン処理。
    クッキーを優先し、失敗時はID/PW/2FAを使用。
    戻り値: (成功フラグ, 最新のCookie辞書)
    """
    try:
        # --- 0. すでにログイン済みかどうかの事前チェック ---
        safe_print(f"[{username}] 🌐 ログイン状態を確認しています...")
        page.get("https://x.com")
        random_delay(3, 4)
        if page.ele('css:[data-testid="AppTabBar_Home_Link"]', timeout=3) or \
           page.ele('css:[data-testid="SideNav_NewTweet_Button"]', timeout=1):
            safe_print(f"[{username}] ✅ すでにログイン済みであることを確認しました。")
            return True, get_all_cookies_dict(page)

        # --- 1. クッキー(auth_token)でのログイン試行 ---
        if auth_token:
            safe_print(f"[{username}] 🍪 クッキー(auth_token)でのログインを試行します...")
            
            # クッキーのセット
            page.set.cookies({'name': 'auth_token', 'value': auth_token, 'domain': '.x.com'})
            page.refresh()
            random_delay(3, 5)
            
            # ログイン成功判定 (Home等の要素があるか)
            if page.ele('css:[data-testid="AppTabBar_Home_Link"]', timeout=3) or \
               page.ele('css:[data-testid="SideNav_NewTweet_Button"]', timeout=1):
                safe_print(f"[{username}] ✅ クッキーでのログインに成功しました。")
                return True, get_all_cookies_dict(page)
            else:
                safe_print(f"[{username}] ⚠️ クッキーが無効、または期限切れです。通常のログインに切り替えます。")

        # --- 2. ID/PWでのログイン ---
        safe_print(f"[{username}] 🔑 ID/PWでのログインを開始します...")
        page.get("https://x.com/i/flow/login")
        random_delay(3, 5)


        # ユーザー名入力
        user_input = page.ele('css:input[autocomplete*="username"]', timeout=10) or \
                     page.ele('css:input[name="username_or_email"]', timeout=2)
        if not user_input:
            safe_print(f"[{username}] ❌ ユーザー名入力欄が見つかりません。")
            return False, ""
        
        safe_input(user_input, username)
        random_delay(1, 2)
        
        # 「次へ」ボタン
        next_btn = page.ele('css:button[type="submit"]') or \
                   page.ele('text=次へ') or \
                   page.ele('text=続ける') or \
                   page.ele('text=Next') or \
                   page.ele('css:[data-testid="ocfEnterTextNextButton"]')
        if next_btn:
            safe_print(f"[{username}] 「次へ」ボタンをクリックします...")
            next_btn.run_js('this.click()')
            try:
                user_input.input('\n')
            except Exception:
                pass
            random_delay(2, 3)

        # パスワード入力欄が表示されるまで待つ
        pass_input = page.ele('css:input[name="password"]', timeout=4)
        if not pass_input:
            # もしパスワード入力欄がなければ、メールアドレス/電話番号の確認画面が表示されているかチェック
            verify_input = page.ele('css:input[name="text"]', timeout=2) or \
                           page.ele('css:input[data-testid="ocfEnterTextTextInput"]', timeout=1)
            
            if verify_input:
                if not email:
                    safe_print(f"[{username}] ❌ メールアドレスまたは電話番号の確認が求められましたが、シートに Email がありません。")
                    return False, ""
                
                safe_print(f"[{username}] ⚠️ メールアドレスまたは電話番号の確認画面を検知しました。登録メールアドレス ({email}) を入力します...")
                safe_input(verify_input, email)
                random_delay(1, 2)
                
                verify_next_btn = page.ele('css:button[type="submit"]') or \
                                  page.ele('text=次へ') or \
                                  page.ele('text=続ける') or \
                                  page.ele('text=Next') or \
                                  page.ele('css:[data-testid="ocfEnterTextNextButton"]')
                if verify_next_btn:
                    safe_print(f"[{username}] 確認画面の「次へ」ボタンをクリックします...")
                    verify_next_btn.run_js('this.click()')
                    try:
                        verify_input.input('\n')
                    except Exception:
                        pass
                    random_delay(2, 3)
                
                # 再度パスワード入力欄を確認
                pass_input = page.ele('css:input[name="password"]', timeout=5)

        if not pass_input:
            safe_print(f"[{username}] ❌ パスワード入力欄が見つかりません。")
            return False, ""
            
        safe_input(pass_input, password)
        random_delay(1, 2)
        
        # 「ログイン」ボタン
        login_btn = page.ele('css:button[type="submit"]') or \
                    page.ele('css:[data-testid="LoginForm_Login_Button"]') or \
                    page.ele('text=ログイン') or \
                    page.ele('text=続ける') or \
                    page.ele('text=Log in')
        if login_btn:
            safe_print(f"[{username}] 「ログイン」ボタンをクリックします...")
            login_btn.run_js('this.click()')
            try:
                pass_input.input('\n')
            except Exception:
                pass
            random_delay(3, 5)

        # --- 3. 2FA または エラー判定 ---
        # ホーム画面に到達したか確認
        if page.ele('css:[data-testid="AppTabBar_Home_Link"]', timeout=3) or \
           page.ele('css:[data-testid="SideNav_NewTweet_Button"]', timeout=1):
            safe_print(f"[{username}] ✅ ID/PWでのログインに成功しました。")
            return True, get_all_cookies_dict(page)

        # 二段階認証(TOTP)コード入力欄の確認
        two_fa_input = page.ele('css:[data-testid="ocfEnterTextTextInput"]', timeout=5) or \
                       page.ele('css:input[name="text"]', timeout=1)
        
        two_fa_inputs_split = page.eles('css:input[id^="jf-code-input-challenge_response-"]')
        has_2fa = two_fa_input or (len(two_fa_inputs_split) > 0)
        
        if not has_2fa:
            # デバッグ用：見つからなかった場合に画面上のすべてのinput要素を探索して出力する
            safe_print(f"[{username}] ⚠️ 二段階認証入力欄が見つかりません。画面上のすべてのinput要素を調査します...")
            try:
                inputs = page.eles('tag:input')
                for idx, inp in enumerate(inputs):
                    attrs = inp.attrs
                    name = attrs.get('name', '')
                    typ = attrs.get('type', '')
                    testid = attrs.get('data-testid', '')
                    placeholder = attrs.get('placeholder', '')
                    autocomplete = attrs.get('autocomplete', '')
                    html_str = inp.html
                    safe_print(f"  Input #{idx}: name={name}, type={typ}, data-testid={testid}, placeholder={placeholder}, autocomplete={autocomplete}, html={html_str[:200]}")
            except Exception as e_debug:
                safe_print(f"  デバッグ調査中にエラー: {e_debug}")

        if has_2fa:
            if not tfa_key:
                safe_print(f"[{username}] ❌ 2FAが求められましたが、シートに2FA Keyがありません。")
                return False, ""
                
            safe_print(f"[{username}] 🔐 2FAコードを入力します...")
            try:
                totp = pyotp.TOTP(tfa_key)
                code = totp.now()
                
                if two_fa_input:
                    safe_input(two_fa_input, code)
                else:
                    safe_print(f"[{username}] ℹ️ 分割された2FA入力欄の1つ目にコード全体を入力します: {code}")
                    safe_input(two_fa_inputs_split[0], code)
                random_delay(1, 2)
                
                two_fa_next = page.ele('css:button[type="submit"]') or \
                              page.ele('css:[data-testid="ocfEnterTextNextButton"]') or \
                              page.ele('text=次へ') or \
                              page.ele('text=続ける') or \
                              page.ele('text=Next') or \
                              page.ele('css:button[class*="submit"]')
                if two_fa_next:
                    safe_print(f"[{username}] 2FAの送信ボタンをクリックします...")
                    two_fa_next.run_js('this.click()')
                    try:
                        if two_fa_input:
                            two_fa_input.input('\n')
                        elif len(two_fa_inputs_split) > 0:
                            two_fa_inputs_split[-1].input('\n')
                    except Exception:
                        pass
                    random_delay(4, 6)
            except Exception as e:
                safe_print(f"[{username}] ❌ 2FAコード生成・入力エラー: {e}")
                return False, ""

        # 最終確認
        if page.ele('css:[data-testid="AppTabBar_Home_Link"]', timeout=5) or \
           page.ele('css:[data-testid="SideNav_NewTweet_Button"]', timeout=1):
            safe_print(f"[{username}] ✅ 2FAを突破し、ログインに成功しました。")
            return True, get_all_cookies_dict(page)
            
        safe_print(f"[{username}] ❌ ログインできませんでした。パスワード違いや凍結の可能性があります。")
        return False, ""

    except Exception as e:
        safe_print(f"[{username}] ❌ ログイン処理中にエラーが発生しました: {e}")
        return False, ""

