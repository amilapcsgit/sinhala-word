"""Manager for transliteration functionality."""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TransliterationManager:
    """Manages Singlish to Sinhala transliteration.
    
    This class handles the transliteration logic, including:
    - Real-time transliteration as user types
    - Suggestion generation
    - Custom transliteration rules
    """

    def __init__(self, transliterator=None):
        """Initialize the transliteration manager.
        
        Args:
            transliterator: Optional transliterator instance to use.
                          If None, creates a new instance.
        """
        self.transliterator = transliterator
        self.enabled = True
        self._suggestion_cache = {}
        logger.info("TransliterationManager initialized")

    def transliterate(self, text: str) -> str:
        """Transliterate Singlish text to Sinhala.
        
        Args:
            text: Singlish text to transliterate
            
        Returns:
            Transliterated Sinhala text
        """
        if not self.enabled or not text:
            return text

        try:
            if self.transliterator:
                return self.transliterator.transliterate(text)
            return text
        except Exception as e:
            logger.error(f"Transliteration error: {e}", exc_info=True)
            return text

    def get_suggestions(self, prefix: str, limit: int = 9) -> list[str]:
        """Get transliteration suggestions for a prefix.
        
        Args:
            prefix: Text prefix to generate suggestions for
            limit: Maximum number of suggestions to return
            
        Returns:
            List of suggestion strings
        """
        if not prefix or not self.enabled:
            return []

        # Check cache first
        cache_key = f"{prefix}_{limit}"
        if cache_key in self._suggestion_cache:
            return self._suggestion_cache[cache_key]

        try:
            suggestions = self._generate_suggestions(prefix, limit)
            self._suggestion_cache[cache_key] = suggestions
            return suggestions
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}", exc_info=True)
            return []

    def _generate_suggestions(self, prefix: str, limit: int) -> list[str]:
        """Generate suggestions from transliterator.
        
        Args:
            prefix: Text prefix
            limit: Maximum suggestions
            
        Returns:
            List of suggestions
        """
        # Placeholder - implement actual suggestion logic
        if self.transliterator and hasattr(self.transliterator, 'get_suggestions'):
            return self.transliterator.get_suggestions(prefix, limit)
        return []

    def toggle_enabled(self) -> bool:
        """Toggle transliteration on/off.
        
        Returns:
            New enabled state
        """
        self.enabled = not self.enabled
        logger.info(f"Transliteration {'enabled' if self.enabled else 'disabled'}")
        return self.enabled

    def clear_cache(self):
        """Clear the suggestion cache."""
        self._suggestion_cache.clear()
        logger.debug("Suggestion cache cleared")
