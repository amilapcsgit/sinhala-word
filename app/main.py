# Sinhala Word Processor — PySide6 (v5.3 - Enhanced)
"""
A lightweight **Word‑2000‑style** editor refreshed with Windows‑11 Fluent UI:

• **Realtime Singlish → Sinhala** (Buffer-based input like Sintip)
• **Suggestion popup** (up to 9 matches, Tab/1-9/Click to accept)
• **Basic spell‑checker** — unknown Sinhala words are underlined red
• **Two classic toolbars** (Standard & Formatting) ‑or‑ hide them and use the menu
• **Dark / Light theme toggle** (View → Toggle Theme) - Enhanced implementation
• Plain‑text load/save functionality.

Install dependencies:
```bash
pip install PySide6 PySide6-Fluent-Widgets
```

Run:
```bash
python SinhalaWordProcessor_simple.py
```

Pack as EXE:
```bash
pyinstaller --noconfirm --onefile --add-data "sinhalawordmap.json;." --add-data "dictionary;dictionary" SinhalaWordProcessor_simple.py
```
"""
import sys
import os
import json
import re
import gzip
import logging

# Allow limited font fallbacks for better compatibility
# We'll handle font fallbacks more carefully in the code
os.environ["QT_ENABLE_FONT_FALLBACKS"] = "1"
os.environ["QT_FONT_NO_SYSTEM_FALLBACKS"] = "0"
from PySide6.QtWidgets import (
    QApplication, QTextEdit, QFileDialog, QToolBar, QWidget, QVBoxLayout,
    QFontComboBox, QComboBox, QMessageBox, QStatusBar, QLabel, 
    QFrame, QInputDialog, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy,
    QStyledItemDelegate, QMenu
)
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QAction, QIcon, QFontDatabase
from PySide6.QtCore import Qt, QPoint, QTimer, QEvent, Slot, QSize, QObject

# Import our custom modules
from ui.keyboard import SinhalaKeyboard
from ui.theme_manager import ThemeManager
from app import config
from app.transliterator import SinhalaTransliterator
from app.spellchecker import SinhalaSpellChecker
from app.input_handler import SinhalaInputHandler
from ui.suggestion_popup import SuggestionPopup
from ui.settings_dialog import SettingsDialog
from ui.icons import get_toolbar_icon

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SinhalaWordProcessor")

# ------------------------------------------------------------------
#  Constants & Global Helpers
# ------------------------------------------------------------------
WORD_PATTERN = re.compile(r'\b\w+\b')  # Compiled regex for word counting

# Custom delegate for better rendering of font sizes in dropdown
class FontSizeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        # Simply use the default painting with centered alignment
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)

# Path to the fonts directory - use absolute path to ensure it works correctly
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "fonts")

def configure_font_fallbacks():
    """Configure font fallbacks for better compatibility."""
    try:
        # Allow limited font fallbacks for better compatibility
        # This helps with rendering Sinhala characters properly
        os.environ["QT_ENABLE_FONT_FALLBACKS"] = "1"
        os.environ["QT_FONT_NO_SYSTEM_FALLBACKS"] = "0"
        logging.info("Configured font fallbacks for better compatibility")
    except Exception as e:
        logging.error(f"Failed to configure font fallbacks: {e}")

def load_sinhala_fonts():
    """Load Sinhala fonts from the fonts directory."""
    global FONTS_DIR
    font_families = []

    # Check if fonts directory exists
    if not os.path.exists(FONTS_DIR):
        logging.warning(f"Fonts directory not found at {FONTS_DIR}")
        # Try alternate path
        alt_fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
        if os.path.exists(alt_fonts_dir):
            logging.info(f"Using alternate fonts directory: {alt_fonts_dir}")
            FONTS_DIR = alt_fonts_dir

    # Load fonts from directory
    if os.path.exists(FONTS_DIR):
        logging.info(f"Loading fonts from: {FONTS_DIR}")
        for font_file in os.listdir(FONTS_DIR):
            if font_file.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(FONTS_DIR, font_file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    family = QFontDatabase.applicationFontFamilies(font_id)
                    if family:
                        font_families.append(family[0])
                        logging.info(f"Loaded font: {family[0]} from {font_file}")
                else:
                    logging.error(f"Failed to load font: {font_file}")
    else:
        logging.error(f"Fonts directory not found: {FONTS_DIR}")

    # Check for system Sinhala fonts as fallbacks
    system_sinhala_fonts = ["Iskoola Pota", "Nirmala UI"]
    for font_name in system_sinhala_fonts:
        if QFontDatabase.hasFamily(font_name) and font_name not in font_families:
            font_families.append(font_name)
            logging.info(f"Found system Sinhala font: {font_name}")

    # If no fonts were found, add a default system font
    if not font_families:
        font_families.append("Arial")
        logging.warning("No Sinhala fonts found, using Arial as fallback")

    return font_families





# Phonetic fallback definitions
VOW = {"aa":"ා","a":"","ae":"ැ","aae":"ෑ","i":"ි","ii":"ී","u":"ු","uu":"ූ",
       "ru":"ෘ","ruu":"ෲ","e":"ෙ","ee":"ේ","o":"ො","oo":"ෝ","au":"ෞ","":""}
CONS = {"kh":"ඛ","gh":"ඝ","chh":"ඡ","jh":"ඣ","th":"ඨ","dh":"ඪ","ph":"ඵ","bh":"භ",
        "sh":"ශ","ss":"ෂ","ng":"ඟ","ny":"ඤ","t":"ට","d":"ඩ","n":"ණ","p":"ප","b":"බ",
        "m":"ම","k":"ක","g":"ග","c":"ච","j":"ජ","l":"ල","w":"ව","y":"ය","r":"ර",
        "s":"ස","h":"හ","f":"ෆ","lh":"ළ","":""}
_RE_CON = re.compile("|".join(sorted(CONS, key=len, reverse=True)))
VOW_INIT = {"a":"අ","aa":"ආ","ae":"ඇ","aae":"ඈ","i":"ඉ","ii":"ඊ","u":"උ","uu":"ඌ",
            "e":"එ","ee":"ඒ","o":"ඔ","oo":"ඕ","au":"ඖ"}

def _phonetic_global(word: str) -> str:
    """Global phonetic fallback function."""
    t, out = word.lower(), ""
    while t:
        match = _RE_CON.match(t)
        c = match.group(0) if match else ""
        t = t[len(c):]
        v = next((vv for vv in sorted(VOW, key=len, reverse=True) if t.startswith(vv)), "")
        t = t[len(v):]
        if c:
            out += CONS[c] + VOW[v]
        else:
            out += VOW_INIT.get(v, v)
    return out or word

# ------------------------------------------------------------------
#  Main window class
# ------------------------------------------------------------------
from enum import Enum

# Constants for font size limits - must match keyboard.py
MIN_KB_FONT = 10  # Minimum keyboard font size
MAX_KB_FONT = 200  # Maximum keyboard font size

class ResizeState(Enum):
    IDLE = 0
    USER = 1  # mouse/drag
    PROGRAMMATIC = 2

class SinhalaWordApp(QMainWindow):
    """
    SinhalaWordApp: Main application class for the Sinhala Word Processor.

    Features:
    - Realtime Singlish to Sinhala transliteration.
    - Suggestion popup (up to 9 matches, Tab/1-9/Click to accept)
    - Basic spell‑checker — unknown Sinhala words are underlined red
    - Two classic toolbars (Standard & Formatting) ‑or‑ hide them and use the menu
    - Dark / Light theme toggle (View → Toggle Theme) - Enhanced implementation
    - Plain‑text load/save functionality.
    """
    # Centralized resize state
    _kb_resize_state = ResizeState.IDLE
    def __init__(self):
        # --- Load User Preferences ---
        self.preferences = config.load_user_preferences()

        # --- Load Sinhala Fonts ---
        self.sinhala_font_families = load_sinhala_fonts()
        font_size = self.preferences["font_size"]
        
        # Prioritize fonts in this order: UN-Ganganee, Iskoola Pota, other loaded fonts
        preferred_fonts = ["UN-Ganganee", "Iskoola Pota", "Nirmala UI"]
        
        # First try to use the preferred font from user preferences
        preferred_font = self.preferences["font"]
        font_name = None
        
        # Check if preferred font is available
        if preferred_font in self.sinhala_font_families:
            font_name = preferred_font
            logging.info(f"Using preferred Sinhala font: {font_name}")
        else:
            # Try each font in our priority list
            for priority_font in preferred_fonts:
                if priority_font in self.sinhala_font_families:
                    font_name = priority_font
                    logging.info(f"Using priority Sinhala font: {font_name}")
                    # Update preferences
                    self.preferences["font"] = font_name
                    break
            
            # If none of the priority fonts are available, use the first available font
            if not font_name and self.sinhala_font_families:
                font_name = self.sinhala_font_families[0]
                logging.info(f"Using available Sinhala font: {font_name}")
                # Update preferences
                self.preferences["font"] = font_name
        
        # If still no font found, use a system font that should be available
        if not font_name:
            font_name = "Arial"
            logging.warning(f"No Sinhala fonts loaded, using system font: {font_name}")
            self.preferences["font"] = font_name
        
        # Create the font with a strategy that allows better fallback
        self.base_font = QFont(font_name, font_size)
        # Use PreferMatch instead of NoFontMerging for better compatibility
        self.base_font.setStyleHint(QFont.StyleHint.AnyStyle, QFont.StyleStrategy.PreferMatch)
        
        # Apply to editor
        
        # --- Initialize Core Attributes FIRST ---
        self.MAIN_LEXICON = {}
        self.USER_MAP = {}
        self.MAP = {}
        self.USER_MAP_FP = config.USER_DICT_FILE
        self.SAVE_PENDING = False

        # --- Suggestion State ---
        self.buffer = []
        self.word_start_pos = None # Position in the document where the current word started
        self.current_suggestions = [] # Store current suggestions for fixed area
        
        # Initialize suggestion timer
        self._suggestion_timer = QTimer()
        self._suggestion_timer.setSingleShot(True)
        self._suggestion_timer.timeout.connect(self.update_suggestion_area)

        # --- Theme Manager ---
        self.theme_manager = ThemeManager()
        # Set theme from preferences
        if self.preferences["theme"] == "dark":
            self.theme_manager.current_theme = "dark"

        # --- Create Core Widgets ---
        self.editor = QTextEdit()
        self.base_font = QFont(
            self.preferences["font"], 
            self.preferences["font_size"]
        )
        self.editor.setFont(self.base_font)

        # --- Call Superclass Initializer ---
        super().__init__()

        # --- Suggestion Popup (Near Cursor) ---
        # Create a popup widget for suggestions
        self.suggestion_popup = SuggestionPopup(self)
        self.suggestion_popup.suggestionSelected.connect(self.accept_suggestion)
        
        # Hide the popup initially
        self.suggestion_popup.hide()
        
        # Log that we've created the suggestion area
        logger.info("Created suggestion label")

        # --- Basic Window Setup ---
        self.setWindowTitle("Sinhala Word Processor")
        self.resize(1100, 780)

        # --- Status Bar for QMainWindow ---
        self.status = self.statusBar()
        self.lineCol = QLabel("Ln 1, Col 1")
        self.wordCount = QLabel("Words: 0")
        self.themeLbl = QLabel("☀️ Light" if self.theme_manager.current_theme == "light" else "🌙 Dark")
        self.status.addPermanentWidget(self.lineCol)
        self.status.addPermanentWidget(self.wordCount)
        self.status.addPermanentWidget(self.themeLbl)

        # --- Load Dictionaries ---
        self._load_dictionaries() # Call load method

        # --- Initialize Transliterator and Spellchecker ---
        self.transliterator = SinhalaTransliterator(self.MAP)
        self.spellchecker = SinhalaSpellChecker(self.MAP)

        # --- Initialize Actions ---
        self.build_shortcuts()  # Initialize shortcuts and actions

        # --- Create Toggle Actions ---
        # These need to be created before building menus and toolbars
        self.singlish_toggle_action = QAction("Singlish: On" if self.preferences["singlish_enabled"] else "Singlish: Off", self, checkable=True)
        self.singlish_toggle_action.setChecked(self.preferences["singlish_enabled"]) 
        self.singlish_toggle_action.triggered.connect(self.toggle_singlish)

        self.suggestions_toggle_action = QAction("Suggestions: On" if self.preferences["show_suggestions"] else "Suggestions: Off", self, checkable=True)
        self.suggestions_toggle_action.setChecked(self.preferences["show_suggestions"]) 
        self.suggestions_toggle_action.triggered.connect(self.toggle_suggestions)

        self.keyboard_toggle_action = QAction("Sinhala Keyboard", self, checkable=True)
        self.keyboard_toggle_action.setChecked(self.preferences["show_keyboard"]) 
        self.keyboard_toggle_action.triggered.connect(self.toggle_keyboard)
        self.keyboard_toggle_action.setIcon(self.create_icon("keyboard"))
        self.keyboard_toggle_action.setProperty("icon_name", "keyboard")

        # --- On-screen Keyboard Area ---
        # Create the Sinhala keyboard using our custom implementation with dark mode support
        # Initialize with dark mode based on current theme and default font size
        is_dark_mode = self.theme_manager.is_dark_mode()
        
        # Use a larger default font size for better visibility
        keyboard_font_size = self.preferences.get("keyboard_font_size", 60)  # Default to 60 if not set
        
        # Create the keyboard with the current theme and font size
        # First, ensure we have a valid font size
        if keyboard_font_size <= 0 or keyboard_font_size > 200:
            keyboard_font_size = 60  # Reset to default if invalid
            self.preferences["keyboard_font_size"] = keyboard_font_size  # Update preferences
            logging.warning(f"Invalid keyboard font size detected, reset to {keyboard_font_size}")

        # Create the Sinhala keyboard instance
        try:
            # Create the keyboard directly with the parent
            self.keyboard_area = SinhalaKeyboard(parent=self, dark_mode=is_dark_mode, font_size=keyboard_font_size)

            # Connect the key press signal
            self.keyboard_area.keyPressed.connect(self.on_keyboard_button_clicked)

            # Calculate appropriate height based on font size
            base_height = 600  # Increased base height for better visibility
            base_font_size = 60  # Increased base font size
            calculated_height = max(400, int((keyboard_font_size / base_font_size) * base_height))
            
            # Ensure the keyboard has a reasonable size before we start
            # Use the calculated height based on font size, with a minimum of 400px
            self.keyboard_area.resize(self.width(), calculated_height)
            
            # Store the calculated height in preferences
            self.preferences["keyboard_height"] = calculated_height
            
            # Force an update of the buttons after initialization
            if hasattr(self.keyboard_area, 'update_buttons'):
                # Give the layout a chance to initialize first
                QTimer.singleShot(100, self.keyboard_area.update_buttons)
                
            # Log successful keyboard creation
            logging.info(f"Created Sinhala keyboard with font size: {keyboard_font_size}")

        except Exception as e:
            logging.error(f"Error creating Sinhala keyboard: {e}")
            # Create an empty widget as a fallback
            self.keyboard_area = QWidget(self)
            self.keyboard_area.setFixedHeight(100)  # Small fixed height
            logging.warning("Created empty widget as keyboard placeholder due to error")

        # Apply initial theme - ensure consistent application
        self.apply_theme_to_all_widgets()
        
        # Update combo box styles based on theme
        self.update_combo_box_styles()
        
        # Update icons for the current theme
        self.update_icons_for_theme(self.theme_manager.current_theme)

        # --- Finalize UI Setup ---
        # Create a central widget and layout to hold the editor and suggestion area
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Note: The suggestion popup is not added to the layout as it's a popup widget
        logger.info("Created suggestion popup widget")
        
        # Add editor with stretch factor to allow it to take most of the space
        main_layout.addWidget(self.editor, 3)  # Higher stretch factor for editor

        # Add keyboard area with responsive height
        self.keyboard_container = QWidget()
        
        # Get saved keyboard height from preferences or use default (20% larger than original)
        default_keyboard_height = 264  # 220 * 1.2 = 264
        
        # Log the current preferences
        logging.info(f"Keyboard preferences: height={self.preferences.get('keyboard_height', 'not set')}, "
                    f"font_size={self.preferences.get('keyboard_font_size', 'not set')}")
        
        # Get saved height but limit it to a reasonable value (25% of screen height - reduced from 30%)
        screen = self.screen()
        if screen:
            screen_height = screen.availableGeometry().height()
            screen_width = screen.availableGeometry().width()
            logging.info(f"Screen dimensions: {screen_width}x{screen_height}")
            
            # More conservative height limit (25% of screen)
            max_keyboard_height = int(screen_height * 0.25)
            
            # Get saved height with validation
            saved_height = self.preferences.get("keyboard_height", default_keyboard_height)
            
            # Validate saved height (must be positive and reasonable)
            if saved_height <= 0 or saved_height > screen_height:
                logging.warning(f"Invalid saved keyboard height: {saved_height}, using default")
                saved_height = default_keyboard_height
                
            # Apply the limit
            keyboard_height = min(saved_height, max_keyboard_height)
            logging.info(f"Using keyboard height: {keyboard_height} (saved: {saved_height}, max: {max_keyboard_height})")
        else:
            keyboard_height = self.preferences.get("keyboard_height", default_keyboard_height)
            logging.info(f"No screen info available, using keyboard height: {keyboard_height}")
        
        # Set a smaller minimum height to allow more flexibility
        self.keyboard_container.setMinimumHeight(80)
        
        # Create a splitter handle effect by adding a frame at the top of the keyboard container
        splitter_handle = QFrame(self.keyboard_container)
        splitter_handle.setFrameShape(QFrame.HLine)
        splitter_handle.setFrameShadow(QFrame.Sunken)
        splitter_handle.setFixedHeight(8)  # Make it a bit taller for easier grabbing
        splitter_handle.setStyleSheet("""
            QFrame {
                background-color: #cccccc;
                border: 1px solid #aaaaaa;
                border-radius: 2px;
            }
            QFrame:hover {
                background-color: #bbbbbb;
                border: 1px solid #999999;
            }
        """)
        
        # Set cursor to indicate resizing is possible
        splitter_handle.setCursor(Qt.SizeVerCursor)
        
        # Create a custom resize handle class to handle mouse events
        class ResizeHandle(QFrame):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setMouseTracking(True)
                self.dragging = False
                self.drag_start_y = 0
                self.drag_start_height = 0
                self.setCursor(Qt.SizeVerCursor)
                self.setMinimumHeight(8)  # Make handle easier to grab
                self.setMaximumHeight(8)  # Keep it small but visible
                
                # Set a background color to make it more visible
                self.setStyleSheet("background-color: rgba(128, 128, 128, 0.5);")
                
            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    self.dragging = True
                    self.drag_start_y = event.globalY()
                    self.drag_start_height = self.parent().height()
                    event.accept()
                else:
                    super().mousePressEvent(event)
                    
            def mouseMoveEvent(self, event):
                if self.dragging:
                    # Find the main window
                    app = QApplication.instance()
                    main_window = None
                    for widget in app.topLevelWidgets():
                        if isinstance(widget, SinhalaWordApp):
                            main_window = widget
                            break
                    
                    if not main_window:
                        super().mouseMoveEvent(event)
                        return
                    
                    # Set the manual resize flag in the main window
                    if hasattr(main_window, '_manual_resize'):
                        main_window._manual_resize = True
                        
                    # Calculate new height
                    delta_y = event.globalY() - self.drag_start_y
                    new_height = max(80, self.drag_start_height - delta_y)
                    
                    # Resize the container directly
                    self.parent().resize(self.parent().width(), new_height)
                    
                    # Update the keyboard area
                    keyboard_area = self.parent().findChild(SinhalaKeyboard)
                    if keyboard_area:
                        # Calculate keyboard height (container height minus margins and handle)
                        keyboard_height = new_height - 10
                        keyboard_area.resize(keyboard_area.width(), keyboard_height)
                        
                        # Update the buttons to match the new size
                        if hasattr(keyboard_area, 'update_buttons'):
                            keyboard_area.update_buttons()
                    
                    # Update the main window's preferences directly
                    if main_window:
                        # Save the current height in preferences
                        main_window.preferences["keyboard_height"] = keyboard_height
                        
                        # Force layout update to apply changes
                        main_window.updateGeometry()
                        
                        # Log the resize for debugging
                        logging.debug(f"Manual resize in progress: Container height={new_height}, Keyboard height={keyboard_height}")
                    
                    event.accept()
                else:
                    super().mouseMoveEvent(event)
                    
            def mouseReleaseEvent(self, event):
                if event.button() == Qt.LeftButton and self.dragging:
                    self.dragging = False
                    
                    # Find the main window
                    app = QApplication.instance()
                    main_window = None
                    for widget in app.topLevelWidgets():
                        if isinstance(widget, SinhalaWordApp):
                            main_window = widget
                            break
                            
                    if main_window:
                        # Get the keyboard area
                        keyboard_area = self.parent().findChild(SinhalaKeyboard)
                        if keyboard_area:
                            # Get the current container height
                            container_height = self.parent().height()
                            
                            # Make sure the container height is reasonable (at least 80px)
                            if container_height < 80:
                                container_height = 80
                                self.parent().resize(self.parent().width(), container_height)
                            
                            # Calculate keyboard height (container height minus margins and handle)
                            keyboard_height = container_height - 10
                            
                            # Save the final height in preferences
                            main_window.preferences["keyboard_height"] = keyboard_height
                            
                            # Set a permanent flag to prevent automatic resizing
                            main_window._manual_resize = True
                            
                            # The key insight: Use the same approach as the settings dialog
                            # Calculate a new font size based on the keyboard height
                            # This is the key to making the resize stick
                            current_font_size = main_window.preferences.get("keyboard_font_size", 26)
                            
                            # Calculate a new font size proportional to the height change
                            # Base calculation: default height 264px corresponds to font size 26
                            # So for every 10px of height, we change font size by about 1
                            base_height = 264
                            base_font_size = 26
                            
                            # Calculate new font size proportional to height and round to nearest integer
                            new_font_size = max(20, min(200, round(base_font_size * keyboard_height / base_height)))
                            
                            # Only update if the integer value has changed
                            if new_font_size != int(current_font_size):
                                # Use the set_keyboard_font_size method which properly updates everything
                                if hasattr(main_window, 'set_keyboard_font_size'):
                                    main_window.set_keyboard_font_size(new_font_size)
                                    logging.info(f"Updated keyboard font size to {new_font_size} based on height {keyboard_height}")
                            else:
                                # If we're not changing the font size, we still need to update the height
                                # Ensure the keyboard has the correct height
                                keyboard_area.resize(keyboard_area.width(), keyboard_height)
                                
                                # Update the buttons to match the new size
                                if hasattr(keyboard_area, 'update_buttons'):
                                    keyboard_area.update_buttons()
                                
                                # Save preferences immediately to disk
                                from app import config
                                config.save_user_preferences(main_window.preferences)
                            
                            # Log the resize for debugging
                            logging.info(f"Manual resize COMPLETED: Container height={container_height}, Keyboard height={keyboard_height}")
                        
                    event.accept()
                else:
                    super().mouseReleaseEvent(event)
        
        # Replace the simple frame with our custom resize handle
        splitter_handle = ResizeHandle(self.keyboard_container)
        
        # Set size policy to allow the container to grow and shrink
        # Use Preferred for vertical to allow manual resizing
        self.keyboard_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Make sure the container can be resized
        self.keyboard_container.setMinimumHeight(80)  # Smaller minimum height for flexibility
        self.keyboard_container.setMaximumHeight(16777215)  # Maximum possible height (QWIDGETSIZE_MAX)
        
        # Create layout for keyboard container
        keyboard_layout = QVBoxLayout(self.keyboard_container)
        keyboard_layout.setContentsMargins(2, 2, 2, 2)
        keyboard_layout.setSpacing(2)
        
        # Add a control bar with buttons
        control_bar = QHBoxLayout()
        
        # Add a button to detach the keyboard
        detach_btn = QPushButton("Detach Keyboard")
        detach_btn.setToolTip("Make the keyboard a floating window")
        detach_btn.clicked.connect(self.detach_keyboard)
        control_bar.addWidget(detach_btn)
        
        # Add a button to reset keyboard size
        reset_btn = QPushButton("Reset Size")
        reset_btn.setToolTip("Reset keyboard to default size")
        reset_btn.clicked.connect(self.reset_keyboard_size)
        control_bar.addWidget(reset_btn)
        
        # Add spacer to push buttons to the left
        control_bar.addStretch(1)
        
        # Add the control bar to the layout
        keyboard_layout.addLayout(control_bar)
        
        # Add the splitter handle to the layout
        keyboard_layout.addWidget(splitter_handle)
        
        # Set an object name for the keyboard container to make it easier to find
        self.keyboard_container.setObjectName("keyboard_container")
        
        # Add the keyboard to the container with stretch factor
        try:
            keyboard_layout.addWidget(self.keyboard_area, 1)  # Add with stretch factor of 1
        except Exception as e:
            logging.error(f"Error adding keyboard to layout: {e}")
            # Try to recover by recreating the keyboard area
            try:
                self.keyboard_area = QWidget(self)
                keyboard_layout.addWidget(self.keyboard_area, 1)  # Add with stretch factor of 1
            except:
                pass
        
        # Add the container to the main layout with stretch factor of 0
        # This prevents automatic stretching and allows manual resizing
        main_layout.addWidget(self.keyboard_container, 0)
        
        # Set initial size without restricting future resizing
        try:
            self.keyboard_container.resize(self.width(), keyboard_height + 10)
            self.keyboard_area.resize(self.width(), keyboard_height)
            
            # Ensure the keyboard area has the right size policy
            if hasattr(self.keyboard_area, 'setSizePolicy'):
                self.keyboard_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        except Exception as resize_error:
            logging.error(f"Error setting initial keyboard size: {resize_error}")
        
        # Connect keyboard resize signal if it's a SinhalaKeyboard
        if hasattr(self.keyboard_area, 'keyboardResized'):
            try:
                # Connect the signal
                self.keyboard_area.keyboardResized.connect(self.on_keyboard_resized)
            except Exception as e:
                logger.error(f"Error connecting keyboard resize signal: {e}")
        
        # Show/hide keyboard container based on preferences
        if self.preferences["show_keyboard"]:
            self.keyboard_container.show()
        else:
            self.keyboard_container.hide()

        # Configure layout properties
        main_layout.setContentsMargins(0, 0, 0, 0) # Remove margins
        main_layout.setSpacing(2)  # Reduce spacing between widgets
        
        # Set the layout's size constraints to allow manual resizing
        # SetNoConstraint allows widgets to be resized beyond their size hints
        main_layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)

        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Force layout update
        central_widget.updateGeometry()

        # Install event filter *after* editor exists and super().__init__ is done
        # Install event filter directly on the editor widget
        self.editor.installEventFilter(self)
        # Connect textChanged to update_status and update_suggestion_list
        self.editor.textChanged.connect(self.on_text_changed)
        # Connect cursor position change to update formatting buttons
        self.editor.cursorPositionChanged.connect(self.update_format_actions)
        # Add context menu support
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.show_context_menu)

        # --- Build Menus/Toolbars ---
        self.build_menu()
        self.build_toolbars()
        self.update_status() # Initial status

        # --- Set up spell checking timer ---
        self.spell_check_timer = QTimer(self)
        self.spell_check_timer.setSingleShot(True)
        self.spell_check_timer.timeout.connect(self.perform_spell_check)

        # --- Initialize Recent Files Menu ---
        self.recent_files_menu = None
        self.update_recent_files_menu()

    def show_context_menu(self, position):
        """Show right-click context menu."""
        menu = self.editor.createStandardContextMenu()

        # Add separator and custom actions
        menu.addSeparator()

        # Add "Learn Selected Word" action
        learn_action = QAction("Learn Selected Word", self)
        learn_action.triggered.connect(self.learn_selected_word)
        menu.addAction(learn_action)

        # Get selected text
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()

            # Check if the selected text contains Sinhala characters
            is_sinhala = any("\u0D80" <= c <= "\u0DFF" for c in selected_text)

            if is_sinhala and not self.spellchecker.is_known_word(selected_text):
                # Add spell check suggestions if available
                suggestions = self.spellchecker.suggest_corrections(selected_text)
                if suggestions:
                    suggestion_menu = menu.addMenu("Spelling Suggestions")
                    for suggestion in suggestions:
                        action = QAction(suggestion, self)
                        action.triggered.connect(lambda checked, word=suggestion: self.replace_selected_text(word))
                        suggestion_menu.addAction(action)

        # Show the menu at the cursor position
        menu.exec_(self.editor.mapToGlobal(position))

    def replace_selected_text(self, replacement):
        """Replace selected text with the given replacement."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(replacement)
            cursor.endEditBlock()

    def learn_selected_word(self):
        """Learn selected Sinhala word and add to user dictionary."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()

            # Check if the selected text contains Sinhala characters
            is_sinhala = any("\u0D80" <= c <= "\u0DFF" for c in selected_text)

            if is_sinhala:
                # Ask for Singlish equivalent
                singlish, ok = QInputDialog.getText(
                    self, 
                    "Add to Dictionary", 
                    f"Enter Singlish for: {selected_text}"
                )

                if ok and singlish:
                    # Add to user dictionary
                    self.USER_MAP[singlish.lower()] = selected_text
                    # Update combined map
                    self.MAP[singlish.lower()] = selected_text
                    # Update transliterator and spellchecker
                    self.transliterator = SinhalaTransliterator(self.MAP)
                    self.spellchecker = SinhalaSpellChecker(self.MAP)
                    # Mark for saving
                    self.SAVE_PENDING = True
                    # Save immediately
                    self._save_map()
                    QMessageBox.information(self, "Success", "Word added to dictionary")
                    # Trigger spell check to remove any red underlines
                    self.perform_spell_check()
            else:
                QMessageBox.warning(self, "Warning", "Please select a Sinhala word")
        else:
            QMessageBox.warning(self, "Warning", "Please select a word first")

    # Removed on_suggestion_link_clicked method
    # as it is no longer needed with the new SuggestionPopup implementation
    # The SuggestionPopup class handles clicks internally and emits a signal
    
    def on_keyboard_button_clicked(self, char):
        """Handles clicks on the on-screen keyboard buttons."""
        try:
            # Simplified implementation matching SinhalaWordProcessor_enhanced.py
            if char == "Space":
                # Insert space and let the eventFilter handle the buffer and suggestions
                self.editor.insertPlainText(" ")
            elif char == "Backspace":
                # Let the editor handle the backspace
                self.editor.textCursor().deletePreviousChar()
            else:
                # For any other character, just insert it into the editor
                # The eventFilter will handle the buffer and suggestions
                self.editor.insertPlainText(char)
                
            # Log successful keyboard input
            logger.debug(f"Keyboard input: '{char}'")
        except Exception as e:
            logger.error(f"Error in on_keyboard_button_clicked for char '{char}': {e}")
            # Try a more direct approach on error
            try:
                # Try to insert the character directly
                if char != "Backspace" and char != "Space":
                    self.editor.insertPlainText(char)
                elif char == "Space":
                    self.editor.insertPlainText(" ")
            except Exception as inner_e:
                logger.error(f"Failed fallback insertion: {inner_e}")
            
            # Clear state on error
            self.reset_input_state()
            
    # Timer for debouncing keyboard resize events
    _keyboard_resize_timer = None
    _pending_keyboard_height = None
    _manual_resize = False  # Flag to indicate manual resizing
    _in_resize = False  # Flag to prevent resize loops
    _last_keyboard_height = None  # Store last height for comparison

    def on_keyboard_resized(self, new_height):
        """Handle keyboard resize events to update the container height (debounced)."""
        try:
            # Check if we're in a manual resize - if so, skip automatic resizing
            if hasattr(self, '_manual_resize') and self._manual_resize:
                logger.debug(f"Ignoring keyboard resize signal during manual resize: {new_height}")
                return
                
            # Validate the height
            if new_height <= 0:
                logger.warning(f"Ignoring invalid keyboard height: {new_height}")
                return
                
            # Store the pending height
            self._pending_keyboard_height = new_height

            # Initialize timer if it doesn't exist
            if self._keyboard_resize_timer is None:
                self._keyboard_resize_timer = QTimer(self)
                self._keyboard_resize_timer.setSingleShot(True)
                self._keyboard_resize_timer.timeout.connect(self._process_keyboard_resize)

            # Restart the timer with a short delay (e.g., 50ms)
            self._keyboard_resize_timer.start(50)

            logger.debug(f"Keyboard resize signal received, pending height: {new_height}")

        except Exception as e:
            logger.error(f"Error in on_keyboard_resized: {e}")

    # Track resize loop detection
    _resize_count = 0
    _last_resize_time = 0
    
    @Slot()
    def request_keyboard_resize(self, new_height):
        """Request a keyboard resize to the specified height.
        This method can be called from the resize handle or other components.
        """
        if new_height <= 0:
            logger.warning(f"Ignoring invalid keyboard height request: {new_height}")
            return
            
        # Store the requested height and trigger the resize timer
        self._pending_keyboard_height = new_height
        self._keyboard_resize_timer.start()
        
    def apply_keyboard_height(self, new_height):
        """Apply a keyboard height immediately without using the timer.
        This is used for manual resizing to ensure the size is maintained.
        """
        if new_height <= 0:
            logger.warning(f"Ignoring invalid keyboard height: {new_height}")
            return
            
        # Set a flag to indicate this is a manual resize
        self._manual_resize = True
        
        try:
            # Calculate container height
            container_height = new_height + 10
            
            # Save the keyboard height in preferences
            self.preferences["keyboard_height"] = new_height
            logger.info(f"Manually applying keyboard height: {new_height}, container: {container_height}")
            
            # Resize the keyboard container directly
            if hasattr(self, 'keyboard_container') and self.keyboard_container.isVisible():
                self.keyboard_container.resize(self.keyboard_container.width(), container_height)
                
                # Resize the keyboard area directly
                if hasattr(self, 'keyboard_area'):
                    self.keyboard_area.resize(self.keyboard_area.width(), new_height)
                    
                    # Update the buttons to match the new size
                    if hasattr(self.keyboard_area, 'update_buttons'):
                        self.keyboard_area.update_buttons()
            
            # Force layout update
            self.updateGeometry()
            
            # Save preferences to ensure the size is remembered
            config.save_user_preferences(self.preferences)
            
        except Exception as e:
            logger.error(f"Error applying keyboard height: {e}")
        finally:
            # Clear the manual resize flag after a delay
            QTimer.singleShot(500, lambda: setattr(self, '_manual_resize', False))
        
    def _process_keyboard_resize(self):
        """Process the pending keyboard resize after the debounce timer times out."""
        try:
            # Check if we're in a user-initiated resize - if so, skip automatic resizing
            if hasattr(self, '_kb_resize_state') and self._kb_resize_state == ResizeState.USER:
                logger.debug("Skipping automatic resize as we're in a user-initiated resize operation")
                return
                
            # Also check if the keyboard is in a manual resize operation
            if hasattr(self.keyboard_area, 'resize_in_progress') and self.keyboard_area.resize_in_progress:
                logger.debug("Skipping automatic resize as keyboard is in a manual resize operation")
                return
                
            # Also check if the keyboard has the manual font size flag set
            if hasattr(self.keyboard_area, '_manual_font_size') and self.keyboard_area._manual_font_size:
                logger.debug("Skipping automatic resize as keyboard has manual font size flag set")
                return
                
            # Get the pending height
            new_height = self._pending_keyboard_height
            self._pending_keyboard_height = None # Clear pending height

            if new_height is None:
                return # No pending resize
                
            # Check for resize loops
            import time
            current_time = time.time()
            if current_time - self._last_resize_time < 1.0:  # Within 1 second
                self._resize_count += 1
                if self._resize_count > 10:
                    logger.warning(f"Detected resize loop! Count: {self._resize_count}, Time: {current_time - self._last_resize_time:.3f}s")
                    self._resize_count = 0  # Reset counter
                    return  # Skip this resize to break the loop
            else:
                self._resize_count = 0  # Reset counter
                
            self._last_resize_time = current_time

            logger.info(f"Processing keyboard resize to height: {new_height}")

            # Validate the new height to ensure it's reasonable
            if new_height <= 0:
                logger.warning(f"Ignoring invalid processed keyboard height: {new_height}")
                return

            # Check if this is a duplicate resize (same height as before)
            if hasattr(self, '_last_keyboard_height') and self._last_keyboard_height == new_height:
                logger.debug(f"Skipping duplicate processed resize to same height: {new_height}")
                return

            # Store the height for future comparison
            self._last_keyboard_height = new_height

            # Set a flag to indicate we're in a programmatic resize
            # This prevents resize loops when the keyboard itself is being resized
            if hasattr(self, '_in_resize') and self._in_resize:
                logger.debug("Skipping resize as we're already in a resize operation")
                return
                
            self._in_resize = True

            try:
                # Don't change minimum height here - keep it at the global minimum
                # Just resize the container to match the keyboard
                container_height = new_height + 10
    
                # Save the keyboard height in preferences
                self.preferences["keyboard_height"] = new_height
                logger.info(f"Keyboard resized to height: {new_height}, container: {container_height}")
                
                # Resize the keyboard container
                if hasattr(self, 'keyboard_container') and self.keyboard_container.isVisible():
                    self.keyboard_container.resize(self.keyboard_container.width(), container_height)
                    
                    # Resize the keyboard area directly
                    if hasattr(self, 'keyboard_area'):
                        self.keyboard_area.resize(self.keyboard_area.width(), new_height)
    
                # Update the buttons to match the new size
                if hasattr(self.keyboard_area, 'update_buttons'):
                    self.keyboard_area.update_buttons()
                    
                # Check if the keyboard is in a manual resize operation
                # If so, we should respect its current font size
                keyboard_in_manual_resize = (hasattr(self.keyboard_area, '_manual_font_size') and 
                                           self.keyboard_area._manual_font_size)
                
                # Only adjust font size if not in a manual resize operation
                if not keyboard_in_manual_resize:
                    # Calculate a new font size based on the keyboard height
                    # This ensures the font size is proportional to the keyboard height
                    # Base calculation: default height 264px corresponds to font size 26
                    base_height = 264
                    base_font_size = 26
                    current_font_size = self.preferences.get("keyboard_font_size", base_font_size)
                    
                    # Calculate new font size proportional to height and round to nearest integer
                    new_font_size = max(MIN_KB_FONT, min(MAX_KB_FONT, round(base_font_size * new_height / base_height)))
                    
                    # Only update if the integer value has changed significantly (more than 2 points)
                    # This prevents small oscillations that can cause resize loops
                    if abs(new_font_size - current_font_size) > 2:
                        logger.info(f"Adjusting keyboard font size from {current_font_size} to {new_font_size} based on height {new_height}")
                        # Update the font size without triggering another resize
                        self._manual_resize = True
                        self.preferences["keyboard_font_size"] = new_font_size
                        
                        # Update the keyboard font size directly without calling set_font_size
                        # to avoid triggering another resize
                        if hasattr(self.keyboard_area, 'font_size'):
                            self.keyboard_area.font_size = new_font_size
                            
                        # Update the buttons again with the new font size
                        if hasattr(self.keyboard_area, 'update_buttons'):
                            self.keyboard_area.update_buttons()
                else:
                    # We're in a manual resize operation, so respect the keyboard's current font size
                    logger.info(f"Skipping font size adjustment during manual keyboard resize")
                    
                    # Update the preferences with the keyboard's current font size
                    if hasattr(self.keyboard_area, 'font_size'):
                        current_font_size = self.keyboard_area.font_size
                        self.preferences["keyboard_font_size"] = current_font_size
                        logger.info(f"Updated preferences with current keyboard font size: {current_font_size}")
                    
                # Force layout update to apply changes
                self.updateGeometry()
            except Exception as layout_error:
                logger.error(f"Error updating layout after processed keyboard resize: {layout_error}")
            finally:
                # Always clear the resize flag
                self._in_resize = False

        except Exception as e:
            logger.error(f"Error in _process_keyboard_resize: {e}")
            # Try to recover by forcing a layout update
            try:
                self.updateGeometry()
            except:
                pass


    def ensure_keyboard_fits_screen(self):
        """Ensure the keyboard size fits within the available screen space"""
        try:
            # Check if we're in a manual resize - if so, skip automatic adjustments
            if hasattr(self, '_manual_resize') and self._manual_resize:
                logger.debug("Skipping keyboard size check as we're in a manual resize operation")
                return
                
            # Also check if the keyboard is in a manual resize operation
            if hasattr(self.keyboard_area, 'resize_in_progress') and self.keyboard_area.resize_in_progress:
                logger.debug("Skipping keyboard size check as keyboard is in a manual resize operation")
                return
                
            # Also check if the keyboard has the manual font size flag set
            if hasattr(self.keyboard_area, '_manual_font_size') and self.keyboard_area._manual_font_size:
                logger.debug("Skipping keyboard size check as keyboard has manual font size flag set")
                return
                
            # Get current screen size
            screen = self.screen()
            if not screen:
                logger.warning("Could not get screen information")
                return

            screen_height = screen.availableGeometry().height()
            screen_width = screen.availableGeometry().width()
            
            # Log screen dimensions for debugging
            logger.info(f"Screen dimensions: {screen_width}x{screen_height}")

            # Get current window size
            window_height = self.height()
            window_width = self.width()

            # Get current keyboard height with error handling
            try:
                # Get the current keyboard height
                keyboard_height = self.keyboard_area.height()
                
                # If the keyboard height is valid, use it
                if keyboard_height <= 0:
                    logger.debug(f"Invalid keyboard height: {keyboard_height}, using saved preference")
                    keyboard_height = self.preferences.get("keyboard_height", 264)
            except Exception as e:
                logger.error(f"Error getting keyboard height: {e}")
                keyboard_height = self.preferences.get("keyboard_height", 264)

            # Calculate maximum allowed keyboard height (e.g., 50% of screen height)
            max_keyboard_height = int(screen_height * 0.50)
            
            # Log the keyboard height information
            logger.info(f"Using keyboard height: {keyboard_height} (saved: {self.preferences.get('keyboard_height', 'not set')}, max: {max_keyboard_height})")

            # If keyboard is too large, resize it
            if keyboard_height > max_keyboard_height:
                # Only log at debug level to reduce noise during normal operation
                logger.debug(f"Limiting keyboard height to {max_keyboard_height} (50% of screen height)")

                # Check if we're already at the max height (within a small margin)
                # to avoid triggering unnecessary resize events
                if abs(keyboard_height - max_keyboard_height) > 5:
                    try:
                        # Resize keyboard without setting fixed height
                        self.keyboard_area.resize(self.keyboard_area.width(), max_keyboard_height)
                        self.keyboard_container.resize(self.keyboard_container.width(), max_keyboard_height + 10)
                        
                        # Update preferences
                        self.preferences["keyboard_height"] = max_keyboard_height

                        # Update buttons to match new size
                        if hasattr(self.keyboard_area, 'update_buttons'):
                             self.keyboard_area.update_buttons()

                        # Force layout update to ensure changes take effect
                        self.keyboard_area.updateGeometry()
                        self.keyboard_container.updateGeometry()
                    except Exception as resize_error:
                        logger.error(f"Error resizing keyboard: {resize_error}")
            else:
                # If the keyboard height is valid and not too large, respect it
                # This is important for manual resizing
                current_container_height = self.keyboard_container.height()
                expected_container_height = keyboard_height + 10
                
                # Only adjust if there's a significant difference
                if abs(current_container_height - expected_container_height) > 5:
                    logger.debug(f"Adjusting container height to match keyboard: {expected_container_height}")
                    self.keyboard_container.resize(self.keyboard_container.width(), expected_container_height)

            # Now ensure the entire window fits on screen
            try:
                self.ensure_window_fits_screen()
            except Exception as window_error:
                logger.error(f"Error ensuring window fits screen: {window_error}")

            # Log screen and window info at debug level to reduce noise
            logger.debug(f"Screen: {screen_width}x{screen_height}, Window: {self.width()}x{self.height()}, Keyboard height: {self.keyboard_area.height()}")
        except Exception as e:
            logger.error(f"Error in ensure_keyboard_fits_screen: {e}")
            # Try to recover by forcing a layout update
            try:
                self.updateGeometry()
            except:
                pass

    def ensure_window_fits_screen(self):
        """Ensure the entire application window fits within the screen"""
        try:
            # Get current screen size
            screen = self.screen()
            if not screen:
                logger.warning("Could not get screen information")
                return

            screen_rect = screen.availableGeometry()
            screen_height = screen_rect.height()
            screen_width = screen_rect.width()

            # Get current window size
            window_height = self.height()
            window_width = self.width()

            # Calculate maximum allowed window size (90% of screen)
            max_window_height = int(screen_height * 0.9)
            max_window_width = int(screen_width * 0.9)

            # If window is too large, resize it
            resized = False
            if window_height > max_window_height:
                logger.info(f"Adjusting window height from {window_height} to {max_window_height} to fit screen")
                window_height = max_window_height
                resized = True

            if window_width > max_window_width:
                logger.info(f"Adjusting window width from {window_width} to {max_window_width} to fit screen")
                window_width = max_window_width
                resized = True

            if resized:
                self.resize(window_width, window_height)

            # Also ensure the window is positioned on screen
            window_pos = self.pos()
            if not screen_rect.contains(self.frameGeometry()):
                # Center the window on screen
                new_x = screen_rect.center().x() - window_width // 2
                new_y = screen_rect.center().y() - window_height // 2
                self.move(new_x, new_y)
                logger.info(f"Repositioned window to center of screen")

            logger.info(f"Final window size: {self.width()}x{self.height()}")
        except Exception as e:
            logger.error(f"Error in ensure_window_fits_screen: {e}")

    def create_icon(self, name):
        """Create an icon for toolbar buttons using pyside_icons.py"""
        try:
            # Import the get_toolbar_icon function from ui.icons.py
            from ui.icons import get_toolbar_icon
            # Use the current theme to get the appropriate icon color
            theme = "dark" if self.theme_manager.is_dark_mode() else "light"
            return get_toolbar_icon(name, theme=theme)
        except (ImportError, AttributeError):
            # Fallback if ui.icons.py is not available or function not found
            return None

    def build_shortcuts(self):
        """Sets up keyboard shortcuts for common actions."""
        # File actions
        self.new_action = QAction("New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        self.new_action.setIcon(self.create_icon("new"))
        self.new_action.setProperty("icon_name", "new")

        self.open_action = QAction("Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setIcon(self.create_icon("open"))
        self.open_action.setProperty("icon_name", "open")

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setIcon(self.create_icon("save"))
        self.save_action.setProperty("icon_name", "save")

        # Edit actions
        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self.editor.cut)
        self.cut_action.setIcon(self.create_icon("cut"))
        self.cut_action.setProperty("icon_name", "cut")

        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.editor.copy)
        self.copy_action.setIcon(self.create_icon("copy"))
        self.copy_action.setProperty("icon_name", "copy")

        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.editor.paste)
        self.paste_action.setIcon(self.create_icon("paste"))
        self.paste_action.setProperty("icon_name", "paste")

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.editor.undo)
        self.undo_action.setIcon(self.create_icon("undo"))
        self.undo_action.setProperty("icon_name", "undo")

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.editor.redo)
        self.redo_action.setIcon(self.create_icon("redo"))
        self.redo_action.setProperty("icon_name", "redo")

        # View actions
        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.setShortcut("Ctrl+T")
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        self.toggle_theme_action.setIcon(self.create_icon("theme"))
        self.toggle_theme_action.setProperty("icon_name", "theme")

        # Add actions to the main window (this makes them available globally)
        self.addAction(self.new_action)
        self.addAction(self.open_action)
        self.addAction(self.save_action)
        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.toggle_theme_action)

# This is a duplicate method - removing it

    def toggle_toolbars(self):
        """Toggle visibility of toolbars."""
        # Get all toolbars
        toolbars = [toolbar for toolbar in self.findChildren(QToolBar)]

        # Check if any toolbar is visible
        any_visible = any(toolbar.isVisible() for toolbar in toolbars)

        # Toggle visibility
        for toolbar in toolbars:
            toolbar.setVisible(not any_visible)

    def toggle_keyboard(self):
        """Toggle on-screen keyboard visibility."""
        if self.keyboard_container.isVisible():
            self.keyboard_container.hide()
            self.keyboard_area.hide()
            if hasattr(self, 'keyboard_toggle_action'):
                # Keep the text as "Sinhala Keyboard" but update checked state
                self.keyboard_toggle_action.setChecked(False)
            # Update preferences
            self.preferences["show_keyboard"] = False
        else:
            self.keyboard_container.show()
            self.keyboard_area.show()
            if hasattr(self, 'keyboard_toggle_action'):
                # Keep the text as "Sinhala Keyboard" but update checked state
                self.keyboard_toggle_action.setChecked(True)
            # Update preferences
            self.preferences["show_keyboard"] = True
    
    def detach_keyboard(self):
        """Detach the keyboard to make it a floating window."""
        try:
            # Check if the keyboard is a SinhalaKeyboard
            if hasattr(self.keyboard_area, 'make_detachable'):
                # Hide the keyboard container
                self.keyboard_container.hide()
                
                # Make the keyboard detachable
                dialog = self.keyboard_area.make_detachable()
                
                # Store the dialog reference to prevent garbage collection
                self._keyboard_dialog = dialog
                
                # Update preferences
                self.preferences["keyboard_detached"] = True
                
                # Save preferences immediately to disk
                from app import config
                config.save_user_preferences(self.preferences)
                
                logger.info("Keyboard detached to floating window")
            else:
                logger.warning("Cannot detach keyboard - not a SinhalaKeyboard instance")
        except Exception as e:
            logger.error(f"Error detaching keyboard: {e}")
            
    def reset_keyboard_size(self):
        """Reset the keyboard to its default size."""
        try:
            # Default keyboard height
            default_height = 600  # Increased default height for better visibility
            
            # We no longer set minimum height constraints to allow more flexibility
            
            # Use resize instead of setFixedHeight to allow future resizing
            self.keyboard_area.resize(self.keyboard_area.width(), default_height)
            logger.info(f"Reset keyboard height to: {default_height}")
                
            # Resize the container
            self.keyboard_container.resize(self.keyboard_container.width(), default_height + 10)
            
            # Update preferences
            self.preferences["keyboard_height"] = default_height
            
            # Update buttons to match new size
            if hasattr(self.keyboard_area, 'update_buttons'):
                self.keyboard_area.update_buttons()
                logger.info("Updated keyboard buttons")
            
            # Force layout update
            self.keyboard_container.updateGeometry()
            self.updateGeometry()
            
            # Reset keyboard font size to default
            default_font_size = 60
            if hasattr(self.keyboard_area, 'set_font_size'):
                self.keyboard_area.set_font_size(default_font_size)
                self.preferences["keyboard_font_size"] = default_font_size
                logger.info(f"Reset keyboard font size to: {default_font_size}")
            
            logger.info(f"Keyboard reset to default height: {default_height}")
        except Exception as e:
            logger.error(f"Error in reset_keyboard_size: {e}")

        # Save preferences
        config.save_user_preferences(self.preferences)
        
    def set_keyboard_font_size(self, size):
        """Update the keyboard font size."""
        try:
            # Convert to integer for consistency
            size = round(float(size))
            
            # Validate size
            if size < MIN_KB_FONT or size > MAX_KB_FONT:
                logger.warning(f"Invalid keyboard font size: {size}")
                return
                
            # Guard against race conditions before we overwrite a user-set font
            if self._kb_resize_state == ResizeState.USER or \
               getattr(self.keyboard_area, '_manual_font_size', False):
                logger.debug("Skipping automatic font-calc during a user-initiated resize.")
                return
                
            # Update preferences
            self.preferences["keyboard_font_size"] = size
            
            # Update keyboard if it exists
            if hasattr(self.keyboard_area, 'set_font_size'):
                # Get the current keyboard height
                current_height = self.keyboard_area.height()
                
                # Check if we're in a manual resize operation
                keyboard_in_manual_resize = (hasattr(self.keyboard_area, 'resize_in_progress') and 
                                           self.keyboard_area.resize_in_progress)
                
                # Only adjust height if we're not in a manual resize operation
                if not keyboard_in_manual_resize:
                    # Calculate appropriate height based on font size
                    # This is the inverse of the calculation in the keyboard's mouseReleaseEvent
                    base_height = 264
                    base_font_size = 26
                    calculated_height = int((size / base_font_size) * base_height)
                    
                    # Set a flag to prevent automatic font size adjustment during resize
                    if hasattr(self.keyboard_area, '_manual_font_size'):
                        self.keyboard_area._manual_font_size = True
                    
                    # Only resize if the height difference is significant
                    if abs(calculated_height - current_height) > 10:
                        # Resize the keyboard to match the font size
                        self.keyboard_area.resize(self.keyboard_area.width(), calculated_height)
                        logger.info(f"Adjusted keyboard height to {calculated_height} based on font size {size}")
                else:
                    # We're in a manual resize operation, so respect the current height
                    logger.info(f"Keeping current keyboard height {current_height} during manual resize")
                
                # Now set the font size - this will trigger update_buttons
                # Pass a flag to indicate this is a manual font size change
                self.keyboard_area.set_font_size(size)
                logger.info(f"Keyboard font size updated to: {size}")
                
                # Force an update of the buttons after setting the font size
                if hasattr(self.keyboard_area, 'update_buttons'):
                    self.keyboard_area.update_buttons()
                    logger.info("Forced update of keyboard buttons after font size change")
                
                # Keep the manual font size flag set for a short time to prevent resize loops
                # We'll use a timer to reset it after a delay
                if hasattr(self, '_keyboard_font_timer'):
                    try:
                        self._keyboard_font_timer.stop()
                    except:
                        pass
                
                from PySide6.QtCore import QTimer
                self._keyboard_font_timer = QTimer()
                self._keyboard_font_timer.setSingleShot(True)
                self._keyboard_font_timer.timeout.connect(self._reset_keyboard_font_flag)
                self._keyboard_font_timer.start(2000)  # Increased to 2000ms (2 seconds) to prevent resize conflicts
            
            # Save preferences
            config.save_user_preferences(self.preferences)
        except Exception as e:
            logger.error(f"Error setting keyboard font size: {e}")
    
    def _reset_keyboard_font_flag(self):
        """Reset the manual font size flag after a delay."""
        try:
            if hasattr(self.keyboard_area, '_manual_font_size'):
                self.keyboard_area._manual_font_size = False
                logger.info("Reset keyboard manual font size flag")
        except Exception as e:
            logger.error(f"Error resetting keyboard font flag: {e}")
        
    def change_font_family(self, font_name):
        """Change the font family for the editor."""
        if not font_name:
            return
            
        # Create a new font with the selected family and current size
        current_size = self.base_font.pointSize()
        new_font = QFont(font_name, current_size)
        
        # Apply to editor
        self.editor.setFont(new_font)
        
        # Apply to suggestion area
        self.suggestion_area.setFont(new_font)
        
        # Update base font
        self.base_font = new_font
        
        # Update preferences
        self.preferences["font"] = font_name
        config.save_user_preferences(self.preferences)
        
    def change_font_size(self, size_text):
        """Change the font size for the editor."""
        try:
            # Convert size text to float
            size = float(size_text)
            if size <= 0:
                return
                
            # Create a new font with the current family and selected size
            font_name = self.base_font.family()
            new_font = QFont(font_name, size)
            
            # Apply to editor
            self.editor.setFont(new_font)
            
            # Apply to suggestion area
            self.suggestion_area.setFont(new_font)
            
            # Update base font
            self.base_font = new_font
            
            # Update preferences
            self.preferences["font_size"] = size
            config.save_user_preferences(self.preferences)
        except (ValueError, TypeError):
            # Ignore invalid input
            pass

    def toggle_singlish(self):
        """Toggle Singlish transliteration."""
        # Update action text based on checked state
        if self.singlish_toggle_action.isChecked():
            self.singlish_toggle_action.setText("Singlish: On")
            # Enable Singlish functionality
            # No need to do anything else as the event filter will handle it
            self.preferences["singlish_enabled"] = True
        else:
            self.singlish_toggle_action.setText("Singlish: Off")
            # Clear any pending buffer
            self.buffer.clear()
            self.word_start_pos = None
            self.clear_suggestion_area()
            self.preferences["singlish_enabled"] = False

        # Save preferences
        config.save_user_preferences(self.preferences)

    def toggle_suggestions(self):
        """Toggle suggestions display."""
        # Update action text based on checked state
        if self.suggestions_toggle_action.isChecked():
            self.suggestions_toggle_action.setText("Suggestions: On")
            # Show suggestions if there are any in the buffer
            if self.buffer:
                self.update_suggestion_area()
            self.preferences["show_suggestions"] = True
            logger.info("Suggestions enabled")
        else:
            self.suggestions_toggle_action.setText("Suggestions: Off")
            # Hide suggestion popup
            self.clear_suggestion_area()
            self.preferences["show_suggestions"] = False
            logger.info("Suggestions disabled")

        # Save preferences
        config.save_user_preferences(self.preferences)

    def build_toolbars(self):
        """Creates toolbars for standard and formatting actions."""
        # Standard Toolbar
        self.standard_toolbar = self.addToolBar("Standard")
        self.standard_toolbar.setObjectName("StandardToolbar")

        # Add actions to the standard toolbar
        self.standard_toolbar.addAction(self.new_action)
        self.standard_toolbar.addAction(self.open_action)
        self.standard_toolbar.addAction(self.save_action)
        self.standard_toolbar.addSeparator()
        self.standard_toolbar.addAction(self.cut_action)
        self.standard_toolbar.addAction(self.copy_action)
        self.standard_toolbar.addAction(self.paste_action)
        self.standard_toolbar.addSeparator()
        self.standard_toolbar.addAction(self.undo_action)
        self.standard_toolbar.addAction(self.redo_action)

        # Formatting Toolbar
        self.formatting_toolbar = self.addToolBar("Formatting")
        self.formatting_toolbar.setObjectName("FormattingToolbar")

        # Custom Font ComboBox for Sinhala fonts
        self.font_combo = QComboBox(self)
        
        # Add Sinhala fonts from our fonts directory
        if self.sinhala_font_families:
            self.font_combo.addItems(self.sinhala_font_families)
        else:
            # Fallback to system fonts that support Sinhala
            default_fonts = ["Iskoola Pota", "Nirmala UI", "Latha"]
            for font in default_fonts:
                self.font_combo.addItem(font)
        
        # Set current font from preferences or use first available Sinhala font
        current_font_name = self.preferences["font"]
        current_font_index = self.font_combo.findText(current_font_name)
        if current_font_index >= 0:
            self.font_combo.setCurrentIndex(current_font_index)
        
        # Connect font change signal to update editor font
        self.font_combo.currentTextChanged.connect(self.change_font_family)
        self.formatting_toolbar.addWidget(self.font_combo)

        # Font Size ComboBox
        self.size_combo = QComboBox(self)
        self.size_combo.setEditable(True)
        self.size_combo.setFixedWidth(50)  # Slightly wider to ensure numbers are visible
        self.size_combo.setMaxVisibleItems(10)  # Limit visible items to prevent excessive scrolling
        self.size_combo.setMaxCount(len(config.FONT_SIZES))  # Limit total items
        
        # Set alignment for the line edit inside the combo box
        if self.size_combo.lineEdit():
            self.size_combo.lineEdit().setAlignment(Qt.AlignCenter)
        
        # Populate with common font sizes
        sizes = config.FONT_SIZES
        self.size_combo.addItems([str(s) for s in sizes])
        
        # Set default size
        current_size = self.base_font.pointSize()
        default_size_index = sizes.index(current_size) if current_size in sizes else -1
        if default_size_index != -1:
             self.size_combo.setCurrentIndex(default_size_index)
        else:
             self.size_combo.setCurrentText(str(current_size))

        # Add custom styling for better appearance
        self.size_combo.setStyleSheet("""
            QComboBox { 
                padding-right: 15px;
                padding-left: 5px;
                font-weight: bold;  /* Make the font bold for better visibility */
            }
            QComboBox::item {
                padding: 3px;
                font-weight: bold;  /* Make dropdown items bold too */
            }
        """)
        
        # Apply custom delegate for better rendering
        self.size_combo.setItemDelegate(FontSizeDelegate(self.size_combo))

        # Connect size change signals
        self.size_combo.currentTextChanged.connect(self.change_font_size)
        self.formatting_toolbar.addWidget(self.size_combo)
        
        # Add separator
        self.formatting_toolbar.addSeparator()
        
        # Add text formatting actions (bold, italic, underline)
        self.bold_action = QAction("Bold", self)
        self.bold_action.setCheckable(True)
        self.bold_action.setIcon(self.create_icon("bold"))
        self.bold_action.setProperty("icon_name", "bold")
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.toggle_bold)
        self.formatting_toolbar.addAction(self.bold_action)
        
        self.italic_action = QAction("Italic", self)
        self.italic_action.setCheckable(True)
        self.italic_action.setIcon(self.create_icon("italic"))
        self.italic_action.setProperty("icon_name", "italic")
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.toggle_italic)
        self.formatting_toolbar.addAction(self.italic_action)
        
        self.underline_action = QAction("Underline", self)
        self.underline_action.setCheckable(True)
        self.underline_action.setIcon(self.create_icon("underline"))
        self.underline_action.setProperty("icon_name", "underline")
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.toggle_underline)
        self.formatting_toolbar.addAction(self.underline_action)

        # --- Feature Toggles Toolbar ---
        self.toggles_toolbar = self.addToolBar("Features")
        self.toggles_toolbar.setObjectName("FeaturesToolbar")

        # Create a custom widget for keyboard toggle with icon and text
        keyboard_widget = QWidget()
        keyboard_layout = QHBoxLayout(keyboard_widget)
        keyboard_layout.setContentsMargins(5, 0, 5, 0)
        keyboard_layout.setSpacing(5)

        # Create the keyboard button with icon
        keyboard_btn = QPushButton()
        keyboard_btn.setIcon(self.create_icon("keyboard"))
        keyboard_btn.setIconSize(QSize(24, 24))
        keyboard_btn.setFixedSize(32, 32)
        keyboard_btn.setCheckable(True)
        keyboard_btn.setChecked(self.preferences["show_keyboard"])
        keyboard_btn.setToolTip("Toggle Sinhala Keyboard")

        # Create the label
        keyboard_label = QLabel("Keyboard")
        keyboard_label.setStyleSheet("font-size: 12px;")

        # Add to layout
        keyboard_layout.addWidget(keyboard_btn)
        keyboard_layout.addWidget(keyboard_label)

        # Connect the button to toggle_keyboard
        keyboard_btn.clicked.connect(self.toggle_keyboard)

        # Add actions to the toggles toolbar
        self.toggles_toolbar.addAction(self.singlish_toggle_action)
        self.toggles_toolbar.addWidget(keyboard_widget)  # Add our custom widget instead of the action
        self.toggles_toolbar.addAction(self.suggestions_toggle_action)
        self.toggles_toolbar.addSeparator()
        self.toggles_toolbar.addAction(self.toggle_theme_action)
        
    def change_font_size(self, size_text):
        """Change the font size of the selected text or the entire editor if no selection."""
        try:
            # Convert the size text to an integer
            size = int(size_text)
            
            # Get the current cursor
            cursor = self.editor.textCursor()
            
            if cursor.hasSelection():
                # Apply font size only to selected text
                format = QTextCharFormat()
                format.setFontPointSize(size)
                cursor.mergeCharFormat(format)
                self.editor.setTextCursor(cursor)
            else:
                # No selection, update the default font for future text
                self.base_font.setPointSize(size)
                self.editor.setFont(self.base_font)
                # Font for suggestion popup is handled internally
                
                # Update preferences
                self.preferences["font_size"] = size
                config.save_user_preferences(self.preferences)
            
            # Log the change
            logging.info(f"Font size changed to {size}")
        except ValueError:
            # Handle invalid input
            logging.warning(f"Invalid font size: {size_text}")
            
            # Reset to current size
            current_size = self.base_font.pointSize()
            self.size_combo.setCurrentText(str(current_size))
            
    def change_font_family(self, font_name):
        """Change the font family of the selected text or the entire editor if no selection."""
        # Get the current cursor
        cursor = self.editor.textCursor()
        
        if cursor.hasSelection():
            # Apply font family only to selected text
            format = QTextCharFormat()
            format.setFontFamily(font_name)
            cursor.mergeCharFormat(format)
            self.editor.setTextCursor(cursor)
        else:
            # No selection, update the default font for future text
            self.base_font.setFamily(font_name)
            self.editor.setFont(self.base_font)
            # Font for suggestion popup is handled internally
            
            # Update preferences
            self.preferences["font"] = font_name
            config.save_user_preferences(self.preferences)
        
        # Log the change
        logging.info(f"Font family changed to {font_name}")
        
    def toggle_bold(self):
        """Toggle bold formatting for selected text."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            # Toggle bold state
            if self.bold_action.isChecked():
                format.setFontWeight(QFont.Bold)
            else:
                format.setFontWeight(QFont.Normal)
            cursor.mergeCharFormat(format)
            self.editor.setTextCursor(cursor)
        else:
            # If no selection, set the state for future typing
            format = self.editor.currentCharFormat()
            if self.bold_action.isChecked():
                format.setFontWeight(QFont.Bold)
            else:
                format.setFontWeight(QFont.Normal)
            self.editor.setCurrentCharFormat(format)
    
    def toggle_italic(self):
        """Toggle italic formatting for selected text."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontItalic(self.italic_action.isChecked())
            cursor.mergeCharFormat(format)
            self.editor.setTextCursor(cursor)
        else:
            # If no selection, set the state for future typing
            format = self.editor.currentCharFormat()
            format.setFontItalic(self.italic_action.isChecked())
            self.editor.setCurrentCharFormat(format)
    
    def toggle_underline(self):
        """Toggle underline formatting for selected text."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontUnderline(self.underline_action.isChecked())
            cursor.mergeCharFormat(format)
            self.editor.setTextCursor(cursor)
        else:
            # If no selection, set the state for future typing
            format = self.editor.currentCharFormat()
            format.setFontUnderline(self.underline_action.isChecked())
            self.editor.setCurrentCharFormat(format)
    
    def update_format_actions(self):
        """Update the state of formatting actions based on current cursor position."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        
        # Update bold action
        self.bold_action.setChecked(format.fontWeight() == QFont.Bold)
        
        # Update italic action
        self.italic_action.setChecked(format.fontItalic())
        
        # Update underline action
        self.underline_action.setChecked(format.fontUnderline())
    
    def update_combo_box_styles(self):
        """Update combo box styles based on current theme."""
        is_dark = self.theme_manager.is_dark_mode()
        
        # Get colors from theme manager
        if is_dark:
            dropdown_bg = self.theme_manager.get_color("SecondaryBackgroundColor")
            dropdown_fg = self.theme_manager.get_color("PrimaryForegroundColor")
            dropdown_border = self.theme_manager.get_color("StrokeColor")
            selection_bg = self.theme_manager.get_color("SelectedColor")
            selection_fg = self.theme_manager.get_color("PrimaryForegroundColor")
        else:
            dropdown_bg = self.theme_manager.get_color("PrimarySolidBackgroundColor")
            dropdown_fg = self.theme_manager.get_color("PrimaryForegroundColor")
            dropdown_border = self.theme_manager.get_color("StrokeColor")
            selection_bg = self.theme_manager.get_color("SelectedColor")
            selection_fg = self.theme_manager.get_color("PrimaryForegroundColor")
        
        # Common combo box style
        combo_style = f"""
            QComboBox {{ 
                background-color: {dropdown_bg};
                color: {dropdown_fg};
                border: 1px solid {dropdown_border};
                padding-right: 12px;
                padding-left: 2px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid {dropdown_border};
            }}
            QComboBox::item {{
                padding: 3px;
                background-color: {dropdown_bg};
                color: {dropdown_fg};
            }}
            QComboBox QAbstractItemView {{
                background-color: {dropdown_bg};
                color: {dropdown_fg};
                border: 1px solid {dropdown_border};
                selection-background-color: {selection_bg};
                selection-color: {selection_fg};
                outline: 0px;
            }}
        """
        
        # Apply styles to font size combo box
        if hasattr(self, 'size_combo'):
            self.size_combo.setStyleSheet(combo_style + """
                QComboBox { 
                    text-align: center;
                }
            """)
            
        # Apply styles to font combo box
        if hasattr(self, 'font_combo'):
            self.font_combo.setStyleSheet(combo_style)
            
    def apply_theme_to_all_widgets(self):
        """Apply the current theme to all widgets for consistent styling."""
        # Get the current theme
        theme = self.theme_manager.current_theme
        is_dark = theme == "dark"
        stylesheet = self.theme_manager.get_stylesheet()
        
        # Apply main stylesheet
        self.setStyleSheet(stylesheet)
        
        # Update theme label
        self.themeLbl.setText("☀️ Light" if not is_dark else "🌙 Dark")
        
        # Update keyboard theme
        self.keyboard_area.set_dark_mode(is_dark)
        
        # Update combo box styles
        self.update_combo_box_styles()
        
        # Update icons for the current theme
        self.update_icons_for_theme(theme)
        
        # Update suggestion popup theme
        theme_colors = {
            "OverlayColor": self.theme_manager.get_color("OverlayColor"),
            "PrimarySolidBackgroundColor": self.theme_manager.get_color("PrimarySolidBackgroundColor"),
            "PrimarySolidBorderColor": self.theme_manager.get_color("PrimarySolidBorderColor"),
            "PrimaryForegroundColor": self.theme_manager.get_color("PrimaryForegroundColor"),
            "MouseOverBackgroundColor": self.theme_manager.get_color("MouseOverBackgroundColor"),
            "AccentColor": self.theme_manager.get_color("AccentColor"),
            "AccentPressedColor": self.theme_manager.get_color("AccentPressedColor")
        }
        self.suggestion_popup.update_theme(is_dark, theme_colors)
        
        # Apply theme to all child widgets recursively
        self.apply_theme_to_widget(self, is_dark)
        
        # Log theme application
        logger.info(f"Applied {theme} theme to all widgets")
    
    def apply_theme_to_widget(self, widget, is_dark):
        """Recursively apply theme to a widget and all its children."""
        # Apply specific styling based on widget type
        if hasattr(widget, 'setProperty'):
            widget.setProperty("dark_mode", is_dark)
            
        # Process all child widgets
        for child in widget.findChildren(QWidget):
            self.apply_theme_to_widget(child, is_dark)
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        # Toggle theme using theme manager
        theme, _ = self.theme_manager.toggle_theme()
        
        # Apply theme to all widgets
        self.apply_theme_to_all_widgets()
        
        # Save theme preference
        self.preferences["theme"] = theme
        
        # Update preferences
        self.preferences["theme"] = theme
        config.save_user_preferences(self.preferences)
        
        # Log theme change
        logger.info(f"Theme toggled to {theme} mode with background: {self.theme_manager.get_color('PrimarySolidBackgroundColor')}")
        
    # Removed update_suggestion_label_style method
    # as it is no longer needed with the new SuggestionPopup implementation
            
    # Removed update_suggestion_buttons_theme method
    # as it is no longer needed with the new SuggestionPopup implementation
        
    def update_icons_for_theme(self, theme):
        """Update all toolbar and menu icons for the current theme."""
        # Import the icon creation function
        from ui.icons import get_toolbar_icon
        
        # Update standard toolbar icons
        if hasattr(self, 'standard_toolbar'):
            for action in self.standard_toolbar.actions():
                icon_name = action.property("icon_name")
                if icon_name:
                    action.setIcon(get_toolbar_icon(icon_name, theme))
        
        # Update formatting toolbar icons
        if hasattr(self, 'formatting_toolbar'):
            for action in self.formatting_toolbar.actions():
                icon_name = action.property("icon_name")
                if icon_name:
                    action.setIcon(get_toolbar_icon(icon_name, theme))
        
        # Update toggles toolbar icons
        if hasattr(self, 'toggles_toolbar'):
            for action in self.toggles_toolbar.actions():
                icon_name = action.property("icon_name")
                if icon_name:
                    action.setIcon(get_toolbar_icon(icon_name, theme))
        
        # Update menu icons
        for menu in self.menuBar().findChildren(QMenu):
            for action in menu.actions():
                icon_name = action.property("icon_name")
                if icon_name:
                    action.setIcon(get_toolbar_icon(icon_name, theme))

    def update_recent_files_menu(self):
        """Update the recent files menu with the latest files."""
        # Create the menu if it doesn't exist
        if not self.recent_files_menu:
            return

        # Clear the menu
        self.recent_files_menu.clear()

        # Add recent files
        if self.preferences["recent_files"]:
            for filepath in self.preferences["recent_files"]:
                if os.path.exists(filepath):
                    action = QAction(os.path.basename(filepath), self)
                    action.setData(filepath)
                    action.triggered.connect(self.open_recent_file)
                    self.recent_files_menu.addAction(action)

            # Add separator and clear action
            if self.recent_files_menu.actions():
                self.recent_files_menu.addSeparator()
                clear_action = QAction("Clear Recent Files", self)
                clear_action.triggered.connect(self.clear_recent_files)
                self.recent_files_menu.addAction(clear_action)
        else:
            # Add a disabled "No Recent Files" action
            no_files_action = QAction("No Recent Files", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)

    def open_recent_file(self):
        """Open a file from the recent files menu."""
        action = self.sender()
        if action:
            filepath = action.data()
            if os.path.exists(filepath):
                # Check if there are unsaved changes
                if self.editor.document().isModified():
                    reply = QMessageBox.question(
                        self, 
                        "Save Changes?",
                        "Do you want to save changes before opening a new file?",
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                    )

                    if reply == QMessageBox.Cancel:
                        return
                    elif reply == QMessageBox.Yes:
                        self.save_file()

                # Open the file
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.editor.setPlainText(f.read())

                    # Update window title
                    self.setWindowTitle(f"Sinhala Word Processor - {os.path.basename(filepath)}")

                    # Move this file to the top of recent files
                    self.preferences = config.add_recent_file(self.preferences, filepath)
                    config.save_user_preferences(self.preferences)

                    # Update recent files menu
                    self.update_recent_files_menu()

                    logger.info(f"Opened recent file: {filepath}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
                    logger.error(f"Error opening recent file: {e}")

    def clear_recent_files(self):
        """Clear the recent files list."""
        self.preferences["recent_files"] = []
        config.save_user_preferences(self.preferences)
        self.update_recent_files_menu()
        logger.info("Cleared recent files list")

    def build_menu(self):
        """Creates the application menu."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        # Use the actions stored as instance attributes
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)

        # Add Save As action
        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(self.save_as_action)

        # Add Recent Files submenu
        file_menu.addSeparator()
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self.update_recent_files_menu()

        file_menu.addSeparator()
        # Create exit action here as it's only used in the menu
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        # Use the actions stored as instance attributes
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

        # Add spell check action
        edit_menu.addSeparator()
        spell_check_action = QAction("Check Spelling", self)
        spell_check_action.setShortcut("F7")
        spell_check_action.triggered.connect(self.perform_spell_check)
        edit_menu.addAction(spell_check_action)

        # Add dictionary management action
        add_to_dict_action = QAction("Add Selected Word to Dictionary", self)
        add_to_dict_action.triggered.connect(self.learn_selected_word)
        edit_menu.addAction(add_to_dict_action)

        # View Menu
        view_menu = menu_bar.addMenu("&View")
        # Use the action stored as instance attribute
        view_menu.addAction(self.toggle_theme_action)

        # Add toggle toolbars action
        self.toggle_toolbars_action = QAction("Toggle Toolbars", self)
        self.toggle_toolbars_action.setShortcut("Ctrl+Alt+T")
        self.toggle_toolbars_action.triggered.connect(self.toggle_toolbars)
        view_menu.addAction(self.toggle_toolbars_action)

        # Add toggle keyboard action
        self.toggle_keyboard_action = QAction("Toggle Keyboard", self)
        self.toggle_keyboard_action.setShortcut("Ctrl+K")
        self.toggle_keyboard_action.triggered.connect(self.toggle_keyboard)
        view_menu.addAction(self.toggle_keyboard_action)
        
        # Add reset keyboard size action
        self.reset_keyboard_action = QAction("Reset Keyboard Size", self)
        self.reset_keyboard_action.setShortcut("Ctrl+Alt+K")
        self.reset_keyboard_action.triggered.connect(self.reset_keyboard_size)
        view_menu.addAction(self.reset_keyboard_action)
        
        # Add keyboard font size submenu
        keyboard_font_menu = QMenu("Keyboard Font Size", self)
        
        # Add font size options - use larger sizes for better visibility
        for size in [40, 50, 60, 70, 80]:
            action = QAction(f"{size}pt", self)
            action.triggered.connect(lambda checked, s=size: self.set_keyboard_font_size(s))
            keyboard_font_menu.addAction(action)
            
        view_menu.addMenu(keyboard_font_menu)

        # Add toggle suggestions action
        view_menu.addAction(self.suggestions_toggle_action)

        # Add toggle Singlish action
        view_menu.addAction(self.singlish_toggle_action)
        
        # Add separator
        view_menu.addSeparator()
        
        # Add settings action
        self.settings_action = QAction("Settings...", self)
        self.settings_action.setShortcut("Ctrl+,")
        self.settings_action.triggered.connect(self.show_settings_dialog)
        view_menu.addAction(self.settings_action)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")

        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Help action
        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Sinhala Word Processor",
            """<h1>Sinhala Word Processor</h1>
            <p>Version 3.3</p>
            <p>A lightweight word processor with Sinhala transliteration support.</p>
            <p>Features:</p>
            <ul>
                <li>Realtime Singlish to Sinhala transliteration</li>
                <li>Suggestion popup</li>
                <li>Basic spell checker</li>
                <li>Dark/Light theme toggle</li>
            </ul>
            """
        )

    def show_help_dialog(self):
        """Show the help dialog."""
        QMessageBox.information(
            self,
            "Help",
            """<h2>Sinhala Word Processor Help</h2>
            <h3>Keyboard Shortcuts:</h3>
            <ul>
                <li><b>Ctrl+N</b>: New file</li>
                <li><b>Ctrl+O</b>: Open file</li>
                <li><b>Ctrl+S</b>: Save file</li>
<li><b>Ctrl+Shift+S</b>: Save file as</li><li><b>Ctrl+X</b>: Cut</li>
                <li><b>Ctrl+C</b>: Copy</li>
                <li><b>Ctrl+V</b>: Paste</li>
                <li><b>Ctrl+Z</b>: Undo</li>
                <li><b>Ctrl+Y</b>: Redo</li>
                <li><b>Ctrl+T</b>: Toggle theme</li>
                <li><b>Ctrl+K</b>: Toggle keyboard</li>
                <li><b>F7</b>: Check spelling</li>
            </ul>

            <h3>Singlish to Sinhala:</h3>
            <p>Type in Singlish (romanized Sinhala) and it will be automatically 
            converted to Sinhala. Use numbers 1-9 to select from suggestions.</p>

            <h3>Adding Words to Dictionary:</h3>
            <p>Select a Sinhala word, right-click and choose "Learn Selected Word" 
            to add it to your personal dictionary.</p>
            """
        )

    def new_file(self):
        """Create a new file."""
        # Ask to save changes if there's content in the editor
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, 
                "Save Changes?",
                "Do you want to save changes before creating a new file?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_file()

        # Clear the editor
        self.editor.clear()
        self.buffer.clear()
        self.word_start_pos = None
        self.clear_suggestion_area()
        self.update_status()

        # Reset window title
        self.setWindowTitle("Sinhala Word Processor")

    def open_file(self):
        """Opens a plain-text file in the editor."""
        # Ask to save changes if there's content in the editor
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, 
                "Save Changes?",
                "Do you want to save changes before opening a new file?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_file()

        # Get the directory of the most recently opened file, if any
        initial_dir = ""
        if self.preferences["recent_files"] and os.path.exists(os.path.dirname(self.preferences["recent_files"][0])):
            initial_dir = os.path.dirname(self.preferences["recent_files"][0])

        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            initial_dir, 
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())

                # Add to recent files
                self.preferences = config.add_recent_file(self.preferences, file_path)
                config.save_user_preferences(self.preferences)

                # Update recent files menu
                self.update_recent_files_menu()

                # Update window title with filename
                self.setWindowTitle(f"Sinhala Word Processor - {os.path.basename(file_path)}")

                logger.info(f"Opened file: {os.path.basename(file_path)}")

                # Perform spell check on the loaded file
                self.spell_check_timer.start(500)  # Start spell check after 500ms
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
                logger.error(f"Error opening file: {e}")

    def save_file(self):
        """Saves the current editor content to a plain-text file."""
        # Check if we have a current file path from recent files
        current_file = None
        if self.windowTitle() != "Sinhala Word Processor":
            # Extract filename from window title
            filename = self.windowTitle().replace("Sinhala Word Processor - ", "")
            # Find the file in recent files
            for filepath in self.preferences["recent_files"]:
                if os.path.basename(filepath) == filename:
                    current_file = filepath
                    break

        if current_file and os.path.exists(current_file):
            # Save to the current file
            try:
                with open(current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                logger.info(f"Saved file: {os.path.basename(current_file)}")
                self.editor.document().setModified(False)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
                logger.error(f"Error saving file: {e}")
                return False
        else:
            # No current file, use Save As
            return self.save_as_file()

    def save_as_file(self):
        """Save the current editor content to a new file."""
        # Get the directory of the most recently saved file, if any
        initial_dir = ""
        if self.preferences["recent_files"] and os.path.exists(os.path.dirname(self.preferences["recent_files"][0])):
            initial_dir = os.path.dirname(self.preferences["recent_files"][0])

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save File As", 
            initial_dir, 
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())

                # Add to recent files
                self.preferences = config.add_recent_file(self.preferences, file_path)
                config.save_user_preferences(self.preferences)

                # Update recent files menu
                self.update_recent_files_menu()

                # Update window title with filename
                self.setWindowTitle(f"Sinhala Word Processor - {os.path.basename(file_path)}")

                logger.info(f"Saved file as: {os.path.basename(file_path)}")
                self.editor.document().setModified(False)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
                logger.error(f"Error saving file: {e}")
                return False

        return False

    def handle_keypress_event(self, obj, event):
        """Handle keypress events for the editor."""
        try:
            key = event.key()
            text = event.text()

            # Check if Singlish is enabled
            singlish_enabled = hasattr(self, 'singlish_toggle_action') and self.singlish_toggle_action.isChecked()
            suggestions_enabled = hasattr(self, 'suggestions_toggle_action') and self.suggestions_toggle_action.isChecked()

            # If Singlish is disabled, don't process any special handling
            if not singlish_enabled:
                return False
                
            # Handle cursor movement keys - commit buffer if active
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End) and self.buffer:
                logger.info(f"Cursor movement detected with active buffer - committing buffer")
                self.commit_buffer()
                return False  # Don't consume the event
                
            # If suggestions are enabled and we have suggestions, handle selection keys
            if suggestions_enabled and self.current_suggestions:
                if key in (Qt.Key_Return, Qt.Key_Enter):
                    # Accept the current suggestion on Enter
                    try:
                        # Get the current index from the popup
                        current_index = self.suggestion_popup.current_index
                        if current_index >= 0 and current_index < len(self.current_suggestions):
                            sinhala_word = self.current_suggestions[current_index]
                        else:
                            # Default to first suggestion if no current index
                            sinhala_word = self.current_suggestions[0]
                        
                        # Log the selected suggestion
                        logger.info(f"Selected suggestion: '{sinhala_word}'")
                        
                        # Clear suggestions first to avoid race conditions
                        self.clear_suggestion_area()
                        # Accept the suggestion (this will also clear the buffer)
                        self.accept_suggestion(sinhala_word)
                        return True # Consume Enter
                    except Exception as e:
                        logger.error(f"Error handling Enter key: {e}")
                        self.reset_input_state()
                        return False
                        
                elif key == Qt.Key_Space:
                    try:
                        # When space is pressed, just hide the suggestions without selecting any
                        # and insert a space character
                        if self.current_suggestions:
                            # Hide the suggestion popup
                            self.suggestion_popup.hide()
                            # Clear suggestions
                            self.current_suggestions = []
                            # Commit the buffer as is
                            if self.buffer:
                                self.commit_buffer()
                            # Insert a space
                            self.editor.insertPlainText(" ")
                            return True # Consume Space
                        else:
                            # No suggestions, commit buffer if any and let space through
                            if self.buffer:
                                self.commit_buffer()
                            return False
                    except Exception as e:
                        logger.error(f"Error handling Space key: {e}")
                        self.reset_input_state()
                        return False
                        
                elif key == Qt.Key_Escape:
                    self.reset_input_state()
                    return True # Consume Escape
                    
                elif key == Qt.Key_Tab:
                    # Navigate to next suggestion
                    self.suggestion_popup.navigate_next()
                    return True # Consume Tab
                    
                elif key == Qt.Key_Backtab:
                    # Navigate to previous suggestion
                    self.suggestion_popup.navigate_previous()
                    return True # Consume Shift+Tab
                    
                elif key == Qt.Key_Down:
                    # Navigate to next suggestion
                    self.suggestion_popup.navigate_next()
                    return True # Consume Down arrow
                    
                elif key == Qt.Key_Up:
                    # Navigate to previous suggestion
                    self.suggestion_popup.navigate_previous()
                    return True # Consume Up arrow
                    
                elif Qt.Key_1 <= key <= Qt.Key_9:
                    index = key - Qt.Key_1
                    if index < len(self.current_suggestions):
                        try:
                            # Make a local copy of the suggestion to avoid race conditions
                            sinhala_word = self.current_suggestions[index]
                            
                            # Log the selected suggestion
                            logger.info(f"Selected suggestion {index+1}: '{sinhala_word}'")
                            
                            # Clear suggestions first to avoid race conditions
                            self.clear_suggestion_area()
                            # Accept the suggestion (this will also clear the buffer)
                            self.accept_suggestion(sinhala_word)
                            return True # Consume number key
                        except Exception as e:
                            logger.error(f"Error handling number key: {e}")
                            logger.error(f"Exception details: {str(e)}")
                            import traceback
                            logger.error(f"Traceback: {traceback.format_exc()}")
                            self.reset_input_state()
                            return False

            # If Backspace is pressed, handle buffer modification
            if key == Qt.Key_Backspace:
                # If buffer is not empty, remove last char from buffer
                if self.buffer:
                    self.buffer.pop()
                    # After popping, update or clear suggestion area
                    if suggestions_enabled:
                        if self.buffer:
                            # Cancel any pending suggestion updates
                            if hasattr(self, '_suggestion_timer') and self._suggestion_timer.isActive():
                                self._suggestion_timer.stop()
                            
                            # Create a new timer with a slightly longer delay
                            self._suggestion_timer = QTimer()
                            self._suggestion_timer.setSingleShot(True)
                            self._suggestion_timer.timeout.connect(self.update_suggestion_area)
                            self._suggestion_timer.start(30)  # Increased delay for better stability
                        else:
                            self.clear_suggestion_area()
                            self.word_start_pos = None
                    # Do NOT consume backspace here, let the editor handle it
                    return False
                else:
                    # If buffer is empty, let editor handle backspace normally
                    if suggestions_enabled:
                        self.clear_suggestion_area() # Ensure area is hidden if buffer becomes empty
                    self.word_start_pos = None # Explicitly reset word_start_pos
                    return False

            # Handle alphanumeric keys: append to buffer
            if text.isalnum() and len(text) == 1:
                # Verify cursor position is where we expect it to be if buffer is not empty
                if self.buffer and self.word_start_pos is not None:
                    current_pos = self.editor.textCursor().position()
                    expected_pos = self.word_start_pos + len(self.buffer)
                    
                    # If cursor is not where expected, commit buffer and start a new one
                    if current_pos != expected_pos:
                        logger.info(f"Cursor position mismatch: expected {expected_pos}, got {current_pos} - committing buffer")
                        self.commit_buffer()
                        self.word_start_pos = self.editor.textCursor().position()
                
                if not self.buffer: # If buffer was empty, mark the start position
                     self.word_start_pos = self.editor.textCursor().position()
                     
                self.buffer.append(text)
                
                # Update suggestions immediately after adding to buffer
                if suggestions_enabled:
                    # Cancel any pending suggestion updates
                    if hasattr(self, '_suggestion_timer') and self._suggestion_timer.isActive():
                        self._suggestion_timer.stop()
                    
                    # Update suggestions immediately
                    self.update_suggestion_area()
                
                # Do NOT consume the event, let the editor insert the character
                return False

            # For any other key (punctuation, symbols, arrows, etc.), commit the current buffer
            # and then clear the suggestion area.
            if self.buffer:
                self.commit_buffer()
            return False # Do not consume the event, let the editor handle it

        except Exception as e:
            logger.error(f"Exception in handle_keypress_event: {e}")
            # Ensure area is hidden on error
            self.reset_input_state()
            return False
            
    def reset_input_state(self):
        """Reset all input state variables to avoid crashes."""
        # Cancel any pending suggestion updates
        if hasattr(self, '_suggestion_timer') and self._suggestion_timer.isActive():
            self._suggestion_timer.stop()
            
        self.buffer.clear()
        self.word_start_pos = None
        self.clear_suggestion_area()
        
        logger.info("Input state reset")
        
    def replace_with_suggestion(self, singlish_word):
        """Replace the current buffer text with the selected suggestion."""
        try:
            if not singlish_word:
                return
                
            # Get the Sinhala word for the suggestion
            sinhala_word = self.transliterator.transliterate(singlish_word)
            if not sinhala_word or sinhala_word == singlish_word:
                # Fallback to phonetic if not in map
                sinhala_word = _phonetic_global(singlish_word)
                
            if not sinhala_word:
                return
                
            # Only proceed if we have a valid word_start_pos
            if self.word_start_pos is None:
                return
                
            # Get the current cursor
            cur = self.editor.textCursor()
            cur.beginEditBlock()
            
            # Store the current position
            current_pos = cur.position()
            
            # Get the current document text
            doc_text = self.editor.toPlainText()
            
            # Calculate how many characters to select - use the buffer content length
            # instead of the suggestion length, as the buffer contains what was actually typed
            buffer_text = "".join(self.buffer) if self.buffer else singlish_word
            buffer_length = len(buffer_text)
            
            # Make sure we don't go beyond document bounds
            document_length = len(doc_text)
            if self.word_start_pos >= document_length:
                # Invalid position, abort
                cur.endEditBlock()
                return
                
            # Adjust buffer_length to not exceed document bounds
            if self.word_start_pos + buffer_length > document_length:
                buffer_length = document_length - self.word_start_pos
                
            # Move to the start position
            cur.setPosition(self.word_start_pos)
            
            # Select the text to replace (only if we have a valid length)
            if buffer_length > 0:
                cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, buffer_length)
                
                # Replace with the Sinhala word
                cur.insertText(sinhala_word)
            
            cur.endEditBlock()
            
        except Exception as e:
            logger.error(f"Error in replace_with_suggestion: {e}")
            # Reset state on error
            self.reset_input_state()

    def update_suggestion_area(self):
        """Update and show/hide the suggestion popup based on the current buffer."""
        try:
            # Check if suggestions are enabled
            if hasattr(self, 'suggestions_toggle_action') and not self.suggestions_toggle_action.isChecked():
                logger.info("Suggestions disabled")
                self.suggestion_popup.hide()
                return
            
            # If buffer is empty, hide suggestion popup
            if not self.buffer:
                logger.info("Buffer is empty, hiding suggestion popup")
                self.suggestion_popup.hide()
                return
                
            current_word = "".join(self.buffer).lower()
            
            # Use the transliterator to get suggestions
            self.current_suggestions = self.transliterator.get_suggestions(current_word, max_suggestions=9)
            
            # Log the suggestions for debugging
            logger.info(f"Suggestions for '{current_word}': {self.current_suggestions}")
            
            # Get the cursor rectangle to position the popup
            cursor = self.editor.textCursor()
            cursor_rect = self.editor.cursorRect(cursor)
            editor_rect = self.editor.rect()
            
            # Update theme colors for the popup
            theme_colors = {
                "OverlayColor": self.theme_manager.get_color("OverlayColor"),
                "PrimarySolidBackgroundColor": self.theme_manager.get_color("PrimarySolidBackgroundColor"),
                "PrimarySolidBorderColor": self.theme_manager.get_color("PrimarySolidBorderColor"),
                "PrimaryForegroundColor": self.theme_manager.get_color("PrimaryForegroundColor"),
                "MouseOverBackgroundColor": self.theme_manager.get_color("MouseOverBackgroundColor"),
                "AccentColor": self.theme_manager.get_color("AccentColor"),
                "AccentPressedColor": self.theme_manager.get_color("AccentPressedColor")
            }
            
            # Update the popup theme
            self.suggestion_popup.update_theme(
                self.theme_manager.is_dark_mode(),
                theme_colors
            )
            
            # Show the popup with suggestions
            if self.current_suggestions:
                # Make sure the editor keeps focus
                self.editor.setFocus()
                
                # Show the popup with suggestions
                self.suggestion_popup.show_popup(
                    self.current_suggestions,
                    cursor_rect,
                    editor_rect
                )
                
                # Make sure the editor still has focus after showing popup
                QTimer.singleShot(10, self.editor.setFocus)
                
                logger.info(f"Showing suggestion popup with {len(self.current_suggestions)} suggestions")
            else:
                # No suggestions available, hide the popup
                self.suggestion_popup.hide()
                logger.info("No suggestions available, hiding popup")
            
        except Exception as e:
            logger.error(f"Error in update_suggestion_area: {e}")
            logger.error(f"Exception details: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Hide the popup in case of error
            self.suggestion_popup.hide()

    def clear_suggestion_area(self):
        """Hide the suggestion popup and clear stored suggestions."""
        try:
            # Hide the popup
            self.suggestion_popup.hide()
            
            # Clear stored suggestions
            self.current_suggestions = []
            
            # Log that we've cleared the area
            logger.info("Cleared suggestion area")
        except Exception as e:
            logger.error(f"Error in clear_suggestion_area: {e}")
            # Reset everything to be safe
            self.current_suggestions = []
        
        # Log the clearing
        logger.info("Cleared suggestion area")

    def accept_suggestion(self, sinhala_word):
        """Accept a suggestion and replace the buffered text."""
        # This matches the behavior in SinhalaWordProcessor_enhanced.py
        if self.buffer and self.word_start_pos is not None:
            try:
                # Log the operation
                buffer_text = "".join(self.buffer)
                logger.info(f"Accepting suggestion: '{sinhala_word}' to replace buffer: '{buffer_text}'")
                
                cur = self.editor.textCursor()
                cur.beginEditBlock()

                # Get the actual text in the document at the expected position
                doc = self.editor.document()
                check_cursor = QTextCursor(doc)
                check_cursor.setPosition(self.word_start_pos)
                check_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(buffer_text))
                actual_text = check_cursor.selectedText()
                
                # Verify the text matches our buffer before replacing
                if actual_text == buffer_text:
                    # Standard replacement as before
                    cur.setPosition(self.word_start_pos)
                    cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(buffer_text))
                    cur.removeSelectedText()
                    cur.insertText(sinhala_word)
                    logger.info(f"Text matched buffer - standard replacement performed")
                else:
                    # Text doesn't match buffer - use a more robust approach
                    logger.warning(f"Buffer text '{buffer_text}' doesn't match document text '{actual_text}'")
                    
                    # Try to find the buffer text near the current position
                    current_pos = cur.position()
                    search_start = max(0, self.word_start_pos - 10)
                    search_end = min(doc.characterCount(), current_pos + 10)
                    
                    # Create a cursor for searching
                    search_cursor = QTextCursor(doc)
                    search_cursor.setPosition(search_start)
                    search_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, search_end - search_start)
                    search_text = search_cursor.selectedText()
                    
                    # Try to find the buffer text in the search area
                    buffer_pos = search_text.find(buffer_text)
                    if buffer_pos >= 0:
                        # Found the buffer text, replace it
                        replace_pos = search_start + buffer_pos
                        cur.setPosition(replace_pos)
                        cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(buffer_text))
                        cur.removeSelectedText()
                        cur.insertText(sinhala_word)
                        logger.info(f"Found buffer text at position {replace_pos} - replacement performed")
                    else:
                        # Couldn't find the buffer text, just insert at current position
                        logger.warning(f"Couldn't find buffer text near cursor - inserting at current position")
                        cur.insertText(sinhala_word)
                
                cur.endEditBlock()

                # Clear the buffer and reset word_start_pos
                self.buffer.clear()
                self.word_start_pos = None
                
                # Log success
                logger.info(f"Successfully accepted suggestion: '{sinhala_word}'")
            except Exception as e:
                logger.error(f"Error in accept_suggestion: {e}")
                logger.error(f"Exception details: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                self.reset_input_state()
                
                # Clear area after accepting
                self.clear_suggestion_area()
        else:
            # If there's no buffer or word_start_pos, just clear the suggestion area
            self.clear_suggestion_area()

    def commit_buffer(self):
        """Commit the buffered input to the editor (phonetic transliteration)."""
        try:
            # Check if Singlish is enabled
            singlish_enabled = hasattr(self, 'singlish_toggle_action') and self.singlish_toggle_action.isChecked()
            
            # Clear suggestion area regardless of Singlish state
            self.clear_suggestion_area()
            
            # If Singlish is disabled or buffer is empty, don't process
            if not singlish_enabled or not self.buffer or self.word_start_pos is None:
                return

            word = "".join(self.buffer)
            logger.info(f"Committing buffer: '{word}'")

            # Use the transliterator to get the Sinhala word
            sinhala_word = self.transliterator.transliterate(word)
            if not sinhala_word or sinhala_word == word:
                # Fallback to phonetic
                sinhala_word = _phonetic_global(word)
                
            logger.info(f"Transliterated to: '{sinhala_word}'")

            cur = self.editor.textCursor()
            cur.beginEditBlock()

            # Move cursor to the start of the buffered word
            cur.setPosition(self.word_start_pos)
            # Select the buffered text
            cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(word))
            # Remove the buffered text
            cur.removeSelectedText()
            # Insert the transliterated Sinhala word
            cur.insertText(sinhala_word)
            cur.endEditBlock()

            # Clear the buffer and reset word_start_pos
            self.buffer.clear()
            self.word_start_pos = None # Reset word_start_pos after committing
            
        except Exception as e:
            logger.error(f"Error in commit_buffer: {e}")
            # Reset state on error
            self.buffer.clear()
            self.word_start_pos = None
            self.clear_suggestion_area()

    def eventFilter(self, obj, event):
        # Check if the event is for the editor
        if event.type() == QEvent.KeyPress and (obj is self.editor or obj is self.editor.viewport()):
             # Pass the event and the object it occurred on to handle_keypress_event
             return self.handle_keypress_event(obj, event)
        
        # Track cursor position changes when buffer is active
        elif event.type() == QEvent.MouseButtonPress and (obj is self.editor or obj is self.editor.viewport()) and self.buffer:
            # If user clicks elsewhere while buffer is active, commit the buffer
            logger.info("Mouse click detected with active buffer - committing buffer")
            self.commit_buffer()
            return False  # Don't consume the event
            
        # For any other event or object, let the default event filter handle it
        return super().eventFilter(obj, event)

    @Slot() # Decorator to indicate this is a slot
    def on_text_changed(self):
        # The buffer is now managed by handle_keypress_event
        # This slot is mainly for updating the status bar
        self.update_status()

        # Start spell check timer
        self.spell_check_timer.start(1000)  # Check spelling after 1 second of inactivity

    def perform_spell_check(self):
        """Perform spell checking on the editor content."""
        # Get the current text
        text = self.editor.toPlainText()

        # Clear existing spell check formatting
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        fmt = QTextCharFormat()
        cursor.setCharFormat(fmt)
        cursor.clearSelection()

        # Find all Sinhala words and check them
        sinhala_word_pattern = re.compile(r'[\u0D80-\u0DFF]+')
        for match in sinhala_word_pattern.finditer(text):
            word = match.group(0)
            if not self.spellchecker.is_known_word(word):
                # Underline the misspelled word
                cursor = self.editor.textCursor()
                cursor.setPosition(match.start())
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(word))

                fmt = QTextCharFormat()
                fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                fmt.setUnderlineColor(QColor("red"))
                cursor.mergeCharFormat(fmt)

    def suggestions(self, prefix: str, limit: int = 9):
        """Get a list of suggestions for a given prefix from the dictionary."""
        # Use the transliterator to get suggestions
        return self.transliterator.get_suggestions(prefix, max_suggestions=limit)

    # --- Transliteration/Suggestion Methods ---
    def tr(self, word: str) -> str:
        """Transliterate a word from Singlish to Sinhala."""
        return self.transliterator.transliterate(word) or _phonetic_global(word)

    # --- Save Method ---
    def _save_map(self, force=False):
        if force or self.SAVE_PENDING:
            try:
                with open(self.USER_MAP_FP, "w", encoding="utf8") as f:
                    json.dump(self.USER_MAP, f, ensure_ascii=False, indent=2)
                self.SAVE_PENDING = False
                logger.info(f"User map saved to {os.path.basename(self.USER_MAP_FP)}")
            except Exception as e:
                logger.error(f"Error saving user map file: {e}")
                QMessageBox.warning(self, "Warning", f"Could not save user dictionary: {e}")

    # --- Status update ---
    def update_status(self):
        # Check if status bar widgets exist before updating
        if hasattr(self, 'lineCol') and hasattr(self, 'wordCount') and hasattr(self, 'status'):
            cur = self.editor.textCursor()
            self.lineCol.setText(f"Ln {cur.blockNumber()+1}, Col {cur.columnNumber()+1}")
            words = len(WORD_PATTERN.findall(self.editor.toPlainText()))
            self.wordCount.setText(f"Words: {words}")

    # --- Show Event ---
    def showEvent(self, event):
        """Handle window show event to ensure it fits on screen."""
        super().showEvent(event)
        
        # Set a flag to indicate we're in the initial show event
        # This will prevent manual resizes from being overridden
        self._in_initial_show = True
        
        # Ensure window fits on screen after a short delay
        # to allow the window to fully initialize
        QTimer.singleShot(200, self.ensure_window_fits_screen)
        
        # Ensure keyboard fits on screen, but only during initial startup
        QTimer.singleShot(300, lambda: self._initial_keyboard_check())
        
        # Clear the initial show flag after a delay
        QTimer.singleShot(1000, lambda: setattr(self, '_in_initial_show', False))
        
    def _initial_keyboard_check(self):
        """Perform initial keyboard size check during startup only."""
        # Only run the keyboard size check if we're in the initial show
        if hasattr(self, '_in_initial_show') and self._in_initial_show:
            self.ensure_keyboard_fits_screen()
            
            # After initial sizing, set the keyboard as manually sized
            # to prevent automatic resizing from changing it
            self._manual_resize = True
            
            # Clear the manual resize flag after a delay
            QTimer.singleShot(1000, lambda: setattr(self, '_manual_resize', False))
    
    # --- Resize Event ---
    def resizeEvent(self, event):
        """Handle window resize events."""
        # Store the old size before calling the parent's resizeEvent
        old_size = event.oldSize()
        
        # Call the parent's resizeEvent
        super().resizeEvent(event)
        
        # Update suggestion popup position if it's visible
        if hasattr(self, 'suggestion_popup') and self.suggestion_popup.isVisible():
            self.update_suggestion_popup_position()
        
        # Only update keyboard if the width changed, not the height
        # This prevents resize loops when the keyboard itself is being resized
        if hasattr(self, 'keyboard_area') and old_size.width() != self.width():
            try:
                # Set a flag to indicate we're in a programmatic resize
                if not hasattr(self, '_in_resize'):
                    self._in_resize = True
                    
                    # Update the keyboard buttons to match the new window size
                    if hasattr(self.keyboard_area, 'update_buttons'):
                        self.keyboard_area.update_buttons()
                    
                    # Clear the flag
                    self._in_resize = False
            except Exception as e:
                logger.error(f"Error updating keyboard in resize event: {e}")
                self._in_resize = False
    
    # --- Close Event ---
    def closeEvent(self, event):
        """Handle application close event."""
        # Check for unsaved changes
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, 
                "Save Changes?",
                "Do you want to save changes before exiting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Yes:
                if not self.save_file():
                    # If save failed and user canceled, don't close
                    event.ignore()
                    return

        # Commit any pending buffer
        self.commit_buffer()

        # Save user dictionary
        self._save_map(force=True)

        # Save window size in preferences
        self.preferences["window_size"] = (self.width(), self.height())

        # Save font settings
        self.preferences["font"] = self.base_font.family()
        self.preferences["font_size"] = self.base_font.pointSize()

        # Save feature states
        self.preferences["show_keyboard"] = self.keyboard_area.isVisible()
        self.preferences["show_suggestions"] = self.suggestions_toggle_action.isChecked()
        self.preferences["singlish_enabled"] = self.singlish_toggle_action.isChecked()

        # Save all preferences
        config.save_user_preferences(self.preferences)
        logger.info("User preferences saved")

        # Remove event filter to prevent memory leaks
        self.editor.removeEventFilter(self)

        # Accept the close event
        event.accept()

    def _load_dictionaries(self):
        """Loads the main lexicon and user-defined dictionary."""
        logger.info("Loading dictionaries...")
        try:
            # Load user map
            if os.path.exists(self.USER_MAP_FP):
                try:
                    with open(self.USER_MAP_FP, "r", encoding="utf8") as f:
                        self.USER_MAP = json.load(f)
                    logger.info(f"Loaded user map from {os.path.basename(self.USER_MAP_FP)}")
                except (IOError, json.JSONDecodeError) as e:
                    logger.error(f"Error loading user map: {e}")
                    QMessageBox.warning(self, "Warning", f"Could not load user dictionary: {e}")
                    self.USER_MAP = {}
            else:
                self.USER_MAP = {}
                logger.info(f"User map file not found at {os.path.basename(self.USER_MAP_FP)}. Starting with empty user map.")

            # Load main lexicon chunks
            self.MAIN_LEXICON = {}
            if os.path.exists(config.LEXICON_DIR):
                for filename in os.listdir(config.LEXICON_DIR):
                    if filename.endswith(".json.gz"):
                        filepath = os.path.join(config.LEXICON_DIR, filename)
                        try:
                            with gzip.open(filepath, "rt", encoding="utf8") as f:
                                chunk = json.load(f)
                                self.MAIN_LEXICON.update(chunk)
                            logger.info(f"Loaded lexicon chunk: {filename}")
                        except Exception as e:
                            logger.error(f"Error loading lexicon chunk {filename}: {e}")
            else:
                logger.warning(f"Lexicon chunks directory not found at {os.path.basename(config.LEXICON_DIR)}. Main lexicon will be empty.")

            # Combine user map and main lexicon for quick lookup
            self.MAP = {**self.MAIN_LEXICON, **self.USER_MAP}
            logger.info(f"Total entries loaded: {len(self.MAP)}")

        except Exception as e:
            logger.error(f"An error occurred during dictionary loading: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load dictionaries: {e}")
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self, self.preferences)
        dialog.settingsApplied.connect(self.apply_settings)
        if dialog.exec():
            logger.info("Settings applied")
    
    def apply_settings(self, settings):
        """Apply settings from the settings dialog."""
        # Update preferences
        for key, value in settings.items():
            self.preferences[key] = value
        
        # Save preferences
        config.save_user_preferences(self.preferences)
        
        # Apply font settings
        self.base_font = QFont(
            self.preferences["font"], 
            self.preferences["font_size"]
        )
        # Use PreferMatch to allow system fonts for English characters
        self.base_font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
        self.editor.setFont(self.base_font)
        
        # Apply keyboard settings - rewritten with consistent indentation
        if hasattr(self.keyboard_area, 'set_font_size'):
            # Use the proper method to update font size
            self.keyboard_area.set_font_size(self.preferences["keyboard_font_size"])
        else:
            # Fallback to direct property setting
            self.keyboard_area.font_size = self.preferences["keyboard_font_size"]
            self.keyboard_area.update_theme()  # This will update the button styles
        
        # Apply keyboard visibility
        if self.preferences["show_keyboard"]:
            self.keyboard_container.show()
            self.keyboard_area.show()
        else:
            self.keyboard_container.hide()
            self.keyboard_area.hide()
        
        # Update toggle actions
        self.singlish_toggle_action.setChecked(self.preferences["singlish_enabled"])
        self.singlish_toggle_action.setText("Singlish: On" if self.preferences["singlish_enabled"] else "Singlish: Off")
        
        self.suggestions_toggle_action.setChecked(self.preferences["show_suggestions"])
        self.suggestions_toggle_action.setText("Suggestions: On" if self.preferences["show_suggestions"] else "Suggestions: Off")
        
        self.keyboard_toggle_action.setChecked(self.preferences["show_keyboard"])
        
        logger.info("Settings applied successfully")


# ------------------------------------------------------------------
#  Main function
# ------------------------------------------------------------------
def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application-wide font policy to allow system fonts for English text
    default_font = QFont()
    default_font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
    QApplication.setFont(default_font)

    # Create and show the main window
    win = SinhalaWordApp()

    # Set window size from preferences
    prefs = config.load_user_preferences()
    width, height = prefs["window_size"]
    win.resize(width, height)

    # Show the window
    win.show()

    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
