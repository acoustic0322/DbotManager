import time
import random
from loguru import logger
from utils.human_action import sleep_random
from modules.ixbrowser.ixbrowser_controller import IXBrowserController

class IXActionRunner:
    def __init__(self, username):
        self.username = username
        self.controller = IXBrowserController()
        self.profile_id = None
        self.page = None

    def setup_client(self):
        """Initializes IXBrowser Profile."""
        logger.info(f"Setting up IXBrowser for {self.username}...")
        self.profile_id = self.controller.get_or_create_profile(self.username)
        if not self.profile_id:
            logger.error(f"Could not get profile for {self.username}")
            return False
            
        self.page = self.controller.open_browser_dp(self.profile_id)
        if not self.page:
            logger.error(f"Could not open browser for {self.username}")
            return False
            
        return True

    def execute_follow(self, target_username):
        """Follows the target user using DrissionPage with human logic."""
        try:
            url = f"https://x.com/{target_username}"
            logger.info(f"Navigating to {url}")
            self.page.get(url)
            
            # Human-like delay after page load to prevent detection
            sleep_random(3, 5)
            
            html = self.page.html.lower() if self.page.html else ""
            
            # 1. Login Failure Check (If session expired or forced out)
            # Logged in users always see the AppTabBar_Home_Link on desktop UI
            if "login" in self.page.url.lower() or not self.page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=2):
                logger.error(f"[{self.username}] Login failed or session expired. Returning CriticalError to mark dead/frozen.")
                return False, "CriticalError"
            
            # 2. Anti-Bot / Freeze Check (Target or Actor is explicitly suspended)
            if "account suspended" in html or "account/access" in self.page.url.lower() or "凍結" in html:
                logger.error(f"[{self.username}] Target account or our account is suspended/locked.")
                return False, "CriticalError"
                
            if "doesn’t exist" in html or "存在しません" in html:
                logger.warning(f"User {target_username} not found.")
                return False, "NotFound"

            # 2. Check if already following
            unfollow_btn = self.page.ele(f"css:[data-testid$='-unfollow']", timeout=1)
            if unfollow_btn:
                logger.info(f"Already following {target_username}")
                return True, "AlreadyFollowed"
                
            # 3. Find Follow button
            follow_btn = self.page.ele(f"css:[data-testid$='-follow']", timeout=3)
            
            if not follow_btn:
                logger.error(f"Follow button not found on {target_username}'s page.")
                return False, "NotFound"
                
            # 4. Human-like scroll and click
            try:
                # Scroll a bit randomly like a human viewing the profile
                self.page.scroll.down(random.randint(100, 300))
                sleep_random(0.5, 1.5)
                follow_btn.scroll.to_see()
                sleep_random(0.5, 1.5)
            except:
                pass
                
            # Execute Follow
            follow_btn.click(by_js=False)
            logger.success(f"{self.username} -> Followed -> {target_username}")
            
            # Post-action human pause
            sleep_random(1, 2)
            
            return True, "Success"
            
        except Exception as e:
            logger.error(f"Follow failed for {target_username}: {str(e)}")
            return False, "UnknownError"

    def close(self):
        if self.profile_id:
            try:
                logger.info("Closing browser...")
                self.controller.close_browser(self.profile_id)
            except Exception as e:
                logger.error(f"Failed to close browser: {e}")
