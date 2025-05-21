**Sinhala Word Py**

A feature‑rich open‑source **Sinhala word‑processor** built with
**Python 3** and **Qt (PySide6)**. It combines a real‑time
Singlish→Sinhala transliterator, spell‑checker, suggestion popup, and an
on‑screen Sinhala keyboard into a desktop‑class editor that runs on
Windows, Linux, and macOS.

![2025-05-15 09_59_08-Sinhala Word Processor](https://github.com/user-attachments/assets/ade6a12b-c127-45bb-aa83-137c6eefb814)

**Why this project?** Native Sinhala editing tools are not customizable
enough to shape into the user's Singlish input style. Sinhala Word Py
aims to fill that gap with a hackable, cross‑platform, MIT‑licensed app
that any developer can extend.

**✨ Key Features**

  -------------------------------------------------------------------------
                      **Details**
  ------------------- -----------------------------------------------------
  **Rich‑text         Bold/italic/underline, lists, alignment, Undo/Redo,
  editor**            custom fonts & sizes, dark/light themes

  **Instant           Typing \"mama\" becomes \"මම\" on‑the‑fly; powered by
  transliteration**   SinhalaTransliterator

  **Spell‑checker**   Underlines unknown words; context menu suggestions;
                      user dictionary

  **Suggestion        shows up to 9 completions under the caret; selectable
  popup**             via 1‑9 / Tab/arrows

  **Custom on‑screen  75+ keys, detachable, resizable, theme‑aware,
  keyboard**          emits Qt key events

  **Multi-format      Open and save files in TXT, DOCX, and PDF formats.
  Support**           Basic style preservation (font, size, bold, italic,
                      underline, color) for DOCX.

  **Recent Files      Quick access to recently opened documents.
  Menu**

  **Settings Dialog** Allows customization of theme, fonts, keyboard, and
                      other application settings.

  **Persistent        JSON‑backed: recent files, window & keyboard sizes,
  preferences**       theme, fonts

  **Extensive         Python logging with rotating file handler for the field
  logging**           debugging
  -------------------------------------------------------------------------

**🚀 Quick Start**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/amilapcsgit/sinhala-word.git
    cd sinhala-word
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # On Windows:
    # .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python run.py
    ```

**Dependencies**

The application relies on the following Python packages, which are listed in `requirements.txt`:

*   `PySide6`: For the main application framework and GUI.
*   `PySide6-Fluent-Widgets`: For modern UI elements.
*   `python-docx`: For opening and saving Microsoft Word (.docx) files.
*   `reportlab`: For exporting documents to PDF (.pdf) format.
*   `pypdf`: For reading PDF (.pdf) files.
*   `pyinstaller`: Used for packaging the application into an executable (typically a development/build dependency).

It is highly recommended to install these using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```
While the application includes a mechanism to dynamically attempt to install `python-docx`, `reportlab`, and `pypdf` if they are not found at runtime, relying on the `requirements.txt` file ensures a smoother and more predictable setup.

**🗂️ Project Layout**

├── README.md
├── run.py                # Main execution script for the application
├── requirements.txt      # Project dependencies
├── app/                  # Core application logic
│   ├── __init__.py
│   ├── main.py           # Handles QApplication & the SinhalaWordApp main window
│   ├── config.py         # Manages user preferences and configurations
│   ├── input_handler.py  # Processes input events for transliteration
│   ├── spellchecker.py   # Implements Sinhala spell-checking logic
│   └── transliterator.py # Handles Singlish to Sinhala transliteration
├── ui/                   # User interface components
│   ├── __init__.py
│   ├── constants.py      # UI related constants
│   ├── font_manager.py   # Manages application fonts
│   ├── icons.py          # Provides access to toolbar icons
│   ├── keyboard.py       # SinhalaKeyboard widget implementation
│   ├── settings_dialog.py # Application settings dialog
│   ├── suggestion_popup.py # UI for transliteration suggestions
│   └── theme_manager.py  # Manages light/dark themes
├── data/                 # User-specific data
│   ├── sinhalawordmap.json # Main Singlish-Sinhala mapping file
│   └── user_config.json  # Stores user preferences
├── resources/            # Static assets (fonts, dictionary)
│   ├── dictionary/       # Spell-checking dictionary files (compressed chunks)
│   └── fonts/            # Bundled Sinhala Unicode fonts
└── .vscode/              # VSCode specific settings (optional)

**🛠️ Development Guide**

**1. Coding style**

-   **Black** for formatting (black .). *80 char lines* where feasible.

-   **isort** for imports.

-   Follow *commitizen* Conventional Commits (e.g., feat: add detachable
    keyboard).

**2. Logging**

-   Use the shared logger from utils.logging (to be factored out)
    instead of bare print().

-   Default level: INFO; switch to DEBUG when troubleshooting.

**3. Running tests**

\$ pytest -q \# logic tests

\$ pytest-qt -q \# GUI tests (requires Xvfb on CI/Linux)

**4. Typical dev cycle**

1.  **Create a feature branch**: git checkout -b feat/add‑autosave

2.  Hack, run black, run tests.

3.  pre‑commit run \--all-files ensures style & static checks.

4.  Push & open a PR.

**🧭 Roadmap**

  -------------------------------------------------------------------------------
  **Phase**            **Goal**          **Milestones**
  -------------------- ----------------- ----------------------------------------
  **0.1 (quick wins)** Stabilise current • Remove duplicate method defs• Replace
                       code              broad except Exception with targeted
                                         errors & tracebacks• Throttle logging
                                         Inside hot paths

  **0.2                Split 2600‑line   • TransliterationManager•
  (modularisation)**   SinhalaWordApp    SpellCheckManager• KeyboardManager•
                       into the services     PreferencesManager

  **0.3 (test          Prevent           • pytest for transliterator &
  harness)**           regressions       spell‑checker• pytest‑qt for GUI smoke
                                         tests• GitHub Actions CI matrix (Ubuntu,
                                         Windows, macOS)

  **0.4                Smooth UI under   • Debounce keyboard resize & button
  (performance)**      load              updates• Switch INFO→WARNING in prod•
                                         Profile with pyinstrument

  **0.5+ (features)**  Nice‑to‑haves     • Auto‑update via PyPI• Hunspell dictionary
                                         integration
  -------------------------------------------------------------------------------

*(Timeline is aspirational---adjust based on contributors &
priorities.)*

**🤝 Contributing**

1.  **Search existing issues**; open a new one if your bug/feature isn't
    tracked.

2.  Discuss major architectural changes before coding---see *Roadmap*
    above.

3.  Small, focused PRs are easier to review than 1,000-line megadiffs.

**Bug report template**

-   **OS / Python / PySide6 versions**

-   **Steps to reproduce**

-   **Expected vs actual result**

-   **Log excerpt** (⇨ \~/.local/share/sinhala-word/logs/...)

**📄 License**

MIT © 2025 Sinhala Word by Amila Prasad PCS. See LICENSE for details.
