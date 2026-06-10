from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.config import Config, Workbook
from src.log import RunResult
from src.ui.widgets import HeaderCheckBox, TabChip

# Mirrors processor._SUFFIX_RE — must stay in sync
_SUFFIX_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


class WorkbookRow(QWidget):
    def __init__(self, workbook: Workbook, parent: QWidget | None = None):
        super().__init__(parent)
        self.workbook_id = workbook.id

        self._checkbox = QCheckBox()
        self._checkbox.setChecked(True)

        name_label = QLabel(workbook.filename)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(4)
        for m in workbook.mappings:
            input_layout.addWidget(TabChip(m.input))
        input_layout.addStretch()

        target_widget = QWidget()
        target_layout = QHBoxLayout(target_widget)
        target_layout.setContentsMargins(0, 0, 0, 0)
        target_layout.setSpacing(4)
        for m in workbook.mappings:
            target_layout.addWidget(TabChip(m.target))
        target_layout.addStretch()

        folder_label = QLabel(workbook.folder)
        folder_label.setObjectName("monospace")

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.addWidget(self._checkbox)
        row_layout.addWidget(name_label, 2)
        row_layout.addWidget(input_widget, 1)
        row_layout.addWidget(target_widget, 1)
        row_layout.addWidget(folder_label, 2)

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._checkbox.stateChanged.connect(self._update_opacity)
        self._update_opacity()

    def _update_opacity(self) -> None:
        self._opacity.setOpacity(1.0 if self._checkbox.isChecked() else 0.4)


class WorkbookTable(QWidget):
    selection_changed = Signal()

    def __init__(self, workbooks: list[Workbook], parent: QWidget | None = None):
        super().__init__(parent)

        self._header_checkbox = HeaderCheckBox()
        self._header_checkbox.setChecked(True)
        self._rows: list[WorkbookRow] = []

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.addWidget(self._header_checkbox)
        for label in ("Workbook", "Input Tab(s)", "Target Tab(s)", "Folder"):
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            header_layout.addWidget(lbl)

        rows_widget = QWidget()
        rows_layout = QVBoxLayout(rows_widget)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(2)
        for wb in workbooks:
            row = WorkbookRow(wb)
            row._checkbox.stateChanged.connect(lambda _: self.selection_changed.emit())
            self._rows.append(row)
            rows_layout.addWidget(row)
        rows_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(rows_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(header_layout)
        layout.addWidget(scroll, 1)

        # clicked(bool) fires on every user interaction; set_all_checked is the
        # public API for programmatic bulk-toggle (used by tests and future code).
        self._header_checkbox.clicked.connect(self.set_all_checked)

    def set_all_checked(self, checked: bool) -> None:
        self._header_checkbox.setChecked(checked)
        for row in self._rows:
            row._checkbox.blockSignals(True)
            row._checkbox.setChecked(checked)
            row._checkbox.blockSignals(False)
        self.selection_changed.emit()

    def get_selected_ids(self) -> list[str]:
        return [row.workbook_id for row in self._rows if row._checkbox.isChecked()]


class RunBar(QWidget):
    def __init__(self, config: Config, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("card")
        self._input_folder = config.input_folder

        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("Select master workbook…")
        self._browse_input_btn = QPushButton("Browse…")
        self._browse_input_btn.clicked.connect(self._browse_for_file)

        prefix_label = QLabel("_")
        prefix_label.setObjectName("secondary")
        self._suffix_field = QLineEdit()
        self._suffix_field.setPlaceholderText("suffix")
        suffix_label = QLabel(".xlsx")
        suffix_label.setObjectName("secondary")

        self._suffix_error = QLabel("Use only letters, numbers, - and _")
        self._suffix_error.setStyleSheet("color: #8c2a1c; font-size: 11px;")
        self._suffix_error.setVisible(False)

        self._run_button = QPushButton("Run")
        self._run_button.setObjectName("primary")
        self._run_button.setEnabled(False)

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Input file"))
        input_row.addWidget(self._input_field, 1)
        input_row.addWidget(self._browse_input_btn)

        suffix_row = QHBoxLayout()
        suffix_row.addWidget(QLabel("Suffix"))
        suffix_row.addWidget(prefix_label)
        suffix_row.addWidget(self._suffix_field, 1)
        suffix_row.addWidget(suffix_label)
        suffix_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(input_row)
        layout.addLayout(suffix_row)
        layout.addWidget(self._suffix_error)
        layout.addWidget(self._run_button, 0, Qt.AlignmentFlag.AlignRight)

    def _browse_for_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select master workbook", self._input_folder, "Excel Files (*.xlsx)"
        )
        if filename:
            self._input_field.setText(filename)


class LogPanel(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("card")

        self._success_count = 0
        self._skipped_count = 0
        self._error_count = 0
        self._plain_text = ""

        self._header_label = QLabel("Run complete")
        self._ok_pill = QLabel("0 ok")
        self._ok_pill.setObjectName("pill_success")
        self._skip_pill = QLabel("0 skipped")
        self._skip_pill.setObjectName("pill_skipped")
        self._err_pill = QLabel("0 error")
        self._err_pill.setObjectName("pill_error")

        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)

        self._copy_btn = QPushButton("Copy log")
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.clicked.connect(self.hide)

        pills_row = QHBoxLayout()
        pills_row.addWidget(self._header_label)
        pills_row.addStretch()
        pills_row.addWidget(self._ok_pill)
        pills_row.addWidget(self._skip_pill)
        pills_row.addWidget(self._err_pill)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._copy_btn)
        btn_row.addWidget(dismiss_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(pills_row)
        layout.addWidget(self._rows_widget)
        layout.addLayout(btn_row)

    def show_results(self, results: list[RunResult], suffix: str) -> None:
        self._success_count = sum(1 for r in results if r.status == "success")
        self._skipped_count = sum(1 for r in results if r.status == "skipped")
        self._error_count = sum(1 for r in results if r.status == "error")

        self._header_label.setText(f"Run complete — _{suffix}.xlsx")
        self._ok_pill.setText(f"{self._success_count} ok")
        self._skip_pill.setText(f"{self._skipped_count} skipped")
        self._err_pill.setText(f"{self._error_count} error")

        # Clear and rebuild per-workbook rows
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        lines = [
            f"Run complete — _{suffix}.xlsx",
            f"{self._success_count} ok / {self._skipped_count} skipped / {self._error_count} error",
        ]
        for r in results:
            row_text = f"{r.status.upper()}  {r.filename}  —  {r.message}"
            if r.output_filename:
                row_text += f"  →  {r.output_filename}"
            lines.append(row_text)
            self._rows_layout.addWidget(QLabel(row_text))

        self._plain_text = "\n".join(lines)

    def _copy_to_clipboard(self) -> None:
        QApplication.clipboard().setText(self._plain_text)


class _EmptyState(QWidget):
    navigate_to_settings = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        icon = QLabel("📂")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading = QLabel("No workbooks configured")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("font-size: 16px; font-weight: bold;")
        description = QLabel("Add a target workbook to get started.")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setObjectName("secondary")

        self._add_btn = QPushButton("Add target workbook")
        self._add_btn.setObjectName("primary")
        self._add_btn.clicked.connect(self.navigate_to_settings)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addWidget(self._add_btn, 0, Qt.AlignmentFlag.AlignCenter)


class MainView(QWidget):
    navigate_to_settings = Signal()

    def __init__(self, config: Config, parent: QWidget | None = None):
        super().__init__(parent)

        self._run_bar = RunBar(config)
        self._workbook_table = WorkbookTable(config.workbooks)
        self._log_panel = LogPanel()
        self._empty_state = _EmptyState()

        self._empty_state.navigate_to_settings.connect(self.navigate_to_settings)

        self._log_panel.setVisible(False)

        if config.workbooks:
            self._empty_state.setVisible(False)
        else:
            self._run_bar.setVisible(False)
            self._workbook_table.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self._run_bar)
        layout.addWidget(self._workbook_table, 1)
        layout.addWidget(self._empty_state, 1)
        layout.addWidget(self._log_panel)

        self._run_bar._input_field.textChanged.connect(self._update_run_button)
        self._run_bar._suffix_field.textChanged.connect(self._update_run_button)
        self._workbook_table.selection_changed.connect(self._update_run_button)
        self._update_run_button()

    def _update_run_button(self) -> None:
        has_input = bool(self._run_bar._input_field.text())
        suffix = self._run_bar._suffix_field.text()
        suffix_valid = bool(_SUFFIX_RE.fullmatch(suffix))
        has_selection = bool(self._workbook_table.get_selected_ids())

        self._run_bar._suffix_error.setVisible(bool(suffix) and not suffix_valid)
        self._run_bar._run_button.setEnabled(has_input and suffix_valid and has_selection)

    def show_results(self, results: list[RunResult], suffix: str) -> None:
        self._log_panel.show_results(results, suffix)
        self._log_panel.setVisible(True)
