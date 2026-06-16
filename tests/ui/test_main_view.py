import pytest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QFileDialog

from src.config import Config, Workbook, TabMapping
from src.log import RunResult
from src.ui.main_view import MainView


@pytest.fixture
def two_workbooks():
    return Config(
        input_folder="/some/input",
        workbooks=[
            Workbook(
                id="wb1",
                filename="Report1.xlsx",
                folder="/target/folder1",
                mappings=[TabMapping(input="Data", target="Data")],
            ),
            Workbook(
                id="wb2",
                filename="Report2.xlsx",
                folder="/target/folder2",
                mappings=[TabMapping(input="Summary", target="Summary")],
            ),
        ],
    )


@pytest.fixture
def empty_config():
    return Config(input_folder="", workbooks=[])


# ── RunBar ────────────────────────────────────────────────────────────────────

def test_run_button_disabled_when_no_input_file(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._suffix_field.setText("Q1")
    assert not view._run_bar._run_button.isEnabled()


def test_run_button_disabled_when_suffix_empty(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/some/master.xlsx")
    view._run_bar._suffix_field.setText("")
    assert not view._run_bar._run_button.isEnabled()


def test_run_button_disabled_when_suffix_has_illegal_chars(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/some/master.xlsx")
    for ch in r'\/:*?"<>|':
        view._run_bar._suffix_field.setText(f"bad{ch}name")
        assert not view._run_bar._run_button.isEnabled(), (
            f"Run button should stay disabled for illegal char {ch!r}"
        )


def test_run_button_disabled_when_suffix_has_space(qtbot, two_workbooks):
    # Space passes the old blocklist but is rejected by the processor's allowlist
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/some/master.xlsx")
    view._run_bar._suffix_field.setText("my suffix")
    assert not view._run_bar._run_button.isEnabled()


def test_run_button_disabled_when_no_rows_checked(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/some/master.xlsx")
    view._run_bar._suffix_field.setText("Q1")
    for row in view._workbook_table._rows:
        row._checkbox.setChecked(False)
    assert not view._run_bar._run_button.isEnabled()


def test_run_button_enabled_when_all_conditions_met(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/some/master.xlsx")
    view._run_bar._suffix_field.setText("Q1")
    view._workbook_table._rows[0]._checkbox.setChecked(True)
    assert view._run_bar._run_button.isEnabled()


def test_browse_button_populates_input_field(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    with patch.object(QFileDialog, "getOpenFileName", return_value=("/picked/master.xlsx", "")):
        view._run_bar._browse_input_btn.click()
    assert view._run_bar._input_field.text() == "/picked/master.xlsx"


def test_browse_button_ignores_cancelled_dialog(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._run_bar._input_field.setText("/existing/path.xlsx")
    with patch.object(QFileDialog, "getOpenFileName", return_value=("", "")):
        view._run_bar._browse_input_btn.click()
    assert view._run_bar._input_field.text() == "/existing/path.xlsx"


# ── WorkbookTable ─────────────────────────────────────────────────────────────

def test_get_selected_ids_returns_only_checked(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._workbook_table._rows[0]._checkbox.setChecked(True)
    view._workbook_table._rows[1]._checkbox.setChecked(False)
    assert view._workbook_table.get_selected_ids() == ["wb1"]


def test_set_all_checked_checks_all_rows(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    for row in view._workbook_table._rows:
        row._checkbox.setChecked(False)
    view._workbook_table.set_all_checked(True)
    assert all(row._checkbox.isChecked() for row in view._workbook_table._rows)


def test_set_all_checked_unchecks_all_rows(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    for row in view._workbook_table._rows:
        row._checkbox.setChecked(True)
    view._workbook_table.set_all_checked(False)
    assert not any(row._checkbox.isChecked() for row in view._workbook_table._rows)


def test_set_all_checked_syncs_row_opacity(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view._workbook_table.set_all_checked(False)
    for row in view._workbook_table._rows:
        assert row._opacity.opacity() == pytest.approx(0.4)
    view._workbook_table.set_all_checked(True)
    for row in view._workbook_table._rows:
        assert row._opacity.opacity() == pytest.approx(1.0)


# ── LogPanel ──────────────────────────────────────────────────────────────────

def test_log_panel_hidden_on_init(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    assert view._log_panel.isHidden()


def test_log_panel_visible_after_show_results(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    results = [
        RunResult(
            workbook_id="wb1",
            filename="Report1.xlsx",
            status="success",
            message="OK",
            output_filename="Report1_Q1.xlsx",
            rows_written=10,
            duration_ms=200,
        )
    ]
    view.show_results(results, suffix="Q1")
    assert not view._log_panel.isHidden()


def test_log_panel_summary_counts_match_results(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    results = [
        RunResult("wb1", "Report1.xlsx", "success", "OK", "Report1_Q1.xlsx", 10, 200),
        RunResult("wb2", "Report2.xlsx", "skipped", "Missing tab", "Report2_Q1.xlsx", 0, 150),
        RunResult("wb3", "Report3.xlsx", "error", "File not found", None, 0, 50),
    ]
    view.show_results(results, suffix="Q1")
    assert view._log_panel._success_count == 1
    assert view._log_panel._skipped_count == 1
    assert view._log_panel._error_count == 1


def test_log_panel_header_contains_suffix(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    results = [RunResult("wb1", "Report1.xlsx", "success", "OK", "Report1_Q1.xlsx", 10, 200)]
    view.show_results(results, suffix="Q1")
    assert "Q1" in view._log_panel._header_label.text()


def test_copy_log_copies_text_to_clipboard(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    results = [
        RunResult("wb1", "Report1.xlsx", "success", "OK", "Report1_Q1.xlsx", 10, 200),
        RunResult("wb2", "Report2.xlsx", "error", "File not found", None, 0, 50),
    ]
    view.show_results(results, suffix="Q1")
    view._log_panel._copy_btn.click()
    text = QApplication.clipboard().text()
    assert "Q1" in text
    assert "Report1.xlsx" in text


# ── Empty State ───────────────────────────────────────────────────────────────

def test_empty_state_shown_and_run_bar_hidden_when_no_workbooks(qtbot, empty_config):
    view = MainView(empty_config)
    qtbot.addWidget(view)
    assert not view._empty_state.isHidden()
    assert view._run_bar.isHidden()


def test_empty_state_has_card_object_name(qtbot, empty_config):
    view = MainView(empty_config)
    qtbot.addWidget(view)
    assert view._empty_state.objectName() == "card"


# ── Dynamic workbook add / remove ─────────────────────────────────────────────

def test_add_workbook_appends_row_to_table(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    new_wb = Workbook(id="wb3", filename="New.xlsx", folder="/new", mappings=[TabMapping("Sheet1", "Sheet1")])
    view.add_workbook(new_wb)
    assert len(view._workbook_table._rows) == 3


def test_add_workbook_row_has_correct_id(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    new_wb = Workbook(id="wb3", filename="New.xlsx", folder="/new", mappings=[TabMapping("Sheet1", "Sheet1")])
    view.add_workbook(new_wb)
    assert view._workbook_table._rows[-1].workbook_id == "wb3"


def test_remove_workbook_removes_correct_row(qtbot, two_workbooks):
    view = MainView(two_workbooks)
    qtbot.addWidget(view)
    view.remove_workbook("wb1")
    assert len(view._workbook_table._rows) == 1
    assert view._workbook_table._rows[0].workbook_id == "wb2"


def test_add_workbook_to_empty_view_shows_run_bar(qtbot, empty_config):
    view = MainView(empty_config)
    qtbot.addWidget(view)
    assert view._run_bar.isHidden()
    new_wb = Workbook(id="wb1", filename="New.xlsx", folder="/new", mappings=[TabMapping("Sheet1", "Sheet1")])
    view.add_workbook(new_wb)
    assert not view._run_bar.isHidden()
    assert view._empty_state.isHidden()


def test_remove_last_workbook_shows_empty_state(qtbot):
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="R.xlsx", folder="/t", mappings=[TabMapping("A", "A")])],
    )
    view = MainView(config)
    qtbot.addWidget(view)
    view.remove_workbook("wb1")
    assert not view._empty_state.isHidden()
    assert view._run_bar.isHidden()
