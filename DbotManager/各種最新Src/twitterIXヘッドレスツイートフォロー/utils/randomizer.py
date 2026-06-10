import random
import time
from loguru import logger

def smart_sleep(min_sec: float, max_sec: float) -> None:
    """
    Sleeps for a random duration based on a Gaussian distribution
    to mimic human behavior.
    
    Args:
        min_sec (float): Minimum sleep time in seconds.
        max_sec (float): Maximum sleep time in seconds.
    """
    mu = (min_sec + max_sec) / 2
    sigma = (max_sec - min_sec) / 4  # 95% of values usually fall within 2 sigma
    
    sleep_time = random.gauss(mu, sigma)
    
    # Clamp the values to be strictly within min/max
    sleep_time = max(min_sec, min(sleep_time, max_sec))
    
    logger.info(f"Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)
