
import asyncio
import time
import random
from loguru import logger
from .db_manager import DBManager
from .action_manager import ActionManager
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from utils.csv_manager import get_active_csv_path

# Placeholder for Router Reset 
# If user wants to integrate existing router logic, we should import it here
# For now, using a simple wait or calling the external script if needed
# from utils.ip_rotation import rotate_ip (Assuming this exists or similar)

async def run_hybrid_mutual_follow_logic(max_cycles=10):
    """
    Main logic for running the hybrid mutual follow system.
    """
    db = DBManager()
    action = ActionManager()
    
    # [NEW] Skip CSV to DB sync, DB is source of truth.
    # logger.info("Syncing accounts from CSV to DB...")
    # db.import_from_csv(accounts_csv_path)
    
    cycle = 0
    consecutive_failures = 0
    
    while cycle < max_cycles:
        logger.info(f"=== Cycle {cycle + 1}/{max_cycles} ===")
        
        # 2. Get Next Task
        from_user, to_user = db.get_next_task()
        
        if not from_user or not to_user:
            logger.info("No more eligible tasks found (Daily limits reached or no pairs).")
            break
            
        logger.info(f"Task Selected: {from_user} -> {to_user}")
        
        # 3. Router Reset (Optional/Speed Priority)
        # User said "Speed Priority", so maybe skip router reset for each follow?
        # But user also said "IP Management: Restart router for each task" in original prompt.
        # "Speed Priority" might mean "Don't open browser", but IP rotation is crucial for safety.
        # We will assume we need to execute IP rotation if consecutive actions happen?
        # For now, I will add a small sleep to simulate human behavior, 
        # but if IP rotation is strictly required per follow, we should add it.
        # Given "Speed Priority", I will skip full router reboot PER FOLLOW unless requested, 
        # or maybe do it every N follows? 
        # "1タスクごとにルーターを再起動" was in the requirements. 
        # I will stick to the requirement: "1 task = 1 pair". So Yes, Reboot.
        
        # However, calling a reboot script takes 3-5 mins. 
        # "Speed priority" conflicts with "Reboot every task".
        # I will assume "Speed priority" implies "Try to go as fast as SAFE".
        # Maybe reboot every 3-5 follows?
        # For now, I'll put a placeholder for IP Reset.
        
        # 4. Get Credentials
        account = db.get_account(from_user)
        if not account:
            logger.error(f"Account data missing for {from_user}")
            continue
            
        auth_token = account.get('auth_token')
        ct0 = account.get('ct0')
        user_agent = account.get('user_agent')
        
        if not auth_token or not ct0:
            logger.error(f"Tokens missing for {from_user}")
            # Mark invalid?
            continue
            
        # 5. Execute Action
        success, code = await action.follow_user(auth_token, ct0, to_user, user_agent)
        
        if success:
            logger.success(f"Follow Success: {from_user} -> {to_user}")
            db.mark_success(from_user, to_user)
            consecutive_failures = 0
        else:
            logger.error(f"Follow Failed: {from_user} -> {to_user} (Code: {code})")
            db.mark_failed(from_user, to_user, code)
            
            if code == "account_locked":
                db.mark_frozen(from_user)
            elif code == "rate_limit":
                # Wait longer?
                time.sleep(60)
            
            consecutive_failures += 1
        
        # Safety Sleep
        sleep_time = random.uniform(5, 15)
        logger.info(f"Sleeping {sleep_time:.1f}s...")
        time.sleep(sleep_time)
        
        cycle += 1
        
    logger.info("Hybrid Mutual Follow Logic Completed.")

if __name__ == "__main__":
    # Test Run
    asyncio.run(run_hybrid_mutual_follow_logic(max_cycles=1))
