import json
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass
class RunResult:
    workbook_id: str
    filename: str
    status: Literal["success", "skipped", "error"]
    message: str
    output_filename: str | None  # None when status == "error"
    rows_written: int            # 0 when status == "error" (workbook not processed)
    duration_ms: int

    def __post_init__(self):
        if self.status not in ("success", "skipped", "error"):
            raise ValueError(f"Invalid status: {self.status!r}")
        if self.status == "error":
            if self.output_filename is not None:
                raise ValueError("output_filename must be None when status is 'error'")
            if self.rows_written != 0:
                raise ValueError("rows_written must be 0 when status is 'error'")


@dataclass
class RunRecord:
    timestamp: str   # ISO-8601, e.g. "2026-01-01T12:00:00"
    input_filename: str
    suffix: str
    results: list[RunResult]


def append_record(path: Path, record: RunRecord) -> None:
    path = Path(path)
    datetime.fromisoformat(record.timestamp)  # validate ISO-8601 format
    path.parent.mkdir(parents=True, exist_ok=True)
    # asdict recurses into nested dataclasses (RunRecord → RunResult)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record)) + "\n")


def read_records(path: Path) -> list[RunRecord]:
    path = Path(path)
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            results = [RunResult(**r) for r in data["results"]]
            records.append(RunRecord(
                timestamp=data["timestamp"],
                input_filename=data["input_filename"],
                suffix=data["suffix"],
                results=results,
            ))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            warnings.warn(f"Skipping unreadable log entry: {e}")
    return list(reversed(records))
