import pytest
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QWidget
from src.config import Config, TabMapping, Workbook
from src.ui.settings_view import SettingsView
from tests.ui._helpers import _make_cancel_msg_box, _make_confirm_msg_box


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


def test_input_folder_edit_autosaves(qtbot, view):
    v, config_path = view
    field = v.findChild(QLineEdit, "input_folder_field")
    assert field is not None
    qtbot.keyClicks(field, "/mydir")
    loaded = Config.load(config_path)
    assert loaded.input_folder == "/mydir"


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


# ── Signals ───────────────────────────────────────────────────────────────────

def test_add_workbook_emits_workbook_added_signal(qtbot, view):
    v, _ = view
    added = []
    v.workbook_added.connect(added.append)
    add_wb_btn = v.findChild(QPushButton, "add_workbook_btn")
    add_wb_btn.click()
    assert len(added) == 1
    assert added[0].id  # new workbook has a uuid


def test_remove_workbook_emits_workbook_removed_signal(qtbot, view):
    v, _ = view
    removed_ids = []
    v.workbook_removed.connect(removed_ids.append)
    remove_wb_btn = v.findChild(QPushButton, "remove_workbook_btn")
    remove_wb_btn.click()
    assert removed_ids == ["wb1"]


def test_editing_workbook_field_emits_workbook_updated_signal(qtbot, view):
    v, _ = view
    updated = []
    v.workbook_updated.connect(updated.append)
    field = v.findChild(QLineEdit, "filename_field")
    qtbot.keyClicks(field, "_v2")
    assert len(updated) >= 1
    assert updated[-1].filename == "Report.xlsx_v2"


@pytest.fixture
def two_wb_view(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="/some/path",
        workbooks=[
            Workbook(id="wb1", filename="A.xlsx", folder="/t", mappings=[TabMapping(input="D", target="D")]),
            Workbook(id="wb2", filename="B.xlsx", folder="/t", mappings=[TabMapping(input="D", target="D")]),
        ],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)
    v.show()
    return v, config_path


def test_reset_emits_workbook_removed_for_each_workbook(qtbot, monkeypatch, two_wb_view):
    v, _ = two_wb_view
    removed_ids = []
    v.workbook_removed.connect(removed_ids.append)
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_confirm_msg_box())
    v.findChild(QPushButton, "reset_btn").click()
    assert sorted(removed_ids) == ["wb1", "wb2"]


def test_reset_clears_config_workbooks(qtbot, monkeypatch, two_wb_view):
    v, config_path = two_wb_view
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_confirm_msg_box())
    v.findChild(QPushButton, "reset_btn").click()
    assert Config.load(config_path).workbooks == []


def test_reset_clears_config_input_folder(qtbot, monkeypatch, two_wb_view):
    v, config_path = two_wb_view
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_confirm_msg_box())
    v.findChild(QPushButton, "reset_btn").click()
    assert Config.load(config_path).input_folder == ""


def test_reset_cancel_leaves_config_unchanged(qtbot, monkeypatch, two_wb_view):
    v, config_path = two_wb_view
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_cancel_msg_box())
    v.findChild(QPushButton, "reset_btn").click()
    loaded = Config.load(config_path)
    assert len(loaded.workbooks) == 2
    assert loaded.input_folder == "/some/path"


def test_reset_clears_list_and_shows_empty_label(qtbot, monkeypatch, two_wb_view):
    v, _ = two_wb_view
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_confirm_msg_box())
    v.findChild(QPushButton, "reset_btn").click()
    assert len(v.findChildren(QWidget, "workbook_list_item")) == 0
    assert v._empty_lbl.isVisible()


def test_reset_clears_input_folder_field_widget(qtbot, monkeypatch, two_wb_view):
    v, _ = two_wb_view
    monkeypatch.setattr("src.ui.settings_view.QMessageBox", _make_confirm_msg_box())
    v.findChild(QPushButton, "reset_btn").click()
    field = v.findChild(QLineEdit, "input_folder_field")
    assert field.text() == ""


def test_completer_populated_from_folder(qtbot, tmp_path):
    folder = tmp_path / "target"
    folder.mkdir()
    (folder / "Report.xlsx").touch()
    (folder / "Budget.xlsx").touch()
    (folder / "notes.txt").touch()  # must not appear

    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder=str(folder), mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)

    field = v.findChild(QLineEdit, "filename_field")
    completer = field.completer()
    assert completer is not None
    model = completer.model()
    names = sorted(model.data(model.index(i, 0)) for i in range(model.rowCount()))
    assert names == ["Budget.xlsx", "Report.xlsx"]


def test_completer_empty_when_folder_invalid(qtbot, tmp_path):
    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder="/nonexistent/path/xyz", mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)

    field = v.findChild(QLineEdit, "filename_field")
    assert field.completer().model().rowCount() == 0


def test_completer_refreshes_on_folder_change(qtbot, tmp_path):
    folder1 = tmp_path / "folder1"
    folder1.mkdir()
    (folder1 / "Alpha.xlsx").touch()
    folder2 = tmp_path / "folder2"
    folder2.mkdir()
    (folder2 / "Beta.xlsx").touch()

    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder=str(folder1), mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)

    folder_field = v.findChild(QLineEdit, "folder_field")
    folder_field.setText(str(folder2))

    field = v.findChild(QLineEdit, "filename_field")
    model = field.completer().model()
    names = [model.data(model.index(i, 0)) for i in range(model.rowCount())]
    assert "Beta.xlsx" in names
    assert "Alpha.xlsx" not in names


def test_completer_refreshes_on_filename_field_focus(qtbot, tmp_path):
    folder = tmp_path / "target"
    folder.mkdir()

    config_path = tmp_path / "config.json"
    config = Config(
        input_folder="",
        workbooks=[Workbook(id="wb1", filename="", folder=str(folder), mappings=[TabMapping("", "")])],
    )
    config.save(config_path)
    v = SettingsView(config, config_path)
    qtbot.addWidget(v)
    v.show()
    qtbot.waitExposed(v)

    # Add a file after the view was created (completer initially empty)
    (folder / "LateArrival.xlsx").touch()

    field = v.findChild(QLineEdit, "filename_field")
    # Send a synthetic FocusIn event to trigger the event filter
    from PySide6.QtGui import QFocusEvent
    from PySide6.QtCore import QEvent, Qt
    event = QFocusEvent(QEvent.Type.FocusIn)
    QApplication.instance().sendEvent(field, event)
    QApplication.processEvents()

    model = field.completer().model()
    names = [model.data(model.index(i, 0)) for i in range(model.rowCount())]
    assert "LateArrival.xlsx" in names
