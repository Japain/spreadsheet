import json
import pytest
from pathlib import Path
from src.config import Config, TabMapping, Workbook


def make_config():
    return Config(
        input_folder="/data/input",
        workbooks=[
            Workbook(
                id="wb1",
                filename="Report_A_v1.xlsx",
                folder="/data/reports",
                mappings=[
                    TabMapping(input="Sheet1", target="Data"),
                    TabMapping(input="Sheet2", target="Summary"),
                ],
            )
        ],
    )


def test_config_round_trip(tmp_path):
    path = tmp_path / "config.json"
    cfg = make_config()
    cfg.save(path)
    loaded = Config.load(path)
    assert loaded == cfg


def test_config_load_missing_file_creates_default(tmp_path):
    path = tmp_path / "subdir" / "config.json"
    cfg = Config.load(path)
    assert path.exists()
    assert cfg.workbooks == []
    assert cfg.input_folder == ""


def test_config_load_malformed_json_raises_clear_error(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{ not valid json }")
    with pytest.raises(ValueError, match="config"):
        Config.load(path)


def test_config_load_missing_workbook_key_raises_clear_error(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"input_folder": "", "workbooks": [{"id": "x"}]}')
    with pytest.raises(ValueError, match="config"):
        Config.load(path)
