import os
import logging
# Allow limited font fallbacks for better compatibility
# We'll handle font fallbacks more carefully in the code
os.environ["QT_ENABLE_FONT_FALLBACKS"] = "1"
os.environ["QT_FONT_NO_SYSTEM_FALLBACKS"] = "0"

# Set up module-specific logger
logger = logging.getLogger(__name__)

# Constants for font size limits
MIN_KB_FONT = 26  # Minimum keyboard font size (increased from 10 for better visibility)
MAX_KB_FONT = 200  # Maximum keyboard font size

# Standard base values for height/font calculations
BASE_KB_HEIGHT = 264  # Base keyboard height
BASE_KB_FONT = 26    # Base font size corresponding to the base height

from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, 
                          QSizePolicy, QDialog, QLabel, QGridLayout, QSplitter)
from PySide6.QtCore import Qt, Signal, QObject, QEvent, QSize
from PySide6.QtGui import QColor, QFont, QCursor, QResizeEvent, QFontDatabase

class SinhalaKeyboard(QFrame):
    """PySide6 implementation of the Sinhala Keyboard with resizing capability"""

    # Signal emitted when a key is pressed
    keyPressed = Signal(str)
    
    # Signal emitted when keyboard is resized
    keyboardResized = Signal(int)

    def __init__(self, parent=None, dark_mode=False, font_size=26):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.font_size = font_size
        self.keyboard_font_family = "Iskoola Pota"  # Default fallback
        self._manual_font_size = False  # Flag to prevent automatic font size adjustment when manually set
        
        # Initialize resize tracking variables
        self._last_resize_time = 0
        self._resize_count = 0
        self._last_emitted_height = 0
        
        # Default height for the keyboard
        self.default_height = 600  # Increased default height for better visibility
        
        # Track initial size for proportional resizing
        self.initial_size = None
        self.resize_in_progress = False
        self.resize_direction = None
        
        # Initialize grid_layout to None - will be created in create_keyboard
        self.grid_layout = None
        
        # Load the Sinhala font for the keyboard
        self.load_keyboard_font()
        
        # Log debug info
        logger.info(f"Keyboard initialized with font: {self.keyboard_font_family}, size: {self.font_size}")
        
        # Define keyboard layouts and other properties
        self.setup_keyboard_properties()
        
        # Enable mouse tracking for resize operations
        self.setMouseTracking(True)
        
        # Set minimum width for the keyboard (but not height to allow more flexibility)
        self.setMinimumWidth(400)
        
        # Set size policy to allow both horizontal and vertical resizing
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set the initial size to a reasonable default
        self.resize(800, self.default_height)
        
        # Create the keyboard UI - this will initialize the layout
        self.create_keyboard()
        
        # Apply initial styling based on theme - AFTER layout is created
        self.update_theme()
        
        # Set size policy to allow both horizontal and vertical resizing
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def load_keyboard_font(self):
        """Load Sinhala font for the keyboard buttons"""
        # Prioritized list of Sinhala fonts that are known to work well
        # Try both embedded and system fonts
        sinhala_fonts = ["UN-Ganganee", "Iskoola Pota", "Nirmala UI"]
        
        try:
            # First check if our embedded UN-Ganganee font is available
            # This should be loaded by the main application
            for font_name in sinhala_fonts:
                try:
                    # Check if font exists in the system
                    if QFontDatabase.hasFamily(font_name):
                        # Test if we can create a font with this family
                        test_font = QFont(font_name)
                        test_font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
                        
                        # If we get here, the font is usable
                        self.keyboard_font_family = font_name
                        print(f"Using Sinhala font for keyboard: {font_name}")
                        return
                except Exception as font_error:
                    print(f"Error testing font {font_name}: {font_error}")
                    continue
            
            # If we get here, none of the preferred fonts worked
            # Try to find any font with "Sinhala" in the name
            all_fonts = QFontDatabase.families()
            for font_name in all_fonts:
                if "sinhala" in font_name.lower() or "iskoola" in font_name.lower():
                    try:
                        test_font = QFont(font_name)
                        self.keyboard_font_family = font_name
                        print(f"Found alternative Sinhala font: {font_name}")
                        return
                    except:
                        continue
            
            # If no suitable Sinhala fonts found, use a simple fallback
            # that's guaranteed to work without causing OpenType errors
            print("No Sinhala fonts found, using default system font")
            # Use a system font that should be available on all systems
            self.keyboard_font_family = "Arial"
            
        except Exception as e:
            print(f"Error in load_keyboard_font: {e}")
            # Use a guaranteed system font as fallback
            self.keyboard_font_family = "Arial"

    def setup_keyboard_properties(self):
        """Define keyboard layouts and properties"""
        # Define keyboard layouts with simplified sections
        self.keys = {
            # Vowels section
            'vowels': ['අ', 'ආ', 'ඇ', 'ඈ', 'ඉ', 'ඊ', 'උ', 'ඌ', 'එ', 'ඒ', 'ඔ', 'ඕ'],

            # Consonants section (all Sinhala consonants)
            'consonants': ['ක', 'ඛ', 'ග', 'ඝ', 'ඟ', 'ච', 'ඡ', 'ජ', 'ඣ', 'ඤ', 'ඥ', 
                          'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ', 'ත', 'ථ', 'ද', 'ධ', 'න', 'ඳ',
                          'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ', 'ය', 'ර', 'ල', 'ව', 'ශ', 'ෂ',
                          'ස', 'හ', 'ළ', 'ෆ'],

            # Special characters and modifiers
            'special': ['ං', 'ඃ', '්', 'ා', 'ැ', 'ෑ', 'ි', 'ී', 'ු', 'ූ'],

            # Vowel modifiers for layout
            'modifiers': ['ු', 'ූ', 'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ']
        }

        # Define vowel groups for popups - only for අ
        self.vowel_groups = {
            'අ': ['අ', 'ආ', 'ඇ', 'ඈ']
        }

        # Define vowel modifiers for consonants
        self.vowel_modifiers = {
            '': '',      # No modifier (base consonant)
            'ා': 'ා',    # aa
            'ැ': 'ැ',    # ae
            'ෑ': 'ෑ',    # aae
            'ි': 'ි',    # i
            'ී': 'ී',    # ii
            'ු': 'ු',    # u
            'ූ': 'ූ',    # uu
            'ෘ': 'ෘ',    # ru
            'ෙ': 'ෙ',    # e
            'ේ': 'ේ',    # ee
            'ෛ': 'ෛ',    # ai
            'ො': 'ො',    # o
            'ෝ': 'ෝ',    # oo
            'ෞ': 'ෞ',    # au
            '්': '්'     # hal kirima
        }

        # Define letters that can have vowel modifiers
        self.consonants = [
            'ක', 'ඛ', 'ග', 'ඝ', 'ඟ', 'ච', 'ඡ', 'ජ', 'ඣ', 'ඤ', 'ඥ',
            'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ', 'ත', 'ථ', 'ද', 'ධ', 'න', 'ඳ',
            'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ', 'ය', 'ර', 'ල', 'ව', 'ශ', 'ෂ',
            'ස', 'හ', 'ළ', 'ෆ'
        ]

        # Define which vowel modifiers can be used with which letters
        # This mapping defines valid combinations based on Sinhala language rules
        self.valid_modifiers = {
            # Vowels have limited or no modifiers
            'අ': ['ා', 'ැ', 'ෑ', 'ි', 'ී', 'ු', 'ූ', '්'],
            'ආ': ['්'],
            'ඇ': ['්'],
            'ඈ': ['්'],
            'ඉ': ['්'],
            'ඊ': ['්'],
            'උ': ['්'],
            'ඌ': ['්'],
            'ඍ': ['්'],
            'ඎ': ['්'],
            'ඏ': ['්'],
            'ඐ': ['්'],

            # Special consonant with no vowel modifiers
            'ඞ': ['්'],

            # Default set of modifiers for most consonants
            'DEFAULT': ['ා', 'ැ', 'ෑ', 'ි', 'ී', 'ු', 'ූ', 'ෘ', 'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ', '්']
        }

    def update_theme(self):
        """Update the keyboard styling based on the current theme"""
        if self.dark_mode:
            # Dark mode styling
            self.setStyleSheet("""
                SinhalaKeyboard {
                    background-color: #2d2d2d;
                    border: 1px solid #444444;
                    border-radius: 10px;
                }
            """)
            self.button_style = self.get_dark_button_style()
        else:
            # Light mode styling
            self.setStyleSheet("""
                SinhalaKeyboard {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                }
            """)
            self.button_style = self.get_light_button_style()
        
        # Update all existing buttons with the new style and size
        # Only if the grid layout has been initialized
        if hasattr(self, 'grid_layout') and self.grid_layout is not None:
            print("Updating buttons after theme change")
            self.update_buttons()
        else:
            print("Skipping button update - layout not ready yet")

    def set_dark_mode(self, is_dark):
        """Set the keyboard theme to dark or light mode"""
        self.dark_mode = is_dark
        self.update_theme()
        
    def make_detachable(self):
        """Convert the keyboard to a detachable floating window"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout
        
        # Check if we're already in a floating window
        if self.parent() and isinstance(self.parent(), QDialog):
            return  # Already detached
            
        # Store the original parent
        original_parent = self.parent()
        
        # Create a new dialog to host the keyboard
        dialog = QDialog(original_parent)
        dialog.setWindowTitle("Sinhala Keyboard")
        dialog.setWindowFlags(dialog.windowFlags() | Qt.Tool)  # Make it a tool window
        
        # Create layout for the dialog
        layout = QVBoxLayout(dialog)
        
        # Add a button bar at the top
        button_bar = QHBoxLayout()
        
        # Add a button to dock the keyboard back
        dock_button = QPushButton("Dock Keyboard")
        dock_button.clicked.connect(lambda: self.make_embedded(original_parent, dialog))
        button_bar.addWidget(dock_button)
        
        # Add a button to reset the keyboard size
        reset_button = QPushButton("Reset Size")
        reset_button.clicked.connect(lambda: self.reset_size())
        button_bar.addWidget(reset_button)
        
        # Add the button bar to the layout
        layout.addLayout(button_bar)
        
        # Remove the keyboard from its current parent
        self.setParent(None)
        
        # Add the keyboard to the dialog
        layout.addWidget(self)
        
        # Show the dialog
        dialog.resize(800, 600)  # Set a reasonable default size
        dialog.show()
        
        return dialog
        
    def make_embedded(self, original_parent, dialog=None):
        """Convert the keyboard back to an embedded widget"""
        if not original_parent:
            return  # No original parent to return to
            
        # Remove the keyboard from the dialog
        self.setParent(None)
        
        # Find the keyboard container in the original parent
        keyboard_container = original_parent.findChild(QWidget, "keyboard_container")
        
        if keyboard_container:
            # Get the layout of the keyboard container
            container_layout = keyboard_container.layout()
            
            if container_layout:
                # Add the keyboard back to the container
                container_layout.addWidget(self, 1)  # Add with stretch factor of 1
                
                # Show the keyboard container
                keyboard_container.show()
                
                # Update the keyboard to match the container size
                self.resize(keyboard_container.width(), keyboard_container.height() - 10)
                
                # Update the buttons
                self.update_buttons()
                
                # If we have a dialog, close it
                if dialog:
                    dialog.close()
                    
    def reset_size(self):
        """Reset the keyboard to its default size"""
        # Default keyboard height
        default_height = 600
        
        # Resize the keyboard
        self.resize(self.width(), default_height)
        
        # Update the buttons
        self.update_buttons()
        
    def set_font_size(self, size):
        """Update the font size and resize buttons accordingly"""
        # Convert to float and then round to nearest integer for consistency
        size = round(float(size))
        if size != self.font_size:  # Simple integer comparison
            self.font_size = size
            print(f"Updating keyboard font size to: {size}")
            # Set a flag to prevent automatic font size adjustment
            self._manual_font_size = True
            # Update the buttons to reflect the new font size
            self.update_buttons()
            # Keep the flag set - it will be reset by the main window after a delay
            # This prevents resize loops when the keyboard is resized
        
    def update_buttons(self):
        """Update all existing buttons with the current style and size"""
        try:
            # Check if layout exists first
            if not self.layout():
                logger.error("Error: No layout found in update_buttons")
                return
                
            # Get the grid layout - safely
            if not hasattr(self, 'grid_layout') or self.grid_layout is None:
                logger.error("Error: Grid layout not initialized in update_buttons")
                return
                
            grid_layout = self.grid_layout # Use the stored instance variable

            # Calculate available height for the grid
            # Subtract main layout margins (top and bottom) and spacing between items
            available_height = self.height() - self.layout().contentsMargins().top() - self.layout().contentsMargins().bottom()
            
            # Subtract spacing between the grid and other widgets in the main layout
            for i in range(self.layout().count()):
                 item = self.layout().itemAt(i)
                 if item and item.widget() and item.widget() != self: # Exclude self if it somehow gets added
                      available_height -= self.layout().spacing()

            # Subtract height of the resize hint label (assuming it's the last widget)
            if self.layout().count() > 1:
                 resize_hint_item = self.layout().itemAt(self.layout().count() - 1)
                 if resize_hint_item and resize_hint_item.widget():
                      available_height -= resize_hint_item.widget().height()

            # Calculate available width for the grid
            available_width = self.width() - self.layout().contentsMargins().left() - self.layout().contentsMargins().right()
            
            # Calculate button dimensions based on available space and grid layout
            # We have 5 rows and 15 columns in the grid
            num_rows = 5
            num_cols = 15
            
            # Calculate button size to fit the available space
            # Subtract grid spacing between rows and columns
            button_height = (available_height - grid_layout.verticalSpacing() * (num_rows - 1)) / num_rows
            button_width = (available_width - grid_layout.horizontalSpacing() * (num_cols - 1)) / num_cols
            
            # Use the smaller dimension to maintain square buttons (except for special buttons)
            button_size = min(button_height, button_width)
            
            # Ensure a minimum button size based on font size but keep it small enough to fit
            min_button_size = max(MIN_KB_FONT, int(self.font_size * 0.8))
            button_size = max(min_button_size, button_size)
            
            logger.debug(f"Calculated button size: {button_size}px (font: {self.font_size}, available height: {available_height}px, width: {available_width}px)")

            # Calculate adjusted font size based on button size
            # Scale font size proportionally to button size, with a higher minimum
            adjusted_font_size = max(MIN_KB_FONT / 2, int(button_size * 0.45))
            
            # Check if we're in the middle of a mouse resize operation
            in_resize_operation = hasattr(self, 'resize_in_progress') and self.resize_in_progress
            
            # Check if we have a stored pre-resize font size
            has_pre_resize_font = hasattr(self, '_pre_resize_font_size') and self._pre_resize_font_size is not None
            
            # During resize, use the pre-resize font size if available
            if in_resize_operation and has_pre_resize_font:
                # Use the stored font size during resize
                logger.debug(f"Using stored pre-resize font size: {self._pre_resize_font_size}")
                self.font_size = self._pre_resize_font_size
            
            # Only update the font size automatically if:
            # 1. Not manually set (_manual_font_size flag is not set)
            # 2. Not in the middle of a mouse resize operation
            # 3. Not immediately after a resize operation
            elif (not hasattr(self, '_manual_font_size') or not self._manual_font_size) and not in_resize_operation:
                # Update the main font size property based on button size
                new_font_size = max(MIN_KB_FONT, round(button_size * 0.9))
                
                # Only update if the change is significant (more than 2 points)
                # Increased threshold to prevent oscillations
                if abs(new_font_size - self.font_size) > 2:
                    logger.info(f"Updating font size from {self.font_size} to {new_font_size} based on button size {button_size}")
                    self.font_size = new_font_size
                    
                    # Let the main window handle preferences updates to avoid race conditions
                    # This prevents a race where keyboard.py writes a value derived from buttons
                    # while main.py simultaneously writes a value derived from height
                    try:
                        from PySide6.QtWidgets import QApplication
                        app = QApplication.instance()
                        if app:
                            for widget in app.topLevelWidgets():
                                if hasattr(widget, 'set_keyboard_font_size'):
                                    # Call the main window's method to update font size
                                    # This ensures only one place writes to preferences
                                    widget.set_keyboard_font_size(new_font_size)
                                    logger.info(f"Requested font size update to {new_font_size} via main window")
                                    break
                    except Exception as e:
                        logger.error(f"Error requesting font size update: {e}")
            else:
                # Skip automatic adjustment during resize operations
                if in_resize_operation:
                    logger.debug(f"Skipping automatic font size adjustment during resize operation")
                else:
                    logger.debug(f"Skipping automatic font size adjustment because font size was manually set to {self.font_size}")

            # Create font with better fallback strategy
            font = QFont(self.keyboard_font_family, adjusted_font_size)
            font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
            font.setBold(True)

            # Update all existing buttons
            for child in self.findChildren(QPushButton):
                try:
                    # Set font directly
                    child.setFont(font)

                    # Apply stylesheet for styling with button_size parameter
                    if child.text() not in ["Space", "Backspace"]:
                        child.setStyleSheet(self.get_button_style(button_size))
                        
                        # Set minimum size but don't fix the size
                        child.setMinimumSize(min_button_size, min_button_size)
                        
                        # Set size policy to allow the button to grow and shrink with the layout
                        child.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    elif child.text() == "Space":
                        child.setStyleSheet(self.get_space_button_style())
                        child.setMinimumHeight(min_button_size)
                        child.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    elif child.text() == "Backspace":
                        child.setStyleSheet(self.get_backspace_button_style())
                        child.setMinimumHeight(min_button_size)
                        child.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                except Exception as e:
                    print(f"Error updating button {child.text()}: {e}")
                    # If there was an error, try with a system font as fallback
                    try:
                        fallback_font = QFont("Arial", 12)
                        child.setFont(fallback_font)
                    except:
                        pass
                        
            # Force the grid layout to update
            grid_layout.update()
            
        except Exception as e:
            print(f"Error in update_buttons: {e}")

    def get_button_style(self, button_size):
        """Get the button style with the specified size based on current theme"""
        # Note: Font settings are now applied directly to the button using setFont()
        # to avoid font fallback issues
        
        # Calculate padding based on button size - smaller padding for larger buttons
        # This ensures text doesn't overflow or get too close to the edges
        padding = max(1, min(4, int(button_size * 0.05)))
        
        # Calculate border radius based on button size
        border_radius = max(3, min(8, int(button_size * 0.15)))
        
        if self.dark_mode:
            return f"""
                QPushButton {{
                    border: 1px solid #555555;
                    border-radius: {border_radius}px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                    padding: {padding}px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: #4d4d4d;
                    border: 1px solid #6699cc;
                }}
                QPushButton:pressed {{
                    background-color: #555555;
                    border: 2px solid #6699cc;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    border: 1px solid #aaaaaa;
                    border-radius: {border_radius}px;
                    background-color: #ffffff;
                    color: #000000;
                    padding: {padding}px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: #e6f0ff;
                    border: 1px solid #4d94ff;
                }}
                QPushButton:pressed {{
                    background-color: #99c2ff;
                    border: 2px solid #0066ff;
                }}
            """
    
    def get_light_button_style(self):
        """Get the button style for light mode"""
        # Use the loaded font family and specified font size
        button_size = max(46, self.font_size + 20)  # Scale button size with font size
        return self.get_button_style(button_size)

    def get_dark_button_style(self):
        """Get the button style for dark mode"""
        # Use the loaded font family and specified font size
        button_size = max(46, self.font_size + 20)  # Scale button size with font size
        return self.get_button_style(button_size)

    def get_space_button_style(self):
        """Get the style for the Space button based on current theme"""
        if self.dark_mode:
            return """
                QPushButton {
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #444444;
                    color: #ffffff;
                    padding: 2px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    border: 1px solid #6699cc;
                }
                QPushButton:pressed {
                    background-color: #555555;
                    border: 2px solid #6699cc;
                }
            """
        else:
            return """
                QPushButton {
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 2px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e6f0ff;
                    border: 1px solid #4d94ff;
                }
                QPushButton:pressed {
                    background-color: #99c2ff;
                    border: 2px solid #0066ff;
                }
            """

    def get_backspace_button_style(self):
        """Get the style for the Backspace button based on current theme"""
        if self.dark_mode:
            return """
                QPushButton {
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #444444;
                    color: #ffffff;
                    padding: 2px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #663333;
                    border: 1px solid #cc6666;
                }
                QPushButton:pressed {
                    background-color: #804040;
                    border: 2px solid #cc6666;
                }
            """
        else:
            return """
                QPushButton {
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 2px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #ffe6e6;
                    border: 1px solid #ff4d4d;
                }
                QPushButton:pressed {
                    background-color: #ffb3b3;
                    border: 2px solid #ff0000;
                }
            """

    def create_button(self, text, button_size):
        """Create a button with proper font settings to avoid font fallback issues"""
        try:
            # Create button with no text initially
            btn = QPushButton()
            
            # Set font directly with better fallback strategy
            # Use a smaller font size for better rendering and compatibility
            adjusted_font_size = max(int(button_size * 0.45), 10)
            
            # Create font with better fallback strategy
            try:
                font = QFont(self.keyboard_font_family, adjusted_font_size)
                # Use PreferMatch instead of NoFontMerging to allow some fallback
                font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
                font.setBold(True)
                
                # Apply the font to the button
                btn.setFont(font)
            except Exception as font_error:
                print(f"Error setting font for button: {font_error}")
                # Use a system font as fallback
                fallback_font = QFont("Arial", 12)
                btn.setFont(fallback_font)
            
            # Set text after font is configured
            try:
                btn.setText(text)
            except Exception as text_error:
                print(f"Error setting text '{text}' for button: {text_error}")
                # Try with a simpler text
                btn.setText("?")
            
            # Apply stylesheet for styling (but not font)
            try:
                btn.setStyleSheet(self.get_button_style(button_size))
                
                # Set minimum size but don't fix the size
                min_button_size = max(20, int(self.font_size * 0.8))
                btn.setMinimumSize(min_button_size, min_button_size)
                
                # Set size policy to allow the button to grow and shrink with the layout
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            except Exception as style_error:
                print(f"Error applying style to button: {style_error}")
                # Apply minimal styling
                min_button_size = max(20, int(self.font_size * 0.8))
                btn.setMinimumSize(min_button_size, min_button_size)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Print debug info for the first few buttons
            if text in ['අ', 'ආ', 'ඇ']:
                print(f"Created button with text: '{text}', font: {btn.font().family()}, size: {adjusted_font_size}")
            
            return btn
        except Exception as e:
            print(f"Error creating button with text '{text}': {e}")
            # Create a fallback button with minimal styling and a system font
            try:
                fallback_btn = QPushButton("?")  # Use ? as fallback text
                fallback_font = QFont("Arial", 12)
                fallback_btn.setFont(fallback_font)
                min_button_size = max(20, int(self.font_size * 0.8))
                fallback_btn.setMinimumSize(min_button_size, min_button_size)
                fallback_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                return fallback_btn
            except Exception as fallback_error:
                print(f"Error creating fallback button: {fallback_error}")
                # Last resort - create an empty button
                empty_btn = QPushButton()
                min_button_size = max(20, int(self.font_size * 0.8))
                empty_btn.setMinimumSize(min_button_size, min_button_size)
                empty_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                return empty_btn
        
    def create_keyboard(self):
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(2)

        # Create a single grid layout for the entire keyboard
        self.grid_layout = QGridLayout() # Store as instance variable
        self.grid_layout.setSpacing(4)  # Increased spacing to prevent overlap
        
        # Make the grid layout stretch to fill available space
        # Set stretch factors for all columns and rows
        for i in range(15):  # 15 columns
            self.grid_layout.setColumnStretch(i, 1)
        for i in range(5):   # 5 rows
            self.grid_layout.setRowStretch(i, 1)
        
        # Calculate initial button size based on font size and default height
        # This will be adjusted in update_buttons when the keyboard is resized
        button_size = max(40, int(self.font_size * 1.5))
        
        print(f"Creating keyboard with button size: {button_size}px, font: {self.keyboard_font_family}")

        # Row 0: Vowels
        vowels = self.keys['vowels']
        for col, key in enumerate(vowels):
            # Create button with proper font settings
            btn = self.create_button(key, button_size)
            
            # Print debug info for first button
            if col == 0:
                print(f"Created button with text: '{key}', font: {self.keyboard_font_family}, size: {self.font_size}")

            # Only අ has a popup with variants
            if key == 'අ':
                btn.clicked.connect(lambda checked=False, k=key, b=btn: self.show_vowel_group(k, b))
            else:
                key_fixed = key
                btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))

            self.grid_layout.addWidget(btn, 0, col)

        # Row 1: Vowel modifiers and first consonants
        row1_keys = ['ු', 'ූ', 'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ', 'ක', 'ඛ', 'ග', 'ඝ', 'ඟ', 'ච', 'ඡ']
        for col, key in enumerate(row1_keys):
            # Create button with proper font settings
            btn = self.create_button(key, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            self.grid_layout.addWidget(btn, 1, col)

        # Row 2: More consonants
        row2_keys = ['ජ', 'ඣ', 'ඤ', 'ඥ', 'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ', 'ත', 'ථ', 'ද', 'ධ', 'න']
        for col, key in enumerate(row2_keys):
            # Create button with proper font settings
            btn = self.create_button(key, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            self.grid_layout.addWidget(btn, 2, col)

        # Row 3: More consonants
        row3_keys = ['ඳ', 'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ', 'ය', 'ර', 'ල', 'ව', 'ශ', 'ෂ', 'ස', 'හ']
        for col, key in enumerate(row3_keys):
            # Create button with proper font settings
            btn = self.create_button(key, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            self.grid_layout.addWidget(btn, 3, col)

        # Row 4: Remaining consonants and special characters
        row4_keys = ['ළ', 'ෆ', 'ං', 'ඃ', '්', 'ා', 'ැ', 'ෑ', 'ි', 'ී']
        for col, key in enumerate(row4_keys):
            # Create button with proper font settings
            btn = self.create_button(key, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            self.grid_layout.addWidget(btn, 4, col)

        try:
            # Add Space button with proper font settings
            space_btn = QPushButton("Space")
            
            # Use a system font for Latin text buttons to avoid rendering issues
            # These buttons don't need Sinhala font support
            font = QFont("Arial", int(button_size * 0.4))
            font.setBold(True)
            space_btn.setFont(font)
            space_btn.setStyleSheet(self.get_space_button_style())
            
            # Set minimum height but don't fix the height
            min_button_size = max(20, int(self.font_size * 0.8))
            space_btn.setMinimumHeight(min_button_size)
            space_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            space_btn.clicked.connect(lambda checked=False, b=space_btn: self.on_key_clicked("Space", b))

            # Add Space button to span 3 columns
            self.grid_layout.addWidget(space_btn, 4, 10, 1, 3)

            # Add Backspace button with proper font settings
            backspace_btn = QPushButton("Backspace")
            backspace_btn.setFont(font)  # Reuse the same font
            backspace_btn.setStyleSheet(self.get_backspace_button_style())
            backspace_btn.setMinimumHeight(min_button_size)
            backspace_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            backspace_btn.clicked.connect(lambda checked=False, b=backspace_btn: self.on_key_clicked("Backspace", b))
            
            # Print debug info
            print(f"Created Space/Backspace buttons with font: {font.family()}")
        except Exception as e:
            print(f"Error creating Space/Backspace buttons: {e}")
            # Create fallback buttons with system font
            space_btn = QPushButton("Space")
            fallback_font = QFont("Arial", 12)
            space_btn.setFont(fallback_font)
            min_button_size = max(20, int(self.font_size * 0.8))
            space_btn.setMinimumHeight(min_button_size)
            space_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            space_btn.clicked.connect(lambda checked=False, b=space_btn: self.on_key_clicked("Space", b))
            self.grid_layout.addWidget(space_btn, 4, 10, 1, 3)
            
            backspace_btn = QPushButton("Backspace")
            backspace_btn.setFont(fallback_font)
            backspace_btn.setMinimumHeight(min_button_size)
            backspace_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            backspace_btn.clicked.connect(lambda checked=False, b=backspace_btn: self.on_key_clicked("Backspace", b))

        # Add Backspace button to span 2 columns
        self.grid_layout.addWidget(backspace_btn, 4, 13, 1, 2)

        main_layout.addLayout(self.grid_layout, 1)  # Add with stretch factor of 1
        
        # Add resize handle indicator at the bottom
        resize_hint = QLabel("▲ Drag edges to resize ▼")
        resize_hint.setAlignment(Qt.AlignCenter)
        resize_hint.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                font-weight: bold;
                padding: 2px;
                background-color: transparent;
                border-top: 1px dotted #aaaaaa;
                border-bottom: 1px dotted #aaaaaa;
            }
        """)
        main_layout.addWidget(resize_hint, 0)  # Add with stretch factor of 0

        # Set size policy to make the keyboard fit within the window but allow vertical resizing
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Now that the layout is fully set up, update the buttons
        # This ensures the layout exists when update_buttons is called
        self.update_buttons()

    def on_key_clicked(self, key, button):
        """Handle key clicks with visual feedback"""
        try:
            # Check if the key is a consonant that can have vowel modifiers
            if key in self.consonants:
                # Show vowel modifier options
                self.show_vowel_modifiers(key)
            elif key in self.keys.get('modifiers', []):
                # For modifiers, we'll just emit them directly
                # In a real implementation, you might want to combine with the last consonant
                self.keyPressed.emit(key)
            else:
                # For non-consonants, just emit the key press signal
                self.keyPressed.emit(key)
        except Exception as e:
            print(f"Error in on_key_clicked for key '{key}': {e}")
            # In case of error, just emit the key directly
            self.keyPressed.emit(key)

    def show_vowel_group(self, vowel, button):
        """Show a popup with vowel variants"""
        try:
            if vowel not in self.vowel_groups:
                # If no group defined, just emit the key
                self.keyPressed.emit(vowel)
                return
    
            # Calculate current button size based on keyboard height
            height_factor = self.height() / self.default_height
            current_button_size = max(46, int((self.font_size + 20) * height_factor))
    
            # Create a dialog to show vowel variants
            dialog = QDialog(self.parent())
            dialog.setWindowTitle(f"Vowel Variants")
            dialog.setModal(False)  # Make it non-modal
        except Exception as e:
            print(f"Error initializing vowel group dialog: {e}")
            # Just emit the vowel without showing the dialog
            self.keyPressed.emit(vowel)
            return

        # Enable closing when clicking outside the dialog
        dialog.setAttribute(Qt.WA_DeleteOnClose)

        # Install event filter to detect clicks outside
        class ClickOutsideFilter(QObject):
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.MouseButtonPress:
                    # Check if the click is outside the dialog
                    # Use event.globalPosition().toPoint() instead of deprecated globalPos()
                    global_pos = event.globalPosition().toPoint() if hasattr(event, 'globalPosition') else event.globalPos()
                    if not dialog.geometry().contains(global_pos):
                        dialog.close()
                        return True
                return False

        # Create and install the filter
        click_filter = ClickOutsideFilter()
        if self.parent():
            self.parent().installEventFilter(click_filter)
            # Connect dialog's finished signal to remove the event filter
            dialog.finished.connect(lambda: self.parent().removeEventFilter(click_filter))

        # Apply theme-specific styling
        if self.dark_mode:
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 10px;
                }
            """)
        else:
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                }
            """)

        # Create layout for the dialog
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Add a label
        label = QLabel(f"Select a variant of {vowel}:")
        label.setAlignment(Qt.AlignCenter)
        
        # Calculate font size based on current keyboard size
        adjusted_font_size = max(self.font_size - 8, int((self.font_size - 8) * height_factor))
        
        # Set style with font size
        if self.dark_mode:
            label.setStyleSheet(f"color: #ffffff; font-size: {adjusted_font_size}px;")
        else:
            label.setStyleSheet(f"color: #000000; font-size: {adjusted_font_size}px;")
        layout.addWidget(label)

        # Create a grid for the vowel variants
        grid = QGridLayout()
        grid.setSpacing(5)

        # Add buttons for each variant
        variants = self.vowel_groups[vowel]
        
        # Create font with better fallback strategy
        adjusted_font_size = max(self.font_size - 4, 12)
        font = QFont(self.keyboard_font_family, adjusted_font_size)
        # Use PreferMatch instead of NoFontMerging to allow some fallback
        font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
        font.setBold(True)
        
        for i, variant in enumerate(variants):
            btn = QPushButton(variant)
            
            # Use the same button size as the main keyboard
            btn.setFixedSize(current_button_size, current_button_size)
            
            # Set font directly with better fallback strategy
            btn.setFont(font)
            
            # Apply theme-specific styling (without font settings)
            if self.dark_mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        border: 1px solid #555555;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                        border: 1px solid #6699cc;
                    }
                    QPushButton:pressed {
                        background-color: #555555;
                        border: 2px solid #6699cc;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #aaaaaa;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #e6f0ff;
                        border: 1px solid #4d94ff;
                    }
                    QPushButton:pressed {
                        background-color: #99c2ff;
                        border: 2px solid #0066ff;
                    }
                """)

            # Use a closure to capture the current value
            variant_fixed = variant  # Create a fixed reference
            btn.clicked.connect(lambda checked=False, v=variant_fixed: self.select_vowel_variant(dialog, v))
            grid.addWidget(btn, 0, i)

        layout.addLayout(grid)

        # Set dialog properties
        dialog.setLayout(layout)
        dialog.setMinimumWidth(250)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # Removed Qt.Popup flag

        try:
            # Position the dialog near the button
            button_pos = button.mapToGlobal(button.rect().topLeft())
            dialog.move(button_pos.x(), button_pos.y() - 80)
            
            # Make sure the dialog is visible on the current screen
            screen = self.screen()
            if screen:
                screen_geometry = screen.geometry()
                dialog_geometry = dialog.geometry()
                
                # Adjust if the dialog is outside the screen
                if not screen_geometry.contains(dialog_geometry):
                    # If outside screen, reposition to be visible
                    if dialog_geometry.right() > screen_geometry.right():
                        dialog.move(screen_geometry.right() - dialog_geometry.width(), dialog_geometry.y())
                    if dialog_geometry.bottom() > screen_geometry.bottom():
                        dialog.move(dialog_geometry.x(), screen_geometry.bottom() - dialog_geometry.height())
                    if dialog_geometry.left() < screen_geometry.left():
                        dialog.move(screen_geometry.left(), dialog_geometry.y())
                    if dialog_geometry.top() < screen_geometry.top():
                        dialog.move(dialog_geometry.x(), screen_geometry.top())
            else:
                # If we can't get screen info, just center the dialog on the keyboard
                keyboard_center = self.mapToGlobal(self.rect().center())
                dialog.move(keyboard_center.x() - dialog.width() // 2, keyboard_center.y() - dialog.height() // 2)
                
            # Show the dialog
            dialog.exec_()
        except Exception as e:
            print(f"Error showing vowel group dialog: {e}")
            # Just emit the vowel without showing the dialog
            self.keyPressed.emit(vowel)

    def select_vowel_variant(self, dialog, vowel):
        """Handle selection of a vowel variant"""
        # Close the dialog
        dialog.accept()

        # Emit the key press signal with the selected vowel
        self.keyPressed.emit(vowel)

    def show_vowel_modifiers(self, consonant):
        """Show a dialog with vowel modifier options for the selected consonant"""
        try:
            # Calculate current button size based on keyboard height
            height_factor = self.height() / self.default_height
            current_button_size = max(46, int((self.font_size + 20) * height_factor))
            
            # Create a dialog to show vowel modifiers
            dialog = QDialog(self.parent())
            dialog.setWindowTitle(f"Vowel Modifiers for {consonant}")
            dialog.setModal(False)  # Changed to non-modal so it can be closed by clicking outside
        except Exception as e:
            print(f"Error initializing vowel modifiers dialog: {e}")
            # Just emit the consonant without showing the dialog
            self.keyPressed.emit(consonant)
            return

        # Enable closing when clicking outside the dialog
        dialog.setAttribute(Qt.WA_DeleteOnClose)

        # Install event filter to detect clicks outside
        class ClickOutsideFilter(QObject):
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.MouseButtonPress:
                    # Check if the click is outside the dialog
                    # Use event.globalPosition().toPoint() instead of deprecated globalPos()
                    global_pos = event.globalPosition().toPoint() if hasattr(event, 'globalPosition') else event.globalPos()
                    if not dialog.geometry().contains(global_pos):
                        dialog.close()
                        return True
                return False

        # Create and install the filter
        click_filter = ClickOutsideFilter()
        if self.parent():
            self.parent().installEventFilter(click_filter)
            # Connect dialog's finished signal to remove the event filter
            dialog.finished.connect(lambda: self.parent().removeEventFilter(click_filter))

        # Apply theme-specific styling
        if self.dark_mode:
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 10px;
                }
            """)
        else:
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                }
            """)

        # Create layout for the dialog
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Add a label
        label = QLabel(f"Select a vowel modifier for {consonant}:")
        label.setAlignment(Qt.AlignCenter)
        
        # Calculate font size based on current keyboard size
        adjusted_font_size = max(self.font_size - 8, int((self.font_size - 8) * height_factor))
        
        # Set style with font size
        if self.dark_mode:
            label.setStyleSheet(f"color: #ffffff; font-size: {adjusted_font_size}px;")
        else:
            label.setStyleSheet(f"color: #000000; font-size: {adjusted_font_size}px;")
        layout.addWidget(label)

        # Create a grid for the vowel modifiers
        grid = QGridLayout()
        grid.setSpacing(5)

        # Get valid modifiers for this consonant
        valid_modifiers = self.valid_modifiers.get(consonant, self.valid_modifiers['DEFAULT'])

        # Add buttons for each modifier
        # First add the base consonant (no modifier)
        btn = QPushButton(consonant)
        
        # Use the same button size as the main keyboard
        btn.setFixedSize(current_button_size, current_button_size)
        
        # Set font directly with better fallback strategy
        adjusted_font_size = max(self.font_size - 4, 12)
        font = QFont(self.keyboard_font_family, adjusted_font_size)
        # Use PreferMatch instead of NoFontMerging to allow some fallback
        font.setStyleStrategy(QFont.StyleStrategy.PreferMatch)
        font.setBold(True)
        btn.setFont(font)
        
        # Apply theme-specific styling (without font settings)
        if self.dark_mode:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    border: 1px solid #6699cc;
                }
                QPushButton:pressed {
                    background-color: #555555;
                    border: 2px solid #6699cc;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #aaaaaa;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #e6f0ff;
                    border: 1px solid #4d94ff;
                }
                QPushButton:pressed {
                    background-color: #99c2ff;
                    border: 2px solid #0066ff;
                }
            """)

        # Use a closure to capture the current value
        btn.clicked.connect(lambda checked=False, c=consonant: self.select_consonant_with_modifier(dialog, c, ''))
        grid.addWidget(btn, 0, 0)

        # Add buttons for each modifier
        col = 1
        row = 0
        for modifier in valid_modifiers:
            # Skip empty modifier as we already added it
            if modifier == '':
                continue
                
            # Create a combined character (consonant + modifier)
            combined = consonant + modifier
            
            btn = QPushButton(combined)
            
            # Use the same button size as the main keyboard and other buttons in this dialog
            btn.setFixedSize(current_button_size, current_button_size)
            
            # Set font directly with better fallback strategy
            # Reuse the same font as the base consonant button
            btn.setFont(font)
            
            # Apply theme-specific styling (without font settings)
            if self.dark_mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        border: 1px solid #555555;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                        border: 1px solid #6699cc;
                    }
                    QPushButton:pressed {
                        background-color: #555555;
                        border: 2px solid #6699cc;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #aaaaaa;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #e6f0ff;
                        border: 1px solid #4d94ff;
                    }
                    QPushButton:pressed {
                        background-color: #99c2ff;
                        border: 2px solid #0066ff;
                    }
                """)

            # Use a closure to capture the current values
            modifier_fixed = modifier  # Create a fixed reference
            btn.clicked.connect(lambda checked=False, c=consonant, m=modifier_fixed: self.select_consonant_with_modifier(dialog, c, m))
            
            # Add to grid, wrapping to next row after 5 columns
            grid.addWidget(btn, row, col)
            col += 1
            if col > 4:  # 5 columns (0-4)
                col = 0
                row += 1

        layout.addLayout(grid)

        # Set dialog properties
        dialog.setLayout(layout)
        dialog.setMinimumWidth(300)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)  # Removed Qt.Popup flag

        try:
            # Position the dialog near the cursor
            cursor_pos = QCursor.pos()
            dialog.move(cursor_pos.x() - 150, cursor_pos.y() - 150)
            
            # If we can't get cursor position, try to position relative to the keyboard
            if cursor_pos.isNull():
                keyboard_pos = self.mapToGlobal(self.rect().topLeft())
                dialog.move(keyboard_pos.x() + 100, keyboard_pos.y() - 200)
                
            # Make sure the dialog is visible on the current screen
            screen = self.screen()
            if screen:
                screen_geometry = screen.geometry()
                dialog_geometry = dialog.geometry()
                
                # Adjust if the dialog is outside the screen
                if not screen_geometry.contains(dialog_geometry):
                    # If outside screen, reposition to be visible
                    if dialog_geometry.right() > screen_geometry.right():
                        dialog.move(screen_geometry.right() - dialog_geometry.width(), dialog_geometry.y())
                    if dialog_geometry.bottom() > screen_geometry.bottom():
                        dialog.move(dialog_geometry.x(), screen_geometry.bottom() - dialog_geometry.height())
                    if dialog_geometry.left() < screen_geometry.left():
                        dialog.move(screen_geometry.left(), dialog_geometry.y())
                    if dialog_geometry.top() < screen_geometry.top():
                        dialog.move(dialog_geometry.x(), screen_geometry.top())
            else:
                # If we can't get screen info, just center the dialog on the keyboard
                keyboard_center = self.mapToGlobal(self.rect().center())
                dialog.move(keyboard_center.x() - dialog.width() // 2, keyboard_center.y() - dialog.height() // 2)
                
            # Show the dialog
            dialog.exec_()
        except Exception as e:
            print(f"Error showing vowel modifiers dialog: {e}")
            # Just emit the consonant without showing the dialog
            self.keyPressed.emit(consonant)

    def select_consonant_with_modifier(self, dialog, consonant, modifier):
        """Handle selection of a consonant with a modifier"""
        # Close the dialog
        dialog.accept()

        # Emit the key press signal with the selected consonant + modifier
        combined = consonant + modifier
        self.keyPressed.emit(combined)

    def on_keyboard_button_clicked(self, text):
        """Handle keyboard button clicks"""
        # This method is called when a key is pressed on the keyboard
        # It emits the keyPressed signal with the text of the key
        self.keyPressed.emit(text)
        
    # --- Resize handling methods ---
    
    # Track resize state to prevent loops
    _last_resize_time = 0
    _resize_count = 0
    _last_emitted_height = 0
    
    def resizeEvent(self, event):
        """Handle resize events to update button sizes"""
        try:
            super().resizeEvent(event)
            
            # Track resize frequency to detect and prevent loops
            import time
            current_time = time.time()
            time_since_last = current_time - self._last_resize_time
            self._last_resize_time = current_time
            
            # Increment resize counter
            if time_since_last < 0.5:  # If resizes are happening rapidly
                self._resize_count += 1
            else:
                # Reset counter if enough time has passed
                self._resize_count = 0
            
            # Detect resize loops and break them - increased threshold to allow more resizes
            if self._resize_count > 20:
                print(f"WARNING: Detected resize loop! Count: {self._resize_count}, Time: {time_since_last:.3f}s")
                # Skip this resize to break the loop
                self._resize_count = 0
                return
                
            # Check if size has changed (either width or height)
            size_changed = (event.size().height() != event.oldSize().height() or 
                           event.size().width() != event.oldSize().width())
                
            # Check if manual font size adjustment is in progress
            # If so, we should be more conservative about triggering updates
            if hasattr(self, '_manual_font_size') and self._manual_font_size:
                # During manual resize, only allow significant changes to trigger updates
                # This prevents resize loops during manual resizing
                if not size_changed or abs(event.size().height() - event.oldSize().height()) < 10:
                    return
            
            # Only update if not in the middle of a resize operation and size has changed
            if not self.resize_in_progress and size_changed:
                # Get current dimensions with error handling
                try:
                    current_height = self.height()
                    current_width = self.width()
                    
                    # Skip if dimensions are invalid
                    if current_height <= 0 or current_width <= 0:
                        return
                        
                    # Skip if this is the same height we just emitted (prevent loops)
                    # Only check height since that's what we emit in the signal
                    # Use a larger threshold during manual resizing to prevent loops
                    threshold = 10 if hasattr(self, '_manual_font_size') and self._manual_font_size else 5
                    if abs(current_height - self._last_emitted_height) < threshold:
                        return
                    
                    # Always update buttons when resizing
                    # This ensures the keyboard layout adjusts properly
                    try:
                        # Force a complete update of all buttons
                        self.update_buttons()
                        
                        # Store the current size for future reference
                        # This helps with proportional calculations
                        if not self.initial_size:
                            self.initial_size = self.size()
                    except Exception as update_error:
                        print(f"Error updating buttons during resize: {update_error}")
                    
                    # Store the height we're about to emit
                    self._last_emitted_height = current_height
                    
                    # Emit signal with new height - only log if significant change
                    if abs(current_height - event.oldSize().height()) > 10:
                        print(f"Keyboard resized to height: {current_height}, width: {current_width}")
                    self.keyboardResized.emit(current_height)
                    
                except Exception as height_error:
                    print(f"Error getting dimensions in resizeEvent: {height_error}")
        except Exception as e:
            print(f"Error in resizeEvent: {e}")
            # Try to recover by forcing a button update
            try:
                self.update_buttons()
            except:
                pass
            
    def mousePressEvent(self, event):
        """Handle mouse press events for resizing"""
        try:
            super().mousePressEvent(event)
            
            # Check if mouse is in the resize area (top 10 pixels or bottom 10 pixels)
            if event.position().y() < 10:  # Top edge for resizing down
                self.resize_in_progress = True
                self.resize_direction = "top"
                self.setCursor(Qt.SizeVerCursor)
                
                # Store initial global mouse position for more reliable delta calculation
                self.initial_mouse_pos = event.globalPosition().y()
                self.initial_height = self.height()
                
                # Store the current font size to maintain it during resize
                self._pre_resize_font_size = self.font_size
                
                # Set the manual font size flag to prevent automatic adjustments during resize
                self._manual_font_size = True
                
                # Find the main window to set manual resize flag
                try:
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    main_window = None
                    for widget in app.topLevelWidgets():
                        if widget.__class__.__name__ == "SinhalaWordApp":
                            main_window = widget
                            break
                    
                    # Set the manual resize flag in the main window
                    if main_window and hasattr(main_window, '_manual_resize'):
                        main_window._manual_resize = True
                except Exception as e:
                    print(f"Error finding main window: {e}")
                    
            elif event.position().y() > self.height() - 10:  # Bottom edge for resizing up
                self.resize_in_progress = True
                self.resize_direction = "bottom"
                self.setCursor(Qt.SizeVerCursor)
                
                # Store initial global mouse position for more reliable delta calculation
                self.initial_mouse_pos = event.globalPosition().y()
                self.initial_height = self.height()
                
                # Store the current font size to maintain it during resize
                self._pre_resize_font_size = self.font_size
                
                # Set the manual font size flag to prevent automatic adjustments during resize
                self._manual_font_size = True
                
                # Find the main window to set manual resize flag
                try:
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    main_window = None
                    for widget in app.topLevelWidgets():
                        if widget.__class__.__name__ == "SinhalaWordApp":
                            main_window = widget
                            break
                    
                    # Set the manual resize flag in the main window
                    if main_window and hasattr(main_window, '_manual_resize'):
                        main_window._manual_resize = True
                except Exception as e:
                    print(f"Error finding main window: {e}")
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for resizing"""
        try:
            super().mouseMoveEvent(event)
            
            # Show resize cursor when hovering over the resize areas
            if not self.resize_in_progress:
                if event.position().y() < 10 or event.position().y() > self.height() - 10:
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
                
            # Perform resize if in progress
            if self.resize_in_progress:
                # Calculate new height based on resize direction using global mouse position
                delta = event.globalPosition().y() - self.initial_mouse_pos
                
                # Use a reasonable minimum height (120px) instead of widget's minimumHeight
                min_height = 120  # Minimum reasonable height for usability
                
                if self.resize_direction == "top":
                    # When dragging from top, invert the delta (drag down = smaller)
                    new_height = max(min_height, self.initial_height - delta)
                else:  # bottom
                    # For bottom edge: dragging up (negative delta) should make it smaller
                    new_height = max(min_height, self.initial_height + delta)
                
                # Add a reasonable maximum height limit (80% of screen height if available)
                try:
                    screen = self.screen()
                    if screen:
                        screen_height = screen.availableGeometry().height()
                        max_height = int(screen_height * 0.8)
                        new_height = min(new_height, max_height)
                except Exception as screen_error:
                    logger.error(f"Error getting screen info: {screen_error}")
                    # Fallback to a reasonable maximum if screen info not available
                    new_height = min(new_height, 800)
                
                # Simplified resize logic - don't throttle as much for better responsiveness
                # Just resize directly and update buttons
                
                # Find the main window to set manual resize flag
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                main_window = None
                for widget in app.topLevelWidgets():
                    if widget.__class__.__name__ == "SinhalaWordApp":
                        main_window = widget
                        break
                
                # Set the resize state in the main window to USER to prevent automatic adjustments
                if main_window and hasattr(main_window, '_kb_resize_state'):
                    main_window._kb_resize_state = main_window.ResizeState.USER
                
                # Resize the widget without fixing the height
                self.resize(self.width(), new_height)
                
                # Set flag to prevent automatic font size adjustment during update_buttons
                # This is critical to prevent resize loops
                self._manual_font_size = True
                
                # Store the current font size to maintain it during resize
                self._pre_resize_font_size = self.font_size
                
                # Update buttons to match new size without changing the font size
                self.update_buttons()
                
                # Store the height we're about to emit
                self._last_emitted_height = new_height
                
                # Update the initial height and mouse position for continuous dragging
                self.initial_height = new_height
                self.initial_mouse_pos = event.globalPosition().y()
                
                # Emit the resize signal to ensure parent containers update
                self.keyboardResized.emit(new_height)

                # If we're in a floating window, we don't need to update the container
                # If we're embedded, update the container through the signal
                
                # Accept the event to prevent it from being propagated
                event.accept()
        except Exception as e:
            print(f"Error in mouseMoveEvent: {e}")
            # Reset resize state to prevent getting stuck
            self.resize_in_progress = False
            self.setCursor(Qt.ArrowCursor)
            self.update_buttons()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for resizing"""
        try:
            super().mouseReleaseEvent(event)
            
            # End resize operation
            if self.resize_in_progress:
                # Get current height with error handling
                try:
                    current_height = self.height()
                    
                    # Always emit on mouse release to ensure the resize is applied
                    if current_height > 0:
                        # Resize without fixing dimensions
                        self.resize(self.width(), current_height)
                        
                        # Store the height we're about to emit
                        self._last_emitted_height = current_height
                        
                        # Set flag to prevent automatic font size adjustment during update_buttons
                        self._manual_font_size = True
                        
                        # Update buttons to match the final size
                        self.update_buttons()
                        
                        # Find the main window to update font size
                        from PySide6.QtWidgets import QApplication
                        app = QApplication.instance()
                        main_window = None
                        for widget in app.topLevelWidgets():
                            if widget.__class__.__name__ == "SinhalaWordApp":
                                main_window = widget
                                break
                        
                        if main_window:
                            # Calculate a new font size based on the keyboard height
                            current_font_size = main_window.preferences.get("keyboard_font_size", 26)
                            
                            # Use the standard base values for consistent scaling
                            
                            # Calculate new font size proportional to height
                            # Use the standard minimum font size for better visibility
                            new_font_size = max(MIN_KB_FONT, min(MAX_KB_FONT, round(BASE_KB_FONT * current_height / BASE_KB_HEIGHT)))
                            
                            # Only update if the integer value has changed significantly
                            if abs(new_font_size - int(current_font_size)) > 2:
                                if hasattr(main_window, 'set_keyboard_font_size'):
                                    main_window.set_keyboard_font_size(new_font_size)
                            
                            # Save the current height in preferences
                            main_window.preferences["keyboard_height"] = current_height
                            
                            # Save preferences immediately to disk
                            try:
                                from app import config
                                config.save_user_preferences(main_window.preferences)
                            except Exception as save_error:
                                logger.error(f"Error saving preferences: {save_error}")
                        
                        # Emit final resize signal
                        self.keyboardResized.emit(current_height)
                        
                except Exception as height_error:
                    print(f"Error getting final height: {height_error}")
                
                # Reset resize state
                self.resize_in_progress = False
                self.resize_direction = None
                self.initial_mouse_pos = None
                self.initial_height = None
                self._resize_count = 0
                self.setCursor(Qt.ArrowCursor)
                
                # Reset the resize state in the main window back to IDLE
                try:
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    for widget in app.topLevelWidgets():
                        if widget.__class__.__name__ == "SinhalaWordApp" and hasattr(widget, '_kb_resize_state'):
                            widget._kb_resize_state = widget.ResizeState.IDLE
                            break
                except Exception as e:
                    print(f"Error resetting main window resize state: {e}")
                
                # After resize is complete, we want to preserve the current font size
                # rather than recalculating it based on height
                try:
                    # Find the main window to update preferences with our current font size
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        for widget in app.topLevelWidgets():
                            if hasattr(widget, 'preferences'):
                                # Update the preferences with our current font size
                                # This ensures the font size is preserved after manual resize
                                widget.preferences["keyboard_font_size"] = self.font_size
                                print(f"Preserved font size {self.font_size} after manual resize")
                                
                                # Also update the keyboard height in preferences
                                widget.preferences["keyboard_height"] = current_height
                                print(f"Updated keyboard height to {current_height} in preferences")
                                
                                # Save preferences immediately
                                try:
                                    from app import config
                                    config.save_user_preferences(widget.preferences)
                                except Exception as save_error:
                                    logger.error(f"Error saving preferences: {save_error}")
                                break
                except Exception as e:
                    logger.error(f"Error updating preferences after resize: {e}")
                
                # Reset the manual font size flag after a longer delay to prevent resize conflicts
                from PySide6.QtCore import QTimer
                QTimer.singleShot(3000, lambda: setattr(self, '_manual_font_size', False))
                
                # Accept the event
                event.accept()
        except Exception as e:
            logger.error(f"Error in mouseReleaseEvent: {e}")
            # Ensure resize state is reset even on error
            self.resize_in_progress = False
            self.resize_direction = None
            self._resize_count = 0
            self.setCursor(Qt.ArrowCursor)
