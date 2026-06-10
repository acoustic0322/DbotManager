import time
import os
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from utils.human_action import human_type, human_click, sleep_random, human_scroll

class IXBrowserBotLogic:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def force_japanese_language(self):
        """
        Ensures the X.com UI is set to Japanese via UI navigation.
        """
        try:
            logger.info("Checking language settings...")
            # If we see common Japanese text, skip
            if self.driver.find_elements(By.XPATH, "//*[text()='ホーム' or text()='話題を検索']"):
                logger.debug("Language already Japanese or partially localized.")
                return

            logger.info("Navigating to Language Settings via UI...")
            # 1. Click "More" icon
            try:
                more_btns = self.driver.find_elements(By.XPATH, "//div[@aria-label='More'] | //div[@aria-label='もっと見る'] | //*[@data-testid='AppTabBar_More_Menu']")
                if more_btns:
                    human_click(self.driver, more_btns[0])
                    sleep_random(2, 3)
                
                # 2. Click "Settings and privacy"
                settings_btns = self.driver.find_elements(By.XPATH, "//span[text()='Settings and privacy'] | //span[text()='設定とプライバシー']")
                if settings_btns:
                    human_click(self.driver, settings_btns[0])
                    sleep_random(2, 3)

                # 3. Click "Accessibility, display, and languages"
                acc_btns = self.driver.find_elements(By.XPATH, "//span[text()='Accessibility, display, and languages'] | //span[text()='アクセシビリティ、表示、言語']")
                if acc_btns:
                    human_click(self.driver, acc_btns[0])
                    sleep_random(2, 3)

                # 4. Click "Languages"
                lang_btns = self.driver.find_elements(By.XPATH, "//span[text()='Languages'] | //span[text()='言語']")
                if lang_btns:
                    human_click(self.driver, lang_btns[0])
                    sleep_random(2, 3)

                # 5. Click "Display language"
                disp_btns = self.driver.find_elements(By.XPATH, "//span[text()='Display language'] | //span[text()='表示言語']")
                if disp_btns:
                    human_click(self.driver, disp_btns[0])
                    sleep_random(3, 5)

                # Find Japanese option
                ja_option_xpath = "//span[text()='Japanese - 日本語']"
                ja_options = self.driver.find_elements(By.XPATH, ja_option_xpath)
                
                if ja_options:
                    human_click(self.driver, ja_options[0])
                    sleep_random(2, 3)
                    save_btns = self.driver.find_elements(By.XPATH, "//span[text()='Save'] | //span[text()='保存']")
                    if save_btns:
                        human_click(self.driver, save_btns[0])
                        logger.success("Language switched to Japanese.")
                        sleep_random(2, 3)
            except Exception as e:
                logger.warning(f"UI Navigation for language failed: {e}")
        except Exception as e:
            logger.error(f"Error in force_japanese_language: {e}")

    def login_with_token(self, auth_token, ct0=None):
        """
        Logs into X.com using auth_token cookie.
        """
        try:
            logger.info("Performing token login...")
            
            # 1. Navigate to domain to set cookies
            self.driver.get("https://x.com")
            sleep_random(5, 7)
            
            # 2. Add Cookies
            cookies = [
                {'name': 'auth_token', 'value': auth_token, 'domain': '.x.com', 'path': '/', 'secure': True, 'httpOnly': True}
            ]
            if ct0:
                cookies.append({'name': 'ct0', 'value': ct0, 'domain': '.x.com', 'path': '/', 'secure': True, 'httpOnly': False})
            
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            # 3. Refresh to apply
            logger.info("Refreshing page to apply cookies...")
            self.driver.refresh()
            sleep_random(7, 10)
            
            # 4. Verify
            if "home" in self.driver.current_url or self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]'):
                logger.success("Token login successful.")
                self.force_japanese_language()
                return True
            else:
                logger.error("Token login failed (Home not loaded). Check if token is valid.")
                return False

        except Exception as e:
            logger.error(f"Token login exception: {e}")
            return False

    def update_profile(self, name=None, bio=None, location=None, icon_path=None, header_path=None):
        """
        Updates profile information using UI elements.
        """
        try:
            logger.info("Navigating to Profile...")
            profile_link = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="AppTabBar_Profile_Link"]')))
            human_click(self.driver, profile_link)
            sleep_random(5, 7)
            
            # Click Edit profile
            edit_xpath = "//span[text()='Edit profile'] | //span[text()='プロフィールを編集']"
            try:
                edit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, edit_xpath)))
                human_click(self.driver, edit_btn)
            except:
                edit_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="editProfileButton"]')))
                human_click(self.driver, edit_btn)
            sleep_random(3, 5)

            # Update Name
            if name:
                logger.info(f"Updating Name: {name}")
                name_field = self.wait.until(EC.presence_of_element_located((By.NAME, "displayName")))
                name_field.click()
                name_field.send_keys(u'\ue009' + 'a')
                name_field.send_keys(u'\ue017')
                time.sleep(1)
                human_type(name_field, name)
                sleep_random(1, 2)

            # Update Bio
            if bio:
                logger.info(f"Updating Bio: {bio}")
                bio_field = self.driver.find_element(By.NAME, "description")
                bio_field.click()
                bio_field.send_keys(u'\ue009' + 'a')
                bio_field.send_keys(u'\ue017')
                time.sleep(1)
                human_type(bio_field, bio)
                sleep_random(1, 2)

            # Update Icon/Header (simplified for now, using absolute paths)
            apply_xpath = "//span[text()='Apply'] | //span[text()='適用']"
            if icon_path and os.path.exists(icon_path):
                logger.info(f"Uploading Icon: {icon_path}")
                avatar_input = self.driver.find_element(By.XPATH, "//div[@aria-label='Add profile photo' or @aria-label='プロフィール画像を追加']//input[@type='file']")
                avatar_input.send_keys(os.path.abspath(icon_path))
                sleep_random(5, 8)
                apply_btns = self.driver.find_elements(By.XPATH, apply_xpath)
                if apply_btns:
                    human_click(self.driver, apply_btns[0])
                    sleep_random(3, 5)

            if header_path and os.path.exists(header_path):
                logger.info(f"Uploading Header: {header_path}")
                header_input = self.driver.find_element(By.XPATH, "//div[@aria-label='Add header photo' or @aria-label='ヘッダー画像を追加']//input[@type='file']")
                header_input.send_keys(os.path.abspath(header_path))
                sleep_random(5, 8)
                apply_btns = self.driver.find_elements(By.XPATH, apply_xpath)
                if apply_btns:
                    human_click(self.driver, apply_btns[0])
                    sleep_random(3, 5)

            # Save
            logger.info("Saving changes...")
            save_xpath = "//span[text()='Save'] | //span[text()='保存']"
            save_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
            human_click(self.driver, save_btn)
            
            sleep_random(7, 10)
            logger.success("Profile updated successfully via UI.")
            return True

        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            return False
