import sqlite3
import json
import os
import sys
import time
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ai_generator import AIGenerator
from modules.mutual_follow.db_manager import DBManager

def load_settings():
    settings_file = 'data/settings.json'
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    db = DBManager()
    settings = load_settings()
    api_keys = settings.get("gemini_api_key", "")
    
    # Initialize Generator
    ai = AIGenerator(api_keys=api_keys)
    
    # Get unassigned accounts
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, display_name, biography FROM accounts WHERE category IS NULL OR category = '' OR category = '日常生活'")
    targets = cursor.fetchall()
    
    if not targets:
        logger.info("No unassigned accounts found.")
        return

    logger.info(f"Targeting {len(targets)} accounts for classification...")
    
    for username, display_name, bio in targets:
        try:
            # Use improved logic (Scoring + AI Fallback)
            category = ai.determine_theme(display_name or username, bio)
            
            if category:
                cursor.execute("UPDATE accounts SET category = ? WHERE username = ?", (category, username))
                conn.commit()
                logger.success(f"@{username} -> {category}")
            else:
                logger.warning(f"@{username} remains unassigned.")
            
            # APIクォータ対策のウェイト
            time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error processing @{username}: {e}")
            
    conn.close()
    logger.info("Distribution complete.")

if __name__ == "__main__":
    main()
