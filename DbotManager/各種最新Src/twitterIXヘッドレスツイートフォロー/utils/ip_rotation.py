import time
import requests
from loguru import logger
# from modules.router.controller import RouterController # Removed: File missing
from modules.router.pixel_rotator import PixelIPRotator

def create_standard_router():
    """Returns a PixelIPRotator as the standard rotation device."""
    # Switched from RouterController to PixelIPRotator
    return PixelIPRotator()

def get_current_ip(max_retries=5):
    """Attempts to get current external IP with retries."""
    urls = ["https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip"]
    for _ in range(max_retries):
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if len(ip.split('.')) == 4:
                        return ip
            except:
                continue
        time.sleep(2)
    return None

def ensure_ip_rotated(router, mandatory_wait=60, timeout=600):
    """
    Executes a guaranteed IP rotation sequence.
    Handles both PixelIPRotator (Self-contained) and RouterController (Manual flow).
    """
    
    # CASE 1: PixelIPRotator
    if isinstance(router, PixelIPRotator):
        logger.info("--- Starting IP Rotation (Pixel ADB) ---")
        # rotate_ip handles toggle, wait, reconnect, and verification internally
        success, new_ip = router.rotate_ip(max_rotation_retries=3)
        return success, new_ip

    # CASE 2: Legacy RouterController (Removed/Disabled)
    # logger.info("--- Starting IP Rotation Sequence (Router Reboot) ---")
    # ... Legacy code removed to prevent confusion ...
    
    logger.warning("No valid IP Rotation logic found for this device type.")
    return False, None
