import os
import sys
import json

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # If run as a bundle: .../Appname.app/Contents/MacOS/Appname
        # We want the folder containing Appname.app
        return os.path.abspath(os.path.join(os.path.dirname(sys.executable), "../../.."))
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
CHARACTERS_FILE = os.path.join(BASE_DIR, "characters.json")
SETTINGS_APP = os.path.join(BASE_DIR, "환경설정.app")

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

def load_characters():
    """Loads character data from JSON file."""
    if not os.path.exists(CHARACTERS_FILE):
        return []
    try:
        with open(CHARACTERS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading characters: {e}")
        return []

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return default_value

def open_settings_ui():
    """Launches the settings UI."""
    import subprocess
    if os.path.exists(SETTINGS_APP):
        subprocess.Popen(["open", SETTINGS_APP])
    else:
        # Fallback for dev mode
        dev_settings = os.path.join(BASE_DIR, "settings.py")
        subprocess.Popen([sys.executable, dev_settings])
