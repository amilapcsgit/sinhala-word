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
    if getattr(sys, 'frozen', False):
        # If the application is frozen (PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            # First try _MEIPASS (PyInstaller's temp directory)
            base_dir = sys._MEIPASS
        else:
            # If _MEIPASS is not available, use the directory where the executable is located
            base_dir = os.path.dirname(sys.executable)
        
        # Check if resources exist in the executable's directory
        if os.path.exists(os.path.join(base_dir, "resources")):
            return base_dir
        
        # If resources don't exist in the executable's directory, check the current working directory
        if os.path.exists(os.path.join(os.getcwd(), "resources")):
            return os.getcwd()
            
        return base_dir
    else:
        # If running from source
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_file(filename, search_paths=None):
    """
    Find a file by searching in multiple locations.
    
    Args:
        filename (str): The name of the file to find
        search_paths (list): Optional list of paths to search in
        
    Returns:
        str: The full path to the file if found, None otherwise
    """
    if search_paths is None:
        # Default search paths
        search_paths = [
            # Current directory
            os.getcwd(),
            # Executable directory (if frozen)
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else None,
            # App directory
            APP_DIR,
            # User data directory
            USER_DATA_DIR,
            # Data directory in app directory
            os.path.join(APP_DIR, "data"),
        ]
        # Remove None entries
        search_paths = [p for p in search_paths if p is not None]
    
    # Search for the file
    for path in search_paths:
        file_path = os.path.join(path, filename)
        if os.path.exists(file_path):
            return file_path
    
    return None

def get_user_data_dir():
    """
    Get the user data directory.
    
    For portable mode, this will be a 'data' directory in the same location as the executable.
    For installed mode, this will be in the user's AppData directory.
    """
    # Check if we're in portable mode
    # Portable mode is determined by checking if we're running from a directory named "SinhalaWord_Portable"
    # or if there's a file named "portable.txt" in the same directory as the executable
    
    if getattr(sys, 'frozen', False):
        # We're running as a frozen executable
        exe_dir = os.path.dirname(sys.executable)
        logger.info(f"Executable directory: {exe_dir}")
        
        # Check if we're in a directory named SinhalaWord_Portable
        logger.info(f"Checking for portable mode: parent directory name is '{os.path.basename(exe_dir)}'")
        if os.path.basename(exe_dir) == "SinhalaWord_Portable":
            portable_mode = True
        else:
            # Check if there's a portable.txt file
            logger.info(f"Checking for portable.txt at: {os.path.join(exe_dir, 'portable.txt')}")
            portable_mode = os.path.exists(os.path.join(exe_dir, "portable.txt"))
            logger.info(f"portable.txt found: {portable_mode}")
            
        if portable_mode:
            # We're in portable mode, use a 'data' directory in the same location as the executable
            user_data_dir = os.path.join(exe_dir, "data")
            logger.info(f"Running in portable mode, using data directory: {user_data_dir}")
        else:
            # We're in installed mode, use the user's AppData directory
            user_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'SinhalaWord')
            logger.info(f"Running in installed mode, using data directory: {user_data_dir}")
    else:
        # We're running from source, check if there's a portable.txt file in the current directory
        logger.info(f"Running from source. Checking for portable.txt in current working directory: {os.path.join(os.getcwd(), 'portable.txt')}")
        if os.path.exists(os.path.join(os.getcwd(), "portable.txt")):
            # We're in portable mode, use a 'data' directory in the current directory
            user_data_dir = os.path.join(os.getcwd(), "data")
            logger.info(f"Running in portable mode from source, using data directory: {user_data_dir}")
        else:
            # We're in installed mode, use the user's AppData directory
            user_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'SinhalaWord')
            logger.info(f"Running in installed mode from source, using data directory: {user_data_dir}")
        logger.info(f"Source mode: portable.txt found in CWD: {os.path.exists(os.path.join(os.getcwd(), 'portable.txt'))}")
    
    # Ensure the directory exists
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

# Fallback paths for resources
def get_lexicon_dir():
    """Get the lexicon directory, with fallbacks for different locations."""
    # First try the standard location
    if os.path.exists(LEXICON_DIR):
        return LEXICON_DIR
    
    # Try in the executable's directory
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        exe_lexicon_dir = os.path.join(exe_dir, "resources", "dictionary", "chunks")
        if os.path.exists(exe_lexicon_dir):
            return exe_lexicon_dir
    
    # Try in the current working directory
    cwd_lexicon_dir = os.path.join(os.getcwd(), "resources", "dictionary", "chunks")
    if os.path.exists(cwd_lexicon_dir):
        return cwd_lexicon_dir
    
    # Return the original path even if it doesn't exist
    return LEXICON_DIR

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
        # Try to create the directory again and retry
        try:
            directory = os.path.dirname(USER_CONFIG_FILE)
            logger.info(f"Attempting to create directory again: {directory}")
            os.makedirs(directory, exist_ok=True)
            
            with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=4)
            logger.info(f"Successfully saved user preferences on second attempt to {USER_CONFIG_FILE}")
        except IOError as e2:
            logger.error(f"Error saving user preferences on second attempt: {e2}")

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
