
import logging

# Get the logger
logger = logging.getLogger("SinhalaWordProcessor")

class SinhalaTransliterator:
    """
    Class to handle transliteration from Singlish to Sinhala
    """
    def __init__(self, word_map):
        self.word_map = word_map
        logger.info(f"Initialized SinhalaTransliterator with {len(word_map)} words")
        
    def transliterate(self, text):
        """
        Transliterate a Singlish word to Sinhala
        
        Args:
            text (str): Singlish text to transliterate
        
        Returns:
            str: Transliterated Sinhala text or original if no match
        """
        text = text.lower()
        if text in self.word_map:
            return self.word_map[text]
        return text
    
    def get_suggestions(self, prefix, max_suggestions=9):
        """
        Get suggestions for a given prefix
        
        Args:
            prefix (str): The prefix to search for
            max_suggestions (int, optional): Maximum number of suggestions. Defaults to 9.
        
        Returns:
            list: List of Sinhala words matching the prefix, sorted by length (shortest first)
        """
        if not prefix:
            return []
            
        prefix = prefix.lower()
        
        # Exact match first
        if prefix in self.word_map:
            exact_match = self.word_map[prefix]
            suggestions = [exact_match]
        else:
            exact_match = None
            suggestions = []
        
        # Find words starting with the prefix
        for word, sinhala in self.word_map.items():
            if word.startswith(prefix) and sinhala not in suggestions:
                suggestions.append(sinhala)
                if len(suggestions) >= max_suggestions * 2:  # Get more suggestions than needed for better sorting
                    break
        
        # Ensure we have valid suggestions before sorting and slicing
        if not suggestions:
            logger.info(f"No suggestions found for prefix '{prefix}'")
            return []
            
        # Sort suggestions by length (shortest first)
        # If there's an exact match, always keep it first
        if exact_match:
            suggestions.remove(exact_match)
            sorted_suggestions = [exact_match] + sorted(suggestions, key=len)
            logger.info(f"Sorted suggestions with exact match '{exact_match}' first")
        else:
            sorted_suggestions = sorted(suggestions, key=len)
            logger.info(f"Sorted suggestions by length (no exact match)")
            
        # Log the first few suggestions with their lengths
        for i, sugg in enumerate(sorted_suggestions[:max_suggestions]):
            logger.info(f"  Suggestion {i+1}: '{sugg}' (length: {len(sugg)})")
            
        return sorted_suggestions[:max_suggestions]
    
    def get_singlish_for_sinhala(self, sinhala_word):
        """
        Get the Singlish equivalent of a Sinhala word
        
        Args:
            sinhala_word (str): The Sinhala word to look up
        
        Returns:
            str: The Singlish equivalent or None if not found
        """
        for singlish, sinhala in self.word_map.items():
            if sinhala == sinhala_word:
                return singlish
        return None
