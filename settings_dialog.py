"""
Settings dialog for the Sinhala Word Processor.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSpinBox, QCheckBox, QTabWidget, QWidget,
    QGroupBox, QFormLayout, QSlider
)
import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase

class SettingsDialog(QDialog):
    """Settings dialog for the Sinhala Word Processor."""
    
    # Signal emitted when settings are applied
    settingsApplied = Signal(dict)
    
    def __init__(self, parent=None, preferences=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        
        # Store preferences
        self.preferences = preferences or {}
        
        # Create the UI
        self.create_ui()
        
        # Load current settings
        self.load_settings()
    
    def create_ui(self):
        """Create the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Font settings group
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)
        
        # Font family
        self.font_combo = QComboBox()
        # Only load Sinhala fonts from our application
        sinhala_fonts = self.get_loaded_sinhala_fonts()
        for family in sinhala_fonts:
            self.font_combo.addItem(family)
        font_layout.addRow("Font:", self.font_combo)
        
        # Font size
        self.font_size_combo = QComboBox()
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]:
            self.font_size_combo.addItem(str(size), size)
        font_layout.addRow("Font Size:", self.font_size_combo)
        
        general_layout.addWidget(font_group)
        
        # Keyboard settings group
        keyboard_group = QGroupBox("Keyboard Settings")
        keyboard_layout = QFormLayout(keyboard_group)
        
        # Keyboard font size
        self.keyboard_font_size = QSpinBox()
        self.keyboard_font_size.setMinimum(16)
        self.keyboard_font_size.setMaximum(48)
        self.keyboard_font_size.setSingleStep(2)
        keyboard_layout.addRow("Keyboard Font Size:", self.keyboard_font_size)
        
        # Show keyboard checkbox
        self.show_keyboard = QCheckBox("Show Keyboard")
        keyboard_layout.addRow("", self.show_keyboard)
        
        general_layout.addWidget(keyboard_group)
        
        # Input settings group
        input_group = QGroupBox("Input Settings")
        input_layout = QFormLayout(input_group)
        
        # Singlish enabled checkbox
        self.singlish_enabled = QCheckBox("Enable Singlish Input")
        input_layout.addRow("", self.singlish_enabled)
        
        # Show suggestions checkbox
        self.show_suggestions = QCheckBox("Show Suggestions")
        input_layout.addRow("", self.show_suggestions)
        
        general_layout.addWidget(input_group)
        
        # Add general tab
        self.tabs.addTab(general_tab, "General")
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        main_layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings into the UI."""
        # Font
        font_index = self.font_combo.findText(self.preferences.get("font", "UN-Ganganee"))
        if font_index >= 0:
            self.font_combo.setCurrentIndex(font_index)
        
        # Font size
        font_size = self.preferences.get("font_size", 14)
        font_size_index = self.font_size_combo.findData(font_size)
        if font_size_index >= 0:
            self.font_size_combo.setCurrentIndex(font_size_index)
        
        # Keyboard font size
        self.keyboard_font_size.setValue(self.preferences.get("keyboard_font_size", 26))
        
        # Show keyboard
        self.show_keyboard.setChecked(self.preferences.get("show_keyboard", True))
        
        # Singlish enabled
        self.singlish_enabled.setChecked(self.preferences.get("singlish_enabled", True))
        
        # Show suggestions
        self.show_suggestions.setChecked(self.preferences.get("show_suggestions", True))
    
    def get_settings(self):
        """Get the current settings from the UI."""
        settings = {}
        
        # Font
        settings["font"] = self.font_combo.currentText()
        
        # Font size
        settings["font_size"] = self.font_size_combo.currentData()
        
        # Keyboard font size
        settings["keyboard_font_size"] = self.keyboard_font_size.value()
        
        # Show keyboard
        settings["show_keyboard"] = self.show_keyboard.isChecked()
        
        # Singlish enabled
        settings["singlish_enabled"] = self.singlish_enabled.isChecked()
        
        # Show suggestions
        settings["show_suggestions"] = self.show_suggestions.isChecked()
        
        return settings
    
    def apply_settings(self):
        """Apply the current settings."""
        settings = self.get_settings()
        self.settingsApplied.emit(settings)
    
    def get_loaded_sinhala_fonts(self):
        """Get only the Sinhala fonts that have been loaded by the application."""
        # Get the fonts directory
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        if not os.path.exists(fonts_dir):
            # Try alternate path
            fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
        
        # If we still don't have a valid fonts directory, return a default list
        if not os.path.exists(fonts_dir):
            return ["UN-Ganganee", "Iskoola Pota", "Nirmala UI"]
        
        # Get the fonts that we've loaded from our fonts directory
        loaded_fonts = []
        for font_file in os.listdir(fonts_dir):
            if font_file.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(fonts_dir, font_file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    loaded_fonts.extend(families)
        
        # Add some common system Sinhala fonts as fallbacks
        fallback_fonts = ["Iskoola Pota", "Nirmala UI", "Dinamika", "Malithi Web"]
        for font in fallback_fonts:
            if font not in loaded_fonts:
                loaded_fonts.append(font)
        
        return loaded_fonts
        
    def accept(self):
        """Accept the dialog and apply settings."""
        self.apply_settings()
        super().accept()