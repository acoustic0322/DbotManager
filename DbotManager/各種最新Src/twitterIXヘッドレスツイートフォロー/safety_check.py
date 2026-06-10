from loguru import logger
import time

def check_login_status_with_page(page):
    """
    Checks the status of the account using the current page.
    Returns (status, message).
    """
    try:
        html = page.html.lower() if page.html else ""
        url = page.url.lower()
        
        # 1. Suspended Check
        if "account suspended" in html or "凍結" in html:
            return "Suspended", "アカウントが凍結されています"
        
        # 2. Locked / Security Check
        if "account/access" in url or "ロック" in html or "ログインを制限しています" in html:
            return "Locked", "ロックまたはセキュリティチェックが発生しています"
            
        # 3. Login Required Check
        if "login" in url and not page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=2):
            return "LoggedOut", "セッションが切れているか、ログインしていません"

        # 4. Normal Check
        if page.ele("css:[data-testid='AppTabBar_Home_Link']", timeout=3):
            return "Active", "正常にログイン・稼働しています"
            
        return "Unknown", "ログイン状態を特定できませんでした"

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return "Error", str(e)
