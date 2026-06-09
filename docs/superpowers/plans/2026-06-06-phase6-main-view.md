# Phase 6 — Main View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `src/ui/main_view.py` with four classes — `WorkbookTable`, `LogPanel`, `RunBar`, and `MainView` — covering the full run screen.

**Architecture:** `MainView` owns a `QStackedWidget` with two pages: an empty-state page (shown when `config.workbooks` is empty) and a run page (RunBar + WorkbookTable + LogPanel). `WorkbookTable` uses custom `_WorkbookRow` widgets in a `QScrollArea` (not `QTableWidget`) for full control over per-row opacity dimming and `TabChip` layout. Run button enable/disable logic lives entirely in `MainView`, which subscribes to change signals from both `RunBar` and `WorkbookTable`. Suffix validation (illegal Windows chars) is detected in `RunBar`, which shows an inline error label and emits `changed` so `MainView` can re-evaluate the button state.

**Tech Stack:** PySide6 (`QWidget`, `QScrollArea`, `QStackedWidget`, `QGraphicsOpacityEffect`, `QFileDialog`), `pytest-qt` (`qtbot`), `src.config` (`Config`, `Workbook`, `TabMapping`), `src.log` (`RunResult`), `src.ui.widgets` (`HeaderCheckBox`, `TabChip`)

---

## File Map

| Path | Action | Responsibility |
|---|---|---|
| `src/ui/main_view.py` | **Create** | All four classes + `_WorkbookRow` + `_EmptyState` helpers |
| `tests/ui/test_main_view.py` | **Create** | All Phase 6 tests |

---

## Task 1: Scaffold test file with imports and fixtures

**Files:**
- Create: `tests/ui/test_main_view.py`

- [ ] **Step 1: Create the test file**

```python
# tests/ui/test_main_view.py
import pytest
from src.config import Config, TabMapping, Workbook
from src.log import RunResult
from src.ui.main_view import LogPanel, MainView, WorkbookTable


def _make_workbook(id: str = "wb-1") -> Workbook:
    return Workbook(
        id=id,
        filename=f"{id}.xlsx",
        folder="C:\\test",
        mappings=[TabMapping(input="Sheet1", target="Data")],
    )


def _make_run_result(status: str, id: str = "wb-1") -> RunResult:
    return RunResult(
        workbook_id=id,
        filename=f"{id}.xlsx",
        status=status,
        message="Updated successfully." if status == "success" else "Warning.",
        output_filename=f"{id}_v1.xlsx" if status != "error" else None,
        rows_written=100 if status != "error" else 0,
        duration_ms=500,
    )
```

- [ ] **Step 2: Verify test file is collected (zero tests expected)**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py --collect-only
```

Expected: `no tests ran` — confirms the file is found and the fixtures parse cleanly. The `ImportError` from `from src.ui.main_view import ...` is expected here since `main_view.py` doesn't exist yet; the real "zero tests" baseline is confirmed in Task 2 after the skeleton file exists.

- [ ] **Step 3: Commit**

```bash
git add tests/ui/test_main_view.py
git commit -m "test: scaffold test_main_view.py with fixtures"
```

---

## Task 2: WorkbookTable — tests + implementation

**Files:**
- Create: `src/ui/main_view.py` (initial skeleton)
- Modify: `tests/ui/test_main_view.py`

- [ ] **Step 1: Add WorkbookTable tests to the test file**

Append to `tests/ui/test_main_view.py`:

```python
from PySide6.QtCore import Qt


def test_get_selected_ids_returns_checked_only(qtbot):
    wbs = [_make_workbook("wb-1"), _make_workbook("wb-2")]
    table = WorkbookTable(wbs)
    qtbot.addWidget(table)
    table._rows[0].checkbox.setChecked(True)
    table._rows[1].checkbox.setChecked(False)
    assert table.get_selected_ids() == ["wb-1"]


def test_header_checkbox_toggles_all_rows(qtbot):
    wbs = [_make_workbook("wb-1"), _make_workbook("wb-2")]
    table = WorkbookTable(wbs)
    qtbot.addWidget(table)
    table._header_cb.setCheckState(Qt.CheckState.Checked)
    assert all(r.checkbox.isChecked() for r in table._rows)
    table._header_cb.setCheckState(Qt.CheckState.Unchecked)
    assert not any(r.checkbox.isChecked() for r in table._rows)
```

- [ ] **Step 2: Run to confirm failure**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py -v
```

Expected: `ImportError: cannot import name 'WorkbookTable' from 'src.ui.main_view'` (file doesn't exist yet).

- [ ] **Step 3: Create `src/ui/main_view.py` with `_WorkbookRow` and `WorkbookTable`**

```python
# src/ui/main_view.py
from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGraphicsOpacityEffect
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.config import Config, Workbook
from src.log import RunResult
from src.ui.widgets import HeaderCheckBox, TabChip

_ILLEGAL_RE = re.compile(r'[\\/:*?"<>|]')


class _WorkbookRow(QWidget):
    def __init__(self, workbook: Workbook, parent: QWidget | None = None):
        super().__init__(parent)
        self.workbook_id = workbook.id

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)

        icon_lbl = QLabel("⊞")
        icon_lbl.setFixedWidth(22)

        filename_lbl = QLabel(workbook.filename)
        filename_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        input_cell = QWidget()
        input_cell_layout = QHBoxLayout(input_cell)
        input_cell_layout.setContentsMargins(0, 0, 0, 0)
        input_cell_layout.setSpacing(4)
        for m in workbook.mappings:
            input_cell_layout.addWidget(TabChip(m.input))
        input_cell_layout.addStretch()

        target_cell = QWidget()
        target_cell_layout = QHBoxLayout(target_cell)
        target_cell_layout.setContentsMargins(0, 0, 0, 0)
        target_cell_layout.setSpacing(4)
        for m in workbook.mappings:
            target_cell_layout.addWidget(TabChip(m.target))
        target_cell_layout.addStretch()

        folder_lbl = QLabel(workbook.folder)
        folder_lbl.setObjectName("monospace")
        folder_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(self.checkbox)
        layout.addWidget(icon_lbl)
        layout.addWidget(filename_lbl, 2)
        layout.addWidget(input_cell, 1)
        layout.addWidget(target_cell, 1)
        layout.addWidget(folder_lbl, 2)

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

    def set_dimmed(self, dimmed: bool) -> None:
        self._opacity_effect.setOpacity(0.4 if dimmed else 1.0)


class WorkbookTable(QWidget):
    selection_changed = Signal()

    def __init__(self, workbooks: list[Workbook], parent: QWidget | None = None):
        super().__init__(parent)
        self._rows: list[_WorkbookRow] = []

        self._header_cb = HeaderCheckBox()
        self._header_cb.stateChanged.connect(self._on_header_changed)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)
        header_layout.addWidget(self._header_cb)
        header_layout.addWidget(QLabel("Workbook"), 2)
        header_layout.addWidget(QLabel("Input tab(s)"), 1)
        header_layout.addWidget(QLabel("Target tab(s)"), 1)
        header_layout.addWidget(QLabel("Folder"), 2)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        for wb in workbooks:
            row = _WorkbookRow(wb)
            row.checkbox.stateChanged.connect(self._on_row_changed)
            self._rows.append(row)
            body_layout.addWidget(row)
        body_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(body)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(header)
        main_layout.addWidget(scroll, 1)

    def get_selected_ids(self) -> list[str]:
        return [r.workbook_id for r in self._rows if r.checkbox.isChecked()]

    def _on_row_changed(self) -> None:
        for row in self._rows:
            row.set_dimmed(not row.checkbox.isChecked())
        self.selection_changed.emit()

    def _on_header_changed(self, state: int) -> None:
        checked = Qt.CheckState(state) == Qt.CheckState.Checked
        for row in self._rows:
            row.checkbox.setChecked(checked)
```

- [ ] **Step 4: Run WorkbookTable tests**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py -v
```

Expected:
```
PASSED tests/ui/test_main_view.py::test_get_selected_ids_returns_checked_only
PASSED tests/ui/test_main_view.py::test_header_checkbox_toggles_all_rows
```

- [ ] **Step 5: Run full suite to confirm no regressions**

```bash
source venv/bin/activate && pytest
```

Expected: all prior tests still pass.

- [ ] **Step 6: Commit**

```bash
git add src/ui/main_view.py tests/ui/test_main_view.py
git commit -m "feat: add WorkbookTable with custom row widgets and opacity dimming"
```

---

## Task 3: LogPanel — tests + implementation

**Files:**
- Modify: `src/ui/main_view.py` (append `LogPanel`)
- Modify: `tests/ui/test_main_view.py`

- [ ] **Step 1: Add LogPanel tests to the test file**

Append to `tests/ui/test_main_view.py`:

```python
def test_log_panel_hidden_on_init(qtbot):
    panel = LogPanel()
    qtbot.addWidget(panel)
    assert not panel.isVisible()


def test_log_panel_visible_after_show_results(qtbot):
    panel = LogPanel()
    qtbot.addWidget(panel)
    panel.show_results(
        [_make_run_result("success")],
        suffix="v1",
        timestamp="2026-06-06 10:00:00",
    )
    assert panel.isVisible()


def test_log_panel_pill_counts_match_results(qtbot):
    panel = LogPanel()
    qtbot.addWidget(panel)
    results = [
        _make_run_result("success", "wb-1"),
        _make_run_result("success", "wb-2"),
        _make_run_result("skipped", "wb-3"),
        _make_run_result("error", "wb-4"),
    ]
    panel.show_results(results, suffix="v1", timestamp="2026-06-06 10:00:00")
    assert panel._pill_success.text() == "2 ok"
    assert panel._pill_skipped.text() == "1 skipped"
    assert panel._pill_error.text() == "1 error"
```

- [ ] **Step 2: Run to confirm failure**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py::test_log_panel_hidden_on_init -v
```

Expected: `ImportError: cannot import name 'LogPanel' from 'src.ui.main_view'`.

- [ ] **Step 3: Append `LogPanel` to `src/ui/main_view.py`**

Add after the `WorkbookTable` class:

```python
class LogPanel(QWidget):
    dismissed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.hide()

        self._pill_success = QLabel()
        self._pill_success.setObjectName("pill_success")
        self._pill_skipped = QLabel()
        self._pill_skipped.setObjectName("pill_skipped")
        self._pill_error = QLabel()
        self._pill_error.setObjectName("pill_error")

        title_lbl = QLabel("Run complete")
        self._ts_label = QLabel()
        self._suffix_label = QLabel()
        self._suffix_label.setObjectName("secondary")

        copy_btn = QPushButton("Copy log")
        copy_btn.clicked.connect(self._copy_log)
        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.clicked.connect(self._on_dismiss)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(self._ts_label)
        header_layout.addWidget(self._suffix_label)
        header_layout.addStretch()
        header_layout.addWidget(self._pill_success)
        header_layout.addWidget(self._pill_skipped)
        header_layout.addWidget(self._pill_error)
        header_layout.addWidget(copy_btn)
        header_layout.addWidget(dismiss_btn)

        self._body = QWidget()
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidget(self._body)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll)

        self._results: list[RunResult] = []
        self._current_suffix = ""

    def show_results(
        self, results: list[RunResult], suffix: str, timestamp: str
    ) -> None:
        self._results = results
        self._current_suffix = suffix
        self._ts_label.setText(timestamp)
        self._suffix_label.setText(f"· suffix _{suffix}")

        n_ok = sum(1 for r in results if r.status == "success")
        n_skip = sum(1 for r in results if r.status == "skipped")
        n_err = sum(1 for r in results if r.status == "error")
        self._pill_success.setText(f"{n_ok} ok")
        self._pill_skipped.setText(f"{n_skip} skipped")
        self._pill_error.setText(f"{n_err} error")

        # Rebuild body rows
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for r in results:
            self._body_layout.addWidget(self._make_row(r))
        self._body_layout.addStretch()

        self.show()

    def _make_row(self, result: RunResult) -> QWidget:
        icons = {"success": "✓", "skipped": "⚠", "error": "✗"}
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 6, 12, 6)

        icon_lbl = QLabel(icons.get(result.status, ""))
        icon_lbl.setFixedWidth(20)

        info = QWidget()
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        name_lbl = QLabel(result.filename)
        name_lbl.setStyleSheet("font-weight: bold;")
        msg_lbl = QLabel(result.message)
        msg_lbl.setObjectName("secondary")
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(msg_lbl)

        out_text = f"→ {result.output_filename}" if result.output_filename else "—"
        out_lbl = QLabel(out_text)
        out_lbl.setObjectName("monospace")
        out_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        rows_lbl = QLabel(f"{result.rows_written} rows" if result.rows_written else "")
        rows_lbl.setObjectName("monospace")
        rows_lbl.setFixedWidth(70)

        dur_lbl = QLabel(
            f"{result.duration_ms / 1000:.2f}s" if result.duration_ms else ""
        )
        dur_lbl.setObjectName("monospace")
        dur_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        dur_lbl.setFixedWidth(60)

        layout.addWidget(icon_lbl)
        layout.addWidget(info, 2)
        layout.addWidget(out_lbl, 2)
        layout.addWidget(rows_lbl)
        layout.addWidget(dur_lbl)
        return row

    def _copy_log(self) -> None:
        lines = [f"Run complete — suffix _{self._current_suffix}"]
        for r in self._results:
            out = r.output_filename or "—"
            lines.append(
                f"  [{r.status.upper()}] {r.filename} → {out}"
                f" ({r.rows_written} rows, {r.duration_ms}ms): {r.message}"
            )
        QApplication.clipboard().setText("\n".join(lines))

    def _on_dismiss(self) -> None:
        self.hide()
        self.dismissed.emit()
```

- [ ] **Step 4: Run LogPanel tests**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py -k "log_panel" -v
```

Expected:
```
PASSED tests/ui/test_main_view.py::test_log_panel_hidden_on_init
PASSED tests/ui/test_main_view.py::test_log_panel_visible_after_show_results
PASSED tests/ui/test_main_view.py::test_log_panel_pill_counts_match_results
```

- [ ] **Step 5: Run full suite**

```bash
source venv/bin/activate && pytest
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/ui/main_view.py tests/ui/test_main_view.py
git commit -m "feat: add LogPanel with pill counts and show_results"
```

---

## Task 4: Write failing MainView + RunBar tests

**Files:**
- Modify: `tests/ui/test_main_view.py`

All six remaining tests use `MainView` as the harness. Write them now so they fail, then implement in Task 5.

- [ ] **Step 1: Append all MainView tests to the test file**

```python
# ── RunBar enable/disable (via MainView) ──────────────────────────────────────

def test_run_button_disabled_when_no_input_file(qtbot):
    config = Config(input_folder="", workbooks=[_make_workbook()])
    view = MainView(config)
    qtbot.addWidget(view)
    # row is checked by default; set valid suffix
    view._run_bar._suffix_edit.setText("v1")
    view._run_bar._input_edit.clear()
    assert not view._run_bar._run_btn.isEnabled()


def test_run_button_disabled_when_no_suffix(qtbot):
    config = Config(input_folder="", workbooks=[_make_workbook()])
    view = MainView(config)
    qtbot.addWidget(view)
    view._run_bar._input_edit.setText("Master.xlsx")
    view._run_bar._suffix_edit.clear()
    assert not view._run_bar._run_btn.isEnabled()


def test_run_button_disabled_when_suffix_has_illegal_chars(qtbot):
    config = Config(input_folder="", workbooks=[_make_workbook()])
    view = MainView(config)
    qtbot.addWidget(view)
    view._run_bar._input_edit.setText("Master.xlsx")
    view._run_bar._suffix_edit.setText("v1:bad")
    assert not view._run_bar._run_btn.isEnabled()


def test_run_button_disabled_when_no_rows_checked(qtbot):
    config = Config(input_folder="", workbooks=[_make_workbook()])
    view = MainView(config)
    qtbot.addWidget(view)
    view._run_bar._input_edit.setText("Master.xlsx")
    view._run_bar._suffix_edit.setText("v1")
    view._wb_table._rows[0].checkbox.setChecked(False)
    assert not view._run_bar._run_btn.isEnabled()


def test_run_button_enabled_when_all_conditions_met(qtbot):
    config = Config(input_folder="", workbooks=[_make_workbook()])
    view = MainView(config)
    qtbot.addWidget(view)
    view._run_bar._input_edit.setText("Master.xlsx")
    view._run_bar._suffix_edit.setText("v1")
    # row is checked by default
    assert view._run_bar._run_btn.isEnabled()


# ── Empty state ────────────────────────────────────────────────────────────────

def test_empty_state_shown_when_no_workbooks(qtbot):
    config = Config(input_folder="", workbooks=[])
    view = MainView(config)
    qtbot.addWidget(view)
    assert view._stack.currentIndex() == 0
    assert view._stack.currentWidget() is view._empty_state
```

- [ ] **Step 2: Run to confirm all six tests fail**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py -k "run_button or empty_state" -v
```

Expected: `ImportError: cannot import name 'MainView' from 'src.ui.main_view'` — all six fail.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/ui/test_main_view.py
git commit -m "test: add failing MainView and RunBar enable/disable tests"
```

---

## Task 5: RunBar + _EmptyState + MainView implementation

**Files:**
- Modify: `src/ui/main_view.py` (append three classes)

- [ ] **Step 1: Append `RunBar` to `src/ui/main_view.py`**

```python
class RunBar(QWidget):
    changed = Signal()
    run_requested = Signal()

    def __init__(self, input_folder: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self._input_folder = input_folder

        input_lbl = QLabel("Master input file")
        self._input_edit = QLineEdit()
        self._input_edit.setPlaceholderText("Master_Q1_2026.xlsx")
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_input)

        input_row_layout = QHBoxLayout()
        input_row_layout.addWidget(self._input_edit)
        input_row_layout.addWidget(browse_btn)

        suffix_lbl = QLabel("Output suffix")
        prefix_lbl = QLabel("_")
        self._suffix_edit = QLineEdit()
        self._suffix_edit.setPlaceholderText("v2_052526")
        dotxlsx_lbl = QLabel(".xlsx")

        self._suffix_error = QLabel("Suffix contains invalid characters")
        self._suffix_error.setStyleSheet("color: #8c2a1c;")
        self._suffix_error.hide()

        suffix_input_layout = QHBoxLayout()
        suffix_input_layout.addWidget(prefix_lbl)
        suffix_input_layout.addWidget(self._suffix_edit)
        suffix_input_layout.addWidget(dotxlsx_lbl)

        self._run_btn = QPushButton("Run")
        self._run_btn.setObjectName("primary")
        self._run_btn.setEnabled(False)
        self._run_btn.clicked.connect(lambda: self.run_requested.emit())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.addWidget(input_lbl)
        layout.addLayout(input_row_layout)
        layout.addWidget(suffix_lbl)
        layout.addLayout(suffix_input_layout)
        layout.addWidget(self._suffix_error)
        layout.addWidget(self._run_btn)

        self._input_edit.textChanged.connect(self._on_changed)
        self._suffix_edit.textChanged.connect(self._on_changed)

    @property
    def input_file(self) -> str:
        return self._input_edit.text().strip()

    @property
    def suffix(self) -> str:
        return self._suffix_edit.text().strip()

    @property
    def suffix_valid(self) -> bool:
        return bool(self.suffix) and not bool(_ILLEGAL_RE.search(self.suffix))

    def set_run_enabled(self, enabled: bool) -> None:
        self._run_btn.setEnabled(enabled)

    def _on_changed(self) -> None:
        raw = self._suffix_edit.text()
        self._suffix_error.setVisible(bool(raw) and bool(_ILLEGAL_RE.search(raw)))
        self.changed.emit()

    def _browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select master input file", self._input_folder, "Excel files (*.xlsx)"
        )
        if path:
            self._input_edit.setText(path)
```

- [ ] **Step 2: Append `_EmptyState` to `src/ui/main_view.py`**

```python
class _EmptyState(QWidget):
    add_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        icon_lbl = QLabel("📁")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        heading_lbl = QLabel("No target workbooks configured")
        heading_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        body_lbl = QLabel(
            "Quarterly copies sheets from your master input file into pre-configured "
            "target workbooks. Add the first one to get started — you can map up to "
            "two tabs per workbook."
        )
        body_lbl.setObjectName("secondary")
        body_lbl.setWordWrap(True)
        body_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        add_btn = QPushButton("Add target workbook")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(lambda: self.add_requested.emit())

        card = QWidget()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(12)
        card_layout.addWidget(icon_lbl)
        card_layout.addWidget(heading_lbl)
        card_layout.addWidget(body_lbl)
        card_layout.addWidget(add_btn, 0, Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(card)
        layout.addStretch()
```

- [ ] **Step 3: Append `MainView` to `src/ui/main_view.py`**

```python
class MainView(QWidget):
    navigate_to_settings = Signal()
    run_requested = Signal(str, str)  # input_file, suffix

    def __init__(self, config: Config, parent: QWidget | None = None):
        super().__init__(parent)

        self._empty_state = _EmptyState()
        self._run_bar = RunBar(config.input_folder)
        self._wb_table = WorkbookTable(config.workbooks)
        self._log_panel = LogPanel()

        run_page = QWidget()
        run_page_layout = QVBoxLayout(run_page)
        run_page_layout.setContentsMargins(0, 0, 0, 0)
        run_page_layout.setSpacing(8)
        run_page_layout.addWidget(self._run_bar)
        run_page_layout.addWidget(self._wb_table, 1)
        run_page_layout.addWidget(self._log_panel)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._empty_state)  # index 0
        self._stack.addWidget(run_page)           # index 1

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._stack)

        self._stack.setCurrentIndex(1 if config.workbooks else 0)

        self._empty_state.add_requested.connect(self.navigate_to_settings)
        self._run_bar.changed.connect(self._update_run_button)
        self._wb_table.selection_changed.connect(self._update_run_button)
        self._run_bar.run_requested.connect(self._on_run)

        self._update_run_button()

    def _update_run_button(self) -> None:
        can = (
            bool(self._run_bar.input_file)
            and self._run_bar.suffix_valid
            and bool(self._wb_table.get_selected_ids())
        )
        self._run_bar.set_run_enabled(can)

    def _on_run(self) -> None:
        self.run_requested.emit(self._run_bar.input_file, self._run_bar.suffix)

    def show_results(
        self, results: list[RunResult], suffix: str, timestamp: str
    ) -> None:
        self._log_panel.show_results(results, suffix, timestamp)
```

- [ ] **Step 4: Run all MainView/RunBar tests**

```bash
source venv/bin/activate && pytest tests/ui/test_main_view.py -v
```

Expected: all 11 tests pass:
```
PASSED test_get_selected_ids_returns_checked_only
PASSED test_header_checkbox_toggles_all_rows
PASSED test_log_panel_hidden_on_init
PASSED test_log_panel_visible_after_show_results
PASSED test_log_panel_pill_counts_match_results
PASSED test_run_button_disabled_when_no_input_file
PASSED test_run_button_disabled_when_no_suffix
PASSED test_run_button_disabled_when_suffix_has_illegal_chars
PASSED test_run_button_disabled_when_no_rows_checked
PASSED test_run_button_enabled_when_all_conditions_met
PASSED test_empty_state_shown_when_no_workbooks
```

- [ ] **Step 5: Run full suite**

```bash
source venv/bin/activate && pytest
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/ui/main_view.py
git commit -m "feat: add RunBar, EmptyState, and MainView — Phase 6 complete"
```

---

## Self-Review Notes

**Spec coverage check:**

| Spec requirement | Covered by |
|---|---|
| Run button disabled — no input file | Task 4 test + Task 5 impl (`_update_run_button`) |
| Run button disabled — no suffix | Task 4 test + Task 5 impl |
| Run button disabled — illegal chars | Task 4 test + `suffix_valid` property |
| Run button disabled — no rows checked | Task 4 test + `get_selected_ids()` check |
| Run button enabled — all conditions met | Task 4 test + Task 5 impl |
| Input file browse button | Task 5 `_browse_input` |
| Suffix `_` prefix / `.xlsx` suffix labels | Task 5 `RunBar.__init__` |
| Suffix inline error label | Task 5 `_suffix_error` label + `_on_changed` |
| `get_selected_ids()` | Task 2 test + impl |
| Header checkbox toggles all rows | Task 2 test + impl |
| Rows dim when unchecked | Task 2 `set_dimmed` / `_on_row_changed` |
| WorkbookTable columns | Task 2 `_WorkbookRow` + header widget |
| LogPanel hidden on init | Task 3 test + `self.hide()` |
| `show_results()` makes panel visible | Task 3 test + `self.show()` in `show_results` |
| Summary pill counts | Task 3 test + pill text logic |
| Per-workbook rows in LogPanel | Task 3 `_make_row` |
| Copy log button | Task 3 `_copy_log` |
| Dismiss button | Task 3 `_on_dismiss` |
| Empty state shown when no workbooks | Task 4 test + Task 5 `_stack.setCurrentIndex` |
| Empty state "Add" navigates to settings | Task 5 `add_requested → navigate_to_settings` |

All spec requirements are covered. No placeholders or TBDs in any step.
