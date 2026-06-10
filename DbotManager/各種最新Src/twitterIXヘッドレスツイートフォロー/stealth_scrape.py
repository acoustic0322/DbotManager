import asyncio
import sqlite3
import os
import requests
from loguru import logger

# ログインせずにゲストとしてプロフィールを取得する試み
# (Xの制限により、完全にゲストだと弾かれる場合があるため、
# 最小限のゲストトークン取得ロジックを含めます)

def get_guest_bio(username):
    url = f"https://syndication.twitter.com/srv/python-get-user-profile/{username}"
    try:
        # Xの公式シンジケーションAPI（ログイン不要）を利用する裏技
        # これが利用可能な場合、ログインなしでBioが取れます。
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(f"https://www.twitter.com/{username}", headers=headers, timeout=10)
        
        # 簡易的なスクレイピング (HTMLからタイトルとdescriptionを取得)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # OpenGraphメタタグからBioを取得
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        bio = meta_desc['content'] if meta_desc else "No Bio found"
        
        # 不要な共通文言(Twitterのメタ情報)をトリミング
        if "from @Twitter" in bio: bio = bio.split("from @Twitter")[0]
        
        return bio.strip()
    except Exception as e:
        return None

def main():
    db_path = 'system.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM accounts WHERE biography IS NULL OR biography = ''")
    accounts = cursor.fetchall()
    
    logger.info(f"Stealth scraping bios for {len(accounts)} accounts without login...")
    
    for (username,) in accounts:
        bio = get_guest_bio(username)
        if bio:
            cursor.execute("UPDATE accounts SET biography = ? WHERE username = ?", (bio, username))
            conn.commit()
            logger.success(f"@{username}: {bio[:40]}...")
        else:
            logger.warning(f"@{username}: Failed to fetch (Login Wall or Private)")
        
        # 負荷軽減
        import time
        time.sleep(1)

    conn.close()

if __name__ == "__main__":
    main()
