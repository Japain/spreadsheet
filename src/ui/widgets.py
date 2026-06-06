from typing import Literal

from PySide6.QtWidgets import QLabel, QCheckBox


class StatusPill(QLabel):
    _VALID = frozenset({"success", "skipped", "error"})

    def __init__(self, status: Literal["success", "skipped", "error"], parent=None):
        super().__init__(status, parent)
        if status not in self._VALID:
            raise ValueError(f"Invalid status: {status!r}")
        self.setObjectName(f"pill_{status}")


class TabChip(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "background-color: #ebebeb; color: #1b1d22;"
            " border-radius: 4px; padding: 1px 6px;"
            " font-size: 11px;"
        )


class HeaderCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
