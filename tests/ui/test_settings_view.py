import pytest
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

from src.config import Config, TabMapping, Workbook
from src.ui.settings_view import SettingsView


@pytest.fixture
def view(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[
            Workbook(
                id="wb1",
                filename="Report.xlsx",
                folder="/target",
                mappings=[TabMapping(input="Data", target="Data")],
            )
        ],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)
    return v, config_path


def test_filename_edit_autosaves(qtbot, view):
    v, config_path = view
    field = v.findChild(QLineEdit, "filename_field")
    qtbot.keyClicks(field, "_updated")
    loaded = Config.load(config_path)
    assert loaded.workbooks[0].filename == "Report.xlsx_updated"


def test_add_mapping_disabled_at_two(qtbot, view):
    v, config_path = view
    add_btn = v.findChild(QPushButton, "add_mapping_btn")
    assert add_btn.isEnabled()
    add_btn.click()
    assert not add_btn.isEnabled()
    loaded = Config.load(config_path)
    assert len(loaded.workbooks[0].mappings) == 2


def test_remove_mapping_disabled_at_one(qtbot, view):
    v, config_path = view
    remove_btns = v.findChildren(QPushButton, "remove_mapping_btn")
    assert len(remove_btns) == 1
    assert not remove_btns[0].isEnabled()


def test_new_workbook_has_one_mapping(qtbot, view):
    v, config_path = view
    add_wb_btn = v.findChild(QPushButton, "add_workbook_btn")
    add_wb_btn.click()
    remove_btns = v.findChildren(QPushButton, "remove_mapping_btn")
    assert len(remove_btns) == 1
    assert not remove_btns[0].isEnabled()
    loaded = Config.load(config_path)
    assert len(loaded.workbooks[-1].mappings) == 1


def test_remove_workbook(qtbot, view):
    v, config_path = view
    remove_wb_btn = v.findChild(QPushButton, "remove_workbook_btn")
    remove_wb_btn.click()
    loaded = Config.load(config_path)
    assert len(loaded.workbooks) == 0
    list_items = v.findChildren(QWidget, "workbook_list_item")
    assert len(list_items) == 0


def test_add_workbook_shows_and_selects(qtbot, view):
    v, config_path = view
    add_wb_btn = v.findChild(QPushButton, "add_workbook_btn")
    add_wb_btn.click()
    # Left list gained a new item
    list_items = v.findChildren(QWidget, "workbook_list_item")
    assert len(list_items) == 2
    # Right pane is populated (placeholder hidden)
    placeholder = v.findChild(QLabel, "detail_placeholder")
    assert placeholder.isHidden()
    filename_field = v.findChild(QLineEdit, "filename_field")
    assert not filename_field.isHidden()
    # Config was saved to disk
    loaded = Config.load(config_path)
    assert len(loaded.workbooks) == 2
