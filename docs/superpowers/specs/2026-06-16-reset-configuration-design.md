# Reset Configuration — Design Spec

**Date:** 2026-06-16
**Status:** Approved

## Summary

Add a "Danger zone" card to the Configure (Settings) view that lets the user reset the entire configuration — removing all target workbooks and clearing the default input folder — with an itemised confirmation dialog before any data is destroyed.

## Placement

A new danger zone card is added to `SettingsView.__init__`, inserted into `outer` (the top-level `QVBoxLayout`) directly below the existing global settings card returned by `_build_global_card`. It has a red left border and contains:

- A short description label: "Remove all target workbooks and reset the default input folder."
- A "Reset…" button (the `…` signals a dialog follows).

The card is always visible in the Configure view; it is not conditional on whether workbooks exist.

## Reset Scope

Resetting clears:
1. `config.workbooks` → `[]`
2. `config.input_folder` → `""`

Both are persisted to disk immediately after clearing.

## Confirmation Dialog

A `QMessageBox` is shown before any data is modified:

- **Title:** "Reset configuration?"
- **Body:** Lists exactly what will be cleared:
  - "All target workbooks (N)" where N is the current workbook count
  - "Default input folder"
- **Warning line:** "This cannot be undone."
- **Buttons:** Cancel (default focus) | Reset (destructive)

If the user cancels, nothing changes. Only on acceptance does the reset proceed.

## Data Flow

```
Reset button clicked
  → QMessageBox shown
  → User cancels → nothing happens
  → User confirms
      → emit workbook_removed(id) for each workbook
      → config.workbooks = []
      → config.input_folder = ""
      → config.save(config_path)
      → SettingsView UI updated:
          - all _WorkbookListItem widgets removed
          - _empty_lbl shown, workbooks title reset to "(0)"
          - _selected_index = None, detail pane cleared, placeholder shown
          - input_folder_field.setText("")
```

The existing `workbook_removed` signal (already connected to `MainView.remove_workbook`) handles the run-view cleanup automatically — no new wiring needed in `MainWindow`.

## UI Changes

| File | Change |
|---|---|
| `src/ui/settings_view.py` | Add `_build_danger_zone_card()` helper; call it from `__init__`; add `_on_reset` method |

No changes needed to `main_view.py`, `main.py`, or any other file.

## Testing

| Test | Location |
|---|---|
| Clicking Reset with 2 workbooks emits `workbook_removed` twice | `tests/ui/test_settings_view.py` |
| Config workbooks are empty after reset | `tests/ui/test_settings_view.py` |
| Config input folder is empty string after reset | `tests/ui/test_settings_view.py` |
| Cancelling the dialog leaves config unchanged | `tests/ui/test_settings_view.py` |
| SettingsView list is empty and empty label visible after reset | `tests/ui/test_settings_view.py` |
| MainView returns to empty state after reset | `tests/ui/test_main_window.py` |

## Out of Scope

- Undo / restore after reset
- Selective reset (workbooks only, or folder only)
- Confirmation via typed text (overkill for this use case)
