
import asyncio
import random
import time
from twikit import Client
from loguru import logger

class TwikitBot:
    def __init__(self, account_data):
        self.screen_name = account_data['screen_name']
        self.auth_token = account_data['auth_token']
        self.ct0 = account_data.get('ct0')
        self.user_agent = account_data.get('user_agent')
        # Initialize Client with specific user agent if possible (Twikit 2.x supports user_agent arg in constructor or connection)
        self.client = Client('en-US', user_agent=self.user_agent)

    async def authenticate(self):
        """
        Authenticates using cookies.
        """
        try:
            cookies = {
                'auth_token': self.auth_token,
                'ct0': self.ct0
            }
            # Add other necessary cookies if available
            self.client.set_cookies(cookies)
            
            # Verify login by getting user info (lightweight)
            # or just assume consistency if no error raised on subsequent calls
            logger.info(f"@{self.screen_name}: Cookies set. Authenticated.")
            return True
        except Exception as e:
            logger.error(f"@{self.screen_name}: Authentication Failed: {e}")
            return False

    async def collect_users_from_hashtags(self, hashtags, limit=20):
        """
        Collects user IDs from tweets containing specified hashtags.
        """
        candidates = []
        try:
            # Shuffle hashtags to avoid pattern
            target_tags = list(hashtags)
            random.shuffle(target_tags)
            
            for tag in target_tags:
                if len(candidates) >= limit:
                    break
                    
                logger.info(f"@{self.screen_name}: Searching for {tag}...")
                tweets = await self.client.search_tweet(tag, product='Latest', count=20)
                
                if not tweets:
                    logger.warning(f"  -> No tweets found for {tag}")
                    continue
                    
                for tweet in tweets:
                    try:
                        user = tweet.user
                        if user and user.screen_name != self.screen_name: # Don't collect self
                            # Basic check: skip if protected or obviously bot-like? (Twikit user obj has details)
                            candidates.append(user)
                            if len(candidates) >= limit:
                                break
                    except:
                        continue
                
                # Small wait between searches
                await asyncio.sleep(random.uniform(2, 5))
                
            # Deduplicate
            unique_candidates = {u.id: u for u in candidates}.values()
            logger.info(f"@{self.screen_name}: Collected {len(unique_candidates)} unique candidates.")
            return list(unique_candidates)

        except Exception as e:
            logger.error(f"@{self.screen_name}: Error collecting users: {e}")
            return []

    async def follow_by_usernames(self, usernames, count=5, dry_run=False):
        """
        Follows a specific list of usernames with human-like 'jitter' and 'thinking time'.
        """
        followed_count = 0
        targets = list(usernames)
        random.shuffle(targets)
        
        for username in targets:
            if followed_count >= count:
                break
                
            try:
                username = username.strip().replace('@', '')
                logger.info(f"@{self.screen_name}: [Human] Processing target @{username}...")
                
                # 1. Thinking time (Deciding to click)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                if dry_run:
                    logger.info(f"@{self.screen_name}: [DRY RUN] Would follow @{username}")
                    followed_count += 1
                else:
                    user = await self.client.get_user_by_screen_name(username)
                    if user:
                        # 2. Reading profile delay
                        await asyncio.sleep(random.uniform(1.5, 3.5))
                        
                        await user.follow()
                        logger.success(f"@{self.screen_name}: Followed @{username}")
                        followed_count += 1
                    else:
                        logger.warning(f"@{self.screen_name}: User @{username} not found.")
                
                # 3. Post-action 'Human' relaxation delay
                wait_time = random.uniform(15.0, 45.0)
                logger.info(f"  -> Next action in {wait_time:.1f}s (Jitter)...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                err = str(e)
                logger.error(f"@{self.screen_name}: Failed to follow @{username}: {err}")
                if "Locked" in err or "Suspended" in err or "401" in err or "403" in err or "terminated" in err.lower():
                    # Propagate critical error to abort batch for this account
                    logger.error(f"@{self.screen_name}: CRITICAL ERROR detected. Aborting session.")
                    raise e
                await asyncio.sleep(5) 
                
        return followed_count

    async def execute_follow(self, users, count=10, dry_run=False, speed_mode=False):
        """
        Phase 1: Follow Phase.
        Follows 'count' users from the list.
        """
        followed_count = 0
        
        # Shuffle execution order
        targets = list(users)
        random.shuffle(targets)
        
        for user in targets:
            if followed_count >= count:
                break
                
            try:
                if dry_run:
                    logger.info(f"@{self.screen_name}: [DRY RUN] Would follow {user.screen_name}")
                    followed_count += 1
                else:
                    await user.follow()
                    logger.success(f"@{self.screen_name}: Followed {user.screen_name}")
                    followed_count += 1
                
                # Wait logic
                if speed_mode:
                    wait_time = random.uniform(2, 5)
                else:
                    wait_time = random.uniform(10, 30)
                    
                logger.info(f"  -> Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                err = str(e)
                logger.error(f"@{self.screen_name}: Failed to follow {user.screen_name}: {err}")
                if "Locked" in err or "Suspended" in err or "401" in err or "403" in err or "terminated" in err.lower():
                    logger.error(f"@{self.screen_name}: CRITICAL ERROR detected. Aborting session.")
                    raise e
                # Don't break on single user failure (e.g. blocked), continue
                await asyncio.sleep(5) 
                
        return followed_count

    async def execute_engagement_phase(self, count=5, dry_run=False, speed_mode=False):
        """
        Phase 2: Engagement Phase (Unrelated Tweets).
        Targets usage of general terms to find random tweets for Like/RT.
        """
        engagement_count = 0
        keywords = ["日常", "ランチ", "おはよう", "疲れた", "ご飯", "帰宅", "仕事", "散歩", "天気"]
        
        try:
            # 1. Collect random unrelated tweets
            chosen_kw = random.choice(keywords)
            logger.info(f"@{self.screen_name}: [Phase 2] Searching '{chosen_kw}' for engagement targets...")
            
            tweets = await self.client.search_tweet(chosen_kw, product='Latest', count=20)
            if not tweets:
                logger.warning(f"  -> No tweets found for engagement.")
                return 0
                
            # Filter valid tweets (no links, Japanese) - simplified for now
            valid_tweets = [t for t in tweets if not t.retweeted_tweet and t.user.screen_name != self.screen_name]
            
            # Select random subset
            targets = random.sample(valid_tweets, min(count, len(valid_tweets)))
            
            for tweet in targets:
                try:
                    action_performed = False
                    
                    # Log target
                    logger.info(f"  -> Targeting tweet by @{tweet.user.screen_name}: {tweet.text[:20]}...")

                    # RT Logic (50%)
                    if random.random() < 0.5:
                        if dry_run:
                            logger.info(f"    [DRY RUN] 🔄 Retweet")
                        else:
                            await tweet.retweet()
                            logger.success(f"    🔄 Retweet executed")
                        action_performed = True
                    
                    # Like Logic (20%)
                    if random.random() < 0.2:
                        if dry_run: # Avoid double sleep if dry run
                             logger.info(f"    [DRY RUN] ❤️ Like")
                        else:
                            # Small wait between RT and Like if both happen
                            if action_performed: await asyncio.sleep(random.uniform(1, 3))
                            await tweet.favorite()
                            logger.success(f"    ❤️ Like executed")
                        action_performed = True

                    if action_performed:
                        engagement_count += 1
                        
                        # Wait logic
                        if speed_mode:
                            wait_time = random.uniform(2, 5)
                        else:
                            wait_time = random.uniform(10, 30)
                        
                        logger.info(f"    Waiting {wait_time:.1f}s...")
                        await asyncio.sleep(wait_time)
                        
                except Exception as e:
                    logger.error(f"    Action failed: {e}")
                    continue

            return engagement_count

        except Exception as e:
            logger.error(f"@{self.screen_name}: Engagement phase error: {e}")
            return 0

    async def delete_tweets_in_range(self, start_date_str, end_date_str):
        """
        Deletes own tweets within the specified date range (inclusive).
        Dates should be 'YYYY-MM-DD'.
        """
        from datetime import datetime, timedelta
        
        try:
            # Parse Range
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            logger.info(f"@{self.screen_name}: Starting Tweet Deletion ({start_date} ~ {end_date})")
            
            # Get User ID (Self)
            user = await self.client.get_user_by_screen_name(self.screen_name)
            if not user:
                logger.error("Could not fetch own user info.")
                return 0
                
            deleted_count = 0
            tweets = await user.get_tweets('Tweets', count=40)
            
            while tweets:
                processed_in_batch = 0
                
                for tweet in tweets:
                    processed_in_batch += 1
                    
                    # Created At Parsing
                    # Twikit usually returns datetime object in .created_at_datetime (UTC) or string in .created_at
                    # We'll use .created_at_datetime if available, else parse
                    if hasattr(tweet, 'created_at_datetime'):
                        # Adjust to local or just compare dates (UTC is fine for day granularity usually)
                        t_date = tweet.created_at_datetime.date() # UTC date
                    else:
                        # Fallback parsing if needed (skip for now, assume attribute exists)
                        continue
                    
                    # Check Range
                    if t_date > end_date:
                        # Too new, skip
                        continue
                    elif t_date < start_date:
                        # Too old, we can stop fetching if we iterate backwards (Twikit usually returns new first)
                        logger.info(f"Reached tweets older than start date ({t_date}). Stopping.")
                        return deleted_count
                    
                    # In Range -> Delete
                    try:
                        logger.info(f"Deleting tweet {tweet.id} from {t_date}...")
                        await tweet.delete()
                        deleted_count += 1
                        await asyncio.sleep(random.uniform(2, 4)) # Wait to avoid ban
                    except Exception as e:
                        logger.error(f"Failed to delete tweet {tweet.id}: {e}")
                        await asyncio.sleep(5)
                
                # Fetch Next Page
                if processed_in_batch == 0:
                     # Safety break if loop logic fails
                     break
                     
                await asyncio.sleep(2)
                tweets = await tweets.next()
                
            return deleted_count

        except Exception as e:
            import traceback
            logger.error(f"Deletion process error: {e}\n{traceback.format_exc()}")
            return 0
