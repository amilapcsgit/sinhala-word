"""
Theme Manager for Sinhala Word Processor

This module provides theme management functionality for the application,
separating styling concerns from the main application logic.
"""

class ThemeManager:
    """
    Manages application themes and provides styling for different UI components.
    
    This class centralizes all theme-related styling to make it easier to maintain
    and update the application's appearance.
    """
    
    def __init__(self):
        """Initialize the theme manager with default theme."""
        self.current_theme = "light"  # Default theme
    
    def toggle_theme(self):
        """
        Toggle between light and dark themes.
        
        Returns:
            tuple: (theme_name, stylesheet) - The new theme name and its stylesheet
        """
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        return self.current_theme, self.get_stylesheet()
    
    def get_stylesheet(self):
        """
        Get the stylesheet for the current theme.
        
        Returns:
            str: CSS stylesheet for the current theme
        """
        if self.current_theme == "dark":
            return self.get_dark_theme()
        else:
            return self.get_light_theme()
    
    def is_dark_mode(self):
        """
        Check if the current theme is dark mode.
        
        Returns:
            bool: True if dark mode is active, False otherwise
        """
        return self.current_theme == "dark"
    
    @staticmethod
    def get_dark_theme():
        """
        Returns the CSS styling for dark theme.
        
        Returns:
            str: CSS styling for dark theme
        """
        return """
            QMainWindow, QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QTextEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #404040;
                selection-background-color: #264F78;
                selection-color: #FFFFFF;
            }
            QMenuBar, QMenu {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QMenuBar::item:selected, QMenu::item:selected {
                background-color: #1A1A1A;  /* Darker highlight color */
                color: #FFFFFF;
            }
            QToolBar {
                background-color: #1E1E1E;
                border-bottom: 1px solid #333333;
                spacing: 2px;
                padding: 2px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
                margin: 1px;
                color: #FFFFFF;
            }
            QToolBar QToolButton:hover {
                background-color: #2A2A2A;
                border: 1px solid #404040;
            }
            QToolBar QToolButton:pressed {
                background-color: #404040;
            }
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
                border: 1px solid #505050;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
            QComboBox, QFontComboBox {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #666666;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #666666;
            }
            QComboBox QAbstractItemView {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #666666;
                selection-background-color: #1A1A1A;  /* Darker selection background */
                selection-color: #FFFFFF;
                outline: 0px;
            }
            QStatusBar {
                background-color: #333333;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QDialog {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QMessageBox {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QInputDialog {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555555;
            }
        """
    
    @staticmethod
    def get_light_theme():
        """
        Returns the CSS styling for light theme.
        
        Returns:
            str: CSS styling for light theme
        """
        return """
            QMainWindow, QWidget {
                background-color: #F5F5F5;
                color: #333333;
            }
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
            }
            QMenuBar, QMenu {
                background-color: #F5F5F5;
                color: #333333;
            }
            QToolBar {
                background-color: #F8F9FA;
                border-bottom: 1px solid #E4E6E8;
                spacing: 2px;
                padding: 2px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
                margin: 1px;
                color: #444444;
            }
            QToolBar QToolButton:hover {
                background-color: #F0F2F4;
                border: 1px solid #E4E6E8;
            }
            QToolBar QToolButton:pressed {
                background-color: #E4E6E8;
            }
            QPushButton {
                background-color: #FFFFFF;
                color: #444444;
                border: 1px solid #DFE1E5;
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                border: 1px solid #C8CCD1;
            }
            QPushButton:pressed {
                background-color: #F0F2F4;
            }
            QComboBox, QFontComboBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #CCCCCC;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
                selection-background-color: #E2E2E2;
                selection-color: #333333;
                outline: 0px;
            }
            QStatusBar {
                background-color: #F0F0F0;
                color: #333333;
            }
            QLabel {
                color: #333333;
            }
            QDialog {
                background-color: #F5F5F5;
                color: #333333;
            }
            QMessageBox {
                background-color: #F5F5F5;
                color: #333333;
            }
            QInputDialog {
                background-color: #F5F5F5;
                color: #333333;
            }
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
            }
        """
