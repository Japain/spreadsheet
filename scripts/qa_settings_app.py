import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from PySide6.QtWidgets import QApplication
from src.config import Config, Workbook, TabMapping
from src.ui.settings_view import SettingsView
from src.ui.styles import STYLESHEET

OUT = Path(__file__).parents[1] / "docs/qa/actual"
OUT.mkdir(parents=True, exist_ok=True)

app = QApplication.instance() or QApplication(sys.argv)
app.setStyleSheet(STYLESHEET)

config_path = Path("/tmp/qa_settings_config.json")
config = Config(
    input_folder="C:/FP&A/Q1_2026",
    workbooks=[
        Workbook(id="wb1", filename="Report_EMEA.xlsx", folder="C:/Reports/EMEA",
                 mappings=[TabMapping(input="Revenue", target="Q_Data")]),
        Workbook(id="wb2", filename="Report_APAC.xlsx", folder="C:/Reports/APAC",
                 mappings=[TabMapping(input="Revenue", target="Q_Data"),
                            TabMapping(input="Summary", target="Summary")]),
    ],
)
config.save(config_path)

view = SettingsView(config, config_path)
view.resize(1060, 740)  # content area width (1280 minus 220px sidebar)
view.show()
app.processEvents()

# State 1: first workbook auto-selected
view.grab().save(str(OUT / "settings_populated.png"))

print("Saved to docs/qa/actual/")
