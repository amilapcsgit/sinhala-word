# sinhala-word
Ultimate Sinhala word processor by Amilapcs



New in UI 5.4

- Typing in Singlish and getting Sinhala transliteration.

- Seeing suggestions as you type and accepting them.

- Using the on-screen Sinhala keyboard.

- Saving and opening files.

- Toggling between light and dark themes.

- Access the settings dialog and change the settings.



sinhala-word/
├── app/                      # Main application code
│   ├── __init__.py           # Makes the directory a package
│   ├── main.py               # Renamed from SinhalaWordProcessor_simple.py
│   ├── config.py             # Configuration settings
│   ├── transliterator.py     # Transliteration logic
│   ├── spellchecker.py       # Spell checking functionality
│   └── input_handler.py      # Input handling logic
│
├── ui/                       # UI-related code
│   ├── __init__.py           # Makes the directory a package
│   ├── keyboard.py           # Renamed from pyside_keyboard_fixed.py
│   ├── icons.py              # Renamed from pyside_icons.py
│   ├── theme_manager.py      # Theme management
│   ├── settings_dialog.py    # Settings dialog
│   └── suggestion_popup.py   # Suggestion popup
│
├── data/                     # Data files
│   ├── sinhalawordmap.json   # Word mapping data
│   └── user_config.json      # User configuration
│
├── resources/                # Application resources
│   ├── fonts/                # Font files
│   └── dictionary/           # Dictionary files
│
├── README.md                 # Project documentation
└── run.py                    # Simple entry point script
