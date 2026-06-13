from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.config import DEFAULT_LOG_PATH
from src.log import RunRecord, read_records


class _HistoryRow(QWidget):
    def __init__(self, record: RunRecord, parent: QWidget | None = None):
        super().__init__(parent)

        ok = sum(1 for r in record.results if r.status == "success")
        skipped = sum(1 for r in record.results if r.status == "skipped")
        error = sum(1 for r in record.results if r.status == "error")

        ts_label = QLabel(record.timestamp)
        ts_label.setObjectName("history_row_timestamp")
        ts_label.setProperty("monospace", True)

        suffix_label = QLabel(f"_{record.suffix}.xlsx")
        filename_label = QLabel(record.input_filename)
        filename_label.setSizePolicy(
            filename_label.sizePolicy().horizontalPolicy(),
            filename_label.sizePolicy().verticalPolicy(),
        )

        ok_pill = QLabel(f"{ok} ok")
        ok_pill.setObjectName("pill_success")
        skip_pill = QLabel(f"{skipped} skipped")
        skip_pill.setObjectName("pill_skipped")
        err_pill = QLabel(f"{error} error")
        err_pill.setObjectName("pill_error")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)
        layout.addWidget(ts_label)
        layout.addWidget(suffix_label)
        layout.addWidget(filename_label, 1)
        layout.addWidget(ok_pill)
        layout.addWidget(skip_pill)
        layout.addWidget(err_pill)


class HistoryView(QWidget):
    def __init__(self, log_path: Path = DEFAULT_LOG_PATH, parent: QWidget | None = None):
        super().__init__(parent)
        self._log_path = Path(log_path)

        self._empty_label = QLabel("No run history yet")
        self._empty_label.setObjectName("empty_state_label")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #9aa0ad; font-size: 13px;")

        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(2)
        self._rows_layout.addStretch()

        self._scroll = QScrollArea()
        self._scroll.setWidget(self._rows_widget)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(self._empty_label, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._scroll, 1)

        self._empty_label.setVisible(True)
        self._scroll.setVisible(False)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._reload()

    def _reload(self) -> None:
        records = read_records(self._log_path)

        # Clear existing rows (everything before the trailing stretch)
        while self._rows_layout.count() > 1:
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if not records:
            self._empty_label.setVisible(True)
            self._scroll.setVisible(False)
            return

        self._empty_label.setVisible(False)
        self._scroll.setVisible(True)
        for record in records:
            row = _HistoryRow(record)
            self._rows_layout.insertWidget(self._rows_layout.count() - 1, row)
