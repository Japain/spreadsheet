# Settings View — Phase 7 Design

**Date:** 2026-06-10
**Branch:** phase7
**Plan ref:** `IMPLEMENTATION_PLAN.md` — Phase 7

---

## Overview

Implement `src/ui/settings_view.py`: a two-pane settings screen where the user manages target workbooks and their tab mappings. All edits auto-save to `config.json` on every change.

---

## Architecture

Four classes, all in `src/ui/settings_view.py`, following the same component decomposition pattern as `main_view.py`.

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

## Files Changed

| File | Change |
|---|---|
| `src/ui/settings_view.py` | Full implementation (currently a stub) |
| `src/main.py` | Pass `DEFAULT_CONFIG_PATH` to `SettingsView` constructor |
| `tests/ui/test_settings_view.py` | New test file |
