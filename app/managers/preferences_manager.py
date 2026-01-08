"""Manager for user preferences and settings."""
from typing import Any, Dict, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PreferencesManager:
    """Manages user preferences and application settings.
    
    This class handles:
    - Loading and saving preferences
    - Default values
    - Recent files list
    - Window geometry and state
    - Theme and appearance settings
    """

    DEFAULT_PREFERENCES = {
        'theme': 'light',
        'font_family': 'Noto Sans Sinhala',
        'font_size': 12,
        'editor_font_family': 'Noto Sans Sinhala',
        'editor_font_size': 14,
        'auto_save': True,
        'auto_save_interval': 300,  # seconds
        'spell_check_enabled': True,
        'transliteration_enabled': True,
        'keyboard_visible': False,
        'keyboard_detached': False,
        'recent_files': [],
        'max_recent_files': 10,
        'window_geometry': {},
        'keyboard_geometry': {},
    }

    def __init__(self, preferences_file: Optional[str] = None):
        """Initialize the preferences manager.
        
        Args:
            preferences_file: Path to preferences JSON file
        """
        self.preferences_file = preferences_file
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        self._load_preferences()
        logger.info("PreferencesManager initialized")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference value.
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value
        """
        return self.preferences.get(key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """Set a preference value.
        
        Args:
            key: Preference key
            value: New value
            save: Whether to save immediately
        """
        self.preferences[key] = value
        logger.debug(f"Preference set: {key} = {value}")
        
        if save:
            self.save()

    def update(self, preferences: Dict[str, Any], save: bool = True):
        """Update multiple preferences at once.
        
        Args:
            preferences: Dictionary of preferences to update
            save: Whether to save immediately
        """
        self.preferences.update(preferences)
        logger.debug(f"Updated {len(preferences)} preferences")
        
        if save:
            self.save()

    def add_recent_file(self, file_path: str):
        """Add a file to recent files list.
        
        Args:
            file_path: Path to file
        """
        recent = self.preferences.get('recent_files', [])
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
        
        # Add to beginning
        recent.insert(0, file_path)
        
        # Limit size
        max_recent = self.preferences.get('max_recent_files', 10)
        recent = recent[:max_recent]
        
        self.preferences['recent_files'] = recent
        self.save()
        logger.info(f"Added to recent files: {file_path}")

    def get_recent_files(self) -> list[str]:
        """Get list of recent files.
        
        Returns:
            List of recent file paths
        """
        return self.preferences.get('recent_files', [])

    def clear_recent_files(self):
        """Clear the recent files list."""
        self.preferences['recent_files'] = []
        self.save()
        logger.info("Recent files cleared")

    def save(self) -> bool:
        """Save preferences to file.
        
        Returns:
            True if successful
        """
        if not self.preferences_file:
            return False

        try:
            path = Path(self.preferences_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            
            logger.debug("Preferences saved")
            return True
        except Exception as e:
            logger.error(f"Error saving preferences: {e}", exc_info=True)
            return False

    def _load_preferences(self):
        """Load preferences from file."""
        if not self.preferences_file:
            return

        try:
            path = Path(self.preferences_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.preferences.update(loaded)
                logger.info("Preferences loaded")
        except Exception as e:
            logger.error(f"Error loading preferences: {e}", exc_info=True)

    def reset_to_defaults(self):
        """Reset all preferences to default values."""
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        self.save()
        logger.info("Preferences reset to defaults")
