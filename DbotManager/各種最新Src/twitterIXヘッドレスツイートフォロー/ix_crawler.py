import sqlite3
import time
from DrissionPage import ChromiumPage
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from loguru import logger

# 1つのログイン済みプロファイルを使って、全垢のプロフィールを巡回取得する

def scrape_via_ixbrowser():
    db_path = 'system.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 失敗している、または未取得のアカウントを抽出
    cursor.execute("SELECT username FROM accounts WHERE biography IS NULL OR biography = '' OR biography = 'No Bio found' LIMIT 200")
    targets = [r[0] for r in cursor.fetchall()]
    
    if not targets:
        logger.info("No targets to scrape.")
        return

    # IXBrowserのコントローラーを起動
    ix = IXBrowserController()
    
    # ログイン済みの代表プロファイルを1つ開く（最初の垢を使う）
    # ※もし特定のプロファイルIDを指定したい場合はここを書き換え
    cursor.execute("SELECT profile_id FROM accounts WHERE profile_id IS NOT NULL AND is_alive = 1 LIMIT 1")
    res = cursor.fetchone()
    if not res:
        logger.error("No valid IX profile found to start scraping.")
        return
    
    profile_id = res[0]
    logger.info(f"Using Profile ID {profile_id} as a crawler...")
    
    # DrissionPageでブラウザを制御
    page = ix.open_browser_dp(profile_id)
    if not page:
        logger.error("Failed to open IXBrowser profile via DrissionPage.")
        return

    from modules.ai_generator import AIGenerator
    generator = AIGenerator()

    try:
        for username in targets:
            logger.info(f"Crawling @{username}...")
            page.get(f"https://x.com/{username}")
            
            # ページ読み込み待機（要素が出るまで最大10秒待機）
            try:
                page.wait.ele_displayed('@data-testid=UserName', timeout=10)
            except:
                logger.warning(f"@{username}: Page load timeout.")
                continue

            # 表示名と自己紹介を取得
            display_name = ""
            bio_text = ""
            
            try:
                # 名前要素の取得
                name_ele = page.ele('@data-testid=UserName')
                if name_ele:
                    display_name = name_ele.text.split('\n')[0] # 最初の行が名前
                
                # 自己紹介要素の取得 (UserDescription)
                bio_element = page.ele('@data-testid=UserDescription')
                if bio_element:
                    bio_text = bio_element.text
                
                # DB更新
                cursor.execute("""
                    UPDATE accounts 
                    SET display_name = ?, biography = ? 
                    WHERE username = ?
                """, (display_name, bio_text, username))
                conn.commit()
                
                # 取得成功後にAI判定を即座に実行
                category = generator.determine_theme(display_name, bio_text)
                if category:
                    cursor.execute("UPDATE accounts SET category = ? WHERE username = ?", (category, username))
                    conn.commit()
                    logger.success(f"@{username} 取得完了: {display_name} / カテゴリ: {category}")
                else:
                    logger.info(f"@{username} 取得完了: {display_name} (カテゴリ判定なし)")

            except Exception as e:
                logger.warning(f"@{username}: Error reading profile data: {e}")
            
            time.sleep(3)
            
    finally:
        ix.close_browser(profile_id)
        conn.close()

if __name__ == "__main__":
    scrape_via_ixbrowser()
