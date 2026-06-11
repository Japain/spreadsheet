from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.config import Config, TabMapping, Workbook


class _MappingRow(QWidget):
    remove_requested = Signal()

    def __init__(self, mapping: TabMapping, save, parent=None):
        super().__init__(parent)
        self._mapping = mapping
        self._save = save

        self._input_field = QLineEdit(mapping.input)
        self._input_field.setPlaceholderText("Input tab")

        arrow = QLabel("→")
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setFixedWidth(20)
        arrow.setStyleSheet("color: #9aa0ad;")

        self._target_field = QLineEdit(mapping.target)
        self._target_field.setPlaceholderText("Target tab")

        self._remove_btn = QPushButton("−")
        self._remove_btn.setObjectName("remove_mapping_btn")
        self._remove_btn.setFixedWidth(28)
        self._remove_btn.clicked.connect(self.remove_requested)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._input_field)
        layout.addWidget(arrow)
        layout.addWidget(self._target_field)
        layout.addWidget(self._remove_btn)

        # Connect after construction so init text doesn't trigger saves
        self._input_field.textChanged.connect(self._on_input_changed)
        self._target_field.textChanged.connect(self._on_target_changed)

    def _on_input_changed(self, value: str) -> None:
        self._mapping.input = value
        self._save()

    def _on_target_changed(self, value: str) -> None:
        self._mapping.target = value
        self._save()

    def set_remove_enabled(self, enabled: bool) -> None:
        self._remove_btn.setEnabled(enabled)


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

        # Target folder
        layout.addWidget(QLabel("Target folder"))
        folder_row = QHBoxLayout()
        folder_row.setSpacing(6)
        self._folder_field = QLineEdit(workbook.folder)
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
        row.setParent(None)
        row.deleteLater()
        self._refresh_mapping_controls()

    def _refresh_mapping_controls(self) -> None:
        count = len(self._rows)
        self._add_mapping_btn.setEnabled(count < 2)
        self._mappings_count_lbl.setText(f"Tab mappings · {count}/2")
        for row in self._rows:
            row.set_remove_enabled(count > 1)


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
        self.setStyleSheet("background: oklch(0.96 0.03 254);" if selected else "")

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


class SettingsView(QWidget):
    def __init__(self, config: Config, config_path: Path, parent: QWidget | None = None):
        super().__init__(parent)
        self._config = config
        self._config_path = Path(config_path)
        self._selected_index: int | None = None
        self._list_items: list[_WorkbookListItem] = []
        self._detail_pane: _WorkbookDetailPane | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        outer.addWidget(self._build_global_card())

        panes = QWidget()
        panes_layout = QHBoxLayout(panes)
        panes_layout.setContentsMargins(0, 0, 0, 0)
        panes_layout.setSpacing(12)
        panes_layout.addWidget(self._build_left_pane(), 3)
        panes_layout.addWidget(self._build_right_container(), 2)
        outer.addWidget(panes, 1)

        for wb in self._config.workbooks:
            self._append_list_item(wb)

        if self._config.workbooks:
            self._select(0)

    # ── Global settings card ───────────────────────────────────────────────────

    def _build_global_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Default input folder"))
        self._input_folder_field = QLineEdit(self._config.input_folder)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self._browse_input_folder)
        layout.addWidget(self._input_folder_field, 1)
        layout.addWidget(browse_btn)

        note = QLabel("The file picker opens here, but you can browse anywhere.")
        note.setStyleSheet("font-size: 11px; color: #6b7080;")
        layout.addWidget(note)

        self._input_folder_field.textChanged.connect(self._on_input_folder_changed)
        return card

    def _browse_input_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select input folder", self._config.input_folder
        )
        if path:
            self._input_folder_field.setText(path)

    def _on_input_folder_changed(self, value: str) -> None:
        self._config.input_folder = value
        self._config.save(self._config_path)

    # ── Left pane ──────────────────────────────────────────────────────────────

    def _build_left_pane(self) -> QWidget:
        pane = QWidget()
        pane.setObjectName("card")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        hdr_layout = QHBoxLayout(header)
        hdr_layout.setContentsMargins(12, 10, 12, 10)
        self._workbooks_title = QLabel("Target workbooks (0)")
        self._workbooks_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        self._add_wb_btn = QPushButton("Add")
        self._add_wb_btn.setObjectName("add_workbook_btn")
        self._add_wb_btn.clicked.connect(self._on_add_workbook)
        hdr_layout.addWidget(self._workbooks_title)
        hdr_layout.addStretch()
        hdr_layout.addWidget(self._add_wb_btn)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)

        self._empty_lbl = QLabel("No workbooks yet. Click Add to create one.")
        self._empty_lbl.setStyleSheet("padding: 32px 16px; color: #9aa0ad; font-size: 12px;")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._list_layout.addWidget(self._empty_lbl)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll, 1)
        return pane

    # ── Right container ────────────────────────────────────────────────────────

    def _build_right_container(self) -> QWidget:
        container = QWidget()
        container.setObjectName("card")
        self._right_layout = QVBoxLayout(container)
        self._right_layout.setContentsMargins(0, 0, 0, 0)

        self._placeholder = QLabel("Select a workbook to configure it")
        self._placeholder.setObjectName("detail_placeholder")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #9aa0ad; font-size: 13px; padding: 40px;")
        self._right_layout.addWidget(self._placeholder)
        self._right_layout.addStretch()
        return container

    # ── List management ────────────────────────────────────────────────────────

    def _append_list_item(self, wb: Workbook) -> None:
        item = _WorkbookListItem(wb)
        self._list_items.append(item)
        pos = self._list_layout.count() - 1  # before trailing stretch
        self._list_layout.insertWidget(pos, item)
        item.clicked.connect(lambda _item=item: self._select_item(_item))
        count = len(self._list_items)
        self._empty_lbl.setVisible(count == 0)
        self._workbooks_title.setText(f"Target workbooks ({count})")

    def _select_item(self, item: _WorkbookListItem) -> None:
        self._select(self._list_items.index(item))

    def _select(self, index: int) -> None:
        self._selected_index = index

        for i, item in enumerate(self._list_items):
            item.set_selected(i == index)

        if self._detail_pane is not None:
            self._detail_pane.setParent(None)
            self._detail_pane.deleteLater()
            self._detail_pane = None

        self._placeholder.hide()

        workbook = self._config.workbooks[index]

        def save() -> None:
            self._config.save(self._config_path)
            if (
                self._selected_index is not None
                and self._selected_index < len(self._list_items)
            ):
                self._list_items[self._selected_index].refresh(
                    self._config.workbooks[self._selected_index]
                )

        self._detail_pane = _WorkbookDetailPane(workbook, save)
        self._detail_pane.workbook_removed.connect(self._on_remove_selected)
        self._right_layout.insertWidget(0, self._detail_pane)

    # ── Workbook CRUD ──────────────────────────────────────────────────────────

    def _on_add_workbook(self) -> None:
        wb = Workbook(
            id=str(uuid4()),
            filename="",
            folder="",
            mappings=[TabMapping("", "")],
        )
        self._config.workbooks.append(wb)
        self._config.save(self._config_path)
        self._append_list_item(wb)
        self._select(len(self._config.workbooks) - 1)

    def _on_remove_selected(self) -> None:
        if self._selected_index is None:
            return
        index = self._selected_index

        del self._config.workbooks[index]
        self._config.save(self._config_path)

        item = self._list_items.pop(index)
        item.setParent(None)
        item.deleteLater()

        if self._detail_pane is not None:
            self._detail_pane.setParent(None)
            self._detail_pane.deleteLater()
            self._detail_pane = None

        count = len(self._list_items)
        self._empty_lbl.setVisible(count == 0)
        self._workbooks_title.setText(f"Target workbooks ({count})")

        if self._config.workbooks:
            self._select(max(0, index - 1))
        else:
            self._selected_index = None
            self._placeholder.show()
