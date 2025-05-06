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
    
    # Windows 11 Fluent UI color scheme
    COLORS = {
        "light": {
            "AccentColor": "#FF005FB8",
            "AccentMouseOverColor": "#E6005FB8",
            "AccentPressedColor": "#CC005FB8",
            "AccentSelectedColor": "#FF0078D4",
            "AccentControlBorderGradientStop1Color": "#14FFFFFF",
            "AccentControlBorderGradientStop2Color": "#66000000",
            "AccentControlForegroundColor": "#FFFFFFFF",
            "AlternativeColor": "#FFF3F3F3",
            "ButtonBorderGradientStop1Color": "#0E000000",
            "ButtonBorderGradientStop2Color": "#29000000",
            "DisabledBackgroundColor": "#4DF9F9F9",
            "DisabledBorderColor": "#0F000000",
            "DisabledForegroundColor": "#FF000000",
            "FocusColor": "#E4000000",
            "FocusInnerColor": "#B3FFFFFF",
            "IconColor": "#E4000000",
            "IconSecondaryColor": "#9B000000",
            "InputBorderGradientStop1Color": "#0F000000",
            "InputBorderGradientStop2Color": "#72000000",
            "MouseOverBackgroundColor": "#B3F9F9F9",
            "MouseOverBorderGradientStop1Color": "#0F000000",
            "MouseOverBorderGradientStop2Color": "#71000000",
            "OverlayColor": "#FFFBFBFB",
            "PressedBackgroundColor": "#4DF9F9F9",
            "PrimaryBackgroundColor": "#B3FFFFFF",
            "PrimaryBorderColor": "#0F000000",
            "PrimaryForegroundColor": "#E4000000",
            "PrimarySolidBackgroundColor": "#FFFFFFFF",
            "PrimarySolidBorderColor": "#FFECECEC",
            "ReadOnlyBackgroundColor": "#E6F6F6F6",
            "ReadOnlyBorderColor": "#FFEBEBEB",
            "SecondaryBackgroundColor": "#FFEEEEEE",
            "SecondaryBorderColor": "#29000000",
            "SecondaryForegroundColor": "#9B000000",
            "SelectedColor": "#0A000000",
            "SelectedMouseOverColor": "#06000000",
            "SelectedUnfocusedColor": "#FFD9D9D9",
            "StrokeColor": "#FFC4C4C4",
            "SubtleColor": "#0A000000",
            "SubtleSecondaryColor": "#06000000",
            "TertiaryBackgroundColor": "#FFF9F9F9",
            "TertiaryBorderColor": "#FFEBEBEB",
            "TertiaryForegroundColor": "#72000000",
            "TertiarySmokeBackgroundColor": "#4D000000",
            "ValidationColor": "#FFC42B1C"
        },
        "dark": {
            "AccentColor": "#FF60CDFF",
            "AccentMouseOverColor": "#E660CDFF",
            "AccentPressedColor": "#CC60CDFF",
            "AccentSelectedColor": "#FF0078D4",
            "AccentControlBorderGradientStop1Color": "#14FFFFFF",
            "AccentControlBorderGradientStop2Color": "#23000000",
            "AccentControlForegroundColor": "#FFFFFFFF",
            "AlternativeColor": "#FF202020",
            "ButtonBorderGradientStop1Color": "#17FFFFFF",
            "ButtonBorderGradientStop2Color": "#17FFFFFF",
            "DisabledBackgroundColor": "#0BFFFFFF",
            "DisabledBorderColor": "#12FFFFFF",
            "DisabledForegroundColor": "#FFFFFFFF",
            "FocusColor": "#FFFFFFFF",
            "FocusInnerColor": "#B3000000",
            "IconColor": "#FFFFFFFF",
            "IconSecondaryColor": "#C8FFFFFF",
            "InputBorderGradientStop1Color": "#14FFFFFF",
            "InputBorderGradientStop2Color": "#8AFFFFFF",
            "MouseOverBackgroundColor": "#15FFFFFF",
            "MouseOverBorderGradientStop1Color": "#14FFFFFF",
            "MouseOverBorderGradientStop2Color": "#8AFFFFFF",
            "OverlayColor": "#FF2D2D2D",
            "PressedBackgroundColor": "#08FFFFFF",
            "PrimaryBackgroundColor": "#0FFFFFFF",
            "PrimaryBorderColor": "#12FFFFFF",
            "PrimaryForegroundColor": "#FFFFFFFF",
            "PrimarySolidBackgroundColor": "#FF1E1E1E",
            "PrimarySolidBorderColor": "#FF2C2C2C",
            "ReadOnlyBackgroundColor": "#08FFFFFF",
            "ReadOnlyBorderColor": "#FF1C1C1C",
            "SecondaryBackgroundColor": "#FF1C1C1C",
            "SecondaryBorderColor": "#18FFFFFF",
            "SecondaryForegroundColor": "#C8FFFFFF",
            "SelectedColor": "#0FFFFFFF",
            "SelectedMouseOverColor": "#0BFFFFFF",
            "SelectedUnfocusedColor": "#FF404040",
            "StrokeColor": "#FF313131",
            "SubtleColor": "#0FFFFFFF",
            "SubtleSecondaryColor": "#0BFFFFFF",
            "TertiaryBackgroundColor": "#FF282828",
            "TertiaryBorderColor": "#FF262626",
            "TertiaryForegroundColor": "#8BFFFFFF",
            "TertiarySmokeBackgroundColor": "#4D000000",
            "ValidationColor": "#FFFF99A4"
        }
    }
    
    def __init__(self):
        """Initialize the theme manager with default theme."""
        self.current_theme = "light"  # Default theme is light
    
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
        
    def get_color(self, color_name):
        """
        Get a specific color from the current theme.
        
        Args:
            color_name: The name of the color to retrieve
            
        Returns:
            str: The color value as a hex string
        """
        return self.COLORS[self.current_theme].get(color_name, "")
    
    def get_dark_theme(self):
        """
        Returns the CSS styling for dark theme using the Windows 11 Fluent UI color scheme.
        
        Returns:
            str: CSS styling for dark theme
        """
        colors = self.COLORS["dark"]
        return f"""
            QMainWindow, QWidget {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QTextEdit {{
                background-color: {colors["OverlayColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                selection-background-color: {colors["AccentColor"]};
                selection-color: {colors["AccentControlForegroundColor"]};
            }}
            QMenuBar, QMenu {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QMenuBar::item:selected, QMenu::item:selected {{
                background-color: {colors["MouseOverBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QToolBar {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                border-bottom: 1px solid {colors["StrokeColor"]};
                spacing: 2px;
                padding: 2px;
            }}
            QToolBar QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
                margin: 1px;
                color: {colors["IconColor"]};
            }}
            QToolBar QToolButton:hover {{
                background-color: {colors["MouseOverBackgroundColor"]};
                border: 1px solid {colors["MouseOverBorderGradientStop2Color"]};
            }}
            QToolBar QToolButton:pressed {{
                background-color: {colors["PressedBackgroundColor"]};
            }}
            QPushButton {{
                background-color: {colors["OverlayColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors["MouseOverBackgroundColor"]};
                border: 1px solid {colors["AccentColor"]};
            }}
            QPushButton:pressed {{
                background-color: {colors["AccentPressedColor"]};
                color: {colors["AccentControlForegroundColor"]};
            }}
            /* Specific styling for suggestion buttons */
            #suggestion_area QPushButton {{
                background-color: {colors["OverlayColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                border-radius: 4px;
                padding: 4px 8px;
                text-align: left;
                min-width: 40px;
            }}
            #suggestion_area QPushButton:hover {{
                background-color: {colors["MouseOverBackgroundColor"]};
                border: 1px solid {colors["AccentColor"]};
            }}
            #suggestion_area QPushButton:pressed {{
                background-color: {colors["AccentPressedColor"]};
                color: {colors["AccentControlForegroundColor"]};
            }}
            QComboBox, QFontComboBox {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["StrokeColor"]};
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid {colors["StrokeColor"]};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["StrokeColor"]};
                selection-background-color: {colors["SelectedColor"]};
                selection-color: {colors["PrimaryForegroundColor"]};
                outline: 0px;
            }}
            QStatusBar {{
                background-color: {colors["TertiaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QLabel {{
                color: {colors["PrimaryForegroundColor"]};
            }}
            QDialog {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QMessageBox {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QInputDialog {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QLineEdit {{
                background-color: {colors["AlternativeColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["StrokeColor"]};
            }}
            /* Suggestion label specific styling */
            #suggestion_label {{
                background-color: {colors["OverlayColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                border-radius: 8px;
                padding: 8px;
            }}
        """
    
    def get_light_theme(self):
        """
        Returns the CSS styling for light theme using the Windows 11 Fluent UI color scheme.
        
        Returns:
            str: CSS styling for light theme
        """
        colors = self.COLORS["light"]
        return f"""
            QMainWindow, QWidget {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QTextEdit {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                selection-background-color: {colors["AccentColor"]};
                selection-color: {colors["AccentControlForegroundColor"]};
            }}
            QMenuBar, QMenu {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QMenuBar::item:selected, QMenu::item:selected {{
                background-color: {colors["MouseOverBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QToolBar {{
                background-color: {colors["TertiaryBackgroundColor"]};
                border-bottom: 1px solid {colors["TertiaryBorderColor"]};
                spacing: 2px;
                padding: 2px;
            }}
            QToolBar QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
                margin: 1px;
                color: {colors["IconColor"]};
            }}
            QToolBar QToolButton:hover {{
                background-color: {colors["MouseOverBackgroundColor"]};
                border: 1px solid {colors["MouseOverBorderGradientStop2Color"]};
            }}
            QToolBar QToolButton:pressed {{
                background-color: {colors["PressedBackgroundColor"]};
            }}
            QPushButton {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors["MouseOverBackgroundColor"]};
                border: 1px solid {colors["AccentColor"]};
            }}
            QPushButton:pressed {{
                background-color: {colors["AccentPressedColor"]};
                color: {colors["AccentControlForegroundColor"]};
            }}
            /* Specific styling for suggestion buttons */
            #suggestion_area QPushButton {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                border-radius: 4px;
                padding: 4px 8px;
                text-align: left;
                min-width: 40px;
            }}
            #suggestion_area QPushButton:hover {{
                background-color: {colors["MouseOverBackgroundColor"]};
                border: 1px solid {colors["AccentColor"]};
            }}
            #suggestion_area QPushButton:pressed {{
                background-color: {colors["AccentPressedColor"]};
                color: {colors["AccentControlForegroundColor"]};
            }}
            QComboBox, QFontComboBox {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["StrokeColor"]};
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid {colors["StrokeColor"]};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["StrokeColor"]};
                selection-background-color: {colors["SelectedColor"]};
                selection-color: {colors["PrimaryForegroundColor"]};
                outline: 0px;
            }}
            QStatusBar {{
                background-color: {colors["SecondaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QLabel {{
                color: {colors["PrimaryForegroundColor"]};
            }}
            QDialog {{
                background-color: {colors["TertiaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QMessageBox {{
                background-color: {colors["TertiaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QInputDialog {{
                background-color: {colors["TertiaryBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
            }}
            QLineEdit {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["StrokeColor"]};
            }}
            /* Suggestion label specific styling */
            #suggestion_label {{
                background-color: {colors["PrimarySolidBackgroundColor"]};
                color: {colors["PrimaryForegroundColor"]};
                border: 1px solid {colors["PrimarySolidBorderColor"]};
                border-radius: 8px;
                padding: 8px;
            }}
        """
