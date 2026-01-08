"""Tests for the SinhalaSpellChecker module."""
import pytest
from app.spellchecker import SinhalaSpellChecker


class TestSinhalaSpellChecker:
    """Test cases for SinhalaSpellChecker class."""

    def test_init_with_map(self, sample_sinhala_map):
        """Test initialization with a valid map."""
        spellchecker = SinhalaSpellChecker(sample_sinhala_map)
        assert spellchecker.known_words is not None

    def test_init_with_empty_map(self, empty_map):
        """Test initialization with an empty map."""
        spellchecker = SinhalaSpellChecker(empty_map)
        assert spellchecker.known_words is not None

    def test_is_known_word_existing(self, sample_sinhala_map):
        """Test checking if a known word exists."""
        spellchecker = SinhalaSpellChecker(sample_sinhala_map)
        assert spellchecker.is_known_word("මම") is True

    def test_is_known_word_nonexistent(self, sample_sinhala_map):
        """Test checking if an unknown word exists."""
        spellchecker = SinhalaSpellChecker(sample_sinhala_map)
        assert spellchecker.is_known_word("xyz") is False

    def test_suggest_corrections_known_word(self, sample_sinhala_map):
        """Test getting corrections for a known word."""
        spellchecker = SinhalaSpellChecker(sample_sinhala_map)
        suggestions = spellchecker.suggest_corrections("මම")
        # Known word should return empty list or itself
        assert isinstance(suggestions, list)

    def test_suggest_corrections_unknown_word(self, sample_sinhala_map):
        """Test getting corrections for an unknown word."""
        spellchecker = SinhalaSpellChecker(sample_sinhala_map)
        suggestions = spellchecker.suggest_corrections("xyz")
        assert isinstance(suggestions, list)
