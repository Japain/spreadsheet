from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from src.config import TabMapping


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
