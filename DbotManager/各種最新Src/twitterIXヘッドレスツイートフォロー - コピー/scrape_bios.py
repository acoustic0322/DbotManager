import asyncio
import sqlite3
import os
from twikit import Client
from loguru import logger

async def scrape_bios():
    db_path = 'system.db'
    if not os.path.exists(db_path):
        logger.error("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 自己紹介が空、または初期状態のアカウントを取得
    cursor.execute("SELECT username, auth_token, ct0 FROM accounts WHERE is_alive = 1")
    accounts = cursor.fetchall()
    
    logger.info(f"Starting bio scrape for {len(accounts)} accounts...")
    
    for username, token, ct0 in accounts:
        try:
            client = Client(language='ja-JP')
            
            # クッキー設定
            cookies_path = f'data/cookies/{username}.json'
            if os.path.exists(cookies_path):
                client.load_cookies(cookies_path)
            else:
                client.set_cookies({
                    'auth_token': token,
                    'ct0': ct0
                })
            
            # 自分自身のユーザー情報を取得
            user = await client.get_user_by_screen_name(username)
            bio = user.description
            display_name = user.name
            
            # DBを更新（カラムがない場合は追加を試みる）
            try:
                cursor.execute("UPDATE accounts SET display_name = ? WHERE username = ?", (display_name, username))
                # biographyカラムがもしあれば更新（念のため try-except）
                cursor.execute("UPDATE accounts SET biography = ? WHERE username = ?", (bio, username))
            except:
                # biographyカラムがない場合は display_name だけでも更新
                pass
            
            conn.commit()
            logger.success(f"Fetched bio for @{username}: {bio[:30]}...")
            
            # 連続アクセスによるロック回避のため少し待機
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"Failed to fetch bio for @{username}: {e}")
            continue

    conn.close()
    logger.info("Bio scraping process completed.")

if __name__ == "__main__":
    asyncio.run(scrape_bios())
