import pytest
from src.config import Config
from src.main import MainWindow
from src.ui.settings_view import SettingsView
from src.ui.history_view import HistoryView


def _config() -> Config:
    return Config(input_folder="", workbooks=[])


def test_configure_nav_switches_to_settings_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_configure.click()
    assert window._stack.currentIndex() == 1
    assert isinstance(window._stack.currentWidget(), SettingsView)


def test_history_nav_switches_to_history_view(qtbot):
    window = MainWindow(config=_config())
    qtbot.addWidget(window)
    window._nav_history.click()
    assert window._stack.currentIndex() == 2
    assert isinstance(window._stack.currentWidget(), HistoryView)
