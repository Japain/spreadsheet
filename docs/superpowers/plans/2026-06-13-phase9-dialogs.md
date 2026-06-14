# Phase 9 — Dialogs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `ConflictDialog` and `ProgressDialog` in `src/ui/dialogs.py` so Phase 10 can wire them into the run flow.

**Architecture:** Two `QDialog` subclasses in a single new file. `ConflictDialog` is a simple modal that lists conflicting filenames and returns Accepted/Rejected. `ProgressDialog` is non-dismissible during a run, animates per-workbook state via a shared `QTimer`, and closes via `accept()` when `run_complete` fires.

**Tech Stack:** PySide6 (`QDialog`, `QTimer`, `QProgressBar`, `QProgressBar`), pytest-qt (`qtbot`)

**Spec:** `docs/superpowers/specs/2026-06-13-dialogs-design.md`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/ui/dialogs.py` | Create | `ConflictDialog`, `_ProgressRow`, `ProgressDialog`, `SPINNER_FRAMES` |
| `tests/ui/test_dialogs.py` | Create | All pytest-qt tests for both dialogs |

---

## Task 1: ConflictDialog

**Files:**
- Create: `src/ui/dialogs.py`
- Create: `tests/ui/test_dialogs.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/ui/test_dialogs.py`:

```python
from PySide6.QtWidgets import QDialog, QLabel, QPushButton

from src.ui.dialogs import ConflictDialog


def test_conflict_dialog_lists_filenames(qtbot):
    dialog = ConflictDialog(["alpha.xlsx", "beta.xlsx"])
    qtbot.addWidget(dialog)
    texts = [w.text() for w in dialog.findChildren(QLabel)]
    assert "alpha.xlsx" in texts
    assert "beta.xlsx" in texts


def test_conflict_dialog_cancel_rejects(qtbot):
    dialog = ConflictDialog(["file.xlsx"])
    qtbot.addWidget(dialog)
    btn = next(b for b in dialog.findChildren(QPushButton) if "Cancel" in b.text())
    btn.click()
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_conflict_dialog_overwrite_accepts(qtbot):
    dialog = ConflictDialog(["file.xlsx"])
    qtbot.addWidget(dialog)
    btn = next(b for b in dialog.findChildren(QPushButton) if "Overwrite" in b.text())
    btn.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source venv/bin/activate && pytest tests/ui/test_dialogs.py -v
```

Expected: `ERROR — ModuleNotFoundError: No module named 'src.ui.dialogs'`

- [ ] **Step 3: Create `src/ui/dialogs.py` with `ConflictDialog`**

```python
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.log import RunResult

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ConflictDialog(QDialog):
    def __init__(self, filenames: list[str], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Overwrite existing files?")
        self.setFixedWidth(480)

        heading = QLabel("These output files already exist")
        heading.setStyleSheet("font-weight: bold;")

        sub = QLabel("Running will overwrite them:")
        sub.setObjectName("secondary")

        file_list = QWidget()
        file_layout = QVBoxLayout(file_list)
        file_layout.setContentsMargins(16, 0, 0, 0)
        file_layout.setSpacing(2)
        for name in filenames:
            lbl = QLabel(name)
            lbl.setObjectName("monospace")
            file_layout.addWidget(lbl)

        # && renders as a literal & in Qt button labels
        cancel_btn = QPushButton("Cancel && change suffix")
        cancel_btn.clicked.connect(self.reject)

        overwrite_btn = QPushButton("Overwrite and continue")
        overwrite_btn.setObjectName("primary")
        overwrite_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(overwrite_btn)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(heading)
        layout.addWidget(sub)
        layout.addWidget(file_list)
        layout.addLayout(btn_row)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/ui/test_dialogs.py -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/ui/dialogs.py tests/ui/test_dialogs.py
git commit -m "feat: add ConflictDialog"
```

---

## Task 2: ProgressDialog — row state machine

**Files:**
- Modify: `src/ui/dialogs.py` — append `_ProgressRow` and `ProgressDialog` classes
- Modify: `tests/ui/test_dialogs.py` — add two imports and two test functions

- [ ] **Step 1: Add the failing tests**

At the top of `tests/ui/test_dialogs.py`, add two imports after the existing ones:

```python
from src.log import RunResult
from src.ui.dialogs import ProgressDialog
```

Then append these two test functions at the bottom of the file:

```python
def test_progress_row_transitions(qtbot):
    dialog = ProgressDialog([("wb-1", "report.xlsx")])
    qtbot.addWidget(dialog)

    row = dialog._rows["wb-1"]
    assert row._indicator.text() == "○"
    assert row._status.text() == "Waiting"

    dialog.on_workbook_started("wb-1")
    assert row._status.text() == "Processing…"

    result = RunResult(
        workbook_id="wb-1",
        filename="report.xlsx",
        status="success",
        message="",
        output_filename="report_q1.xlsx",
        rows_written=42,
        duration_ms=100,
    )
    dialog.on_workbook_finished(result)
    assert row._indicator.text() == "✓"
    assert row._status.text() == "42 rows"


def test_progress_row_transitions_error(qtbot):
    dialog = ProgressDialog([("wb-1", "report.xlsx")])
    qtbot.addWidget(dialog)

    dialog.on_workbook_started("wb-1")
    result = RunResult(
        workbook_id="wb-1",
        filename="report.xlsx",
        status="error",
        message="File could not be accessed",
        output_filename=None,
        rows_written=0,
        duration_ms=50,
    )
    dialog.on_workbook_finished(result)
    row = dialog._rows["wb-1"]
    assert row._indicator.text() == "✗"
    assert row._status.text() == "File could not be accessed"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/ui/test_dialogs.py::test_progress_row_transitions tests/ui/test_dialogs.py::test_progress_row_transitions_error -v
```

Expected: `ImportError — cannot import name 'ProgressDialog' from 'src.ui.dialogs'`

- [ ] **Step 3: Append `_ProgressRow` and `ProgressDialog` to `src/ui/dialogs.py`**

Append after the `ConflictDialog` class:

```python
class _ProgressRow(QWidget):
    def __init__(self, filename: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._indicator = QLabel("○")
        self._indicator.setFixedWidth(20)
        self._name = QLabel(filename)
        self._status = QLabel("Waiting")
        self._status.setObjectName("secondary")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(self._indicator)
        layout.addWidget(self._name, 1)
        layout.addWidget(self._status)

    def set_running(self, frame: str) -> None:
        self._indicator.setText(frame)
        self._status.setText("Processing…")

    def set_done(self, result: RunResult) -> None:
        if result.status == "success":
            self._indicator.setText("✓")
            self._status.setText(f"{result.rows_written} rows")
        else:
            self._indicator.setText("✗")
            self._status.setText(result.message)


class ProgressDialog(QDialog):
    def __init__(self, workbooks: list[tuple[str, str]], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Running…")

        self._rows: dict[str, _ProgressRow] = {}
        self._frame_index = 0
        self._current_row: _ProgressRow | None = None

        title = QLabel("Running…")
        title.setStyleSheet("font-weight: bold;")

        rows_widget = QWidget()
        rows_layout = QVBoxLayout(rows_widget)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(0)
        for wb_id, filename in workbooks:
            row = _ProgressRow(filename)
            self._rows[wb_id] = row
            rows_layout.addWidget(row)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, len(workbooks))
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._tick)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(rows_widget)
        layout.addWidget(self._progress_bar)

    def _tick(self) -> None:
        if self._current_row is None:
            return
        self._frame_index = (self._frame_index + 1) % len(SPINNER_FRAMES)
        self._current_row.set_running(SPINNER_FRAMES[self._frame_index])

    def on_workbook_started(self, wb_id: str) -> None:
        row = self._rows.get(wb_id)
        if row is None:
            return
        self._current_row = row
        row.set_running(SPINNER_FRAMES[0])
        self._timer.start()

    def on_workbook_finished(self, result: RunResult) -> None:
        row = self._rows.get(result.workbook_id)
        if row is None:
            return
        self._timer.stop()
        self._current_row = None
        row.set_done(result)
        self._progress_bar.setValue(self._progress_bar.value() + 1)
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
pytest tests/ui/test_dialogs.py -v
```

Expected: 5 tests pass (3 ConflictDialog + 2 ProgressDialog row tests).

- [ ] **Step 5: Commit**

```bash
git add src/ui/dialogs.py tests/ui/test_dialogs.py
git commit -m "feat: add ProgressDialog with row state machine"
```

---

## Task 3: ProgressDialog — run completion and non-dismissible

**Files:**
- Modify: `src/ui/dialogs.py` — add `on_run_complete`, `closeEvent`, `keyPressEvent`, window flags to `ProgressDialog`
- Modify: `tests/ui/test_dialogs.py` — add `test_progress_dialog_closes_on_run_complete`

- [ ] **Step 1: Add the failing test**

Append to `tests/ui/test_dialogs.py`:

```python
def test_progress_dialog_closes_on_run_complete(qtbot):
    dialog = ProgressDialog([("wb-1", "report.xlsx")])
    qtbot.addWidget(dialog)
    dialog.on_run_complete()
    assert dialog.result() == QDialog.DialogCode.Accepted
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/ui/test_dialogs.py::test_progress_dialog_closes_on_run_complete -v
```

Expected: `FAILED — AttributeError: 'ProgressDialog' object has no attribute 'on_run_complete'`

- [ ] **Step 3: Add `on_run_complete`, non-dismissible overrides, and window flags to `ProgressDialog`**

In `src/ui/dialogs.py`, inside `ProgressDialog.__init__`, add this line immediately after `self.setWindowTitle("Running…")`:

```python
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
```

Then append these three methods to the `ProgressDialog` class (after `on_workbook_finished`):

```python
    def on_run_complete(self) -> None:
        self.accept()

    def closeEvent(self, event) -> None:
        event.ignore()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
```

Note: `accept()` calls `hide()` internally — it does not trigger `closeEvent`, so the non-dismissible override does not block programmatic close via `on_run_complete`.

- [ ] **Step 4: Run all dialog tests**

```bash
pytest tests/ui/test_dialogs.py -v
```

Expected: 6 tests pass.

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/ui/dialogs.py tests/ui/test_dialogs.py
git commit -m "feat: complete ProgressDialog — run_complete and non-dismissible"
```
