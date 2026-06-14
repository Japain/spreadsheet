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

- [x] **Test:** `StatusPill("success")` sets `objectName` to `"pill_success"`
- [x] **Test:** `StatusPill("error")` sets `objectName` to `"pill_error"`
- [x] **Test:** `StatusPill("unknown")` raises `ValueError` before constructing any QWidget
- [x] `StatusPill(QLabel)` — takes `status: Literal["success", "skipped", "error"]`, applies correct pill colors
- [x] `TabChip(QLabel)` — small rounded chip for displaying tab names
- [x] `HeaderCheckBox(QCheckBox)` — "toggle all" checkbox for WorkbookTable header

---

## Phase 6 — Main View (`src/ui/main_view.py`) ✓

**Test file:** `tests/ui/test_main_view.py` — uses `qtbot` with a minimal `Config`.

### RunBar
- [x] **Test:** Run button disabled when input file field is empty
- [x] **Test:** Run button disabled when suffix field is empty
- [x] **Test:** Run button disabled when suffix contains filesystem-illegal characters (`\/:*?"<>|`)
- [x] **Test:** Run button disabled when no workbook rows are checked
- [x] **Test:** Run button enabled when all three conditions are met (valid non-empty suffix, input file set, ≥1 checked row)
- [x] Input file text field + browse button (opens to `config.input_folder`)
- [x] Output suffix text field with `_` prefix label and `.xlsx` suffix label
- [x] Suffix validation: reject characters illegal on Windows filesystems (`\/:*?"<>|`); show inline error
- [x] Run button (disabled until input file, valid suffix, and ≥1 checked workbook are set)
- [x] Run button enable/disable logic wired to field changes and checkbox state

### WorkbookTable
- [x] **Test:** `get_selected_ids()` returns only IDs of checked rows
- [x] **Test:** header checkbox checks all rows; unchecking header unchecks all
- [x] Scrollable table with columns: Run (checkbox), Workbook, Input Tab(s), Target Tab(s), Folder
- [x] Rows dim (reduced opacity) when unchecked
- [x] Header checkbox toggles all row checkboxes
- [x] `get_selected_ids()` — returns list of checked workbook IDs

### LogPanel
- [x] **Test:** LogPanel hidden on init; visible after `show_results()` called
- [x] **Test:** summary pill counts match the `RunResult` list passed in
- [x] Hidden by default; shown after run completes
- [x] Header: "Run complete", suffix, summary pills (N ok / N skipped / N error)
- [x] Per-workbook rows: status text, filename, message, output filename
- [x] "Copy log" button (copies plain-text summary to clipboard)
- [x] "Dismiss" button (hides panel)
- [ ] *(deferred)* Header timestamp
- [ ] *(deferred)* Per-workbook rows: status icon, row count, duration

### Empty State
- [x] **Test:** empty-state widget shown when `config.workbooks` is empty; RunBar hidden
- [x] Replaces RunBar + WorkbookTable when `config.workbooks` is empty
- [x] Centred card with icon, heading, description, and "Add target workbook" button that navigates to SettingsView

---

## Phase 7 — Settings View (`src/ui/settings_view.py`)

**Design spec:** `docs/superpowers/specs/2026-06-10-settings-view-design.md`

**Test file:** `tests/ui/test_settings_view.py` — uses `qtbot` and `tmp_path` for config I/O.

- [x] **Test:** editing filename field auto-saves to config JSON
- [x] **Test:** "Add mapping" button disabled when 2 mappings exist
- [x] **Test:** "Remove mapping" button disabled (or hidden) when only 1 mapping exists, preventing zero-mapping workbooks
- [x] **Test:** newly added workbook starts with 1 default mapping and cannot be saved with 0 mappings
- [x] **Test:** "Remove workbook" removes workbook from config and list
- [x] **Test:** adding a new workbook shows it in the list and selects it

### Known gaps — resolved

- [x] `test_add_workbook_shows_and_selects` — added left list item count assertion
- [x] `test_add_workbook_shows_and_selects` — added `Config.load()` disk check
- [x] `test_add_mapping_disabled_at_two` — added `Config.load()` disk check
- [x] `test_new_workbook_has_one_mapping` — added `Config.load()` disk check
- [x] Placeholder text trailing period removed
- [x] List items now show green Excel icon before filename (V1 checklist item 3)
- [x] Mapping chips are now styled gray monospace pill chips (V1 checklist item 3)
- [x] Left pane header now shows `"Target workbooks (N)"` count (V1 checklist item 5)
- [x] Remove mapping button is now danger-ghost style (V1 checklist item 9)
- [x] Remove workbook button is now danger-ghost red style (V1 checklist item 12)
- [x] Global settings card: default input folder field + browse button; auto-saves on change
- [x] Two-pane layout:
  - [x] Left pane: scrollable workbook list (filename + folder + mapping chips); "Add" button in header
  - [x] Right pane: detail form for selected workbook
    - [x] Filename field
    - [x] Target folder field + browse button
    - [x] Tab mapping rows (1–2): input field → arrow → target field + remove button each; remove button disabled/hidden when only 1 mapping remains
    - [x] "Add mapping" button (disabled when 2 mappings exist)
    - [x] "Remove workbook" danger button at bottom
- [x] All edits auto-save to `config.json` immediately on change

---

## Phase 8 — History View (`src/ui/history_view.py`) ✓

**Design spec:** `docs/superpowers/specs/2026-06-12-history-view-design.md`

**Test file:** `tests/ui/test_history_view.py`

- [x] **Test:** view populated with records in most-recent-first order
- [x] **Test:** empty state shown when log file does not exist
- [x] Reads `runs.log` on view activation
- [x] Scrollable list of `RunRecord` entries, most recent first
- [x] Each row: timestamp (monospace), suffix, input filename, result pill summary (N ok / N skipped / N error)
- [x] Empty state when no records exist

---

## Phase 9 — Dialogs (`src/ui/dialogs.py`) ✓

**Design spec:** `docs/superpowers/specs/2026-06-13-dialogs-design.md`

**Test file:** `tests/ui/test_dialogs.py`

### ConflictDialog
- [x] **Test:** dialog lists each conflicting filename
- [x] **Test:** "Cancel" returns `QDialog.Rejected`; "Overwrite" returns `QDialog.Accepted`
- [x] Lists all conflicting output filenames
- [x] "Cancel & change suffix" button (closes dialog, no action)
- [x] "Overwrite and continue" button (signals caller to proceed)

### ProgressDialog
- [x] **Test:** row transitions from pending → running → done when signals fire in sequence
- [x] **Test:** dialog closes when `run_complete` is emitted
- [x] Non-dismissible (no close button, ESC ignored) during run
- [x] Per-workbook rows: spinner (running) / check (done) / dashed circle (pending), filename, row count or status label
- [x] Overall progress bar
- [x] Closes automatically when `run_complete` fires

---

## Phase 10 — Main Window (`src/main.py`)

**Test file:** `tests/ui/test_main_window.py` — integration smoke tests only.

### Skeleton (completed before Phase 6) ✓

- [x] **Test:** clicking "Configure" nav item switches to SettingsView
- [x] **Test:** clicking "Run History" nav item switches to HistoryView
- [x] `QApplication` setup with app name and style
- [x] Apply `STYLESHEET` from `styles.py`
- [x] `QMainWindow` fixed at 1280×820, non-resizable
- [x] Sidebar (220px):
  - [x] Brand mark / app name at top
  - [x] Nav items: Run, Configure, Run History
  - [x] Footer: config file path, version string
- [x] `QStackedWidget` content area hosting `MainView`, `SettingsView`, `HistoryView`
- [x] Sidebar nav items switch the stacked widget page
- [x] Config loaded at startup; passed to all views

### Wiring (after Phase 9)

- [ ] **Test:** Run click with conflicts shows ConflictDialog before starting processor
- [ ] **Test:** Run click with no conflicts starts `WorkbookProcessor` directly
- [ ] Wire `WorkbookProcessor` signals to `MainView` and `ProgressDialog`:
  - [ ] `workbook_started` → update ProgressDialog row to spinner
  - [ ] `workbook_finished` → update ProgressDialog row to done/error
  - [ ] `run_complete` → close ProgressDialog, show LogPanel
  - [ ] `run_error` → close ProgressDialog, show error in UI
- [ ] On Run click: call `check_conflicts()`, show `ConflictDialog` if needed, then start `WorkbookProcessor`
- [ ] **Revisit config error UX** — skeleton shows `QMessageBox.critical` + exits on corrupt `config.json`; consider backup-and-reset strategy for better UX

---

## Phase 10.5 — Visual QA

**Script:** `tests/ui/test_visual_qa.py`
**Reference images:** `docs/qa/reference/`
**Actual images:** `docs/qa/actual/`

Run with: `pytest tests/ui/test_visual_qa.py -s`

Not a pass/fail test — a screenshot capture script run manually as part of QA. Each test function instantiates a view with representative data, calls `widget.grab()`, and saves a PNG to `docs/qa/actual/`.

### Capture

- [ ] Main View — empty state (no workbooks in config)
- [ ] Main View — populated state (workbooks listed, run button active)
- [ ] Settings View — empty state
- [ ] Settings View — populated (workbooks with tab mappings)
- [ ] History View — empty state
- [ ] History View — populated (several run records)
- [ ] ConflictDialog — conflict list shown
- [ ] ProgressDialog — mid-run with mixed statuses

### Compare & promote

- [ ] For each actual screenshot, compare visually against reference in `docs/qa/reference/` (or the HTML prototype in `docs/design/` if no reference exists yet)
- [ ] Fix any layout, color, or spacing discrepancies found
- [ ] Promote approved actuals without existing references to `docs/qa/reference/`

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
→ Phase 10.5 (Visual QA)
→ Phase 11
```

Start with Phase 2 and 3 (data + logic) so they can be unit-tested independently before any UI exists.
