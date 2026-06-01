import json
from twitter_api.twitter_api import TwitterAPI
from typing import Tuple, Optional, Dict
from curl_cffi.requests import AsyncSession

import config
from config import outputLog

# ===== 認証情報 (DBが空の場合のフォールバック用) =====
AUTH_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

CSRF_TOKEN = "49e9c73594ba48c2180b2fdbaf7d0036cca9d38ac4e211f12dd64f33e1e970d4ae65bd3d902ec244d529f8fa0112e1ebb0ade0b352051113e2be8f82f74cfdb8e4feabce33eed23c00dd8b8029d6c38c"

COOKIES = 'guest_id_marketing=v1%3A176706367671646141; guest_id_ads=v1%3A176706367671646141; guest_id=v1%3A176706367671646141; personalization_id="v1_wXSND0yTktiS7pAu6IvwkA=="; __cuid=e42f0f34a59e4ea384a880c66c0b8c1c; g_state={"i_l":0,"i_ll":1767063691982,"i_b":"lkCGx/7QfnIH6q3XwrgvuAwjCGJMVlk8esr/uRLUXrU","i_e":{"enable_itp_optimization":0}}; kdt=KAwBXaUF1vf48Ktic2bJ6G1BpL4XvoF5E68UYIpY; auth_token=3fcdce5ff5771fb6641fd159e06f4825cb9dfcde; ct0=49e9c73594ba48c2180b2fdbaf7d0036cca9d38ac4e211f12dd64f33e1e970d4ae65bd3d902ec244d529f8fa0112e1ebb0ade0b352051113e2be8f82f74cfdb8e4feabce33eed23c00dd8b8029d6c38c; lang=ja; twid=u%3D1998751479008735232; external_referer=8e8t2xd8A2w%3D|0|F8C7rVpldvGNltGxuH%2ByoRY%2FzjrflHIZH061f%2B5OiIwP17ZTz34ZGg%3D%3D; __cf_bm=epRlez8KxZXvlSY.y76JbbFBC8DXeZUJUra5yPzJKSc-1767700141.4133637-1.0.1.1-AqT1AR3ck2nRfgf1KLW5RmbrjrGS.U3pA9Yc8fI8rLyy2P1rfScHWm0lSX5ggeIri.VveiNNS8xcSOwn9oNyrGtvIgbOF_xGkHwp_wDdJQoHezKJCbWFpLE5ykDki_zu' 
# ===== デフォルトツイートID（URLまたはIDを入力しない場合に使用） =====
DEFAULT_TWEET_ID = "2008834917497803068"

async def proc_like(credentials, exe_like , exe_bookmark, tweet_id: str = None):

    # Cookie
    session_cookies = credentials.get('cookies', {})

    if isinstance(session_cookies, str):
        session_cookies = json.loads(session_cookies)

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

    outputLog(results)

    if exe_like:
        return results['like'], ""

    return results['bookmark'], ""

# ===== ブラウザ環境設定 (Cookie取得元のブラウザに合わせて変更してください) =====
# 自動検出ロジックに使用されます
CURRENT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'

def detect_impersonate_target(ua_string: str) -> str:
    """User-Agent文字列から最適なimpersonateターゲットを判定する"""
    from twitter_api.user_agents import get_impersonate_for_ua

    return get_impersonate_for_ua(ua_string)
