from typing import Literal

from PySide6.QtWidgets import QLabel, QCheckBox


class StatusPill(QLabel):
    _VALID = frozenset({"success", "skipped", "error"})

    def __init__(self, status: Literal["success", "skipped", "error"], parent=None):
        if status not in self._VALID:
            raise ValueError(f"Invalid status: {status!r}")
        super().__init__(status, parent)
        self.setObjectName(f"pill_{status}")


class TabChip(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("tab_chip")


class HeaderCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
