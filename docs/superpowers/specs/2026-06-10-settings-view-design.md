# Settings View — Phase 7 Design

**Date:** 2026-06-10
**Branch:** phase7
**Plan ref:** `IMPLEMENTATION_PLAN.md` — Phase 7

---

## Overview

Implement `src/ui/settings_view.py`: a two-pane settings screen where the user manages target workbooks and their tab mappings. All edits auto-save to `config.json` on every change.

---

## Architecture

Four classes, split into `src/ui/settings_view.py` plus a few small private sub-component modules, following the same component decomposition pattern as `main_view.py`.

| Class | Role |
|---|---|
| `_MappingRow(QWidget)` | One input → target mapping row with a remove button; emits `remove_requested` signal |
| `_WorkbookDetailPane(QWidget)` | Right pane — filename field, folder field + browse, 1–2 `_MappingRow`s, add mapping button, remove workbook button; emits `workbook_removed` signal |
| `_WorkbookListItem(QWidget)` | One left-pane row — filename, folder label, mapping chips; highlights when selected |
| `SettingsView(QWidget)` | Top-level coordinator — global settings card, scrollable workbook list, `_WorkbookDetailPane`, empty placeholder; owns all `Config` mutations and saves |

### Constructor

```python
class SettingsView(QWidget):
    def __init__(self, config: Config, config_path: Path, parent: QWidget | None = None):
```

`MainWindow` updated to pass `DEFAULT_CONFIG_PATH` as the second argument.

---

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Global settings card                                        │
│  Default input folder: [____________________] [Browse…]     │
├──────────────────────┬──────────────────────────────────────┤
│  Workbooks  [Add]    │  Right pane (detail or placeholder)  │
│  ────────────────    │                                       │
│  ▶ Report1.xlsx      │  Filename: [___________________]     │
│    /target/folder1   │  Folder:   [___________________] [Browse] │
│    Data → Data       │                                       │
│                      │  Data      → Data        [−]         │
│  Report2.xlsx        │  [+ Add mapping]                     │
│    /target/folder2   │                                       │
│    Summary→Summary   │  [Remove workbook]                   │
└──────────────────────┴──────────────────────────────────────┘
```

- Left pane: fixed width, scrollable. Header row contains "Workbooks" label and "Add" button. Each `_WorkbookListItem` shows filename (bold), folder (monospace secondary), and mapping chips.
- Right pane: takes remaining width. Shows `_WorkbookDetailPane` when a workbook is selected; shows a centered placeholder label when the list is empty or nothing is selected.
- Global settings card: sits above both panes; contains default input folder field and browse button.

---

## State Model

`SettingsView` holds:
- `self._config: Config` — the shared mutable config object (same reference passed to `MainWindow`)
- `self._config_path: Path` — where to persist on every change
- `self._selected_index: int | None` — which workbook is currently selected in the left pane

All edits mutate `self._config` in-place then call `self._config.save(self._config_path)`. No pending-changes buffer — every keystroke persists immediately.

---

## Data Flow

### Field edit (filename, folder, mapping input/target)
1. `textChanged` signal fires on the `QLineEdit`
2. Mutate `self._config.workbooks[i].<field>` (or `.mappings[j].input/target`)
3. Call `self._config.save(self._config_path)`
4. Refresh the corresponding `_WorkbookListItem` to reflect the new filename/chips

### Add workbook
1. Append `Workbook(id=str(uuid4()), filename="", folder="", mappings=[TabMapping("", "")])` to `self._config.workbooks`
2. Save
3. Create and append a `_WorkbookListItem` to the scroll list
4. Set `_selected_index` to the new item's index and populate the right pane

### Remove workbook
1. Remove `self._config.workbooks[i]`
2. Save
3. Remove the corresponding `_WorkbookListItem`
4. Select the previous item if one exists; else show the placeholder

### Add mapping
1. Append `TabMapping("", "")` to the selected workbook's `mappings`
2. Save
3. Add a `_MappingRow` to `_WorkbookDetailPane`
4. Disable the "Add mapping" button if count is now 2

### Remove mapping
1. Remove `mappings[j]` from the selected workbook
2. Save
3. Remove the `_MappingRow` from `_WorkbookDetailPane`
4. Re-enable "Add mapping" button
5. Keep remove button disabled (not hidden) if only 1 mapping remains

---

## Constraints

- **Mapping count:** 1 minimum, 2 maximum per workbook.
  - "Add mapping" button is disabled when 2 mappings exist.
  - Remove button on each `_MappingRow` is disabled (not hidden) when only 1 mapping remains.
- **New workbook defaults:** empty filename, empty folder, one empty `TabMapping("", "")`.
- **Workbook IDs:** generated with `str(uuid.uuid4())` at add time; never modified.
- **Placeholder:** right pane shows a centered "Select a workbook to configure it" label when no workbook is selected.

---

## Testing

**File:** `tests/ui/test_settings_view.py`
**Pattern:** `qtbot` + `tmp_path`; real config I/O (no mocking of file I/O, per project rules)

### Fixture

```python
@pytest.fixture
def view(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[
            Workbook(id="wb1", filename="Report.xlsx", folder="/target",
                     mappings=[TabMapping(input="Data", target="Data")])
        ],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)
    return v, config_path
```

### Test cases

| Test | Assertion |
|---|---|
| `test_filename_edit_autosaves` | Edit filename field → `Config.load(path).workbooks[0].filename` matches new value |
| `test_add_mapping_disabled_at_two` | Add mapping until count=2 → "Add mapping" button is disabled |
| `test_remove_mapping_disabled_at_one` | One mapping present → remove button on that `_MappingRow` is disabled |
| `test_new_workbook_has_one_mapping` | Add workbook → 1 mapping row present, its remove button disabled |
| `test_remove_workbook` | Click "Remove workbook" → workbook absent from `Config.load(path).workbooks` and absent from list |
| `test_add_workbook_shows_and_selects` | Add workbook → new item in left list, right pane populated (not showing placeholder) |

All tests verify both in-memory state and the config JSON on disk to confirm auto-save is wiring through end-to-end.

---

## Visual QA

### Goal

Confirm `SettingsView` matches the **V1 "Quarterly"** design reference:
`docs/design/spreadsheets/project/Excel Update Tool · standalone.html`, V1 section → Configure view
(`V1Settings` component, accessed via the "Configure" sidebar item inside the V1 artboard).

> **Colour note:** The design and the PySide6 app share the same light palette (`#f4f5f9` background,
> `#ffffff` cards, `#4b6bdf` accent). Colour should match — flag deviations.

---

### Step 1 — Capture reference screenshots with Playwright

Create `scripts/qa_settings_reference.py`:

```python
from playwright.sync_api import sync_playwright
from pathlib import Path

DESIGN = (
    Path(__file__).parents[1]
    / "docs/design/spreadsheets/project/Excel Update Tool · standalone.html"
).resolve()
OUT = Path("docs/qa/reference")
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    page.goto(f"file://{DESIGN}")
    page.wait_for_timeout(1200)  # let React + Babel render

    # The V1 app is the first interactive artboard; click Configure in its sidebar.
    # Playwright resolves coordinates through the design canvas transform.
    page.locator(".v1-side-item", has_text="Configure").first().click()
    page.wait_for_timeout(400)

    # State 1: first workbook auto-selected (populated right pane)
    page.screenshot(path=str(OUT / "settings_populated.png"))

    # State 2: clip just the two-pane settings area (below the global card)
    page.screenshot(
        path=str(OUT / "settings_panes.png"),
        clip={"x": 220, "y": 200, "width": 1060, "height": 620},
    )

    browser.close()

print("Saved to docs/qa/reference/")
```

Run with:
```
pip install playwright && playwright install chromium
python scripts/qa_settings_reference.py
```

---

### Step 2 — Capture app screenshots via Qt grab

Create `scripts/qa_settings_app.py`:

```python
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.config import Config, Workbook, TabMapping
from src.ui.settings_view import SettingsView

OUT = Path("docs/qa/actual")
OUT.mkdir(parents=True, exist_ok=True)

app = QApplication.instance() or QApplication(sys.argv)

config_path = Path("/tmp/qa_settings_config.json")
config = Config(
    input_folder="C:/FP&A/Q1_2026",
    workbooks=[
        Workbook(id="wb1", filename="Report_EMEA.xlsx", folder="C:/Reports/EMEA",
                 mappings=[TabMapping(input="Revenue", target="Q_Data")]),
        Workbook(id="wb2", filename="Report_APAC.xlsx", folder="C:/Reports/APAC",
                 mappings=[TabMapping(input="Revenue", target="Q_Data"),
                            TabMapping(input="Summary", target="Summary")]),
    ],
)
config.save(config_path)

view = SettingsView(config, config_path)
view.resize(1060, 740)  # content area width (1280 minus 220px sidebar)
view.show()
app.processEvents()

# State 1: first workbook auto-selected
view.grab().save(str(OUT / "settings_populated.png"))

print("Saved to docs/qa/actual/")
```

Run with:
```
source venv/bin/activate
python scripts/qa_settings_app.py
```

---

### Step 3 — Visual checklist

Open `docs/qa/reference/settings_populated.png` and `docs/qa/actual/settings_populated.png`
side-by-side and verify each item:

| # | Element | V1 reference | Pass criteria |
|---|---|---|---|
| 1 | Global settings card | Full-width single card; one field (default input folder + browse) + note text | Single-column card; input folder field present; no second column |
| 2 | Two-pane grid | Left pane wider than right (`1.5fr 1fr` split) | Left list visibly wider than the detail pane |
| 3 | List row structure | Excel icon → filename (bold 13px) → folder path (mono 11.5px) → mapping chips | Three tiers; chips show `input → target`; Excel icon present |
| 4 | Active row highlight | Light blue/indigo tint background; no left border | Selected row has distinct background tint; no hard left border |
| 5 | List header | "Target workbooks (N)" label + "Add" button (right-aligned) | Title with count and Add button in header |
| 6 | Empty list placeholder | "No workbooks yet. Click **Add** to create one." | Placeholder text visible when list is empty |
| 7 | Detail pane heading | "Edit workbook" (14px bold) + "Up to two tab mappings per workbook." subtitle | Heading + subtitle present at top of right pane |
| 8 | Field vertical order | Filename → target folder (+ browse) → divider → mappings section → divider → Remove workbook | Same top-to-bottom order |
| 9 | Mapping row columns | `1fr 16px 1fr 24px` — input / arrow (grey) / target / trash (ghost danger) | Four columns; narrow arrow; trash is low-visual-weight danger style |
| 10 | "Tab mappings" header | "Tab mappings · N/2" label + "Add mapping" button (disabled at 2) | Count shown; button disabled state visible when at limit |
| 11 | Column sub-headers | "Input tab (master)" / "Target tab (this workbook)" small grey labels | Both sub-headers present above mapping rows |
| 12 | Remove workbook button | Danger-ghost style (red text, no fill), right-aligned, below final divider | Low-fill danger button at bottom right of detail pane |
| 13 | Empty right pane | "Select a workbook to edit its mappings, or add a new one." | Placeholder text when nothing selected |

---

### Step 4 — Add scripts to Files Changed

Once `scripts/qa_settings_reference.py` and `scripts/qa_settings_app.py` exist, add them to
the file list below.

---

## Files Changed

| File | Change |
|---|---|
| `src/ui/settings_view.py` | Full implementation (currently a stub) |
| `src/main.py` | Pass `DEFAULT_CONFIG_PATH` to `SettingsView` constructor |
| `tests/ui/test_settings_view.py` | New test file |
