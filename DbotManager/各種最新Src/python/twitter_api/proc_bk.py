import config
from config import outputLog

async def proc_like(credentials , tweet_id: str = None):
    """テスト3: 自然な行動フロー"""

#    print("\n" + "="*50)
#    print("テスト3: 自然な行動フロー（いいね + ブックマーク）")
#    print("="*50)
    
#    # DBからアカウント取得を試みる
#    from database import AccountDB
#    db = AccountDB()
#    accounts = db.get_active_accounts()
    print("test")
    print(credentials['cookies'])

    target_proxy = None
    target_account = None

    # DB利用 (最初の1件)
#    acc = accounts[0]
#    print(f"[User] DBのアカウントを使用: @{credentials['screen_name']}")
    session_cookies = credentials['cookies']
    target_proxy = credentials.get('proxy_url')
#    target_account = acc
        
    # User-Agent等
    detected_user_agent = credentials.get('user_agent') or CURRENT_USER_AGENT
    detected_browser = credentials.get('impersonate') or detect_impersonate_target(detected_user_agent)
        
    # sec_ch_ua 簡易生成 (DBになければ)
    detected_ch = credentials.get('sec_ch_ua')
    if not detected_ch:
        detected_ch = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'

    # CSRFトークン抽出
    csrf_token_val = session_cookies.get('ct0')
    if not csrf_token_val:
        # フォールバック
        csrf_token_val = CSRF_TOKEN

    print(f"[INFO] ブラウザ: {detected_browser}")
    if target_proxy:
        print(f"[INFO] プロキシ: {target_proxy}")
    else:
        print(f"[INFO] プロキシ: なし (直接接続)")
    
    # API初期化 
    # 【修正】Proxyを渡すように変更
    api = TwitterAPI(AUTH_TOKEN, csrf_token_val, session_cookies, proxy=target_proxy, user_agent=detected_user_agent, sec_ch_ua=detected_ch)
    print(f"アカウント速度: {api.account_speed}")
    
    async with AsyncSession(impersonate=detected_browser, cookies=session_cookies) as session:
        print("[INFO] 自然な行動フロー開始...")
        results = await api.natural_action(
            tweet_id,
            session,
            do_like=True,
            do_bookmark=True
        )
        
    print(f"\n結果:")
    print(f"  いいね: {'[OK] 成功' if results['like'] else '[NG] 失敗'}")
    print(f"  ブックマーク: {'[OK] 成功' if results['bookmark'] else '[NG] 失敗'}")
    
    # 【追加】CookieをDBに保存
    if api.cookies and target_account:
        account_id = target_account['id']
        # API内のCookie更新分をマージ
        target_account['cookies'].update(api.cookies)
        
        db.update_cookies(account_id, target_account['cookies'])
        print(f"[Saved] Cookieを自動更新しました (@{target_account['screen_name']})")
    
#    return results
    return True , ""


# ===== ブラウザ環境設定 (Cookie取得元のブラウザに合わせて変更してください) =====
# 自動検出ロジックに使用されます
CURRENT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'

def detect_impersonate_target(ua_string: str) -> str:
    """User-Agent文字列から最適なimpersonateターゲットを判定する"""
    from .user_agents import get_impersonate_for_ua
    return get_impersonate_for_ua(ua_string)