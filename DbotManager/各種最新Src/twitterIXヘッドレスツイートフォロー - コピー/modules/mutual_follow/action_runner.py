from twikit import Client
import time
import random
from loguru import logger

class ActionRunner:
    def __init__(self, username, auth_token, ct0=None, proxy=None):
        self.username = username
        self.auth_token = auth_token
        self.ct0 = ct0
        self.client = None
        self.proxy = proxy
        
        # Simple UA list for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
        ]

    async def setup_client(self):
        """Initializes Twikit Client with random UA and Token."""
        ua = random.choice(self.user_agents)
        
        # Initialize Client
        # Note: language='jp' might be needed if Twikit supports it, strictly sticking to 'ja' if possible
        self.client = Client(language="ja", user_agent=ua, proxy=self.proxy)
        
        # Set cookies manually since we rely on auth_token
        # Twikit usually requires cookies. Auth_token is the 'auth_token' cookie.
        # We also need ct0 (csrf) often. 
        # If the CSV only has 'auth_token', we might be limited.
        # BUT the user request says: "twikit と auth_token を使用して"
        # Twikit's 'login' method usually uses username/password/totp or cookies.
        # If we only have auth_token string, we inject it into cookies.
        
        cookies = {}
        if self.auth_token:
            cookies["auth_token"] = self.auth_token
            
        if self.ct0:
             cookies["ct0"] = self.ct0
        
        # Twikit often needs detailed cookies or at least ct0. 
        # However, typically 'set_cookies' is the way.
        self.client.set_cookies(cookies)
        
        # Verify login state? 
        # Some endpoints might transparently work. If not, we might fail.
        # Let's trust the user knows auth_token is enough or we try strict.
        # Often 'ct0' is required for write actions. If missing, Twikit might fetch it or fail.
        # We can try to get it if we had a full session log, but here we don't.
        # Let's proceed with just auth_token context.
        return self.client

    async def execute_follow(self, target_username):
        """Follows the target user."""
        try:
            # 1. Get User ID (Twikit operations usually need User ID, not Screen Name)
            # Fetch user info
            user = await self.client.get_user_by_screen_name(target_username)
            
            if not user:
                logger.error(f"User {target_username} not found.")
                return False, "NotFound"

            # 2. Check if already following (Optimistic check via User obj if available)
            # The 'following' attribute might be on the user object
            if hasattr(user, 'following') and user.following:
                logger.info(f"Already following {target_username}")
                return True, "AlreadyFollowed"

            # 3. Follow
            await user.follow()
            logger.success(f"{self.username} -> Followed -> {target_username}")
            return True, "Success"

        except Exception as e:
            err_str = str(e)
            logger.error(f"Follow failed for {target_username}: {err_str}")
            
            if "Locked" in err_str or "Suspended" in err_str or "401" in err_str or "403" in err_str or "terminated" in err_str.lower():
                return False, "CriticalError"
            elif "429" in err_str:
                 return False, "RateLimit"
            
            return False, "UnknownError"
