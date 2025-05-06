"""
Suggestion Popup Widget for Sinhala Word Processor

This module provides a custom popup widget for displaying transliteration suggestions
near the cursor position, with support for keyboard navigation and mouse interaction.
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QEvent
from PySide6.QtGui import QFont, QFontMetrics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SuggestionPopup")

class SuggestionButton(QPushButton):
    """Custom button for suggestions with improved styling and keyboard navigation."""
    
    def __init__(self, text, index, parent=None):
        super().__init__(text, parent)
        self.index = index
        self.setFocusPolicy(Qt.NoFocus)  # Don't steal focus from editor
        self.setAutoDefault(False)
        
        # Set minimum size for better usability
        self.setMinimumHeight(30)
        
        # Set object name for styling
        self.setObjectName("suggestion_button")
        
        # Add shortcut number to text if index < 9
        if index < 9:
            self.setText(f"{index+1}. {text}")
        else:
            self.setText(text)

class SuggestionPopup(QWidget):
    """
    A tooltip-style popup widget that displays suggestions near the cursor position.
    
    Features:
    - Displays suggestions as clickable buttons
    - Supports keyboard navigation (Tab, arrow keys)
    - Positions itself near the cursor
    - Adapts to available screen space
    - Supports theme changes
    - Does not interfere with text input
    """
    
    # Signal emitted when a suggestion is selected
    suggestionSelected = Signal(str)
    
    def __init__(self, parent=None):
        # Use ToolTip window type to avoid stealing focus
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        
        # Initialize attributes
        self.suggestions = []
        self.buttons = []
        self.current_index = -1
        self.max_width = 400
        self.max_height = 300
        self.is_dark_mode = False
        
        # Set up the UI
        self.setup_ui()
        
        # Set focus policy to ensure we don't steal focus from editor
        self.setFocusPolicy(Qt.NoFocus)
        
        # Don't show in taskbar and don't activate
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        
        # Create a scroll area for suggestions
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a container widget for the scroll area
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_container)
        self.scroll_layout.setContentsMargins(2, 2, 2, 2)
        self.scroll_layout.setSpacing(2)
        
        # Set the container as the scroll area widget
        self.scroll_area.setWidget(self.scroll_container)
        
        # Add the scroll area to the main layout
        self.main_layout.addWidget(self.scroll_area)
        
        # Set size policies
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        # Set a border and background
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
        """)
        
    def set_suggestions(self, suggestions):
        """Set the suggestions to display."""
        self.suggestions = suggestions
        self.update_buttons()
        
    def update_buttons(self):
        """Update the buttons based on the current suggestions."""
        # Clear existing buttons
        for button in self.buttons:
            self.scroll_layout.removeWidget(button)
            button.deleteLater()
        self.buttons.clear()
        
        # Create new buttons for each suggestion
        for i, suggestion in enumerate(self.suggestions):
            button = SuggestionButton(suggestion, i, self)
            button.clicked.connect(lambda checked=False, s=suggestion: self.on_suggestion_clicked(s))
            
            # Highlight the first button
            if i == 0:
                button.setStyleSheet("font-weight: bold; border-width: 2px;")
                
            self.scroll_layout.addWidget(button)
            self.buttons.append(button)
            
        # Reset current index
        self.current_index = 0 if self.buttons else -1
        
        # Update size
        self.adjust_size()
        
    def adjust_size(self):
        """Adjust the size of the popup based on content."""
        if not self.buttons:
            self.hide()
            return
            
        # Calculate the width based on the widest button
        font_metrics = QFontMetrics(self.font())
        width = 0
        for button in self.buttons:
            text_width = font_metrics.horizontalAdvance(button.text()) + 40  # Add padding
            width = max(width, text_width)
            
        # Limit width to max_width
        width = min(width, self.max_width)
        
        # Calculate height based on number of buttons
        button_height = self.buttons[0].sizeHint().height() if self.buttons else 30
        height = min(len(self.buttons) * (button_height + 2) + 10, self.max_height)
        
        # Set the size
        self.resize(width, height)
        
    def position_near_cursor(self, cursor_rect, editor_rect):
        """Position the popup near the cursor."""
        # Get the editor widget
        editor = self.parent().editor
        
        # Get the cursor position in editor coordinates
        cursor_pos = QPoint(cursor_rect.x(), cursor_rect.y() + cursor_rect.height())
        
        # Convert to global coordinates
        global_cursor_pos = editor.mapToGlobal(cursor_pos)
        
        # Calculate the position to ensure the popup is visible
        screen_rect = self.screen().availableGeometry()
        
        # Default position below the cursor
        x = global_cursor_pos.x()
        y = global_cursor_pos.y() + 5  # Add a small offset for better visibility
        
        # Adjust if the popup would go off the right edge
        if x + self.width() > screen_rect.right():
            x = screen_rect.right() - self.width()
            
        # Adjust if the popup would go off the bottom edge
        if y + self.height() > screen_rect.bottom():
            # Position above the cursor instead
            y = global_cursor_pos.y() - cursor_rect.height() - self.height() - 5
            
        # Ensure the popup is not positioned off the left or top edge
        x = max(x, screen_rect.left())
        y = max(y, screen_rect.top())
        
        # Log the positioning for debugging
        logger = logging.getLogger("SuggestionPopup")
        logger.info(f"Positioning popup at ({x}, {y}) relative to cursor at {global_cursor_pos}")
        
        # Move the popup to the calculated position
        self.move(x, y)
        
    def show_popup(self, suggestions, cursor_rect, editor_rect):
        """Show the popup with the given suggestions near the cursor."""
        if not suggestions:
            self.hide()
            return
            
        self.set_suggestions(suggestions)
        self.position_near_cursor(cursor_rect, editor_rect)
        
        # Set the first button as the current one, but don't focus it
        if self.buttons:
            self.current_index = 0
            
        # Show the popup without stealing focus or activating
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.show()
        
        # Make sure the editor keeps focus
        self.parent().editor.activateWindow()
        self.parent().editor.setFocus()
            
    def on_suggestion_clicked(self, suggestion):
        """Handle a suggestion being clicked."""
        self.suggestionSelected.emit(suggestion)
        self.hide()
        
    def select_suggestion(self, index):
        """Select the suggestion at the given index."""
        if 0 <= index < len(self.suggestions):
            self.suggestionSelected.emit(self.suggestions[index])
            self.hide()
            
    def navigate_to(self, index):
        """Navigate to the button at the given index."""
        if 0 <= index < len(self.buttons):
            # Reset styling on all buttons
            for button in self.buttons:
                button.setStyleSheet("")
            
            # Update current index
            self.current_index = index
            
            # Highlight the selected button
            self.buttons[index].setStyleSheet("font-weight: bold; border-width: 2px;")
            
            # Log navigation
            logger.info(f"Navigated to suggestion {index+1}: {self.suggestions[index]}")
            
    def navigate_next(self):
        """Navigate to the next suggestion."""
        if self.buttons:
            next_index = (self.current_index + 1) % len(self.buttons)
            self.navigate_to(next_index)
            return True
        return False
            
    def navigate_previous(self):
        """Navigate to the previous suggestion."""
        if self.buttons:
            prev_index = (self.current_index - 1) % len(self.buttons)
            self.navigate_to(prev_index)
            return True
        return False
            
    def eventFilter(self, obj, event):
        """Filter events to handle keyboard navigation."""
        # Only handle events for this widget, not for the editor
        if obj is not self:
            return False
            
        if event.type() == QEvent.KeyPress:
            key = event.key()
            
            # Handle Tab key for navigation
            if key == Qt.Key_Tab:
                self.navigate_next()
                return True
                
            # Handle Shift+Tab for reverse navigation
            elif key == Qt.Key_Backtab:
                self.navigate_previous()
                return True
                
            # Handle arrow keys
            elif key == Qt.Key_Down:
                self.navigate_next()
                return True
                
            elif key == Qt.Key_Up:
                self.navigate_previous()
                return True
                
            # Handle Enter/Return to select current suggestion
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                if 0 <= self.current_index < len(self.suggestions):
                    self.select_suggestion(self.current_index)
                return True
                
            # Handle Escape to close the popup
            elif key == Qt.Key_Escape:
                self.hide()
                return True
                
            # Handle number keys 1-9 to select suggestions
            elif Qt.Key_1 <= key <= Qt.Key_9:
                index = key - Qt.Key_1
                if index < len(self.suggestions):
                    self.select_suggestion(index)
                return True
                
            # Let all other keys pass through to the editor
            return False
                
        return super().eventFilter(obj, event)
        
    def update_theme(self, is_dark_mode, theme_colors):
        """Update the theme of the popup."""
        self.is_dark_mode = is_dark_mode
        
        # Apply theme colors
        if is_dark_mode:
            bg_color = theme_colors.get("OverlayColor", "#2D2D2D")
            text_color = theme_colors.get("PrimaryForegroundColor", "#FFFFFF")
            border_color = theme_colors.get("PrimarySolidBorderColor", "#3F3F3F")
            button_bg = theme_colors.get("OverlayColor", "#3F3F3F")
            button_hover = theme_colors.get("MouseOverBackgroundColor", "#505050")
            accent_color = theme_colors.get("AccentColor", "#60CDFF")
        else:
            bg_color = theme_colors.get("PrimarySolidBackgroundColor", "#F9F9F9")
            text_color = theme_colors.get("PrimaryForegroundColor", "#000000")
            border_color = theme_colors.get("PrimarySolidBorderColor", "#CCCCCC")
            button_bg = theme_colors.get("PrimarySolidBackgroundColor", "#F0F0F0")
            button_hover = theme_colors.get("MouseOverBackgroundColor", "#E5E5E5")
            accent_color = theme_colors.get("AccentColor", "#0078D4")
            
        # Set stylesheet for the popup
        self.setStyleSheet(f"""
            SuggestionPopup {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QPushButton#suggestion_button {{
                background-color: {button_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 6px 10px;
                text-align: left;
            }}
            
            QPushButton#suggestion_button:hover {{
                background-color: {button_hover};
                border: 1px solid {accent_color};
            }}
            
            QPushButton#suggestion_button:focus {{
                background-color: {button_hover};
                border: 2px solid {accent_color};
                outline: none;
            }}
        """)