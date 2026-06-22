# Filename Autocomplete — Design Spec

**Date:** 2026-06-19
**Status:** Approved

## Problem

In the Edit workbook panel, users must manually type the target workbook filename. There is no discovery mechanism — if the target folder is already set, the app has enough information to offer completions from the filesystem.

## Scope

Single file: `src/ui/_workbook_detail_pane.py`. No other files are modified.

## Design

### Behaviour

- When the filename field is focused, a popup dropdown appears listing `.xlsx` files found in the target folder.
- The list filters as the user types.
- Matching is case-insensitive (Windows filesystems are case-insensitive).
- If the folder is empty, invalid, or contains no `.xlsx` files, the dropdown does not appear — the field remains fully editable.
- A filename not present in the folder may still be typed freely; the completer suggests but does not restrict.

### Refresh triggers

| Trigger | Why |
|---|---|
| `_folder_field.textChanged` | Covers manual typing and the Browse button (Browse calls `setText`, which fires `textChanged`) |
| `_filename_field` focus event | Catches `.xlsx` files added to the folder since the last folder-field change |

### Implementation

**Additions to `__init__`:**

1. After `_filename_field` is created, instantiate `QCompleter` with `PopupCompletion` mode and `Qt.CaseInsensitive`.
2. Attach to `_filename_field` via `setCompleter()`.
3. Connect `_folder_field.textChanged` to `_refresh_completer`.
4. Call `_refresh_completer(workbook.folder)` to pre-populate on load.

**New method `_refresh_completer(folder: str) -> None`:**

- If `Path(folder).is_dir()`: glob `*.xlsx`, sort, extract names only (no full paths), set as a `QStringListModel` on the completer.
- Otherwise: set an empty model.

**Override `_filename_field` focus:**

- Install an event filter on `_filename_field` (via `installEventFilter`) that calls `_refresh_completer(self._folder_field.text())` when it receives a `QEvent.Type.FocusIn` event.

### Imports added

- `QCompleter` from `PySide6.QtWidgets`
- `QStringListModel` from `PySide6.QtCore`
- `Qt` from `PySide6.QtCore`
- `Path` from `pathlib` (already available via `src.config` import chain — add explicit import)

## Testing

- Completer is populated when folder field contains a valid directory with `.xlsx` files.
- Completer is empty when folder is blank, non-existent, or contains no `.xlsx` files.
- Completer refreshes when folder field text changes.
- Completer refreshes when filename field is focused.
- Non-`.xlsx` files in the folder do not appear in suggestions.
- User can still type a filename not present in the folder.
