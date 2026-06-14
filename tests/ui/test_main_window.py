from unittest.mock import MagicMock

from PySide6.QtWidgets import QDialog

from src.config import Config, TabMapping, Workbook
from src.main import MainWindow
from src.ui.history_view import HistoryView
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView


def _config() -> Config:
    return Config(input_folder="", workbooks=[])


def _config_with_workbooks() -> Config:
    wb = Workbook(
        id="wb1",
        filename="sales.xlsx",
        folder="/tmp",
        mappings=[TabMapping(input="Sheet1", target="Sheet1")],
    )
    return Config(input_folder="/tmp", workbooks=[wb])


def test_initial_state_is_main_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    assert window._stack.currentIndex() == 0
    assert isinstance(window._stack.currentWidget(), MainView)
    assert window._nav_run.property("active") is True
    assert window._nav_configure.property("active") is False
    assert window._nav_history.property("active") is False


def test_configure_nav_switches_to_settings_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_configure.click()
    assert window._stack.currentIndex() == 1
    assert isinstance(window._stack.currentWidget(), SettingsView)
    assert window._nav_configure.property("active") is True
    assert window._nav_run.property("active") is False
    assert window._nav_history.property("active") is False


def test_history_nav_switches_to_history_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_history.click()
    assert window._stack.currentIndex() == 2
    assert isinstance(window._stack.currentWidget(), HistoryView)
    assert window._nav_history.property("active") is True
    assert window._nav_run.property("active") is False
    assert window._nav_configure.property("active") is False


def test_empty_state_add_workbook_navigates_to_settings(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._main_view._empty_state._add_btn.click()
    assert window._stack.currentIndex() == 1


def test_run_with_conflicts_shows_conflict_dialog(qtbot, monkeypatch):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._main_view._run_bar._input_field.setText("/tmp/master.xlsx")
    window._main_view._run_bar._suffix_field.setText("q1")

    conflicts_received = []

    class FakeConflictDialog:
        def __init__(self, filenames, parent=None):
            conflicts_received.append(filenames)

        def exec(self):
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr("src.main.check_conflicts", lambda *a: ["sales_q1.xlsx"])
    monkeypatch.setattr("src.main.ConflictDialog", FakeConflictDialog)

    window._main_view._run_bar._run_button.click()

    assert conflicts_received == [["sales_q1.xlsx"]]


def test_run_with_no_conflicts_starts_processor(qtbot, monkeypatch):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._main_view._run_bar._input_field.setText("/tmp/master.xlsx")
    window._main_view._run_bar._suffix_field.setText("q1")

    processor_started = []

    class FakeProcessor:
        def __init__(self):
            self.workbook_started = MagicMock()
            self.workbook_finished = MagicMock()
            self.run_complete = MagicMock()
            self.run_error = MagicMock()

        def configure(self, *a, **kw):
            pass

        def start(self):
            processor_started.append(True)

    class FakeProgressDialog:
        def __init__(self, *a, **kw):
            pass

        def exec(self):
            pass

        def on_workbook_started(self, wb_id):
            pass

        def on_workbook_finished(self, result):
            pass

    monkeypatch.setattr("src.main.check_conflicts", lambda *a: [])
    monkeypatch.setattr("src.main.WorkbookProcessor", FakeProcessor)
    monkeypatch.setattr("src.main.ProgressDialog", FakeProgressDialog)

    window._main_view._run_bar._run_button.click()

    assert processor_started
