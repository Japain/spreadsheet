from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.config import Config, DEFAULT_CONFIG_PATH
from src.processor import WorkbookProcessor, check_conflicts
from src.ui.dialogs import ConflictDialog, ProgressDialog
from src.ui.history_view import HistoryView
from src.ui.main_view import MainView
from src.ui.settings_view import SettingsView
from src.ui.styles import STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self, config: Config | None = None):
        super().__init__()
        if config is None:
            config = Config.load(DEFAULT_CONFIG_PATH)

        self._config = config

        self.setWindowTitle("Quarterly — Workbook Updater")
        self.setFixedSize(1280, 820)
        self.setStyleSheet(STYLESHEET)

        self._main_view = MainView(config)
        self._settings_view = SettingsView(config, DEFAULT_CONFIG_PATH)
        self._history_view = HistoryView()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._main_view)      # index 0
        self._stack.addWidget(self._settings_view)  # index 1
        self._stack.addWidget(self._history_view)   # index 2

        self._main_view.navigate_to_settings.connect(lambda: self._switch_page(1))
        self._main_view.run_requested.connect(self._start_run)
        self._settings_view.workbook_added.connect(self._main_view.add_workbook)
        self._settings_view.workbook_removed.connect(self._main_view.remove_workbook)
        self._settings_view.workbook_updated.connect(self._main_view.update_workbook)

        sidebar = self._setup_sidebar()

        central = QWidget()
        central.setObjectName("central")
        body_layout = QHBoxLayout(central)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(sidebar)
        body_layout.addWidget(self._stack, 1)

        self.setCentralWidget(central)

    def _setup_sidebar(self) -> QWidget:
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
        self._nav_buttons = (self._nav_run, self._nav_configure, self._nav_history)

        for btn in self._nav_buttons:
            btn.setObjectName("nav_item")
            btn.setCheckable(False)

        self._nav_run.clicked.connect(lambda: self._switch_page(0))
        self._nav_configure.clicked.connect(lambda: self._switch_page(1))
        self._nav_history.clicked.connect(lambda: self._switch_page(2))

        config_display = f".../{DEFAULT_CONFIG_PATH.parent.name}/{DEFAULT_CONFIG_PATH.name}"
        config_lbl = QLabel(config_display)
        config_lbl.setObjectName("secondary")
        config_lbl.setToolTip(str(DEFAULT_CONFIG_PATH))
        config_lbl.setStyleSheet("font-size:10px;")

        version_lbl = QLabel("v1.0.0")  # TODO: read from package metadata (Phase 11)
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

    def _start_run(self) -> None:
        try:
            self._main_view._run_bar._run_button.setEnabled(False)
            if (prev := getattr(self, '_processor', None)) is not None:
                prev.wait()

            input_file = self._main_view._run_bar._input_field.text()
            suffix = self._main_view._run_bar._suffix_field.text()
            selected_ids = self._main_view._workbook_table.get_selected_ids()

            conflicts = check_conflicts(self._config, selected_ids, suffix)
            if conflicts:
                dlg = ConflictDialog(conflicts, self)
                if dlg.exec() != QDialog.DialogCode.Accepted:
                    return

            workbooks_for_dialog = [
                (wb.id, wb.filename)
                for wb in self._config.workbooks
                if wb.id in selected_ids
            ]
            progress_dlg = ProgressDialog(workbooks_for_dialog, self)

            self._processor = WorkbookProcessor()
            self._processor.configure(self._config, input_file, suffix, selected_ids)

            self._processor.workbook_started.connect(progress_dlg.on_workbook_started)
            self._processor.workbook_finished.connect(progress_dlg.on_workbook_finished)
            self._processor.run_complete.connect(lambda results, _: progress_dlg.on_run_complete())
            self._processor.run_complete.connect(self._main_view.show_results)
            self._processor.run_error.connect(
                lambda msg: self._handle_run_error(progress_dlg, msg)
            )

            self._processor.start()
            progress_dlg.exec()
        finally:
            self._main_view._update_run_button()

    def _handle_run_error(self, progress_dlg: ProgressDialog, message: str) -> None:
        progress_dlg.reject()
        QMessageBox.critical(self, "Run Error", message)

    def _switch_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self._update_nav_active(index)

    def _update_nav_active(self, active_index: int) -> None:
        for i, btn in enumerate(self._nav_buttons):
            btn.setProperty("active", i == active_index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("quarterly")
    try:
        window = MainWindow()
    except (ValueError, OSError) as e:
        QMessageBox.critical(
            None,
            "Configuration Error",
            f"Could not load configuration:\n\n{e}\n\nPlease fix or delete:\n{DEFAULT_CONFIG_PATH}",
        )
        sys.exit(1)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
