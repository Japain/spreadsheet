from src.ui.widgets import StatusPill, TabChip, HeaderCheckBox
import pytest


def test_status_pill_success_object_name(qtbot):
    pill = StatusPill("success")
    qtbot.addWidget(pill)
    assert pill.objectName() == "pill_success"


def test_status_pill_error_object_name(qtbot):
    pill = StatusPill("error")
    qtbot.addWidget(pill)
    assert pill.objectName() == "pill_error"


def test_status_pill_skipped_object_name(qtbot):
    pill = StatusPill("skipped")
    qtbot.addWidget(pill)
    assert pill.objectName() == "pill_skipped"


def test_status_pill_invalid_status_raises_value_error(qtbot):
    with pytest.raises(ValueError, match="Invalid status"):
        StatusPill("unknown")


def test_tab_chip_is_creatable(qtbot):
    chip = TabChip("Sheet1")
    qtbot.addWidget(chip)
    assert chip.text() == "Sheet1"


def test_header_checkbox_is_creatable(qtbot):
    cb = HeaderCheckBox()
    qtbot.addWidget(cb)
    assert not cb.isChecked()
