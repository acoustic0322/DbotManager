import sqlite3
import os
import sys
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ai_generator import AIGenerator

def main():
    ai = AIGenerator() # No keys needed if we use keywords/logic
    
    conn = sqlite3.connect('system.db')
    cursor = conn.cursor()
    
    # 男性的なワードが含まれているのに「裏垢女子」になっているアカウントを抽出
    masculine_words = ["俺", "僕", "駿", "鋼鉄", "親父", "おじさん", "パパ", "男子", "野郎", "漢"]
    
    cursor.execute("SELECT username, display_name, biography FROM accounts WHERE category LIKE '%裏垢女子%' OR category LIKE '%女子%'")
    targets = cursor.fetchall()
    
    fixed_count = 0
    for username, display_name, bio in targets:
        combined = f"{display_name} {bio}".lower()
        if any(mw in combined for mw in masculine_words):
            logger.warning(f"Fixing misclassified masculine account: @{username} ({display_name})")
            
            # 再判定（ガードが効くはず）
            new_cat = ai.determine_theme(display_name, bio)
            
            cursor.execute("UPDATE accounts SET category = ? WHERE username = ?", (new_cat, username))
            conn.commit()
            logger.success(f"@{username} -> {new_cat}")
            fixed_count += 1
            
    conn.close()
    logger.info(f"Fixed {fixed_count} accounts.")

if __name__ == "__main__":
    main()
