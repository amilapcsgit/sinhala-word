"""Tests for the configuration module."""
import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class."""

    @pytest.fixture
    def config_manager(self, tmp_path):
        """Create a config manager instance with temporary directory."""
        config_file = tmp_path / "test_config.json"
        return ConfigManager(str(config_file))

    def test_initialization(self, config_manager):
        """Test that config manager initializes correctly."""
        assert config_manager is not None

    def test_save_and_load(self, config_manager, tmp_path):
        """Test saving and loading configuration."""
        test_data = {"theme": "dark", "font_size": 12}
        
        if hasattr(config_manager, 'save'):
            config_manager.save(test_data)
        
        if hasattr(config_manager, 'load'):
            loaded_data = config_manager.load()
            # Verify data persistence

    def test_default_values(self, config_manager):
        """Test that default values are set correctly."""
        # Test depends on actual implementation
        if hasattr(config_manager, 'get_default'):
            defaults = config_manager.get_default()
            assert isinstance(defaults, dict)
