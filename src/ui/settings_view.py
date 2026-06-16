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
from src.ui._workbook_detail_pane import _WorkbookDetailPane
from src.ui._workbook_list_item import _WorkbookListItem


class SettingsView(QWidget):
    workbook_added = Signal(object)
    workbook_removed = Signal(str)

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
        self._input_folder_field.setObjectName("input_folder_field")
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

        self._placeholder = QLabel("Select a workbook to edit its mappings, or add a new one.")
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
            self._right_layout.removeWidget(self._detail_pane)
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
        self.workbook_added.emit(wb)

    def _on_remove_selected(self) -> None:
        if self._selected_index is None:
            return
        index = self._selected_index
        removed_id = self._config.workbooks[index].id

        del self._config.workbooks[index]
        self._config.save(self._config_path)

        item = self._list_items.pop(index)
        self._list_layout.removeWidget(item)
        item.setParent(None)
        item.deleteLater()

        if self._detail_pane is not None:
            self._right_layout.removeWidget(self._detail_pane)
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
        self.workbook_removed.emit(removed_id)
