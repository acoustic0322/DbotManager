import json
from twitter_api.twitter_api import TwitterAPI
from typing import Tuple, Optional, Dict
from curl_cffi.requests import AsyncSession
import random
import asyncio
import os
from typing import Optional
from twitter_api.tweet import Tweeter

import config
from config import outputLog

from .user_agents import get_ua_for_account, get_sec_ch_ua

from mysql import update_cookies
import re

# ===== 認証情報 (DBが空の場合のフォールバック用) =====
AUTH_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

CSRF_TOKEN = "49e9c73594ba48c2180b2fdbaf7d0036cca9d38ac4e211f12dd64f33e1e970d4ae65bd3d902ec244d529f8fa0112e1ebb0ade0b352051113e2be8f82f74cfdb8e4feabce33eed23c00dd8b8029d6c38c"

COOKIES = 'guest_id_marketing=v1%3A176706367671646141; guest_id_ads=v1%3A176706367671646141; guest_id=v1%3A176706367671646141; personalization_id="v1_wXSND0yTktiS7pAu6IvwkA=="; __cuid=e42f0f34a59e4ea384a880c66c0b8c1c; g_state={"i_l":0,"i_ll":1767063691982,"i_b":"lkCGx/7QfnIH6q3XwrgvuAwjCGJMVlk8esr/uRLUXrU","i_e":{"enable_itp_optimization":0}}; kdt=KAwBXaUF1vf48Ktic2bJ6G1BpL4XvoF5E68UYIpY; auth_token=3fcdce5ff5771fb6641fd159e06f4825cb9dfcde; ct0=49e9c73594ba48c2180b2fdbaf7d0036cca9d38ac4e211f12dd64f33e1e970d4ae65bd3d902ec244d529f8fa0112e1ebb0ade0b352051113e2be8f82f74cfdb8e4feabce33eed23c00dd8b8029d6c38c; lang=ja; twid=u%3D1998751479008735232; external_referer=8e8t2xd8A2w%3D|0|F8C7rVpldvGNltGxuH%2ByoRY%2FzjrflHIZH061f%2B5OiIwP17ZTz34ZGg%3D%3D; __cf_bm=epRlez8KxZXvlSY.y76JbbFBC8DXeZUJUra5yPzJKSc-1767700141.4133637-1.0.1.1-AqT1AR3ck2nRfgf1KLW5RmbrjrGS.U3pA9Yc8fI8rLyy2P1rfScHWm0lSX5ggeIri.VveiNNS8xcSOwn9oNyrGtvIgbOF_xGkHwp_wDdJQoHezKJCbWFpLE5ykDki_zu' 
# ===== デフォルトツイートID（URLまたはIDを入力しない場合に使用） =====
DEFAULT_TWEET_ID = "2008834917497803068"

async def proc_like(credentials, exe_like, exe_bookmark, tweet_id: str = None):

    # Cookie
    session_cookies = credentials.get('cookies', {})

    # 壊れたJSON補正 + dict化
    if isinstance(session_cookies, str):
        session_cookies = fix_broken_cookie_json(session_cookies)

    outputLog(type(session_cookies))
    outputLog(len(session_cookies))
    outputLog(session_cookies)

    # 念のため保険
    if not isinstance(session_cookies, dict):
        raise Exception(
            f"session_cookies is invalid. type={type(session_cookies)}"
        )

    outputLog(type(session_cookies))
    outputLog(len(session_cookies))

    # 接続情報
    target_proxy = credentials.get('proxy_url')

    detected_user_agent = (
        credentials.get('user_agent')
        or CURRENT_USER_AGENT
    )
    detected_browser = (
        credentials.get('impersonate')
        or detect_impersonate_target(detected_user_agent)
    )

    detected_ch = (
        credentials.get('sec_ch_ua')
        or '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
    )

    # CSRF
    csrf_token_val = (
        session_cookies.get('ct0')
        or CSRF_TOKEN
    )

    outputLog(f"[INFO] browser={detected_browser}")
    outputLog(f"[INFO] proxy={target_proxy or 'none'}")

    # API
    api = TwitterAPI(
        AUTH_TOKEN,
        csrf_token_val,
        session_cookies,
        proxy=target_proxy,
        user_agent=detected_user_agent,
        sec_ch_ua=detected_ch
    )

    async with AsyncSession(
        impersonate=detected_browser,
        cookies=session_cookies
    ) as session:

        results = await api.natural_action(
            tweet_id,
            session,
            do_like=exe_like,
            do_bookmark=exe_bookmark
        )

    # 戻り値のキーを補完
    results.setdefault("like", False)
    results.setdefault("like_reason", "")
    results.setdefault("bookmark", False)
    results.setdefault("bookmark_reason", "")    
    results.setdefault("retweet", False)
    results.setdefault("retweet_reason", "")    

    outputLog(results)

    return results

async def proc_repost(credentials, tweet_id: str = None):

    # Cookie
    session_cookies = credentials.get('cookies', {})

    # 壊れたJSON補正 + dict化
    if isinstance(session_cookies, str):
        session_cookies = fix_broken_cookie_json(session_cookies)

    outputLog(type(session_cookies))
    outputLog(len(session_cookies))
    outputLog(session_cookies)

    # 念のため保険
    if not isinstance(session_cookies, dict):
        raise Exception(
            f"session_cookies is invalid. type={type(session_cookies)}"
        )

    outputLog(type(session_cookies))
    outputLog(len(session_cookies))

    # 接続情報
    target_proxy = credentials.get('proxy_url')

    detected_user_agent = (
        credentials.get('user_agent')
        or CURRENT_USER_AGENT
    )
    detected_browser = (
        credentials.get('impersonate')
        or detect_impersonate_target(detected_user_agent)
    )

    detected_ch = (
        credentials.get('sec_ch_ua')
        or '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
    )

    # CSRF
    csrf_token_val = (
        session_cookies.get('ct0')
        or CSRF_TOKEN
    )

    outputLog(f"[INFO] browser={detected_browser}")
    outputLog(f"[INFO] proxy={target_proxy or 'none'}")

    # API
    api = TwitterAPI(
        AUTH_TOKEN,
        csrf_token_val,
        session_cookies,
        proxy=target_proxy,
        user_agent=detected_user_agent,
        sec_ch_ua=detected_ch
    )

    async with AsyncSession(
        impersonate=detected_browser,
        cookies=session_cookies
    ) as session:

        results = await api.natural_retweet_action(
            tweet_id,
            session
        )

    # 戻り値のキーを補完
    results.setdefault("like", False)
    results.setdefault("like_reason", "")
    results.setdefault("bookmark", False)
    results.setdefault("bookmark_reason", "")    
    results.setdefault("retweet", False)
    results.setdefault("retweet_reason", "")    

    outputLog(results)

    return results


#async def test_natural_retweet(tweet_id: str | None = None) -> dict[str, bool]:
#    tweet_id = tweet_id or DEFAULT_TWEET_ID
#    outputLog("\n" + "=" * 50)
#    outputLog("テスト: 自然フローRT")
#    outputLog("=" * 50)

#    ctx = build_runtime_context(load_first_account())
#    print_runtime_context(ctx)

#    async with AsyncSession(
#        impersonate=ctx["browser"],
#        cookies=ctx["cookies"],
#        proxies=ctx["proxies"],
#    ) as session:
#        results = await ctx["api"].natural_retweet_action(tweet_id, session)
#        results = await diagnose_failures(ctx, tweet_id, session, results)

#    save_cookies_if_needed(ctx)
#    log_failed_actions(ctx, tweet_id, results)
#    outputLog("\n結果:")
#    outputLog(f"  インプレッション: {'[OK] 成功' if results.get('impression') else '[NG] 失敗'}")
#    outputLog(f"  RT: {'[OK] 成功' if results.get('retweet') else '[NG] 失敗'}")
#    if results.get("retweet_wait_seconds") is not None:
#        outputLog(f"  RT待機: {results['retweet_wait_seconds']:.1f}s")
#    return results

def fix_broken_cookie_json(cookie_text):

    # ""abc"" → "abc"
    cookie_text = re.sub(
        r':\s*""([^"]*)""',
        r': "\1"',
        cookie_text
    )

    # g_state の中身をエスケープ
    m = re.search(
        r'"g_state"\s*:\s*"(\{.*?\})"',
        cookie_text
    )

    if m:
        g_state = m.group(1)

        escaped = (
            g_state
            .replace('\\', '\\\\')
            .replace('"', '\\"')
        )

        cookie_text = cookie_text.replace(
            f'"g_state": "{g_state}"',
            f'"g_state": "{escaped}"'
        )

    return json.loads(cookie_text)

# ===== ブラウザ環境設定 (Cookie取得元のブラウザに合わせて変更してください) =====
# 自動検出ロジックに使用されます
CURRENT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'

def detect_impersonate_target(ua_string: str) -> str:
    """User-Agent文字列から最適なimpersonateターゲットを判定する"""
    from twitter_api.user_agents import get_impersonate_for_ua

    return get_impersonate_for_ua(ua_string)


def normalize_proxy(proxy: Optional[str]) -> Optional[str]:
    if proxy and proxy.upper().startswith("SOCKS5://"):
        return proxy.replace("SOCKS5://", "socks5h://", 1)
    return proxy

async def proc_post(credentials):
    """特定アカウントのツイート投稿を処理する非同期タスク"""
    screen_name = credentials['account_name']
    
    # 複数アカウントが同時にスケジュールされた場合のタイミング分散（ジッター）
    delay = random.uniform(5.0, 20.0)
    print(f"[PROCESS] @{screen_name}: 同時実行防止のため {delay:.1f}秒 待機します...")
    await asyncio.sleep(delay)
    
#    sheet_name = acc.get('tweet_sheet_name')
#    print(f"[PROCESS] @{screen_name}: ツイート投稿を開始します...")
    
    # 最新のDB情報を取得して再確認
#    conn = db._get_conn()
#    cursor = conn.cursor()
#    cursor.execute("SELECT today_tweet_count, tweet_limit_count FROM accounts WHERE id = ?", (acc['id'],))
#    row = cursor.fetchone()
#    conn.close()
#    
#    today_count = acc.get('today_tweet_count', 0)
#    limit_count = acc.get('tweet_limit_count', 0)
#    if row:
#        today_count, limit_count = row
        
#    limit_count = get_max_limit_count(limit_count)
        
#    if today_count >= limit_count:
#        print(f"[SKIP] @{screen_name}: 本日のツイート上限 ({limit_count}回) に達しているため投稿をスキップします。")
#        return
        
    # 画像の選定
    image_path = None
    is_temporary = False

#    if random.random() < IMAGE_PROBABILITY:
#        print(f"[{screen_name}] 50%の判定：今回は【画像付き】でツイートします。")
#        image_path, is_temporary = get_random_image(IMAGE_DIR)
#    else:
#        print(f"[{screen_name}] 50%の判定：今回は【文章のみ】でツイートします。")
        
    try:

        current_cookies = credentials['cookies']

        if isinstance(current_cookies, str):
            current_cookies = json.loads(current_cookies)

        csrf_token = current_cookies.get("ct0", "")

#        current_cookies = credentials['cookies']
#        csrf_token = current_cookies.get("ct0", "")
        
        # User-Agentの設定
        user_agent, _imp = get_ua_for_account(int(credentials.get('id', 0)))
        sec_ch_ua = get_sec_ch_ua(user_agent)
        proxy = normalize_proxy(credentials.get('proxy_url'))
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # セッションの初期化
        async with AsyncSession(impersonate=_imp, cookies=current_cookies, proxies=proxies) as session:
            # Tweeterインスタンスの初期化
            tweeter = Tweeter(
                auth_token=AUTH_TOKEN,
                csrf_token=csrf_token,
                cookies=current_cookies,
                proxy=proxy,
                user_agent=user_agent,
                sec_ch_ua=sec_ch_ua
            )
            
            # ツイート内容をスプレッドシートからランダム取得
#            tweet_text = get_random_tweet_text(sheet_name)
            tweet_text = 'test'
            
            # 投稿実行
            success = await tweeter.post_tweet(
                text=tweet_text,
                session=session,
                image_path=image_path
            )

            updated_cookies = session.cookies.get_dict()

            if isinstance(tweeter.cookies, dict):
                updated_cookies.update(tweeter.cookies)

            if updated_cookies:
                final_cookies = current_cookies.copy()
                final_cookies.update(updated_cookies)
                update_cookies(credentials['id'], final_cookies)
                print(f"[DB] @{screen_name}: Cookieを更新しました")
            
            if success:
                new_count = today_count + 1
                print(f"[SUCCESS] @{screen_name}: ツイートの投稿に成功しました！")
                
                # DB側のカウントを更新（成功時はエラー詳細をクリア）
#                conn = db._get_conn()
#                cursor = conn.cursor()
#                cursor.execute("""
#                    UPDATE accounts 
#                    SET today_tweet_count = ?, last_action_time = ?, error_detail = NULL
#                    WHERE id = ?
#                """, (new_count, datetime.now(), acc['id']))
#                conn.commit()
#                conn.close()
                print(f"[DB] @{screen_name}: 更新完了: 本日のツイート数 = {new_count} (上限: {limit_count})")
            else:
                reason = getattr(tweeter, 'last_error_summary', '不明なエラー')
                diagnostics = getattr(tweeter, 'last_tweet_diagnostics', {})

#                append_failed_tweet_log(credentials, tweet_text, image_path, sheet_name, reason, diagnostics)
                append_failed_tweet_log(credentials, tweet_text, image_path, "sheet_name", reason, diagnostics)

                print(f"[DIAG] @{screen_name}: 失敗診断を failed_tweets.jsonl に保存しました")
                print(f"[FAILED] @{screen_name}: ツイートの投稿に失敗しました。 【原因: {reason}】")
                
                # DBのエラー詳細を更新
#                conn = db._get_conn()
#                cursor = conn.cursor()
#                cursor.execute("""
#                    UPDATE accounts 
#                    SET error_detail = ?, last_action_time = ?
#                    WHERE id = ?
#                """, (reason, datetime.now(), acc['id']))
#                conn.commit()
#                conn.close()
                
    except Exception as e:
        print(f"[ERROR] @{screen_name}: 投稿処理中にエラーが発生しました: {e}")
    finally:
        # クリーンアップ
        if is_temporary and image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"[CLEANUP] 一時フォールバック画像を削除しました: {image_path}")
            except Exception as e:
                print(f"[WARN] 一時フォールバック画像 {image_path} の削除に失敗しました: {e}")
