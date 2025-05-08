"""
Configuration settings for the Sinhala Word Processor (PySide6 version)

This module contains application-wide settings and constants.
"""
import os
import json
import logging

logger = logging.getLogger("SinhalaWordProcessor.config")

# Application paths
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level to project root
USER_CONFIG_FILE = os.path.join(APP_DIR, "data", "user_config.json")
USER_DICT_FILE = os.path.join(APP_DIR, "data", "sinhalawordmap.json")
LEXICON_DIR = os.path.join(APP_DIR, "resources", "dictionary", "chunks")

# Default font settings
DEFAULT_FONT = "UN-Ganganee"  # Use a Sinhala font that's included in our fonts directory
DEFAULT_FONT_SIZE = 14
DEFAULT_WINDOW_SIZE = (1100, 780)

# Available font sizes
FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]

# Default user preferences
DEFAULT_PREFERENCES = {
    "theme": "light",
    "font": DEFAULT_FONT,
    "font_size": DEFAULT_FONT_SIZE,
    "keyboard_font_size": 26,  # Default keyboard font size
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
