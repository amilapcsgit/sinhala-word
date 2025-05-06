"""
Sinhala Input Handler Module

This module provides a clean separation between the input handling logic and the UI.
It handles the Singlish to Sinhala transliteration, suggestions, and buffer management.
"""

import logging
import re
from PySide6.QtCore import QObject, Signal, Qt, QTimer
from PySide6.QtGui import QTextCursor

# Set up logging
logger = logging.getLogger("SinhalaInputHandler")

class SinhalaInputHandler(QObject):
    """
    Handles Singlish to Sinhala transliteration and suggestions.
    
    This class is responsible for:
    - Managing the input buffer
    - Providing suggestions
    - Transliterating Singlish to Sinhala
    - Handling keyboard input
    
    It emits signals when suggestions change or when text needs to be replaced.
    """
    
    # Signals
    suggestions_changed = Signal(list)  # Emitted when suggestions change
    buffer_committed = Signal(str, str)  # Emitted when buffer is committed (original, transliterated)
    buffer_cleared = Signal()  # Emitted when buffer is cleared
    
    def __init__(self, transliterator, phonetic_fallback_func):
        """
        Initialize the input handler.
        
        Args:
            transliterator: An object with a transliterate method
            phonetic_fallback_func: A function to use for phonetic fallback
        """
        super().__init__()
        
        # Core components
        self.transliterator = transliterator
        self.phonetic_fallback = phonetic_fallback_func
        
        # State
        self.buffer = []
        self.word_start_pos = None
        self.current_suggestions = []
        self.enabled = True
        self.suggestions_enabled = True
        
    def set_enabled(self, enabled):
        """Enable or disable Singlish input."""
        self.enabled = enabled
        if not enabled:
            self.clear_buffer()
            
    def set_suggestions_enabled(self, enabled):
        """Enable or disable suggestions."""
        self.suggestions_enabled = enabled
        if not enabled:
            self.clear_suggestions()
            
    def clear_buffer(self):
        """Clear the input buffer and reset state."""
        self.buffer = []
        self.word_start_pos = None
        self.clear_suggestions()
        self.buffer_cleared.emit()
        
    def clear_suggestions(self):
        """Clear the current suggestions."""
        self.current_suggestions = []
        self.suggestions_changed.emit([])
        
    def handle_key_press(self, key, text, cursor_position):
        """
        Handle a key press event.
        
        Args:
            key: The Qt key code
            text: The text from the key press
            cursor_position: The current cursor position
            
        Returns:
            bool: True if the event was handled and should be consumed
        """
        if not self.enabled:
            return False
            
        # Handle suggestion selection keys
        if self.suggestions_enabled and self.current_suggestions:
            # Enter key - accept first suggestion
            if key in (Qt.Key_Return, Qt.Key_Enter):
                if self.current_suggestions:
                    self.accept_suggestion(self.current_suggestions[0])
                    return True
                    
            # Space key - accept first suggestion and add space
            elif key == Qt.Key_Space:
                if self.current_suggestions:
                    self.accept_suggestion(self.current_suggestions[0])
                    # Space will be handled by the editor
                    return False
                    
            # Escape key - clear suggestions
            elif key == Qt.Key_Escape:
                self.clear_buffer()
                return True
                
            # Number keys 1-9 - accept corresponding suggestion
            elif Qt.Key_1 <= key <= Qt.Key_9:
                index = key - Qt.Key_1
                if index < len(self.current_suggestions):
                    self.accept_suggestion(self.current_suggestions[index])
                    return True
        
        # Backspace key - remove last character from buffer
        if key == Qt.Key_Backspace:
            if self.buffer:
                self.buffer.pop()
                if self.buffer and self.suggestions_enabled:
                    self.update_suggestions()
                else:
                    self.clear_suggestions()
            return False  # Let the editor handle the backspace
            
        # Alphanumeric keys - add to buffer
        if text.isalnum() and len(text) == 1:
            if not self.buffer:
                self.word_start_pos = cursor_position
            self.buffer.append(text)
            if self.suggestions_enabled:
                self.update_suggestions()
            return False  # Let the editor handle the character insertion
            
        # Any other key - commit buffer
        if self.buffer:
            self.commit_buffer()
            
        return False
        
    def handle_keyboard_input(self, char, cursor_position):
        """
        Handle input from the on-screen keyboard.
        
        Args:
            char: The character from the keyboard
            cursor_position: The current cursor position
            
        Returns:
            str: The text to insert, or None if no text should be inserted
        """
        if not self.enabled:
            return char
            
        # For Space, Backspace, and other characters, just return the character
        # and let the main application handle the buffer and suggestions
        # This matches the behavior in SinhalaWordProcessor_enhanced.py
        return char
            
    def update_suggestions(self):
        """Update suggestions based on the current buffer."""
        if not self.buffer:
            self.clear_suggestions()
            return
            
        buffer_text = "".join(self.buffer)
        suggestions = self.get_suggestions(buffer_text)
        
        self.current_suggestions = suggestions
        self.suggestions_changed.emit(suggestions)
        
    def get_suggestions(self, prefix):
        """
        Get suggestions for the given prefix.
        
        Args:
            prefix: The prefix to get suggestions for
            
        Returns:
            list: A list of suggestions
        """
        # This is a simplified implementation
        # In a real implementation, you would use a more sophisticated algorithm
        # to generate suggestions based on the prefix and the dictionary
        
        # For now, just return the prefix itself as a suggestion
        return [prefix]
        
    def accept_suggestion(self, suggestion):
        """
        Accept a suggestion and replace the buffer text.
        
        Args:
            suggestion: The suggestion to accept
        """
        if not suggestion:
            return
            
        # Get the Sinhala word for the suggestion
        sinhala_word = self.transliterator.transliterate(suggestion)
        if not sinhala_word or sinhala_word == suggestion:
            # Fallback to phonetic
            sinhala_word = self.phonetic_fallback(suggestion)
            
        if not sinhala_word:
            return
            
        # Emit the buffer committed signal
        buffer_text = "".join(self.buffer)
        self.buffer_committed.emit(buffer_text, sinhala_word)
        
        # Clear the buffer and suggestions
        self.clear_buffer()
        
    def commit_buffer(self):
        """Commit the buffered input."""
        if not self.buffer:
            return
            
        buffer_text = "".join(self.buffer)
        
        # Get the Sinhala word
        sinhala_word = self.transliterator.transliterate(buffer_text)
        if not sinhala_word or sinhala_word == buffer_text:
            # Fallback to phonetic
            sinhala_word = self.phonetic_fallback(buffer_text)
            
        # Emit the buffer committed signal
        self.buffer_committed.emit(buffer_text, sinhala_word)
        
        # Clear the buffer and suggestions
        self.clear_buffer()
