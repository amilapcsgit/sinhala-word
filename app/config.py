"""
Configuration settings for the Sinhala Word Processor (PySide6 version)

This module contains application-wide settings and constants.
"""
import os
import json
import logging
import sys

logger = logging.getLogger("SinhalaWordProcessor.config")

# Application paths
def get_app_dir():
    """Get the application directory, handling both frozen and non-frozen cases."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # If the application is frozen (PyInstaller) and _MEIPASS is available
        return sys._MEIPASS
    else:
        # If running from source or _MEIPASS is not available
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_user_data_dir():
    """Get the user data directory."""
    user_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'SinhalaWord')
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return user_data_dir

APP_DIR = get_app_dir()
USER_DATA_DIR = get_user_data_dir()

# User configuration files
USER_CONFIG_FILE = os.path.join(USER_DATA_DIR, "user_config.json")
USER_DICT_FILE = os.path.join(USER_DATA_DIR, "sinhalawordmap.json")

# Application resources
LEXICON_DIR = os.path.join(APP_DIR, "resources", "dictionary", "chunks")

# Default font settings
DEFAULT_FONT = "UN-Ganganee"  # Use a Sinhala font that's included in our fonts directory
DEFAULT_FONT_SIZE = 20
DEFAULT_WINDOW_SIZE = (1280, 720)

# Available font sizes
FONT_SIZES = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 44, 48, 54, 60, 66, 72, 80, 88, 96]

# Default user preferences
DEFAULT_PREFERENCES = {
    "theme": "dark",
    "font": DEFAULT_FONT,
    "font_size": DEFAULT_FONT_SIZE,
    "keyboard_font_size": 20,  # Default keyboard font size
    "window_size": DEFAULT_WINDOW_SIZE,
    "show_keyboard": True,
    "show_suggestions": True,
    "singlish_enabled": True,
    "recent_files": []
}

# Maximum number of recent files to remember
MAX_RECENT_FILES = 10

def load_user_preferences():
    """
    Load user preferences from the config file.
    
    Returns:
        dict: User preferences, or default preferences if file not found or invalid
    """
    try:
        if os.path.exists(USER_CONFIG_FILE):
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                logger.info(f"Loaded user preferences from {USER_CONFIG_FILE}")
                # Ensure all default keys exist
                for key, value in DEFAULT_PREFERENCES.items():
                    if key not in prefs:
                        prefs[key] = value
                return prefs
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading user preferences: {e}")
    
    # Return default preferences if file not found or invalid
    return DEFAULT_PREFERENCES.copy()

def save_user_preferences(prefs):
    """
    Save user preferences to the config file.
    
    Args:
        prefs (dict): User preferences to save
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(USER_CONFIG_FILE), exist_ok=True)
        
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=4)
        logger.info(f"Saved user preferences to {USER_CONFIG_FILE}")
    except IOError as e:
        logger.error(f"Error saving user preferences: {e}")

def add_recent_file(prefs, filepath):
    """
    Add a file to the recent files list.
    
    Args:
        prefs (dict): User preferences
        filepath (str): Path to the file to add
    
    Returns:
        dict: Updated user preferences
    """
    if 'recent_files' not in prefs:
        prefs['recent_files'] = []
    
    # Remove the file if it already exists in the list
    if filepath in prefs['recent_files']:
        prefs['recent_files'].remove(filepath)
    
    # Add the file to the beginning of the list
    prefs['recent_files'].insert(0, filepath)
    
    # Limit the number of recent files
    prefs['recent_files'] = prefs['recent_files'][:MAX_RECENT_FILES]
    
    return prefs
