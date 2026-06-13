from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


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
