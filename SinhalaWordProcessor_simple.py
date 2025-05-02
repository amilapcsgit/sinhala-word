# Sinhala Word Processor — PySide6 (v3.3 - Enhanced)
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
python SinhalaWordProcessor_enhanced.py
```

Pack as EXE:
```bash
pyinstaller --noconfirm --onefile --add-data "sinhalawordmap.json;." --add-data "dictionary;dictionary" SinhalaWordProcessor_enhanced.py
```
"""
import sys
import os
import json
import re
import gzip
import logging
from PySide6.QtWidgets import (
    QApplication, QTextEdit, QFileDialog, QToolBar, QWidget, QVBoxLayout,
    QFontComboBox, QComboBox, QMessageBox, QStatusBar, QLabel, 
    QFrame, QInputDialog, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy,
    QStyledItemDelegate
)
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QAction, QIcon, QFontDatabase, QFontDatabase, QFontDatabase
from PySide6.QtCore import Qt, QPoint, QTimer, QEvent, Slot, QSize, QObject

# Import our custom modules
from pyside_keyboard import SinhalaKeyboard
from theme_manager import ThemeManager
import config
from transliterator import SinhalaTransliterator
from spellchecker import SinhalaSpellChecker
from input_handler import SinhalaInputHandler

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
        # Ensure text is centered and properly sized
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)

# Path to the fonts directory - use absolute path to ensure it works correctly
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

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
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    font_families.extend(families)
                    logging.info(f"Loaded font: {font_file} - Families: {', '.join(families)}")
                else:
                    logging.error(f"Failed to load font: {font_file}")
    else:
        logging.error(f"Fonts directory not found: {FONTS_DIR}")
    
    # Log all available font families for debugging
    all_fonts = QFontDatabase.families()
    logging.info(f"All available font families: {', '.join(all_fonts)}")
    
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
    def __init__(self):
        # --- Load User Preferences ---
        self.preferences = config.load_user_preferences()

        # --- Load Sinhala Fonts ---
        self.sinhala_font_families = load_sinhala_fonts()
        font_name = self.preferences["font"]
        font_size = self.preferences["font_size"]
        
        # If we have Sinhala fonts loaded, prefer those
        if self.sinhala_font_families and font_name not in self.sinhala_font_families:
            # Use the first available Sinhala font if preferred font not in our loaded fonts
            if self.sinhala_font_families:
                font_name = self.sinhala_font_families[0]
                # Update preferences
                self.preferences["font"] = font_name
                logging.info(f"Using Sinhala font: {font_name}")
        
        # Create the font
        self.base_font = QFont(font_name, font_size)
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

        # --- Suggestion Area (Fixed) ---
        self.suggestion_area = QTextEdit(self)
        self.suggestion_area.setReadOnly(True)
        self.suggestion_area.setFixedHeight(50) # Adjust height as needed
        self.suggestion_area.setFont(self.base_font) # Use same font

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

        # --- On-screen Keyboard Area ---
        # Create the Sinhala keyboard using our custom implementation with dark mode support
        # Initialize with dark mode based on current theme
        is_dark_mode = self.theme_manager.is_dark_mode()
        self.keyboard_area = SinhalaKeyboard(parent=self, dark_mode=is_dark_mode)
        self.keyboard_area.keyPressed.connect(self.on_keyboard_button_clicked)
        # Show keyboard based on preferences
        if self.preferences["show_keyboard"]:
            self.keyboard_area.show()
        else:
            self.keyboard_area.hide()

        # Apply initial theme
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        
        # Update combo box styles based on theme
        self.update_combo_box_styles()

        # --- Finalize UI Setup ---
        # Create a central widget and layout to hold the editor and suggestion area
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.suggestion_area) # Add suggestion area above editor
        main_layout.addWidget(self.editor)

        # Add keyboard area with fixed height
        keyboard_container = QWidget()
        keyboard_container.setFixedHeight(220)  # Fixed height for keyboard
        keyboard_layout = QVBoxLayout(keyboard_container)
        keyboard_layout.addWidget(self.keyboard_area)
        keyboard_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(keyboard_container)

        main_layout.setContentsMargins(0, 0, 0, 0) # Remove margins
        main_layout.setSpacing(2)  # Reduce spacing between widgets

        # Set the central widget
        self.setCentralWidget(central_widget)

        # Install event filter *after* editor exists and super().__init__ is done
        # Install event filter directly on the editor widget
        self.editor.installEventFilter(self)
        # Connect textChanged to update_status and update_suggestion_list
        self.editor.textChanged.connect(self.on_text_changed)
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
        except Exception as e:
            logger.error(f"Error in on_keyboard_button_clicked: {e}")
            # Clear state on error
            self.reset_input_state()

    def create_icon(self, name):
        """Create an icon for toolbar buttons using pyside_icons.py"""
        try:
            # Import the get_toolbar_icon function from pyside_icons.py
            from pyside_icons import get_toolbar_icon
            return get_toolbar_icon(name)
        except (ImportError, AttributeError):
            # Fallback if pyside_icons.py is not available or function not found
            return None

    def build_shortcuts(self):
        """Sets up keyboard shortcuts for common actions."""
        # File actions
        self.new_action = QAction("New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        self.new_action.setIcon(self.create_icon("new"))

        self.open_action = QAction("Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setIcon(self.create_icon("open"))

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setIcon(self.create_icon("save"))

        # Edit actions
        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self.editor.cut)
        self.cut_action.setIcon(self.create_icon("cut"))

        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.editor.copy)
        self.copy_action.setIcon(self.create_icon("copy"))

        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.editor.paste)
        self.paste_action.setIcon(self.create_icon("paste"))

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.editor.undo)
        self.undo_action.setIcon(self.create_icon("undo"))

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.editor.redo)
        self.redo_action.setIcon(self.create_icon("redo"))

        # View actions
        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.setShortcut("Ctrl+T")
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        self.toggle_theme_action.setIcon(self.create_icon("theme"))

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

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        # Use the theme manager to toggle theme and get the new stylesheet
        theme, stylesheet = self.theme_manager.toggle_theme()

        # Update the theme label
        if theme == "dark":
            self.themeLbl.setText("🌙 Dark")
            # Set dark mode for the keyboard
            self.keyboard_area.set_dark_mode(True)
        else:
            self.themeLbl.setText("☀️ Light")
            # Set light mode for the keyboard
            self.keyboard_area.set_dark_mode(False)

        # Apply the stylesheet
        self.setStyleSheet(stylesheet)

        # Save the theme preference
        self.preferences["theme"] = theme
        config.save_user_preferences(self.preferences)

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
        if self.keyboard_area.isVisible():
            self.keyboard_area.hide()
            if hasattr(self, 'keyboard_toggle_action'):
                # Keep the text as "Sinhala Keyboard" but update checked state
                self.keyboard_toggle_action.setChecked(False)
            # Update preferences
            self.preferences["show_keyboard"] = False
        else:
            self.keyboard_area.show()
            if hasattr(self, 'keyboard_toggle_action'):
                # Keep the text as "Sinhala Keyboard" but update checked state
                self.keyboard_toggle_action.setChecked(True)
            # Update preferences
            self.preferences["show_keyboard"] = True

        # Save preferences
        config.save_user_preferences(self.preferences)
        
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
            # Show suggestion area if there are suggestions
            if self.buffer:
                self.update_suggestion_area()
            self.preferences["show_suggestions"] = True
        else:
            self.suggestions_toggle_action.setText("Suggestions: Off")
            # Hide suggestion area
            self.clear_suggestion_area()
            self.preferences["show_suggestions"] = False

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
        self.size_combo.setMinimumWidth(70)  # Ensure enough width to display numbers
        self.size_combo.setMaxVisibleItems(10)  # Limit visible items to prevent excessive scrolling
        self.size_combo.setMaxCount(len(config.FONT_SIZES))  # Limit total items
        
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
            }
            QComboBox::item {
                padding: 3px;
            }
        """)
        
        # Apply custom delegate for better rendering
        self.size_combo.setItemDelegate(FontSizeDelegate(self.size_combo))

        # Connect size change signals
        self.size_combo.currentTextChanged.connect(self.change_font_size)
        self.formatting_toolbar.addWidget(self.size_combo)

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
        """Change the font size of the editor."""
        try:
            # Convert the size text to an integer
            size = int(size_text)
            
            # Update the font
            self.base_font.setPointSize(size)
            self.editor.setFont(self.base_font)
            self.suggestion_area.setFont(self.base_font)
            
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
        """Change the font family of the editor."""
        # Update the font
        self.base_font.setFamily(font_name)
        self.editor.setFont(self.base_font)
        self.suggestion_area.setFont(self.base_font)
        
        # Update preferences
        self.preferences["font"] = font_name
        config.save_user_preferences(self.preferences)
        
        # Log the change
        logging.info(f"Font family changed to {font_name}")
        
    def update_combo_box_styles(self):
        """Update combo box styles based on current theme."""
        is_dark = self.theme_manager.is_dark_mode()
        
        # Define colors based on theme
        if is_dark:
            dropdown_bg = "#444444"
            dropdown_fg = "#FFFFFF"
            dropdown_border = "#666666"
            selection_bg = "#264F78"
            selection_fg = "#FFFFFF"
        else:
            dropdown_bg = "#FFFFFF"
            dropdown_fg = "#333333"
            dropdown_border = "#CCCCCC"
            selection_bg = "#E2E2E2"
            selection_fg = "#333333"
        
        # Apply styles to font size combo box
        if hasattr(self, 'size_combo'):
            self.size_combo.setStyleSheet(f"""
                QComboBox {{ 
                    background-color: {dropdown_bg};
                    color: {dropdown_fg};
                    border: 1px solid {dropdown_border};
                    padding-right: 15px;
                    padding-left: 5px;
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
            """)
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        # Toggle theme using theme manager
        theme, stylesheet = self.theme_manager.toggle_theme()
        
        # Update application stylesheet
        self.setStyleSheet(stylesheet)
        
        # Update theme label in status bar
        self.themeLbl.setText("🌙 Dark" if theme == "dark" else "☀️ Light")
        
        # Update keyboard theme
        self.keyboard_area.set_dark_mode(theme == "dark")
        
        # Update combo box styles
        self.update_combo_box_styles()
        
        # Update preferences
        self.preferences["theme"] = theme
        config.save_user_preferences(self.preferences)
        
        # Log theme change
        logging.info(f"Theme changed to {theme}")

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

        # Add toggle suggestions action
        view_menu.addAction(self.suggestions_toggle_action)

        # Add toggle Singlish action
        view_menu.addAction(self.singlish_toggle_action)

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

            # If suggestion area is visible, handle selection keys
            if suggestions_enabled and self.suggestion_area.isVisible() and self.current_suggestions:
                if key in (Qt.Key_Return, Qt.Key_Enter):
                    # Accept the first suggestion on Enter
                    try:
                        # Make a local copy of the suggestion to avoid race conditions
                        suggestion = self.current_suggestions[0]
                        # Clear suggestions first to avoid race conditions
                        self.clear_suggestion_area()
                        # Clear buffer before accepting suggestion
                        self.buffer.clear()
                        # Now replace the text
                        self.replace_with_suggestion(suggestion)
                        return True # Consume Enter
                    except Exception as e:
                        logger.error(f"Error handling Enter key: {e}")
                        self.reset_input_state()
                        return False
                        
                elif key == Qt.Key_Space:
                    try:
                        # Accept the first suggestion on Space and insert a space
                        # This matches the behavior in SinhalaWordProcessor_enhanced.py
                        if self.current_suggestions:
                            self.accept_suggestion(self.current_suggestions[0])
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
                    
                elif Qt.Key_1 <= key <= Qt.Key_9:
                    index = key - Qt.Key_1
                    if index < len(self.current_suggestions):
                        try:
                            # Make a local copy of the suggestion to avoid race conditions
                            suggestion = self.current_suggestions[index]
                            # Clear suggestions first to avoid race conditions
                            self.clear_suggestion_area()
                            # Clear buffer before accepting suggestion
                            self.buffer.clear()
                            # Now replace the text
                            self.replace_with_suggestion(suggestion)
                            return True # Consume number key
                        except Exception as e:
                            logger.error(f"Error handling number key: {e}")
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
                            QTimer.singleShot(10, self.update_suggestion_area)
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
                if not self.buffer: # If buffer was empty, mark the start position
                     self.word_start_pos = self.editor.textCursor().position()
                self.buffer.append(text)
                # Do NOT consume the event, let the editor insert the character
                if suggestions_enabled:
                    QTimer.singleShot(10, self.update_suggestion_area) # Use singleShot to allow editor to process keypress
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
        self.buffer.clear()
        self.word_start_pos = None
        self.clear_suggestion_area()
        
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
        """Update and show/hide the fixed suggestion area based on the current buffer."""
        try:
            # Check if suggestions are enabled
            if hasattr(self, 'suggestions_toggle_action') and not self.suggestions_toggle_action.isChecked():
                self.clear_suggestion_area()
                return
                
            # If buffer is empty, clear suggestions
            if not self.buffer:
                self.clear_suggestion_area()
                return
                
            current_word = "".join(self.buffer).lower()
            
            # Use the transliterator to get suggestions
            self.current_suggestions = self.transliterator.get_suggestions(current_word, max_suggestions=9)
            
            # Log the suggestions for debugging
            logger.info(f"Suggestions for '{current_word}': {self.current_suggestions}")

            if self.current_suggestions:
                suggestion_text = " ".join([f"{i+1}. {suggestion}" for i, suggestion in enumerate(self.current_suggestions)])
                self.suggestion_area.setPlainText(suggestion_text)
                self.suggestion_area.show()
            else:
                self.clear_suggestion_area()
        except Exception as e:
            logger.error(f"Error in update_suggestion_area: {e}")
            self.clear_suggestion_area()

    def clear_suggestion_area(self):
        """Clear the fixed suggestion area content."""
        self.suggestion_area.setPlainText("") # Clear text content
        self.current_suggestions = [] # Clear stored suggestions

    def accept_suggestion(self, sinhala_word):
        """Accept a suggestion and replace the buffered text."""
        # This matches the behavior in SinhalaWordProcessor_enhanced.py
        if self.buffer and self.word_start_pos is not None:
            try:
                cur = self.editor.textCursor()
                cur.beginEditBlock()

                # Move cursor to the start of the buffered word
                cur.setPosition(self.word_start_pos)
                # Select the buffered text
                cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len("".join(self.buffer)))
                # Remove the buffered text
                cur.removeSelectedText()
                # Insert the accepted Sinhala word
                cur.insertText(sinhala_word)
                cur.endEditBlock()

                # Clear the buffer and reset word_start_pos
                self.buffer.clear()
                self.word_start_pos = None
                
                # Clear area after accepting
                self.clear_suggestion_area()
            except Exception as e:
                logger.error(f"Error in accept_suggestion: {e}")
                # If there's an error, at least clear the buffer and suggestion area
                self.buffer.clear()
                self.word_start_pos = None
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


# ------------------------------------------------------------------
#  Main function
# ------------------------------------------------------------------
def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Create QApplication
    app = QApplication(sys.argv)

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