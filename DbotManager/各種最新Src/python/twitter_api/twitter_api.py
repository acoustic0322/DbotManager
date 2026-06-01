import asyncio
import random
from datetime import datetime, timedelta
import json
import base64
import os
import subprocess
import platform
import urllib.request
import urllib.parse
import time
from curl_cffi.requests import AsyncSession
from typing import Optional, Dict, List, Tuple

import config
from config import outputLog

class TwitterAPI:
    """X (Twitter) の非公式API操作クラス"""
    
    def __init__(self, auth_token: str, csrf_token: str, cookies: str, proxy: Optional[str] = None, user_agent: str = None, sec_ch_ua: str = None):
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
        
        # Cookieのフィルタリングとパース
        self.cookies = {}
        # 必須または許可するCookieのキーリスト
        ALLOWED_COOKIES = {
            'auth_token', 'ct0', 'kdt', 'twid', 'guest_id', 'guest_id_ads', 
            'guest_id_marketing', 'personalization_id', '_twitter_sess', 'lang',
            '__cf_bm', 'cf_clearance', 'gt', 'att', 'night_mode'
        }
        
        parsed_cookies = {}
        if cookies:
            if isinstance(cookies, dict):
                parsed_cookies = cookies
            else:
                try:
                    # まず単純な split でパース（http.cookiesは厳格すぎる場合があるため）
                    for pair in cookies.split(';'):
                        if '=' in pair:
                            key, val = pair.strip().split('=', 1)
                            parsed_cookies[key.strip()] = val.strip()
                except Exception as e:
                    outputLog(f"[WARN] Cookie parse error in init: {e}")
                    parsed_cookies = {}

        # フィルタリング実行 (ホワイトリスト方式でゴミCookieを排除)
        for k, v in parsed_cookies.items():
            if k in ALLOWED_COOKIES or k.startswith('guest_id'):
                self.cookies[k] = v
        
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
        
        # Node.jsサーバー管理
        self._ensure_tid_server_running()

    def _generate_sec_ch_ua(self, user_agent: str) -> str:
        """User-Agent文字列から適切なsec-ch-uaヘッダーを生成する"""
        try:
            import re
            ua = user_agent.lower()
            if "chrome" in ua:
                match = re.search(r'chrome/(\d+)', ua)
                ver = match.group(1) if match else "124"
                return f'"Chromium";v="{ver}", "Google Chrome";v="{ver}", "Not-A.Brand";v="99"'
            elif "edge" in ua:
                match = re.search(r'edge/(\d+)', ua)
                ver = match.group(1) if match else "124"
                return f'"Chromium";v="{ver}", "Microsoft Edge";v="{ver}", "Not-A.Brand";v="99"'
            else:
                 # Fallback
                 return '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
        except:
            return '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'


    def _ensure_tid_server_running(self):
        """Node.js TIDサーバーが起動しているか確認し、なければ起動する"""
        try:
            # サーバー生存確認 (timeout時間を短く)
            with urllib.request.urlopen("http://localhost:3000/status", timeout=0.5) as response:
                if response.status == 200:
                    return # 起動済み
        except:
            pass # 起動していない、またはエラー
            
        outputLog("[System] Starting Node.js TID Server...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, 'tid_node', 'server.js')
        
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
            ['node', script_path],
            stdout=log_file,
            stderr=log_file,
            creationflags=creationflags
        )
        
        # 起動待機
        time.sleep(2)
        outputLog("[System] Node.js TID Server started.")
        
    def _get_headers(self, extra_headers: Dict = None) -> Dict:
        """リクエストヘッダーを生成"""
        headers = {
            'authorization': self.auth_token,
            'x-csrf-token': self.csrf_token,
            # 'cookie': self.cookies,  # CookieはAsyncSession(cookie_jar)に任せるため削除
            'content-type': 'application/json',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'ja-JP,ja;q=0.9',
            # 'user-agent': self.user_agent, 
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'ja',
            'origin': 'https://x.com',
            'referer': 'https://x.com/',
            'priority': 'u=1, i',
            # 'sec-ch-ua': self.sec_ch_ua,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers
    
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
        """人間らしい待機時間"""
        wait_time = random.uniform(base_min, base_max) * self.speed_multiplier
        hour = datetime.now().hour
        if 2 <= hour <= 6:
            wait_time *= 2.0
        await asyncio.sleep(wait_time)
    
#    async def view_tweet(self, tweet_id: str, session: AsyncSession) -> tuple[Optional[str], dict]:
    async def view_tweet(
        self,
        tweet_id: str,
        session: AsyncSession
    ) -> Tuple[Optional[str], Dict]:

        """ツイートを閲覧し、スクリーンネームとメディア情報を返す"""
        try:
            url = f"https://x.com/i/api/graphql/sMoYQ8oNKf7pyC3ILopasw/TweetDetail"
            variables = {
                "focalTweetId": tweet_id,
                "with_rux_injections": False,
                "rankingMode": "Relevance",
                "includePromotedContent": True,
                "withCommunity": True,
                "withQuickPromoteEligibilityTweetFields": True,
                "withBirdwatchNotes": True,
                "withVoice": True
            }
            # ... (features/fieldToggles are same, omitted for brevity if unchanged, but for safety I keep logic same)
            # To save tokens I will just replace the parsing logic block significantly
            features = {
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
                "responsive_web_grok_annotations_enabled": False,
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
                "responsive_web_enhance_cards_enabled": False
            }
            fieldToggles = {
                "withArticleRichContentState": True,
                "withArticlePlainText": False,
                "withGrokAnalyze": False,
                "withDisallowedReplyControls": False
            }
            params = {
                'variables': json.dumps(variables),
                'features': json.dumps(features),
                'fieldToggles': json.dumps(fieldToggles)
            }
            
            response = await session.get(
                url, headers=self._get_headers(), params=params, proxy=self.proxy, timeout=30
            )
            
            media_info = {"has_video": False, "has_image": False}
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    entries = data.get('data', {}).get('threaded_conversation_with_injections_v2', {}).get('instructions', [])
                    for instruction in entries:
                        if instruction.get('type') == 'TimelineAddEntries':
                            for entry in instruction.get('entries', []):
                                if entry.get('entryId') == f"tweet-{tweet_id}":
                                    content = entry.get('content', {}).get('itemContent', {})
                                    tweet_result = content.get('tweet_results', {}).get('result', {})
                                    
                                    # Legacy field extraction
                                    legacy = tweet_result.get('legacy', {}) or tweet_result.get('core', {}).get('legacy', {}) or tweet_result.get('tweet', {}).get('legacy', {})
                                    
                                    # Screen Name
                                    user_result = tweet_result.get('core', {}).get('user_results', {}).get('result', {})
                                    screen_name = user_result.get('legacy', {}).get('screen_name') 
                                    
                                    # Media Check
                                    extended_entities = legacy.get('extended_entities', {})
                                    media_list = extended_entities.get('media', [])
                                    for m in media_list:
                                        m_type = m.get('type')
                                        if m_type == 'video' or m_type == 'animated_gif':
                                            media_info['has_video'] = True
                                        elif m_type == 'photo':
                                            media_info['has_image'] = True
                                            
                                    if screen_name:
                                        outputLog(f"[DEBUG] screen_name取得成功: @{screen_name}, Media: {media_info}")
                                        return screen_name, media_info
                except:
                    pass
                return "Unknown", media_info
            elif response.status_code == 429:
                self.rate_limit_count += 1
                if self.rate_limit_count >= 3:
                    self.pause_account(hours=2)
                return None, media_info
            return None, media_info
        except:
            return None, {"has_video": False, "has_image": False}
    
    async def fetch_user_profile(self, screen_name: str, session: AsyncSession) -> bool:
        """ユーザープロフィールを取得"""
        try:
            url = "https://x.com/i/api/graphql/-oaLodhGbbnzJBACb1kk2Q/UserByScreenName"
            variables = {"screen_name": screen_name, "withGrokTranslatedBio": False}
            features = {
                "hidden_profile_subscriptions_enabled": True,
                "profile_label_improvements_pcf_label_in_post_enabled": True,
                "responsive_web_profile_redirect_enabled": False,
                "rweb_tipjar_consumption_enabled": True,
                "verified_phone_label_enabled": False,
                "subscriptions_verification_info_is_identity_verified_enabled": True,
                "subscriptions_verification_info_verified_since_enabled": True,
                "highlights_tweets_tab_ui_enabled": True,
                "responsive_web_twitter_article_notes_tab_enabled": True,
                "subscriptions_feature_can_gift_premium": True,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True
            }
            fieldToggles = {"withPayments": False, "withAuxiliaryUserLabels": True}
            
            response = await session.get(
                url, headers=self._get_headers(), 
                params={'variables': json.dumps(variables), 'features': json.dumps(features), 'fieldToggles': json.dumps(fieldToggles)},
                proxy=self.proxy, timeout=30
            )
            return response.status_code == 200
        except:
            return False

    async def _execute_via_native_curl(self, url: str, payload: str, referer: str, success_keyword: str = '"Done"', transaction_id: str = None) -> Dict[str, any]:
        """Native Curl実行 (非同期/別スレッド)"""
        try:
            # コンストラクタで渡された(または自動生成された)UA/CHを使用
            user_agent = self.user_agent
            sec_ch_ua = self.sec_ch_ua
            
            headers = [
                'accept: */*',
                'accept-language: ja-JP,ja;q=0.9',
                f'authorization: {self.auth_token}',
                'content-type: application/json',
                'origin: https://x.com',
                'priority: u=1, i',
                f'referer: {referer}',
                f'sec-ch-ua: {sec_ch_ua}',
                'sec-ch-ua-mobile: ?0',
                'sec-ch-ua-platform: "Windows"',
                'sec-fetch-dest: empty',
                'sec-fetch-mode: cors',
                'sec-fetch-site: same-origin',
                f'user-agent: {user_agent}',
                f'x-client-transaction-id: {transaction_id if transaction_id else self._generate_session_transaction_id()}', 
                f'x-csrf-token: {self.csrf_token}',
                'x-twitter-active-user: yes',
                'x-twitter-auth-type: OAuth2Session',
                'x-twitter-client-language: ja'
            ]
            
            cmd = ['curl', url, '-i'] # -i for headers
            if self.proxy:
                cmd.extend(['-x', self.proxy])
            for h in headers:
                cmd.extend(['-H', h])
            if self.cookies:
                cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
                cmd.extend(['-b', cookie_str])
            cmd.extend(['--data-raw', payload])
            
            # curlコマンドを保存（失敗時のデバッグ用）
            curl_command = ' '.join(cmd)
            
            # Windows SelectorEventLoop対策: 別スレッドでsubprocess.run
            def run_curl_sync():
                creationflags = 0
                if platform.system() == 'Windows':
                    creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
                return subprocess.run(cmd, capture_output=True, creationflags=creationflags)

#            proc_result = await asyncio.to_thread(run_curl_sync)
            loop = asyncio.get_event_loop()
            proc_result = await loop.run_in_executor(
                None,
                run_curl_sync
            )            
            
            stdout_text = proc_result.stdout.decode('utf-8', errors='replace')
            stderr_text = proc_result.stderr.decode('utf-8', errors='replace')
            
            if proc_result.returncode == 0:
                # 成功判定ロジック（厳格化版）
                # 1. success_keywordが必須
                # 2. エラーレスポンスは必ず失敗とする
                is_success_keyword = success_keyword in stdout_text
                is_200_ok = "HTTP/1.1 200 OK" in stdout_text or "HTTP/2 200" in stdout_text
                is_401 = "HTTP/1.1 401" in stdout_text or "HTTP/2 401" in stdout_text
                is_403 = "HTTP/1.1 403" in stdout_text or "HTTP/2 403" in stdout_text
                is_429 = "HTTP/1.1 429" in stdout_text or "HTTP/2 429" in stdout_text
                
                # エラー判定（論理演算子を修正）
                has_errors = '"errors":' in stdout_text or ('"code":' in stdout_text and not is_success_keyword)
                
                # エラーコード139 = すでにいいね/ブックマーク済み → 成功扱い
                is_already_done = '"code":139' in stdout_text
                if is_already_done:
                    has_errors = False

                # success_keywordが見つかり、かつエラーがない場合のみ成功
                # または「すでに済み」の場合も成功
                if (is_success_keyword and not has_errors) or is_already_done:
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
                    return {'success': True, 'cookies': new_cookies}
                else:
                    # 失敗時は詳細ログを出力（デバッグ用curlコマンド含む）
                    outputLog("\n" + "="*70)
                    outputLog("[ERROR] API Request Failed - Debug Information")
                    outputLog("="*70)
                    
                    # HTTP ステータスコードを判定
                    if is_401:
                        error_type = "Authentication Failed (401 Unauthorized)"
                    elif is_403:
                        error_type = "Access Forbidden (403 Forbidden)"
                    elif is_429:
                        error_type = "Rate Limited (429 Too Many Requests)"
                    elif is_200_ok:
                        error_type = "Success Keyword Not Found (200 OK but invalid response)"
                    else:
                        error_type = "Unknown HTTP Error"
                    
                    outputLog(f"Error Type: {error_type}")
                    
                    # JSONレスポンスボディを抽出（ヘッダーと本文を分離）
                    body_start = stdout_text.find('{"')
                    response_body = stdout_text[body_start:] if body_start != -1 else stdout_text
                    
                    # エラーメッセージを抽出（"errors"キーがあれば）
                    error_message = "No error message"
                    if '"errors":' in response_body:
                        try:
                            import json
                            json_data = json.loads(response_body)
                            if 'errors' in json_data and json_data['errors']:
                                error_message = json_data['errors'][0].get('message', 'Unknown error')
                        except:
                            pass
                    
                    outputLog(f"Error Message: {error_message}")
                    outputLog(f"Keyword Expected: {success_keyword}")
                    outputLog(f"Keyword Found: {is_success_keyword}")
                    outputLog(f"Has Errors Field: {has_errors}")
                    
                    # curlコマンドを出力（認証情報をマスク）
                    outputLog("\n[DEBUG] Curl Command (auth tokens masked):")
                    safe_command = curl_command.replace(self.auth_token, "Bearer XXXXX").replace(self.csrf_token, "XXXXX")
                    outputLog(safe_command)
                    
                    # レスポンス詳細
                    outputLog(f"\n[DEBUG] Response Preview (first 1500 chars):")
                    outputLog(response_body[:1500])
                    outputLog("="*70 + "\n")
                    
                    return {
                        'success': False, 
                        'cookies': {},
                        'error_type': error_type,
                        'error_message': error_message,
                        'response_body': response_body[:500]
                    }
            else:
                # プロセスエラー時も詳細出力
                outputLog("\n" + "="*70)
                outputLog("[ERROR] Curl Process Failed - Debug Information")
                outputLog("="*70)
                error_msg = f"Curl process error (exit code {proc_result.returncode})"
                outputLog(f"Error: {error_msg}")
                outputLog(f"Stderr: {stderr_text}")
                
                outputLog("\n[DEBUG] Curl Command (auth tokens masked):")
                safe_command = curl_command.replace(self.auth_token, "Bearer XXXXX").replace(self.csrf_token, "XXXXX")
                outputLog(safe_command)
                outputLog("="*70 + "\n")
                
                return {
                    'success': False, 
                    'cookies': {},
                    'error_type': 'Process Error',
                    'error_message': stderr_text[:200],
                    'response_body': ''
                }
        except Exception as e:
            error_msg = f"Exception in curl execution: {str(e)}"
            outputLog(f"[WARN] Native Curl Error: {error_msg}")
            import traceback
            outputLog(f"  - Traceback: {traceback.format_exc()[:500]}")
            return {
                'success': False, 
                'cookies': {},
                'error_type': 'Exception',
                'error_message': str(e),
                'response_body': ''
            }

    async def _generate_dynamic_transaction_id(self, path: str, method: str = 'POST') -> str:
        """Node.jsサーバーからTID取得"""
        try:
            params = urllib.parse.urlencode({'path': path, 'method': method})
            url = f"http://localhost:3000/tid?{params}"
            
            def fetch_tid_sync():
                try:
                    with urllib.request.urlopen(url, timeout=5) as response:
                        if response.status == 200:
                            return response.read().decode('utf-8').strip()
                except Exception as e:
                    outputLog(f"[WARN] TID Server Query Error: {e}")
                    return None
            
#            tid = await asyncio.to_thread(fetch_tid_sync)
            loop = asyncio.get_running_loop()

            tid = await loop.run_in_executor(
                None,
                fetch_tid_sync
            )

            if tid:
                return tid
            return self._generate_session_transaction_id()
        except Exception as e:
            outputLog(f"[WARN] Node.js TID Error: {e}")
            return self._generate_session_transaction_id()

    async def bookmark_tweet(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> bool:
        if self.is_paused(): return False
        if "status" not in referer: referer = f"https://x.com/i/status/{tweet_id}"
        url = "https://x.com/i/api/graphql/aoDbu3RHznuiSkQ9aNM67Q/CreateBookmark"
        payload = f'{{"variables":{{"tweet_id":"{tweet_id}"}},"queryId":"aoDbu3RHznuiSkQ9aNM67Q"}}'
        outputLog("[Processing] Generating TID via Node.js...")
        tid = await self._generate_dynamic_transaction_id('/i/api/graphql/aoDbu3RHznuiSkQ9aNM67Q/CreateBookmark', 'POST')
        result = await self._execute_via_native_curl(url, payload, referer, '"tweet_bookmark_put":"Done"', tid)
        if result['cookies']:
            for k, v in result['cookies'].items():
                session.cookies.set(k, v, domain=".x.com")
        return result['success']

    async def like_tweet(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> bool:
        if self.is_paused(): return False
        if "status" not in referer: referer = f"https://x.com/i/status/{tweet_id}"
        url = "https://x.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet"
        payload = f'{{"variables":{{"tweet_id":"{tweet_id}"}},"queryId":"lI07N6Otwv1PhnEgXILM7A"}}'
        outputLog("[Processing] Generating TID via Node.js...")
        tid = await self._generate_dynamic_transaction_id('/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet', 'POST')
        result = await self._execute_via_native_curl(url, payload, referer, '"favorite_tweet":"Done"', tid)
        if result['cookies']:
            for k, v in result['cookies'].items():
                session.cookies.set(k, v, domain=".x.com")
        return result['success']
    
    async def upload_media(self, file_path: str, session: AsyncSession) -> Optional[str]:
        """画像ファイルをアップロードし、media_idを返す"""
        import os
        import mimetypes
        
        if not os.path.exists(file_path):
            outputLog(f"[ERROR] Image file not found: {file_path}")
            return None
            
        total_bytes = os.path.getsize(file_path)
        media_type, _ = mimetypes.guess_type(file_path)
        if not media_type:
            media_type = "image/jpeg"
            
        # 1. INIT
        url_init = "https://upload.twitter.com/i/media/upload.json"
        tid = await self._generate_dynamic_transaction_id('/i/media/upload.json', 'POST')
        
        headers_base = [
            'accept: */*',
            'accept-language: ja-JP,ja;q=0.9',
            f'authorization: {self.auth_token}',
            'origin: https://x.com',
            'referer: https://x.com/',
            f'sec-ch-ua: {self.sec_ch_ua}',
            'sec-fetch-dest: empty',
            'sec-fetch-mode: cors',
            'sec-fetch-site: same-origin',
            f'user-agent: {self.user_agent}',
            f'x-client-transaction-id: {tid}',
            f'x-csrf-token: {self.csrf_token}',
            'x-twitter-active-user: yes',
            'x-twitter-auth-type: OAuth2Session',
            'x-twitter-client-language: ja'
        ]
        
        init_payload = f"command=INIT&total_bytes={total_bytes}&media_type={urllib.parse.quote(media_type)}&media_category=tweet_image"
        
        cmd_init = ['curl', url_init, '-i']
        if self.proxy:
            cmd_init.extend(['-x', self.proxy])
        for h in headers_base:
            cmd_init.extend(['-H', h])
        cmd_init.extend(['-H', 'content-type: application/x-www-form-urlencoded'])
        
        cookie_str = ""
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            cmd_init.extend(['-b', cookie_str])
        cmd_init.extend(['--data-raw', init_payload])
        
        def run_cmd(cmd):
            creationflags = 0
            if platform.system() == 'Windows':
                creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            return subprocess.run(cmd, capture_output=True, creationflags=creationflags)
            
        outputLog("[UPLOAD] Initializing image upload (INIT)...")

#        res = await asyncio.to_thread(run_cmd, cmd_init)
        loop = asyncio.get_running_loop()

        res = await loop.run_in_executor(
            None,
            lambda: run_cmd(cmd_init)
        )

        stdout = res.stdout.decode('utf-8', errors='replace')
        
        media_id = None
        try:
            body_start = stdout.find('{"')
            if body_start != -1:
                body_json = json.loads(stdout[body_start:])
                media_id = body_json.get('media_id_string')
        except Exception as e:
            outputLog(f"[ERROR] Failed to parse INIT response: {e}")
            
        if not media_id:
            outputLog(f"[ERROR] INIT step failed. Stdout preview:\n{stdout[:1000]}")
            return None
            
        # 2. APPEND
        tid = await self._generate_dynamic_transaction_id('/i/media/upload.json', 'POST')
        headers_append = [h for h in headers_base if not h.startswith('x-client-transaction-id:')]
        headers_append.append(f'x-client-transaction-id: {tid}')
        
        cmd_append = ['curl', url_init, '-i']
        if self.proxy:
            cmd_append.extend(['-x', self.proxy])
        for h in headers_append:
            cmd_append.extend(['-H', h])
        if cookie_str:
            cmd_append.extend(['-b', cookie_str])
            
        cmd_append.extend([
            '-F', 'command=APPEND',
            '-F', f'media_id={media_id}',
            '-F', 'segment_index=0',
            '-F', f'media=@{file_path}'
        ])
        
        outputLog("[UPLOAD] Uploading image chunk (APPEND)...")

#        res = await asyncio.to_thread(run_cmd, cmd_append)
        loop = asyncio.get_running_loop()

        res = await loop.run_in_executor(
            None,
            lambda: run_cmd(cmd_append)
        )

        stdout = res.stdout.decode('utf-8', errors='replace')
        
        if "204" not in stdout and "200" not in stdout:
            outputLog(f"[ERROR] APPEND step failed. Stdout preview:\n{stdout[:1000]}")
            return None
            
        # 3. FINALIZE
        tid = await self._generate_dynamic_transaction_id('/i/media/upload.json', 'POST')
        headers_finalize = [h for h in headers_base if not h.startswith('x-client-transaction-id:')]
        headers_finalize.append(f'x-client-transaction-id: {tid}')
        
        finalize_payload = f"command=FINALIZE&media_id={media_id}"
        
        cmd_finalize = ['curl', url_init, '-i']
        if self.proxy:
            cmd_finalize.extend(['-x', self.proxy])
        for h in headers_finalize:
            cmd_finalize.extend(['-H', h])
        cmd_finalize.extend(['-H', 'content-type: application/x-www-form-urlencoded'])
        if cookie_str:
            cmd_finalize.extend(['-b', cookie_str])
        cmd_finalize.extend(['--data-raw', finalize_payload])
        
        outputLog("[UPLOAD] Completing image upload (FINALIZE)...")

#        res = await asyncio.to_thread(run_cmd, cmd_finalize)
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            None,
            lambda: run_cmd(cmd_finalize)
        )

        stdout = res.stdout.decode('utf-8', errors='replace')
        
        try:
            body_start = stdout.find('{"')
            if body_start != -1:
                body_json = json.loads(stdout[body_start:])
                if 'media_id_string' in body_json:
                    outputLog(f"[UPLOAD] Image upload successful. media_id: {media_id}")
                    return media_id
        except Exception as e:
            outputLog(f"[ERROR] Failed to parse FINALIZE response: {e}")
            
        outputLog(f"[ERROR] FINALIZE step failed. Stdout preview:\n{stdout[:1000]}")
        return None
    
    async def fetch_home_timeline(self, session: AsyncSession) -> bool:
        """ホームタイムライン取得 (Warm-up)"""
        try:
            url = "https://x.com/i/api/graphql/edseUwk9sP5Phz__9TIRnA/HomeTimeline"
            variables = {"count": 20, "includePromotedContent": True, "requestContext": "ptr", "withCommunity": True}
            features = {
                "rweb_video_screen_enabled": False, "profile_label_improvements_pcf_label_in_post_enabled": True, "responsive_web_profile_redirect_enabled": False,
                "rweb_tipjar_consumption_enabled": True, "verified_phone_label_enabled": False, "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True, "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "premium_content_api_read_enabled": False, "communities_web_enable_tweet_community_results_fetch": True, "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "responsive_web_grok_analyze_button_fetch_trends_enabled": False, "responsive_web_grok_analyze_post_followups_enabled": True, "responsive_web_jetfuel_frame": True,
                "responsive_web_grok_share_attachment_enabled": True, "responsive_web_grok_annotations_enabled": False, "articles_preview_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True, "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True, "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True, "responsive_web_twitter_article_tweet_consumption_enabled": True, "tweet_awards_web_tipping_enabled": False,
                "responsive_web_grok_show_grok_translated_post": False, "responsive_web_grok_analysis_button_from_backend": True, "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True, "standardized_nudges_misinfo": True, "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True, "longform_notetweets_inline_media_enabled": True, "responsive_web_grok_image_annotation_enabled": True,
                "responsive_web_grok_imagine_annotation_enabled": True, "responsive_web_grok_community_note_auto_translation_is_enabled": False, "responsive_web_enhance_cards_enabled": False
            }
            params = {'variables': json.dumps(variables), 'features': json.dumps(features)}
            response = await session.get(url, headers=self._get_headers(), params=params, proxy=self.proxy, timeout=30)
            if response.status_code == 200:
                outputLog("[HOME] ホームタイムライン取得成功 (Warm-up)")
                return True
            else:
                return False
        except:
            return False

    async def send_client_event_log(self, tweet_id: str, session: AsyncSession, referer: str = "https://x.com/home") -> bool:
        """インプレッションログをjot/client_eventに送信する"""
        if self.is_paused(): return False
        
        url = "https://x.com/i/api/1.1/jot/client_event.json"
        
        # ログ構造の構築 (Web版仕様)
        log_data = [
            {
                "integration_id": 12,
                "log": {
                    "client_event": {
                        "client_app_id": "1",
                        "event_namespace": {
                            "page": "tweet",
                            "section": "permalink",
                            "component": "tweet",
                            "element": "",
                            "action": "impression"
                        },
                        "item_details": [
                            {
                                "tweet_details": {
                                    "tweet_id": tweet_id,
                                    "is_ads": False
                                }
                            }
                        ]
                    }
                }
            }
        ]
        
        # フォームデータ形式 (URLエンコード)
        payload = f"log={urllib.parse.quote(json.dumps(log_data))}"
        
        headers = [
            'accept: */*',
            'accept-language: ja-JP,ja;q=0.9',
            f'authorization: {self.auth_token}',
            'content-type: application/x-www-form-urlencoded',
            'origin: https://x.com',
            'priority: u=1, i',
            f'referer: {referer}',
            f'sec-ch-ua: {self.sec_ch_ua}',
            'sec-ch-ua-mobile: ?0',
            'sec-ch-ua-platform: "Windows"',
            'sec-fetch-dest: empty',
            'sec-fetch-mode: cors',
            'sec-fetch-site: same-origin',
            f'user-agent: {self.user_agent}',
            f'x-csrf-token: {self.csrf_token}',
            'x-twitter-active-user: yes',
            'x-twitter-auth-type: OAuth2Session',
            'x-twitter-client-language: ja'
        ]
        
        cmd = ['curl', url, '-i']
        if self.proxy:
            cmd.extend(['-x', self.proxy])
        for h in headers:
            cmd.extend(['-H', h])
        
        cookie_str = ""
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            cmd.extend(['-b', cookie_str])
        cmd.extend(['--data-raw', payload])
        
        def run_curl_sync():
            creationflags = 0
            if platform.system() == 'Windows':
                creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            return subprocess.run(cmd, capture_output=True, creationflags=creationflags)

        outputLog(f"[IMPRESSION] Sending jot/client_event log for tweet_id: {tweet_id}")

#        proc_result = await asyncio.to_thread(run_curl_sync)
        loop = asyncio.get_event_loop()
        proc_result = await loop.run_in_executor(
            None,
            run_curl_sync
        )            
            

        stdout_text = proc_result.stdout.decode('utf-8', errors='replace')
        
        is_success = "HTTP/1.1 200" in stdout_text or "HTTP/2 200" in stdout_text or "HTTP/1.1 204" in stdout_text or "HTTP/2 204" in stdout_text
        if is_success:
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
                for k, v in new_cookies.items():
                    session.cookies.set(k, v, domain=".x.com")
            return True
        else:
            outputLog(f"[WARN] Failed to send impression log. Stdout preview:\n{stdout_text[:500]}")
            return False

    async def natural_action(self, tweet_id: str, session: AsyncSession, do_like: bool = True, do_bookmark: bool = False) -> Dict[str, bool]:
        results = {'like': False, 'bookmark': False}
        hour = datetime.now().hour
#        if 2 <= hour <= 6 and random.random() < 0.7:
#            outputLog("[SLEEP] 深夜のため操作をスキップ")
#            return results
        
        await self.fetch_home_timeline(session)
        await self._wait_natural(2.0, 5.0)
        
        outputLog(f"[VIEW] ツイート詳細へ移動: {tweet_id}")
        screen_name, media_info = await self.view_tweet(tweet_id, session)
        
        # ツイートが表示されてから数秒ディレイを空けてインプレッションログを送信
        await self._wait_natural(2.0, 5.0)
        ref = f"https://x.com/{screen_name}/status/{tweet_id}" if screen_name and screen_name != "Unknown" else f"https://x.com/i/status/{tweet_id}"
        await self.send_client_event_log(tweet_id, session, referer=ref)
        
        # 【Media View 実装】メディアがある場合は滞在時間を大幅に伸ばす
        if media_info.get('has_video'):
            wait_video = random.uniform(15.0, 30.0)
            outputLog(f"[MEDIA] 動画を再生中... ({wait_video:.1f}s)")
            await asyncio.sleep(wait_video)
        elif media_info.get('has_image'):
            wait_image = random.uniform(8.0, 15.0)
            outputLog(f"[MEDIA] 画像を閲覧中... ({wait_image:.1f}s)")
            await asyncio.sleep(wait_image)
        else:
            # テキストのみの滞在時間
            await self._wait_natural(4.0, 12.0)
        
        # プロフィール閲覧
        if screen_name and screen_name != "Unknown" and random.random() < 0.5:
            await self._wait_natural(1.0, 2.0)
            outputLog(f"[PROFILE] プロフィール閲覧: @{screen_name}")
            await self.fetch_user_profile(screen_name, session)
            await self._wait_natural(2.0, 4.0)
        
        await self._wait_natural(1.5, 3.5)
        
        if do_like:
            results['like'] = await self.like_tweet(tweet_id, session, referer=ref)
            await self._wait_natural(1.5, 3.0)
        
        if do_bookmark:
            results['bookmark'] = await self.bookmark_tweet(tweet_id, session, referer=ref)
            await self._wait_natural(0.5, 1.5)
        
        await self._wait_natural(2.0, 4.0)
        return results