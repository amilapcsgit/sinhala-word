"""Manager for on-screen keyboard functionality."""
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class KeyboardManager:
    """Manages on-screen Sinhala keyboard.
    
    This class handles:
    - Keyboard visibility and positioning
    - Key press events
    - Keyboard layout switching
    - Keyboard customization
    """

    def __init__(self, keyboard_widget=None):
        """Initialize the keyboard manager.
        
        Args:
            keyboard_widget: Optional keyboard widget instance
        """
        self.keyboard_widget = keyboard_widget
        self.visible = False
        self.detached = False
        self.on_key_press: Optional[Callable] = None
        logger.info("KeyboardManager initialized")

    def show(self):
        """Show the on-screen keyboard."""
        if self.keyboard_widget:
            self.keyboard_widget.show()
            self.visible = True
            logger.debug("Keyboard shown")

    def hide(self):
        """Hide the on-screen keyboard."""
        if self.keyboard_widget:
            self.keyboard_widget.hide()
            self.visible = False
            logger.debug("Keyboard hidden")

    def toggle_visibility(self) -> bool:
        """Toggle keyboard visibility.
        
        Returns:
            New visibility state
        """
        if self.visible:
            self.hide()
        else:
            self.show()
        return self.visible

    def toggle_detached(self) -> bool:
        """Toggle keyboard detached/attached mode.
        
        Returns:
            New detached state
        """
        self.detached = not self.detached
        logger.info(f"Keyboard {'detached' if self.detached else 'attached'}")
        return self.detached

    def set_key_press_handler(self, handler: Callable):
        """Set the handler for key press events.
        
        Args:
            handler: Function to call when key is pressed
        """
        self.on_key_press = handler
        logger.debug("Key press handler set")

    def handle_key_press(self, key: str):
        """Handle a key press from the keyboard.
        
        Args:
            key: Key that was pressed
        """
        if self.on_key_press:
            try:
                self.on_key_press(key)
            except Exception as e:
                logger.error(f"Error handling key press: {e}", exc_info=True)

    def resize(self, width: int, height: int):
        """Resize the keyboard.
        
        Args:
            width: New width
            height: New height
        """
        if self.keyboard_widget and hasattr(self.keyboard_widget, 'resize'):
            self.keyboard_widget.resize(width, height)
            logger.debug(f"Keyboard resized to {width}x{height}")
