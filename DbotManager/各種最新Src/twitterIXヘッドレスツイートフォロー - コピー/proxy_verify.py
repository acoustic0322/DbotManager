from modules.router.pixel_rotator import PixelIPRotator
from loguru import logger
import sys

def main():
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
    
    logger.info("=== Pixel 4a (5G) IP Rotation Verification ===")
    
    rotator = PixelIPRotator()
    
    try:
        success, new_ip = rotator.rotate_ip()
        
        if success:
            logger.success(f"Verification Check: OK. New IP is {new_ip}")
        else:
            logger.error("Verification Check: FAILED.")
            
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
