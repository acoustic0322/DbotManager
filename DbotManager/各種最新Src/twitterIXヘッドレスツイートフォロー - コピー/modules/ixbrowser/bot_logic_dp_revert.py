class IXBrowserBotLogicDP:
    def login_with_token(self, auth_token, ct0=None, username=None, password=None, email=None, totp_secret=None, show_2fa_tab=False):
        """
        Logs into X.com using auth_token cookie.
        Includes robust account status verification (Lock/Suspension).
        Returns:
            (success (bool|str), new_cookies (dict|None))
        """
        try:
            logger.info("Performing token login...")
            
            # 1. Navigate to domain
            self.page.get("https://x.com")
            sleep_random(3, 5)
            
            # [Optimization] Check if already logged in
            if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']"):
                logger.success("Session already active (Home detected). Skipping cookie injection.")
                return True, None

            logger.info("Session not active. Injecting cookies...")
            
            # 2. Add Cookies
            cookies = [
                {'name': 'auth_token', 'value': auth_token, 'domain': '.x.com', 'path': '/', 'secure': True, 'httpOnly': True}
            ]
            if ct0:
                cookies.append({'name': 'ct0', 'value': ct0, 'domain': '.x.com', 'path': '/', 'secure': True, 'httpOnly': False})
            
            self.page.set.cookies(cookies)
            
            # 3. Refresh
            logger.info("Refreshing page to apply session cookies...")
            self.page.refresh()
            sleep_random(7, 10)
            
            # [Anti-Detection] Check for verification
            self._handle_verification_challenge()
            
            # 4. Comprehensive Status Verification
            status, msg = self.check_account_status()
            logger.info(f"Account Status Check: {status} - {msg}")
            
            if status == "LOCKED":
                logger.warning(f"🔒 [{username}] アカウントロック/検証要求検知")
                return "LOCKED", None
            elif status == "SUSPENDED":
                logger.error(f"🚫 [{username}] アカウント凍結検知")
                return "SUSPENDED", None
            
            # Final check for Home
            if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=5):
                logger.success("Token login successful.")
                return True, None
            else:
                logger.warning("Token login failed (Home not loaded). Check if token is valid.")
                return False, None

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False, None

    def login_with_password(self, username, password, email=None, totp_secret=None, show_2fa_tab=False):
        """
        Logs into X.com using Username/Password (and Email if challenged).
        """
        try:
            logger.info(f"Performing Password Login for {username}...")
            
            # 1. Go to Login Page
            if "login" not in self.page.url:
                self.page.get("https://x.com/i/flow/login")
            sleep_random(3, 6)
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
            
            # 「やり直す」ボタンが出たらクリック
            for kw in ["やりなおす", "やり直す", "Start over"]:
                try:
                    btn = self.page.ele(f'text:{kw}', timeout=2)
                    if btn:
                        btn.click()
                        logger.warning(f"「{kw}」ボタンを検知してクリックしました。")
                        sleep_random(2, 3)
                        break
                except: pass

            # 2. Input Username
            logger.info("Inputting Username...")
            username_input = None
            
            # Try multiple selectors
            for _ in range(3): # Retry logic
                username_input = self.page.ele("css:input[autocomplete='username']", timeout=5)
                if username_input: break
                
                # Fallback: generic text input often used for username/phone/email
                username_input = self.page.ele("css:input[name='text']", timeout=2)
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
            # Click Next
            next_keywords = ["Next", "次へ", "Lanjut", "ต่อไป", "Siguiente", "Próximo", "Suivant", "Weiter", "Volgende", "İleri", "Далее", "التالي", "Tiếp theo"]
            kw_pred = " or ".join([f"text()='{kw}'" for kw in next_keywords])
            next_btn = self.page.ele(f"xpath://span[{kw_pred}]", timeout=5)
            
            if next_btn:
                next_btn.click()
            else:
                # Fallback to data-testid or generic button
                next_btn = self.page.ele("css:[data-testid='identifierNext']", timeout=1) or \
                           self.page.ele("xpath://div[@role='button'][.//span]", timeout=1)
                if next_btn:
                    next_btn.click()
                else:
                    self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
            sleep_random(2, 3) 
            
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
            password_input = self.page.ele("css:input[name='password']", timeout=5)
            if not password_input:
                # Check directly for home again just in case
                if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']"):
                    return True
            if self.page.ele('text:セキュリティ検証の実行', timeout=3):
                logger.warning(f"🔒 [{username}] セキュリティ検証を検知 → ロック")
                return False    
            
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
            
            # 5. Click Login
            logger.info("Clicking Login button...")
            login_btn = self.page.ele("css:[data-testid='LoginForm_Login_Button']")
            if not login_btn:
                login_btn = self.page.ele("xpath://span[text()='Log in'] | //span[text()='ログイン']")

            if login_btn:
                if login_btn.attr("aria-disabled") == "true":
                    logger.warning("Login button is disabled.")
                login_btn.click()
            else:
                self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)

            # Wait for home load detection instead of fixed sleep
            logger.info("Waiting for Home redirect (up to 30s)...")
            totp_done = False
            
            for _ in range(30):
                if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=0.1):
                    logger.success("Password login successful.")
                    return True
                
                # Check for errors immediately
                if self.page.ele("text:The password you entered is incorrect", timeout=0.1) or \
                   self.page.ele("text:パスワードが正しくありません", timeout=0.1):
                    logger.error("Incorrect password detected.")
                    return "WRONG_PASSWORD"
                
                # Check for 2FA Challenge
                if not totp_done:
                    # Check for generic verification input
                    # Typically input[name='verification_code'] or data-testid='ocfEnterTextTextInput'
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
                                    
                                    logger.info(f"Inputting TOTP Code: {code}")
                                    v_input.input(code)
                                    sleep_random(1, 2)
                                    
                                    # Click Next/Verify
                                    next_btn = self.page.ele("xpath://span[text()='Next'] | //span[text()='次へ'] | //span[text()='Verify'] | //span[text()='認証']", timeout=1)
                                    if not next_btn:
                                        next_btn = self.page.ele("css:[data-testid='ocfEnterTextNextButton']", timeout=1)
                                        
                                    if next_btn:
                                        next_btn.click()
                                        totp_done = True
                                        logger.info("Clicked Verify/Next for TOTP.")
                                        sleep_random(3, 5) # Wait for processing
                                    else:
                                        self.page.actions.key_down(Keys.ENTER).key_up(Keys.ENTER)
                                        totp_done = True
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
                return "LOCKED"
            if status == "SUSPENDED":
                logger.error(f"🚫 [{username}] ログイン後の凍結検知: {msg}")
                return "SUSPENDED"
            
            if "home" in self.page.url or self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=2):
                 return True
                 
            # If we are here, probably failed or slow
            current_url = self.page.url
            logger.error(f"Password login failed (Timeout/Unknown). URL: {current_url}")
            
            if self.page.ele("text:Wrong password") or self.page.ele("text:パスワードが間違っています"):
                 logger.error("Login failed: Wrong password.")
                 return "WRONG_PASSWORD"

            return False
                
        except Exception as e:
            logger.error(f"Password login error: {e}")
            return False
