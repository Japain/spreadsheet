from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.config import Config, DEFAULT_CONFIG_PATH
from src.ui.history_view import HistoryView
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView
from src.ui.styles import STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self, config: Config | None = None):
        super().__init__()
        if config is None:
            config = Config.load(DEFAULT_CONFIG_PATH)

        self.setWindowTitle("Quarterly — Workbook Updater")
        self.setFixedSize(1280, 820)
        self.setStyleSheet(STYLESHEET)

        self._main_view = MainView(config)
        self._settings_view = SettingsView()
        self._history_view = HistoryView()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._main_view)      # index 0
        self._stack.addWidget(self._settings_view)  # index 1
        self._stack.addWidget(self._history_view)   # index 2

        sidebar = self._build_sidebar()

        central = QWidget()
        central.setObjectName("central")
        body_layout = QHBoxLayout(central)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(sidebar)
        body_layout.addWidget(self._stack, 1)

        self.setCentralWidget(central)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        mark_lbl = QLabel("Q")
        mark_lbl.setStyleSheet(
            "background:#4b6bdf; color:#fff; border-radius:6px;"
            " padding:4px 10px; font-weight:bold; font-size:16px;"
        )
        mark_lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        brand_name_lbl = QLabel("Quarterly")
        brand_name_lbl.setStyleSheet("font-weight:bold; font-size:14px;")
        brand_sub_lbl = QLabel("Workbook Updater")
        brand_sub_lbl.setObjectName("secondary")

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)
        brand_text_layout.addWidget(brand_name_lbl)
        brand_text_layout.addWidget(brand_sub_lbl)

        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.addWidget(mark_lbl)
        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()

        self._nav_run = QPushButton("Run")
        self._nav_configure = QPushButton("Configure")
        self._nav_history = QPushButton("Run History")

        for btn in (self._nav_run, self._nav_configure, self._nav_history):
            btn.setObjectName("nav_item")
            btn.setStyleSheet(
                "QPushButton { text-align:left; padding:8px 12px;"
                " border:none; border-radius:6px; color:#1b1d22; background:transparent; }"
                " QPushButton:hover { background:#ebebeb; }"
                " QPushButton[active=true] { background:#e8ecfc; color:#4b6bdf; font-weight:bold; }"
            )
            btn.setCheckable(False)

        self._nav_run.clicked.connect(lambda: self._switch_page(0))
        self._nav_configure.clicked.connect(lambda: self._switch_page(1))
        self._nav_history.clicked.connect(lambda: self._switch_page(2))

        config_lbl = QLabel(str(DEFAULT_CONFIG_PATH))
        config_lbl.setObjectName("secondary")
        config_lbl.setWordWrap(True)
        config_lbl.setStyleSheet("font-size:10px;")

        version_lbl = QLabel("v1.0.0")
        version_lbl.setObjectName("secondary")
        version_lbl.setStyleSheet("font-size:10px;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 12)
        sidebar_layout.setSpacing(2)
        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(16)
        sidebar_layout.addWidget(self._nav_run)
        sidebar_layout.addWidget(self._nav_configure)
        sidebar_layout.addWidget(self._nav_history)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(config_lbl)
        sidebar_layout.addWidget(version_lbl)

        self._update_nav_active(0)
        return sidebar

    def _switch_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._update_nav_active(index)

    def _update_nav_active(self, active_index: int) -> None:
        for i, btn in enumerate(
            [self._nav_run, self._nav_configure, self._nav_history]
        ):
            btn.setProperty("active", i == active_index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("quarterly")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
