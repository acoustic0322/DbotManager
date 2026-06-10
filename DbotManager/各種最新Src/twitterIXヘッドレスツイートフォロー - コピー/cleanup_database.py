import sqlite3
import os
import sys
import json
from loguru import logger

# Add root to sys.path
sys.path.append(os.getcwd())

from modules.ai_generator import AIGenerator

def cleanup_db():
    db_path = 'system.db'
    settings_path = 'data/settings.json'
    
    if not os.path.exists(db_path):
        logger.error(f"Database {db_path} not found.")
        return

    # Load API keys from settings
    api_keys = ""
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                api_keys = settings.get("gemini_api_key", "")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    generator = AIGenerator(api_keys=api_keys)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check schema for biography
    cursor.execute("PRAGMA table_info(accounts)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'biography' not in columns:
        logger.warning("biography column missing. Adding it.")
        cursor.execute("ALTER TABLE accounts ADD COLUMN biography TEXT DEFAULT ''")
        conn.commit()

    # 2. Find problematic accounts (Forbidden, Missing, Generic)
    cursor.execute("""
        SELECT username, display_name, biography, category 
        FROM accounts 
        WHERE category LIKE '%裏垢%' 
           OR category LIKE '%女子%' 
           OR category LIKE '%乙女%'
           OR category LIKE '%姫%'
           OR category IS NULL 
           OR category = '' 
           OR category = 'unknown'
           OR category = '日常生活'
    """)
    rows = cursor.fetchall()
    
    total_fixed = 0
    total_targets = len(rows)
    logger.info(f"Targeting {total_targets} accounts for re-categorization...")

    for username, display_name, biography, old_category in rows:
        logger.info(f"Re-categorizing @{username} (Current: {old_category})")
        new_theme = generator.determine_theme(display_name or username, biography or "")
        
        if new_theme != old_category:
            cursor.execute("UPDATE accounts SET category = ? WHERE username = ?", (new_theme, username))
            logger.success(f"Updated @{username}: {old_category} -> {new_theme}")
            total_fixed += 1

    conn.commit()
    conn.close()
    logger.info(f"Finished cleanup. Fixed {total_fixed} accounts.")

if __name__ == "__main__":
    cleanup_db()
