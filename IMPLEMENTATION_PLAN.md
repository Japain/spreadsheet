# Implementation Plan — Excel Workbook Update & Export Tool

**Spec:** `docs/superpowers/specs/2026-05-26-excel-update-tool-design.md`
**PRD:** `PRD.md` (v0.7)

---

## Testing Approach

Every phase follows this TDD loop: **write failing tests → implement to pass → refactor**.

- Test runner: `pytest`
- Qt widget tests: `pytest-qt` (`QApplication` fixture, `qtbot`)
- All tests live in `tests/` mirroring `src/` (e.g. `tests/test_config.py`, `tests/ui/test_main_view.py`)
- Run with `pytest` from the project root; CI-level: all tests must pass before moving to the next phase

---

## Phase 1 — Project Scaffolding ✓

- [x] Create `src/`, `src/ui/`, `build/`, and `tests/`, `tests/ui/` directories
- [x] Create `requirements.txt` with `PySide6`, `openpyxl`, `pyinstaller`, `pytest`, `pytest-qt`
- [x] Add `pytest.ini` (or `[tool.pytest.ini_options]` in `pyproject.toml`) pointing testpaths at `tests/`
- [x] Confirm Python version target (3.11+) and note in README
- [x] Verify `pytest` collects zero tests (clean baseline)

---

## Phase 2 — Data Models (`src/config.py`, `src/log.py`) ✓

**Test file:** `tests/test_config.py`, `tests/test_log.py`

### `src/config.py`
- [x] **Test:** round-trip `Config.save` → `Config.load` returns equal object
- [x] **Test:** `Config.load` on missing file creates default config and writes it to disk
- [x] **Test:** malformed JSON raises a clear error (not a raw `JSONDecodeError`)
- [x] `TabMapping` dataclass (`input: str`, `target: str`)
- [x] `Workbook` dataclass (`id`, `filename`, `folder`, `mappings: list[TabMapping]`)
- [x] `Config` dataclass (`input_folder`, `workbooks: list[Workbook]`)
- [x] `Config.load(path)` — deserialize from JSON; create default file if absent
- [x] `Config.save(path)` — serialize to JSON
- [x] Config path resolution: `%USERPROFILE%\.quarterly\config.json`
- [x] Default config creation on first run (empty workbooks list, empty input_folder)

### `src/log.py`
- [x] **Test:** `append_record` writes valid newline-delimited JSON; second call appends (not overwrites)
- [x] **Test:** `read_records` returns records most-recent-first
- [x] **Test:** `read_records` on missing file returns empty list (no crash)
- [x] `RunResult` dataclass (`workbook_id`, `filename`, `status`, `message`, `output_filename`, `rows_written`, `duration_ms`)
- [x] `RunRecord` dataclass (`timestamp`, `input_filename`, `suffix`, `results: list[RunResult]`)
- [x] `append_record(path, record)` — append newline-delimited JSON to `runs.log`
- [x] `read_records(path)` — read all records from `runs.log`, return most-recent-first

---

## Phase 3 — Processing Logic (`src/processor.py`) ✓

**Test file:** `tests/test_processor.py` — uses `tmp_path` fixture and real `.xlsx` files built with openpyxl; no mocking of file I/O.

- [x] **Test:** `check_conflicts` returns empty list when no output files exist
- [x] **Test:** `check_conflicts` returns filenames of pre-existing output files
- [x] **Test:** successful run writes correct values to output file, leaves source unchanged
- [x] **Test:** master file not found emits `run_error`, no output files created
- [x] **Test:** target file not found → `RunResult(status="error")`, other workbooks still process
- [x] **Test:** missing input tab → mapping skipped, workbook still saved with `status="skipped"`
- [x] **Test:** missing target tab → mapping skipped, same as above
- [x] **Test:** paste zone cleared before write (stale rows from a longer prior dataset are gone)
- [x] **Test:** values-only write — no formula strings in output cells
- [x] **Test:** columns right of `max_column` are untouched in output
- [x] `check_conflicts(config, selected_ids, suffix) -> list[str]` — synchronous pre-run check for existing output files
- [x] `WorkbookProcessor(QThread)` class skeleton with signals:
  - `workbook_started = Signal(str)`
  - `workbook_finished = Signal(RunResult)`
  - `run_complete = Signal(list)`
  - `run_error = Signal(str)`
- [x] `configure(config, input_filename, suffix, selected_ids)` method
- [x] `run()` entry point implementing the full run sequence:
  - [x] Resolve and validate master file path; emit `run_error` and stop if not found
  - [x] Open master workbook read-only via openpyxl
  - [x] Iterate selected workbooks in order:
    - [x] Emit `workbook_started`
    - [x] Open target file; on missing → `RunResult(status="error")`, continue
    - [x] **Test:** locked file emits `workbook_finished` with `RunResult(status="error")` and processor continues to next workbook
    - [x] Detect file lock (exclusive open attempt); on locked → emit `workbook_finished` with `RunResult(status="error")`, continue
    - [x] For each `TabMapping`:
      - [x] Look up input sheet in master; on missing → log, mark skipped, continue
      - [x] Look up target sheet; on missing → log, mark skipped, continue
      - [x] Clear paste zone: A1 → last used row × master `max_column`, set values to `None`
      - [x] Write values only (`cell.value = master_cell.value`) from A1
    - [x] **Test:** unwritable output folder emits `workbook_finished` with `RunResult(status="error")` and processor continues to next workbook
    - [x] Save output as `{base}_{suffix}.xlsx` in target folder; on unwritable → emit `workbook_finished` with `RunResult(status="error")`, continue
    - [x] Emit `workbook_finished` with `RunResult`
  - [x] Emit `run_complete` with all results
  - [x] Append `RunRecord` to `runs.log`
- [x] Status logic: `"success"` = all mappings written; `"skipped"` = ≥1 mapping skipped but file saved; `"error"` = workbook skipped entirely

---

## Phase 4 — Styling (`src/ui/styles.py`) ✓

**Test:** `tests/ui/test_styles.py` — `STYLESHEET` is a non-empty string and contains key tokens (`#4b6bdf`, `#f4f5f9`); smoke test only.

- [x] Define `STYLESHEET` as a QSS string covering:
  - [x] Window background `#f4f5f9`
  - [x] Card surface `#ffffff`, border `1px solid #ebebeb`
  - [x] Sidebar background `#f5f6fa`
  - [x] Accent / primary button `#4b6bdf`, white text
  - [x] Body text `#1b1d22`, secondary text `#6b7080`
  - [x] Monospace font family: `"Cascadia Mono", Consolas`
  - [x] Success pill: bg `#dff2e4`, text `#2a7a48`
  - [x] Warning pill: bg `#fdf3d0`, text `#7a5c00`
  - [x] Error pill: bg `#fde8e4`, text `#8c2a1c`

---

## Phase 5 — Shared Widgets (`src/ui/widgets.py`) ✓

**Test file:** `tests/ui/test_widgets.py` — uses `qtbot`.

- [x] **Test:** `StatusPill("success")` has success bg color in stylesheet
- [x] **Test:** `StatusPill("error")` has error bg color in stylesheet
- [x] `StatusPill(QLabel)` — takes `status: Literal["success", "skipped", "error"]`, applies correct pill colors
- [x] `TabChip(QLabel)` — small rounded chip for displaying tab names
- [x] `HeaderCheckBox(QCheckBox)` — "toggle all" checkbox for WorkbookTable header

---

## Phase 6 — Main View (`src/ui/main_view.py`)

**Test file:** `tests/ui/test_main_view.py` — uses `qtbot` with a minimal `Config`.

### RunBar
- [ ] **Test:** Run button disabled when input file field is empty
- [ ] **Test:** Run button disabled when suffix field is empty
- [ ] **Test:** Run button disabled when suffix contains filesystem-illegal characters (`\/:*?"<>|`)
- [ ] **Test:** Run button disabled when no workbook rows are checked
- [ ] **Test:** Run button enabled when all three conditions are met (valid non-empty suffix, input file set, ≥1 checked row)
- [ ] Input file text field + browse button (opens to `config.input_folder`)
- [ ] Output suffix text field with `_` prefix label and `.xlsx` suffix label
- [ ] Suffix validation: reject characters illegal on Windows filesystems (`\/:*?"<>|`); show inline error
- [ ] Run button (disabled until input file, valid suffix, and ≥1 checked workbook are set)
- [ ] Run button enable/disable logic wired to field changes and checkbox state

### WorkbookTable
- [ ] **Test:** `get_selected_ids()` returns only IDs of checked rows
- [ ] **Test:** header checkbox checks all rows; unchecking header unchecks all
- [ ] Scrollable table with columns: Run (checkbox), Workbook, Input Tab(s), Target Tab(s), Folder
- [ ] Rows dim (reduced opacity) when unchecked
- [ ] Header checkbox toggles all row checkboxes
- [ ] `get_selected_ids()` — returns list of checked workbook IDs

### LogPanel
- [ ] **Test:** LogPanel hidden on init; visible after `show_results()` called
- [ ] **Test:** summary pill counts match the `RunResult` list passed in
- [ ] Hidden by default; shown after run completes
- [ ] Header: "Run complete", timestamp, suffix, summary pills (N ok / N skipped / N error)
- [ ] Per-workbook rows: status icon, filename, message, output filename, row count, duration
- [ ] "Copy log" button (copies plain-text summary to clipboard)
- [ ] "Dismiss" button (hides panel)

### Empty State
- [ ] **Test:** empty-state widget shown when `config.workbooks` is empty; RunBar hidden
- [ ] Replaces RunBar + WorkbookTable when `config.workbooks` is empty
- [ ] Centred card with icon, heading, description, and "Add target workbook" button that navigates to SettingsView

---

## Phase 7 — Settings View (`src/ui/settings_view.py`)

**Test file:** `tests/ui/test_settings_view.py` — uses `qtbot` and `tmp_path` for config I/O.

- [ ] **Test:** editing filename field auto-saves to config JSON
- [ ] **Test:** "Add mapping" button disabled when 2 mappings exist
- [ ] **Test:** "Remove mapping" button disabled (or hidden) when only 1 mapping exists, preventing zero-mapping workbooks
- [ ] **Test:** newly added workbook starts with 1 default mapping and cannot be saved with 0 mappings
- [ ] **Test:** "Remove workbook" removes workbook from config and list
- [ ] **Test:** adding a new workbook shows it in the list and selects it
- [ ] Global settings card: default input folder field + browse button; auto-saves on change
- [ ] Two-pane layout:
  - [ ] Left pane: scrollable workbook list (filename + folder + mapping chips); "Add" button in header
  - [ ] Right pane: detail form for selected workbook
    - [ ] Filename field
    - [ ] Target folder field + browse button
    - [ ] Tab mapping rows (1–2): input field → arrow → target field + remove button each; remove button disabled/hidden when only 1 mapping remains
    - [ ] "Add mapping" button (disabled when 2 mappings exist)
    - [ ] "Remove workbook" danger button at bottom
- [ ] All edits auto-save to `config.json` immediately on change

---

## Phase 8 — History View (`src/ui/history_view.py`)

**Test file:** `tests/ui/test_history_view.py`

- [ ] **Test:** view populated with records in most-recent-first order
- [ ] **Test:** empty state shown when log file does not exist
- [ ] Reads `runs.log` on view activation
- [ ] Scrollable list of `RunRecord` entries, most recent first
- [ ] Each row: timestamp (monospace), suffix, input filename, result pill summary (N ok / N skipped / N error)
- [ ] Empty state when no records exist

---

## Phase 9 — Dialogs (`src/ui/dialogs.py`)

**Test file:** `tests/ui/test_dialogs.py`

### ConflictDialog
- [ ] **Test:** dialog lists each conflicting filename
- [ ] **Test:** "Cancel" returns `QDialog.Rejected`; "Overwrite" returns `QDialog.Accepted`
- [ ] Lists all conflicting output filenames
- [ ] "Cancel & change suffix" button (closes dialog, no action)
- [ ] "Overwrite and continue" button (signals caller to proceed)

### ProgressDialog
- [ ] **Test:** row transitions from pending → running → done when signals fire in sequence
- [ ] **Test:** dialog closes when `run_complete` is emitted
- [ ] Non-dismissible (no close button, ESC ignored) during run
- [ ] Per-workbook rows: spinner (running) / check (done) / dashed circle (pending), filename, row count or status label
- [ ] Overall progress bar
- [ ] Closes automatically when `run_complete` fires

---

## Phase 10 — Main Window (`src/main.py`)

**Test file:** `tests/ui/test_main_window.py` — integration smoke tests only.

- [ ] **Test:** clicking "Configure" nav item switches to SettingsView
- [ ] **Test:** clicking "Run History" nav item switches to HistoryView
- [ ] **Test:** Run click with conflicts shows ConflictDialog before starting processor
- [ ] **Test:** Run click with no conflicts starts `WorkbookProcessor` directly
- [ ] `QApplication` setup with app name and style
- [ ] Apply `STYLESHEET` from `styles.py`
- [ ] `QMainWindow` fixed at 1280×820, non-resizable
- [ ] Sidebar (220px):
  - [ ] Brand mark / app name at top
  - [ ] Nav items: Run, Configure, Run History
  - [ ] Footer: config file path, version string
- [ ] `QStackedWidget` content area hosting `MainView`, `SettingsView`, `HistoryView`
- [ ] Sidebar nav items switch the stacked widget page
- [ ] Wire `WorkbookProcessor` signals to `MainView` and `ProgressDialog`:
  - [ ] `workbook_started` → update ProgressDialog row to spinner
  - [ ] `workbook_finished` → update ProgressDialog row to done/error
  - [ ] `run_complete` → close ProgressDialog, show LogPanel
  - [ ] `run_error` → close ProgressDialog, show error in UI
- [ ] On Run click: call `check_conflicts()`, show `ConflictDialog` if needed, then start `WorkbookProcessor`
- [ ] Config loaded at startup; passed to all views

---

## Phase 11 — Packaging (`build/quarterly.spec`)

- [ ] Write PyInstaller spec file (`--onedir` mode)
- [ ] Hidden imports: `openpyxl`, `PySide6`
- [ ] App name: `quarterly`
- [ ] Output: `dist/quarterly/quarterly.exe`
- [ ] Verify no admin privileges required
- [ ] Test on a clean Windows machine (no Python installed)

---

## Implementation Order

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
→ Phase 10 skeleton (window + nav only)
→ Phase 6 → Phase 7 → Phase 8 → Phase 9
→ Phase 10 wiring
→ Phase 11
```

Start with Phase 2 and 3 (data + logic) so they can be unit-tested independently before any UI exists.
