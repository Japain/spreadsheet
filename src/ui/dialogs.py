from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.log import RunResult

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ConflictDialog(QDialog):
    def __init__(self, filenames: list[str], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Overwrite existing files?")
        self.setFixedWidth(480)

        heading = QLabel("These output files already exist")
        heading.setStyleSheet("font-weight: bold;")

        sub = QLabel("Running will overwrite them:")
        sub.setObjectName("secondary")

        file_list = QWidget()
        file_layout = QVBoxLayout(file_list)
        file_layout.setContentsMargins(16, 0, 0, 0)
        file_layout.setSpacing(2)
        for name in filenames:
            lbl = QLabel(name)
            lbl.setObjectName("monospace")
            file_layout.addWidget(lbl)

        # && renders as a literal & in Qt button labels
        cancel_btn = QPushButton("Cancel && change suffix")
        cancel_btn.clicked.connect(self.reject)

        overwrite_btn = QPushButton("Overwrite and continue")
        overwrite_btn.setObjectName("primary")
        overwrite_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(overwrite_btn)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(heading)
        layout.addWidget(sub)
        layout.addWidget(file_list)
        layout.addLayout(btn_row)


class _ProgressRow(QWidget):
    def __init__(self, filename: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._indicator = QLabel("○")
        self._indicator.setFixedWidth(20)
        self._name = QLabel(filename)
        self._status = QLabel("Waiting")
        self._status.setObjectName("secondary")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(self._indicator)
        layout.addWidget(self._name, 1)
        layout.addWidget(self._status)

    def set_running(self, frame: str) -> None:
        self._indicator.setText(frame)
        self._status.setText("Processing…")

    def set_done(self, result: RunResult) -> None:
        if result.status == "success":
            self._indicator.setText("✓")
            self._status.setText(f"{result.rows_written} rows")
        else:
            self._indicator.setText("✗")
            self._status.setText(result.message)


class ProgressDialog(QDialog):
    def __init__(self, workbooks: list[tuple[str, str]], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Running…")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self._rows: dict[str, _ProgressRow] = {}
        self._frame_index = 0
        self._current_row: _ProgressRow | None = None

        title = QLabel("Running…")
        title.setStyleSheet("font-weight: bold;")

        rows_widget = QWidget()
        rows_layout = QVBoxLayout(rows_widget)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(0)
        for wb_id, filename in workbooks:
            row = _ProgressRow(filename)
            self._rows[wb_id] = row
            rows_layout.addWidget(row)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, len(workbooks))
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._tick)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(rows_widget)
        layout.addWidget(self._progress_bar)

    def _tick(self) -> None:
        if self._current_row is None:
            return
        self._frame_index = (self._frame_index + 1) % len(SPINNER_FRAMES)
        self._current_row.set_running(SPINNER_FRAMES[self._frame_index])

    def on_workbook_started(self, wb_id: str) -> None:
        row = self._rows.get(wb_id)
        if row is None:
            return
        self._current_row = row
        row.set_running(SPINNER_FRAMES[0])
        self._timer.start()

    def on_workbook_finished(self, result: RunResult) -> None:
        row = self._rows.get(result.workbook_id)
        if row is None:
            return
        self._timer.stop()
        self._current_row = None
        row.set_done(result)
        self._progress_bar.setValue(self._progress_bar.value() + 1)

    def on_run_complete(self) -> None:
        self.accept()

    def closeEvent(self, event) -> None:
        event.ignore()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
