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

  **Custom on‑screen  75+ keys, draggable dialog, resizable, theme‑aware,
  keyboard**          emits Qt key events

  **Persistent        JSON‑backed: recent files, window & keyboard sizes,
  preferences**       theme, fonts

  **Extensive         Python logging with rotating file handler for the field
  logging**           debugging
  -------------------------------------------------------------------------

**🚀 Quick Start**

\# 1. Clone & enter the repo

\$ git clone https://github.com/amilapcsgit/sinhala-word.git

\$ cd sinhala-word

\# 2. Create venv (recommended)

\$ python -m venv .venv

\$ source .venv/bin/activate \# Windows: .venv\\Scripts\\activate

\# 3. Install runtime dependencies

\$ pip install -r requirements.txt \# see below if the file is missing

\# 4. Run the app

\$ python main.py

**Dependencies** (add these to requirements.txt if not present):

PySide6\>=6.6

pyenchant\>=3.2 \# spell‑checking backend

**🗂️ Project Layout**

├── main.py \# QApplication & SinhalaWordApp (main window)

├── keyboard.py \# SinhalaKeyboard widget

├── transliterator.py \# (planned) pure‑logic transliteration engine

├── spellcheck.py \# (planned) spell‑checker helpers

├── config.py \# (planned) persistence helpers

├── resources/ \# icons, fonts, style sheets

└── tests/ \# pytest & pytest‑qt suites (to be added)

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

  **0.5+ (features)**  Nice‑to‑haves     • Auto‑update via PyPI• Rich‑text export
                                         (docx, pdf)• Hunspell dictionary
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
