# Test Suite for Sinhala Word Processor

This directory contains the test suite for the Sinhala Word Processor application.

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_transliterator.py
```

### Run with verbose output:
```bash
pytest -v
```

### Run tests matching a pattern:
```bash
pytest -k "transliterate"
```

## Test Structure

- `conftest.py` - Shared fixtures and pytest configuration
- `test_transliterator.py` - Tests for the transliteration module
- `test_spellchecker.py` - Tests for the spell checker module
- `test_config.py` - Tests for configuration management (TODO)
- `test_ui/` - UI component tests using pytest-qt (TODO)

## Writing Tests

### Unit Tests
Unit tests should focus on testing individual functions and classes in isolation.

### Integration Tests
Integration tests should test how multiple components work together.

### GUI Tests
GUI tests use pytest-qt to test PySide6 widgets and user interactions.

## Coverage Goals

- Aim for at least 80% code coverage for core modules
- All public APIs should have tests
- Critical user workflows should have integration tests

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Scheduled daily runs

See `.github/workflows/ci.yml` for CI configuration.
