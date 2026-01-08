"""Manager classes for organizing application logic."""

from .transliteration_manager import TransliterationManager
from .spellcheck_manager import SpellCheckManager
from .keyboard_manager import KeyboardManager
from .preferences_manager import PreferencesManager
from .document_manager import DocumentManager

__all__ = [
    'TransliterationManager',
    'SpellCheckManager',
    'KeyboardManager',
    'PreferencesManager',
    'DocumentManager',
]
