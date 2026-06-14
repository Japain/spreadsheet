# Phase 9 — Dialogs Design Spec

**Date:** 2026-06-13
**Phase:** 9
**File:** `src/ui/dialogs.py`
**Tests:** `tests/ui/test_dialogs.py`

---

## Overview

Phase 9 adds two modal dialogs that gate and track a processor run:

- **ConflictDialog** — shown before the run when output files would be overwritten; lets the user cancel or proceed.
- **ProgressDialog** — shown during the run; displays live per-workbook state and closes automatically when the run completes.

Both are `QDialog` subclasses styled to match the existing app palette (`#4b6bdf` primary, `#1b1d22` body text, `#6b7080` secondary, `#f4f5f9` background).

---

## ConflictDialog

### Purpose

Warn the user that one or more output files already exist and give them the choice to cancel (and change the suffix) or overwrite and proceed.

### Constructor

```python
ConflictDialog(filenames: list[str], parent: QWidget | None = None)
```

`filenames` is the list of conflicting output filenames returned by `check_conflicts()`.

### Layout (top to bottom)

1. **Heading** — `"These output files already exist"` — bold `QLabel`
2. **Sub-heading** — `"Running will overwrite them:"` — secondary-color `QLabel`
3. **File list** — one monospace `QLabel` per filename, indented with left margin
4. **Button row** (right-aligned):
   - `"Cancel & change suffix"` — plain/ghost button → `reject()` → `QDialog.Rejected`
   - `"Overwrite and continue"` — `#primary` blue button → `accept()` → `QDialog.Accepted`

### Sizing

Fixed width 480 px; height grows with file count. Parented to the main window so Qt centers it over the parent.

### Non-visual behavior

- Returns `QDialog.Accepted` when the user clicks "Overwrite and continue".
- Returns `QDialog.Rejected` when the user clicks "Cancel & change suffix" or closes the window normally.
- The dialog is **dismissible** (standard close button is fine; Cancel and close-window are equivalent).

---

## ProgressDialog

### Purpose

Show live per-workbook progress during a `WorkbookProcessor` run. Non-dismissible while the run is active. Closes automatically when the run completes.

### Constructor

```python
ProgressDialog(workbooks: list[tuple[str, str]], parent: QWidget | None = None)
```

`workbooks` is an ordered list of `(workbook_id, filename)` pairs for the selected workbooks, in processing order. The dialog builds one `_ProgressRow` per pair, keyed internally by workbook ID.

The caller (Phase 10 wiring) derives this from the selected `Workbook` configs: `[(wb.id, wb.filename) for wb in selected_workbooks]`.

### Layout (top to bottom)

1. **Title label** — `"Running…"` — bold `QLabel`
2. **Row list** — one `_ProgressRow` per workbook, in processing order
3. **Overall `QProgressBar`** — determinate, `setRange(0, N)` where N = number of workbooks; increments by 1 on each `workbook_finished` signal

### `_ProgressRow`

Each row is a horizontal widget with three elements:

| Element | Width | Content |
|---|---|---|
| Indicator `QLabel` | fixed ~20 px | `"○"` pending / braille frame running / `"✓"` success / `"✗"` error or skipped |
| Filename `QLabel` | expanding | workbook filename |
| Status `QLabel` | right-aligned | `"Waiting"` → `"Processing…"` → row count or full message (see below) |

**Status label text by state:**

| State | Text |
|---|---|
| Pending | `"Waiting"` |
| Running | `"Processing…"` |
| Done — success | `"{rows_written} rows"` from `RunResult.rows_written` |
| Done — error | full `RunResult.message` |
| Done — skipped | full `RunResult.message` |

### Spinner Animation

A single `QTimer` (100 ms interval) is shared across the dialog. It cycles through the braille spinner frames:

```python
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
```

The timer updates the indicator label of whichever row is currently in the "running" state. Because `WorkbookProcessor` processes workbooks sequentially, at most one row is running at any moment.

The timer is started when a row transitions to "running" and stopped when that row transitions to "done".

### Signal Wiring

The caller (Phase 10 wiring) connects `WorkbookProcessor` signals to these slots:

| Signal | Slot | Effect |
|---|---|---|
| `workbook_started(str wb_id)` | `on_workbook_started(wb_id)` | Find row by `wb_id`; switch to running state; start spinner timer |
| `workbook_finished(RunResult)` | `on_workbook_finished(result)` | Find row by `result.workbook_id`; switch to done state; set status text; advance progress bar; stop spinner timer |
| `run_complete(list)` | `on_run_complete()` | Call `accept()` to close dialog |

Note: `workbook_started` emits the workbook ID (not filename) — confirmed from `processor.py:78`.

### Non-dismissible Behavior

While the run is in progress the dialog cannot be closed:

- `closeEvent` is overridden to call `event.ignore()`.
- `keyPressEvent` is overridden to ignore the `Key_Escape` key.
- `setWindowFlags` removes the title-bar close (`X`) button.

After `on_run_complete()` calls `accept()`, the dialog closes normally.

---

## File Structure

```
src/ui/dialogs.py          # ConflictDialog, ProgressDialog, _ProgressRow
tests/ui/test_dialogs.py   # pytest-qt tests (see test plan below)
```

---

## Test Plan

### ConflictDialog

- **`test_conflict_dialog_lists_filenames`** — construct with `["a.xlsx", "b.xlsx"]`; assert both filenames appear as text somewhere in the dialog.
- **`test_conflict_dialog_cancel_rejects`** — click "Cancel & change suffix"; assert `dialog.result() == QDialog.Rejected`.
- **`test_conflict_dialog_overwrite_accepts`** — click "Overwrite and continue"; assert `dialog.result() == QDialog.Accepted`.

### ProgressDialog

- **`test_progress_row_transitions`** — construct dialog with one `(id, filename)` pair; emit `workbook_started(id)` then `workbook_finished(RunResult)`; assert the row's indicator and status text match the done state.
- **`test_progress_dialog_closes_on_run_complete`** — emit `run_complete`; assert `dialog.result() == QDialog.Accepted` (dialog accepted/closed).
