# Quarterly — Workbook Updater

Quarterly is a Windows desktop tool that automates the quarter-end process of copying data from a single **master Excel workbook** into multiple pre-configured **target workbooks**, then exporting each as a versioned output file.

Without this tool an analyst must manually open each target workbook, find the right sheet, paste in the latest data (being careful not to disturb adjacent formulas or formatting), rename the file, and repeat — across 2–8 workbooks every quarter. Quarterly does all of that in one click.

## What it does

1. **Reads** one or more named sheets from a master `.xlsx` file (read-only — the source is never modified).
2. **Pastes values** into the matching sheet in each target workbook, clearing only the data region so surrounding formulas and formatting are preserved.
3. **Exports** each updated workbook as a new file named `{original_name}_{suffix}.xlsx` — the originals are never overwritten.
4. **Detects conflicts** before the run starts: if an output file already exists you are prompted to confirm or cancel before anything is written.
5. **Logs every run** so you can review which workbooks were processed, skipped, or errored.

## Key concepts

| Term | Meaning |
|---|---|
| Master Workbook | The source `.xlsx` file containing fresh data for this quarter |
| Target Workbook | A pre-existing report file that receives updated data |
| Tab Mapping | A configured link between a sheet in the master and a sheet in a target workbook |
| Output Suffix | A user-typed string (e.g. `Q2_2026`) appended to each exported filename |

## Views

- **Run screen** — pick the master file, enter a suffix, check/uncheck which workbooks to include, then click Run.
- **Settings** — add or remove target workbooks and their tab mappings; changes are saved immediately to a local JSON config file.
- **History** — browse the log of past runs.

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

**Run flow checklist** (requires real `.xlsx` files in the configured folder)

| Scenario | Expected |
|---|---|
| Click Run with no conflicts | ProgressDialog opens; rows animate through pending → running → done |
| Click Run when output files already exist | ConflictDialog lists filenames; Cancel aborts; Overwrite proceeds |
| Run completes successfully | ProgressDialog closes; LogPanel appears with summary pills |
| Run encounters an error (e.g. missing master file) | ProgressDialog closes; `QMessageBox` shows error text |
| Click Run button while run is in progress | Button is disabled — second click is ignored |

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

## Visual QA

Capture screenshots of all views with representative data:

```bash
source venv/bin/activate
pytest tests/ui/test_visual_qa.py -s
```

Output PNGs are written to `docs/qa/actual/`. Both directories are gitignored — references are local-only, not version-controlled. To establish a baseline, run the script once and copy the actuals to `docs/qa/reference/`. On subsequent runs, diff the new actuals against those local references to spot regressions.

## Building

To produce a Windows `.exe`, run PyInstaller on a Windows machine with Python installed (the spec resolves all paths via `SPECPATH`, so CWD does not matter):

```bash
source venv/bin/activate
pip install -r requirements.txt
python -m PyInstaller build/quarterly.spec
```

The packaged app lands at `dist/quarterly/quarterly.exe`. The entire `dist/quarterly/` folder must be distributed together (not just the `.exe`).

**Requirements:**
- Python 3.11+ on the build machine
- The packaged app should not require admin privileges to run (verify on a clean machine)
- Test the `.exe` on a clean Windows machine without Python to verify all dependencies are bundled

## Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project scaffolding | ✅ Done |
| 2 | Data models (`config.py`, `log.py`) | ✅ Done |
| 3 | Processing logic (`processor.py`) | ✅ Done |
| 4 | Styling (`styles.py`) | ✅ Done |
| 5 | Shared widgets (`widgets.py`) | ✅ Done |
| 6 | Main view — `WorkbookTable`, `RunBar`, `LogPanel` | ✅ Done |
| 7 | Settings view | ✅ Done |
| 8 | History view | ✅ Done |
| 9 | Dialogs (`ConflictDialog`, `ProgressDialog`) | ✅ Done |
| 10 | `MainWindow` — skeleton + full run-flow wiring | ✅ Done |
| 10.5 | Visual QA — screenshot capture & comparison | ✅ Done |
| 11 | PyInstaller packaging | 🔲 Pending |

## Project Structure

```
src/
  config.py          # Config, TabMapping, Workbook dataclasses + JSON persistence
  log.py             # RunRecord, RunResult + append/read run log
  processor.py       # WorkbookProcessor (QThread) + check_conflicts — Excel copy logic
  validation.py      # Shared suffix regex
  main.py            # MainWindow — sidebar, nav, run-flow wiring
  ui/
    styles.py        # Global QSS stylesheet
    widgets.py       # StatusPill, TabChip, HeaderCheckBox
    main_view.py     # Run screen — RunBar, WorkbookTable, LogPanel, empty state
    settings_view.py # Settings view — workbook list + tab mapping editor
    history_view.py  # History view — run log reader
    dialogs.py       # ConflictDialog, ProgressDialog
tests/
  test_config.py
  test_log.py
  test_processor.py
  ui/
    test_main_window.py
    test_main_view.py
    test_settings_view.py
    test_history_view.py
    test_dialogs.py
    test_styles.py
    test_widgets.py
    test_visual_qa.py  # screenshot capture — run with pytest -s; not pass/fail
docs/
  qa/
    actual/            # captured screenshots (gitignored)
    reference/         # approved reference screenshots (gitignored)
```
