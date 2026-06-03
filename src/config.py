import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

# Live config/log paths; USERPROFILE used on Windows, Path.home() fallback for Linux/CI
_home = Path(os.environ.get("USERPROFILE") or Path.home())
DEFAULT_CONFIG_PATH = _home / ".quarterly" / "config.json"
DEFAULT_LOG_PATH = _home / ".quarterly" / "runs.log"


@dataclass
class TabMapping:
    input: str
    target: str


@dataclass
class Workbook:
    id: str
    filename: str
    folder: str
    mappings: list[TabMapping]


@dataclass
class Config:
    input_folder: str
    workbooks: list[Workbook]

    @classmethod
    def load(cls, path: Path) -> "Config":
        path = Path(path)
        if not path.exists():
            cfg = cls(input_folder="", workbooks=[])
            path.parent.mkdir(parents=True, exist_ok=True)
            cfg.save(path)
            return cfg
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid config file: {e}") from e
        if not isinstance(data, dict):
            raise ValueError("Invalid config file: expected a JSON object")
        try:
            workbooks = [
                Workbook(
                    id=wb["id"],
                    filename=wb["filename"],
                    folder=wb["folder"],
                    mappings=[TabMapping(**m) for m in wb["mappings"]],
                )
                for wb in data.get("workbooks", [])
            ]
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid config file: {e}") from e
        return cls(input_folder=data.get("input_folder", ""), workbooks=workbooks)

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # asdict recurses into nested dataclasses (Workbook → TabMapping)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
