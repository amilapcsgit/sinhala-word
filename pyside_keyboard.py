from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, 
                          QSizePolicy, QDialog, QLabel, QGridLayout)
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QColor, QFont

class SinhalaKeyboard(QFrame):
    """PySide6 implementation of the Sinhala Keyboard"""
    
    # Signal emitted when a key is pressed
    keyPressed = Signal(str)
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        
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
        
        # Apply initial styling based on theme
        self.update_theme()
        
        self.create_keyboard()
        
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
    
    def set_dark_mode(self, is_dark):
        """Set the keyboard theme to dark or light mode"""
        self.dark_mode = is_dark
        self.update_theme()
        # Update all existing buttons
        for child in self.findChildren(QPushButton):
            if child.text() not in ["Space", "Backspace"]:
                child.setStyleSheet(self.button_style)
            elif child.text() == "Space":
                child.setStyleSheet(self.get_space_button_style())
            elif child.text() == "Backspace":
                child.setStyleSheet(self.get_backspace_button_style())
    
    def get_light_button_style(self):
        """Get the button style for light mode"""
        return """
            QPushButton {
                font-family: "Iskoola Pota";
                font-size: 22px;
                font-weight: bold;
                border: 1px solid #aaaaaa;
                border-radius: 6px;
                background-color: #ffffff;
                color: #000000;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
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
    
    def get_dark_button_style(self):
        """Get the button style for dark mode"""
        return """
            QPushButton {
                font-family: "Iskoola Pota";
                font-size: 22px;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 6px;
                background-color: #3c3c3c;
                color: #ffffff;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
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
        
        # Row 0: Vowels
        vowels = self.keys['vowels']
        for col, key in enumerate(vowels):
            btn = QPushButton(key)
            btn.setStyleSheet(button_style)
            btn.setFixedSize(40, 40)
            
            # Only අ has a popup with variants
            if key == 'අ':
                btn.clicked.connect(lambda checked=False, k=key, b=btn: self.show_vowel_group(k, b))
            else:
                key_fixed = key
                btn.clicked.connect(lambda checked=False, k=key_fixed: self.on_key_clicked(k, btn))
            
            grid_layout.addWidget(btn, 0, col)
        
        # Row 1: Vowel modifiers and first consonants
        row1_keys = ['ු', 'ූ', 'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ', 'ක', 'ඛ', 'ග', 'ඝ', 'ඟ', 'ච', 'ඡ']
        for col, key in enumerate(row1_keys):
            btn = QPushButton(key)
            btn.setStyleSheet(button_style)
            btn.setFixedSize(40, 40)
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed: self.on_key_clicked(k, btn))
            grid_layout.addWidget(btn, 1, col)
        
        # Row 2: More consonants
        row2_keys = ['ජ', 'ඣ', 'ඤ', 'ඥ', 'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ', 'ත', 'ථ', 'ද', 'ධ', 'න']
        for col, key in enumerate(row2_keys):
            btn = QPushButton(key)
            btn.setStyleSheet(button_style)
            btn.setFixedSize(40, 40)
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed: self.on_key_clicked(k, btn))
            grid_layout.addWidget(btn, 2, col)
        
        # Row 3: More consonants
        row3_keys = ['ඳ', 'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ', 'ය', 'ර', 'ල', 'ව', 'ශ', 'ෂ', 'ස', 'හ']
        for col, key in enumerate(row3_keys):
            btn = QPushButton(key)
            btn.setStyleSheet(button_style)
            btn.setFixedSize(40, 40)
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed: self.on_key_clicked(k, btn))
            grid_layout.addWidget(btn, 3, col)
        
        # Row 4: Remaining consonants and special characters
        row4_keys = ['ළ', 'ෆ', 'ං', 'ඃ', '්', 'ා', 'ැ', 'ෑ', 'ි', 'ී']
        
        # Add Space and Backspace buttons to the last row
        for col, key in enumerate(row4_keys):
            btn = QPushButton(key)
            btn.setStyleSheet(button_style)
            btn.setFixedSize(40, 40)
            key_fixed = key
            btn.clicked.connect(lambda checked=False, k=key_fixed: self.on_key_clicked(k, btn))
            grid_layout.addWidget(btn, 4, col)
        
        # Add Space button
        space_btn = QPushButton("Space")
        space_btn.setStyleSheet(self.get_space_button_style())
        space_btn.setFixedHeight(40)
        space_btn.clicked.connect(lambda checked=False: self.on_key_clicked("Space", space_btn))
        
        # Add Space button to span 3 columns
        grid_layout.addWidget(space_btn, 4, 10, 1, 3)
        
        # Add Backspace button
        backspace_btn = QPushButton("Backspace")
        backspace_btn.setStyleSheet(self.get_backspace_button_style())
        backspace_btn.setFixedHeight(40)
        backspace_btn.clicked.connect(lambda checked=False: self.on_key_clicked("Backspace", backspace_btn))
        
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
                    if not dialog.geometry().contains(event.globalPos()):
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
        layout = QVBoxLayout(dialog)
        
        # Add title label with theme-specific styling
        title_label = QLabel(f"Select a vowel variant")
        if self.dark_mode:
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #ffffff;")
        else:
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #000000;")
        layout.addWidget(title_label)
        
        # Create grid layout for vowel buttons
        grid = QGridLayout()
        grid.setSpacing(5)
        
        # Add buttons for each vowel variant
        for i, variant in enumerate(self.vowel_groups[vowel]):
            btn = QPushButton(variant)
            btn.setFixedSize(50, 50)
            btn.setFont(QFont("Iskoola Pota", 22, QFont.Bold))
            
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
                    if not dialog.geometry().contains(event.globalPos()):
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
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Add title label with theme-specific styling
        title_label = QLabel(f"Select a vowel modifier for '{consonant}'")
        if self.dark_mode:
            title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px; color: #ffffff;")
        else:
            title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px; color: #000000;")
        layout.addWidget(title_label)
        
        # Create grid layout for modifier buttons
        grid = QGridLayout()
        grid.setSpacing(4)
        
        # Get valid modifiers for this consonant
        valid_modifiers = self.valid_modifiers.get(consonant, self.valid_modifiers['DEFAULT'])
        
        # Add buttons for each vowel modifier
        row, col = 0, 0
        max_cols = 5  # Increase number of columns in the grid
        
        # First add the base consonant (no modifier) with theme-specific styling
        base_btn = QPushButton(consonant)
        base_btn.setFixedSize(50, 50)
        base_btn.setFont(QFont("Iskoola Pota", 18, QFont.Bold))
        
        if self.dark_mode:
            base_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 6px;
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
            base_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #aaaaaa;
                    border-radius: 6px;
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
        
        base_btn.clicked.connect(lambda checked=False, c=consonant: self.select_modifier(dialog, c, ''))
        grid.addWidget(base_btn, row, col)
        
        col += 1
        if col >= max_cols:
            col = 0
            row += 1
        
        # Add buttons for each valid vowel modifier
        for modifier in valid_modifiers:
            if modifier == '':  # Skip the empty modifier (already added)
                continue
                
            # Create the combined character (consonant + modifier)
            if modifier == '්':  # Hal kirima is a special case
                combined = consonant + modifier
            elif modifier in ['ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ']:  # Modifiers that go before the consonant
                combined = modifier + consonant
            else:  # Modifiers that go after the consonant
                combined = consonant + modifier
            
            # Create button for this modifier with theme-specific styling
            btn = QPushButton(combined)
            btn.setFixedSize(50, 50)
            btn.setFont(QFont("Iskoola Pota", 18, QFont.Bold))
            
            if self.dark_mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        border: 1px solid #555555;
                        border-radius: 6px;
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
                        border-radius: 6px;
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
            
            # Use a closure to capture the current value of combined
            combined_fixed = combined  # Create a fixed reference
            btn.clicked.connect(lambda checked=False, c=combined_fixed: self.select_modifier(dialog, c, ''))
            grid.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addLayout(grid)
        
        # Set dialog properties
        dialog.setLayout(layout)
        dialog.setMinimumWidth(280)
        # Use Qt.Popup flag to make it close when clicking outside
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.Popup)
        
        # Position the dialog near the parent widget
        parent_pos = self.mapToGlobal(self.rect().center())
        dialog.move(parent_pos.x() - dialog.width()/2, parent_pos.y() - 250)
        
        # Show the dialog
        dialog.exec_()
    
    def select_modifier(self, dialog, combined_char, modifier):
        """Handle selection of a vowel modifier"""
        # Close the dialog
        dialog.accept()
        
        # Emit the key press signal with the combined character
        self.keyPressed.emit(combined_char)
        
    def show(self):
        """Show the keyboard"""
        super().show()
        
    def hide(self):
        """Hide the keyboard"""
        super().hide()