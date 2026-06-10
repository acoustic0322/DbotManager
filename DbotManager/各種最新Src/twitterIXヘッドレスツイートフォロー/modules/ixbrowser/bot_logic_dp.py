import time
import os
import random
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Keys
from loguru import logger
import pyotp
from utils.human_action import sleep_random
import re

class IXBrowserBotLogicDP:
    def __init__(self, page: ChromiumPage):
        self.page = page
        
    def get_display_name(self):
        """
        Scrapes the current X display name from the UI (bottom left switcher button).
        """
        try:
            # Side navigation account switcher button usually contains the display name
            switcher = self.page.ele('css:[data-testid="SideNav_AccountSwitcher_Button"]', timeout=5)
            if switcher:
                # The text content of the switcher contains Display Name \n @handle
                text = switcher.text
                if text and "\n" in text:
                    return text.split("\n")[0].strip()
                elif text:
                    return text.strip()
        except Exception as e:
            logger.debug(f"Failed to scrape display name: {e}")
        return None


    def open_2fa_tab(self, secret):
        """
        Opens a 2FA generation site in a new tab, inputs secret, and generates code.
        User requested visual aid.
        """
        try:
            logger.info("Opening 2FA Generator Tab (User Request)...")
            tab = self.page.new_tab("https://2fa.f5.si/")
            if tab:
                # Wait for load
                tab.ele("#secret", timeout=10)
                
                # Input Secret
                tab.ele("#secret").input(secret)
                
                # Click Generate
                btn = tab.ele("xpath://button[contains(text(), '2FAコードを生成')]")
                if btn:
                    btn.click()
                    logger.success("2FA Code Generated in new tab.")
                else:
                    logger.warning("Generate button not found in 2FA tab.")
        except Exception as e:
            logger.error(f"Failed to open 2FA tab: {e}")

    def check_account_status(self):
        """
        Checks for Account Suspension, Lock, or Restriction based on URL.
        """
        try:
            logger.info("Checking account status...")
            current_url = self.page.url.lower()
            
            # 1. Suspended Check (Strict URL Match)
            if "account/suspended" in current_url:
                return "SUSPENDED", "Account is suspended (URL Match: /suspended)."
            
            # 2. Locked / Challenge Check (Strict URL Match)
            # Twitter redirects to /account/access when locked or needs verification
            if "account/access" in current_url:
                return "LOCKED", "Account is in Access/Challenge mode (URL Match: /access)."

            # 3. Arkose Challenge (Visible iframe)
            arkose_iframe = self.page.ele("css:iframe[src*='arkose']", timeout=0.1)
            if arkose_iframe and arkose_iframe.states.is_displayed:
                return "LOCKED", "Account is facing an Arkose Challenge (Captcha)."

            return "OK", "Account seems active."

            # [REFINED] Arkose / Challenge check
            arkose_iframe = self.page.ele("css:iframe[src*='arkose']", timeout=0.1)
            if arkose_iframe and arkose_iframe.states.is_displayed:
                 return "LOCKED", "Account requires authentication challenge (Arkose Visible)."
            
            unlock_btn = self.page.ele("css:[data-testid='confirmationSheetConfirm']", timeout=0.1) or \
                         self.page.ele("xpath://input[@type='submit'][@value='Start']", timeout=0.1) or \
                         self.page.ele("xpath://input[@type='submit'][@value='始める']", timeout=0.1)

            if unlock_btn and unlock_btn.states.is_displayed:
                 return "LOCKED", "Account requires validation start."

            return "OK", "Account seems active."

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return "UNKNOWN", f"Check failed: {e}"

    def _handle_verification_challenge(self):
        """
        Checks for verification screen, applies mouse wiggles, and waits for user resolution.
        """
        try:
            self.handle_retry_button()
            html = self.page.html.lower() if self.page.html else ""
            if "あなたがボットではないことを確認します" in html or "verifying you are human" in html:
                logger.warning("Bot verification challenge detected!")
                logger.info("Applying Anti-Detection moves (Mouse Wiggle)...")
                
                # Mouse Wiggle
                import random
                for _ in range(5):
                    x = random.randint(100, 500)
                    y = random.randint(100, 500)
                    try:
                        self.page.actions.move(x, y, duration=0.5)
                    except:
                        pass
                    time.sleep(0.5)

                logger.warning("Please solve the captcha manually if it persists...")
                
                # Wait for user to solve
                start_wait = time.time()
                while time.time() - start_wait < 120: # Wait up to 2 mins
                    time.sleep(1)
                    html_now = self.page.html.lower()
                    if "あなたがボットではないことを確認します" not in html_now and "verifying you are human" not in html_now:
                        logger.success("Verification screen passed (or gone).")
                        return True
                else:
                     logger.error("Verification timed out.")
                     return False
        except Exception as e:
            logger.error(f"Error in verification handler: {e}")
            return False

    def _is_valid_content(self, text):
        """
        Strict check for "Japanese Human" content.
        1. Must contain Hiragana (Language Check).
        2. Must NOT contain URLs (Link Check - filters news/affiliates).
        3. Must NOT contain commercial keywords (Spam Check).
        """
        if not text: return False
        
        # 1. Hiragana Check (Strict Japanese)
        if not re.search(r'[ぁ-ん]', text):
            return False
            
        # 2. URL Check (Filter out News/Promotion/Blog updates)
        if "http" in text or "t.co/" in text:
             return False
             
        # 3. NG Keywords (Commercial/Spam)
        ng_words = ["Amazon", "amzn", "楽天", "セール", "クーポン", "無料", "プレゼント", "当選", "公式", "Official", "Video", "Movie"]
        if any(w in text for w in ng_words):
            return False
            
        return True

    def engage_specific_user(self, username, count=3, like_rate=70, rt_rate=30):
        """
        Fallback logic: Visit specific user, Follow, then Engage with their tweets.
        """
        try:
            logger.info(f"FALLBACK: Targeting {username} for engagement...")
            
            # 1. Ensure Follow
            self.follow_by_username(username)
            sleep_random(3, 5)
            
            # 2. Engage with their tweets
            # Navigation to profile is done by follow_by_username, but ensure we are there
            if username not in self.page.url:
                 self.page.get(f"https://x.com/{username}")
                 sleep_random(4, 6)
            
            actions_done = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            logger.info(f"Engaging with {username}'s tweets...")
            
            while actions_done < count and scroll_attempts < max_scrolls:
                tweets = self.page.eles("css:article[data-testid='tweet']")
                
                if not tweets:
                    self.page.scroll.down(500)
                    sleep_random(2, 3)
                    scroll_attempts += 1
                    continue
                
                # Process tweets
                for tweet in tweets[:8]: # Look at top few
                    if actions_done >= count: break
                    
                    try:
                        # Skip if Pinned (Optional, but pinned is usually old)
                        # Identify pinned: text "Pinned" or "固定"
                        if "固定" in tweet.text or "Pinned" in tweet.text:
                            # It's fine to like pinned, but maybe we want fresh ones. Let's allow it for fallback.
                            pass
                            
                        # Logic similar to timeline
                        roll = random.randint(1, 100)
                        
                        # Like
                        if roll <= like_rate:
                            like_btn = tweet.ele("css:[data-testid='like']", timeout=0.1)
                            if like_btn:
                                like_btn.click()
                                logger.info(f"❤️ Like performed on {username}.")
                                actions_done += 1
                                sleep_random(2, 4)
                        
                        # RT
                        roll_rt = random.randint(1, 100)
                        if roll_rt <= rt_rate:
                             rt_btn = tweet.ele("css:[data-testid='retweet']", timeout=0.1)
                             if rt_btn:
                                 rt_btn.click()
                                 sleep_random(1, 2)
                                 confirm_rt = self.page.ele("css:[data-testid='retweetConfirm']", timeout=2)
                                 if confirm_rt:
                                     confirm_rt.click()
                                     logger.info(f"🔄 Retweet performed on {username}.")
                                     actions_done += 1
                                     sleep_random(2, 4)

                    except Exception as e:
                        logger.error(f"Error acting on tweet: {e}")
                        continue
                
                self.page.scroll.down(600)
                scroll_attempts += 1
                sleep_random(2, 4)
                
            return actions_done

        except Exception as e:
            logger.error(f"Specific user engagement failed: {e}")
            return 0

    def _select_language_option(self, scope, *, keywords, timeout=5):
        """
        言語選択UI上で、指定キーワードを含む言語行(ラベル/行)をクリックして選択状態まで確認する。
        """
        # ... (Method body omitted for brevity, logic remains same, just ensuring context) ...
        # できるだけ「行(ラベル)」をクリックする（input単体クリックより状態が反映されやすい）
        kw_pred = " or ".join([f"contains(normalize-space(.), '{kw}')" for kw in keywords])
        # label > span 構造 / div role=option / div role=radio などをまとめて拾う
        row = scope.ele(
            f"xpath:.//label[.//span[{kw_pred}]]"
            f" | .//*[@role='option'][.//span[{kw_pred}]]"
            f" | .//*[@role='radio'][.//span[{kw_pred}]]"
            f" | .//div[.//span[{kw_pred}]]",
            timeout=timeout,
        )

        if not row:
            return False

        try:
            row.scroll.to_see()
        except Exception:
            pass

        # クリックは段階的に強める
        for _ in range(3):
            try:
                row.click()
            except Exception:
                try:
                    row.click(by_js=True)
                except Exception:
                    try:
                        row.run_js("this.click()")
                    except Exception:
                        pass

            sleep_random(0.6, 1.2)

            # 選択状態の検証（複数属性を試す）
            try:
                aria_selected = row.attr("aria-selected")
                aria_checked = row.attr("aria-checked")
                data_selected = row.attr("data-selected")
                if aria_selected == "true" or aria_checked == "true" or data_selected == "true":
                    return True
            except Exception:
                pass

            # input checked の検証
            try:
                inp = row.ele("css:input[type='checkbox'],input[type='radio']", timeout=0.2)
                if inp:
                    checked = inp.attr("checked")
                    aria_checked = inp.attr("aria-checked")
                    if checked is not None or aria_checked == "true":
                        return True
            except Exception:
                pass

        return True  # 最後まで明確に取れなくてもクリックは通っている可能性が高いので True 扱い

    def _click_primary_dialog_button(self, *, keywords=None, timeout=5):
        """
        多言語でも動くように、ダイアログ内の「主ボタン(Next/Save/Done等)」をクリックする。
        優先: data-testid -> white text style -> keyword text
        """
        dialog = self.page.ele("css:[role='dialog']")
        scope = dialog if dialog else self.page

        # 1) data-testid (言語非依存)
        btn = scope.ele('css:[data-testid="ChoiceSelectionNextButton"]', timeout=0.5)
        if btn:
            try:
                btn.scroll.to_see()
            except Exception:
                pass
            try:
                btn.click(by_js=True)
                return True
            except Exception:
                try:
                    btn.run_js("this.click()")
                    return True
                except Exception:
                    pass

        # 2) white text style (言語非依存・UI依存)
        # Selenium版の //span[text()='Next']/ancestor::div[contains(@style,'color: rgb(255, 255, 255)')] を一般化
        styled = scope.eles("xpath:.//*[contains(@style, 'color: rgb(255, 255, 255)')]")
        # 末尾が主ボタンであることが多い
        for el in reversed(styled):
            try:
                if not el.states.is_displayed:
                    continue
            except Exception:
                pass

            # クリック対象をbutton/role=buttonまで持ち上げる
            target = None
            try:
                target = el.ele("xpath:ancestor::button[1]", timeout=0.01)
            except Exception:
                target = None
            if not target:
                try:
                    target = el.ele("xpath:ancestor::*[@role='button'][1]", timeout=0.01)
                except Exception:
                    target = None
            if not target:
                target = el

            try:
                # disabledなら次へは無理なのでスキップ
                if target.attr("disabled") is not None or target.attr("aria-disabled") == "true":
                    continue
            except Exception:
                pass

            try:
                target.scroll.to_see()
            except Exception:
                pass
            try:
                target.run_js("this.click()")
                return True
            except Exception:
                try:
                    target.click(by_js=True)
                    return True
                except Exception:
                    continue

        # 3) keyword text fallback (言語依存・最後の保険)
        if keywords:
            for kw in keywords:
                spans = scope.eles(f"xpath:.//span[normalize-space()='{kw}']")
                for sp in reversed(spans):
                    try:
                        btn = sp.ele("xpath:ancestor::button[1]", timeout=0.01)
                    except Exception:
                        btn = None
                    target = btn if btn else sp
                    try:
                        target.run_js("this.click()")
                        return True
                    except Exception:
                        try:
                            target.click(by_js=True)
                            return True
                        except Exception:
                            pass

        # 4) Enter fallback
        try:
            self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
            return True
        except Exception:
            return False

    def handle_interstitial_popups(self):
        """
        Checks for and closes common interstitial popups (ToS updates, etc).
        """
        try:
            # [OPTIMIZED] Strict timeout to prevent freezing when no popups exist (reduced to 1s)
            got_it_btn = self.page.ele("xpath://span[text()='Got it'] | //span[text()='OK'] | //span[text()='了解'] | //span[contains(text(), 'Updates to our Terms')]//ancestor::div//button[.//span[text()='Got it']]", timeout=1.0)
            
            if got_it_btn and got_it_btn.states.is_displayed:
                logger.info("Found interstitial popup ('Got it'). Clicking to dismiss...")
                try:
                    got_it_btn.click()
                except Exception as click_err:
                    logger.warning(f"Standard click failed on interstitial button, using JS fallback: {click_err}")
                    self.page.run_js("arguments[0].click();", got_it_btn)
                sleep_random(1, 2)
                return
            
            # Privacy policy specific check (reduced timeout to 0.5s)
            tos_text = self.page.ele("text:Updates to our Terms of Service", timeout=0.5)
            if tos_text:
                 logger.info("Found ToS Popup (text detected). Looking for button...")
                 dialog = self.page.ele("css:[role='dialog']", timeout=1.0)
                 if dialog:
                     btn = dialog.ele("css:[role='button']", timeout=0.5) 
                     if btn:
                         btn.click()
                         sleep_random(1, 2)
        except Exception as e:
            pass

    def get_jf_error_message(self):
        """Return visible JustFix-style form error text, if present."""
        try:
            error_nodes = self.page.eles("css:svg[data-icon='icon-error-triangle']")
            for icon in error_nodes:
                try:
                    container = icon.ele("xpath:ancestor::div[contains(@class, 'jf-element')][1]", timeout=0.1)
                    scope = container.ele("xpath:ancestor::div[contains(@class, 'jf-element')][1]", timeout=0.1) if container else None
                    text = (scope.text if scope else container.text).strip()
                    if text:
                        return text
                except Exception:
                    pass

            generic = self.page.ele(
                "xpath://p[contains(., '問題が発生しました') or contains(., 'もう一度お試しください') or contains(., 'Something went wrong') or contains(., 'try again')]",
                timeout=0.1,
            )
            if generic:
                return generic.text.strip()
        except Exception:
            pass
        return None

    def handle_jf_error_message(self, username, stage, retry_click=None):
        """Handle transient JustFix-style form errors; returns True if still failing."""
        msg = self.get_jf_error_message()
        if not msg:
            return False

        logger.warning(f"[{username}] JF form error at {stage}: {msg}")
        retryable = "問題が発生しました" in msg or "もう一度" in msg or "Something went wrong" in msg or "try again" in msg.lower()
        if retryable and retry_click:
            sleep_random(2, 4)
            try:
                logger.info(f"[{username}] Retrying {stage} after JF form error...")
                retry_click()
                sleep_random(3, 5)
            except Exception as e:
                logger.warning(f"[{username}] Retry click failed at {stage}: {e}")
            msg_after = self.get_jf_error_message()
            if not msg_after:
                logger.info(f"[{username}] JF form error cleared after retry.")
                return False
            logger.warning(f"[{username}] JF form error remained after retry: {msg_after}")
        return True

    def handle_jf_error_message(self, username, stage, retry_click=None):
        """Treat any visible JustFix-style form error as a profile reset trigger."""
        msg = self.get_jf_error_message()
        if not msg:
            return False
        logger.warning(f"[{username}] JF form error at {stage}: {msg}")
        return True

    def classify_jf_error_message(self, msg):
        if not msg:
            return None
        if "ログインを一時的に制限しました" in msg or "しばらくしてから" in msg:
            return "TEMP_LOGIN_LIMIT"
        return f"JF_ERROR:{msg}"

    def force_japanese_language(self):
        """言語を日本語に変更 (User Provided Friend's Logic Integrated)"""
        logger.info("🌐 言語を日本語に変更中 (Force Japanese - Friend Logic Ver)...")
        
        try:
            # 0. Check if already Japanese
            try:
                html_lang = self.page.ele("css:html").attr("lang")
                if html_lang == "ja":
                    logger.success("🌐 Already set to Japanese (html lang='ja'). Skipping.")
                    return
                if self.page.ele("xpath://span[text()='ホーム']"):
                    logger.success("🌐 Already set to Japanese (Found 'ホーム'). Skipping.")
                    return
            except:
                pass

            # Settingsへ移動クリックできない時の保険
            self.page.get("https://x.com/settings")
            sleep_random(5, 8)
            self.handle_interstitial_popups()
            
            # 1. Accessibility
            logger.info("    - Accessibility... クリック")
            acc_link = self.page.ele('css:a[data-testid="accessibilityLink"]', timeout=15) or \
                       self.page.ele('xpath://span[contains(text(), "Accessibility")]', timeout=1)
            if acc_link:
                acc_link.click(by_js=True)
                sleep_random(3, 5)
            
            # 2. Languages
            logger.info("    - Languages クリック")
            lang_link = self.page.ele('css:a[href="/settings/languages"]', timeout=15) or \
                        self.page.ele('xpath://span[contains(text(), "Languages")]', timeout=1)
            if lang_link:
                lang_link.click(by_js=True)
                sleep_random(3, 5)
            
            # 3. App/Display languages
            logger.info("    - App languages クリック")
            # Universal href selector verified from user HTML (Robust against all languages)
            app_lang = self.page.ele('css:a[href*="uls_content_and_app_language_selector"]', timeout=5) or \
                       self.page.ele('xpath://span[contains(text(), "App and post languages")]', timeout=1) or \
                       self.page.ele('xpath://span[contains(text(), "Display language")]', timeout=1) or \
                       self.page.ele('xpath://span[contains(text(), "Bahasa")]', timeout=1)
            
            if app_lang:
                app_lang.click(by_js=True)
                sleep_random(3, 5)
            
            # 4. Search '日本語'
            logger.info("    - '日本語' を検索")
            search_input = self.page.ele('css:input[data-testid="ChoiceSelectionInput"]', timeout=10)
            if search_input:
                search_input.clear()
                sleep_random(0.3, 0.5)
                search_input.input("日本語")
                sleep_random(2, 3)

            # 5. 日本語のチェックボックスをクリック（友人のロジックに合わせてシンプルに）
            logger.info("    - 日本語のチェックボックスをクリック")
            try:
                checkbox = self.page.ele('css:input[type="checkbox"]', timeout=5)
                if checkbox:
                    checkbox.click(by_js=True)
                    logger.info("    - チェックボックスクリック成功")
                    sleep_random(1, 2)
                else:
                    logger.warning("    - チェックボックスが見つかりませんでした")
            except Exception as e:
                logger.error(f"    - チェックボックスエラー: {e}")
            
            # 6. Next クリック（1回目）- 友人のロジック完全準拠 (Text Match FIRST)
            logger.info("    - Next クリック（1回目）...")
            try:
                next_btn = None
                
                # Strategy 1: Keywords (Primary - User Requested Logic)
                # 多言語対応キーワードリスト
                next_keywords = [
                    "Next", "次へ",  # 英語、日本語
                    "Lanjut", "ต่อไป",  # インドネシア語、タイ語
                    "Siguiente", "Próximo",  # スペイン語、ポルトガル語
                    "Suivant", "Weiter", "Volgende",  # フランス語、ドイツ語、オランダ語
                    "İleri",  # トルコ語
                    "Далее",  # ロシア語
                    "التالي",  # アラビア語
                    "Tiếp theo", # ベトナム語
                ]
                
                for kw in next_keywords:
                    try:
                         # 友人のロジック準拠: //span[contains(text(), 'Next')]
                         # 大文字小文字や部分一致許容のため contains を使用
                         btn = self.page.ele(f"xpath://span[contains(text(), '{kw}')]", timeout=0.1)
                         if btn:
                             next_btn = btn
                             logger.info(f"    - Nextボタン発見（キーワード: {kw}）")
                             break
                    except:
                        continue

                # Strategy 2: Data Test ID (Fallback)
                if not next_btn:
                    logger.warning("    - Nextボタン(Keyword)なし -> data-testid試行...")
                    next_btn = self.page.ele('css:[data-testid="ChoiceSelectionNextButton"]', timeout=3)

                # Strategy 3: Style (Fallback)
                if not next_btn:
                     logger.warning("    - Nextボタン(data-testid)なし -> Style試行...")
                     next_btn = self.page.ele("xpath://div[@role='button']//span[contains(@style, 'color: rgb(255, 255, 255)')]", timeout=1) or \
                                self.page.ele("xpath://button//span[contains(@style, 'color: rgb(255, 255, 255)')]", timeout=1)

                if next_btn:
                    try:
                        # Ensure we scroll to it
                        next_btn.scroll.to_see()
                        # Click
                        next_btn.click(by_js=True)
                        logger.info("    - Next クリック成功")
                    except Exception as e:
                        logger.error(f"    - Next クリック失敗: {e}")
                        try:
                            next_btn.run_js("this.click()")
                            logger.info("    - Next クリック成功（直接JS実行）")
                        except Exception as e2:
                            logger.error(f"    - 直接JS実行も失敗: {e2}")
                else:
                    logger.warning("    - Nextボタンが見つかりませんでした")
                sleep_random(3, 5)
            except Exception as e:
                logger.error(f"    - Next エラー: {e}")
                import traceback
                logger.debug(traceback.format_exc())

            # 7. ラジオボタン（2番目）をクリック - 友人のロジックに合わせて
            logger.info("    - ラジオボタンクリック")
            try:
                radio = self.page.ele('css:input[aria-posinset="2"]', timeout=5)
                if radio:
                    radio.click(by_js=True)
                    logger.info("    - ラジオボタンクリック成功")
                    sleep_random(2, 3)
                else:
                    logger.warning("    - ラジオボタンが見つかりませんでした")
            except Exception as e:
                logger.error(f"    - ラジオボタンエラー: {e}")
            
            # 8. Next クリック（2回目）- 友人のロジック完全準拠 (User Provided Snippet Logic)
            logger.info("    - Next クリック（2回目）")
            try:
                sleep_random(1, 2)
                
                next_keywords = [
                    "Next", "次へ",
                    "Lanjut", "ต่อไป",
                    "Siguiente", "Próximo",
                    "Suivant", "Weiter", "Volgende",
                    "İleri", "Далее", "التالي", "Tiếp theo",
                ]
                
                target_element = None
                
                # Priority 1: Styled Div (White Text) with Keyword
                for kw in next_keywords:
                    try:
                        next_divs = self.page.eles(f"xpath://span[text()='{kw}']/ancestor::div[contains(@style, 'color: rgb(255, 255, 255)')]", timeout=0.1)
                        if next_divs:
                            target_element = next_divs[-1]
                            logger.info(f"    - Next div発見（キーワード: {kw}）")
                            break
                    except:
                        continue
                
                # Priority 2: Span Only (Fallback)
                if not target_element:
                    for kw in next_keywords:
                        try:
                            next_spans = self.page.eles(f"xpath://span[text()='{kw}']", timeout=0.1)
                            if next_spans:
                                target_element = next_spans[-1]
                                logger.info(f"    - Next span発見（キーワード: {kw}）")
                                break
                        except:
                            continue
                
                if target_element:
                    target_element.click(by_js=True)
                    logger.info("    - Next クリック成功")
                else:
                    logger.warning("    - Nextボタンが見つかりませんでした")
                
                sleep_random(3, 5)
            except Exception as e:
                logger.error(f"    - Next エラー: {e}")

        except Exception as e:
            logger.error(f"Error in force_japanese_language: {e}")

    def login_with_token(self, auth_token, ct0=None, username=None, password=None, email=None, totp_secret=None):
        """
        Attempts to login using auth_token and ct0.
        Prioritizes existing browser session to avoid accidental logouts.
        """
        try:
            logger.info(f"[{username}] Checking existing session...")
            if "x.com" in self.page.url:
                logger.info("Already on X.com. Refreshing session...")
                self.page.refresh()
                sleep_random(5, 8)
                
                # [NEW] プレミアム勧誘ポップアップ/ページ対策 (URL+要素の多角チェック)
                is_premium = (
                    "premium_sign_up" in self.page.url.lower() or
                    self.page.ele("text:Premiumに登録", timeout=0.5) or
                    self.page.ele("text:Subscribe to Premium", timeout=0.5) or
                    self.page.ele("xpath://svg[.//path[starts-with(@d, 'M10.59 12')]]", timeout=0.5)
                )
                if is_premium:
                    logger.warning(f"[{username}] Premium sign-up screen detected. Trying to close and redirect...")
                    try:
                        close_btn = self.page.ele("css:[data-testid='app-bar-close']", timeout=5) or \
                                    self.page.ele("css:[aria-label='Close']", timeout=1) or \
                                    self.page.ele("css:[aria-label='閉じる']", timeout=1) or \
                                    self.page.ele("xpath://svg[.//path[starts-with(@d, 'M10.59 12')]]", timeout=1)
                        if close_btn:
                            try:
                                close_btn.click()
                            except Exception:
                                close_btn.click(by_js=True)
                            sleep_random(2, 3)
                            logger.info(f"[{username}] Clicked close button on premium screen.")
                    except Exception as e_close:
                        logger.warning(f"[{username}] Close button click failed: {e_close}")
                    
                    # 確実にホームに強制遷移する
                    logger.info(f"[{username}] Forcing navigation to /home to escape premium screen...")
                    try:
                        self.page.get("https://x.com/home")
                        sleep_random(5, 8)
                    except Exception as e_home:
                        logger.error(f"[{username}] Failed to force get home: {e_home}")
            else:
                self.page.get("https://x.com/home")
                sleep_random(5, 8)
            
            # [FIX] 「やりなおす」ボタンの徹底排除
            for _ in range(3):
                if self.handle_retry_button():
                    sleep_random(3, 5)
                else:
                    break

            # 1. すでにログイン済みかチェック（最優先）
            has_local_cookie = False
            try:
                local_cookies = self.page.cookies()
                has_local_cookie = any(c.get('name') == 'auth_token' and c.get('value') for c in local_cookies)
            except Exception as ce:
                logger.debug(f"Failed to check local cookies: {ce}")

            timeout_home = 15 if has_local_cookie else 7
            if has_local_cookie:
                logger.info(f"[{username}] Local auth_token cookie detected in profile. Waiting up to {timeout_home}s for session to stabilize...")

            if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=timeout_home) or self.page.ele("css:[data-testid='SideNav_AccountSwitcher_Button']", timeout=1):
                logger.success(f"[{username}] Active session detected. Preserving this session.")
                return True, self.get_current_cookies()

            # 2. ログイン画面に飛ばされているかチェック
            if "login" in self.page.url or self.page.ele("css:[data-testid='loginButton']", timeout=2):
                logger.warning(f"[{username}] Redirected to login page. Session might be expired.")

            import pandas as pd
            if not auth_token or (isinstance(auth_token, float) and pd.isna(auth_token)) or str(auth_token).strip() == "":
                logger.warning(f"[{username}] DB auth_token is empty. Cannot inject.")
                return False, None

            logger.info(f"[{username}] Session not active. Injecting cookies from DB...")
            cookies = [{'name': 'auth_token', 'value': str(auth_token).strip(), 'domain': '.x.com', 'path': '/', 'secure': True, 'httpOnly': True}]
            if ct0 and not (isinstance(ct0, float) and pd.isna(ct0)) and str(ct0).strip() != "":
                cookies.append({'name': 'ct0', 'value': str(ct0).strip(), 'domain': '.x.com', 'path': '/', 'secure': True, 'httpOnly': False})
            
            self.page.set.cookies(cookies)
            time.sleep(random.uniform(3.0, 7.0))
            self.page.refresh()
            sleep_random(5, 8)
            
            # [NEW] プレミアム勧誘ポップアップ/ページ対策 (URL+要素の多角チェック)
            is_premium = (
                "premium_sign_up" in self.page.url.lower() or
                self.page.ele("text:Premiumに登録", timeout=0.5) or
                self.page.ele("text:Subscribe to Premium", timeout=0.5) or
                self.page.ele("xpath://svg[.//path[starts-with(@d, 'M10.59 12')]]", timeout=0.5)
            )
            if is_premium:
                logger.warning(f"[{username}] Premium sign-up screen detected. Trying to close and redirect...")
                try:
                    close_btn = self.page.ele("css:[data-testid='app-bar-close']", timeout=5) or \
                                self.page.ele("css:[aria-label='Close']", timeout=1) or \
                                self.page.ele("css:[aria-label='閉じる']", timeout=1) or \
                                self.page.ele("xpath://svg[.//path[starts-with(@d, 'M10.59 12')]]", timeout=1)
                    if close_btn:
                        try:
                            close_btn.click()
                        except Exception:
                            close_btn.click(by_js=True)
                        sleep_random(2, 3)
                        logger.info(f"[{username}] Clicked close button on premium screen.")
                except Exception as e_close:
                    logger.warning(f"[{username}] Close button click failed: {e_close}")
                
                # 確実にホームに強制遷移する
                logger.info(f"[{username}] Forcing navigation to /home to escape premium screen...")
                try:
                    self.page.get("https://x.com/home")
                    sleep_random(5, 8)
                except Exception as e_home:
                    logger.error(f"[{username}] Failed to force get home: {e_home}")

            try: self.page.stop_loading() 
            except: pass
            
            # [ADD] リロード後に再度「やりなおす」が出る場合があるためチェック
            self.handle_retry_button()
            self.handle_interstitial_popups()
            self._handle_verification_challenge()
            
            # 6. Status Verification (Moved down to be more natural)
            # ログインが通っているかだけをまず確認
            if not ("home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=7)):
                 # もしホームに行けてないならステータスチェック
                 status, msg = self.check_account_status()
                 if status in ["LOCKED", "SUSPENDED"]:
                     return status, None
                 logger.warning(f"[{username}] Token injection might have failed. Final URL: {self.page.url}")
                 return False, None

            logger.success(f"[{username}] Token login successful via injection.")
            
            # [STEALTH] ログイン成功後のTL観覧シーケンス
            # [TL読み込み無視] Skipping timeline browsing to prevent freezing and save time
            logger.info(f"[{username}] Ignoring/Skipping timeline browsing warm-up as requested.")
            
            # 最後にステータスを裏で確認（人間らしいタイミング）
            status, msg = self.check_account_status()
            logger.info(f"Final status check: {status}")

            return True, self.get_current_cookies()

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False, None

    def handle_retry_button(self):
        """[AGGRESSIVE] Checks for 'やりなおす' button variants and clicks until they are gone."""
        found_total = False
        for i in range(5):
            try:
                # Combined single xpath check using text() or contains(text(), ...) which is extremely fast.
                # Avoid using '.' or normalize-space(.) on '*' because it recursively processes the entire descendant tree and freezes the CPU.
                btn = self.page.ele("xpath://*[text()='やりなおす' or text()='やり直す' or text()='Start over' or text()='start over' or text()='Retry' or text()='retry' or contains(text(), 'やりなおす') or contains(text(), 'やり直す') or contains(text(), 'Start over') or contains(text(), 'start over') or contains(text(), 'Retry') or contains(text(), 'retry')]", timeout=1.0)
                if btn and btn.states.is_displayed:
                    text_found = btn.text.strip() if btn.text else "やりなおす/Start over"
                    logger.warning(f"Retry button '{text_found}' detected (Attempt {i+1}). Clicking to recover...")
                    
                    # 1. Elevate click target to parent button or role='button' if possible
                    target = None
                    try:
                        target = btn.ele("xpath:ancestor::button[1]", timeout=0.05)
                    except:
                        pass
                    if not target:
                        try:
                            target = btn.ele("xpath:ancestor::*[@role='button'][1]", timeout=0.05)
                        except:
                            pass
                    if not target:
                        target = btn
                        
                    # 2. Click with robust fallback sequence
                    clicked = False
                    try:
                        target.scroll.to_see()
                        sleep_random(0.3, 0.6)
                        self.page.actions.move_to(target).click()
                        clicked = True
                    except Exception as click_err:
                        logger.warning(f"Physical action click failed on retry button: {click_err}")
                        
                    if not clicked:
                        try:
                            target.click(timeout=3)
                            clicked = True
                        except Exception as click_err:
                            logger.warning(f"Standard click failed on retry button: {click_err}")
                            
                    if not clicked:
                        try:
                            target.click(by_js=True)
                            clicked = True
                            logger.info("Clicked retry button via by_js=True.")
                        except Exception as click_err:
                            logger.warning(f"JS click failed on retry button: {click_err}")
                            
                    if not clicked:
                        try:
                            target.run_js("this.click()")
                            clicked = True
                            logger.info("Clicked retry button via run_js.")
                        except Exception as click_err:
                            logger.error(f"All click methods failed on retry button: {click_err}")
                            
                    sleep_random(3, 5)
                    found_total = True
                else:
                    break
            except Exception as e:
                logger.debug(f"Error handling retry button: {e}")
                break
        return found_total

    def login_with_password(self, username, password, email=None, totp_secret=None, show_2fa_tab=False):
        """
        Logs into X.com using Username/Password (and Email if challenged).
        """
        try:
            logger.info(f"Performing Password Login for {username}...")
            
            # [Double-Safety Net] すでにログイン済みの場合は即リターン
            is_logged_in = (
                "home" in self.page.url or 
                self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=3) or 
                self.page.ele("css:[data-testid='SideNav_AccountSwitcher_Button']", timeout=1)
            )
            if is_logged_in:
                logger.success(f"[{username}] Already logged in at start of password login. Preserving session.")
                return True

            # 1. Go to Home first (Human-like)
            if "x.com" not in self.page.url:
                logger.info("Visiting x.com landing page first...")
                self.page.get("https://x.com/")
            
            sleep_random(3, 6)
            
            # 1.1 Click Login Button if on landing page
            jf_form_present = self.page.ele("css:#jf-input-username_or_email", timeout=1) or \
                              self.page.ele("css:input[name='username_or_email']", timeout=0.5)
            if not jf_form_present and "login" not in self.page.url and "home" not in self.page.url:
                login_btn = self.page.ele("css:[data-testid='loginButton']", timeout=5) or \
                            self.page.ele("xpath://span[text()='ログイン']", timeout=1) or \
                            self.page.ele("xpath://span[text()='Log in']", timeout=1)
                
                if login_btn:
                    logger.info("Clicking Login button from landing page...")
                    login_btn.click()
                    sleep_random(3, 5)
                else:
                    # Fallback to direct URL if button not found
                    logger.warning("Login button not found, jumping to login flow...")
                    self.page.get("https://x.com/")
                    sleep_random(4, 6)
            
            # [Anti-Detection] 人間らしいマウス操作
            # 人間らしいマウス操作
            try:
                import random as _random
                for _ in range(_random.randint(2, 4)):
                    self.page.actions.move_to((_random.randint(150, 750), _random.randint(150, 550)))
                    time.sleep(_random.uniform(0.2, 0.5))
            except: pass
            
            # 1.5 Check if already logged in (redirected to home)
            if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']"):
                logger.success("Already logged in (Home detected).")
                return True
            
            # [REFINED] 「やり直す」ボタンの徹底排除 (強化された共通メソッドを呼び出す)
            self.handle_retry_button()

            # 2. Input Username
            logger.info("Inputting Username...")
            username_input = None
            
            # Try multiple selectors
            for _ in range(3): # Retry logic
                self.handle_retry_button() # [ADD] 入力前にも念のためチェック
                # Use part-match to handle multi-values (e.g. autocomplete="username webauthn") and custom gateways
                username_input = self.page.ele("css:#jf-input-username_or_email", timeout=2) or \
                                 self.page.ele("css:input[name='username_or_email']", timeout=1) or \
                                 self.page.ele("css:input[autocomplete*='username']", timeout=5) or \
                                 self.page.ele("css:input[name='text']", timeout=1) or \
                                 self.page.ele("css:input[id*='username_or_email']", timeout=1)
                if username_input: break
                
                logger.warning("Username input not found, refreshing...")
                self.page.refresh()
                sleep_random(3, 5) # Reduced refresh wait

            if not username_input:
                logger.error("Username input field not found after retries.")
                return False
                
            input_username = f"@{username}" if username.isdigit() else username
            username_input.click()
            sleep_random(0.3, 0.6)
            self.human_typing(username_input, input_username)
            # Click Next (頑健な部分一致と複数タグ判定に変更)
            next_keywords = ["Next", "次へ", "Lanjut", "ต่อไป", "Siguiente", "Próximo", "Suivant", "Weiter", "Volgende", "İleri", "Далее", "التالي", "Tiếp theo"]
            kw_pred = " or ".join([f"contains(., '{kw}')" for kw in next_keywords])
            next_btn = self.page.ele("css:button[type='submit']", timeout=1) or \
                       self.page.ele(f"xpath://p[{kw_pred}]/ancestor::button[1] | //span[{kw_pred}] | //div[@role='button'][{kw_pred}] | //button[{kw_pred}]", timeout=5)
            
            if not next_btn:
                next_btn = self.page.ele("css:[data-testid='identifierNext']", timeout=1)
                
            if next_btn:
                self.stealth_click(next_btn)
            else:
                logger.warning("Next button not found, sending Enter key...")
                self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
            sleep_random(2, 3) 
            if self.handle_jf_error_message(
                username,
                "username submit",
                retry_click=lambda: self.stealth_click(next_btn, wait_after=False) if next_btn else self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER),
            ):
                return self.classify_jf_error_message(self.get_jf_error_message()) or "JF_ERROR_USERNAME"
            
            # 3. Handle Unusual Activity / Email Verification (Optional)
            if self.page.ele("text:Phone or email") or self.page.ele("text:Email address"):
                logger.info("Email verification challenge detected.")
                if not email:
                    logger.error("Email required for verification but not provided.")
                    return False
                
                email_input = self.page.ele("css:input[name='text']")
                if email_input:
                    email_input.input(email)
                    sleep_random(0.5, 1)
                    # Click Next again
                    next_btns = self.page.eles("xpath://span[text()='Next'] | //span[text()='次へ']")
                    if next_btns:
                         next_btns[-1].click()
                    sleep_random(2, 3)
            
            # 4. Input Password
            logger.info("Inputting Password...")
            self.handle_retry_button() # [ADD] パスワード入力前にもチェック
            password_input = self.page.ele("css:#jf-input-password", timeout=3) or \
                             self.page.ele("css:input[autocomplete='current-password']", timeout=2) or \
                             self.page.ele("css:input[name='password'][required]", timeout=2) or \
                             self.page.ele("css:input[name='password']", timeout=3)
            if not password_input:
                # Check directly for home again just in case
                if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']"):
                    return True
                
                # Check for various account lock / verification / suspension screens
                lock_keywords = [
                    "セキュリティ検証", "認証コード", "電話番号", "確認してください", "アカウントを保護", 
                    "ロボットではない", "不審なアクティビティ", "ロックされています", "unusual activity", 
                    "verify your", "confirmation code", "protect your account", "confirm your phone", 
                    "prove you're not a robot", "limited some of your", "一時的に制限"
                ]
                for kw in lock_keywords:
                    if self.page.ele(f"text:{kw}", timeout=1):
                        logger.warning(f"🔒 [{username}] Password field missing due to lock/verification screen: '{kw}'")
                        return "LOCKED"

                suspension_keywords = [
                    "凍結されています", "無効になっています", "suspended", "deactivated"
                ]
                for kw in suspension_keywords:
                    if self.page.ele(f"text:{kw}", timeout=1):
                        logger.error(f"❌ [{username}] Password field missing due to suspension screen: '{kw}'")
                        return "SUSPENDED"

                # [NEW/RESTORE] パスワード欄が見つからない異常事態を報告
                logger.error(f"Password input field not found for {username}. Returning PASSWORD_FIELD_MISSING.")
                return "PASSWORD_FIELD_MISSING"

            if self.page.ele('text:セキュリティ検証の実行', timeout=3):
                logger.warning(f"🔒 [{username}] セキュリティ検証を検知 → ロック")
                return "LOCKED"
            
            # Robust Input Sequence using Actions (simulating keyboard)
            logger.info("  - Clicking password field...")
            password_input.click()
            sleep_random(0.2, 0.5)
            password_input.clear()
            sleep_random(0.2, 0.4)
            logger.info("  - Typing password using keyboard actions...")
            self.human_typing(password_input, password)
            
            # Trigger Blur
            try:
                self.page.ele("css:h1").click(timeout=1)
            except:
                pass
            
            sleep_random(0.5, 1)

            # Verify
            if not password_input.value:
                logger.warning("  - Field still empty? Trying JS injection fallback...")
                password_input.run_js(f"this.value = '{password}'; this.dispatchEvent(new Event('input', {{ bubbles: true }}));")
                sleep_random(0.5, 1)
            
            # 5. Click Login (頑健な部分一致と複数タグ判定に変更)
            logger.info("Clicking Login button...")
            login_btn = self.page.ele("css:button[type='submit']", timeout=1) or \
                        self.page.ele("css:[data-testid='LoginForm_Login_Button']")
            if not login_btn:
                login_keywords = ["Log in", "ログイン", "Sign in", "ログインする", "ログイン ボタン"]
                kw_login_pred = " or ".join([f"contains(., '{kw}')" for kw in login_keywords])
                login_btn = self.page.ele(f"xpath://p[{kw_login_pred}]/ancestor::button[1] | //span[{kw_login_pred}] | //div[@role='button'][{kw_login_pred}] | //button[{kw_login_pred}]", timeout=5)

            if login_btn:
                if login_btn.attr("aria-disabled") == "true":
                    logger.warning("Login button is disabled.")
                self.stealth_click(login_btn, wait_after=False)
            else:
                logger.warning("Login button not found, sending Enter key...")
                self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
            sleep_random(1, 2)
            if self.handle_jf_error_message(
                username,
                "password submit",
                retry_click=lambda: self.stealth_click(login_btn, wait_after=False) if login_btn else self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER),
            ):
                return self.classify_jf_error_message(self.get_jf_error_message()) or "JF_ERROR_PASSWORD"

            # Wait for home load detection instead of fixed sleep
            logger.info("Waiting for Home redirect (up to 30s)...")
            totp_done = False
            
            for loop_idx in range(30):
                # 10秒以上経ってもホームに到達せず、かつURLがhomeでないなら強制的にhomeへ遷移を試みる
                if loop_idx == 10 and not ("home" in self.page.url):
                    logger.warning(f"[{username}] Home not reached in 10s. Forcing get('https://x.com/home')...")
                    try:
                        self.page.get("https://x.com/home")
                        sleep_random(3, 5)
                    except Exception as e_home:
                        logger.error(f"[{username}] Failed to force get home: {e_home}")

                if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=0.1):
                    logger.success("Password login successful.")

                    # [STEALTH] ログイン成功後の「慣らし」シーケンス
                    # 1. まずランダムな時間静止
                    wait_time = random.uniform(4.0, 10.0)
                    logger.info(f"[{username}] Login success. Waiting {wait_time:.1f}s before refresh...")
                    time.sleep(wait_time)
                    
                    # 2. リロード
                    logger.info(f"[{username}] Refreshing page...")
                    self.page.refresh()
                    sleep_random(5, 8)
                    
                    # [NEW] プレミアム勧誘ポップアップ/ページ対策 (URL+要素の多角チェック)
                    is_premium = (
                        "premium_sign_up" in self.page.url.lower() or
                        self.page.ele("text:Premiumに登録", timeout=0.5) or
                        self.page.ele("text:Subscribe to Premium", timeout=0.5) or
                        self.page.ele("xpath://svg[.//path[starts-with(@d, 'M10.59 12')]]", timeout=0.5)
                    )
                    if is_premium:
                        logger.warning(f"[{username}] Premium sign-up screen detected. Trying to close and redirect...")
                        try:
                            close_btn = self.page.ele("css:[data-testid='app-bar-close']", timeout=5) or \
                                        self.page.ele("css:[aria-label='Close']", timeout=1) or \
                                        self.page.ele("css:[aria-label='閉じる']", timeout=1) or \
                                        self.page.ele("xpath://svg[.//path[starts-with(@d, 'M10.59 12')]]", timeout=1)
                            if close_btn:
                                try:
                                    close_btn.click()
                                except Exception:
                                    close_btn.click(by_js=True)
                                sleep_random(2, 3)
                                logger.info(f"[{username}] Clicked close button on premium screen.")
                        except Exception as e_close:
                            logger.warning(f"[{username}] Close button click failed: {e_close}")
                        
                        # 確実にホームに強制遷移する
                        logger.info(f"[{username}] Forcing navigation to /home to escape premium screen...")
                        try:
                            self.page.get("https://x.com/home")
                            sleep_random(5, 8)
                        except Exception as e_home:
                            logger.error(f"[{username}] Failed to force get home: {e_home}")
                    
                    # 3. 「やりなおす」掃除
                    self.handle_retry_button()
                    self.handle_interstitial_popups()

                    # 4. TL観覧（必須）
                    logger.info(f"[{username}] Browsing TL for a bit after setup...")
                    for _ in range(random.randint(4, 8)):
                        self.human_scroll()
                        self.handle_interstitial_popups()
                    
                    # [NEW] トレンドチラ見
                    if random.random() < 0.5:
                        trend_btn = self.page.ele("css:[data-testid='AppTabBar_Explore_Link']", timeout=3)
                        if trend_btn:
                            trend_btn.click()
                            sleep_random(4, 8)
                            self.page.scroll.down(random.randint(300, 700))
                            sleep_random(3, 5)
                            home_btn = self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=3)
                            if home_btn:
                                home_btn.click()
                                sleep_random(3, 5)

                    return True, self.get_current_cookies()

                jf_error = self.get_jf_error_message()
                if jf_error:
                    logger.warning(f"[{username}] JF form error while waiting for login: {jf_error}")
                    return self.classify_jf_error_message(jf_error)
                
                # Check for errors immediately
                if self.page.ele("text:The password you entered is incorrect", timeout=0.1) or \
                   self.page.ele("text:パスワードが正しくありません", timeout=0.1) or \
                   self.page.ele("text:Wrong password", timeout=0.1) or \
                   self.page.ele("text:wrong password", timeout=0.1) or \
                   self.page.ele("text:Incorrect password", timeout=0.1) or \
                   self.page.ele("text:incorrect password", timeout=0.1) or \
                   self.page.ele("text:パスワードが間違っています", timeout=0.1) or \
                   self.page.ele("text:間違ってい", timeout=0.1) or \
                   self.page.ele("text:正しくありません", timeout=0.1):
                    logger.error("Incorrect password detected.")
                    return "WRONG_PASSWORD"
                
                # Check for 2FA Challenge
                if not totp_done:
                    # 6-split individual boxes form
                    code_inputs = self.page.eles('css:input[id^="jf-code-input-challenge_response-"]')
                    if not code_inputs:
                        code_inputs = self.page.eles('css:input[id^="jf-code-input"]')
                    if not code_inputs:
                        code_inputs = self.page.eles('css:input[autocomplete="one-time-code"]')
                    
                    if code_inputs and len(code_inputs) == 6:
                        logger.warning("6-split 2FA Challenge Detected!")
                        if totp_secret:
                            try:
                                logger.info("Generating TOTP code...")
                                clean_secret = totp_secret.replace(" ", "")
                                totp = pyotp.TOTP(clean_secret)
                                code = totp.now()
                                
                                # [HUMANIZATION] Add random wait before code input
                                sleep_random(10, 25)
                                
                                logger.info(f"Inputting TOTP Code (split): {code}")
                                for idx, char in enumerate(code):
                                    if idx < len(code_inputs):
                                        code_inputs[idx].click()
                                        time.sleep(0.1)
                                        code_inputs[idx].clear()
                                        code_inputs[idx].input(char)
                                        time.sleep(0.1)
                                sleep_random(2, 4)
                                
                                # Click Verify/Next/続ける
                                # Click Verify/Next/続ける
                                # Support multiple tags like span, p, div, button for diverse gateways
                                next_keywords = ["Next", "次へ", "Verify", "認証", "続ける"]
                                kw_next_pred = " or ".join([f"contains(., '{kw}')" for kw in next_keywords])
                                next_btn = self.page.ele(f"xpath://span[{kw_next_pred}] | //p[{kw_next_pred}] | //div[@role='button'][{kw_next_pred}] | //button[{kw_next_pred}]", timeout=3)
                                if not next_btn:
                                    next_btn = self.page.ele("css:[data-testid='ocfEnterTextNextButton']", timeout=1) or \
                                               self.page.ele("css:div[role='button'][data-testid*='Next']", timeout=1)
                                    
                                if next_btn:
                                    next_btn.click()
                                    totp_done = True
                                    logger.info("Clicked Verify/Next for TOTP.")
                                    sleep_random(3, 5)
                                    if self.handle_jf_error_message(username, "totp submit", retry_click=lambda: next_btn.click()):
                                        return "JF_ERROR_TOTP"
                                else:
                                    self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
                                    totp_done = True
                                    sleep_random(2, 3)
                                    if self.handle_jf_error_message(username, "totp submit", retry_click=lambda: self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)):
                                        return "JF_ERROR_TOTP"
                            except Exception as e:
                                logger.error(f"Failed to generate/input split TOTP: {e}")
                        else:
                            logger.error("2FA required but no TOTP secret provided.")
                            return "2FA_REQUIRED"
                    else:
                        # Traditional single box form
                        v_input = self.page.ele("css:input[name='verification_code']", timeout=0.1) or \
                                  self.page.ele("css:[data-testid='ocfEnterTextTextInput']", timeout=0.1)
                                  
                        if v_input:
                            logger.warning("2FA Challenge Detected!")
                            if totp_secret:
                                # User Visual Aid Request: Open 2FA Tab
                                if show_2fa_tab:
                                    # In manual mode, user wants to handle it manually with the helper tab.
                                    # Disable background pyotp as requested.
                                    self.open_2fa_tab(totp_secret)
                                    totp_done = True # Prevent repeated tab opening, but don't auto-input
                                    logger.info("2FA Tab detected/opened. Waiting for manual input...")
                                    sleep_random(3, 5) # Give user time
                                    
                                else:
                                    # Automation Mode (Bulk): Use pyotp
                                    try:
                                        logger.info("Generating TOTP code...")
                                        # Remove spaces from secret just in case
                                        clean_secret = totp_secret.replace(" ", "")
                                        totp = pyotp.TOTP(clean_secret)
                                        code = totp.now()
                                        
                                        # [HUMANIZATION] Add random wait before code input
                                        sleep_random(10, 25)
                                        
                                        logger.info(f"Inputting TOTP Code: {code}")
                                        v_input.input(code)
                                        sleep_random(2, 4)
                                        
                                        # Click Next/Verify
                                        next_btn = self.page.ele("xpath://span[text()='Next'] | //span[text()='次へ'] | //span[text()='Verify'] | //span[text()='認証']", timeout=1)
                                        if not next_btn:
                                            next_btn = self.page.ele("css:[data-testid='ocfEnterTextNextButton']", timeout=1)
                                            
                                        if next_btn:
                                            next_btn.click()
                                            totp_done = True
                                            logger.info("Clicked Verify/Next for TOTP.")
                                            sleep_random(3, 5) # Wait for processing
                                            if self.handle_jf_error_message(username, "totp submit", retry_click=lambda: next_btn.click()):
                                                return "JF_ERROR_TOTP"
                                        else:
                                            self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
                                            totp_done = True
                                            sleep_random(2, 3)
                                            if self.handle_jf_error_message(username, "totp submit", retry_click=lambda: self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)):
                                                return "JF_ERROR_TOTP"
                                    except Exception as e:
                                        logger.error(f"Failed to generate/input TOTP: {e}")
                            else:
                                logger.error("2FA required but no TOTP secret provided in CSV.")
                                # Don't return False yet, maybe user inputs it manually? 
                                # But effectively automation is stuck.
                                return "2FA_REQUIRED"

                time.sleep(1)
            
            # Final check logic using check_account_status
            status, msg = self.check_account_status()
            if status == "LOCKED":
                logger.warning(f"🔒 [{username}] ログイン後のロック検知: {msg}")
                return "LOCKED", None
            if status == "SUSPENDED":
                logger.error(f"🚫 [{username}] ログイン後の凍結検知: {msg}")
                return "SUSPENDED", None
            
            if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=2):
                 return True, self.get_current_cookies()
                 
            # If we are here, probably failed or slow
            current_url = self.page.url
            logger.error(f"Password login failed (Timeout/Unknown). URL: {current_url}")
            
            if self.page.ele("text:Wrong password", timeout=0.1) or \
               self.page.ele("text:パスワードが間違っています", timeout=0.1) or \
               self.page.ele("text:wrong password", timeout=0.1) or \
               self.page.ele("text:Incorrect password", timeout=0.1) or \
               self.page.ele("text:incorrect password", timeout=0.1) or \
               self.page.ele("text:パスワードが正しくありません", timeout=0.1) or \
               self.page.ele("text:間違ってい", timeout=0.1) or \
               self.page.ele("text:正しくありません", timeout=0.1):
                 logger.error("Login failed: Wrong password.")
                 return "WRONG_PASSWORD", None

            return False, None
                
        except Exception as e:
            logger.error(f"Password login error: {e}")
            return False, None

    def get_current_cookies(self):
        """
        Returns auth_token and ct0 from current session.
        """
        try:
            # Force a small wait ensuring they are set
            sleep_random(2, 4)
            
            cookies_list = self.page.cookies()
            cookies = {c['name']: c['value'] for c in cookies_list}
            logger.info(f"debug: Found {len(cookies)} cookies. Keys: {list(cookies.keys())}")
            
            auth_token = cookies.get("auth_token")
            ct0 = cookies.get("ct0")
            
            if not auth_token:
                logger.warning("auth_token not found in cookies!")
            if not ct0:
                 logger.warning("ct0 not found in cookies!")
                 
            return {"auth_token": auth_token, "ct0": ct0}
        except Exception as e:
            logger.error(f"Failed to get cookies: {e}")
            return {}


    def navigate_to_profile(self, target_username):
        """
        Stealthily navigates to a profile using the search bar.
        Avoids direct URL jumps which are highly detectable.
        """
        from DrissionPage.common import Keys
        try:
            target_username = target_username.replace('@', '')
            logger.info(f"Stealthily navigating to @{target_username} via search...")
            
            # 1. 検索窓を探す
            search_input = self.page.ele("css:[data-testid='SearchBox_Search_Input']", timeout=5)
            if not search_input:
                # ホームに戻ってから再試行
                self.page.get("https://x.com/home")
                sleep_random(3, 5)
                search_input = self.page.ele("css:[data-testid='SearchBox_Search_Input']", timeout=5)

            if search_input:
                search_input.click()
                sleep_random(0.5, 1.0)
                # 既存のテキストがあれば消去（Ctrl+A -> Backspace）
                self.page.actions.key_down(Keys.CONTROL).type('a').key_up(Keys.CONTROL).type(Keys.BACKSPACE)
                self.human_typing(search_input, f"@{target_username}")
                sleep_random(0.5, 1.0)
                self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
                sleep_random(3, 5)

                # 「ユーザー」タブへ（確実性を高めるため）
                people_tab = self.page.ele("xpath://span[text()='ユーザー'] | //span[text()='People']", timeout=3)
                if people_tab:
                    people_tab.click()
                    sleep_random(2, 3)

                # ユーザーセルを探してクリック
                user_link = self.page.ele(f"xpath://div[@data-testid='UserCell']//span[contains(text(), '@{target_username}')]", timeout=5)
                if user_link:
                    user_link.click()
                    logger.success(f"Reached @{target_username} profile via search.")
                    return True
            
            # 検索で見つからない、あるいは窓がない場合は最終手段
            logger.warning(f"Search navigation failed for @{target_username}. Jumping via URL as last resort.")
            # [NOTE] 頻繁なURL直接ジャンプは避けるべきだが、検索不能時の救済措置として維持
            self.page.get(f"https://x.com/{target_username}")
            return True
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False

    def follow_by_username(self, target_username):
        """
        Navigates to a user's profile using Search (Human-like) and follows them.
        """
        try:
            logger.info(f"Searching for {target_username} via UI...")
            
            # 1. Look for Search Box
            search_input = self.page.ele("css:[data-testid='SearchBox_Search_Input']", timeout=5)
            
            if search_input:
                # Human-like interaction: Click, type, enter
                search_input.click()
                sleep_random(0.5, 1.2)
                self.human_typing(search_input, target_username)
                sleep_random(0.3, 0.8)
                self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
                sleep_random(4, 6)
                
                # Click the "People" (ユーザー) tab to be sure
                people_tab = self.page.ele("xpath://span[text()='ユーザー'] | //span[text()='People']", timeout=3)
                if people_tab:
                    people_tab.click()
                    sleep_random(2, 4)
                
                # Find the user in the list and click
                # Match by @handle in the text
                user_cell = self.page.ele(f"xpath://div[@data-testid='UserCell']//span[contains(text(), '@{target_username}')]", timeout=5)
                if user_cell:
                    logger.info(f"Found {target_username} in search results. Clicking...")
                    user_cell.click()
                    sleep_random(3, 5)
            
            # 2. Fallback: If not reached profile, use direct GET (last resort)
            if target_username.lower() not in self.page.url.lower():
                url = f"https://x.com/{target_username}"
                logger.warning(f"Search navigation failed or skipped. Using direct GET as fallback: {url}")
                self.page.get(url)
                sleep_random(4, 6)
            
            # Check if valid profile
            if "Example Domain" in self.page.title or "Account suspended" in self.page.html:
                 logger.warning(f"Profile {target_username} not accessible.")
                 return False

            # Check Follow Status
            # "Following" button usually has testid="userActions-unfollow" or similar status
            # Or text "Following" / "フォロー中"
            # Follow button: testid="placementTracking" -> span text "Follow"
            
            # Use strict layout check
            # Follow Button: [data-testid*="-follow"] (careful with unfollow)
            # data-testid="placementTracking" often contains the button
            
            follow_btn = self.page.ele("css:[data-testid$='-follow']", timeout=3)
            if not follow_btn:
                # If no follow button, check if "unfollow" button exists (Already following)
                if self.page.ele("css:[data-testid$='-unfollow']"):
                    logger.info(f"Already following {target_username}.")
                    return True
                logger.warning("Follow button not found (and not following).")
                return False
            
            # Check text to be sure it's not pending or unblock etc
            btn_text = follow_btn.text.lower()
            if "follow" in btn_text or "フォロー" in btn_text:
                logger.info(f"Clicking Follow button for {target_username}...")
                follow_btn.click()
                sleep_random(2, 4)
                
                # Check for success (button should change to unfollow or 'following')
                if self.page.ele("css:[data-testid$='-unfollow']", timeout=3):
                    logger.success(f"Successfully followed {target_username}.")
                    return True
                else:
                    logger.warning("Follow click performed but status change not confirmed.")
                    return True # Assume success if no error
            else:
                 logger.info(f"Button text '{btn_text}' implies already following or restricted.")
                 return False

        except Exception as e:
            logger.error(f"Error following {target_username}: {e}")
            return False

    def search_and_follow_users(self, keyword, count=5):
        """
        Searches for a keyword, goes to People tab, and follows 'count' users.
        Japanese Keywords ONLY ideally.
        """
        try:
            import urllib.parse
            encoded_kw = urllib.parse.quote(keyword)
            # f=user filters for People
            url = f"https://x.com/search?q={encoded_kw}&src=typed_query&f=user"
            logger.info(f"Searching users with keyword: {keyword}...")
            self.page.get(url)
            sleep_random(4, 6)
            
            followed_count = 0
            attempts = 0
            max_attempts = count * 3 # Prevent infinite loops
            
            while followed_count < count and attempts < max_attempts:
                # Get all follow buttons visible
                # data-testid$="-follow" (ends with -follow) matches "12345-follow"
                # Exclude "-unfollow"
                
                # Get user cells to ensure we are targeting valid users
                user_cells = self.page.eles("css:[data-testid='UserCell']")
                
                if not user_cells:
                    logger.warning("No user cells found in search results.")
                    break
                
                # Randomize order to be "human-like" and diverse
                random.shuffle(user_cells)
                
                for cell in user_cells:
                    if followed_count >= count:
                        break
                        
                    try:
                        # Find follow button within cell
                        btn = cell.ele("css:[data-testid$='-follow']", timeout=0.1)
                        if btn:
                            # Verify it is NOT unfollow (double check selector logic)
                            # The query [data-testid$='-follow'] MIGHT match '123-unfollow' depending on regex engine? 
                            # CSS selector: [attr$=val] ends with. 'unfollow' ends with 'follow' YES.
                            # So we must explicitly exclude or check attribute.
                            
                            testid = btn.attr("data-testid")
                            if "unfollow" in testid:
                                continue # Already following
                                
                            # Safe to click
                            user_name_ele = cell.ele("css:div[dir='ltr'] > span", timeout=0.1)
                            user_name = user_name_ele.text if user_name_ele else "Unknown"
                            
                            logger.info(f"Following found user: {user_name}")
                            btn.click()
                            followed_count += 1
                            sleep_random(4, 8) # Good delay between follows
                            
                            if followed_count >= count:
                                break
                    except Exception as e:
                        logger.debug(f"Error processing user cell: {e}")
                        continue
                        
                attempts += 1
                
                # Scroll down to load more if needed
                if followed_count < count:
                    logger.info("Scrolling for more users...")
                    self.page.scroll.down(500)
                    sleep_random(2, 4)
            
            logger.success(f"Search follow complete. Followed: {followed_count}/{count} users.")
            return followed_count

        except Exception as e:
            logger.error(f"Search and follow error: {e}")
            return 0

    def engage_timeline_random(self, count=5, like_rate=50, rt_rate=20):
        """
        Scrolls timeline and interacts ONLY with Japanese tweets.
        Fallback to @McDonaldsJapan if no Japanese tweets found.
        [UPDATED] Opens tweet details before Liking/RTing as requested.
        """
        try:
            logger.info(f"Starting Timeline Engagement (Target: {count}, Japanese Only)...")
            
            if "home" not in self.page.url:
                self.page.get("https://x.com/home")
                sleep_random(3, 5)
            
            actions_done = 0
            scroll_attempts = 0
            max_scrolls = 20 # Increased due to navigation overhead
            processed_urls = set()
            
            while actions_done < count and scroll_attempts < max_scrolls:
                tweets = self.page.eles("css:article[data-testid='tweet']")
                
                if not tweets:
                    logger.warning(f"No tweets found (Attempt {scroll_attempts+1}/{max_scrolls}). Scrolling...")
                    self.page.scroll.down(600)
                    sleep_random(2, 3)
                    scroll_attempts += 1
                    continue
                
                # Find a valid candidate that hasn't been processed
                target_tweet = None
                target_url = None
                
                for tweet in tweets:
                    # Get URL to track uniqueness
                    try:
                        # Time element usually has the permalink
                        time_ele = tweet.ele("css:time", timeout=0.1)
                        if time_ele:
                            parent = time_ele.parent()
                            if parent and parent.tag == 'a':
                                url = parent.attr("href")
                                if url in processed_urls:
                                    continue
                                
                                txt = tweet.text
                                if self._is_valid_content(txt):
                                    target_tweet = tweet
                                    target_url = url
                                    processed_urls.add(url)
                                    break # Handle one at a time due to navigation
                    except:
                        continue
                
                if not target_tweet:
                    # No valid new tweets in current view, scroll
                    self.human_scroll()
                    scroll_attempts += 1
                    sleep_random(2, 4)
                    continue
                
                # PROCESS TARGET
                try:
                    txt = target_tweet.text
                    logger.info(f"Targeting tweet for DETAILED interaction: {txt[:20]}...")
                    
                    # 1. Click to Open (Simulate reading in detail)
                    # Click the text or background, avoid links/hashtags if possible, but tweet body is safe-ish
                    # Safe bet: click the <time> element or the text body container
                    target_tweet.click()
                    
                    # 2. Wait for Details Page
                    sleep_random(3, 5)
                    if "status" in self.page.url:
                        logger.info("Opened Tweet Details. Simulating reading...")
                        sleep_random(2, 5) # Read content
                        
                        performed_action = False
                        
                        # LIKE
                        roll = random.randint(1, 100)
                        if roll <= like_rate:
                            # In detail view, selectors might differ slightly but usually data-testid='like' is same
                            # Scoping to page is fine now
                            like_btn = self.page.ele("css:article[data-testid='tweet'] [data-testid='like']", timeout=2)
                            if like_btn:
                                if self.stealth_click(like_btn):
                                    logger.info(f"❤️ Like (Detail View): {txt[:15]}...")
                                    actions_done += 1
                                    performed_action = True
                        
                        sleep_random(1, 3)
                        
                        # RT
                        # logic similar...
                        if actions_done < count:
                            roll_rt = random.randint(1, 100)
                            if roll_rt <= rt_rate:
                                rt_btn = self.page.ele("css:article[data-testid='tweet'] [data-testid='retweet']", timeout=2)
                                if rt_btn:
                                    if self.stealth_click(rt_btn, wait_after=False):
                                        sleep_random(1, 2)
                                        confirm_rt = self.page.ele("css:[data-testid='retweetConfirm']", timeout=3)
                                        if confirm_rt:
                                            self.stealth_click(confirm_rt)
                                            logger.info(f"🔄 RT (Detail View): {txt[:15]}...")
                                            actions_done += 1
                                            performed_action = True
                        
                        # Return to Timeline
                        logger.info("Returning to Timeline...")
                        self.page.back()
                        sleep_random(3, 5) # Wait for list reload
                        
                    else:
                        logger.warning("Failed to open tweet details. Skipping.")
                        self.page.back() # Just in case
                        sleep_random(2, 3)

                except Exception as e:
                    logger.debug(f"Interaction error: {e}")
                    self.page.back() # Safety return
                    sleep_random(2, 3)
                    continue

            # FALLBACK CHECK
            if actions_done == 0:
                logger.warning("⚠️ No Japanese tweets engaged in timeline. Triggering Fallback: McDonaldsJapan")
                remaining = count - actions_done
                self.engage_specific_user("McDonaldsJapan", count=remaining, like_rate=like_rate, rt_rate=rt_rate)
                return max(1, count)

            logger.success(f"Engagement complete. Total actions: {actions_done}")
            return actions_done
        except Exception as e:
            logger.error(f"Timeline engagement error: {e}")
            return 0

    def engage_from_trends(self, count=3, like_rate=60, rt_rate=30, follow_rate=20):
        """
        Clicks a topic from the Right Sidebar ("What's Happening" / Trends)
        and engages with 2-3 tweets from the search results.
        Also attempts to FOLLOW users via Hover Card.
        """
        try:
            logger.info("Starting Trend-based Engagement (with Follows)...")
            
            # 1. Ensure Home to see sidebar
            if "home" not in self.page.url:
                self.page.get("https://x.com/home")
                sleep_random(4, 6)
            
            # 2. Find Trend Items (Right Sidebar)
            # data-testid="trend" is the standard container for each item in the "What's happening" box
            trend_items = self.page.eles("css:[data-testid='trend']")
            
            if not trend_items:
                logger.warning("No trend items found in sidebar. Fallback to Timeline.")
                return self.engage_timeline_random(count, like_rate, rt_rate)
            
            # Filter out potentially harmful/boring trends if needed? 
            # For now just pick random.
            # Avoid topmost if it's "Live" or "Promoted"? 
            # Usually promoted trends are at the top or distinct.
            # [MODIFIED] Pick from top 15 to diversify (was 5)
            candidates = trend_items[:15] 
            target_trend = random.choice(candidates)
            
            try:
                trend_text = target_trend.text.split('\n')[0]
                logger.info(f"Clicked Trend: {trend_text}")
                # Stealth click Trend
                target_trend.hover()
                sleep_random(1, 2)
                target_trend.click()
            except:
                logger.warning("Failed to click trend. Trying fallback index 0.")
                trend_items[0].click()
            
            sleep_random(5, 8)
            
            # 3. Engage with Search Results (Reuse logic?)
            # We are now on a search page.
            # We can reuse the loop logic or specific logic.
            # Let's implement a mini-loop here reusing the strict filtering.
            
            actions_done = 0
            scroll_attempts = 0
            max_scrolls = 10
            processed_urls = set() # Initialize processed_urls for this method
            
            logger.info(f"Engaging with Trend Search Results (Target: {count})...")
            
            # [MODIFIED] Initial Random Scroll to avoid always hitting top tweets
            initial_scroll_count = random.randint(0, 2)
            if initial_scroll_count > 0:
                 logger.info(f"Scrolling down {initial_scroll_count} times to find diverse tweets...")
                 for _ in range(initial_scroll_count):
                     self.human_scroll()
                     sleep_random(2, 4)

            while actions_done < count and scroll_attempts < max_scrolls:
                tweets = self.page.eles("css:article[data-testid='tweet']")
                
                if not tweets:
                    self.page.scroll.down(600)
                    sleep_random(2, 3)
                    scroll_attempts += 1
                    continue
                
                # [MODIFIED] Randomize processing order of visible tweets
                # Instead of iterating sequentially, shuffle the list or pick random
                # We need to filter processed ones still, but order matters for variety
                random.shuffle(tweets)
                
                # Limit checking to a subset to avoid stalling if many tweets are loaded
                check_subset = tweets[:8] 

                for tweet in check_subset:
                    if actions_done >= count: break
                    
                    try:
                        # Re-verify existence (stale element check)
                        # DrissionPage elements might go stale if DOM changed heavily
                        # But usually 'tweet' object holds ref. 
                        pass 
                    except:
                        continue
                        
                    url = self._get_tweet_url(tweet)
                    if not url: 
                        continue
                    
                    if url in processed_urls:
                        continue
                    
                    try:
                        txt = tweet.text
                        
                        # Strict Checker
                        if not self._is_valid_content(txt):
                            processed_urls.add(url) # Mark as processed to avoid re-checking
                            continue
                            
                        # Name Checker
                        try:
                            user_name_ele = tweet.ele("css:[data-testid='User-Name']", timeout=0.01)
                            if user_name_ele:
                                user_txt = user_name_ele.text
                                if any(x in user_txt for x in ["Bot", "bot", "Info", "News", "公式", "案内", "運営"]):
                                    processed_urls.add(url) # Mark as processed to avoid re-checking
                                    continue
                        except:
                            pass
                        
                        logger.info(f"Targeting Trend Tweet: {txt[:20]}...")
                        
                        # 1. Click to Open (Simulate reading in detail)
                        # 1. Click to Open (Robust Logic)
                        navigated = False
                        try:
                            # Attempt 1: Click Tweet Text (Most neutral area)
                            text_ele = tweet.ele("css:[data-testid='tweetText']", timeout=1)
                            if text_ele:
                                logger.info("Attempting to open via Tweet Text...")
                                text_ele.click()
                                sleep_random(3, 5)
                            
                            if "status" in self.page.url:
                                navigated = True
                            
                            # Attempt 2: Click Timestamp (Permalink) if not yet navigated
                            if not navigated:
                                logger.info("Tweet Text click failed to navigate. Retrying via Timestamp...")
                                time_ele = tweet.ele("css:time", timeout=1)
                                if time_ele:
                                    # Click the parent <a> tag of the time element
                                    # DrissionPage usually clicks the center of the element, so <time> itself might not be the link anchor, 
                                    # but almost always is wrapped in one. Clicking <time> propagates.
                                    time_ele.click()
                                    sleep_random(3, 5)
                            
                            if "status" in self.page.url:
                                navigated = True

                            # Verification
                            if navigated:
                                logger.info("Verified: Opened Tweet Details successfully.")
                                sleep_random(2, 4)
                                
                                # 2. Action: Like
                                roll = random.randint(1, 100)
                                if roll <= like_rate:
                                    # Ensure we find the like button in the current view (detail page)
                                    like_btn = self.page.ele("css:article[data-testid='tweet'] [data-testid='like']", timeout=2)
                                    if like_btn:
                                        if self.stealth_click(like_btn):
                                            logger.info(f"❤️ Like (Detail View - Trend): {txt[:15]}...")
                                            actions_done += 1
                                
                                sleep_random(1, 3)
                                
                                # 3. Action: RT
                                if actions_done < count:
                                    roll_rt = random.randint(1, 100)
                                    if roll_rt <= rt_rate:
                                        rt_btn = self.page.ele("css:article[data-testid='tweet'] [data-testid='retweet']", timeout=2)
                                        if rt_btn:
                                            if self.stealth_click(rt_btn, wait_after=False):
                                                sleep_random(1.2, 2.8)
                                                confirm_rt = self.page.ele("css:[data-testid='retweetConfirm']", timeout=5)
                                                if confirm_rt:
                                                    self.stealth_click(confirm_rt)
                                                    logger.info(f"🔄 RT (Detail View - Trend): {txt[:15]}...")
                                                    actions_done += 1
                                
                                # 4. Return to Search Results
                                logger.info("Returning to Search Results...")
                                self.page.back()
                                sleep_random(3, 5)
                            else:
                                logger.warning("Failed to navigate to tweet status page. FALLBACK: Liking from List View.")
                                # Fallback: Logic for List View (using `tweet` element scope)
                                
                                # Like
                                roll = random.randint(1, 100)
                                if roll <= like_rate:
                                    try:
                                        like_btn = tweet.ele("css:[data-testid='like']", timeout=2)
                                        if like_btn:
                                            if self.stealth_click(like_btn):
                                                logger.info(f"❤️ Like (List View - Fallback): {txt[:15]}...")
                                                actions_done += 1
                                    except Exception as e_like:
                                        logger.debug(f"List View Like failed: {e_like}")
                                
                                sleep_random(1, 2)
                                
                                # RT
                                if actions_done < count:
                                    roll_rt = random.randint(1, 100)
                                    if roll_rt <= rt_rate:
                                        try:
                                            rt_btn = tweet.ele("css:[data-testid='retweet']", timeout=2)
                                            if rt_btn:
                                                if self.stealth_click(rt_btn, wait_after=True):
                                                    confirm_rt = self.page.ele("css:[data-testid='retweetConfirm']", timeout=3)
                                                    if confirm_rt:
                                                        self.stealth_click(confirm_rt)
                                                        logger.info(f"🔄 RT (List View - Fallback): {txt[:15]}...")
                                                        actions_done += 1
                                        except Exception as e_rt:
                                            logger.debug(f"List View RT failed: {e_rt}")

                        except Exception as inner_e:
                            logger.error(f"Error interacting with tweet/detail view: {inner_e}")
                            # If we ARE in a status page, try to get back
                            if "status" in self.page.url:
                                try:
                                    self.page.back()
                                    sleep_random(2, 3)
                                except:
                                    pass

                        # FOLLOW (Via Hover Card to avoid navigation)
                        roll_follow = random.randint(1, 100)
                        if roll_follow <= follow_rate:
                             try:
                                 # 1. Hover over User Name to trigger card
                                 user_name_ele = tweet.ele("css:[data-testid='User-Name']", timeout=0.5)
                                 if user_name_ele:
                                     user_name_ele.hover()
                                     sleep_random(1.5, 3) # Wait for animation
                                     
                                     # 2. Find Hover Card
                                     # It is usually a direct child of layers or body, context might be page
                                     hover_card = self.page.ele("css:[data-testid='hoverCard']", timeout=2)
                                     
                                     if hover_card:
                                         # 3. Find Follow Button in Card
                                         # Ensure we don't click "Unfollow"
                                         fbtn = hover_card.ele("css:[data-testid$='-follow']", timeout=1)
                                         if fbtn:
                                             # Double check it's not unfollow
                                             if "unfollow" not in fbtn.attr("data-testid"):
                                                 fbtn.click()
                                                 logger.success(f"➕ Followed User (via Hover): {txt[:10]}...")
                                                 sleep_random(2, 3)
                                                 # Move mouse away to close card?
                                                 self.page.scroll.down(10) 
                                             else:
                                                 logger.debug("Already following (Hover).")
                                     else:
                                         logger.debug("Hover card did not appear.")
                             except Exception as e:
                                 logger.debug(f"Hover follow failed: {e}")

                    except Exception:
                        continue
                
                self.human_scroll()
                scroll_attempts += 1
                sleep_random(2, 4)
            
            return actions_done

        except Exception as e:
            logger.error(f"Trend engagement failed: {e}")
            return 0

    def update_profile(self, name=None, bio=None, location=None, icon_path=None, header_path=None):
        """
        Updates profile information using UI elements.
        Verified selectors based on Subagent Trace.
        """
        try:
            logger.info("Navigating to Profile...")
            # Try specific profile URL if known, else Navigate via UI
            # self.page.get(f"https://x.com/{self.screen_name}") # Ideal if screen_name available
            
            profile_link = self.page.ele("css:[data-testid='AppTabBar_Profile_Link']")
            if profile_link:
                profile_link.click()
                sleep_random(5, 7)
            
            # Direct Navigation to Edit Profile (Bypassing "Set up profile" Wizard)
            # The "Set up profile" button often triggers a multi-step wizard (i/flow/setup_profile)
            # which blocks the standard edit modal. Direct URL forces the standard modal.
            logger.info("Navigating directly to Edit Profile settings (Bypassing Wizards)...")
            self.page.get("https://x.com/settings/profile")
            sleep_random(4, 6)
            
            # Verify we are in the modal (Edit Profile)
            # Check for name field or save button
            if not self.page.ele("css:input[name='displayName']") and not self.page.ele("css:[data-testid='Profile_Save_Button']"):
                logger.warning("Standard Edit Modal not detected. Attempting legacy button click...")
                # Fallback: Click button if direct URL failed (unlikely but safe)
                edit_btn = self.page.ele("css:[data-testid='editProfileButton']")
                if edit_btn: edit_btn.click()
                sleep_random(3, 5)

            # Update Name
            if name:
                logger.info(f"Updating Name: {name}")
                name_field = self.page.ele("css:input[name='displayName']")
                if name_field:
                    name_field.click()
                    sleep_random(0.5, 1)
                    # Robust clear using standard method
                    name_field.clear()
                    time.sleep(0.5)
                    # Input new text
                    name_field.input(name)
                    sleep_random(1, 2)
                else:
                    logger.warning("Name field not found!")

            # Update Bio
            if bio:
                logger.info(f"Updating Bio: {bio}")
                bio_field = self.page.ele("css:textarea[name='description']")
                if bio_field:
                    bio_field.click()
                    sleep_random(0.5, 1)
                    # Robust clear using standard method
                    bio_field.clear()
                    time.sleep(0.5)
                    # Input new text
                    bio_field.input(bio)
                    sleep_random(1, 2)
                else:
                     logger.warning("Bio field not found!")

            # Update Icon/Header
            if icon_path and os.path.exists(icon_path):
                logger.info(f"Uploading Icon: {icon_path}")
                try:
                    # User's "Ironclad Code" Logic: Target DIV with broad keywords
                    # "プロフィール画像" or "profile photo"
                    icon_input = self.page.ele('xpath://div[contains(@aria-label, "プロフィール画像") or contains(@aria-label, "profile photo")]//input[@type="file"]')
                    
                    # Fallback: Button (sometimes it is a button)
                    if not icon_input:
                         icon_input = self.page.ele('xpath://button[contains(@aria-label, "プロフィール画像") or contains(@aria-label, "profile photo")]//input[@type="file"]')

                    # Fallback: Index 1 (Standard Layout)
                    if not icon_input:
                         all_inputs = self.page.eles("xpath://input[@type='file']")
                         if len(all_inputs) >= 2:
                             logger.warning("Icon Selector failed. Using Fallback: Index 1")
                             icon_input = all_inputs[1]

                    if icon_input:
                        icon_input.input(os.path.abspath(icon_path))
                        sleep_random(3, 5)

                        # Click Apply ("適用" / "Apply")
                        # Selector: [data-testid="applyButton"]
                        apply_btn = self.page.ele("css:[data-testid='applyButton']")
                        if not apply_btn:
                             apply_btn = self.page.ele("xpath://span[text()='Apply'] | //span[text()='適用']") 
                        
                        if apply_btn:
                            logger.info("Clicking Apply for Icon...")
                            apply_btn.click()
                            sleep_random(2, 3)
                        else:
                            logger.info("Apply button not found.")
                    else:
                        logger.warning("Icon input element not found.")
                except Exception as e:
                    logger.error(f"Icon upload failed: {e}")

            if header_path and os.path.exists(header_path):
                logger.info(f"Uploading Header: {header_path}")
                try:
                    # User's "Ironclad Code" Logic: Target DIV with broad keywords
                    # "ヘッダー" or "header"
                    header_input = self.page.ele('xpath://div[contains(@aria-label, "ヘッダー") or contains(@aria-label, "header")]//input[@type="file"]')
                    
                    if not header_input:
                         header_input = self.page.ele('xpath://button[contains(@aria-label, "ヘッダー") or contains(@aria-label, "header")]//input[@type="file"]')

                    # Fallback: Index 0 (Standard Layout)
                    if not header_input:
                         all_inputs = self.page.eles("xpath://input[@type='file']")
                         if len(all_inputs) >= 1:
                             logger.warning("Header Selector failed. Using Fallback: Index 0")
                             header_input = all_inputs[0]

                    if header_input:
                        header_input.input(os.path.abspath(header_path))
                        sleep_random(3, 5)

                        # Click Apply ("適用")
                        apply_btn = self.page.ele("css:[data-testid='applyButton']")
                        if not apply_btn:
                             apply_btn = self.page.ele("xpath://span[text()='Apply'] | //span[text()='適用']")

                        if apply_btn:
                            logger.info("Clicking Apply for Header...")
                            apply_btn.click()
                            sleep_random(2, 3)
                    else:
                        logger.warning("Header input element not found.")
                except Exception as e:
                    logger.error(f"Header upload failed: {e}")

            # Save (Enhanced)
            logger.info("Saving changes (Enhanced Logic)...")
            
            # 1. Try Standard ID
            save_btn = self.page.ele("css:[data-testid='Profile_Save_Button']")
            
            # 2. Try Text (JP/EN)
            if not save_btn:
                 save_btn = self.page.ele("xpath://span[text()='Save'] | //span[text()='保存']")
            
            # 3. Universal/Scoped Search (Same logic as Force Language)
            if not save_btn:
                logger.info("Standard save button not found. Searching in Scoped area...")
                # Usually profile edit is a modal
                dialog = self.page.ele("css:[role='dialog']")
                base = dialog if dialog else self.page
                
                # Search for buttons with White Text (Primary)
                buttons = base.eles("css:[role='button']")
                for btn in buttons:
                     if not btn.states.is_displayed: continue
                     if btn.ele("xpath:.//*[contains(@style, 'color: rgb(255, 255, 255)')]", timeout=0.1):
                          save_btn = btn
                          logger.info("Found Save button by Style (White Text)")
                          break
            
            if save_btn:
                save_btn.click()
                logger.info("Save button clicked.")
                sleep_random(5, 7)
                logger.success("Profile updated successfully via UI.")
                return True
            else:
                logger.warning("Save button not found!")
                return False

        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            return False

    def browse_timeline(self, scrolls=3):
        """
        Passive browsing: scrolls the timeline and occasionally clicks a tweet to view details (then goes back).
        NO Likes, NO RTs, NO follows.
        """
        try:
            logger.info(f"Starting passive browsing (Scrolls: {scrolls})...")
            if "home" not in self.page.url:
                self.page.get("https://x.com/home")
                sleep_random(3, 5)

            for i in range(scrolls):
                logger.info(f"Browsing Scroll {i+1}/{scrolls}...")
                self.human_scroll()
                sleep_random(2, 4)
                
                # 30% chance to click a random tweet to "view" it
                if random.random() < 0.3:
                    tweets = self.page.eles("css:article[data-testid='tweet']")
                    if tweets:
                        target = random.choice(tweets[:min(5, len(tweets))]) # Pick from top current view
                        logger.info("Human Action: Clicking tweet to view details...")
                        self.stealth_click(target, wait_after=True)
                        sleep_random(3, 6) # Look at the tweet
                        
                        # Go back to home
                        if random.random() < 0.5:
                            logger.info("Going back via Home link...")
                            home_link = self.page.ele("css:[data-testid='AppTabBar_Home_Link']")
                            if home_link: home_link.click()
                        else:
                            logger.info("Going back via Browser Back...")
                            self.page.back()
                        
                        sleep_random(3, 5)

            return True
        except Exception as e:
            logger.error(f"Passive browsing failed: {e}")
            return False

    def browse_trends_passive(self, trend_count=1):
        """
        Actively checks trends and Japanese account information (Passive).
        Clicks a trend, reads results, and visits 1-2 Japanese profiles.
        """
        try:
            logger.info("Starting Passive Trend Browsing...")
            if "home" not in self.page.url:
                self.page.get("https://x.com/home")
                sleep_random(3, 5)
            
            # 1. Find Trends
            # Broad search for trend items (various possible selectors)
            trend_items = self.page.eles("css:[data-testid='trend']") or \
                          self.page.eles("css:section[aria-labelledby*='accessible-list'] div[data-testid='cellInnerDiv'] a") or \
                          self.page.eles("css:[aria-label='Trends'] [role='link']")
            
            if not trend_items:
                logger.warning("No trends found in sidebar. Checking for Explore link...")
                explore_link = self.page.ele("css:[data-testid='AppTabBar_Explore_Link']")
                if explore_link:
                    explore_link.click()
                    sleep_random(4, 6)
                    trend_items = self.page.eles("css:[data-testid='trend']")
            
            if not trend_items:
                logger.warning("Still no trends found. Skipping trend browsing.")
                return False
            
            # 2. Pick a random trend (avoiding first if possible)
            target = random.choice(trend_items[:min(5, len(trend_items))])
            logger.info(f"Human Action: Clicking Trend -> {target.text[:20].strip()}...")
            self.stealth_click(target)
            sleep_random(4, 7)
            
            # 3. Browse search results
            for _ in range(random.randint(2, 4)):
                self.human_scroll()
                sleep_random(2, 5)
                
                # Check for Japanese accounts to visit
                tweets = self.page.eles("css:article[data-testid='tweet']")
                if tweets:
                    for tweet in random.sample(tweets, min(len(tweets), 3)):
                        txt = tweet.text
                        if self._is_valid_content(txt):
                            # Found a Japanese tweet, visit their profile
                            user_ele = tweet.ele("css:[data-testid='User-Name']", timeout=0.1)
                            if user_ele:
                                logger.info("Human Action: Interested in this Japanese account. Visiting profile...")
                                self.stealth_click(user_ele)
                                sleep_random(4, 8) # "Read" the profile
                                
                                # Scroll profile a bit
                                if random.random() < 0.5:
                                    self.human_scroll()
                                    sleep_random(2, 4)
                                
                                self.page.back()
                                sleep_random(3, 5)
                                break # Move to next scroll/batch
            
            return True
        except Exception as e:
            logger.error(f"Passive trend browsing failed: {e}")
            return False

    def perform_initial_follows(self):
        """
        Subagent Verified Flow:
        1. Go to https://x.com/i/connect_people (Connect Page)
        2. Find [data-testid="UserCell"]
        3. Click -> Profile -> Scroll -> Follow -> Back
        4. Repeat 3 times
        """
        try:
            logger.info("Starting Initial Recommended Follow sequence...")
            
            # Loop 3 times
            for i in range(3):
                logger.info(f"--- Follow Sequence {i+1}/3 ---")
                
                # 1. Ensure we are on Connect Page (Robustness Fix)
                if "connect_people" not in self.page.url:
                     logger.info("Navigating to Connect Page to refresh list...")
                     self.page.get("https://x.com/i/connect_people")
                     sleep_random(4, 6)
                
                # 2. Get User Cells
                # Re-fetch every loop to ensure freshness
                user_cells = self.page.eles("css:[data-testid='UserCell']")
                if not user_cells:
                    logger.warning("No recommended users found. Retrying page load...")
                    self.page.get("https://x.com/i/connect_people")
                    sleep_random(5, 7)
                    user_cells = self.page.eles("css:[data-testid='UserCell']")
                    if not user_cells:
                        logger.error("Still no users found. Aborting sequence.")
                        break
                
                # Random choice
                target_cell = random.choice(user_cells)
                
                # Try to extract name for logging (optional)
                try:
                    user_text = target_cell.text.split('\n')[0]
                    logger.info(f"Selected user: {user_text}")
                except:
                    logger.info("Selected a user (name unknown)")

                # 3. Click to Profile
                target_cell.click()
                sleep_random(3, 5) # Wait for profile load
                
                # 4. Simulate Timeline Reading (Scroll)
                logger.info("Browsing timeline...")
                # Scroll down a bit
                self.page.scroll.down(random.randint(300, 700))
                sleep_random(1, 3)
                self.page.scroll.down(random.randint(300, 700))
                sleep_random(2, 4)
                # Scroll up a bit
                self.page.scroll.up(random.randint(100, 300))
                sleep_random(1, 2)
                
                # 5. Follow
                # Selector: button[data-testid$="-follow"] or [aria-label*="フォロー"]
                logger.info("Attempting to follow...")
                # Ensure we scroll up to the top area where profile buttons usually are
                self.page.scroll.to_top()
                sleep_random(1, 2)
                
                follow_btn = self.page.ele("css:button[data-testid$='-follow']", timeout=2)
                
                if follow_btn:
                    try:
                        # Ensure button is in view
                        follow_btn.scroll.to_see()
                        sleep_random(0.5, 1.5)
                        follow_btn.click()
                        logger.success("Followed user.")
                        sleep_random(2, 3)
                    except Exception as e:
                        logger.warning(f"Standard click failed, trying JS click: {e}")
                        self.page.run_js("arguments[0].click();", follow_btn)
                        sleep_random(2, 3)
                else:
                    logger.info("Follow button not found (Already followed or Restricted).")
                
                # 6. Return to List
                # Explicitly re-visit the Connect page in the next loop iteration (handled by top of loop)
                # But here we can just wait or do a simple back for speed if it works, 
                # but relying on the "Top of loop navigation" is safer.
                logger.info("Preparing for next user...")
                sleep_random(2, 4)
                
            return True
                
        except Exception as e:
            logger.error(f"Initial follow sequence failed: {e}")
            return False

    def human_typing(self, element, text, speed_min=0.12, speed_max=0.35):
        """
        Simulates highly realistic human typing, optimized to reduce CDP bottlenecks
        on high-latency file systems while preserving natural speed illusions.
        If CDP lag is detected, falls back to fast batch entry.
        """
        import random
        import time
        try:
            element.click()
            sleep_random(0.2, 0.4)
        except Exception as e:
            # 要素の有効性をチェック
            is_alive = getattr(getattr(element, 'states', None), 'is_alive', True)
            if not is_alive:
                raise e

        # [1文字ずつ入力] 1文字単位でCDPを呼び出し、より人間らしいタイピングを実現
        try:
            for char in text:
                t0 = time.time()
                try:
                    element.input(char)
                except Exception as e:
                    logger.warning(f"Error inputting char '{char}': {e}")
                    # エラーメッセージに「失效」が含まれるか、states.is_aliveがFalseの場合は即座に中断
                    err_msg = str(e)
                    is_alive = getattr(getattr(element, 'states', None), 'is_alive', True)
                    if "失效" in err_msg or "stale" in err_msg.lower() or not is_alive:
                        logger.error("Element has become stale/invalid during typing! Aborting character loop.")
                        raise e
                
                # 1文字入力にかかった時間が1秒を超えた場合、CDPの深刻な遅延とみなしてフォールバック
                input_duration = time.time() - t0
                if input_duration > 1.0:
                    logger.warning(f"CDP connection lag detected ({input_duration:.2f}s per char). Switching to batch typing fallback to prevent freezing.")
                    raise RuntimeError("CDP connection lag detected")

                # Human-like delay per character
                delay = random.uniform(speed_min, speed_max)
                
                # Natural punctuation pause
                if char in "。、,.!?！？\n\r ":
                    delay += random.uniform(0.1, 0.2)
                
                # Thinking pause (1% chance)
                if random.random() < 0.01:
                    delay += random.uniform(0.15, 0.3)
                
                time.sleep(delay)
        except Exception as e:
            logger.warning(f"Typing simulation failed, using batch fallback: {e}")
            try:
                element.clear()
                element.input(text)
            except Exception as fallback_err:
                logger.error(f"Batch typing fallback also failed: {fallback_err}")
                raise fallback_err

    def mouse_wiggle(self, element=None):
        """Simulates human-like mouse movement before interaction."""
        try:
            if element:
                element.scroll.to_see()
            
            # 2-3 small random moves
            for _ in range(random.randint(2, 3)):
                x_offset = random.randint(-15, 15)
                y_offset = random.randint(-15, 15)
                self.page.actions.move(x_offset, y_offset)
                time.sleep(random.uniform(0.1, 0.2))
        except:
            pass

    def stealth_click(self, element, wait_after=True):
        """Hover, wiggle, and click with physical coordinate actions & JS fallback."""
        try:
            # 1. Scroll to view
            element.scroll.to_see()
            sleep_random(0.5, 1.0)
            
            # 2. Hover & Wiggle
            element.hover()
            self.mouse_wiggle()
            sleep_random(0.2, 0.5)
            
            # 3. Physical Click (Coordinate-based via Actions)
            # This is more reliable for complex nested divs/svgs
            try:
                self.page.actions.move_to(element).click()
                logger.debug("Performed physical action click.")
            except Exception as e:
                logger.warning(f"Physical click failed, trying standard: {e}")
                element.click(timeout=5)
            
            # 4. JS Fallback (If the click didn't trigger what we expect - basic check)
            # We don't always know if it worked, but JS click is a good safety net
            # However, JS click is less 'stealthy', so we use it only as a last resort or supplement
            
            if wait_after:
                sleep_random(1.5, 3.5)
            return True
        except Exception as e:
            logger.error(f"Stealth click completely failed: {e}")
            # Final desperate attempt: JS Click
            try:
                self.page.run_js("arguments[0].click();", element)
                return True
            except:
                return False

    def human_scroll(self, min_dist=100, max_dist=3000):
        """
        [AGGRESSIVE RANDOM] Simulates human scrolling with extreme variability.
        Prevents stopping at predictable offsets.
        """
        import random
        # 1. 距離を大きくバラけさせる
        # 70%は普通〜大きめ、20%は超特大、10%は微小
        r = random.random()
        if r < 0.7:
            dist = random.randint(400, 1500)
        elif r < 0.9:
            dist = random.randint(1500, 4000)
        else:
            dist = random.randint(50, 300)
            
        # 2. 複数の小さなステップに分けて「慣性」を出す
        steps = random.randint(3, 7)
        for i in range(steps):
            step_dist = dist // steps + random.randint(-50, 50)
            if step_dist > 0:
                self.page.scroll.down(step_dist)
            elif step_dist < 0:
                self.page.scroll.up(abs(step_dist))
            time.sleep(random.uniform(0.1, 0.4))
            
        # 3. 読了後の「微調整」 (人間が位置を直す動き)
        if random.random() < 0.4:
            time.sleep(random.uniform(0.5, 1.5))
            self.page.scroll.down(random.randint(-100, 100)) # 上下どちらかに微動
            
        # 4. 思考・読み込み待ち
        time.sleep(random.uniform(2.0, 5.0))
            
    def post_tweet(self, text, media_path=None):
        """
        Posts a tweet with text and optional media.
        """
        try:
            logger.info("Starting Post Tweet sequence (Stellar Stealth Implementation)...")

            # 1. ログイン後の「慣らし」動作
            # ランダム待機してからリロード
            sleep_random(3, 7)
            logger.info("Refreshing page for session stabilization...")
            self.page.refresh()
            sleep_random(5, 8)

            # ポップアップ掃除 (アプリインストール等)
            self.handle_interstitial_popups()
            
            # 「やりなおす」徹底排除
            self.handle_retry_button()

            # 3. 投稿ボタンを探してクリック
            logger.info("Locating Sidebar 'Post' button...")
            input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=2)
            
            if not input_box:
                # サイドバーのボタン
                post_nav_btn = self.page.ele("css:[data-testid='SideNav_NewTweet_Button']", timeout=3)
                if post_nav_btn:
                    logger.info("Clicked Sidebar Post button.")
                    self.stealth_click(post_nav_btn)
                    sleep_random(2, 4)
                    input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=4)
            
            if not input_box:
                # キーボードショートカット 'n'
                logger.info("Trying keyboard shortcut 'n' fallback...")
                self.page.actions.key_down('n').key_up('n')
                sleep_random(3, 5)
                input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=5)
 
            if not input_box:
                # 予備：ホームアイコン経由
                home_btn = self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=2)
                if home_btn:
                    self.stealth_click(home_btn)
                    sleep_random(2, 3)
                    input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=3)
 
            if not input_box:
                # 最終予備 (FAB)
                fab = self.page.ele("css:[aria-label='Post']", timeout=2) or \
                      self.page.ele("css:[aria-label='ポストする']", timeout=1)
                if fab:
                    self.stealth_click(fab)
                    sleep_random(2, 3)
                    input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=3)
 
            if not input_box:
                input_box = self.page.ele("css:.public-DraftEditor-content", timeout=2) or \
                            self.page.ele("css:[data-testid='tweetTextarea_0RichTextInputContainer']", timeout=1)
            
            if not input_box:
                logger.error("Could not find tweet input box. Giving up.")
                return False
                
            # 3. Handle Media Upload
            if media_path and os.path.exists(media_path):
                logger.info(f"📤 Uploading media: {os.path.basename(media_path)}")
                try:
                    # Target the hidden file input
                    file_input = self.page.ele("css:input[data-testid='fileInput']", timeout=2)
                    if not file_input:
                        # Sometimes it's inside a specific container
                        file_input = self.page.ele("xpath://input[@type='file' and @accept='image/*,video/*,image/gif']")
                    
                    if file_input:
                        file_input.input(os.path.abspath(media_path))
                        logger.info("  - Waiting for media processing...")
                        # Wait for preview to confirm upload
                        self.page.ele("css:[data-testid='attachments']", timeout=15)
                        sleep_random(2, 4)
                    else:
                        logger.warning("Media input not found. Skipping image.")
                except Exception as e:
                    logger.warning(f"Media upload failed (Skipping): {e}")
 
            # 4. Input Text
            logger.info(f"Typing tweet: {text[:30]}...")
            
            # Re-locate input box in case it was refreshed/re-rendered during media upload
            try:
                if not input_box or not input_box.states.is_displayed:
                    input_box = None
            except Exception:
                logger.info("Input box element expired/stale. Re-locating...")
                input_box = None

            if not input_box:
                input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=5)
                if not input_box:
                    input_box = self.page.ele("css:.public-DraftEditor-content", timeout=3) or \
                                self.page.ele("css:[data-testid='tweetTextarea_0RichTextInputContainer']", timeout=2)
            
            if not input_box:
                logger.error("Could not re-locate tweet input box before typing. Giving up.")
                return False

            try:
                input_box.click()
                sleep_random(0.5, 1.0)
                
                # Clear any residual text just in case (Draft.js safe)
                try:
                    self.page.actions.key_down(Keys.CONTROL)
                    try:
                        self.page.actions.type('a')
                    finally:
                        self.page.actions.key_up(Keys.CONTROL)
                    self.page.actions.key_down(Keys.BACKSPACE).key_up(Keys.BACKSPACE)
                    sleep_random(0.3, 0.6)
                except Exception as clear_err:
                    logger.debug(f"Draft.js text clear failed: {clear_err}")
                    try:
                        self.page.actions.key_up(Keys.CONTROL)
                    except:
                        pass
                
                try:
                    self.human_typing(input_box, text)
                except Exception as typ_err:
                    if "失效" in str(typ_err) or "stale" in str(typ_err).lower() or "invalid" in str(typ_err).lower():
                        logger.warning("Input box became stale during typing. Re-locating and retrying via batch fallback...")
                        input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=5) or \
                                    self.page.ele("css:.public-DraftEditor-content", timeout=3)
                        if input_box:
                            input_box.click()
                            sleep_random(0.5, 1.0)
                            input_box.input(text)
                            logger.success("Tweet text entered successfully after re-locating stale element.")
                        else:
                            raise typ_err
                    else:
                        raise typ_err
                
                sleep_random(1.0, 1.5)
                
                # Verify text presence in Draft.js contenteditable div (Direct injection fallback if needed)
                try:
                    entered_text = input_box.text or ""
                except Exception:
                    entered_text = ""
                
                if len(entered_text.strip()) == 0:
                    logger.warning("Draft.js typing check was empty or element stale. Performing final direct injection fallback...")
                    input_box = self.page.ele("css:[data-testid='tweetTextarea_0']", timeout=5) or \
                                input_box
                    if input_box:
                        try:
                            input_box.click()
                            sleep_random(0.3, 0.5)
                            input_box.input(text)
                            sleep_random(1.0, 1.5)
                        except Exception as final_err:
                            logger.error(f"Final injection fallback completely failed: {final_err}")
                            raise final_err
                else:
                    logger.success("Tweet text entered successfully.")
            except Exception as typ_err:
                logger.error(f"Error encountered during typing: {typ_err}")
                return False
            finally:
                # Always ensure CONTROL key is released at the end of the input block
                try:
                    self.page.actions.key_up(Keys.CONTROL)
                except:
                    pass
                
            sleep_random(1.5, 3.0)
            
            # 5. Click Tweet Button (Multiple Selectors for Inline vs Modal)
            tweet_btn = self.page.ele("css:[data-testid='tweetButtonInline']") or \
                        self.page.ele("css:[data-testid='tweetButton']")
            
            if tweet_btn:
                # Ensure it's not disabled (wait for upload to finish if needed)
                for _ in range(5):
                    if "disabled" not in (tweet_btn.attr("aria-disabled") or "").lower():
                        break
                    logger.info("Wait: Tweet button is disabled (Uploading?)...")
                    time.sleep(2)
 
                self.mouse_wiggle(tweet_btn)
                tweet_btn.click()
                
                # 送信後のエラーポップアップ検出
                sleep_random(1.5, 3.0)
                error_popups = [
                    "問題が発生しました。やりなおしてください。",
                    "問題が発生しました",
                    "やりなおしてください",
                    "Something went wrong, but don't fret",
                    "Something went wrong",
                    "let's give it another shot"
                ]
                
                for err_txt in error_popups:
                    err_ele = self.page.ele(f"text:{err_txt}", timeout=1)
                    if err_ele:
                        logger.error(f"Critical error toast detected: '{err_txt}'")
                        raise ValueError(f"CriticalError: Account is suspended/restricted. Tweet failed with: {err_txt}")
                
                logger.success("Tweet posted successfully.")
                sleep_random(3, 5)
                return True
            else:
                logger.error("Tweet button not found.")
                return False

        except Exception as e:
            logger.error(f"Post tweet failed: {e}")
            if "CriticalError" in str(e):
                raise e
            return False
