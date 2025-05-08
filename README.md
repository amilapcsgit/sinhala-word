# sinhala-word
Ultimate Sinhala word processor by Amilapcs



New in UI 5.4

- Typing in Singlish and getting Sinhala transliteration.

- Seeing suggestions as you type and accepting them.

- Using the on-screen Sinhala keyboard.

- Saving and opening files.

- Toggling between light and dark themes.

- Access the settings dialog and change the settings.

Application Overview


The Sinhala Word Processor is a desktop application built with PySide6 (Qt for Python) that provides a word processing environment with specialized features for the Sinhala language. The application's main features include:


- Singlish to Sinhala Transliteration: Converts Latin-based "Singlish" text to Sinhala script in real-time.
- Suggestion Popup: Shows up to 9 suggestions for Sinhala words as you type.
- Basic Spell Checking: Underlines unknown Sinhala words in red.
- On-screen Sinhala Keyboard: Provides a virtual keyboard for Sinhala input.
- Theme Support: Offers both light and dark themes.
- Text Editing Features: Standard text editing capabilities with formatting options.

  
The application follows a modular architecture:

Main Application (app/main.py): Contains the SinhalaWordApp class that serves as the main window and orchestrates all components.
Transliterator (app/transliterator.py): Handles conversion from Singlish to Sinhala.
Spellchecker (app/spellchecker.py): Provides basic spell checking for Sinhala text.
Input Handler (app/input_handler.py): Manages keyboard input and buffer for transliteration.
Configuration (app/config.py): Handles user preferences and application settings.
UI Components:
Suggestion Popup (ui/suggestion_popup.py): Displays word suggestions.
Keyboard (ui/keyboard.py): Implements the on-screen Sinhala keyboard.
Theme Manager (ui/theme_manager.py): Manages application theming.
