"""Pytest configuration and fixtures."""
import pytest
from PySide6.QtWidgets import QApplication
import sys


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Cleanup is handled automatically


@pytest.fixture
def mock_config(tmp_path):
    """Create a temporary configuration directory for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir
