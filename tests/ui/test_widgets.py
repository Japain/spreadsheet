import pytest
from src.ui.widgets import StatusPill, TabChip, HeaderCheckBox


def test_status_pill_success_contains_success_bg(qtbot):
    pill = StatusPill("success")
    qtbot.addWidget(pill)
    assert "#dff2e4" in pill.styleSheet()


def test_status_pill_error_contains_error_bg(qtbot):
    pill = StatusPill("error")
    qtbot.addWidget(pill)
    assert "#fde8e4" in pill.styleSheet()


def test_status_pill_skipped_contains_warning_bg(qtbot):
    pill = StatusPill("skipped")
    qtbot.addWidget(pill)
    assert "#fdf3d0" in pill.styleSheet()


def test_tab_chip_is_creatable(qtbot):
    chip = TabChip("Sheet1")
    qtbot.addWidget(chip)
    assert chip.text() == "Sheet1"


def test_header_checkbox_is_creatable(qtbot):
    cb = HeaderCheckBox()
    qtbot.addWidget(cb)
    assert not cb.isChecked()
