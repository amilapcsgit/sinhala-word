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
            QComboBox, QFontComboBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #CCCCCC;
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
