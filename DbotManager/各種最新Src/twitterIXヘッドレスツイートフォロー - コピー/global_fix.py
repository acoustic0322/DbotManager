import sqlite3
import os
import sys
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ai_generator import AIGenerator

def main():
    # 裏垢女子をブロック済みのGeneratorを初期化
    ai = AIGenerator() 
    
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()
    
    # 全力ですべてのアカウントを正し、二度と「裏垢女子」を出現させない
    cursor.execute("SELECT username, display_name, biography FROM accounts")
    targets = cursor.fetchall()
    
    logger.info(f"Global Cleanup: Re-evaluating {len(targets)} accounts...")
    
    for username, display_name, bio in targets:
        # 新ロジック（裏垢女子除外・ランサー対応済）で再判定
        new_cat = ai.determine_theme(display_name or username, bio)
        
        cursor.execute("UPDATE accounts SET category = ? WHERE username = ?", (new_cat, username))
        conn.commit()
        logger.info(f"@{username} -> {new_cat}")
            
    conn.close()
    logger.success("Global classification fix complete. All 'Uraaka Joshi' removed.")

if __name__ == "__main__":
    main()
