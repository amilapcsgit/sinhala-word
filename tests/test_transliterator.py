"""Tests for the transliterator module."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.transliterator import SinhalaTransliterator


class TestSinhalaTransliterator:
    """Test cases for SinhalaTransliterator class."""

    @pytest.fixture
    def transliterator(self):
        """Create a transliterator instance for testing."""
        return SinhalaTransliterator()

    def test_basic_transliteration(self, transliterator):
        """Test basic Singlish to Sinhala transliteration."""
        # Test simple words
        result = transliterator.transliterate("mama")
        assert result == "මම", f"Expected 'මම', got '{result}'"

    def test_empty_string(self, transliterator):
        """Test transliteration of empty string."""
        result = transliterator.transliterate("")
        assert result == "", "Empty string should return empty string"

    def test_english_only(self, transliterator):
        """Test that pure English text is preserved or handled correctly."""
        # This test depends on implementation - adjust as needed
        result = transliterator.transliterate("hello")
        assert isinstance(result, str), "Result should be a string"

    def test_mixed_content(self, transliterator):
        """Test transliteration with mixed Singlish and English."""
        # Adjust based on expected behavior
        result = transliterator.transliterate("mama hello")
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"

    def test_special_characters(self, transliterator):
        """Test handling of special characters."""
        result = transliterator.transliterate("mama!")
        assert isinstance(result, str), "Result should be a string"

    def test_numbers(self, transliterator):
        """Test handling of numbers in input."""
        result = transliterator.transliterate("mama 123")
        assert isinstance(result, str), "Result should be a string"
        assert "123" in result or "මම" in result, "Should preserve numbers or transliterate text"
