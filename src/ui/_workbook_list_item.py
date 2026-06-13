from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.config import Workbook


class _WorkbookListItem(QWidget):
    clicked = Signal()

    def __init__(self, workbook: Workbook, parent=None):
        super().__init__(parent)
        self.setObjectName("workbook_list_item")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        # Filename row: small Excel icon + bold name
        fn_row = QHBoxLayout()
        fn_row.setContentsMargins(0, 0, 0, 0)
        fn_row.setSpacing(8)

        _icon = QLabel("X")
        _icon.setStyleSheet(
            "background: #1d6f42; color: #fff; border-radius: 3px;"
            " font-size: 9px; font-weight: 800; padding: 1px 2px;"
            " font-family: 'Segoe UI', Arial, sans-serif;"
        )
        _icon.setFixedSize(18, 18)
        _icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._fn_lbl = QLabel(workbook.filename or "(no filename)")
        self._fn_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")

        fn_row.addWidget(_icon)
        fn_row.addWidget(self._fn_lbl)
        fn_row.addStretch()
        layout.addLayout(fn_row)

        self._folder_lbl = QLabel(workbook.folder)
        self._folder_lbl.setStyleSheet(
            "font-size: 11.5px; color: #6b7080;"
            " font-family: 'Cascadia Mono', Consolas, monospace;"
        )
        layout.addWidget(self._folder_lbl)

        self._chips_container = QWidget()
        self._chips_layout = QHBoxLayout(self._chips_container)
        self._chips_layout.setContentsMargins(0, 2, 0, 0)
        self._chips_layout.setSpacing(4)
        self._rebuild_chips(workbook)
        layout.addWidget(self._chips_container)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def refresh(self, workbook: Workbook) -> None:
        self._fn_lbl.setText(workbook.filename or "(no filename)")
        self._folder_lbl.setText(workbook.folder)
        self._rebuild_chips(workbook)

    def set_selected(self, selected: bool) -> None:
        self.setStyleSheet("background: #e8ecfc;" if selected else "")

    def _rebuild_chips(self, workbook: Workbook) -> None:
        while self._chips_layout.count():
            item = self._chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for m in workbook.mappings:
            chip = QLabel(f"{m.input or '—'} → {m.target or '—'}")
            chip.setStyleSheet(
                "background: rgba(0,0,0,0.05); color: #2a2d35; border-radius: 4px;"
                " font-size: 12px; padding: 2px 7px;"
                " font-family: 'Cascadia Mono', Consolas, monospace;"
            )
            self._chips_layout.addWidget(chip)
        self._chips_layout.addStretch()
