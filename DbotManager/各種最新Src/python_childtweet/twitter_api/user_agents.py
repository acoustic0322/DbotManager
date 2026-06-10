"""
user_agents.py - 2026年最新UAリスト & impersonate選択ロジック
curl_cffi 0.14.0 の指紋に対応した、アカウントIDベースの決定論的UA割り当て
"""
import random
import re
from typing import Tuple

# =============================================================================
# iOS Safari (iPhone/iPad) 統合リスト
# =============================================================================
IOS_SAFARI_UAS = [
    # iOS 18系 (最新)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    # iOS 17系 (主力)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    # iOS 16/15系 (iPhone 8/X/11)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7.10 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.8.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7_9 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7.9 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
]

# =============================================================================
# Android Chrome 統合リスト
# =============================================================================
ANDROID_CHROME_UAS = [
    # Android 15/14 (Pixel 9, Galaxy S24)
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 8a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SH-51E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SO-51E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    # Android 13/12 (Xperia, Galaxy S21, AQUOS sense7)
    "Mozilla/5.0 (Linux; Android 13; SO-52D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SO-53C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SCG13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Android 11/10 (Galaxy S10, Xperia 5, AQUOS sense3)
    "Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SH-41A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SO-01M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SH-02M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    # 格安スマホ・中華系 (OPPO, Xiaomi)
    "Mozilla/5.0 (Linux; Android 14; CPH2523) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; 23127PN0CC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
]

# =============================================================================
# Desktop リスト (Windows/Mac Chrome/Safari/Firefox)
# =============================================================================
DESKTOP_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
]


def get_impersonate_for_ua(ua: str) -> str:
    """
    UA文字列から最適な curl_cffi impersonateターゲットを返す。
    curl_cffi 0.14.0 対応:
      safari180_ios, safari172_ios, safari17_2_ios, safari18_0_ios
      chrome131_android
      chrome142, chrome136, chrome133a, chrome131, safari184, firefox135
    """
    if not ua:
        return "chrome142"

    ua_lower = ua.lower()

    # --- iOS Safari ---
    if "iphone" in ua_lower or "ipad" in ua_lower:
        match = re.search(r'version/(\d+)', ua_lower)
        if match:
            ver = int(match.group(1))
            if ver >= 18:
                return "safari180_ios"
            elif ver >= 17:
                return "safari172_ios"
            else:
                return "safari17_2_ios"
        return "safari180_ios"

    # --- Android Chrome ---
    if "android" in ua_lower:
        return "chrome131_android"

    # --- Desktop Chrome ---
    if "chrome" in ua_lower and "safari" in ua_lower and "android" not in ua_lower:
        match = re.search(r'chrome/(\d+)', ua_lower)
        if match:
            ver = int(match.group(1))
            if ver >= 142:   return "chrome142"
            elif ver >= 136: return "chrome136"
            elif ver >= 133: return "chrome133a"
            elif ver >= 131: return "chrome131"
            else:            return "chrome142"
        return "chrome142"

    # --- Desktop Safari ---
    if "safari" in ua_lower and "chrome" not in ua_lower:
        return "safari184"

    # --- Firefox ---
    if "firefox" in ua_lower:
        return "firefox135"

    return "chrome142"


def get_ua_for_account(account_id: int) -> Tuple[str, str]:
    """
    アカウントIDに基づいて決定論的にUAとimpersonateターゲットを返す。
    同じアカウントIDなら常に同じUA/指紋を使う。

    Returns:
        (user_agent, impersonate_target)
    """
    random.seed(account_id)

    # アカウントIDの末尾2桁でデバイス種別を分散 (60% iOS, 30% Android, 10% Desktop)
    mod = account_id % 10
    if mod <= 5:      # 60% iOS Safari
        ua = random.choice(IOS_SAFARI_UAS)
    elif mod <= 8:    # 30% Android Chrome
        ua = random.choice(ANDROID_CHROME_UAS)
    else:             # 10% Desktop
        ua = random.choice(DESKTOP_UAS)

    random.seed()  # リセット

    imp = get_impersonate_for_ua(ua)
    return ua, imp


def get_sec_ch_ua(ua: str) -> str:
    """UA文字列からsec-ch-uaヘッダーを生成する（Chromeのみ対応、SafariはNone）"""
    if not ua:
        return None
    ua_lower = ua.lower()
    if "chrome" in ua_lower:
        match = re.search(r'chrome/(\d+)', ua_lower)
        ver = match.group(1) if match else "142"
        return f'"Chromium";v="{ver}", "Google Chrome";v="{ver}", "Not-A.Brand";v="99"'
    # Safari/Firefoxにはsec-ch-uaなし
    return None
