# Sinhala Word Processor — PySide6 (v3.2 - Refactored)
"""
A lightweight **Word‑2000‑style** editor refreshed with Windows‑11 Fluent UI:

• **Realtime Singlish → Sinhala** (Buffer-based input like Sintip)
• **Suggestion popup** (up to 9 matches, Tab/1-9/Click to accept)
• **Basic spell‑checker** — unknown Sinhala words are underlined red
• **Two classic toolbars** (Standard & Formatting) ‑or‑ hide them and use the menu
• **Dark / Light theme toggle** (View → Toggle Theme) - Basic implementation
• Plain‑text load/save functionality.

Install dependencies:
```bash
pip install PySide6 PySide6-Fluent-Widgets
```

Run:
```bash
python SinhalaWordProcessor.py
```

Pack as EXE:
```bash
pyinstaller --noconfirm --onefile --add-data "sinhalawordmap.json;." --add-data "dictionary;dictionary" SinhalaWordProcessor.py
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
    QFrame, QInputDialog, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QAction, QIcon
from PySide6.QtCore import Qt, QPoint, QTimer, QEvent, Slot, QSize, QObject

# Import our custom keyboard implementation
from pyside_keyboard import SinhalaKeyboard

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SinhalaWordProcessor")

# ------------------------------------------------------------------
#  Constants & Global Helpers
# ------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON_CHUNKS_DIR = os.path.join(HERE, "dictionary", "chunks")
USER_MAP_FP_DEFAULT = os.path.join(HERE, "sinhalawordmap.json")
WORD_PATTERN = re.compile(r'\b\w+\b')  # Compiled regex for word counting

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
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # --- Create QApplication FIRST ---
    app = QApplication(sys.argv)

    # ------------------------------------------------------------------
    #  Main window class (defined inside main block)
    # ------------------------------------------------------------------
    class SinhalaWordApp(QMainWindow):
        """
        SinhalaWordApp: Main application class for the Sinhala Word Processor.

        Features:
        - Realtime Singlish to Sinhala transliteration.
        - Suggestion popup (up to 9 matches, Tab/1-9/Click to accept)
        - Basic spell‑checker — unknown Sinhala words are underlined red
        - Two classic toolbars (Standard & Formatting) ‑or‑ hide them and use the menu
        - Dark / Light theme toggle (View → Toggle Theme) - Basic implementation
        - Plain‑text load/save functionality.

        Methods:
        - __init__: Initializes the application and sets up the UI.
        - _load_dictionaries: Loads the main lexicon and user-defined dictionary.
        - build_shortcuts: Sets up keyboard shortcuts for common actions.
        - build_menu: Creates the application menu.
        - build_toolbars: Creates toolbars for standard and formatting actions.
        - open_file: Opens a plain-text file in the editor.
        - save_file: Saves the current editor content to a plain-text file.
        - add_to_dict: Adds a selected Sinhala word to the user dictionary.
        - toggle_theme: Toggles between light and dark themes.
        - spell_check_word: Underlines unknown Sinhala words in the editor.
        - suggestions: Provides transliteration suggestions for a given prefix.
        - commit_buffer: Commits the buffered input to the editor.
        - accept_suggestion_singlish: Accepts a transliteration suggestion (now handles inline replacement).
        - refresh_suggestions: Updates the inline suggestion based on the buffer.
        - update_status: Updates the status bar with line, column, and word count.
        - closeEvent: Handles application close events, saving the user dictionary.
        """
        def __init__(self):
            # --- Initialize Core Attributes FIRST ---
            self.MAIN_LEXICON = {}
            self.USER_MAP = {}
            self.MAP = {}
            self.USER_MAP_FP = USER_MAP_FP_DEFAULT
            self.SAVE_PENDING = False

            # --- Suggestion State ---
            self.buffer = []
            self.word_start_pos = None # Position in the document where the current word started
            # Removed inline suggestion attributes
            self.current_suggestions = [] # Store current suggestions for fixed area

            # --- Create Core Widgets ---
            self.editor = QTextEdit()
            self.base_font = QFont("Iskoola Pota", 14)
            self.editor.setFont(self.base_font)

            # --- Call Superclass Initializer ---
            super().__init__()

            # --- Suggestion Area (Fixed) ---
            self.suggestion_area = QTextEdit(self)
            self.suggestion_area.setReadOnly(True)
            self.suggestion_area.setFixedHeight(50) # Adjust height as needed
            self.suggestion_area.setFont(self.base_font) # Use same font
            # self.suggestion_area.hide() # Hide initially - Keep visible


            # --- Basic Window Setup ---
            self.setWindowTitle("Sinhala Word Processor")
            self.resize(1100, 780)

            # --- Load Dictionaries ---
            self._load_dictionaries() # Call load method

            # --- On-screen Keyboard Area ---
            # Create the Sinhala keyboard using our custom implementation with dark mode support
            # Initialize with dark mode based on current theme
            is_dark_mode = self.themeLbl.text() == "🌙 Dark" if hasattr(self, 'themeLbl') else False
            self.keyboard_area = SinhalaKeyboard(parent=self, dark_mode=is_dark_mode)
            self.keyboard_area.keyPressed.connect(self.on_keyboard_button_clicked)
            # Show keyboard by default
            self.keyboard_area.show()

            # --- Finalize UI Setup ---
            # Create a central widget and layout to hold the editor and suggestion area
            central_widget = QWidget()
            main_layout = QVBoxLayout(central_widget)
            main_layout.addWidget(self.suggestion_area) # Add suggestion area above editor
            main_layout.addWidget(self.editor)
            main_layout.addWidget(self.keyboard_area) # Add keyboard area below editor
            main_layout.setContentsMargins(0, 0, 0, 0) # Remove margins

            # Set the central widget
            self.setCentralWidget(central_widget)

            # Status Bar for QMainWindow
            self.status = self.statusBar()
            self.lineCol = QLabel("Ln 1, Col 1")
            self.wordCount = QLabel("Words: 0")
            self.themeLbl = QLabel("☀️ Light")
            self.status.addPermanentWidget(self.lineCol)
            self.status.addPermanentWidget(self.wordCount)
            self.status.addPermanentWidget(self.themeLbl)

            self.build_shortcuts()  # Add this call to initialize shortcuts

            # Install event filter *after* editor exists and super().__init__ is done
            # Install event filter directly on the editor widget
            self.editor.installEventFilter(self)
            # Connect textChanged to update_status and update_suggestion_list
            self.editor.textChanged.connect(self.on_text_changed)
            # Add context menu support
            self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
            self.editor.customContextMenuRequested.connect(self.show_context_menu)
            # Update suggestion list is now triggered by keypress handling


            # --- Build Menus/Toolbars ---
            self.build_menu()
            self.build_toolbars()
            self.update_status() # Initial status

        def show_context_menu(self, position):
            """Show right-click context menu."""
            menu = self.editor.createStandardContextMenu()
            
            # Add separator and custom actions
            menu.addSeparator()
            
            # Add "Learn Selected Word" action
            learn_action = QAction("Learn Selected Word", self)
            learn_action.triggered.connect(self.learn_selected_word)
            menu.addAction(learn_action)
            
            # Show the menu at the cursor position
            menu.exec_(self.editor.mapToGlobal(position))
            
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
                        # Mark for saving
                        self.SAVE_PENDING = True
                        # Save immediately
                        self._save_map()
                        QMessageBox.information(self, "Success", "Word added to dictionary")
                else:
                    QMessageBox.warning(self, "Warning", "Please select a Sinhala word")
            else:
                QMessageBox.warning(self, "Warning", "Please select a word first")
                
        def on_keyboard_button_clicked(self, char):
            """Handles clicks on the on-screen keyboard buttons."""
            if char == "Space":
                self.editor.insertPlainText(" ")
            elif char == "Backspace":
                self.editor.textCursor().deletePreviousChar()
            else:
                self.editor.insertPlainText(char)


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
            if self.themeLbl.text() == "☀️ Light":
                self.themeLbl.setText("🌙 Dark")
                # Set dark mode for the keyboard
                self.keyboard_area.set_dark_mode(True)
                
                # Enhanced dark theme with better styling
                self.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #2E2E2E;
                        color: #FFFFFF;
                    }
                    QTextEdit {
                        background-color: #3A3A3A;
                        color: #FFFFFF;
                        border: 1px solid #555555;
                    }
                    QMenuBar, QMenu {
                        background-color: #2E2E2E;
                        color: #FFFFFF;
                    }
                    QToolBar {
                        background-color: #333333;
                        border: 1px solid #555555;
                    }
                    QPushButton {
                        background-color: #444444;
                        color: #FFFFFF;
                        border: 1px solid #666666;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #555555;
                    }
                    QComboBox, QFontComboBox {
                        background-color: #444444;
                        color: #FFFFFF;
                        border: 1px solid #666666;
                    }
                    QStatusBar {
                        background-color: #333333;
                        color: #FFFFFF;
                    }
                """)
            else:
                self.themeLbl.setText("☀️ Light")
                # Set light mode for the keyboard
                self.keyboard_area.set_dark_mode(False)
                
                # Revert to light theme with some basic styling
                self.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #F5F5F5;
                        color: #333333;
                    }
                    QTextEdit {
                        background-color: #FFFFFF;
                        color: #333333;
                        border: 1px solid #CCCCCC;
                    }
                    QToolBar {
                        background-color: #F0F0F0;
                        border: 1px solid #DDDDDD;
                    }
                    QPushButton {
                        background-color: #E0E0E0;
                        color: #333333;
                        border: 1px solid #CCCCCC;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #D0D0D0;
                    }
                """)

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
            else:
                self.keyboard_area.show()
                if hasattr(self, 'keyboard_toggle_action'):
                    # Keep the text as "Sinhala Keyboard" but update checked state
                    self.keyboard_toggle_action.setChecked(True)
                    
        def toggle_singlish(self):
            """Toggle Singlish transliteration."""
            # Update action text based on checked state
            if self.singlish_toggle_action.isChecked():
                self.singlish_toggle_action.setText("Singlish: On")
                # Enable Singlish functionality
                # No need to do anything else as the event filter will handle it
            else:
                self.singlish_toggle_action.setText("Singlish: Off")
                # Clear any pending buffer
                self.buffer.clear()
                self.word_start_pos = None
                self.clear_suggestion_area()
                
        def toggle_suggestions(self):
            """Toggle suggestions display."""
            # Update action text based on checked state
            if self.suggestions_toggle_action.isChecked():
                self.suggestions_toggle_action.setText("Suggestions: On")
                # Show suggestion area if there are suggestions
                if self.buffer:
                    self.update_suggestion_area()
            else:
                self.suggestions_toggle_action.setText("Suggestions: Off")
                # Hide suggestion area
                self.clear_suggestion_area()
                    
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

            # Font Family ComboBox
            font_combo = QFontComboBox(self)
            font_combo.currentFontChanged.connect(self.editor.setCurrentFont)
            self.formatting_toolbar.addWidget(font_combo)

            # Font Size ComboBox
            size_combo = QComboBox(self)
            size_combo.setEditable(True)
            # Populate with common font sizes
            sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
            size_combo.addItems([str(s) for s in sizes])
            # Set default size
            default_size_index = sizes.index(self.base_font.pointSize()) if self.base_font.pointSize() in sizes else -1
            if default_size_index != -1:
                 size_combo.setCurrentIndex(default_size_index)
            else:
                 size_combo.setCurrentText(str(self.base_font.pointSize()))

            size_combo.currentIndexChanged.connect(lambda index: self.editor.setFontPointSize(float(size_combo.currentText())))
            size_combo.editTextChanged.connect(lambda text: self.editor.setFontPointSize(float(text) if text else self.base_font.pointSize())) # Handle empty input
            self.formatting_toolbar.addWidget(size_combo)

            # Add other formatting actions here (Bold, Italic, Underline, etc.) if needed later
            # For now, just font and size.

            # --- Feature Toggles Toolbar ---
            self.toggles_toolbar = self.addToolBar("Features")
            self.toggles_toolbar.setObjectName("FeaturesToolbar")

            # Toggle Actions (initially unchecked, will need logic to manage state)
            self.singlish_toggle_action = QAction("Singlish: On", self, checkable=True)
            self.singlish_toggle_action.setChecked(True) # Assuming Singlish is on by default
            self.singlish_toggle_action.triggered.connect(self.toggle_singlish)
            
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
            keyboard_btn.setChecked(True)
            keyboard_btn.setToolTip("Toggle Sinhala Keyboard")
            
            # Create the label
            keyboard_label = QLabel("Keyboard")
            keyboard_label.setStyleSheet("font-size: 12px;")
            
            # Add to layout
            keyboard_layout.addWidget(keyboard_btn)
            keyboard_layout.addWidget(keyboard_label)
            
            # Connect the button to toggle_keyboard
            keyboard_btn.clicked.connect(self.toggle_keyboard)
            
            # Create the action for menu
            self.keyboard_toggle_action = QAction("Sinhala Keyboard", self, checkable=True)
            self.keyboard_toggle_action.setChecked(True) # Keyboard is on by default
            self.keyboard_toggle_action.triggered.connect(self.toggle_keyboard)
            self.keyboard_toggle_action.setIcon(self.create_icon("keyboard"))

            self.suggestions_toggle_action = QAction("Suggestions: On", self, checkable=True)
            self.suggestions_toggle_action.setChecked(True) # Assuming Suggestions are on by default
            self.suggestions_toggle_action.triggered.connect(self.toggle_suggestions)

            self.toggles_toolbar.addAction(self.singlish_toggle_action)
            self.toggles_toolbar.addWidget(keyboard_widget)  # Add our custom widget instead of the action
            self.toggles_toolbar.addAction(self.suggestions_toggle_action)
            self.toggles_toolbar.addSeparator()
            self.toggles_toolbar.addAction(self.toggle_theme_action)


        def build_menu(self):
            """Creates the application menu."""
            menu_bar = self.menuBar()

            # File Menu
            file_menu = menu_bar.addMenu("&File")
            # Use the actions stored as instance attributes
            file_menu.addAction(self.new_action)
            file_menu.addAction(self.open_action)
            file_menu.addAction(self.save_action)
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

        def new_file(self):
            """Create a new file."""
            # Ask to save changes if there's content in the editor
            if self.editor.toPlainText().strip():
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
            
        def open_file(self):
            """Opens a plain-text file in the editor."""
            # Ask to save changes if there's content in the editor
            if self.editor.toPlainText().strip():
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
            
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.editor.setPlainText(f.read())
                    print(f"Opened file: {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

        def save_file(self):
            """Saves the current editor content to a plain-text file."""
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(self.editor.toPlainText())
                    print(f"Saved file: {os.path.basename(file_path)}")
                    self.SAVE_PENDING = False # Reset save pending flag after successful save
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")


        # Removed hide_suggestion_list and accept_suggestion_from_list (QListWidget specific)

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
                        self.accept_suggestion(self.current_suggestions[0])
                        return True # Consume Enter
                    elif key == Qt.Key_Space:
                        # Accept the first suggestion on Space and insert a space
                        self.accept_suggestion(self.current_suggestions[0])
                        self.editor.insertPlainText(" ")
                        return True # Consume Space
                    elif key == Qt.Key_Escape:
                        self.clear_suggestion_area()
                        self.buffer.clear() # Clear buffer on escape
                        self.word_start_pos = None
                        return True # Consume Escape
                    elif Qt.Key_1 <= key <= Qt.Key_9:
                        index = key - Qt.Key_1
                        if index < len(self.current_suggestions):
                            # Accept the selected suggestion by number
                            self.accept_suggestion(self.current_suggestions[index])
                            return True # Consume number key
                    # Let other keys (like alphanumeric, backspace) fall through to modify buffer

                # If Backspace is pressed, handle buffer modification
                if key == Qt.Key_Backspace:
                    # If buffer is not empty, remove last char from buffer
                    if self.buffer:
                        self.buffer.pop()
                        # After popping, update or clear suggestion area
                        if suggestions_enabled:
                            QTimer.singleShot(0, self.update_suggestion_area)
                        # Do NOT consume backspace here, let the editor handle it
                        return False
                    else:
                        # If buffer is empty, let editor handle backspace normally
                        if suggestions_enabled:
                            self.clear_suggestion_area() # Ensure area is hidden if buffer becomes empty
                        self.word_start_pos = None # Explicitly reset word_start_pos
                        return False

                # Handle alphanumeric keys: append to buffer
                if event.text().isalnum() and len(event.text()) == 1:
                    if not self.buffer: # If buffer was empty, mark the start position
                         self.word_start_pos = self.editor.textCursor().position()
                    self.buffer.append(text)
                    # Do NOT consume the event, let the editor insert the character
                    if suggestions_enabled:
                        QTimer.singleShot(0, self.update_suggestion_area) # Use singleShot to allow editor to process keypress
                    return False

                # For any other key (punctuation, symbols, arrows, etc.), commit the current buffer
                # and then clear the suggestion area.
                self.commit_buffer()
                return False # Do not consume the event, let the editor handle it

            except Exception as e:
                print(f"ERROR: Exception in handle_keypress_event: {e}")  # Error log
                # Ensure area is hidden on error
                if hasattr(self, 'suggestions_toggle_action') and self.suggestions_toggle_action.isChecked():
                    self.clear_suggestion_area()
                return False

        def update_suggestion_area(self):
            """Update and show/hide the fixed suggestion area based on the current buffer."""
            # Check if suggestions are enabled
            if hasattr(self, 'suggestions_toggle_action') and not self.suggestions_toggle_action.isChecked():
                self.clear_suggestion_area()
                return
                
            current_word = "".join(self.buffer).lower()

            self.current_suggestions = self.suggestions(current_word, limit=9) # Get up to 9 suggestions

            if self.current_suggestions:
                suggestion_text = " ".join([f"{i+1}. {self.MAP.get(s, s)}" for i, s in enumerate(self.current_suggestions)])
                self.suggestion_area.setPlainText(suggestion_text)
                self.suggestion_area.show()
            else:
                self.clear_suggestion_area()

        def clear_suggestion_area(self):
            """Clear the fixed suggestion area content."""
            self.suggestion_area.setPlainText("") # Clear text content
            self.current_suggestions = [] # Clear stored suggestions
            # print("DEBUG: Suggestion area content cleared.") # Debug log

        def accept_suggestion(self, singlish_word):
            """Accept a suggestion and replace the buffered text."""
            # print(f"DEBUG: accept_suggestion called with singlish_word: {singlish_word}") # Debug log
            sinhala_word = self.MAP.get(singlish_word)
            if not sinhala_word:
                # Fallback to phonetic if somehow not in map (shouldn't happen with current logic)
                sinhala_word = _phonetic_global(singlish_word)
                # print(f"DEBUG: Fallback to phonetic for '{singlish_word}': '{sinhala_word}'") # Debug log


            if self.buffer and self.word_start_pos is not None:
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

            self.clear_suggestion_area() # Clear area after accepting
            # print("DEBUG: Suggestion accepted and committed.") # Debug log


        # Removed accept_suggestion_from_list (QListWidget specific)

        def commit_buffer(self):
            """Commit the buffered input to the editor (phonetic transliteration)."""
            # Check if Singlish is enabled
            singlish_enabled = hasattr(self, 'singlish_toggle_action') and self.singlish_toggle_action.isChecked()
            
            # Clear suggestion area regardless of Singlish state
            self.clear_suggestion_area()
            
            # If Singlish is disabled or buffer is empty, don't process
            if not singlish_enabled or not self.buffer or self.word_start_pos is None:
                return

            word = "".join(self.buffer)

            # Perform phonetic transliteration for the buffered word
            sinhala_word = _phonetic_global(word)

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

            # print("DEBUG: Buffer committed successfully.")  # Debug log - Reduced verbosity


        def eventFilter(self, obj, event):
            # Check if the event is for the editor
            if event.type() == QEvent.KeyPress and (obj is self.editor or obj is self.editor.viewport()):
                 # Pass the event and the object it occurred on to handle_keypress_event
                 return self.handle_keypress_event(obj, event)

            # For any other event or object, let the default event filter handle it
            return super().eventFilter(obj, event)

        @Slot() # Decorator to indicate this is a slot
        def on_text_changed(self):
            # print("DEBUG: on_text_changed called.") # Debug log - Reduced verbosity
            # The buffer is now managed by handle_keypress_event
            # This slot is mainly for updating the status bar
            self.update_status()
            # Update suggestion list is now triggered by keypress handling


        def suggestions(self, prefix: str, limit: int = 9):
            """Get a list of suggestions for a given prefix from the dictionary."""
            # This method is still needed for the phonetic fallback, but not for suggestions list
            pref = prefix.lower()
            # print(f"DEBUG: Entering suggestions. Prefix: '{pref}'") # Debug log
            if not pref:
                # print("DEBUG: Prefix is empty. Returning no suggestions.") # Debug log - Reduced verbosity
                return []

            results = []
            try:
                # Check user map first
                user_matches = [k for k in self.USER_MAP if k.startswith(pref)]
                results.extend(user_matches)

                # Then main lexicon, avoiding duplicates from user map
                main_matches = [k for k in self.MAIN_LEXICON if k.startswith(pref) and k not in self.USER_MAP]
                results.extend(main_matches)

                # Limit the number of results
                results = results[:limit]

            except Exception as e:
                print(f"DEBUG: Error while fetching suggestions: {e}")
                sys.stdout.flush()

            # print(f"DEBUG: Suggestions generated: {results}") # Debug log
            return results

        # --- Transliteration/Suggestion Methods ---
        def tr(self, word: str) -> str:
            return self.MAP.get(word.lower()) or _phonetic_global(word) # Use global phonetic

        # This method is no longer needed as suggestion list is removed
        # @Slot(QListWidgetItem)
        # def accept_suggestion_from_list(self, item):
        #     """Accept a suggestion selected from the list widget."""
        #     pass # No operation needed


        # --- Save Method ---
        def _save_map(self, force=False):
            if force or self.SAVE_PENDING:
                try:
                    with open(self.USER_MAP_FP, "w", encoding="utf8") as f:
                        json.dump(self.USER_MAP, f, ensure_ascii=False, indent=2)
                    self.SAVE_PENDING = False
                    print(f"User map saved to {os.path.basename(self.USER_MAP_FP)}")
                except Exception as e:
                    print(f"Error saving user map file: {e}")

        # --- Spell checker ---
        def spell_check_word(self, word):
            """Spell-check a Sinhala word and underline it if not found in the dictionary."""
            if not word:
                return

            is_sinhala = any("\u0D80" <= c <= "\u0DFF" for c in word)
            if is_sinhala and word not in self.MAP.values():
                fmt = QTextCharFormat()
                fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                fmt.setUnderlineColor("red") # Changed to string "red" for consistency

                cur = self.editor.textCursor()
                start_pos = cur.position() - len(word)
                cur.setPosition(start_pos)
                cur.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(word))
                cur.mergeCharFormat(fmt)
                cur.clearSelection()
                cur.setPosition(start_pos + len(word))
                self.editor.setTextCursor(cur)

        # --- Status update ---
        # Note: on_text_changed is already defined above, so this is removed to avoid duplication

        def update_status(self):
            # Check if status bar widgets exist before updating
            if hasattr(self, 'lineCol') and hasattr(self, 'wordCount') and hasattr(self, 'status'):
                cur = self.editor.textCursor()
                self.lineCol.setText(f"Ln {cur.blockNumber()+1}, Col {cur.columnNumber()+1}")
                words = len(re.findall(r'\b\w+\b', self.editor.toPlainText()))
                self.wordCount.setText(f"Words: {words}")

        # --- Close Event ---
        def closeEvent(self, event):
            self.commit_buffer()
            self._save_map(force=True)
            event.accept()

        def _load_dictionaries(self):
            """Loads the main lexicon and user-defined dictionary."""
            print("Loading dictionaries...")
            try:
                # Load user map
                if os.path.exists(self.USER_MAP_FP):
                    with open(self.USER_MAP_FP, "r", encoding="utf8") as f:
                        self.USER_MAP = json.load(f)
                    print(f"Loaded user map from {os.path.basename(self.USER_MAP_FP)}")
                else:
                    self.USER_MAP = {}
                    print(f"User map file not found at {os.path.basename(self.USER_MAP_FP)}. Starting with empty user map.")

                # Load main lexicon chunks
                self.MAIN_LEXICON = {}
                if os.path.exists(LEXICON_CHUNKS_DIR):
                    for filename in os.listdir(LEXICON_CHUNKS_DIR):
                        if filename.endswith(".json.gz"):
                            filepath = os.path.join(LEXICON_CHUNKS_DIR, filename)
                            try:
                                with gzip.open(filepath, "rt", encoding="utf8") as f:
                                    chunk = json.load(f)
                                    self.MAIN_LEXICON.update(chunk)
                                print(f"Loaded lexicon chunk: {filename}")
                            except Exception as e:
                                print(f"Error loading lexicon chunk {filename}: {e}")
                else:
                    print(f"Lexicon chunks directory not found at {os.path.basename(LEXICON_CHUNKS_DIR)}. Main lexicon will be empty.")

                # Combine user map and main lexicon for quick lookup
                self.MAP = {**self.MAIN_LEXICON, **self.USER_MAP}
                print(f"Total entries loaded: {len(self.MAP)}")

            except Exception as e:
                print(f"An error occurred during dictionary loading: {e}")


    # --- Create and run the app ---
    win = SinhalaWordApp()
    win.show()
    sys.exit(app.exec())
