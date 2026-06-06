# Phase 10 Skeleton — Main Window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `QMainWindow` shell — sidebar, nav, and `QStackedWidget` — with stub view files so the app is runnable before any content views exist.

**Architecture:** `MainWindow` owns the full window layout: a fixed-width sidebar (220px) and a `QStackedWidget` content area. Three stub view files (`main_view.py`, `settings_view.py`, `history_view.py`) are created as minimal `QWidget` subclasses so imports are correct from day one; each phase replaces the stub with real implementation. `MainWindow` accepts an optional `Config` parameter so tests bypass the real config file on disk.

**Tech Stack:** PySide6 (`QMainWindow`, `QStackedWidget`, `QWidget`, `QPushButton`), `src.ui.styles.STYLESHEET`, `src.config.Config` / `DEFAULT_CONFIG_PATH`, pytest-qt (`qtbot`)

---

## File Map

| Path | Action | Responsibility |
|---|---|---|
| `src/ui/main_view.py` | **Create** | Stub `MainView(QWidget)` — replaced in Phase 6 |
| `src/ui/settings_view.py` | **Create** | Stub `SettingsView(QWidget)` — replaced in Phase 7 |
| `src/ui/history_view.py` | **Create** | Stub `HistoryView(QWidget)` — replaced in Phase 8 |
| `src/main.py` | **Create** | `MainWindow` class + `main()` entry point |
| `tests/ui/test_main_window.py` | **Create** | 2 nav smoke tests |

> **Note for Phase 6:** `src/ui/main_view.py` will already exist as a stub when Phase 6 runs. Phase 6 Task 2 should **replace** (not create) this file with the full `WorkbookTable`, `LogPanel`, `RunBar`, and `MainView` implementation.

---

## Task 1: Stub view files

**Files:**
- Create: `src/ui/main_view.py`
- Create: `src/ui/settings_view.py`
- Create: `src/ui/history_view.py`

- [ ] **Step 1: Create the three stub files**

`src/ui/main_view.py`:
```python
from PySide6.QtWidgets import QWidget

from src.config import Config


class MainView(QWidget):
    def __init__(self, config: Config, parent: QWidget | None = None):
        super().__init__(parent)
```

`src/ui/settings_view.py`:
```python
from PySide6.QtWidgets import QWidget


class SettingsView(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
```

`src/ui/history_view.py`:
```python
from PySide6.QtWidgets import QWidget


class HistoryView(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
```

- [ ] **Step 2: Verify they import cleanly**

```bash
source venv/bin/activate && python -c "
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView
from src.ui.history_view import HistoryView
print('OK')
"
```

Expected: `OK`

- [ ] **Step 3: Run existing test suite to confirm no regressions**

```bash
source venv/bin/activate && pytest
```

Expected: all prior tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/ui/main_view.py src/ui/settings_view.py src/ui/history_view.py
git commit -m "feat: add stub view files for MainView, SettingsView, HistoryView"
```

---

## Task 2: Failing nav tests

**Files:**
- Create: `tests/ui/test_main_window.py`

- [ ] **Step 1: Create the test file with two failing nav tests**

```python
# tests/ui/test_main_window.py
import pytest
from src.config import Config
from src.main import MainWindow
from src.ui.settings_view import SettingsView
from src.ui.history_view import HistoryView


def _config() -> Config:
    return Config(input_folder="", workbooks=[])


def test_configure_nav_switches_to_settings_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_configure.click()
    assert window._stack.currentIndex() == 1
    assert isinstance(window._stack.currentWidget(), SettingsView)


def test_history_nav_switches_to_history_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_history.click()
    assert window._stack.currentIndex() == 2
    assert isinstance(window._stack.currentWidget(), HistoryView)
```

- [ ] **Step 2: Run to confirm failure**

```bash
source venv/bin/activate && pytest tests/ui/test_main_window.py -v
```

Expected: `ImportError: cannot import name 'MainWindow' from 'src.main'` — both tests fail.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/ui/test_main_window.py
git commit -m "test: add failing MainWindow nav smoke tests"
```

---

## Task 3: MainWindow implementation

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Create `src/main.py`**

```python
from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.config import Config, DEFAULT_CONFIG_PATH
from src.ui.history_view import HistoryView
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView
from src.ui.styles import STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self, config: Config | None = None):
        super().__init__()
        if config is None:
            config = Config.load(DEFAULT_CONFIG_PATH)

        self.setWindowTitle("Quarterly — Workbook Updater")
        self.setFixedSize(1280, 820)
        self.setStyleSheet(STYLESHEET)

        self._main_view = MainView(config)
        self._settings_view = SettingsView()
        self._history_view = HistoryView()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._main_view)      # index 0
        self._stack.addWidget(self._settings_view)  # index 1
        self._stack.addWidget(self._history_view)   # index 2

        sidebar = self._build_sidebar()

        central = QWidget()
        central.setObjectName("central")
        body_layout = QHBoxLayout(central)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(sidebar)
        body_layout.addWidget(self._stack, 1)

        self.setCentralWidget(central)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        mark_lbl = QLabel("Q")
        mark_lbl.setStyleSheet(
            "background:#4b6bdf; color:#fff; border-radius:6px;"
            " padding:4px 10px; font-weight:bold; font-size:16px;"
        )
        mark_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        brand_name_lbl = QLabel("Quarterly")
        brand_name_lbl.setStyleSheet("font-weight:bold; font-size:14px;")
        brand_sub_lbl = QLabel("Workbook Updater")
        brand_sub_lbl.setObjectName("secondary")

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)
        brand_text_layout.addWidget(brand_name_lbl)
        brand_text_layout.addWidget(brand_sub_lbl)

        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.addWidget(mark_lbl)
        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()

        self._nav_run = QPushButton("Run")
        self._nav_configure = QPushButton("Configure")
        self._nav_history = QPushButton("Run History")

        for btn in (self._nav_run, self._nav_configure, self._nav_history):
            btn.setObjectName("nav_item")
            btn.setStyleSheet(
                "QPushButton { text-align:left; padding:8px 12px;"
                " border:none; border-radius:6px; color:#1b1d22; background:transparent; }"
                " QPushButton:hover { background:#ebebeb; }"
                " QPushButton[active=true] { background:#e8ecfc; color:#4b6bdf; font-weight:bold; }"
            )
            btn.setCheckable(False)

        self._nav_run.clicked.connect(lambda: self._switch_page(0))
        self._nav_configure.clicked.connect(lambda: self._switch_page(1))
        self._nav_history.clicked.connect(lambda: self._switch_page(2))

        config_lbl = QLabel(str(DEFAULT_CONFIG_PATH))
        config_lbl.setObjectName("secondary")
        config_lbl.setWordWrap(True)
        config_lbl.setStyleSheet("font-size:10px;")

        version_lbl = QLabel("v1.0.0")
        version_lbl.setObjectName("secondary")
        version_lbl.setStyleSheet("font-size:10px;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 12)
        sidebar_layout.setSpacing(2)
        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(16)
        sidebar_layout.addWidget(self._nav_run)
        sidebar_layout.addWidget(self._nav_configure)
        sidebar_layout.addWidget(self._nav_history)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(config_lbl)
        sidebar_layout.addWidget(version_lbl)

        self._update_nav_active(0)
        return sidebar

    def _switch_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._update_nav_active(index)

    def _update_nav_active(self, active_index: int) -> None:
        for i, btn in enumerate(
            [self._nav_run, self._nav_configure, self._nav_history]
        ):
            btn.setProperty("active", i == active_index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("quarterly")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the nav tests**

```bash
source venv/bin/activate && pytest tests/ui/test_main_window.py -v
```

Expected:
```
PASSED tests/ui/test_main_window.py::test_configure_nav_switches_to_settings_view
PASSED tests/ui/test_main_window.py::test_history_nav_switches_to_history_view
```

- [ ] **Step 3: Run full test suite**

```bash
source venv/bin/activate && pytest
```

Expected: all tests pass.

- [ ] **Step 4: Smoke-test the app visually**

```bash
source venv/bin/activate && python src/main.py
```

Expected: a 1280×820 window opens with a sidebar showing "Q / Quarterly / Workbook Updater", three nav buttons (Run, Configure, Run History), and a blank content area. Clicking each nav button should switch the active highlight on the sidebar. Close with the window's × button.

- [ ] **Step 5: Commit**

```bash
git add src/main.py tests/ui/test_main_window.py
git commit -m "feat: Phase 10 skeleton — MainWindow with sidebar nav and stub views"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|---|---|
| `QApplication` setup with app name | Task 3 `main()` — `app.setApplicationName("quarterly")` |
| `STYLESHEET` applied | Task 3 `self.setStyleSheet(STYLESHEET)` |
| `QMainWindow` fixed 1280×820, non-resizable | Task 3 `self.setFixedSize(1280, 820)` |
| Sidebar 220px | Task 3 `sidebar.setFixedWidth(220)` |
| Brand mark / app name | Task 3 `_build_sidebar` — "Q" mark + "Quarterly" + "Workbook Updater" |
| Nav items: Run, Configure, Run History | Task 3 `_nav_run`, `_nav_configure`, `_nav_history` |
| Footer: config path + version | Task 3 `config_lbl` + `version_lbl` |
| `QStackedWidget` with 3 views | Task 3 `self._stack` — indices 0/1/2 |
| Nav items switch pages | Task 3 `_switch_page` + test coverage |
| Config loaded at startup | Task 3 `Config.load(DEFAULT_CONFIG_PATH)` |
| Config passed to MainView | Task 3 `MainView(config)` |
| Stub files with correct signatures | Task 1 — `MainView(config)`, `SettingsView()`, `HistoryView()` |
| Clicking Configure → SettingsView | Task 2 + 3 test |
| Clicking Run History → HistoryView | Task 2 + 3 test |

**Deferred (Phase 10 wiring, after Phase 9):**
- `WorkbookProcessor` signal wiring
- `ConflictDialog` / `ProgressDialog` integration
- `run_requested` handler
- `MainView.navigate_to_settings` → `_switch_page(1)` connection
