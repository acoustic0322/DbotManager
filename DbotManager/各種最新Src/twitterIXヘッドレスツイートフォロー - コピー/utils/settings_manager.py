import json
import os

SETTINGS_FILE = 'data/settings.json'

def load_settings():
    """
    Load settings from settings.json. Returns a dictionary.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    """
    Save settings to settings.json.
    """
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False
