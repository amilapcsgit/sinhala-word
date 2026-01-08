"""Tests for the SinhalaTransliterator module."""
import pytest
from app.transliterator import SinhalaTransliterator


class TestSinhalaTransliterator:
    """Test cases for SinhalaTransliterator class."""

    def test_init_with_map(self, sample_sinhala_map):
        """Test initialization with a valid map."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        assert transliterator.word_map == sample_sinhala_map

    def test_init_with_empty_map(self, empty_map):
        """Test initialization with an empty map."""
        transliterator = SinhalaTransliterator(empty_map)
        assert transliterator.word_map == empty_map

    def test_transliterate_existing_word(self, sample_sinhala_map):
        """Test transliteration of a word that exists in the map."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        result = transliterator.transliterate("mama")
        assert result == "මම"

    def test_transliterate_case_insensitive(self, sample_sinhala_map):
        """Test that transliteration is case-insensitive."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        assert transliterator.transliterate("MAMA") == "මම"
        assert transliterator.transliterate("Mama") == "මම"
        assert transliterator.transliterate("MaMa") == "මම"

    def test_transliterate_nonexistent_word(self, sample_sinhala_map):
        """Test transliteration of a word not in the map."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        result = transliterator.transliterate("unknown")
        assert result == "unknown" or result == ""

    def test_get_suggestions_prefix_match(self, sample_sinhala_map):
        """Test getting suggestions for a prefix that matches entries."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        suggestions = transliterator.get_suggestions("ma", max_suggestions=5)
        assert "මම" in suggestions

    def test_get_suggestions_no_match(self, sample_sinhala_map):
        """Test getting suggestions when no prefix matches."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        suggestions = transliterator.get_suggestions("xyz", max_suggestions=5)
        assert len(suggestions) == 0

    def test_get_suggestions_max_limit(self, sample_sinhala_map):
        """Test that get_suggestions respects the max limit."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        suggestions = transliterator.get_suggestions("a", max_suggestions=2)
        assert len(suggestions) <= 2

    def test_get_suggestions_empty_prefix(self, sample_sinhala_map):
        """Test getting suggestions with an empty prefix."""
        transliterator = SinhalaTransliterator(sample_sinhala_map)
        suggestions = transliterator.get_suggestions("", max_suggestions=5)
        # Should return no suggestions or all suggestions depending on implementation
        assert isinstance(suggestions, list)
