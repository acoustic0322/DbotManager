import time
import random
import math
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from loguru import logger

def sleep_random(min_seconds=1.0, max_seconds=3.0):
    """Sleeps for a random amount of time with a slight Gaussian bias towards the lower-middle."""
    if min_seconds >= max_seconds:
        time.sleep(min_seconds)
        return
        
    # Gaussian distribution centered around (min + max) / 2 could be too uniform.
    # Let's use triangular or uniform for simplicity but add micro-variations.
    base = random.uniform(min_seconds, max_seconds)
    # Add slight noise
    noise = random.uniform(-0.1, 0.1)
    final_sleep = max(0.1, base + noise)
    time.sleep(final_sleep)

def human_type(element, text, min_delay=0.12, max_delay=0.35):
    """Types text into an element with human-like delays and occasional 'mistakes' (optional)."""
    for char in text:
        element.send_keys(char)
        # Random delay between keystrokes
        sleep_random(min_delay, max_delay)
        
        # 3% chance to pause longer (thinking)
        if random.random() < 0.03:
            sleep_random(0.8, 2.0)

def human_scroll(driver, steps=5):
    """Scrolls the page in small increments."""
    for _ in range(steps):
        # Random scroll amount
        amount = random.randint(100, 400)
        driver.execute_script(f"window.scrollBy(0, {amount});")
        sleep_random(0.2, 0.8)

def bezier_curve(p0, p1, p2, p3, t):
    """Calculates a point on a cubic Bezier curve."""
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)

def move_mouse_human(driver, element):
    """
    Moves mouse to an element using a simulate Bezier curve human path.
    Note: Selenium's move_to_element is instantaneous in standard drivers.
    Undetected-chromedriver doesn't inherently fix mouse physics.
    We can simulate 'hover' steps or use ActionChains with pauses, 
    but for 'undetected' it is often better to just use JS click if we want to be stealthy 
    OR use a very robust input simulation.
    
    However, standard ActionChains `move_to_element` is usually 'good enough' if timing is right.
    For high-end spoofing, we'd calculate a path and move strictly step-by-step.
    """
    action = ActionChains(driver)
    action.move_to_element(element).perform()
    # Adding a small delay after moving before clicking is very human
    sleep_random(0.3, 0.7)

def human_click(driver, element):
    """Moves to element and clicks with human timing."""
    move_mouse_human(driver, element)
    element.click()
    sleep_random(0.5, 1.5)
