from PySide6.QtWidgets import QWidget

from src.config import Config


class SettingsView(QWidget):
    def __init__(self, config: Config, parent: QWidget | None = None):
        super().__init__(parent)
