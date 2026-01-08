"""Manager for spell-checking functionality."""
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SpellCheckManager:
    """Manages spell-checking functionality.
    
    This class handles:
    - Checking words against dictionary
    - Providing spelling suggestions
    - Managing user dictionary
    - Highlighting misspelled words
    """

    def __init__(self, spellchecker=None, user_dictionary_path: Optional[str] = None):
        """Initialize the spell check manager.
        
        Args:
            spellchecker: Optional spellchecker instance
            user_dictionary_path: Path to user dictionary file
        """
        self.spellchecker = spellchecker
        self.user_dictionary_path = user_dictionary_path
        self.user_words = set()
        self.enabled = True
        self._load_user_dictionary()
        logger.info("SpellCheckManager initialized")

    def check_word(self, word: str) -> bool:
        """Check if a word is spelled correctly.
        
        Args:
            word: Word to check
            
        Returns:
            True if word is correct, False otherwise
        """
        if not self.enabled or not word:
            return True

        # Check user dictionary first
        if word in self.user_words:
            return True

        try:
            if self.spellchecker and hasattr(self.spellchecker, 'check_word'):
                return self.spellchecker.check_word(word)
            return True  # Default to correct if no spellchecker
        except Exception as e:
            logger.error(f"Spell check error: {e}", exc_info=True)
            return True

    def get_suggestions(self, word: str, limit: int = 5) -> List[str]:
        """Get spelling suggestions for a misspelled word.
        
        Args:
            word: Misspelled word
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested corrections
        """
        if not self.enabled or not word:
            return []

        try:
            if self.spellchecker and hasattr(self.spellchecker, 'suggest'):
                return self.spellchecker.suggest(word)[:limit]
            return []
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}", exc_info=True)
            return []

    def add_to_dictionary(self, word: str) -> bool:
        """Add a word to user dictionary.
        
        Args:
            word: Word to add
            
        Returns:
            True if successfully added
        """
        if not word:
            return False

        self.user_words.add(word)
        self._save_user_dictionary()
        logger.info(f"Added '{word}' to user dictionary")
        return True

    def remove_from_dictionary(self, word: str) -> bool:
        """Remove a word from user dictionary.
        
        Args:
            word: Word to remove
            
        Returns:
            True if successfully removed
        """
        if word in self.user_words:
            self.user_words.remove(word)
            self._save_user_dictionary()
            logger.info(f"Removed '{word}' from user dictionary")
            return True
        return False

    def toggle_enabled(self) -> bool:
        """Toggle spell checking on/off.
        
        Returns:
            New enabled state
        """
        self.enabled = not self.enabled
        logger.info(f"Spell checking {'enabled' if self.enabled else 'disabled'}")
        return self.enabled

    def _load_user_dictionary(self):
        """Load user dictionary from file."""
        if not self.user_dictionary_path:
            return

        try:
            import json
            from pathlib import Path
            
            path = Path(self.user_dictionary_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_words = set(data.get('words', []))
                logger.info(f"Loaded {len(self.user_words)} words from user dictionary")
        except Exception as e:
            logger.error(f"Error loading user dictionary: {e}", exc_info=True)

    def _save_user_dictionary(self):
        """Save user dictionary to file."""
        if not self.user_dictionary_path:
            return

        try:
            import json
            from pathlib import Path
            
            path = Path(self.user_dictionary_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({'words': list(self.user_words)}, f, ensure_ascii=False, indent=2)
            logger.debug("User dictionary saved")
        except Exception as e:
            logger.error(f"Error saving user dictionary: {e}", exc_info=True)
