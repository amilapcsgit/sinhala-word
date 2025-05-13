"""
Font Manager for Sinhala Word Processor

This module provides centralized font management for the application,
handling font loading, discovery, and providing access to available fonts.
"""
import os
import logging
from PySide6.QtGui import QFont, QFontDatabase

# Set up logging
logger = logging.getLogger("FontManager")

class FontManager:
    """
    Centralized font management for the Sinhala Word Processor.
    
    This class handles:
    - Loading fonts from the application's font directory
    - Discovering system Sinhala fonts
    - Providing access to available fonts
    - Managing font preferences
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of FontManager exists."""
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the font manager."""
        # Only initialize once
        if self._initialized:
            return
            
        self._initialized = True
        
        # Font directories
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.fonts_dir = os.path.join(self.app_dir, "resources", "fonts")
        self.alt_fonts_dir = os.path.join(self.app_dir, "fonts")
        
        # Font collections
        self.loaded_fonts = []  # Fonts loaded from application
        self.system_sinhala_fonts = []  # Sinhala fonts available on the system
        self.all_sinhala_fonts = []  # Combined list of all available Sinhala fonts
        
        # Default font preferences
        self.default_font = "UN-Ganganee"
        self.fallback_fonts = ["Iskoola Pota", "Nirmala UI", "Arial"]
        
        # Current font selections
        self.current_font = None
        self.current_font_size = 14
        self.current_keyboard_font_size = 26
        
        # Font size constants
        self.MIN_FONT_SIZE = 8
        self.MAX_FONT_SIZE = 72
        self.MIN_KB_FONT = 26
        self.MAX_KB_FONT = 200
        self.BASE_KB_HEIGHT = 264
        self.BASE_KB_FONT = 26
        
        # Available font sizes
        self.font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        
        # Load fonts
        self.load_fonts()
    
    def load_fonts(self):
        """Load all available Sinhala fonts."""
        self.loaded_fonts = []
        
        # First try the primary fonts directory
        if os.path.exists(self.fonts_dir):
            self._load_fonts_from_directory(self.fonts_dir)
        # If primary directory doesn't exist or has no fonts, try alternate
        elif len(self.loaded_fonts) == 0 and os.path.exists(self.alt_fonts_dir):
            self._load_fonts_from_directory(self.alt_fonts_dir)
        
        # Discover system Sinhala fonts
        self._discover_system_fonts()
        
        # Combine all fonts
        self.all_sinhala_fonts = list(set(self.loaded_fonts + self.system_sinhala_fonts))
        
        # Set current font to the best available option
        self._set_best_font()
        
        logger.info(f"Loaded {len(self.loaded_fonts)} application fonts and {len(self.system_sinhala_fonts)} system fonts")
        logger.info(f"Using font: {self.current_font}")
    
    def _load_fonts_from_directory(self, directory):
        """Load fonts from the specified directory."""
        logger.info(f"Loading fonts from: {directory}")
        
        try:
            for font_file in os.listdir(directory):
                if font_file.lower().endswith(('.ttf', '.otf')):
                    font_path = os.path.join(directory, font_file)
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    
                    if font_id != -1:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        if families:
                            for family in families:
                                self.loaded_fonts.append(family)
                                logger.info(f"Loaded font: {family} from {font_file}")
                    else:
                        logger.error(f"Failed to load font: {font_file}")
        except Exception as e:
            logger.error(f"Error loading fonts from {directory}: {e}")
    
    def _discover_system_fonts(self):
        """Discover Sinhala fonts available on the system."""
        self.system_sinhala_fonts = []
        
        # Known Sinhala fonts that might be available on the system
        known_sinhala_fonts = [
            "Iskoola Pota", "Nirmala UI", "Dinamika", "Malithi Web",
            "Sinhala Sangam MN", "Sinhala MN", "Sinhala Sangam"
        ]
        
        # Check for known Sinhala fonts
        for font_name in known_sinhala_fonts:
            if QFontDatabase.hasFamily(font_name):
                self.system_sinhala_fonts.append(font_name)
                logger.info(f"Found system Sinhala font: {font_name}")
        
        # Look for other fonts with "Sinhala" in the name
        all_fonts = QFontDatabase.families()
        for font_name in all_fonts:
            if ("sinhala" in font_name.lower() or "iskoola" in font_name.lower()) and font_name not in self.system_sinhala_fonts:
                self.system_sinhala_fonts.append(font_name)
                logger.info(f"Found additional system Sinhala font: {font_name}")
    
    def _set_best_font(self):
        """Set the current font to the best available option."""
        # First try the default font
        if self.default_font in self.all_sinhala_fonts:
            self.current_font = self.default_font
            return
        
        # Then try the fallback fonts in order
        for font in self.fallback_fonts:
            if font in self.all_sinhala_fonts:
                self.current_font = font
                return
        
        # If no preferred fonts are available, use the first available font
        if self.all_sinhala_fonts:
            self.current_font = self.all_sinhala_fonts[0]
        else:
            # Last resort - use a system font that should be available everywhere
            self.current_font = "Arial"
            logger.warning("No Sinhala fonts found, using Arial as fallback")
    
    def get_font(self, size=None, strategy=QFont.StyleStrategy.PreferMatch):
        """
        Get a QFont object with the current font family.
        
        Args:
            size (int, optional): Font size. If None, uses current_font_size.
            strategy (QFont.StyleStrategy, optional): Font style strategy.
            
        Returns:
            QFont: A QFont object with the specified properties.
        """
        if size is None:
            size = self.current_font_size
            
        font = QFont(self.current_font, size)
        font.setStyleStrategy(strategy)
        return font
    
    def get_keyboard_font(self, size=None, strategy=QFont.StyleStrategy.PreferMatch):
        """
        Get a QFont object for the keyboard with the current font family.
        
        Args:
            size (int, optional): Font size. If None, uses current_keyboard_font_size.
            strategy (QFont.StyleStrategy, optional): Font style strategy.
            
        Returns:
            QFont: A QFont object with the specified properties.
        """
        if size is None:
            size = self.current_keyboard_font_size
            
        # Ensure size is within valid range for keyboard
        size = max(self.MIN_KB_FONT, min(self.MAX_KB_FONT, size))
            
        font = QFont(self.current_font, size)
        font.setStyleStrategy(strategy)
        return font
    
    def set_font(self, font_name):
        """
        Set the current font.
        
        Args:
            font_name (str): Name of the font to use.
            
        Returns:
            bool: True if the font was set successfully, False otherwise.
        """
        if font_name in self.all_sinhala_fonts or QFontDatabase.hasFamily(font_name):
            self.current_font = font_name
            logger.info(f"Font set to: {font_name}")
            return True
        else:
            logger.warning(f"Font {font_name} not available, keeping {self.current_font}")
            return False
    
    def set_font_size(self, size):
        """
        Set the current font size.
        
        Args:
            size (int): Font size to use.
            
        Returns:
            int: The actual font size set (may be clamped to valid range).
        """
        # Ensure size is within valid range
        size = max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, size))
        self.current_font_size = size
        logger.info(f"Font size set to: {size}")
        return size
    
    def set_keyboard_font_size(self, size):
        """
        Set the current keyboard font size.
        
        Args:
            size (int): Font size to use for the keyboard.
            
        Returns:
            int: The actual font size set (may be clamped to valid range).
        """
        # Ensure size is within valid range for keyboard
        size = max(self.MIN_KB_FONT, min(self.MAX_KB_FONT, size))
        self.current_keyboard_font_size = size
        logger.info(f"Keyboard font size set to: {size}")
        return size
    
    def calculate_keyboard_font_size(self, height):
        """
        Calculate the appropriate font size for a keyboard of the given height.
        
        Args:
            height (int): Height of the keyboard in pixels.
            
        Returns:
            int: The calculated font size.
        """
        # Calculate proportional font size based on height
        font_size = int(self.BASE_KB_FONT * (height / self.BASE_KB_HEIGHT))
        # Ensure it's within valid range
        font_size = max(self.MIN_KB_FONT, min(self.MAX_KB_FONT, font_size))
        return font_size
    
    def update_from_preferences(self, preferences):
        """
        Update font settings from user preferences.
        
        Args:
            preferences (dict): User preferences dictionary.
        """
        # Update font family if available
        font_name = preferences.get("font", self.default_font)
        self.set_font(font_name)
        
        # Update font sizes
        self.set_font_size(preferences.get("font_size", 14))
        self.set_keyboard_font_size(preferences.get("keyboard_font_size", 26))
        
        logger.info(f"Updated font settings from preferences: {font_name}, {self.current_font_size}, {self.current_keyboard_font_size}")
    
    def get_available_fonts(self):
        """
        Get a list of all available Sinhala fonts.
        
        Returns:
            list: List of available font family names.
        """
        return self.all_sinhala_fonts
    
    def get_available_font_sizes(self):
        """
        Get a list of available font sizes.
        
        Returns:
            list: List of available font sizes.
        """
        return self.font_sizes