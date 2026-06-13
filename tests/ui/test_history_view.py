from PySide6.QtWidgets import QLabel

from src.log import RunRecord, RunResult, append_record
from src.ui.history_view import HistoryView


def _make_record(timestamp: str, suffix: str, statuses: list[str]) -> RunRecord:
    results = [
        RunResult(
            workbook_id=f"wb{i}",
            filename=f"wb{i}.xlsx",
            status=s,
            message="",
            output_filename=None if s == "error" else f"wb{i}_out.xlsx",
            rows_written=0 if s == "error" else 5,
            duration_ms=100,
        )
        for i, s in enumerate(statuses)
    ]
    return RunRecord(timestamp=timestamp, input_filename="master.xlsx", suffix=suffix, results=results)


def test_records_most_recent_first(qtbot, tmp_path):
    log_path = tmp_path / "runs.log"
    older = _make_record("2026-01-01T10:00:00", "Q4", ["success"])
    newer = _make_record("2026-06-01T10:00:00", "Q1", ["success"])
    append_record(log_path, older)
    append_record(log_path, newer)

    view = HistoryView(log_path=log_path)
    qtbot.addWidget(view)
    view.show()

    rows = view.findChildren(QLabel, "history_row_timestamp")
    assert len(rows) == 2
    assert rows[0].text() == "2026-06-01T10:00:00"
    assert rows[1].text() == "2026-01-01T10:00:00"


def test_empty_state_when_no_log(qtbot, tmp_path):
    log_path = tmp_path / "nonexistent.log"

    view = HistoryView(log_path=log_path)
    qtbot.addWidget(view)
    view.show()

    empty_lbl = view.findChild(QLabel, "empty_state_label")
    assert empty_lbl is not None
    assert empty_lbl.isVisible()


def test_reload_on_reshown(qtbot, tmp_path):
    log_path = tmp_path / "runs.log"
    older = _make_record("2026-01-01T10:00:00", "Q4", ["success"])
    append_record(log_path, older)

    view = HistoryView(log_path=log_path)
    qtbot.addWidget(view)
    view.show()
    view.hide()

    newer = _make_record("2026-06-01T10:00:00", "Q1", ["success"])
    append_record(log_path, newer)
    view.show()

    rows = view.findChildren(QLabel, "history_row_timestamp")
    assert len(rows) == 2
    assert rows[0].text() == "2026-06-01T10:00:00"
    assert rows[1].text() == "2026-01-01T10:00:00"
