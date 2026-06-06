from typing import Literal

from PySide6.QtWidgets import QLabel, QCheckBox


class StatusPill(QLabel):
    _STYLES: dict[str, tuple[str, str]] = {
        "success": ("#dff2e4", "#2a7a48"),
        "skipped": ("#fdf3d0", "#7a5c00"),
        "error":   ("#fde8e4", "#8c2a1c"),
    }

    def __init__(self, status: Literal["success", "skipped", "error"], parent=None):
        super().__init__(status, parent)
        bg, fg = self._STYLES[status]
        self.setStyleSheet(
            f"background-color: {bg}; color: {fg};"
            " border-radius: 10px; padding: 2px 8px;"
        )


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
