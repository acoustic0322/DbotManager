
from twikit import Client
import asyncio
from loguru import logger
import random

class ActionManager:
    def __init__(self):
        pass

    async def follow_user(self, auth_token, ct0, target_username, user_agent=None):
        """
        Executes follow action using Twikit with provided cookies.
        Returns: (success: bool, code: str)
        """
        # Initialize Client
        # Twikit uses 'en-US' by default, maybe set to Japanese?
        client = Client(language="ja", user_agent=user_agent)
        
        # Set Cookies
        # Note: Twikit's set_cookies expects a dictionary
        cookies = {
            "auth_token": auth_token,
            "ct0": ct0
        }
        client.set_cookies(cookies)
        
        try:
            # Get User ID
            # This is an API call
            logger.debug(f"Fetching ID for {target_username}...")
            user = await client.get_user_by_screen_name(target_username)
            
            if not user:
                logger.error(f"User {target_username} not found.")
                return False, "not_found"
                
            # Follow
            logger.info(f"Following {target_username} ({user.id})...")
            await client.follow_user(user.id)
            
            return True, "ok"

        except Exception as e:
            err_str = str(e).lower()
            logger.error(f"Twikit error following {target_username}: {e}")
            
            if "locked" in err_str or "suspended" in err_str:
                return False, "account_locked"
            if "rate limit" in err_str:
                return False, "rate_limit"
            
            return False, f"error_{err_str[:20]}"
