# Filename Autocomplete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a popup dropdown autocomplete to the filename field in the Edit workbook panel, populated from `.xlsx` files found in the target folder.

**Architecture:** All changes are confined to `src/ui/_workbook_detail_pane.py`. A `QCompleter` with a `QStringListModel` is attached to `_filename_field`. The model is refreshed (a) whenever `_folder_field.textChanged` fires, and (b) when `_filename_field` gains focus via an event filter installed on `_WorkbookDetailPane` itself.

**Tech Stack:** PySide6 (`QCompleter`, `QStringListModel`, `QEvent`), pytest-qt

## Global Constraints

- All production code changes must be in `src/ui/_workbook_detail_pane.py` only.
- Autocomplete suggests only `.xlsx` filenames (basename only, not full path), sorted alphabetically, case-insensitive matching.
- The filename field remains freely editable — the completer suggests but does not restrict.
- Tests live in `tests/ui/test_settings_view.py`.
- Always activate venv before running tests: `source venv/bin/activate`
- Run tests with: `pytest tests/ui/test_settings_view.py -v`

---

### Task 1: Add `_refresh_completer` and wire to folder changes

**Files:**
- Modify: `src/ui/_workbook_detail_pane.py`
- Test: `tests/ui/test_settings_view.py`

**Interfaces:**
- Produces: `_WorkbookDetailPane._refresh_completer(folder: str) -> None` — globs `Path(folder).glob("*.xlsx")`, sorts basenames, sets them on `self._completer` via `QStringListModel`; sets empty model if folder is not a valid directory.
- Produces: `_filename_field.completer()` — returns a `QCompleter` with `PopupCompletion` mode and `CaseInsensitive` sensitivity.
- Produces: `_folder_field` has `objectName == "folder_field"` (needed by tests to locate it via `findChild`).

- [ ] **Step 1: Write the failing tests**

Add to `tests/ui/test_settings_view.py`:

```python
def test_completer_populated_from_folder(qtbot, tmp_path):
    folder = tmp_path / "target"
    folder.mkdir()
    (folder / "Report.xlsx").touch()
    (folder / "Budget.xlsx").touch()
    (folder / "notes.txt").touch()  # must not appear

    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder=str(folder), mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)

    field = v.findChild(QLineEdit, "filename_field")
    completer = field.completer()
    assert completer is not None
    model = completer.model()
    names = sorted(model.data(model.index(i, 0)) for i in range(model.rowCount()))
    assert names == ["Budget.xlsx", "Report.xlsx"]


def test_completer_empty_when_folder_invalid(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder="/nonexistent/path/xyz", mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)

    field = v.findChild(QLineEdit, "filename_field")
    assert field.completer().model().rowCount() == 0


def test_completer_refreshes_on_folder_change(qtbot, tmp_path):
    folder1 = tmp_path / "folder1"
    folder1.mkdir()
    (folder1 / "Alpha.xlsx").touch()
    folder2 = tmp_path / "folder2"
    folder2.mkdir()
    (folder2 / "Beta.xlsx").touch()

    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder=str(folder1), mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)

    folder_field = v.findChild(QLineEdit, "folder_field")
    folder_field.setText(str(folder2))

    field = v.findChild(QLineEdit, "filename_field")
    model = field.completer().model()
    names = [model.data(model.index(i, 0)) for i in range(model.rowCount())]
    assert "Beta.xlsx" in names
    assert "Alpha.xlsx" not in names
```

- [ ] **Step 2: Run tests to verify they fail**

```
source venv/bin/activate && pytest tests/ui/test_settings_view.py::test_completer_populated_from_folder tests/ui/test_settings_view.py::test_completer_empty_when_folder_invalid tests/ui/test_settings_view.py::test_completer_refreshes_on_folder_change -v
```

Expected: all three FAIL — `field.completer()` returns `None` (no completer attached yet), `findChild(QLineEdit, "folder_field")` returns `None` (no object name set yet).

- [ ] **Step 3: Implement**

Apply all of the following changes to `src/ui/_workbook_detail_pane.py`:

**3a. Update the import block** (replace the existing imports at the top of the file):

```python
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QStringListModel, Signal
from PySide6.QtWidgets import (
    QCompleter,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import TabMapping, Workbook
from src.ui._mapping_row import _MappingRow
```

**3b. Add `setObjectName` to `_folder_field`** — find this block in `__init__`:

```python
        self._folder_field = QLineEdit(workbook.folder)
        browse_btn = QPushButton("Browse…")
```

Change it to:

```python
        self._folder_field = QLineEdit(workbook.folder)
        self._folder_field.setObjectName("folder_field")
        browse_btn = QPushButton("Browse…")
```

**3c. Add completer setup** — find this block in `__init__`:

```python
        self._filename_field = QLineEdit(workbook.filename)
        self._filename_field.setObjectName("filename_field")
        layout.addWidget(self._filename_field)
```

Change it to:

```python
        self._filename_field = QLineEdit(workbook.filename)
        self._filename_field.setObjectName("filename_field")
        layout.addWidget(self._filename_field)

        self._completer = QCompleter(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._filename_field.setCompleter(self._completer)
```

**3d. Connect folder change and seed the completer** — find this block near the end of `__init__`:

```python
        # Connect field signals after layout is fully built
        self._filename_field.textChanged.connect(self._on_filename_changed)
        self._folder_field.textChanged.connect(self._on_folder_changed)

        self._refresh_mapping_controls()
```

Change it to:

```python
        # Connect field signals after layout is fully built
        self._filename_field.textChanged.connect(self._on_filename_changed)
        self._folder_field.textChanged.connect(self._on_folder_changed)
        self._folder_field.textChanged.connect(self._refresh_completer)
        self._refresh_completer(workbook.folder)

        self._refresh_mapping_controls()
```

**3e. Add `_refresh_completer` method** — add after `_on_folder_changed`:

```python
    def _refresh_completer(self, folder: str) -> None:
        path = Path(folder)
        if path.is_dir():
            names = sorted(p.name for p in path.glob("*.xlsx"))
        else:
            names = []
        self._completer.setModel(QStringListModel(names, self._completer))
```

- [ ] **Step 4: Run new tests to verify they pass**

```
source venv/bin/activate && pytest tests/ui/test_settings_view.py::test_completer_populated_from_folder tests/ui/test_settings_view.py::test_completer_empty_when_folder_invalid tests/ui/test_settings_view.py::test_completer_refreshes_on_folder_change -v
```

Expected: 3 PASSED

- [ ] **Step 5: Run full test suite to check for regressions**

```
source venv/bin/activate && pytest -v
```

Expected: all existing tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/ui/_workbook_detail_pane.py tests/ui/test_settings_view.py
git commit -m "feat: add filename autocomplete from target folder"
```

---

### Task 2: Refresh completer when filename field gains focus

**Files:**
- Modify: `src/ui/_workbook_detail_pane.py`
- Test: `tests/ui/test_settings_view.py`

**Interfaces:**
- Consumes: `_WorkbookDetailPane._refresh_completer(folder: str) -> None` from Task 1
- Produces: `_WorkbookDetailPane.eventFilter(obj, event)` — calls `_refresh_completer(self._folder_field.text())` when `obj is self._filename_field` and `event.type() == QEvent.Type.FocusIn`; always returns `super().eventFilter(obj, event)`.

- [ ] **Step 1: Write the failing test**

Add to `tests/ui/test_settings_view.py`:

```python
from PySide6.QtWidgets import QApplication

def test_completer_refreshes_on_filename_field_focus(qtbot, tmp_path):
    folder = tmp_path / "target"
    folder.mkdir()

    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder=str(folder), mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)
    v.show()
    qtbot.waitExposed(v)

    # Add a file after the view was created (completer initially empty)
    (folder / "LateArrival.xlsx").touch()

    field = v.findChild(QLineEdit, "filename_field")
    field.setFocus()
    QApplication.processEvents()

    model = field.completer().model()
    names = [model.data(model.index(i, 0)) for i in range(model.rowCount())]
    assert "LateArrival.xlsx" in names
```

- [ ] **Step 2: Run test to verify it fails**

```
source venv/bin/activate && pytest tests/ui/test_settings_view.py::test_completer_refreshes_on_filename_field_focus -v
```

Expected: FAIL — `"LateArrival.xlsx"` not in names (no event filter installed yet).

- [ ] **Step 3: Implement the event filter**

**3a. Update the import block** — add `QEvent` to the `PySide6.QtCore` import:

```python
from PySide6.QtCore import QEvent, Qt, QStringListModel, Signal
```

**3b. Install the event filter** — find this block in `__init__`:

```python
        self._completer = QCompleter(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._filename_field.setCompleter(self._completer)
```

Change it to:

```python
        self._completer = QCompleter(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._filename_field.setCompleter(self._completer)
        self._filename_field.installEventFilter(self)
```

**3c. Add `eventFilter` override** — add after `_refresh_completer`:

```python
    def eventFilter(self, obj, event) -> bool:
        if obj is self._filename_field and event.type() == QEvent.Type.FocusIn:
            self._refresh_completer(self._folder_field.text())
        return super().eventFilter(obj, event)
```

- [ ] **Step 4: Run test to verify it passes**

```
source venv/bin/activate && pytest tests/ui/test_settings_view.py::test_completer_refreshes_on_filename_field_focus -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite to check for regressions**

```
source venv/bin/activate && pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/ui/_workbook_detail_pane.py tests/ui/test_settings_view.py
git commit -m "feat: refresh filename autocomplete on field focus"
```
