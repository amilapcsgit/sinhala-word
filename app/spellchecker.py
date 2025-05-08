import re

class SinhalaSpellChecker:
    """
    Basic spell checker for Sinhala text
    """
    def __init__(self, word_map):
        # Create a set of known Sinhala words from the word map
        self.known_words = set(word_map.values())
        
        # Define Sinhala Unicode character range
        self.sinhala_char_pattern = re.compile(r'[\u0D80-\u0DFF]+')
        
        # Define word boundary pattern for Sinhala
        self.word_pattern = re.compile(r'[\u0D80-\u0DFF]+')
    
    def is_known_word(self, word):
        """
        Check if a word is known
        
        Args:
            word (str): Word to check
        
        Returns:
            bool: True if word is known, False otherwise
        """
        return word in self.known_words
    
    def is_sinhala_word(self, word):
        """
        Check if a word contains Sinhala characters
        
        Args:
            word (str): Word to check
        
        Returns:
            bool: True if word contains Sinhala characters, False otherwise
        """
        return bool(self.sinhala_char_pattern.search(word))
    
    def check_text(self, text):
        """
        Check spelling in a text and return positions of misspelled words
        
        Args:
            text (str): Text to check
        
        Returns:
            list: List of (start, end) positions of misspelled words
        """
        misspelled_positions = []
        
        # Find all Sinhala words
        for match in self.word_pattern.finditer(text):
            word = match.group(0)
            if not self.is_known_word(word):
                # Add the position of the misspelled word
                misspelled_positions.append((
                    f"1.0 + {match.start()} chars",
                    f"1.0 + {match.end()} chars"
                ))
        
        return misspelled_positions
    
    def suggest_corrections(self, word, max_suggestions=5):
        """
        Suggest corrections for a misspelled word
        
        Args:
            word (str): Misspelled word
            max_suggestions (int, optional): Maximum number of suggestions. Defaults to 5.
        
        Returns:
            list: List of suggested corrections
        """
        # For now, we'll just return empty list as implementing a proper
        # Sinhala spelling correction algorithm is complex
        return []
