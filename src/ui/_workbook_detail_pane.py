from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QStringListModel, Signal
from PySide6.QtWidgets import (
    QCompleter,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import TabMapping, Workbook
from src.ui._mapping_row import _MappingRow


class _WorkbookDetailPane(QWidget):
    workbook_removed = Signal()

    def __init__(self, workbook: Workbook, save, parent=None):
        super().__init__(parent)
        self._workbook = workbook
        self._save = save
        self._rows: list[_MappingRow] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        heading = QLabel("Edit workbook")
        heading.setStyleSheet("font-size: 14px; font-weight: 600;")
        sub = QLabel("Up to two tab mappings per workbook.")
        sub.setStyleSheet("font-size: 12px; color: #6b7080;")
        layout.addWidget(heading)
        layout.addWidget(sub)
        layout.addSpacing(4)

        # Filename
        layout.addWidget(QLabel("Filename"))
        self._filename_field = QLineEdit(workbook.filename)
        self._filename_field.setObjectName("filename_field")
        layout.addWidget(self._filename_field)

        self._completer = QCompleter(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._filename_field.setCompleter(self._completer)

        # Target folder
        layout.addWidget(QLabel("Target folder"))
        folder_row = QHBoxLayout()
        folder_row.setSpacing(6)
        self._folder_field = QLineEdit(workbook.folder)
        self._folder_field.setObjectName("folder_field")
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self._folder_field)
        folder_row.addWidget(browse_btn)
        layout.addLayout(folder_row)

        layout.addWidget(self._make_divider())

        # Mappings header
        mappings_hdr = QHBoxLayout()
        self._mappings_count_lbl = QLabel(f"Tab mappings · {len(workbook.mappings)}/2")
        self._mappings_count_lbl.setStyleSheet("font-size: 12px;")
        self._add_mapping_btn = QPushButton("+ Add mapping")
        self._add_mapping_btn.setObjectName("add_mapping_btn")
        self._add_mapping_btn.clicked.connect(self._on_add_mapping)
        mappings_hdr.addWidget(self._mappings_count_lbl)
        mappings_hdr.addStretch()
        mappings_hdr.addWidget(self._add_mapping_btn)
        layout.addLayout(mappings_hdr)

        # Column sub-headers
        col_hdr = QHBoxLayout()
        col_hdr.setContentsMargins(0, 0, 0, 0)
        in_lbl = QLabel("Input tab (master)")
        out_lbl = QLabel("Target tab (this workbook)")
        for lbl in (in_lbl, out_lbl):
            lbl.setStyleSheet("font-size: 11px; color: #6b7080;")
        col_hdr.addWidget(in_lbl)
        col_hdr.addWidget(QLabel(""))
        col_hdr.addWidget(out_lbl)
        col_hdr.addWidget(QLabel(""))
        layout.addLayout(col_hdr)

        # Mapping rows container
        self._rows_layout = QVBoxLayout()
        self._rows_layout.setSpacing(6)
        layout.addLayout(self._rows_layout)

        for m in workbook.mappings:
            self._add_row(m)

        layout.addWidget(self._make_divider())

        # Remove workbook
        remove_row = QHBoxLayout()
        remove_row.addStretch()
        self._remove_wb_btn = QPushButton("Remove workbook")
        self._remove_wb_btn.setObjectName("remove_workbook_btn")
        self._remove_wb_btn.clicked.connect(self.workbook_removed)
        remove_row.addWidget(self._remove_wb_btn)
        layout.addLayout(remove_row)

        layout.addStretch()

        # Connect field signals after layout is fully built
        self._filename_field.textChanged.connect(self._on_filename_changed)
        self._folder_field.textChanged.connect(self._on_folder_changed)
        self._folder_field.textChanged.connect(self._refresh_completer)
        self._refresh_completer(workbook.folder)

        self._refresh_mapping_controls()

    @staticmethod
    def _make_divider() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(0,0,0,0.06);")
        return line

    def _add_row(self, mapping: TabMapping) -> None:
        row = _MappingRow(mapping, self._save)
        row.remove_requested.connect(lambda _row=row: self._on_remove_mapping(_row))
        self._rows.append(row)
        self._rows_layout.addWidget(row)

    def _on_filename_changed(self, value: str) -> None:
        self._workbook.filename = value
        self._save()

    def _on_folder_changed(self, value: str) -> None:
        self._workbook.folder = value
        self._save()

    def _refresh_completer(self, folder: str) -> None:
        path = Path(folder)
        if path.is_dir():
            names = sorted(p.name for p in path.glob("*.xlsx"))
        else:
            names = []
        self._completer.setModel(QStringListModel(names, self._completer))

    def _browse_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select folder", self._workbook.folder)
        if path:
            self._folder_field.setText(path)

    def _on_add_mapping(self) -> None:
        m = TabMapping("", "")
        self._workbook.mappings.append(m)
        self._save()
        self._add_row(m)
        self._refresh_mapping_controls()

    def _on_remove_mapping(self, row: _MappingRow) -> None:
        idx = self._rows.index(row)
        del self._workbook.mappings[idx]
        self._save()
        self._rows.remove(row)
        self._rows_layout.removeWidget(row)
        row.setParent(None)
        row.deleteLater()
        self._refresh_mapping_controls()

    def _refresh_mapping_controls(self) -> None:
        count = len(self._rows)
        self._add_mapping_btn.setEnabled(count < 2)
        self._mappings_count_lbl.setText(f"Tab mappings · {count}/2")
        for row in self._rows:
            row.set_remove_enabled(count > 1)
