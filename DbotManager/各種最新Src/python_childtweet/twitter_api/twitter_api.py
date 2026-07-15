import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
import json
import base64
import os
import subprocess
import platform
import shutil
import urllib.request
import urllib.parse
import time
import threading
import re
from curl_cffi.requests import AsyncSession

import config
from config import outputLog



class TwitterAPI:
    """X (Twitter) の非公式API操作クラス"""
    _tid_server_lock = threading.Lock()
    _tid_query_lock = threading.Lock()
    _tid_server_disabled_until = 0.0
    _tid_server_ready = False
    _local_url_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    _graphql_operation_cache = {}

    FEATURES_TEMPLATE = {
        "rweb_video_screen_enabled": False,
        "profile_label_improvements_pcf_label_in_post_enabled": True,
        "responsive_web_profile_redirect_enabled": False,
        "rweb_tipjar_consumption_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "premium_content_api_read_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
        "responsive_web_grok_analyze_post_followups_enabled": True,
        "responsive_web_jetfuel_frame": True,
        "responsive_web_grok_share_attachment_enabled": True,
        "articles_preview_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "responsive_web_grok_show_grok_translated_post": False,
        "responsive_web_grok_analysis_button_from_backend": True,
        "creator_subscriptions_quote_tweet_preview_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_grok_image_annotation_enabled": True,
        "responsive_web_grok_imagine_annotation_enabled": True,
        "responsive_web_grok_community_note_auto_translation_is_enabled": False,
        "responsive_web_enhance_cards_enabled": False,
    }
    
    def __init__(self, auth_token: str, csrf_token: str, cookies: Union[str, Dict[str, str]], proxy: Optional[str] = None, user_agent: Optional[str] = None, sec_ch_ua: Optional[str] = None):
        """
        初期化
        
        Args:
            auth_token: Bearer認証トークン
            csrf_token: CSRFトークン
            cookies: Cookie文字列 または 辞書
            proxy: プロキシURL (オプション)
            user_agent: User-Agent文字列
            sec_ch_ua: sec-ch-uaヘッダー文字列
        """
        self.auth_token = auth_token
        self.csrf_token = csrf_token
        self.proxy = proxy
        
        self.server_process = None

        # Cookieのパース
        self.cookies = {}
        parsed_cookies = {}
        if cookies:
            if isinstance(cookies, dict):
                parsed_cookies = {str(k): str(v) for k, v in cookies.items() if v is not None}
            else:
                try:
                    # まず単純な split でパース（http.cookiesは厳格すぎる場合があるため）
                    for pair in cookies.split(';'):
                        if '=' in pair:
                            key, val = pair.strip().split('=', 1)
                            parsed_cookies[key.strip()] = val.strip()
                except Exception as e:
                    outputLog(f"[WARN] Cookie parse error in init: {type(e).__name__}: {e}")
                    parsed_cookies = {}

        # すべてのクッキーを保持（手動ブラウザセッションと完全に一致させるため、フィルタリングを廃止）
        self.cookies = parsed_cookies
        
        # 必須Cookieのログ確認（デバッグ用）
        # if 'auth_token' not in self.cookies:
        #     outputLog("[WARN] auth_token missing in initialized cookies")

        # User-Agent設定 (デフォルトはChrome 142に合わせる)
        # ユーザーからUAが渡された場合はそれを優先し、CHもそこから生成する
        self.user_agent = user_agent if user_agent else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
        
        if sec_ch_ua:
            self.sec_ch_ua = sec_ch_ua
        else:
            self.sec_ch_ua = self._generate_sec_ch_ua(self.user_agent)

        # セッション管理（通知対策）
        self.session_id = base64.b64encode(os.urandom(16)).decode('utf-8')  # セッション識別子
        self.base_transaction_id = base64.b64encode(os.urandom(72)).decode('utf-8')  # ベースTransaction ID
        self.transaction_counter = 0  # 同一セッション内での操作カウンター
        
        # アカウントの個性を設定
        self.account_speed = random.choice(['slow', 'normal', 'fast'])
        self.speed_multiplier = {
            'slow': 1.5,
            'normal': 1.0,
            'fast': 0.7
        }[self.account_speed]
        
        # ステータス管理
        self.status = 'active'
        self.last_action_time = None
        self.pause_until = None
        
        # レート制限検知
        self.rate_limit_count = 0
        self.last_error_summary = None
        self.last_summary_type = None
        
        # Node.jsサーバー管理
        self._ensure_tid_server_running()

    def _generate_sec_ch_ua(self, user_agent: str) -> Optional[str]:
        """User-Agent文字列から適切なsec-ch-uaヘッダーを生成する"""
        try:
            import re
            ua = user_agent.lower()
            if "chrome" in ua:
                match = re.search(r'chrome/(\d+)', ua)
                ver = match.group(1) if match else "124"
                return f'"Not:A-Brand";v="99", "Google Chrome";v="{ver}", "Chromium";v="{ver}"'
            elif "edg/" in ua or "edge/" in ua:
                match = re.search(r'(?:edg|edge)/(\d+)', ua)
                ver = match.group(1) if match else "124"
                return f'"Chromium";v="{ver}", "Microsoft Edge";v="{ver}", "Not-A.Brand";v="99"'
            else:
                 # Safari や iOS 等、Chrome/Edge以外は sec-ch-ua を送らないようにする
                 return None
        except:
            return None


    def _ensure_tid_server_running(self):
        """Node.js TIDサーバーが起動しているか確認し、なければ起動する"""
        def is_server_ready(timeout=2.0):
            try:
                with TwitterAPI._local_url_opener.open("http://127.0.0.1:3000/status", timeout=timeout) as response:
                    return response.status == 200
            except Exception:
                return False

        with TwitterAPI._tid_server_lock:
            if is_server_ready(timeout=0.5):
                TwitterAPI._tid_server_ready = True
                return

            TwitterAPI._tid_server_ready = False
                
            outputLog("[System] Starting Node.js TID Server...")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, 'tid_node', 'server.js')
            node_path = shutil.which('node')
            if not node_path:
                bundled_node = os.path.join(current_dir, 'tools', 'node-v24.16.0-win-x64', 'node.exe')
                if os.path.exists(bundled_node):
                    node_path = bundled_node
            if not node_path:
                raise RuntimeError("Node.js executable not found. Install Node.js or add node.exe to PATH.")
            
            # 独立したプロセスとして起動
            creationflags = 0
            if platform.system() == 'Windows':
                creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)

            # サーバー起動 (デバッグ用にログをファイルに出力)
            log_path = os.path.join(current_dir, 'tid_node', 'server.log')
            try:
                log_file = open(log_path, 'a', encoding='utf-8')
            except Exception:
                log_file = subprocess.DEVNULL

            self.server_process = subprocess.Popen(
                [node_path, script_path],
                stdout=log_file,
                stderr=log_file,
                creationflags=creationflags,
                env={**os.environ, "NODE_TLS_REJECT_UNAUTHORIZED": "0"}
            )
            
            # 起動待機
            for _ in range(20):
                if self.server_process.poll() is not None:
                    raise RuntimeError(f"Node.js TID Server exited early with code {self.server_process.returncode}. See tid_node/server.log")
                if is_server_ready(timeout=0.5):
                    TwitterAPI._tid_server_ready = True
                    outputLog("[System] Node.js TID Server started.")
                    return
                time.sleep(0.5)
            raise RuntimeError("Node.js TID Server did not become ready. See tid_node/server.log")
    def _get_language_headers(self) -> Dict[str, str]:
        """Cookieのlangパラメータに基づいて適切な言語ヘッダーを取得する"""
        lang = self.cookies.get('lang', 'ja') if isinstance(self.cookies, dict) else 'ja'
        lang_short = lang.split('-')[0].lower() if lang else 'ja'
        
        # 主要言語のマッピング
        mappings = {
            'ja': ('ja-JP,ja;q=0.9', 'ja'),
            'en': ('en-US,en;q=0.9', 'en'),
            'es': ('es-ES,es;q=0.9', 'es'),
            'pt': ('pt-BR,pt;q=0.9', 'pt'),
            'zh': ('zh-CN,zh;q=0.9', 'zh'),
            'ko': ('ko-KR,ko;q=0.9', 'ko'),
            'fr': ('fr-FR,fr;q=0.9', 'fr'),
            'de': ('de-DE,de;q=0.9', 'de'),
            'it': ('it-IT,it;q=0.9', 'it'),
            'ru': ('ru-RU,ru;q=0.9', 'ru'),
        }
        
        accept_lang, client_lang = mappings.get(lang_short, (f"{lang_short}-{lang_short.upper()},{lang_short};q=0.9", lang_short))
        return {
            'accept-language': accept_lang,
            'x-twitter-client-language': client_lang
        }

# (既存の _get_language_headers の終わり)

    def _build_full_headers(self, referer: str = None, transaction_id: str = None, extra_headers: Dict = None) -> Dict:
        """全メソッド共通のヘッダー生成窓口"""
        lang = self._get_language_headers()
        headers = {
            'authorization': self.auth_token,
            'x-csrf-token': self.csrf_token,
            'content-type': 'application/json',
            'accept': '*/*',
            'accept-language': lang['accept-language'],
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': lang['x-twitter-client-language'],
            'origin': 'https://x.com',
            'priority': 'u=1, i',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
        }
        
        # 動的な値の注入
        if referer: headers['referer'] = referer
        if transaction_id: headers['x-client-transaction-id'] = transaction_id
        
        # Sec-CH-UAロジックを一括適用
        if self.sec_ch_ua:
            headers['sec-ch-ua'] = self.sec_ch_ua
            mobile = self._sec_ch_ua_mobile()
            platform = self._sec_ch_ua_platform()
            if mobile: headers['sec-ch-ua-mobile'] = mobile
            if platform: headers['sec-ch-ua-platform'] = platform
            
        if extra_headers: headers.update(extra_headers)
        return headers

    def _get_headers(self, extra_headers: Dict = None) -> Dict:
        """レガシーな呼び出し元への互換性保持"""
        return self._build_full_headers(extra_headers=extra_headers)
    
    def _generate_transaction_id(self) -> str:
        """ユニークなTransaction IDを生成（レガシー用）"""
        return base64.b64encode(os.urandom(72)).decode('utf-8')
    
    def _generate_session_transaction_id(self) -> str:
        """セッション一貫性のあるTransaction IDを生成（通知対策）"""
        self.transaction_counter += 1
        base_bytes = base64.b64decode(self.base_transaction_id)
        counter_bytes = self.transaction_counter.to_bytes(4, byteorder='big')
        modified_bytes = base_bytes[:-4] + counter_bytes
        return base64.b64encode(modified_bytes).decode('utf-8')
    
    def get_cookie_dict(self) -> Dict[str, str]:
        """Cookie辞書を返す"""
        return self.cookies

    def _format_cookie_header(self) -> str:
        """Cookie dict/stringをHTTPヘッダー用の文字列へ正規化する"""
        if not self.cookies:
            return ""
        if isinstance(self.cookies, dict):
            return "; ".join(f"{k}={v}" for k, v in self.cookies.items() if v is not None)
        return str(self.cookies)

    def _normalized_proxy(self) -> Optional[str]:
        """curl_cffiで扱いやすいproxy URLへ正規化する"""
        if not self.proxy:
            return None
        if self.proxy.upper().startswith('SOCKS5://'):
            return self.proxy.replace('SOCKS5://', 'socks5h://', 1)
        return self.proxy

    def _response_preview(self, response, limit: int = 500) -> str:
        """HTTP失敗時に見やすい本文プレビューを返す"""
        try:
            text = response.text
        except Exception:
            text = ""
        if not text:
            return ""
        text = text.replace("\r", "\\r").replace("\n", "\\n")
        return text[:limit]

    def _log_http_failure(self, label: str, url: str, response) -> None:
        """HTTP失敗をURL・status・本文つきで表示する"""
        preview = self._response_preview(response)
        outputLog(f"[WARN] {label} failed: status={response.status_code} url={url}")
        header_keys = [
            'content-type',
            'x-transaction-id',
            'x-response-time',
            'x-rate-limit-remaining',
            'x-rate-limit-reset'
        ]
        header_parts = []
        for key in header_keys:
            value = response.headers.get(key)
            if value:
                header_parts.append(f"{key}={value}")
        if header_parts:
            outputLog(f"[WARN] {label} headers: {', '.join(header_parts)}")
        if preview:
            outputLog(f"[WARN] {label} response: {preview}")

    def _classify_api_failure(
        self,
        status_code: Optional[int],
        response_body: str = "",
        error_message: str = ""
    ) -> tuple[str, str]:
        """Return (summary_type, summary_text)."""

        body = response_body or ""
        message = error_message or ""
        combined = f"{message} {body}".lower()

        code_match = re.search(r'"code"\s*:\s*(\d+)', body)
        code = code_match.group(1) if code_match else None

        status_part = f"HTTP {status_code}" if status_code else "HTTP unknown"
        code_part = f" code={code}" if code else ""
        msg_part = f" message={message}" if message and message != "No error message" else ""

        if status_code == 401 or code == "32" or any(
            token in combined for token in (
                "could not authenticate",
                "not authorized",
                "invalid or expired token"
            )
        ):
            return "TOKEN_EXPIRED_OR_INVALID", \
                f"TOKEN_EXPIRED_OR_INVALID | {status_part}{code_part}{msg_part}"

        if code == "326" or any(
            token in combined for token in (
                "locked",
                "account is temporarily locked",
                "challenge",
                "verify your account"
            )
        ):
            return "ACCOUNT_LOCKED_OR_CHALLENGE_REQUIRED", \
                f"ACCOUNT_LOCKED_OR_CHALLENGE_REQUIRED | {status_part}{code_part}{msg_part}"

        if code == "64" or any(
            token in combined for token in (
                "suspended",
                "deactivated",
                "offboarded"
            )
        ):
            return "ACCOUNT_SUSPENDED_DEACTIVATED_OR_OFFBOARDED", \
                f"ACCOUNT_SUSPENDED_DEACTIVATED_OR_OFFBOARDED | {status_part}{code_part}{msg_part}"

        if status_code == 429 or code == "88":
            return "RATE_LIMITED", \
                f"RATE_LIMITED | {status_part}{code_part}{msg_part}"

        if code == "226":
            return "SPAM_OR_AUTOMATION_DETECTED", \
                f"SPAM_OR_AUTOMATION_DETECTED | {status_part}{code_part}{msg_part}"

        if code == "344":
            return "POST_LIMIT_OR_COOKIE_DEGRADED", \
                f"POST_LIMIT_OR_COOKIE_DEGRADED | {status_part}{code_part}{msg_part}"

        if status_code == 403:
            return "FORBIDDEN_OR_PERMISSION_DENIED", \
                f"FORBIDDEN_OR_PERMISSION_DENIED | {status_part}{code_part}{msg_part}"

        if status_code == 404:
            return "ENDPOINT_OR_OPERATION_NOT_FOUND", \
                f"ENDPOINT_OR_OPERATION_NOT_FOUND | {status_part}{code_part}{msg_part}"

        if msg_part:
            return "API_ERROR", \
                f"API_ERROR | {status_part}{code_part}{msg_part}"

        preview = " ".join(body[:240].split())
        return "UNKNOWN_API_ERROR", \
            f"UNKNOWN_API_ERROR | {status_part}{code_part} preview={preview}"

    def _detect_account_lock_marker(self, body: str = "", url: str = "") -> Optional[str]:
        """Return a lock/challenge label when a read-only page clearly shows account access gates."""
        url_lower = (url or "").lower()
        body_lower = (body or "").lower()
        if "account/access" in url_lower:
            return "account/access"

        strong_markers = (
            "account is locked",
            "temporarily locked",
            "unlock your account",
            "verify your account",
            "account has been locked",
            "your account has been locked",
            "challenge_required",
            "challenge required",
            "arkose",
            "アカウントはロック",
            "ロックされています",
            "本人確認",
            "認証が必要",
        )
        for marker in strong_markers:
            if marker in body_lower:
                return marker
        return None

    async def probe_account_lock_state(self, session: AsyncSession) -> Dict[str, object]:
        """Read-only probe for account lock/challenge pages without sending actions."""
        probes = (
            ("home_html", "https://x.com/home"),
            ("account_access", "https://x.com/account/access"),
        )
        headers = self._build_full_headers(
            referer="https://x.com/home",
            extra_headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
            },
        )

        for label, url in probes:
            try:
                response = await session.get(
                    url,
                    headers=headers,
                    proxy=self._normalized_proxy(),
                    timeout=30,
                    allow_redirects=True,
                )
                final_url = str(getattr(response, "url", url))
                text = response.text or ""
                marker = self._detect_account_lock_marker(text[:12000], final_url if label == "home_html" else "")
                if marker:
                    reason = (
                        "ACCOUNT_LOCKED_OR_CHALLENGE_REQUIRED | "
                        f"read-only probe={label} HTTP {response.status_code} marker={marker}"
                    )
                    self.last_error_summary = reason
                    return {
                        "locked": True,
                        "reason": reason,
                        "probe": label,
                        "status_code": response.status_code,
                        "url": final_url,
                    }
            except Exception as exc:
                return {
                    "locked": None,
                    "reason": f"ACCOUNT_LOCK_PROBE exception: {type(exc).__name__}: {exc}",
                    "probe": label,
                    "status_code": None,
                    "url": url,
                }

        return {
            "locked": False,
            "reason": None,
            "probe": "home_html/account_access",
            "status_code": None,
            "url": None,
        }

    def _sec_ch_ua_mobile(self) -> Optional[str]:
        ua_lower = (self.user_agent or "").lower()
        if not self.sec_ch_ua:
            return None
        return "?1" if ("android" in ua_lower or "mobile" in ua_lower) else "?0"

    def _sec_ch_ua_platform(self) -> Optional[str]:
        ua_lower = (self.user_agent or "").lower()
        if not self.sec_ch_ua:
            return None
        if "android" in ua_lower:
            return '"Android"'
        if "macintosh" in ua_lower:
            return '"macOS"'
        return '"Windows"'
    
    def is_paused(self) -> bool:
        """アカウントが一時停止中かチェック"""
        if self.pause_until and datetime.now() < self.pause_until:
            return True
        return False
    
    def pause_account(self, hours: float = 2):
        """アカウントを一時停止"""
        self.status = 'paused'
        self.pause_until = datetime.now() + timedelta(hours=hours)
        outputLog(f"[PAUSE] アカウント一時停止: {hours}時間")
    
    async def _wait_natural(self, base_min: float = 1.0, base_max: float = 3.0):
        """人間らしい待機時間（ロングテール追加）"""
        long_tail_prob = 0.07  # 7%の確率で長い滞在
        
        if random.random() < long_tail_prob:
            # たまにじっくり滞在（対数正規分布）
            wait_time = random.lognormvariate(mu=1.8, sigma=0.9)
        else:
            # 通常の揺らぎ
            wait_time = random.uniform(base_min, base_max)
        
        wait_time *= self.speed_multiplier
        
        # 深夜はさらに操作間隔を空ける
        hour = datetime.now().hour
        if 2 <= hour <= 6:
            wait_time *= 1.8
            
        await asyncio.sleep(max(wait_time, 0.3))

    def _extract_thread_tweet_ids(self, detail_data: Dict, focal_tweet_id: str, limit: int = 6) -> List[str]:
        """Extract tweet ids shown in a TweetDetail conversation, preserving order."""
        root = detail_data.get("data", {}).get("threaded_conversation_with_injections_v2", {})
        seen = set()
        ids: List[str] = []

        def add(tweet_id: object) -> None:
            value = str(tweet_id) if tweet_id is not None else ""
            if value.isdigit() and value not in seen:
                seen.add(value)
                ids.append(value)

        add(focal_tweet_id)

        def walk(node: object) -> None:
            if len(ids) >= limit:
                return
            if isinstance(node, dict):
                legacy = node.get("legacy")
                typename = node.get("__typename")
                rest_id = node.get("rest_id")
                if (
                    rest_id
                    and isinstance(legacy, dict)
                    and ("full_text" in legacy or "id_str" in legacy)
                    and typename in {None, "Tweet", "TweetWithVisibilityResults"}
                ):
                    add(rest_id)

                if isinstance(legacy, dict):
                    add(legacy.get("id_str"))

                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(root)
        return ids[:limit]
    
    async def view_tweet(self, tweet_id: str, session: AsyncSession) -> tuple[Optional[str], dict]:
        """ツイートを閲覧し、スクリーンネームとメディア情報を返す"""
        media_info = {"has_video": False, "has_image": False, "author_id": "0"}
        try:
            url = "https://x.com/i/api/graphql/sMoYQ8oNKf7pyC3ILopasw/TweetDetail"
            variables = {
                "focalTweetId": tweet_id,
                "with_rux_injections": False,
                "rankingMode": "Relevance",
                "includePromotedContent": True,
                "withCommunity": True,
                "withQuickPromoteEligibilityTweetFields": True,
                "withBirdwatchNotes": True,
                "withVoice": True,
            }
            features = self.FEATURES_TEMPLATE.copy()
            field_toggles = {
                "withArticleRichContentState": True,
                "withArticlePlainText": False,
                "withGrokAnalyze": False,
                "withDisallowedReplyControls": False,
            }
            params = {
                "variables": json.dumps(variables),
                "features": json.dumps(features),
                "fieldToggles": json.dumps(field_toggles),
            }

            response = await session.get(
                url,
                headers=self._get_headers(),
                params=params,
                proxy=self._normalized_proxy(),
                timeout=30,
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.last_detail_tweet_ids = self._extract_thread_tweet_ids(data, tweet_id)
                    if len(self.last_detail_tweet_ids) > 1:
                        outputLog(f"[THREAD] collected {len(self.last_detail_tweet_ids)} tweet ids from detail")

                    entries = data.get("data", {}).get("threaded_conversation_with_injections_v2", {}).get("instructions", [])
                    for instruction in entries:
                        if instruction.get("type") != "TimelineAddEntries":
                            continue
                        for entry in instruction.get("entries", []):
                            if entry.get("entryId") != f"tweet-{tweet_id}":
                                continue
                            content = entry.get("content", {}).get("itemContent", {})
                            tweet_result = content.get("tweet_results", {}).get("result", {})
                            if not tweet_result:
                                self.last_error_summary = (
                                    "TWEET_DETAIL_EMPTY_RESULT | HTTP 200 but tweet_results.result is empty; "
                                    "request/viewer-specific TweetDetail empty result"
                                )
                                continue
                            legacy = (
                                tweet_result.get("legacy", {})
                                or tweet_result.get("core", {}).get("legacy", {})
                                or tweet_result.get("tweet", {}).get("legacy", {})
                            )
                            user_result = (
                                tweet_result.get("core", {}).get("user_results", {}).get("result", {})
                                or tweet_result.get("tweet", {}).get("core", {}).get("user_results", {}).get("result", {})
                            )
                            screen_name = (
                                user_result.get("core", {}).get("screen_name")
                                or user_result.get("legacy", {}).get("screen_name")
                            )
                            media_info["author_id"] = user_result.get("rest_id") or "0"

                            media_list = legacy.get("extended_entities", {}).get("media", [])
                            for item in media_list:
                                media_type = item.get("type")
                                if media_type in {"video", "animated_gif"}:
                                    media_info["has_video"] = True
                                elif media_type == "photo":
                                    media_info["has_image"] = True

                            if screen_name:
                                outputLog(f"[DEBUG] screen_name取得成功: @{screen_name}, Media: {media_info}")
                                self.last_error_summary = None
                                self.last_summary_type = None
                                return screen_name, media_info
                except Exception as exc:
                    self.last_error_summary = f"TWEET_DETAIL parse exception: {type(exc).__name__}: {exc}"
                    outputLog(f"[WARN] {self.last_error_summary}")
                return "Unknown", media_info

            if response.status_code == 429:
                self.rate_limit_count += 1

                #self.last_error_summary = f"TWEET_DETAIL {self._classify_api_failure(response.status_code, self._response_preview(response), '')}"
                summary_type, summary_text = self._classify_api_failure(
                    response.status_code,
                    self._response_preview(response)
                )
                self.last_summary_type = summary_type
                self.last_error_summary = f"TWEET_DETAIL | {summary_text}"

                if self.rate_limit_count >= 3:
                    self.pause_account(hours=2)
                return None, media_info

            try:
                response_text = response.text or ""
            except Exception:
                response_text = ""

#            self.last_error_summary = f"TWEET_DETAIL {self._classify_api_failure(response.status_code, response_text, '')}"
            summary_type, summary_text = self._classify_api_failure(
                response.status_code,
                response_text
            )
            self.last_summary_type = summary_type
            self.last_error_summary = f"TWEET_DETAIL | {summary_text}"

            self._log_http_failure("TWEET_DETAIL", url, response)
            return None, media_info
        except Exception as exc:
            self.last_error_summary = f"TWEET_DETAIL exception: {type(exc).__name__}: {exc}"
            outputLog(f"[WARN] {self.last_error_summary}")
            return None, media_info


    def _find_tweet_legacy_in_detail(self, detail_data: Dict, tweet_id: str) -> Optional[Dict]:
        """TweetDetail responseから対象ツイートのlegacy dictを探す。"""
        target = str(tweet_id)

        def walk(value):
            if isinstance(value, dict):
                legacy = value.get("legacy") if isinstance(value.get("legacy"), dict) else None
                rest_id = str(value.get("rest_id") or "")
                legacy_id = str((legacy or {}).get("id_str") or "")
                if legacy and (rest_id == target or legacy_id == target):
                    return legacy
                for child in value.values():
                    found = walk(child)
                    if found is not None:
                        return found
            elif isinstance(value, list):
                for child in value:
                    found = walk(child)
                    if found is not None:
                        return found
            return None

        return walk(detail_data)

    async def verify_tweet_engagement_state(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> Dict[str, Optional[bool]]:
        """POST結果が不明なとき、TweetDetail上のいいね/ブクマ状態を確認する。"""
        state: Dict[str, Optional[bool]] = {"favorited": None, "bookmarked": None}
        try:
            url = "https://x.com/i/api/graphql/sMoYQ8oNKf7pyC3ILopasw/TweetDetail"
            variables = {
                "focalTweetId": str(tweet_id),
                "with_rux_injections": False,
                "rankingMode": "Relevance",
                "includePromotedContent": True,
                "withCommunity": True,
                "withQuickPromoteEligibilityTweetFields": True,
                "withBirdwatchNotes": True,
                "withVoice": True,
            }
            field_toggles = {
                "withArticleRichContentState": True,
                "withArticlePlainText": False,
                "withGrokAnalyze": False,
                "withDisallowedReplyControls": False,
            }
            response = await session.get(
                url,
                headers=self._get_headers({"referer": referer}),
                params={
                    "variables": json.dumps(variables, separators=(",", ":")),
                    "features": json.dumps(self.FEATURES_TEMPLATE.copy(), separators=(",", ":")),
                    "fieldToggles": json.dumps(field_toggles, separators=(",", ":")),
                },
                proxy=self._normalized_proxy(),
                timeout=30,
            )
            if response.status_code != 200:
                self._log_http_failure("ENGAGEMENT_VERIFY", url, response)
                return state
            legacy = self._find_tweet_legacy_in_detail(response.json(), str(tweet_id)) or {}
            if "favorited" in legacy:
                state["favorited"] = bool(legacy.get("favorited"))
            if "bookmarked" in legacy:
                state["bookmarked"] = bool(legacy.get("bookmarked"))
            elif "bookmarked_by" in legacy:
                state["bookmarked"] = bool(legacy.get("bookmarked_by"))
            outputLog(f"[ENGAGEMENT_VERIFY] tweet_id={tweet_id} favorited={state['favorited']} bookmarked={state['bookmarked']}")
            return state
        except Exception as exc:
            outputLog(f"[ENGAGEMENT_VERIFY] exception: {type(exc).__name__}: {exc}")
            return state

    async def fetch_user_profile(self, screen_name: str, session: AsyncSession) -> bool:
        """ユーザープロフィールを取得"""
        try:
            url = "https://x.com/i/api/graphql/-oaLodhGbbnzJBACb1kk2Q/UserByScreenName"
            variables = {"screen_name": screen_name, "withGrokTranslatedBio": False}
            features = self.FEATURES_TEMPLATE.copy()
            features.update({
                "hidden_profile_subscriptions_enabled": True,
                "subscriptions_verification_info_is_identity_verified_enabled": True,
                "subscriptions_verification_info_verified_since_enabled": True,
                "highlights_tweets_tab_ui_enabled": True,
                "responsive_web_twitter_article_notes_tab_enabled": True,
                "subscriptions_feature_can_gift_premium": True,
            })
            field_toggles = {"withPayments": False, "withAuxiliaryUserLabels": True}

            response = await session.get(
                url,
                headers=self._get_headers(),
                params={
                    "variables": json.dumps(variables),
                    "features": json.dumps(features),
                    "fieldToggles": json.dumps(field_toggles),
                },
                proxy=self._normalized_proxy(),
                timeout=30,
            )
            if response.status_code == 200:
                return True
            try:
                response_text = response.text or ""
            except Exception:
                response_text = ""

            #self.last_error_summary = f"USER_PROFILE {self._classify_api_failure(response.status_code, response_text, '')}"
            summary_type, summary_text = self._classify_api_failure(
                response.status_code,
                response_text
            )
            self.last_summary_type = summary_type
            self.last_error_summary = f"USER_PROFILE | {summary_text}"            

            self._log_http_failure("USER_PROFILE", url, response)
            return False
        except Exception as exc:
            self.last_error_summary = f"USER_PROFILE exception: {type(exc).__name__}: {exc}"
            outputLog(f"[PROFILE] Exception: {type(exc).__name__}")
            return False
    async def _execute_via_native_curl(self, url: str, payload: str, referer: str, 
                                       success_keyword: Union[str, List[str]] = '"Done"', 
                                       transaction_id: str = None, 
                                       session: AsyncSession = None) -> Dict[str, any]:
        """GraphQL POST実行（curl_cffi使用・簡略化版）"""
        try:
            if not transaction_id:
                self.last_error_summary = "TID取得失敗"
                outputLog(f"[WARN] {self.last_error_summary}")
                return {'success': False, 'cookies': {}, 'error_type': 'TID Error', 'error_message': self.last_error_summary}

            # 共通ヘッダーを使用（これがメインの簡略化ポイント）
            headers_dict = self._build_full_headers(
                referer=referer, 
                transaction_id=transaction_id
            )
            headers_dict['content-type'] = 'application/json'

            # Cookie追加
            cookie_header = self._format_cookie_header()
            if cookie_header:
                headers_dict['cookie'] = cookie_header

            # 実行
            try:
                if session:
                    r = await session.post(
                        url, 
                        headers=headers_dict, 
                        data=payload, 
                        proxy=self._normalized_proxy(), 
                        timeout=30
                    )
                else:
                    # フォールバック
                    from curl_cffi.requests import AsyncSession
                    impersonate_target = "chrome"  # 簡易フォールバック
                    async with AsyncSession(impersonate=impersonate_target) as s:
                        r = await s.post(
                            url, 
                            headers=headers_dict, 
                            data=payload, 
                            cookies=self.cookies, 
                            proxy=self._normalized_proxy(), 
                            timeout=30
                        )
                
                stdout_text = f"HTTP/2 {r.status_code}\r\n{r.text}"
                returncode = 0

            except Exception as e:
                self.last_error_summary = f"Request exception: {str(e)}"
                outputLog(f"[WARN] {self.last_error_summary}")
                return {'success': False, 'cookies': {}, 'error_type': 'Exception', 'error_message': str(e)}

            # 成功判定
            success_keywords = success_keyword if isinstance(success_keyword, list) else [success_keyword]
            is_success = any(kw in stdout_text for kw in success_keywords)
            is_already_done = '"code":139' in stdout_text

            if (is_success or is_already_done):
                # Cookie更新
                new_cookies = {}
                for line in stdout_text.splitlines():
                    if line.lower().strip().startswith('set-cookie:'):
                        try:
                            parts = line.split(':', 1)[1].strip()
                            cookie_part = parts.split(';', 1)[0].strip()
                            if '=' in cookie_part:
                                k, v = cookie_part.split('=', 1)
                                new_cookies[k.strip()] = v.strip()
                        except:
                            pass
                if new_cookies:
                    self.cookies.update(new_cookies)
                self.last_error_summary = None
                self.last_summary_type = None
                return {'success': True, 'cookies': new_cookies}

            # 失敗時
            self._log_http_failure("API", url, r)

            #error_summary = self._classify_api_failure(r.status_code, r.text or "")
            #self.last_error_summary = error_summary
            summary_type, summary_text = self._classify_api_failure(
                r.status_code,
                r.text or ""
            )

            self.last_summary_type = summary_type
            self.last_error_summary = summary_text

            outputLog(f"[ERROR(type)] {summary_type}")
            outputLog(f"[ERROR(text)] {summary_text}")

            return {
                'success': False,
                'cookies': {},
                'error_type': 'API_ERROR',
                'error_message': summary_text,
                'response_body': (r.text or "")[:500]
            }

        except Exception as e:
            self.last_error_summary = f"Execution exception: {str(e)}"
            outputLog(f"[WARN] _execute_via_native_curl: {self.last_error_summary}")
            return {'success': False, 'cookies': {}, 'error_type': 'Exception', 'error_message': str(e)}

    async def _generate_dynamic_transaction_id(self, path: str, method: str = 'POST', purpose: str = 'api') -> Optional[str]:
        """Node.jsサーバーから用途別にTID取得"""
        try:
            if time.time() < TwitterAPI._tid_server_disabled_until:
                outputLog(f"[WARN] {purpose} Node.js TID cooldown; fallback transaction id for {method} {path}")
                return self._generate_session_transaction_id()

            await asyncio.to_thread(self._ensure_tid_server_running)
            account_twid = self.cookies.get("twid", "") if isinstance(self.cookies, dict) else ""
            params = urllib.parse.urlencode({
                'path': path,
                'method': method,
                'ua': self.user_agent or '',
                'ch': self.sec_ch_ua or '',
                'mobile': self._sec_ch_ua_mobile() or '',
                'platform': self._sec_ch_ua_platform() or '',
                'twid': account_twid
            })
            url = f"http://127.0.0.1:3000/tid?{params}"
            local_headers = {"x-x-cookie": self._format_cookie_header()} if self.cookies else {}
            
            def fetch_tid_sync():
                with TwitterAPI._tid_query_lock:
                    for attempt in range(1, 4):
                        try:
                            request = urllib.request.Request(url, headers=local_headers)
                            with TwitterAPI._local_url_opener.open(request, timeout=8) as response:
                                if response.status == 200:
                                    tid_value = response.read().decode('utf-8').strip()
                                    if tid_value:
                                        return tid_value
                                outputLog(f"[WARN] TID Server Query returned HTTP {response.status} (attempt {attempt}/3)")
                        except Exception as e:
                            outputLog(f"[WARN] TID Server Query Error (attempt {attempt}/3): {e}")
                        time.sleep(0.35 * attempt)
                    return None
            
            tid = await asyncio.to_thread(fetch_tid_sync)
            if tid:
                return tid
            TwitterAPI._tid_server_ready = False
            await asyncio.to_thread(self._ensure_tid_server_running)
            tid = await asyncio.to_thread(fetch_tid_sync)
            if tid:
                return tid
            TwitterAPI._tid_server_disabled_until = time.time() + 600
            fallback_tid = self._generate_session_transaction_id()
            outputLog(f"[WARN] {purpose} Node.js TID failed; falling back to session transaction id for {method} {path}")
            return fallback_tid
        except Exception as e:
            outputLog(f"[WARN] Node.js TID Error: {e}")
            self.last_error_summary = f"{purpose} TID取得失敗: {type(e).__name__}: {e}"
            return None

    async def _generate_tweet_transaction_id(self, path: str, method: str = 'POST') -> Optional[str]:
        """投稿系API用のTID取得。いいね/ブクマ系とはログと失敗扱いを分ける。"""
        return await self._generate_dynamic_transaction_id(path, method, purpose='TWEET')

    async def _generate_engagement_transaction_id(self, path: str, method: str = 'POST') -> Optional[str]:
        """いいね/ブクマ系API用のTID取得。疑似TIDへフォールバックしない。"""
        return await self._generate_dynamic_transaction_id(path, method, purpose='ENGAGEMENT')

    async def _generate_media_transaction_id(self, path: str, method: str = 'POST') -> Optional[str]:
        """メディアアップロード用のTID取得。"""
        return await self._generate_dynamic_transaction_id(path, method, purpose='MEDIA')

    async def _generate_client_event_transaction_id(self, path: str, method: str = 'POST') -> Optional[str]:
        """jot/client_event用のTID取得。"""
        return await self._generate_dynamic_transaction_id(path, method, purpose='CLIENT_EVENT')

    async def retweet_tweet(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> bool:
        """指定ツイートを単独でRT（リポスト）する。"""
        if self.is_paused(): return False
        if "status" not in referer: referer = f"https://x.com/i/status/{tweet_id}"

        query_id = await self._resolve_graphql_operation("CreateRetweet", session, "/home")
        if not query_id:
            self.last_error_summary = "RETWEET query id not resolved; set X_QUERY_ID_CREATE_RETWEET"
            outputLog(f"[RETWEET] {self.last_error_summary}")
            return False

        path = f"/i/api/graphql/{query_id}/CreateRetweet"
        url = f"https://x.com{path}"
        payload = json.dumps({
            "variables": {
                "tweet_id": str(tweet_id),
                "dark_request": False,
            },
            "queryId": query_id,
        }, separators=(",", ":"))

        outputLog("[Processing] Generating TID via Node.js...")
        tid = await self._generate_engagement_transaction_id(path, 'POST')
        if not tid:
            return False

        result = await self._execute_via_native_curl(
            url,
            payload,
            referer,
            ['"retweet":"Done"', '"create_retweet":"Done"', '"retweeted":true', '"retweet_results"'],
            tid,
            session,
        )
        if result['cookies']:
            for k, v in result['cookies'].items():
                session.cookies.set(k, v, domain=".x.com")
        return result['success']
    async def bookmark_tweet(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> bool:
        if self.is_paused(): return False
        query_id = await self._resolve_graphql_operation("CreateBookmark", session, "/home")
        if not query_id:
            self.last_error_summary = "BOOKMARK query id not resolved; set X_QUERY_ID_CREATE_BOOKMARK"
            outputLog(f"[BOOKMARK] {self.last_error_summary}")
            return False

        path = f"/i/api/graphql/{query_id}/CreateBookmark"
        url = f"https://x.com{path}"
        payload = json.dumps({
            "variables": {"tweet_id": str(tweet_id)},
            "queryId": query_id
        }, separators=(",", ":"))
        outputLog("[Processing] Generating TID via Node.js...")
        tid = await self._generate_engagement_transaction_id(path, "POST")
        if not tid:
            return False
        result = await self._execute_via_native_curl(url, payload, referer, "\"tweet_bookmark_put\":\"Done\"", tid, session)
        if result['cookies']:
            for k, v in result['cookies'].items():
                session.cookies.set(k, v, domain=".x.com")
        if result['success']:
            return True

        original_summary = self.last_error_summary
        await asyncio.sleep(random.uniform(3.0, 6.0))
        state = await self.verify_tweet_engagement_state(tweet_id, session, referer=referer)
        if state.get("bookmarked") is True:
            self.last_error_summary = None
            self.last_summary_type = None
            outputLog(f"[BOOKMARK] POST result was uncertain, but TweetDetail shows bookmarked=true: {tweet_id}")
            return True
        self.last_error_summary = original_summary or self.last_error_summary
        return False

    async def like_tweet(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> bool:
        if self.is_paused(): return False
        if "status" not in referer: referer = f"https://x.com/i/status/{tweet_id}"
        url = "https://x.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet"
        
        # 辞書型として定義し、管理を容易にする
        payload_data = {
            "variables": {
                "tweet_id": str(tweet_id)
            },
            "features": self.FEATURES_TEMPLATE.copy(),
            "queryId": "lI07N6Otwv1PhnEgXILM7A"
        }
        # 空白なしのJSON文字列に自動変換（Xの要求仕様に合わせる）
        payload = json.dumps(payload_data, separators=(',', ':'))
        
        outputLog("[Processing] Generating TID via Node.js...")
        tid = await self._generate_engagement_transaction_id('/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet', 'POST')
        if not tid:
            return False
        result = await self._execute_via_native_curl(url, payload, referer, '"favorite_tweet":"Done"', tid, session)
        if result['cookies']:
            for k, v in result['cookies'].items():
                session.cookies.set(k, v, domain=".x.com")
        if result['success']:
            return True

        original_summary = self.last_error_summary
        await asyncio.sleep(random.uniform(3.0, 6.0))
        state = await self.verify_tweet_engagement_state(tweet_id, session, referer=referer)
        if state.get("favorited") is True:
            self.last_error_summary = None
            self.last_summary_type = None
            outputLog(f"[LIKE] POST result was uncertain, but TweetDetail shows favorited=true: {tweet_id}")
            return True
        self.last_error_summary = original_summary or self.last_error_summary
        return False
    
    def _timeline_features(self) -> Dict:
        """SearchTimelineなどで使用するfeature flags（FEATURES_TEMPLATEをベースに調整）"""
        # 共通テンプレートをベースに使用
        features = self.FEATURES_TEMPLATE.copy()
        
        # SearchTimeline特有の差分を上書き
        features.update({
            "rweb_cashtags_enabled": True,
            "rweb_tipjar_consumption_enabled": False,
            "rweb_cashtags_composer_attachment_enabled": True,
            "responsive_web_grok_annotations_enabled": True,
            "rweb_conversational_replies_downvote_enabled": False,
            "longform_notetweets_inline_media_enabled": False,
            "responsive_web_grok_community_note_auto_translation_is_enabled": True,
            "responsive_web_grok_show_grok_translated_post": True,
        })
        return features

    @staticmethod
    def _json_contains_tweet_id(value, tweet_id: str) -> bool:
        """GraphQL応答内に対象ツイートIDが存在するか再帰的に確認する。"""
        target = str(tweet_id)
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"rest_id", "id_str", "tweet_id"} and str(item) == target:
                    return True
                if TwitterAPI._json_contains_tweet_id(item, target):
                    return True
        elif isinstance(value, list):
            return any(TwitterAPI._json_contains_tweet_id(item, target) for item in value)
        return False

    @staticmethod
    def _find_bottom_cursor(value) -> Optional[str]:
        """Timeline応答から次ページ用Bottom cursorを取得する。"""
        if isinstance(value, dict):
            if value.get("cursorType") == "Bottom" and value.get("value"):
                return str(value["value"])
            for item in value.values():
                cursor = TwitterAPI._find_bottom_cursor(item)
                if cursor:
                    return cursor
        elif isinstance(value, list):
            for item in value:
                cursor = TwitterAPI._find_bottom_cursor(item)
                if cursor:
                    return cursor
        return None

    async def _resolve_graphql_operation(
        self,
        operation_name: str,
        session: AsyncSession,
        bootstrap_path: str,
    ) -> Optional[str]:
        """環境変数またはX配信JSからGraphQL Query IDを解決する。"""
        env_key = f"X_QUERY_ID_{re.sub(r'(?<!^)(?=[A-Z])', '_', operation_name).upper()}"
        configured = (os.getenv(env_key) or "").strip()
        if configured:
            return configured
        cached = self._graphql_operation_cache.get(operation_name)
        if cached:
            return cached

        bootstrap_url = urllib.parse.urljoin("https://x.com", bootstrap_path)
        page_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": self._get_language_headers()["accept-language"],
            "cache-control": "no-cache",
            "referer": "https://x.com/",
            "user-agent": self.user_agent,
        }
        script_headers = {
            "accept": "*/*",
            "accept-language": self._get_language_headers()["accept-language"],
            "referer": bootstrap_url,
            "user-agent": self.user_agent,
        }
        try:
            response = await session.get(
                bootstrap_url,
                headers=page_headers,
                proxy=self._normalized_proxy(),
                timeout=30,
            )
            if response.status_code != 200:
                outputLog(f"[ROUTE] {operation_name} bootstrap failed: HTTP {response.status_code}")
                return None
            html = response.text or ""
            sources = [html]
            script_urls = []
            for src in re.findall(r'<script[^>]+src=["\']([^"\']+)', html):
                url = urllib.parse.urljoin(bootstrap_url, src)
                if url not in script_urls:
                    script_urls.append(url)
            for start in range(0, min(len(script_urls), 24), 6):
                batch = script_urls[start:start + 6]
                fetched = await asyncio.gather(
                    *[
                        session.get(
                            url,
                            headers=script_headers,
                            proxy=self._normalized_proxy(),
                            timeout=30,
                        )
                        for url in batch
                    ],
                    return_exceptions=True,
                )
                for item in fetched:
                    if not isinstance(item, Exception) and item.status_code == 200:
                        sources.append(item.text or "")

            escaped_name = re.escape(operation_name)
            patterns = (
                rf'queryId\s*:\s*["\']([A-Za-z0-9_-]+)["\']\s*,\s*operationName\s*:\s*["\']{escaped_name}["\']',
                rf'operationName\s*:\s*["\']{escaped_name}["\']\s*,\s*queryId\s*:\s*["\']([A-Za-z0-9_-]+)["\']',
                rf'queryId\s*:\s*["\']([A-Za-z0-9_-]+)["\'][^{{}}]{{0,1200}}operationName\s*:\s*["\']{escaped_name}["\']',
                rf'operationName\s*:\s*["\']{escaped_name}["\'][^{{}}]{{0,1200}}queryId\s*:\s*["\']([A-Za-z0-9_-]+)["\']',
            )
            for source in sources:
                for pattern in patterns:
                    match = re.search(pattern, source)
                    if match:
                        query_id = match.group(1)
                        self._graphql_operation_cache[operation_name] = query_id
                        outputLog(f"[ROUTE] Resolved {operation_name} query id")
                        return query_id
        except Exception as exc:
            outputLog(f"[ROUTE] {operation_name} discovery failed: {type(exc).__name__}: {exc}")

        outputLog(f"[ROUTE] {operation_name} query id not found; set {env_key} to override")
        return None

    async def _fetch_timeline_operation(
        self,
        operation_name: str,
        variables: Dict,
        tweet_id: str,
        session: AsyncSession,
        referer: str,
        bootstrap_path: str,
        max_pages: int = 1,
    ) -> bool:
        """タイムラインを最大max_pagesまで取得し、対象ツイートの存在を確認する。"""
        query_id = await self._resolve_graphql_operation(operation_name, session, bootstrap_path)
        if not query_id:
            return False

        path = f"/i/api/graphql/{query_id}/{operation_name}"
        url = f"https://x.com{path}"
        current_variables = dict(variables)

        try:
            for page in range(1, max(1, max_pages) + 1):
                tid = await self._generate_dynamic_transaction_id(
                    path,
                    "GET",
                    purpose=operation_name.upper(),
                )
                if not tid:
                    return False

                params = {
                    "variables": json.dumps(current_variables, separators=(",", ":")),
                    "features": json.dumps(self._timeline_features(), separators=(",", ":")),
                }
                response = await session.get(
                    url,
                    headers=self._get_headers({
                        "referer": referer,
                        "user-agent": self.user_agent,
                        "x-client-transaction-id": tid,
                    }),
                    params=params,
                    proxy=self._normalized_proxy(),
                    timeout=30,
                )
                if response.status_code != 200:
                    self._log_http_failure(operation_name, url, response)
                    return False

                data = response.json()
                found = self._json_contains_tweet_id(data, tweet_id)
                outputLog(f"[ROUTE] {operation_name}: page={page} target_found={found}")
                if found:
                    return True

                if page >= max_pages:
                    break

                cursor = self._find_bottom_cursor(data)
                if not cursor:
                    outputLog(f"[ROUTE] {operation_name}: no bottom cursor")
                    break
                current_variables["cursor"] = cursor
                outputLog(f"[ROUTE] {operation_name}: loading page {page + 1}")

            return False
        except Exception as exc:
            outputLog(f"[ROUTE] {operation_name} failed: {type(exc).__name__}: {exc}")
            return False

    async def fetch_search_timeline(self, tweet_id: str, session: AsyncSession) -> bool:
        """投稿者指定の検索タイムラインから対象ツイートを取得する。"""
        screen_name, _ = await self.view_tweet(tweet_id, session)
        if not screen_name or screen_name == "Unknown":
            outputLog("[ROUTE] SearchTimeline skipped: tweet author could not be resolved")
            return False

        # --- 検索クエリの分散化 ---
        search_patterns = [
            f"from:{screen_name}",
            f"@{screen_name}",
            screen_name
        ]
        query = random.choice(search_patterns)
        # --------------------------
        self.last_search_query = query
        encoded_query = urllib.parse.quote(query)
        referer = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"
        return await self._fetch_timeline_operation(
            "SearchTimeline",
            {
                "rawQuery": query,
                "count": 20,
                "querySource": "typed_query",
                "product": "Latest",
                "withGrokTranslatedBio": False,
                "withQuickPromoteEligibilityTweetFields": False,
            },
            tweet_id,
            session,
            referer,
            f"/search?q={encoded_query}&src=typed_query&f=live",
            max_pages=2,
        )

    async def fetch_home_timeline(self, session: AsyncSession, tweet_id: Optional[str] = None) -> bool:
        """ホームタイムライン取得 (Warm-up)"""
        try:
            url = "https://x.com/i/api/graphql/edseUwk9sP5Phz__9TIRnA/HomeTimeline"
            variables = {"count": 20, "includePromotedContent": True, "requestContext": "ptr", "withCommunity": True}
            
            # FEATURES_TEMPLATEを使用（一元管理）
            features = self.FEATURES_TEMPLATE.copy()
            
            params = {'variables': json.dumps(variables), 'features': json.dumps(features)}
            response = await session.get(url, headers=self._get_headers(), params=params, proxy=self._normalized_proxy(), timeout=30)
            
            if response.status_code == 200:
                if tweet_id is not None:
                    found = self._json_contains_tweet_id(response.json(), tweet_id)
                    outputLog(f"[HOME] target_found={found} tweet_id={tweet_id}")
                    return found
                self.last_error_summary = None
                self.last_summary_type = None
                outputLog("[HOME] ホームタイムライン取得成功 (Warm-up)")
                return True

            try:
                response_text = response.text or ""
            except Exception:
                response_text = ""

            #self.last_error_summary = f"HOME_TIMELINE {self._classify_api_failure(response.status_code, response_text)}"
            summary_type, summary_text = self._classify_api_failure(
                response.status_code,
                response_text
            )
            self.last_summary_type = summary_type
            self.last_error_summary = f"HOME_TIMELINE | {summary_text}"

            self._log_http_failure("HOME_TIMELINE", url, response)
            return False
        except Exception as e:
            self.last_error_summary = f"HOME_TIMELINE exception: {type(e).__name__}: {e}"
            outputLog(f"[HOME] Exception: {type(e).__name__}: {e}")
            return False
    async def send_client_event_log(
        self,
        tweet_id: str,
        session: AsyncSession,
        referer: str = "https://x.com/home",
        *,
        page: str = "tweet",
        include_stream_results: bool = True,
        include_bottom: bool = True,
        author_id: str = "0",
    ) -> bool:
        """実際の閲覧経路で発生したclient_eventだけを送信する。"""
        if self.is_paused():
            return False

        now_ms = int(time.time() * 1000)
        start_ms = now_ms - random.randint(1000, 1800)
        client_name = "m5" if ("mobile" in self.user_agent.lower() or "iphone" in self.user_agent.lower() or "ipad" in self.user_agent.lower() or "android" in self.user_agent.lower()) else "web"
        base_item = {
            "item_type": 0,
            "id": tweet_id,
            "author_id": author_id,
            "is_viewer_follows_tweet_author": False,
            "is_tweet_author_follows_viewer": False,
            "is_viewer_super_following_tweet_author": False,
            "is_viewer_super_followed_by_tweet_author": False,
            "is_tweet_author_super_followable": False,
            "engagement_metrics": {
                "reply_count": 0,
                "retweet_count": 0,
                "favorite_count": 0,
                "quote_count": 0
            }
        }
        log_data = []
        if include_stream_results:
            log_data.append({
                "_category_": "client_event",
                "format_version": 2,
                "triggered_on": now_ms,
                "items": [{**base_item, "position": 0, "sort_index": "1", "percent_screen_height_100k": 31346}],
                "event_namespace": {
                    "page": page,
                    "component": "stream",
                    "action": "results",
                    "client": client_name
                },
                "client_event_sequence_start_timestamp": start_ms,
                "client_event_sequence_number": 10,
                "client_app_id": "3033300"
            })

        if include_bottom:
            log_data.append({
                "_category_": "client_event",
                "format_version": 2,
                "triggered_on": now_ms + random.randint(50, 250),
                "tweet_id": tweet_id,
                "items": [base_item],
                "event_namespace": {
                    "page": page,
                    "action": "bottom",
                    "client": client_name
                },
                "client_event_sequence_start_timestamp": start_ms,
                "client_event_sequence_number": 11 if include_stream_results else 10,
                "client_app_id": "3033300"
            })

        if not log_data:
            self.last_error_summary = "IMPRESSION skipped: no client events for the selected route"
            outputLog(f"[IMPRESSION] {self.last_error_summary}")
            return False
        payload = urllib.parse.urlencode({
            "debug": "true",
            "log": json.dumps(log_data, separators=(",", ":"))
        })

        candidates = [
            ("https://x.com/i/api/1.1/jot/client_event.json?keepalive=true", "/i/api/1.1/jot/client_event.json"),
            ("https://api.twitter.com/1.1/jot/client_event.json?keepalive=true", "/1.1/jot/client_event.json"),
        ]

        event_names = [
            "/".join(filter(None, (
                event["event_namespace"].get("page"),
                event["event_namespace"].get("component"),
                event["event_namespace"].get("action"),
            )))
            for event in log_data
        ]
        event_label = ", ".join(event_names)
        outputLog(f"[IMPRESSION] Sending {event_label} for tweet_id: {tweet_id}")
        for url, path in candidates:
            try:
                tid = await self._generate_client_event_transaction_id(path, 'POST')
                if not tid:
                    self.last_error_summary = self.last_error_summary or f"IMPRESSION TID取得失敗: {path}"
                    outputLog(f"[WARN] IMPRESSION skipped: {self.last_error_summary}")
                    continue
                
                # tidが確定した後にヘッダーを構築する
                headers_dict = self._build_full_headers(
                    referer=referer,
                    transaction_id=tid,
                    extra_headers={"content-type": "application/x-www-form-urlencoded"},
                )
                response = await session.post(
                    url,
                    headers=headers_dict,
                    data=payload,
                    proxy=self._normalized_proxy(),
                    timeout=30
                )
                if response.status_code in [200, 204]:
                    outputLog(f"[IMPRESSION] OK status={response.status_code} url={url}")
                    self.last_error_summary = None
                    self.last_summary_type = None
                    return True

                self._log_http_failure("IMPRESSION", url, response)
                try:
                    response_text = response.text or ""
                except Exception:
                    response_text = ""

#                classified = self._classify_api_failure(response.status_code, response_text, "")
#                self.last_error_summary = f"IMPRESSION {classified}"
                summary_type, summary_text = self._classify_api_failure(
                    response.status_code,
                    response_text
                )
                self.last_summary_type = summary_type
                self.last_error_summary = f"IMPRESSION | {summary_text}"

            except Exception as e:
                outputLog(f"[WARN] IMPRESSION exception: url={url} error={type(e).__name__}: {e}")
                self.last_error_summary = f"IMPRESSION exception: {type(e).__name__}: {e}"

        outputLog("[WARN] IMPRESSION failed: all endpoints rejected the request")
        if not self.last_error_summary:
            self.last_error_summary = "IMPRESSION failed: all endpoints rejected the request"
        return False

    async def send_thread_client_event_logs(
        self,
        tweet_ids: List[str],
        session: AsyncSession,
        referer: str,
        *,
        page: str = "tweet",
        include_bottom: bool = True,
        author_id: str = "0",
    ) -> bool:
        """Send impression logs for the focal tweet and visible tweets in the same thread."""
        unique_ids = []
        seen = set()
        for tweet_id in tweet_ids:
            value = str(tweet_id)
            if value.isdigit() and value not in seen:
                seen.add(value)
                unique_ids.append(value)

        if not unique_ids:
            return False

        outputLog(f"[THREAD] sending impressions for {len(unique_ids)} tweet(s)")
        focal_ok = False
        for index, item_id in enumerate(unique_ids):
            ok = await self.send_client_event_log(
                item_id,
                session,
                referer=referer,
                page=page,
                include_stream_results=True,
                include_bottom=include_bottom and index == len(unique_ids) - 1,
                author_id=author_id,
            )
            if index == 0:
                focal_ok = ok
            if index < len(unique_ids) - 1:
                await self._wait_natural(0.3, 0.8)

        return focal_ok

    async def _wait_before_retweet(self, media_info: Optional[Dict] = None) -> float:
        """RT前だけ長めに熟考しているように待機する。"""
        roll = random.random()
        if roll < 0.20:
            wait_time = random.uniform(35.0, 75.0)
            label = "long"
        elif roll < 0.75:
            wait_time = random.uniform(18.0, 40.0)
            label = "normal"
        else:
            wait_time = random.uniform(8.0, 18.0)
            label = "quick"

        if media_info and (media_info.get("has_video") or media_info.get("has_image")) and random.random() < 0.35:
            extra = random.uniform(10.0, 30.0)
            wait_time += extra
            label = f"{label}+media"

        wait_time *= self.speed_multiplier
        outputLog(f"[RETWEET_WAIT] RT判断待機 ({label})... ({wait_time:.1f}s)")
        await asyncio.sleep(max(wait_time, 3.0))
        return wait_time

    async def natural_retweet_action(self, tweet_id: str, session: AsyncSession) -> Dict[str, bool]:
        """閲覧・impression・プロフィール揺らぎを挟んで、RTだけを自然フローで実行する。"""
        results = {'impression': False, 'retweet': False}
        screen_name = None
        media_info = {"has_video": False, "has_image": False, "author_id": "0"}

        home_found = await self.fetch_home_timeline(session, tweet_id)
        results['home_found'] = bool(home_found)
        await self._wait_natural(2.0, 5.0)

        if home_found:
            route = random.choice(("home", "detail"))
            route_origin = "home"
        else:
            route = random.choice(("search", "detail"))
            route_origin = "search_or_direct"
        results['route'] = route

        acquired = False
        ref = "https://x.com/home"

        if route == "home":
            acquired = True
            ref = "https://x.com/home"
            results['impression'] = await self.send_client_event_log(
                tweet_id,
                session,
                referer=ref,
                page="home",
                include_stream_results=True,
                include_bottom=False,
            )

        elif route == "search":
            acquired = await self.fetch_search_timeline(tweet_id, session)
            if acquired:
                query = urllib.parse.quote(getattr(self, "last_search_query", str(tweet_id)))
                ref = f"https://x.com/search?q={query}&src=typed_query&f=live"
                results['impression'] = await self.send_client_event_log(
                    tweet_id,
                    session,
                    referer=ref,
                    page="search",
                    include_stream_results=True,
                    include_bottom=False,
                )
            else:
                outputLog("[ROUTE] SearchTimeline did not contain target; moving to direct detail")
                route = "detail"
                results['route'] = "detail_after_search"

        if route == "detail":
            outputLog(f"[ROUTE] {route_origin} -> tweet detail: {tweet_id}")
            screen_name, media_info = await self.view_tweet(tweet_id, session)
            acquired = bool(screen_name and screen_name != "Unknown")
            if acquired:
                await self._wait_natural(2.0, 5.0)
                if media_info.get('has_video'):
                    wait_video = random.uniform(8.0, 18.0)
                    outputLog(f"[MEDIA] 動画を再生中... ({wait_video:.1f}s)")
                    await asyncio.sleep(wait_video)
                elif media_info.get('has_image'):
                    wait_image = random.uniform(5.0, 10.0)
                    outputLog(f"[MEDIA] 画像を閲覧中... ({wait_image:.1f}s)")
                    await asyncio.sleep(wait_image)
                else:
                    await self._wait_natural(3.0, 8.0)

                ref = f"https://x.com/{screen_name}/status/{tweet_id}"
                detail_tweet_ids = getattr(self, "last_detail_tweet_ids", None) or [tweet_id]
                results['thread_impression_ids'] = detail_tweet_ids
                results['thread_impression_count'] = len(detail_tweet_ids)
                current_author_id = media_info.get("author_id", "0")
                results['impression'] = await self.send_thread_client_event_logs(
                    detail_tweet_ids,
                    session,
                    referer=ref,
                    page="tweet",
                    include_bottom=True,
                    author_id=current_author_id,
                )

        if acquired and route != "detail":
            outputLog(f"[THREAD] loading tweet detail for RT context: {tweet_id}")
            detail_screen_name, detail_media_info = await self.view_tweet(tweet_id, session)
            detail_tweet_ids = getattr(self, "last_detail_tweet_ids", None) or [tweet_id]
            extra_tweet_ids = [item_id for item_id in detail_tweet_ids if item_id != tweet_id]
            results['thread_impression_ids'] = detail_tweet_ids
            results['thread_impression_count'] = len(detail_tweet_ids)
            if detail_screen_name and detail_screen_name != "Unknown":
                screen_name = screen_name or detail_screen_name
                media_info = detail_media_info
                detail_ref = f"https://x.com/{detail_screen_name}/status/{tweet_id}"
                if media_info.get('has_video'):
                    wait_video = random.uniform(8.0, 18.0)
                    outputLog(f"[MEDIA] 動画を再生中... ({wait_video:.1f}s)")
                    await asyncio.sleep(wait_video)
                elif media_info.get('has_image'):
                    wait_image = random.uniform(5.0, 10.0)
                    outputLog(f"[MEDIA] 画像を閲覧中... ({wait_image:.1f}s)")
                    await asyncio.sleep(wait_image)
                if extra_tweet_ids:
                    await self._wait_natural(1.0, 2.0)
                    current_author_id = media_info.get("author_id", "0")
                    results['thread_extra_impression'] = await self.send_thread_client_event_logs(
                        extra_tweet_ids,
                        session,
                        referer=detail_ref,
                        page="tweet",
                        include_bottom=False,
                        author_id=current_author_id,
                    )
                ref = detail_ref

        if not acquired:
            results['route_reason'] = "Target tweet could not be acquired from home, search, or detail"
            outputLog(f"[ROUTE] skipped: {results['route_reason']}")
            return results

        if not results['impression']:
            results['impression_reason'] = self.last_error_summary or "IMPRESSION returned False without explicit API error"
            results['impression_error_type'] = self.last_summary_type

        if screen_name and random.random() < 0.5:
            await self._wait_natural(1.0, 2.0)
            outputLog(f"[PROFILE] プロフィール閲覧: @{screen_name}")
            results['profile_view'] = await self.fetch_user_profile(screen_name, session)
            await self._wait_natural(2.0, 4.0)

        results['retweet_wait_seconds'] = await self._wait_before_retweet(media_info)
        results['retweet'] = await self.retweet_tweet(tweet_id, session, referer=ref)
        if not results['retweet']:
            results['retweet_reason'] = self.last_error_summary or "retweet returned False without explicit API error"
            results['retweet_error_type'] = self.last_summary_type

        await self._wait_natural(2.0, 4.0)
        return results
    async def natural_action(self, tweet_id: str, session: AsyncSession, do_like: bool = True, do_bookmark: bool = False) -> Dict[str, bool]:
        results = {'impression': False, 'like': False, 'bookmark': False}
        screen_name = None
        media_info = {"has_video": False, "has_image": False}

        # Xを開いた最初の画面としてHomeTimelineを必ず取得する。
        home_found = await self.fetch_home_timeline(session, tweet_id)
        await self._wait_natural(2.0, 5.0)

        # ホームに対象があれば一覧上または詳細へ進む。
        # なければ検索またはURLから直接詳細へ進む。
        if home_found:
            route = random.choice(("home", "detail"))
            route_origin = "home"
        else:
            route = random.choice(("search", "detail"))
            route_origin = "search_or_direct"

        acquired = False
        ref = "https://x.com/home"

        if route == "home":
            acquired = True
            ref = "https://x.com/home"
            results['impression'] = await self.send_client_event_log(
                tweet_id,
                session,
                referer=ref,
                page="home",
                include_stream_results=True,
                include_bottom=False,
            )

        elif route == "search":
            acquired = await self.fetch_search_timeline(tweet_id, session)
            if acquired:
                query = urllib.parse.quote(getattr(self, "last_search_query", str(tweet_id)))
                ref = f"https://x.com/search?q={query}&src=typed_query&f=live"
                results['impression'] = await self.send_client_event_log(
                    tweet_id,
                    session,
                    referer=ref,
                    page="search",
                    include_stream_results=True,
                    include_bottom=False,
                )
            else:
                outputLog("[ROUTE] SearchTimeline did not contain target; moving to direct detail")
                route = "detail"

        if route == "detail":
            outputLog(f"[ROUTE] {route_origin} -> tweet detail: {tweet_id}")
            screen_name, media_info = await self.view_tweet(tweet_id, session)
            acquired = bool(screen_name and screen_name != "Unknown")
            if acquired:
                await self._wait_natural(2.0, 5.0)
                if media_info.get('has_video'):
                    wait_video = random.uniform(8.0, 18.0)
                    outputLog(f"[MEDIA] 動画を再生中... ({wait_video:.1f}s)")
                    await asyncio.sleep(wait_video)
                elif media_info.get('has_image'):
                    wait_image = random.uniform(5.0, 10.0)
                    outputLog(f"[MEDIA] 画像を閲覧中... ({wait_image:.1f}s)")
                    await asyncio.sleep(wait_image)
                else:
                    await self._wait_natural(3.0, 8.0)

                ref = f"https://x.com/{screen_name}/status/{tweet_id}"
                detail_tweet_ids = getattr(self, "last_detail_tweet_ids", None) or [tweet_id]
                results['thread_impression_ids'] = detail_tweet_ids
                results['thread_impression_count'] = len(detail_tweet_ids)
                current_author_id = media_info.get("author_id", "0")
                results['impression'] = await self.send_thread_client_event_logs(
                    detail_tweet_ids,
                    session,
                    referer=ref,
                    page="tweet",
                    include_bottom=True,
                    author_id=current_author_id,
                )

        if acquired and route != "detail":
            outputLog(f"[THREAD] loading tweet detail for thread impressions: {tweet_id}")
            detail_screen_name, _detail_media_info = await self.view_tweet(tweet_id, session)
            detail_tweet_ids = getattr(self, "last_detail_tweet_ids", None) or [tweet_id]
            extra_tweet_ids = [item_id for item_id in detail_tweet_ids if item_id != tweet_id]
            results['thread_impression_ids'] = detail_tweet_ids
            results['thread_impression_count'] = len(detail_tweet_ids)
            if detail_screen_name and detail_screen_name != "Unknown":
                screen_name = screen_name or detail_screen_name
                detail_ref = f"https://x.com/{detail_screen_name}/status/{tweet_id}"
                if extra_tweet_ids:
                    await self._wait_natural(1.0, 2.0)
                    current_author_id = _detail_media_info.get("author_id", "0")
                    results['thread_extra_impression'] = await self.send_thread_client_event_logs(
                        extra_tweet_ids,
                        session,
                        referer=detail_ref,
                        page="tweet",
                        include_bottom=False,
                        author_id=current_author_id,
                    )

        if not acquired:
            results['route_reason'] = "Target tweet could not be acquired from home, search, or detail"
            outputLog(f"[ROUTE] skipped: {results['route_reason']}")
            return results

        if not results['impression']:
            results['impression_reason'] = self.last_error_summary or "IMPRESSION returned False without explicit API error"
            results['impression_error_type'] = self.last_summary_type

        if route == "detail" and screen_name and random.random() < 0.5:
            await self._wait_natural(1.0, 2.0)
            outputLog(f"[PROFILE] プロフィール閲覧: @{screen_name}")
            await self.fetch_user_profile(screen_name, session)
            await self._wait_natural(2.0, 4.0)

        await self._wait_natural(1.5, 3.5)

        actions = []
        if do_like: actions.append("like")
        if do_bookmark: actions.append("bookmark")
        random.shuffle(actions)

        for act in actions:
            if act == "like":
                results['like'] = await self.like_tweet(tweet_id, session, referer=ref)
                if not results['like']:
                    results['like_reason'] = self.last_error_summary or "like returned False without explicit API error"
                    results['like_error_type'] = self.last_summary_type
                await self._wait_natural(1.5, 3.0)
            elif act == "bookmark":
                results['bookmark'] = await self.bookmark_tweet(tweet_id, session, referer=ref)
                if not results['bookmark']:
                    results['bookmark_reason'] = self.last_error_summary or "bookmark returned False without explicit API error"
                    results['bookmark_error_type'] = self.last_summary_type
                await self._wait_natural(0.5, 1.5)

        await self._wait_natural(2.0, 4.0)
        return results











































