# Quarterly — Workbook Updater

A PySide6 desktop application that copies Excel tab data between workbooks and exports versioned output files. Packaged as a Windows `.exe` via PyInstaller.

## Requirements

- Python 3.11 or later
- Windows (target platform) — Linux/WSL supported for development

## Dev Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
source venv/bin/activate
python src/main.py
```

## Testing

```bash
source venv/bin/activate
pytest
```

## Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffolding | ✅ Done |
| 2 | Data models (`config.py`, `log.py`) | ✅ Done |
| 3 | Processing logic (`processor.py`) | ✅ Done |
| 4 | Styling (`styles.py`) | ✅ Done |
| 5 | Shared widgets (`widgets.py`) | ✅ Done |
| 10 | `MainWindow` — shell done; signal wiring after Phase 9 | 🔄 In Progress |
| 6 | Main view — `WorkbookTable`, `RunBar`, `LogPanel` | 🔲 Pending |
| 7 | Settings view | 🔲 Pending |
| 8 | History view | 🔲 Pending |
| 9 | Dialogs (`ConflictDialog`, `ProgressDialog`) | 🔲 Pending |
| 11 | PyInstaller packaging | 🔲 Pending |

## Project Structure

```
src/
  config.py         # Config, TabMapping, Workbook dataclasses + JSON persistence
  log.py            # RunRecord, RunResult + append/read run log
  processor.py      # WorkbookProcessor (QThread) — Excel copy logic
  main.py           # MainWindow entry point
  ui/
    styles.py       # Global QSS stylesheet
    widgets.py      # StatusPill, TabChip, HeaderCheckBox
    main_view.py    # Main view (stub — Phase 6)
    settings_view.py# Settings view (stub — Phase 7)
    history_view.py # History view (stub — Phase 8)
tests/
  test_config.py
  test_log.py
  test_processor.py
  ui/
    test_main_window.py
    test_styles.py
    test_widgets.py
```
