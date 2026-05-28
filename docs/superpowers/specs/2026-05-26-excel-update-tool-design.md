# Design Spec: Excel Workbook Update & Export Tool
**Date:** 2026-05-26
**Status:** Approved
**PRD:** PRD.md (v0.7)
**Design files:** docs/design/spreadsheets/

---

## 1. Overview

A Windows desktop app (PySide6) that lets an analyst load a master Excel workbook, copy specific sheets into pre-configured target workbooks (overwriting only the designated data range), and export the updated workbooks with a user-defined suffix. Replaces a manual quarterly copy-paste workflow.

---

## 2. Technology Decisions

| Decision | Choice | Reason |
|---|---|---|
| GUI framework | PySide6 | PRD requirement; native Windows feel |
| Excel I/O | openpyxl | Pure Python, no Excel install needed, packages cleanly with PyInstaller |
| Packaging | PyInstaller (onedir) | Self-contained Windows executable, no Python required on target machine |
| Config storage | JSON at `~/.quarterly/config.json` | Human-readable, hand-editable, PRD requirement |
| Run log storage | Newline-delimited JSON at `~/.quarterly/runs.log` | Simple, appendable, easy to read in History view |
| UI theme | V1 "Quarterly" (Windows 11 Fluent-inspired light) | Approved direction; dark mode deferred |

---

## 3. Project Structure

```
src/
  main.py                # Entry point, QApplication, QMainWindow setup
  config.py              # Config data model + JSON load/save
  processor.py           # openpyxl processing logic, runs on QThread
  log.py                 # RunRecord append/read for run history
  ui/
    main_view.py         # Run screen (RunBar + WorkbookTable + LogPanel)
    settings_view.py     # Configure view (workbook list + detail pane)
    history_view.py      # Run history view
    dialogs.py           # ConflictDialog + ProgressDialog
    widgets.py           # Shared small widgets (CheckBox, TabChip, etc.)
    styles.py            # QSS stylesheet (V1 Quarterly theme)
build/
  quarterly.spec         # PyInstaller spec
```

---

## 4. Data Model

### 4.1 Config (`config.py`)

```python
@dataclass
class TabMapping:
    input: str       # sheet name in master workbook
    target: str      # sheet name in target workbook

@dataclass
class Workbook:
    id: str
    filename: str    # e.g. "Revenue_Report_v1.xlsx"
    folder: str      # absolute path to target folder
    mappings: list[TabMapping]  # 1–2 entries

@dataclass
class Config:
    input_folder: str           # default browse location for master file
    workbooks: list[Workbook]

    @classmethod
    def load(cls, path: Path) -> "Config": ...
    def save(self, path: Path) -> None: ...
```

Config file path: `~/.quarterly/config.json`. Created with defaults on first run if absent.

### 4.2 Run Results

```python
@dataclass
class RunResult:
    workbook_id: str
    filename: str
    status: Literal["success", "partial", "error"]
    # success: all mappings written, output file created
    # partial: ≥1 mapping skipped (missing tab), but output file was still created
    # error:   workbook skipped entirely (file not found / locked / unwritable folder)
    message: str
    output_filename: str | None   # None when status == "error"
    rows_written: int
    duration_ms: int
```

### 4.3 Run Record (log)

```python
@dataclass
class RunRecord:
    timestamp: str       # ISO-8601
    input_filename: str
    suffix: str
    results: list[RunResult]
```

---

## 5. UI Structure

### 5.1 Main Window

Single `QMainWindow`, fixed 1280×820. Contains:
- **Sidebar** (220px wide): brand mark, nav items (Run / Configure / Run History), footer with config path and version.
- **Content area**: `QStackedWidget` swapping between `MainView`, `SettingsView`, `HistoryView`.

### 5.2 MainView (`ui/main_view.py`)

Three vertical sections:

**RunBar** (top card)
- Input file: text field + folder browse button (opens pre-navigated to `config.input_folder`)
- Output suffix: text field with `_` prefix label and `.xlsx` suffix label
- Run button: disabled until input file, suffix, and at least one workbook are filled/selected

**WorkbookTable** (main card, scrollable)
- Columns: Run (checkbox), Workbook (filename + Excel icon), Input Tab(s) (chips), Target Tab(s) (chips), Folder (truncated monospace path)
- Rows dim when unchecked
- Header checkbox toggles all

**LogPanel** (bottom card, hidden until run completes)
- Header: "Run complete", timestamp, suffix, summary pills (N ok / N partial / N error)
- Body: per-workbook rows with status icon, filename, message, output filename, row count, duration
- Copy log button, dismiss button

**Empty state** (replaces RunBar + WorkbookTable when `config.workbooks` is empty)
- Centred card with icon, heading, description, and "Add target workbook" button that navigates to SettingsView

### 5.3 SettingsView (`ui/settings_view.py`)

**Global setting (top card):** Default input folder field + browse button.

**Two-pane workbook editor (main card):**
- Left pane: scrollable list of workbooks (filename + folder + mapping chips). "Add" button in header.
- Right pane: detail form for selected workbook:
  - Filename field
  - Target folder field + browse button
  - Tab mappings (up to 2): input field → arrow → target field + remove button
  - "Add mapping" button (disabled when 2 mappings exist)
  - "Remove workbook" button (danger, bottom)

All edits auto-save to `config.json` immediately.

### 5.4 HistoryView (`ui/history_view.py`)

Scrollable list of `RunRecord` entries from `runs.log`, most recent first. Each row: timestamp (monospace), suffix, input filename, result pill summary.

### 5.5 Dialogs (`ui/dialogs.py`)

**ConflictDialog**
- Lists all output filenames that already exist
- "Cancel & change suffix" / "Overwrite and continue" buttons
- Shown before any file is touched

**ProgressDialog** (non-dismissable during run)
- Per-workbook rows: spinner (running) / check (done) / dashed circle (pending), filename, row count or status
- Overall progress bar
- Closes automatically when run completes

---

## 6. Processing Logic (`processor.py`)

`WorkbookProcessor` runs on a `QThread`. Public interface:

```python
class WorkbookProcessor(QThread):
    workbook_started = Signal(str)           # workbook_id
    workbook_finished = Signal(RunResult)
    run_complete = Signal(list)              # list[RunResult]
    run_error = Signal(str)                  # fatal error message

    def configure(self, config, input_filename, suffix, selected_ids): ...
    def run(self): ...                       # QThread entry point
```

### 6.1 Run sequence

1. Resolve full master path (`config.input_folder / input_filename`). If not found → emit `run_error`, stop.
2. Open master workbook in read-only mode with openpyxl.
3. For each selected workbook (in order):
   a. Emit `workbook_started`.
   b. Attempt to open target file. If not found → log error, emit `workbook_finished` with status=error, continue.
   c. Detect file lock by attempting exclusive open before writing. If locked → log "file is open — close it and re-run", continue.
   d. For each tab mapping:
      - Find input sheet in master. If missing → log warning, mark partial, continue.
      - Find target sheet. If missing → log warning, mark partial, continue.
      - Clear paste zone: iterate from A1 to last used row × master `max_column`, set values to None.
      - Write values only (no formulas) from master sheet starting at A1.
   e. Save to `{target_folder}/{base}_{suffix}.xlsx`. If folder unwritable → log error, continue.
   f. Emit `workbook_finished` with RunResult.
4. Emit `run_complete` with all results.
5. Append `RunRecord` to `runs.log`.

### 6.2 Paste Zone rules

- Width: determined by master sheet's `max_column` (dynamic, per PRD §4.3)
- Clear zone before write to prevent stale rows when new dataset is smaller
- Write values only (`cell.value = master_cell.value`), never copy formulas
- Preserve all columns to the right of `max_column`

---

## 7. Pre-run Conflict Check

Before showing `ConflictDialog` or starting a run:

```python
def check_conflicts(config, selected_ids, suffix) -> list[str]:
    # Returns list of output filenames that already exist on disk
```

Called synchronously in the UI thread on Run click. If the list is non-empty, show `ConflictDialog`. User must confirm before `WorkbookProcessor` is started.

---

## 8. Error Handling Matrix

| Condition | Behaviour |
|---|---|
| Master file not found | Halt run, surface error in UI before any processing |
| Target file not found | Skip workbook, log error, continue |
| Input tab missing in master | Skip mapping, log warning, workbook output still created if other mappings succeed |
| Target tab missing | Skip mapping, log warning, same as above |
| Output folder not writable | Skip workbook, log error, continue |
| Target file open in Excel | Skip workbook, log "file is open — close it and re-run" |

All errors surface in LogPanel at run end. No silent failures.

---

## 9. Styling (`ui/styles.py`)

V1 "Quarterly" theme as a QSS string, matching the HTML prototype:

| Design token | HTML value | QSS equivalent |
|---|---|---|
| Window background | `#f4f5f9` | `QPalette` base + `#f4f5f9` |
| Accent | `oklch(0.55 0.16 254)` | `#4b6bdf` |
| Card surface | `#ffffff` | `background: #ffffff` |
| Card border | `rgba(0,0,0,0.06)` | `border: 1px solid #ebebeb` |
| Sidebar background | `rgba(245,246,250,0.55)` | `#f5f6fa` (no blur in Qt) |
| Body text | `#1b1d22` | `color: #1b1d22` |
| Secondary text | `#6b7080` | `color: #6b7080` |
| Monospace font | Cascadia Mono / Consolas | `"Cascadia Mono", Consolas` |
| Primary button | `oklch(0.55 0.16 254)` bg, white text | `#4b6bdf` bg, `#ffffff` text |
| Success pill | `oklch(0.94 0.07 145)` bg | `#dff2e4` bg, `#2a7a48` text |
| Warning pill | `oklch(0.95 0.08 80)` bg | `#fdf3d0` bg, `#7a5c00` text |
| Error pill | `oklch(0.94 0.06 25)` bg | `#fde8e4` bg, `#8c2a1c` text |

---

## 10. Packaging (`build/quarterly.spec`)

- PyInstaller `--onedir` (faster startup than `--onefile`)
- Hidden imports: `openpyxl`, `PySide6`
- Output: `dist/quarterly/quarterly.exe`
- No admin privileges required

---

## 11. Out of Scope (v1)

- Dark mode (deferred)
- Mac / Linux support
- Multi-user shared config
- Scheduling / automated runs
- Charts, pivot tables, merged cell handling
- Undo / rollback
