from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, 
                          QSizePolicy, QDialog, QLabel, QGridLayout)
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QColor, QFont, QCursor

class SinhalaKeyboard(QFrame):
    """PySide6 implementation of the Sinhala Keyboard"""

    # Signal emitted when a key is pressed
    keyPressed = Signal(str)

    def __init__(self, parent=None, dark_mode=False, font_size=26):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.font_size = font_size
        self.keyboard_font_family = "Iskoola Pota"  # Default fallback
        
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
        
    def load_keyboard_font(self):
        """Load Sinhala font for the keyboard buttons"""
        import os
        from PySide6.QtGui import QFontDatabase
        
        # Only check for specific Sinhala fonts we need
        system_sinhala_fonts = ["Iskoola Pota", "Nirmala UI", "Dinamika", "Malithi Web"]
        
        # First try to use system Sinhala fonts that are known to work well
        for font in system_sinhala_fonts:
                self.keyboard_font_family = font
                print(f"Using system Sinhala font for keyboard: {font}")
                return
        
        # If no system Sinhala fonts found, try to load embedded fonts
        # Path to the fonts directory
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        
        # Check if fonts directory exists
        if os.path.exists(fonts_dir):
            print(f"Fonts directory found: {fonts_dir}")
            # List all font files
            font_files = [f for f in os.listdir(fonts_dir) if f.lower().endswith(('.ttf', '.otf'))]
            print(f"Font files found: {', '.join(font_files)}")
            
            # Try UN-Ganganee first
            un_ganganee_path = os.path.join(fonts_dir, "un-ganganee.ttf")
            if os.path.exists(un_ganganee_path):
                print(f"Loading UN-Ganganee from: {un_ganganee_path}")
                font_id = QFontDatabase.addApplicationFont(un_ganganee_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.keyboard_font_family = families[0]
                        print(f"Successfully loaded UN-Ganganee font for keyboard: {self.keyboard_font_family}")
                        return
                    else:
                        print("Failed to get font families for UN-Ganganee")
                else:
                    print("Failed to add UN-Ganganee font")
            else:
                print(f"UN-Ganganee font not found at: {un_ganganee_path}")
            
            # If UN-Ganganee not found, try any Sinhala font
            for font_file in font_files:
                font_path = os.path.join(fonts_dir, font_file)
                print(f"Trying to load font: {font_path}")
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.keyboard_font_family = families[0]
                        print(f"Successfully loaded alternative Sinhala font for keyboard: {self.keyboard_font_family}")
                        return
                    else:
                        print(f"No families found for font: {font_file}")
                else:
                    print(f"Failed to add font: {font_file}")
        else:
            print(f"Fonts directory not found: {fonts_dir}")
        
        # Fallback to a generic sans-serif font if no Sinhala fonts found
        print("Falling back to generic sans-serif font for keyboard")
        self.keyboard_font_family = "Arial"
        # Don't call self.load_keyboard_font() again to avoid infinite recursion

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
        button_size = max(46, self.font_size + 20)  # Scale button size with font size
        
        # Update all existing buttons
        for child in self.findChildren(QPushButton):
            if child.text() not in ["Space", "Backspace"]:
                child.setStyleSheet(self.button_style)
                child.setFixedSize(button_size, button_size)
            elif child.text() == "Space":
                child.setStyleSheet(self.get_space_button_style())
                child.setFixedHeight(button_size)
            elif child.text() == "Backspace":
                child.setStyleSheet(self.get_backspace_button_style())
                child.setFixedHeight(button_size)

    def get_light_button_style(self):
        """Get the button style for light mode"""
        # Use the loaded font family and specified font size
        button_size = max(46, self.font_size + 20)  # Scale button size with font size
        return f"""
            QPushButton {{
                font-family: "{self.keyboard_font_family}";
                font-size: {self.font_size}px;
                font-weight: bold;
                border: 1px solid #aaaaaa;
                border-radius: 6px;
                background-color: #ffffff;
                color: #000000;
                min-width: {button_size}px;
                min-height: {button_size}px;
                max-width: {button_size}px;
                max-height: {button_size}px;
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

    def get_dark_button_style(self):
        """Get the button style for dark mode"""
        # Use the loaded font family and specified font size
        button_size = max(46, self.font_size + 20)  # Scale button size with font size
        return f"""
            QPushButton {{
                font-family: "{self.keyboard_font_family}";
                font-size: {self.font_size}px;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 6px;
                background-color: #3c3c3c;
                color: #ffffff;
                min-width: {button_size}px;
                min-height: {button_size}px;
                max-width: {button_size}px;
                max-height: {button_size}px;
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

    def get_space_button_style(self):
        """Get the style for the Space button based on current theme"""
        if self.dark_mode:
            return """
                QPushButton {
                    font-family: "Segoe UI";
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #444444;
                    color: #ffffff;
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
                    font-family: "Segoe UI";
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    color: #000000;
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
                    font-family: "Segoe UI";
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    background-color: #444444;
                    color: #ffffff;
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
                    font-family: "Segoe UI";
                    font-size: 16px;
                    font-weight: bold;
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
                    background-color: #f0f0f0;
                    color: #000000;
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

        # Use the button style based on current theme
        button_style = self.button_style

        # Create a single grid layout for the entire keyboard
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)

        # Set button size based on font size
        button_size = max(46, self.font_size + 20)  # Scale button size with font size
        
        print(f"Creating keyboard with button size: {button_size}px")

        # Row 0: Vowels
        vowels = self.keys['vowels']
        for col, key in enumerate(vowels):
            # Create button with explicit font
            btn = QPushButton(key)
            
            # Set explicit font for the button
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn.setFont(btn_font)
            
            # Apply stylesheet
            btn.setStyleSheet(button_style)
            btn.setFixedSize(button_size, button_size)  # Larger buttons for better visibility
            
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
            # Create button with explicit font
            btn = QPushButton(key)
            
            # Set explicit font for the button
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn.setFont(btn_font)
            
            # Apply stylesheet
            btn.setStyleSheet(button_style)
            btn.setFixedSize(button_size, button_size)  # Larger buttons for better visibility
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 1, col)

        # Row 2: More consonants
        row2_keys = ['ජ', 'ඣ', 'ඤ', 'ඥ', 'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ', 'ත', 'ථ', 'ද', 'ධ', 'න']
        for col, key in enumerate(row2_keys):
            # Create button with explicit font
            btn = QPushButton(key)
            
            # Set explicit font for the button
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn.setFont(btn_font)
            
            # Apply stylesheet
            btn.setStyleSheet(button_style)
            btn.setFixedSize(button_size, button_size)  # Larger buttons for better visibility
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 2, col)

        # Row 3: More consonants
        row3_keys = ['ඳ', 'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ', 'ය', 'ර', 'ල', 'ව', 'ශ', 'ෂ', 'ස', 'හ']
        for col, key in enumerate(row3_keys):
            # Create button with explicit font
            btn = QPushButton(key)
            
            # Set explicit font for the button
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn.setFont(btn_font)
            
            # Apply stylesheet
            btn.setStyleSheet(button_style)
            btn.setFixedSize(button_size, button_size)  # Larger buttons for better visibility
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 3, col)

        # Row 4: Remaining consonants and special characters
        row4_keys = ['ළ', 'ෆ', 'ං', 'ඃ', '්', 'ා', 'ැ', 'ෑ', 'ි', 'ී']
        for col, key in enumerate(row4_keys):
            # Create button with explicit font
            btn = QPushButton(key)
            
            # Set explicit font for the button
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn.setFont(btn_font)
            
            # Apply stylesheet
            btn.setStyleSheet(button_style)
            btn.setFixedSize(button_size, button_size)  # Larger buttons for better visibility
            
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed, b=btn: self.on_key_clicked(k, b))
            grid_layout.addWidget(btn, 4, col)

        # Add Space button
        space_btn = QPushButton("Space")
        
        # Set explicit font for the button (use system font for English text)
        space_font = QFont("Arial", self.font_size - 4)
        space_btn.setFont(space_font)
        
        space_btn.setStyleSheet(self.get_space_button_style())
        space_btn.setFixedHeight(button_size)
        space_btn.clicked.connect(lambda checked=False, b=space_btn: self.on_key_clicked("Space", b))

        # Add Space button to span 3 columns
        grid_layout.addWidget(space_btn, 4, 10, 1, 3)

        # Add Backspace button
        backspace_btn = QPushButton("Backspace")
        
        # Set explicit font for the button (use system font for English text)
        backspace_font = QFont("Arial", self.font_size - 4)
        backspace_btn.setFont(backspace_font)
        
        backspace_btn.setStyleSheet(self.get_backspace_button_style())
        backspace_btn.setFixedHeight(button_size)
        backspace_btn.clicked.connect(lambda checked=False, b=backspace_btn: self.on_key_clicked("Backspace", b))

        # Add Backspace button to span 2 columns
        grid_layout.addWidget(backspace_btn, 4, 13, 1, 2)

        main_layout.addLayout(grid_layout)

        # Set size policy to make the keyboard fit within the window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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
        label.setFont(QFont("Arial", self.font_size - 8))  # Use a slightly smaller font for the label
        if self.dark_mode:
            label.setStyleSheet(f"color: #ffffff; font-size: {self.font_size - 8}px;")
        else:
            label.setStyleSheet(f"color: #000000; font-size: {self.font_size - 8}px;")
        layout.addWidget(label)

        # Create a grid for the vowel variants
        grid = QGridLayout()
        grid.setSpacing(5)

        # Add buttons for each variant
        variants = self.vowel_groups[vowel]
        for i, variant in enumerate(variants):
            btn = QPushButton(variant)
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn_font.setBold(True)
            btn.setFont(btn_font)
            
            # Set fixed size based on font size
            button_size = max(46, self.font_size + 20)
            btn.setFixedSize(button_size, button_size)
            
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
        label.setFont(QFont("Arial", self.font_size - 8))  # Use a slightly smaller font for the label
        if self.dark_mode:
            label.setStyleSheet(f"color: #ffffff; font-size: {self.font_size - 8}px;")
        else:
            label.setStyleSheet(f"color: #000000; font-size: {self.font_size - 8}px;")
        layout.addWidget(label)

        # Create a grid for the vowel modifiers
        grid = QGridLayout()
        grid.setSpacing(5)

        # Get valid modifiers for this consonant
        valid_modifiers = self.valid_modifiers.get(consonant, self.valid_modifiers['DEFAULT'])

        # Add buttons for each modifier
        # First add the base consonant (no modifier)
        btn = QPushButton(consonant)
        btn_font = QFont(self.keyboard_font_family, self.font_size)
        btn_font.setBold(True)
        btn.setFont(btn_font)
        
        # Set fixed size based on font size
        button_size = max(46, self.font_size + 20)
        btn.setFixedSize(button_size, button_size)
        
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
            btn_font = QFont(self.keyboard_font_family, self.font_size)
            btn_font.setBold(True)
            btn.setFont(btn_font)
            
            # Set fixed size based on font size
            button_size = max(46, self.font_size + 20)
            btn.setFixedSize(button_size, button_size)
            
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