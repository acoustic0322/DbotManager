import sqlite3
from modules.ai_generator import AIGenerator
from loguru import logger

def finalize_judgment_with_shields():
    db_path = 'system.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 最新のシールドロジックを搭載したAIGeneratorを使用
    ai = AIGenerator()
    
    cursor.execute("SELECT username, display_name, biography FROM accounts WHERE biography IS NOT NULL AND biography != ''")
    rows = cursor.fetchall()
    
    logger.info(f"Re-scanning {len(rows)} accounts with Hardened Shield Logic...")
    
    for username, display_name, biography in rows:
        # 新しい determine_theme を呼び出し（これがシールド付きの最新版）
        category = ai.determine_theme(display_name, bio=biography)
        
        cursor.execute("UPDATE accounts SET category = ? WHERE username = ?", (category, username))
        if "スピリチュアル" in category or "お菓子" in category:
            logger.success(f"Fixed Identity: @{username} -> {category}")

    conn.commit()
    conn.close()
    print("Final character alignment completed. All shields active.")

if __name__ == "__main__":
    finalize_judgment_with_shields()
