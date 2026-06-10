import os
import time
from modules.ai_generator import AIGenerator
from loguru import logger
import json

# Configuration
SETTINGS_FILE = 'data/settings.json'
ICON_DIR = 'data/assets/icons'
HEADER_DIR = 'data/assets/headers'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def main():
    settings = load_settings()
    api_key = settings.get('gemini_api_key')
    
    if not api_key:
        logger.error("Gemini API Key not found in settings. Please configure it in the dashboard first.")
        return

    ai = AIGenerator(api_key)
    
    print("=== Asset Generator ===")
    try:
        count = int(input("Enter number of sets to generate (Icon + Header): "))
    except ValueError:
        logger.error("Invalid number.")
        return

    # Prompts for 20s Japanese Female
    icon_prompt = "A beautiful young Japanese woman, selfie, casual daily life, natural lighting, high quality, photorealistic, 4k"
    header_prompt = "Aesthetic scenery, Tokyo street, cafe, nature, soft lighting, cozy vibes, high quality, 4k"

    logger.info(f"Starting generation of {count} sets...")

    for i in range(count):
        logger.info(f"Generating Set {i+1}/{count}...")
        
        # Generator Icon (Curated Waifu.im)
        icon_path = ai.generate_icon_waifuim(save_dir=ICON_DIR, prefix=f"icon_gen_{int(time.time())}_{i}")
        
        if icon_path:
            logger.success(f"Icon generated: {icon_path}")
        else:
            logger.error("Failed to generate icon.")

        # Generator Header (Picsum)
        header_path = ai.generate_header_picsum(save_dir=HEADER_DIR, prefix=f"header_gen_{int(time.time())}_{i}")
        if header_path:
            logger.success(f"Header generated: {header_path}")
        else:
            logger.error("Failed to generate header.")
            
        time.sleep(0.5) # Minimal delay for file operations

    logger.info("Generation complete.")

if __name__ == "__main__":
    main()
