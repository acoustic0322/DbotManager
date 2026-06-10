import os
import pandas as pd
from twikit import Client
from loguru import logger
from datetime import datetime
import asyncio

HISTORY_FILE = 'data/created_profiles.csv'

class ProfileManager:
    def __init__(self):
        self._init_history_file()

    def _init_history_file(self):
        if not os.path.exists(HISTORY_FILE):
            df = pd.DataFrame(columns=['screen_name', 'assigned_name', 'bio', 'location', 'icon_path', 'header_path', 'updated_at'])
            df.to_csv(HISTORY_FILE, index=False)

    def log_history(self, screen_name, name, bio, location, icon_path, header_path):
        new_row = {
            'screen_name': screen_name,
            'assigned_name': name,
            'bio': bio,
            'location': location,
            'icon_path': icon_path,
            'header_path': header_path,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        df = pd.read_csv(HISTORY_FILE)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(HISTORY_FILE, index=False)

    async def update_account_profile(self, account_data, profile_data, icon_path=None, header_path=None, targets=None):
        if targets is None:
            targets = ['name', 'bio', 'location', 'icon', 'header']

        client = Client(language='en-US', user_agent=account_data.get('user_agent'))
        screen_name = account_data.get('screen_name')
        cookies_path = account_data.get('cookies_path', f'data/cookies/{screen_name}.json')

        try:
            # Login Strategy
            logged_in = False
            
            # 1. Try loading cookies first
            if os.path.exists(cookies_path):
                client.load_cookies(cookies_path)
                logged_in = True
            
            # 2. If no cookies, try simple auth_token set (fallback)
            if not logged_in and account_data.get('auth_token') and account_data.get('ct0'):
                client.set_cookies({
                    'auth_token': account_data.get('auth_token'),
                    'ct0': account_data.get('ct0')
                })
                # Check validity? For now assume it might work or fail at request time.
                # But to avoid 400 Bad Auth, we might want to ensure login.
            
            # 3. Perform explicit full login if we have password (safest for sensitive operations)
            # Or if the previous request failed (which we handle in try/catch, but maybe proactive here)
            # Actually, let's keep it simple: Try explicit login if we have credentials and no cookie file?
            # Or always try to login if not logged in?
            
            # For update_profile to work reliably, we often need a refreshed session.
            # If we just set cookies from random ct0, it fails.
            # So let's try to LOGIN using credentials if available.
            
            if not os.path.exists(cookies_path) and account_data.get('password'):
                logger.info("Performing full login flow due to missing cookies...")
                await client.login(
                    auth_info_1=screen_name,
                    auth_info_2=account_data.get('email'),
                    password=account_data.get('password'),
                    totp_secret=account_data.get('totp_secret')
                )
                logged_in = True
            
            # --- Update Text (Name, Bio, Location) ---
            params = {}
            should_update_text = False
            
            if 'name' in targets and profile_data.get('name'):
                params['name'] = profile_data.get('name')
                should_update_text = True
            if 'bio' in targets and profile_data.get('bio'):
                params['description'] = profile_data.get('bio')
                should_update_text = True
            if 'location' in targets and profile_data.get('location'):
                params['location'] = profile_data.get('location')
                should_update_text = True

            if should_update_text:
                logger.info(f"Updating text profile for {screen_name}...")
                await client.post('https://api.twitter.com/1.1/account/update_profile.json', data=params)

            # --- Update Icon ---
            if 'icon' in targets and icon_path and os.path.exists(icon_path):
                logger.info(f"Uploading icon for {screen_name}...")
                with open(icon_path, 'rb') as f:
                    await client.post('https://api.twitter.com/1.1/account/update_profile_image.json', files={'image': f})
            
            # --- Update Header ---
            if 'header' in targets:
                 # Check if we should fetch a random generated header
                 if not header_path:
                      import glob
                      import random
                      headers = glob.glob('data/assets/headers/*.jpg') + glob.glob('data/assets/headers/*.png')
                      if headers:
                           header_path = random.choice(headers)
                           logger.info(f"Selected random header: {header_path}")
            
            if 'header' in targets and header_path and os.path.exists(header_path):
                logger.info(f"Uploading header for {screen_name}...")
                with open(header_path, 'rb') as f:
                    await client.post('https://api.twitter.com/1.1/account/update_profile_banner.json', files={'banner': f})

            # --- Update Icon (Fixed Logic) ---
            if 'icon' in targets:
                 if not icon_path:
                      import glob
                      import random
                      icons = glob.glob('data/assets/icons/*.jpg') + glob.glob('data/assets/icons/*.png')
                      if icons:
                           icon_path = random.choice(icons)
                           logger.info(f"Selected random icon: {icon_path}")

            if 'icon' in targets and icon_path and os.path.exists(icon_path):
                logger.info(f"Uploading icon for {screen_name}...")
                with open(icon_path, 'rb') as f:
                    await client.post('https://api.twitter.com/1.1/account/update_profile_image.json', files={'image': f})

            # --- Follow McDonald's Japan ---
            # Using '20s Female' preset usually implies this check
            if targets and '20s_female_mode' in targets: # We will pass this special flag
                 try:
                      logger.info("Following McDonald's Japan (@McDonaldsJapan)...")
                      # We need the User ID for McDonaldsJapan. 
                      # A safe way is to get it by screen_name first, or hardcode if known.
                      # Let's try to get user by screen name.
                      target_user = await client.get_user_by_screen_name('McDonaldsJapan')
                      if target_user:
                           await client.follow_user(target_user.id)
                           logger.success("Followed McDonald's Japan.")
                 except Exception as e_follow:
                      logger.warning(f"Failed to follow McDonald's Japan: {e_follow}")

            # Save cookies after success
            client.save_cookies(cookies_path)
            
            # Log success
            self.log_history(
                screen_name, 
                profile_data.get('name') if 'name' in targets else None, 
                profile_data.get('bio') if 'bio' in targets else None, 
                profile_data.get('location') if 'location' in targets else None, 
                icon_path if 'icon' in targets else None,
                header_path if 'header' in targets else None
            )
            logger.success(f"Profile updated for {screen_name}")
            return True, "Success"

        except Exception as e:
            # If error is 215 Bad Auth, and we haven't tried full login yet, we could retry?
            # But simpler to just fail for now. The logic above attempts login if no cookies.
            # If we had cookies but they were invalid, we might want to delete them and retry.
            logger.error(f"Failed to update profile for {screen_name}: {e}")
            
            # Retry logic for Bad Auth
            if '215' in str(e) or 'Bad Authentication' in str(e):
                logger.info("Auth failed. Clearing cookies and retrying full login...")
                if os.path.exists(cookies_path):
                    os.remove(cookies_path)
                
                try:
                    if account_data.get('password'):
                         await client.login(
                            auth_info_1=screen_name,
                            auth_info_2=account_data.get('email'),
                            password=account_data.get('password'),
                            totp_secret=account_data.get('totp_secret')
                        )
                         # Retry text update
                         if should_update_text:
                             await client.post('https://api.twitter.com/1.1/account/update_profile.json', data=params)
                         # Retry icon
                         if 'icon' in targets and icon_path and os.path.exists(icon_path):
                            with open(icon_path, 'rb') as f:
                                await client.post('https://api.twitter.com/1.1/account/update_profile_image.json', files={'image': f})
                         # Retry header
                         if 'header' in targets and header_path and os.path.exists(header_path):
                            with open(header_path, 'rb') as f:
                                await client.post('https://api.twitter.com/1.1/account/update_profile_banner.json', files={'banner': f})
                                
                         client.save_cookies(cookies_path)
                         logger.success(f"Profile updated for {screen_name} after retry")
                         return True, "Success (Retry)"
                except Exception as retry_e:
                     return False, f"Retry failed: {retry_e}"
            
            return False, str(e)
