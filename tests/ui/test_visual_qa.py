"""
Visual QA screenshot capture — not a pass/fail test suite.
Run with: pytest tests/ui/test_visual_qa.py -s
Outputs to docs/qa/actual/
"""
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from src.config import Config, TabMapping, Workbook
from src.log import RunRecord, RunResult, append_record
from src.ui.dialogs import ConflictDialog, ProgressDialog
from src.ui.history_view import HistoryView
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView
from src.ui.styles import STYLESHEET

ACTUAL = Path("docs/qa/actual")


@pytest.fixture(autouse=True)
def _stylesheet(qapp):
    prev = qapp.styleSheet()
    qapp.setStyleSheet(STYLESHEET)
    yield
    qapp.setStyleSheet(prev)


def _save(widget, name: str) -> None:
    QApplication.processEvents()
    ACTUAL.mkdir(parents=True, exist_ok=True)
    path = ACTUAL / f"{name}.png"
    if not widget.grab().save(str(path)):
        raise RuntimeError(f"Failed to save screenshot: {path}")
    print(f"\n  → {path}")


# ── Main View ─────────────────────────────────────────────────────────────────

def test_main_view_empty(qtbot):
    config = Config(input_folder="", workbooks=[])
    view = MainView(config)
    qtbot.addWidget(view)
    view.resize(1060, 700)
    view.show()
    _save(view, "main_view_empty")


def test_main_view_populated(qtbot):
    config = Config(
        input_folder="/data/input",
        workbooks=[
            Workbook(
                "wb1", "Q1_Sales.xlsx", "/reports/sales",
                [TabMapping("Sales Data", "Sales Data"), TabMapping("Summary", "Summary")],
            ),
            Workbook(
                "wb2", "Q1_Finance.xlsx", "/reports/finance",
                [TabMapping("P&L", "P&L")],
            ),
            Workbook(
                "wb3", "Q1_HR.xlsx", "/reports/hr",
                [TabMapping("Headcount", "Headcount")],
            ),
        ],
    )
    view = MainView(config)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/data/input/master_Q1.xlsx")
    view._run_bar._suffix_field.setText("Q1_2026")
    view.resize(1060, 700)
    view.show()
    _save(view, "main_view_populated")


# ── Settings View ─────────────────────────────────────────────────────────────

def test_settings_view_empty(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(input_folder="", workbooks=[])
    config.save(config_path)
    view = SettingsView(config, config_path)
    qtbot.addWidget(view)
    view.resize(1060, 700)
    view.show()
    _save(view, "settings_view_empty")


def test_settings_view_populated(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="/data/input",
        workbooks=[
            Workbook(
                "wb1", "Q1_Sales.xlsx", "/reports/sales",
                [TabMapping("Sales Data", "Sales Data"), TabMapping("Summary", "Summary")],
            ),
            Workbook(
                "wb2", "Q1_Finance.xlsx", "/reports/finance",
                [TabMapping("P&L", "P&L")],
            ),
        ],
    )
    config.save(config_path)
    view = SettingsView(config, config_path)
    qtbot.addWidget(view)
    view.resize(1060, 700)
    view.show()
    _save(view, "settings_view_populated")


# ── History View ──────────────────────────────────────────────────────────────

def test_history_view_empty(qtbot, tmp_path):
    view = HistoryView(log_path=tmp_path / "runs.log")
    qtbot.addWidget(view)
    view.resize(1060, 500)
    view.show()
    _save(view, "history_view_empty")


def test_history_view_populated(qtbot, tmp_path):
    log_path = tmp_path / "runs.log"
    records = [
        RunRecord(
            "2026-03-01T11:00:00", "master_Q3.xlsx", "Q3_2025",
            [RunResult("wb1", "Q3_Sales.xlsx", "success", "", "Q3_Sales_Q3_2025.xlsx", 112, 350)],
        ),
        RunRecord(
            "2026-05-15T09:15:00", "master_Q4.xlsx", "Q4_2025",
            [
                RunResult("wb1", "Q4_Sales.xlsx", "success", "", "Q4_Sales_Q4_2025.xlsx", 118, 380),
                RunResult("wb2", "Q4_Finance.xlsx", "error", "File locked by another process", None, 0, 50),
            ],
        ),
        RunRecord(
            "2026-06-12T14:30:00", "master_Q1.xlsx", "Q1_2026",
            [
                RunResult("wb1", "Q1_Sales.xlsx", "success", "", "Q1_Sales_Q1_2026.xlsx", 124, 450),
                RunResult("wb2", "Q1_Finance.xlsx", "success", "", "Q1_Finance_Q1_2026.xlsx", 89, 320),
                RunResult("wb3", "Q1_HR.xlsx", "skipped", "Missing tab: Headcount", "Q1_HR_Q1_2026.xlsx", 0, 200),
            ],
        ),
    ]
    for record in records:
        append_record(log_path, record)
    view = HistoryView(log_path=log_path)
    qtbot.addWidget(view)
    view.resize(1060, 500)
    view.show()
    _save(view, "history_view_populated")


# ── Dialogs ───────────────────────────────────────────────────────────────────

def test_conflict_dialog(qtbot):
    dialog = ConflictDialog([
        "Q1_Sales_Q1_2026.xlsx",
        "Q1_Finance_Q1_2026.xlsx",
        "Q1_HR_Q1_2026.xlsx",
    ])
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.adjustSize()
    _save(dialog, "conflict_dialog")


def test_progress_dialog_mid_run(qtbot):
    workbooks = [
        ("wb1", "Q1_Sales.xlsx"),
        ("wb2", "Q1_Finance.xlsx"),
        ("wb3", "Q1_HR.xlsx"),
        ("wb4", "Q1_Ops.xlsx"),
    ]
    dialog = ProgressDialog(workbooks)
    qtbot.addWidget(dialog)

    dialog.on_workbook_started("wb1")
    dialog.on_workbook_finished(
        RunResult("wb1", "Q1_Sales.xlsx", "success", "", "Q1_Sales_Q1_2026.xlsx", 124, 450)
    )
    dialog.on_workbook_started("wb2")
    dialog.on_workbook_finished(
        RunResult("wb2", "Q1_Finance.xlsx", "error", "File locked by another process", None, 0, 50)
    )
    dialog.on_workbook_started("wb3")
    dialog._timer.stop()  # freeze spinner for screenshot

    dialog.show()
    dialog.adjustSize()
    _save(dialog, "progress_dialog_mid_run")
