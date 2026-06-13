from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton

from src.log import RunResult
from src.ui.dialogs import ConflictDialog, ProgressDialog, SPINNER_FRAMES


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
    assert dialog._progress_bar.value() == 0

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
    assert dialog._progress_bar.value() == 1


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


def test_progress_dialog_closes_on_run_complete(qtbot):
    dialog = ProgressDialog([("wb-1", "report.xlsx")])
    qtbot.addWidget(dialog)
    dialog.on_run_complete()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_progress_dialog_timer_animations(qtbot):
    dialog = ProgressDialog([("wb-1", "report.xlsx")])
    qtbot.addWidget(dialog)

    assert not dialog._timer.isActive()

    dialog.on_workbook_started("wb-1")
    assert dialog._timer.isActive()
    row = dialog._rows["wb-1"]
    assert row._indicator.text() == SPINNER_FRAMES[0]

    dialog._tick()
    assert row._indicator.text() == SPINNER_FRAMES[1]

    dialog.on_workbook_finished(
        RunResult("wb-1", "report.xlsx", "success", "", "out.xlsx", 5, 10)
    )
    assert not dialog._timer.isActive()


def test_progress_dialog_non_dismissible_during_run(qtbot):
    dialog = ProgressDialog([("wb-1", "report.xlsx")])
    qtbot.addWidget(dialog)
    dialog.show()

    # Try to close programmatically
    assert not dialog.close()
    assert dialog.isVisible()

    # Try to close with Escape key
    qtbot.keyClick(dialog, Qt.Key.Key_Escape)
    assert dialog.isVisible()
