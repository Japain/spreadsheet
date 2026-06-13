# History View — Design Spec

**Date:** 2026-06-12
**Phase:** 8
**File:** `src/ui/history_view.py`
**Tests:** `tests/ui/test_history_view.py`

---

## Overview

Read-only view that displays past processing runs in reverse-chronological order. Reads `runs.log` via `read_records()` from `src/log.py` every time the view becomes visible (`showEvent`), so runs completed mid-session appear without a restart.

---

## Interface

```python
class HistoryView(QWidget):
    def __init__(self, log_path: Path = DEFAULT_LOG_PATH, parent=None)
    def showEvent(self, event) -> None   # reloads records on every activation
```

`main.py` already instantiates `HistoryView()` with no args; tests pass a `tmp_path`-based path for isolation.

---

## Layout

**Populated state** — `QScrollArea` containing one `_HistoryRow` per `RunRecord`, most-recent-first:

| Field | Widget | Notes |
|---|---|---|
| Timestamp | `QLabel`, `objectName="history_row_timestamp"`, `setProperty("monospace", True)` | ISO-8601 string from `RunRecord.timestamp`; objectName used for test lookup, property drives QSS monospace font via `QLabel[monospace=true]` |
| Suffix | `QLabel` | `RunRecord.suffix` |
| Input filename | `QLabel` | `RunRecord.input_filename` |
| N ok | `QLabel`, `objectName="pill_success"` | count of `status=="success"` results |
| N skipped | `QLabel`, `objectName="pill_skipped"` | count of `status=="skipped"` results |
| N error | `QLabel`, `objectName="pill_error"` | count of `status=="error"` results |

**Empty state** — shown when `runs.log` does not exist or has no parseable records:

- Centered `QLabel` reading "No run history yet"
- `objectName="empty_state_label"` for test lookup

---

## Data Flow

1. `showEvent` fires when user navigates to the view.
2. `read_records(self._log_path)` is called — returns `[]` if file missing.
3. Scroll area is rebuilt: old `_HistoryRow` widgets are deleted, new ones inserted.
4. If list is empty, scroll area is hidden and empty-state label is shown; otherwise reversed.

---

## Testing

| Test | Assertion |
|---|---|
| `test_records_most_recent_first` | Build a log with 2 records (older then newer). Show the view. First visible row's timestamp label matches the newer record. |
| `test_empty_state_when_no_log` | Construct `HistoryView` with a path to a nonexistent file. Empty-state label is visible. |

---

## Constraints

- No write operations — view is read-only.
- Pill styling matches existing `LogPanel` pattern (set `objectName`, rely on QSS from `styles.py`).
- `_HistoryRow` is a private widget class in the same file; not exported.
