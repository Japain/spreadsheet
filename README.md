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
python -m src.main
```

## Testing

```bash
source venv/bin/activate
pytest
```

## Manual QA

Launch the app against a temporary config with sample workbooks:

```bash
source venv/bin/activate
python -c "
import sys
from PySide6.QtWidgets import QApplication
from src.config import Config, Workbook, TabMapping
from src.main import MainWindow

app = QApplication(sys.argv)
cfg = Config(
    input_folder='/tmp',
    workbooks=[
        Workbook('wb1', 'Revenue_Report.xlsx', '/tmp', [TabMapping('Data', 'Data')]),
        Workbook('wb2', 'Cost_Analysis.xlsx',  '/tmp', [TabMapping('Actuals', 'Actuals')]),
    ],
)
w = MainWindow(config=cfg)
w.show()
sys.exit(app.exec())
"
```

**Run screen checklist**

| Scenario | Expected |
|---|---|
| App opens | WorkbookTable shows both rows, Run button disabled |
| Set input file path only | Run button still disabled |
| Set valid suffix (e.g. `Q1`) + input file | Run button enables |
| Type a suffix with a space or dot (e.g. `my.suffix`) | Error label appears, Run button stays disabled |
| Clear the bad char | Error label hides, Run button re-enables |
| Uncheck all rows | Run button disables |
| Click Browse | File dialog opens pre-navigated to `/tmp`; selecting a file fills the input field; cancelling leaves it unchanged |
| Uncheck one row | That row dims; `get_selected_ids()` excludes it |
| Header checkbox unchecks all | All rows dim, Run button disables |
| Header checkbox checks all | All rows restore opacity |

**Empty state checklist**

```bash
source venv/bin/activate
python -c "
import sys
from PySide6.QtWidgets import QApplication
from src.config import Config
from src.main import MainWindow
app = QApplication(sys.argv)
w = MainWindow(config=Config(input_folder='', workbooks=[]))
w.show()
sys.exit(app.exec())
"
```

| Scenario | Expected |
|---|---|
| App opens | Empty state card shown; RunBar hidden |
| Click "Add target workbook" | Navigates to Configure (Settings) view |
| Nav items | Run / Configure / Run History all switch views |

## Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffolding | ✅ Done |
| 2 | Data models (`config.py`, `log.py`) | ✅ Done |
| 3 | Processing logic (`processor.py`) | ✅ Done |
| 4 | Styling (`styles.py`) | ✅ Done |
| 5 | Shared widgets (`widgets.py`) | ✅ Done |
| 6 | Main view — `WorkbookTable`, `RunBar`, `LogPanel` | ✅ Done |
| 10 | `MainWindow` — shell done; signal wiring after Phase 9 | 🔄 In Progress |
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
    main_view.py    # Run screen — RunBar, WorkbookTable, LogPanel, empty state
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
