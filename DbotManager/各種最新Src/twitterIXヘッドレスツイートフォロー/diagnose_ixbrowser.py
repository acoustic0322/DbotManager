import sys
import os
from loguru import logger

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.ixbrowser.ixbrowser_local_api import IXBrowserClient

def main():
    logger.info("=== ixBrowser Local API Diagnostic Tool ===")
    
    # 1. Test connection
    client = IXBrowserClient()
    logger.info(f"Connecting to ixBrowser Local API at {client.base_url}...")
    
    try:
        # Try listing profiles (very light API call)
        profiles = client.get_profile_list(limit=5)
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.info("\n[PROPOSED RESOLUTION]")
        logger.info("1. Make sure ixBrowser application is running on this PC.")
        logger.info("2. Go to ixBrowser Settings -> Local API, and ensure it is turned ON.")
        logger.info("3. Ensure the port is set to 53200 (or matches the script configuration).")
        return

    if client.code == 0:
        logger.success("✅ Connection successful!")
        if profiles:
            logger.info(f"Successfully retrieved {len(profiles)} profiles from ixBrowser.")
            for p in profiles[:5]:
                logger.info(f" - Profile ID: {p.get('profile_id', p.get('id'))}, Name: {p.get('name')}")
        else:
            logger.warning("No profiles found, but API responded successfully.")
            
        # Test group list
        groups = client.get_group_list()
        logger.info(f"Successfully retrieved {len(groups)} groups.")
    else:
        logger.error(f"❌ API responded with Error Code {client.code}: {client.message}")
        
        logger.info("\n[PROPOSED RESOLUTION]")
        if client.code in [1004, 1007] or "login" in client.message.lower() or "auth" in client.message.lower() or "not found" in client.message.lower():
            logger.warning("👉 The ixBrowser client appears to be LOGGED OUT, the session has expired, or the Local API is not fully initialized.")
            logger.info("Please open the ixBrowser desktop application on this PC and LOG IN again.")
            logger.info("Note: If you logged in on another PC, ixBrowser might have logged you out of this PC.")
        else:
            logger.info("Please open the ixBrowser desktop application and verify if it is working normally.")

if __name__ == "__main__":
    main()
