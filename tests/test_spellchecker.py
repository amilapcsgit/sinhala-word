"""Tests for the spellchecker module."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.spellchecker import SinhalaSpellChecker


class TestSinhalaSpellChecker:
    """Test cases for SinhalaSpellChecker class."""

    @pytest.fixture
    def spellchecker(self):
        """Create a spellchecker instance for testing."""
        return SinhalaSpellChecker()

    def test_initialization(self, spellchecker):
        """Test that spellchecker initializes correctly."""
        assert spellchecker is not None
        assert hasattr(spellchecker, 'check_word') or hasattr(spellchecker, 'check')

    def test_valid_word(self, spellchecker):
        """Test checking a valid Sinhala word."""
        # Add known valid word - adjust based on your dictionary
        if hasattr(spellchecker, 'add_word'):
            spellchecker.add_word("මම")
        # Test will need adjustment based on actual implementation

    def test_empty_string(self, spellchecker):
        """Test handling of empty string."""
        # Should not crash
        if hasattr(spellchecker, 'check_word'):
            result = spellchecker.check_word("")
            assert isinstance(result, (bool, list, type(None)))
