from PySide6.QtWidgets import QDialog, QLabel, QPushButton

from src.log import RunResult
from src.ui.dialogs import ConflictDialog, ProgressDialog


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
