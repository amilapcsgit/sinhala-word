class SinhalaTransliterator:
    """
    Class to handle transliteration from Singlish to Sinhala
    """
    def __init__(self, word_map):
        self.word_map = word_map
        
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
            list: List of Sinhala words matching the prefix
        """
        if not prefix:
            return []
            
        prefix = prefix.lower()
        
        # Exact match first
        if prefix in self.word_map:
            suggestions = [self.word_map[prefix]]
        else:
            suggestions = []
        
        # Find words starting with the prefix
        for word, sinhala in self.word_map.items():
            if word.startswith(prefix) and sinhala not in suggestions:
                suggestions.append(sinhala)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions[:max_suggestions]
    
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
