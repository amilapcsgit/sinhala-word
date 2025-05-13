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
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QEvent, QTimer
from PySide6.QtGui import QFont, QFontMetrics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SuggestionPopup")

class SuggestionButton(QPushButton):
    """Custom button for suggestions with improved styling and keyboard navigation."""
    
    def __init__(self, text, index, parent=None, accent_color="#0078D4"):
        super().__init__(text, parent)
        self.index = index
        self.setFocusPolicy(Qt.NoFocus)  # Don't steal focus from editor
        self.setAutoDefault(False)
        
        # Set minimum size for better usability
        self.setMinimumHeight(48)  # Increased height for better Sinhala character display
        
        # Set object name for styling
        self.setObjectName("suggestion_button")
        
        # Enable rich text interpretation - keep padding moderate to maximize text space
        self.setStyleSheet("text-align: left; padding: 6px 12px;")
        
        # Store the original text and accent color
        self.suggestion_text = text
        self.accent_color = accent_color
        
        # Add shortcut number to text if index < 9 with special formatting
        self.update_text()
        
    def update_text(self):
        """Update the button text with formatted number prefix."""
        if self.index < 9:
            # Don't use HTML, just prepend the number
            self.setText(f"{self.index+1}. {self.suggestion_text}")
        else:
            self.setText(self.suggestion_text)
            
    def set_accent_color(self, color):
        """Update the accent color for the number."""
        self.accent_color = color
        self.update_text()

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
        self.max_width = 500
        self.max_height = 400
        self.is_dark_mode = False
        self.accent_color = "#0078D4"
        
        # Set up the custom font
        self.setup_font()
        
        # Set up the UI
        self.setup_ui()
        
        # Set focus policy to ensure we don't steal focus from editor
        self.setFocusPolicy(Qt.NoFocus)
        
        # Don't show in taskbar and don't activate
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        
    def setup_font(self):
        """Set up the font using the FontManager."""
        # Import FontManager here to avoid circular imports
        from ui.font_manager import FontManager
        self.font_manager = FontManager()
        
        # Get the font family from the font manager
        self.font_family = self.font_manager.current_font
        
        # Get system DPI settings to adjust font size
        # Default to size 20 if we can't determine system settings
        try:
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
            dpi = screen.logicalDotsPerInch()
            # Scale font size based on DPI (20 at 96 DPI, up to 40 at 192 DPI)
            font_size = max(20, min(40, int(20 * dpi / 96)))
        except Exception as e:
            logger.warning(f"Error getting DPI: {e}")
            font_size = 20
        
        # Create the font with appropriate size using the font manager
        self.popup_font = self.font_manager.get_font(font_size)
        self.popup_font.setBold(False)  # Ensure it's not bold by default
        self.setFont(self.popup_font)
        
        logger.info(f"Suggestion popup using font: {self.font_family} at size {font_size}")
    
    def find_sinhala_font(self):
        """
        Legacy method kept for backward compatibility.
        Font discovery is now handled by the FontManager.
        """
        # This method is no longer needed as FontManager handles font discovery
        # Just update the font family from the font manager
        self.font_family = self.font_manager.current_font
        logger.info(f"Using font from FontManager: {self.font_family}")
        
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
        # Store the new suggestions
        self.suggestions = suggestions
        
        # Log the new suggestions for debugging
        logger.info(f"Setting {len(suggestions)} new suggestions")
        
        # Update buttons and recalculate size
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
            # Create button with accent color
            button = SuggestionButton(suggestion, i, self, self.accent_color)
            button.clicked.connect(lambda checked=False, s=suggestion: self.on_suggestion_clicked(s))
            
            # Set the custom font
            button.setFont(self.popup_font)
            
            # Set fixed height to ensure consistent sizing
            button.setMinimumHeight(48)  # Increased height for better Sinhala character display
            
            # Add to layout
            self.scroll_layout.addWidget(button)
            self.buttons.append(button)
            
        # Reset current index
        self.current_index = 0 if self.buttons else -1
        
        # Apply styling after adding to layout
        self.apply_button_styles()
        
        # Update size
        self.adjust_size()
        
    def apply_button_styles(self):
        """Apply styles to all buttons."""
        # Get theme colors (use defaults if not set)
        bg_color = getattr(self, 'button_bg', "#F0F0F0")
        text_color = getattr(self, 'text_color', "#000000")
        border_color = getattr(self, 'border_color', "#CCCCCC")
        
        # Base style for all buttons
        base_style = f"""
            text-align: left;
            padding: 6px 16px;  /* Reduced padding to maximize text space */
            margin: 2px;
            border-radius: 6px;
            border-width: 1px;
            border-style: solid;
            border-color: {border_color};
            background-color: {bg_color};
            color: {text_color};
            font-family: "{self.font_family}";
        """
        
        # Apply styles to all buttons
        for i, button in enumerate(self.buttons):
            if i == self.current_index:
                # Highlighted button
                button.setStyleSheet(f"""
                    {base_style}
                    font-weight: bold;
                    border-width: 2px;
                    border-style: solid;
                    border-color: {self.accent_color};
                """)
            else:
                button.setStyleSheet(base_style)
        
    def adjust_size(self):
        """Adjust the size of the popup based on content."""
        if not self.buttons:
            self.hide()
            return
            
        # Calculate the width based on the widest button in the current set of suggestions
        font_metrics = QFontMetrics(self.popup_font)
        width = 0
        
        # Log all button texts for debugging
        button_texts = []
        for button in self.buttons:
            button_text = button.text()
            button_texts.append(button_text)
            # Get the actual text width for each suggestion with extra padding for safety
            text_width = font_metrics.horizontalAdvance(button_text) + 60  # Increased padding
            width = max(width, text_width)
        
        # Log the button texts and calculated width
        logger.info(f"Button texts: {button_texts}")
        logger.info(f"Calculated width before limit: {width}")
        
        # Ensure minimum width for better usability
        width = max(width, 200)  # Minimum width of 200 pixels
            
        # Limit width to max_width
        width = min(width, self.max_width)
        
        # Calculate height based on number of buttons
        button_height = self.buttons[0].sizeHint().height() if self.buttons else 48  # Increased height for Sinhala characters
        # Use minimal spacing between buttons to maximize visible area
        height = min(len(self.buttons) * (button_height + 2) + 8, self.max_height)
        
        # Log the final dimensions
        logger.info(f"Adjusting popup size to width: {width}, height: {height}")
        
        # Set the size with a slight delay to ensure it takes effect
        self.resize(width, height)
        
        # Force layout update
        self.updateGeometry()
        self.scroll_container.updateGeometry()
        
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
        
        # Log the suggestions we're about to show
        logger.info(f"Showing popup with suggestions: {suggestions}")
            
        # Set suggestions and update buttons
        self.set_suggestions(suggestions)
        
        # Force size recalculation
        self.adjust_size()
        
        # Position the popup near the cursor
        self.position_near_cursor(cursor_rect, editor_rect)
        
        # Set the first button as the current one, but don't focus it
        if self.buttons:
            self.current_index = 0
            
        # Show the popup without stealing focus or activating
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        
        # Install event filter on the editor to catch space key events
        # This allows us to hide the popup when space is pressed
        editor = self.parent().editor
        editor.installEventFilter(self)
        
        # Show the popup
        self.show()
        
        # Force layout update after showing
        QTimer.singleShot(10, self.updateGeometry)
        
        # Make sure the editor keeps focus
        editor.activateWindow()
        editor.setFocus()
            
    def hide(self):
        """Override hide to remove event filter from editor."""
        # Remove event filter from editor when hiding
        try:
            editor = self.parent().editor
            if editor:
                editor.removeEventFilter(self)
                logger.info("Removed event filter from editor")
        except Exception as e:
            logger.error(f"Error removing event filter: {e}")
            
        # Call parent class hide method
        super().hide()
        
    def on_suggestion_clicked(self, suggestion):
        """Handle a suggestion being clicked."""
        self.suggestionSelected.emit(suggestion)
        self.hide()
        
    def select_suggestion(self, index):
        """Select the suggestion at the given index."""
        if 0 <= index < len(self.suggestions):
            self.suggestionSelected.emit(self.suggestions[index])
            self.hide()  # This will call our custom hide method
            
    def navigate_to(self, index):
        """Navigate to the button at the given index."""
        if 0 <= index < len(self.buttons):
            # Update current index
            self.current_index = index
            
            # Apply styles to all buttons
            self.apply_button_styles()
            
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
                
            # Handle Space to hide the popup without selecting
            elif key == Qt.Key_Space:
                logger.info("Space key pressed - hiding suggestion popup")
                self.hide()
                return False  # Don't consume the event, let it pass to editor
                
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
            self.bg_color = theme_colors.get("OverlayColor", "#2D2D2D")
            self.text_color = theme_colors.get("PrimaryForegroundColor", "#FFFFFF")
            self.border_color = theme_colors.get("PrimarySolidBorderColor", "#3F3F3F")
            self.button_bg = theme_colors.get("OverlayColor", "#3F3F3F")
            self.button_hover = theme_colors.get("MouseOverBackgroundColor", "#505050")
            self.accent_color = theme_colors.get("AccentColor", "#60CDFF")
        else:
            self.bg_color = theme_colors.get("PrimarySolidBackgroundColor", "#F9F9F9")
            self.text_color = theme_colors.get("PrimaryForegroundColor", "#000000")
            self.border_color = theme_colors.get("PrimarySolidBorderColor", "#CCCCCC")
            self.button_bg = theme_colors.get("PrimarySolidBackgroundColor", "#F0F0F0")
            self.button_hover = theme_colors.get("MouseOverBackgroundColor", "#E5E5E5")
            self.accent_color = theme_colors.get("AccentColor", "#0078D4")
            
        # Set stylesheet for the popup container
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: 6px;
            }}
            
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QWidget#scroll_container {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Update accent color for all buttons
        for button in self.buttons:
            if isinstance(button, SuggestionButton):
                button.set_accent_color(self.accent_color)
                
        # Reapply styling to all buttons
        self.apply_button_styles()
