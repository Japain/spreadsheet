from unittest.mock import MagicMock

from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton

from src.config import Config, TabMapping, Workbook
from src.main import MainWindow
from src.ui.history_view import HistoryView
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView
from tests.ui._helpers import _make_confirm_msg_box


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


def _make_fake_progress_dialog():
    class FakeProgressDialog:
        def __init__(self, *a, **kw):
            pass

        def exec(self):
            pass

        def on_workbook_started(self, wb_id):
            pass

        def on_workbook_finished(self, result):
            pass

    return FakeProgressDialog


def test_run_button_disabled_during_run_and_re_enabled_after(qtbot, monkeypatch):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._main_view._run_bar._input_field.setText("/tmp/master.xlsx")
    window._main_view._run_bar._suffix_field.setText("q1")

    button_state_during_start = []

    class FakeProcessor:
        def __init__(self):
            self.workbook_started = MagicMock()
            self.workbook_finished = MagicMock()
            self.run_complete = MagicMock()
            self.run_error = MagicMock()

        def configure(self, *a, **kw):
            pass

        def start(self):
            button_state_during_start.append(window._main_view._run_bar._run_button.isEnabled())

        def wait(self):
            pass

    monkeypatch.setattr("src.main.check_conflicts", lambda *a: [])
    monkeypatch.setattr("src.main.WorkbookProcessor", FakeProcessor)
    monkeypatch.setattr("src.main.ProgressDialog", _make_fake_progress_dialog())

    window._main_view._run_bar._run_button.click()

    assert button_state_during_start == [False], "button must be disabled when processor.start() is called"
    assert window._main_view._run_bar._run_button.isEnabled(), "button must be re-enabled after exec() returns"


def test_previous_processor_is_waited_on_before_new_run(qtbot, monkeypatch):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._main_view._run_bar._input_field.setText("/tmp/master.xlsx")
    window._main_view._run_bar._suffix_field.setText("q1")

    waited = []

    class FakeProcessor:
        def __init__(self):
            self.workbook_started = MagicMock()
            self.workbook_finished = MagicMock()
            self.run_complete = MagicMock()
            self.run_error = MagicMock()

        def configure(self, *a, **kw):
            pass

        def start(self):
            pass

        def wait(self):
            waited.append(True)

    monkeypatch.setattr("src.main.check_conflicts", lambda *a: [])
    monkeypatch.setattr("src.main.WorkbookProcessor", FakeProcessor)
    monkeypatch.setattr("src.main.ProgressDialog", _make_fake_progress_dialog())

    window._processor = FakeProcessor()
    window._main_view._run_bar._run_button.click()

    assert waited, "wait() must be called on the previous processor before starting a new run"


# ── Settings → Run view synchronisation ──────────────────────────────────────

def test_workbook_added_in_settings_appears_in_run_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_configure.click()
    add_btn = window._settings_view.findChild(QPushButton, "add_workbook_btn")
    add_btn.click()
    assert len(window._main_view._workbook_table._rows) == 1


def test_workbook_removed_in_settings_disappears_from_run_view(qtbot):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._nav_configure.click()
    remove_btn = window._settings_view.findChild(QPushButton, "remove_workbook_btn")
    remove_btn.click()
    assert len(window._main_view._workbook_table._rows) == 0


def test_workbook_renamed_in_settings_updates_run_view_row(qtbot):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._nav_configure.click()
    field = window._settings_view.findChild(QLineEdit, "filename_field")
    field.clear()
    qtbot.keyClicks(field, "renamed.xlsx")
    row = window._main_view._workbook_table._rows[0]
    assert row._name_label.text() == "renamed.xlsx"


# ── Reset integration ─────────────────────────────────────────────────────────


def test_reset_in_settings_clears_run_view(qtbot, monkeypatch):
    window = MainWindow(config=_config_with_workbooks())
    qtbot.addWidget(window)
    window._nav_configure.click()
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_confirm_msg_box())
    reset_btn = window._settings_view.findChild(QPushButton, "reset_btn")
    reset_btn.click()
    assert len(window._main_view._workbook_table._rows) == 0
