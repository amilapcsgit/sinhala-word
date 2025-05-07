from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, 
                          QSizePolicy, QDialog, QLabel, QGridLayout, QSplitter)
from PySide6.QtCore import Qt, Signal, QObject, QEvent, QSize
from PySide6.QtGui import QColor, QFont, QCursor, QResizeEvent

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
        
        # Increase default height by 20%
        self.default_height = 264  # 220 * 1.2 = 264
        
        # Track initial size for proportional resizing
        self.initial_size = None
        self.resize_in_progress = False
        self.resize_direction = None
        
        # Load the Sinhala font for the keyboard
        self.load_keyboard_font()
        
        # Print debug info
        print(f"Keyboard initialized with font: {self.keyboard_font_family}, size: {self.font_size}")
        
        # Define keyboard layouts and other properties
        self.setup_keyboard_properties()
        
        # Apply initial styling based on theme
        self.update_theme()
        
        # Create the keyboard UI
        self.create_keyboard()
        
        # Enable mouse tracking for resize operations
        self.setMouseTracking(True)
        
        # Set minimum height
        self.setMinimumHeight(180)
        
        # Set size policy to allow vertical resizing
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
    def load_keyboard_font(self):
        """Load Sinhala font for the keyboard buttons"""
        import os
        from PySide6.QtGui import QFontDatabase, QFont
        
        # Prioritized list of Sinhala fonts that are known to work well
        # Only try fonts that are likely to be installed on Windows systems
        system_sinhala_fonts = ["Iskoola Pota", "Nirmala UI"]
        
        # First try to use system Sinhala fonts that are known to work well
        for font_name in system_sinhala_fonts:
            # Check if font exists in the system
            font = QFont(font_name)
            if font.exactMatch() or font.family() == font_name:
                self.keyboard_font_family = font_name
                print(f"Using system Sinhala font for keyboard: {font_name}")
                return
        
        # If no system Sinhala fonts found, use a simple fallback
        # that's guaranteed to work without causing OpenType errors
        print("No Sinhala system fonts found, using fallback font")
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
        self.update_buttons()

    def set_dark_mode(self, is_dark):
        """Set the keyboard theme to dark or light mode"""
        self.dark_mode = is_dark
        self.update_theme()
        
    def update_buttons(self):
        """Update all existing buttons with the current style and size"""
        # Calculate button size based on keyboard height
        if self.height() > 0:
            # Calculate button size proportionally to keyboard height
            # Base size is font_size + 20, but adjust based on keyboard height
            height_factor = self.height() / self.default_height
            button_size = max(46, int((self.font_size + 20) * height_factor))
        else:
            button_size = max(46, self.font_size + 20)
        
        # Update all existing buttons
        for child in self.findChildren(QPushButton):
            if child.text() not in ["Space", "Backspace"]:
                child.setStyleSheet(self.get_button_style(button_size))
                child.setFixedSize(button_size, button_size)
            elif child.text() == "Space":
                child.setStyleSheet(self.get_space_button_style())
                child.setFixedHeight(button_size)
            elif child.text() == "Backspace":
                child.setStyleSheet(self.get_backspace_button_style())
                child.setFixedHeight(button_size)

    def get_button_style(self, button_size):
        """Get the button style with the specified size based on current theme"""
        # Calculate font size proportionally to button size
        adjusted_font_size = max(self.font_size, int(self.font_size * button_size / (self.font_size + 20)))
        
        if self.dark_mode:
            return f"""
                QPushButton {{
                    font-family: "{self.keyboard_font_family}";
                    font-size: {adjusted_font_size}px;
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #3c3c3c;
                    color: #ffffff;
                    min-width: {button_size}px;
                    min-height: {button_size}px;
                    max-width: {button_size}px;
                    max-height: {button_size}px;
                    padding: 2px;
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
                    font-family: "{self.keyboard_font_family}";
                    font-size: {adjusted_font_size}px;
                    font-weight: bold;
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #ffffff;
                    color: #000000;
                    min-width: {button_size}px;
                    min-height: {button_size}px;
                    max-width: {button_size}px;
                    max-height: {button_size}px;
                    padding: 2px;
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
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #444444;
                    color: #ffffff;
                    padding: 2px;
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
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 2px;
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
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #444444;
                    color: #ffffff;
                    padding: 2px;
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
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 2px;
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

    def create_keyboard(self):
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(2)

        # Create a single grid layout for the entire keyboard
        grid_layout = QGridLayout()
        grid_layout.setSpacing(4)  # Increased spacing to prevent overlap

        # Set button size based on font size with 20% increase
        button_size = max(55, int((self.font_size + 20) * 1.2))  # Scale button size with font size and add 20%
        
        print(f"Creating keyboard with button size: {button_size}px")

        # Row 0: Vowels
        vowels = self.keys['vowels']
        for col, key in enumerate(vowels):
            # Create button
            btn = QPushButton(key)
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(button_size))
            btn.setFixedSize(button_size, button_size)
            
            # Print debug info for first button
            if col == 0:
                print(f"Created button with text: '{key}', font: {self.keyboard_font_family}, size: {self.font_size}")

            # Only අ has a popup with variants
            if key == 'අ':
                btn.clicked.connect(lambda checked=False, k=key, b=btn: self.show_vowel_group(k, b))
            else:
                key_fixed = key
                btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))

            grid_layout.addWidget(btn, 0, col)

        # Row 1: Vowel modifiers and first consonants
        row1_keys = ['ු', 'ූ', 'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ', 'ක', 'ඛ', 'ග', 'ඝ', 'ඟ', 'ච', 'ඡ']
        for col, key in enumerate(row1_keys):
            # Create button
            btn = QPushButton(key)
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(button_size))
            btn.setFixedSize(button_size, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 1, col)

        # Row 2: More consonants
        row2_keys = ['ජ', 'ඣ', 'ඤ', 'ඥ', 'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ', 'ත', 'ථ', 'ද', 'ධ', 'න']
        for col, key in enumerate(row2_keys):
            # Create button
            btn = QPushButton(key)
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(button_size))
            btn.setFixedSize(button_size, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 2, col)

        # Row 3: More consonants
        row3_keys = ['ඳ', 'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ', 'ය', 'ර', 'ල', 'ව', 'ශ', 'ෂ', 'ස', 'හ']
        for col, key in enumerate(row3_keys):
            # Create button
            btn = QPushButton(key)
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(button_size))
            btn.setFixedSize(button_size, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 3, col)

        # Row 4: Remaining consonants and special characters
        row4_keys = ['ළ', 'ෆ', 'ං', 'ඃ', '්', 'ා', 'ැ', 'ෑ', 'ි', 'ී']
        for col, key in enumerate(row4_keys):
            # Create button
            btn = QPushButton(key)
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(button_size))
            btn.setFixedSize(button_size, button_size)
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 4, col)

        # Add Space button
        space_btn = QPushButton("Space")
        space_btn.setStyleSheet(self.get_space_button_style())
        space_btn.setFixedHeight(button_size)
        space_btn.clicked.connect(lambda checked=False, b=space_btn: self.on_key_clicked("Space", b))

        # Add Space button to span 3 columns
        grid_layout.addWidget(space_btn, 4, 10, 1, 3)

        # Add Backspace button
        backspace_btn = QPushButton("Backspace")
        backspace_btn.setStyleSheet(self.get_backspace_button_style())
        backspace_btn.setFixedHeight(button_size)
        backspace_btn.clicked.connect(lambda checked=False, b=backspace_btn: self.on_key_clicked("Backspace", b))

        # Add Backspace button to span 2 columns
        grid_layout.addWidget(backspace_btn, 4, 13, 1, 2)

        main_layout.addLayout(grid_layout)
        
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
        main_layout.addWidget(resize_hint)

        # Set size policy to make the keyboard fit within the window but allow vertical resizing
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def on_key_clicked(self, key, button):
        """Handle key clicks with visual feedback"""
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

    def show_vowel_group(self, vowel, button):
        """Show a popup with vowel variants"""
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
        for i, variant in enumerate(variants):
            btn = QPushButton(variant)
            
            # Use the same button size as the main keyboard
            btn.setFixedSize(current_button_size, current_button_size)
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(current_button_size))
            
            # Apply theme-specific styling
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

        # Position the dialog near the button
        button_pos = button.mapToGlobal(button.rect().topLeft())
        dialog.move(button_pos.x(), button_pos.y() - 80)
        
        # Make sure the dialog is visible on the current screen
        screen_geometry = self.screen().geometry()
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

        # Show the dialog
        dialog.exec_()

    def select_vowel_variant(self, dialog, vowel):
        """Handle selection of a vowel variant"""
        # Close the dialog
        dialog.accept()

        # Emit the key press signal with the selected vowel
        self.keyPressed.emit(vowel)

    def show_vowel_modifiers(self, consonant):
        """Show a dialog with vowel modifier options for the selected consonant"""
        # Calculate current button size based on keyboard height
        height_factor = self.height() / self.default_height
        current_button_size = max(46, int((self.font_size + 20) * height_factor))
        
        # Create a dialog to show vowel modifiers
        dialog = QDialog(self.parent())
        dialog.setWindowTitle(f"Vowel Modifiers for {consonant}")
        dialog.setModal(False)  # Changed to non-modal so it can be closed by clicking outside

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
        
        # Apply stylesheet which includes font settings
        btn.setStyleSheet(self.get_button_style(current_button_size))
        
        # Apply theme-specific styling
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
            
            # Apply stylesheet which includes font settings
            btn.setStyleSheet(self.get_button_style(current_button_size))
            
            # Apply theme-specific styling
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

        # Position the dialog near the cursor
        cursor_pos = QCursor.pos()
        dialog.move(cursor_pos.x() - 150, cursor_pos.y() - 150)
        
        # If we can't get cursor position, try to position relative to the keyboard
        if cursor_pos.isNull():
            keyboard_pos = self.mapToGlobal(self.rect().topLeft())
            dialog.move(keyboard_pos.x() + 100, keyboard_pos.y() - 200)
            
        # Make sure the dialog is visible on the current screen
        screen_geometry = self.screen().geometry()
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

        # Show the dialog
        dialog.exec_()

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
    
    def resizeEvent(self, event):
        """Handle resize events to update button sizes"""
        super().resizeEvent(event)
        
        # Only update if not in the middle of a resize operation
        if not self.resize_in_progress and event.size().height() != event.oldSize().height():
            self.update_buttons()
            # Emit signal with new height
            self.keyboardResized.emit(self.height())
            
    def mousePressEvent(self, event):
        """Handle mouse press events for resizing"""
        super().mousePressEvent(event)
        
        # Check if mouse is in the resize area (top 10 pixels or bottom 10 pixels)
        if event.position().y() < 10:  # Top edge for resizing down
            self.resize_in_progress = True
            self.resize_direction = "top"
            self.setCursor(Qt.SizeVerCursor)
            self.initial_mouse_pos = event.position().y()
            self.initial_height = self.height()
        elif event.position().y() > self.height() - 10:  # Bottom edge for resizing up
            self.resize_in_progress = True
            self.resize_direction = "bottom"
            self.setCursor(Qt.SizeVerCursor)
            self.initial_mouse_pos = event.position().y()
            self.initial_height = self.height()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events for resizing"""
        super().mouseMoveEvent(event)
        
        # Show resize cursor when hovering over the resize areas
        if not self.resize_in_progress:
            if event.position().y() < 10 or event.position().y() > self.height() - 10:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            
        # Perform resize if in progress
        if self.resize_in_progress:
            # Calculate new height based on resize direction
            delta = event.position().y() - self.initial_mouse_pos
            
            if self.resize_direction == "top":
                # When dragging from top, invert the delta (drag down = smaller)
                new_height = max(self.minimumHeight(), self.initial_height - delta)
            else:  # bottom
                new_height = max(self.minimumHeight(), self.initial_height + delta)
            
            # Resize the keyboard
            self.setFixedHeight(new_height)
            
            # Update buttons to match new size
            self.update_buttons()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for resizing"""
        super().mouseReleaseEvent(event)
        
        # End resize operation
        if self.resize_in_progress:
            self.resize_in_progress = False
            self.resize_direction = None
            self.setCursor(Qt.ArrowCursor)
            
            # Emit signal with new height
            self.keyboardResized.emit(self.height())