import json
import pytest
from src.log import RunResult, RunRecord, append_record, read_records


def make_result(workbook_id="wb1", status="success"):
    return RunResult(
        workbook_id=workbook_id,
        filename="Report_A_v1.xlsx",
        status=status,
        message="",
        output_filename="Report_A_v1_Q1.xlsx",
        rows_written=10,
        duration_ms=120,
    )


def make_record(timestamp="2026-01-01T00:00:00", suffix="Q1"):
    return RunRecord(
        timestamp=timestamp,
        input_filename="Master_Q1.xlsx",
        suffix=suffix,
        results=[make_result()],
    )


def test_append_record_writes_ndjson_and_second_call_appends(tmp_path):
    path = tmp_path / "runs.log"
    r1 = make_record(timestamp="2026-01-01T00:00:00", suffix="Q1")
    r2 = make_record(timestamp="2026-02-01T00:00:00", suffix="Q2")
    append_record(path, r1)
    append_record(path, r2)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["suffix"] == "Q1"
    assert json.loads(lines[1])["suffix"] == "Q2"


def test_read_records_returns_most_recent_first(tmp_path):
    path = tmp_path / "runs.log"
    append_record(path, make_record(timestamp="2026-01-01T00:00:00", suffix="Q1"))
    append_record(path, make_record(timestamp="2026-02-01T00:00:00", suffix="Q2"))
    records = read_records(path)
    assert records[0].suffix == "Q2"
    assert records[1].suffix == "Q1"


def test_read_records_missing_file_returns_empty_list(tmp_path):
    path = tmp_path / "nonexistent.log"
    assert read_records(path) == []


def test_read_records_skips_corrupt_lines(tmp_path):
    path = tmp_path / "runs.log"
    append_record(path, make_record(timestamp="2026-01-01T00:00:00", suffix="Q1"))
    with path.open("a", encoding="utf-8") as f:
        f.write("{corrupt json\n")
    append_record(path, make_record(timestamp="2026-03-01T00:00:00", suffix="Q3"))
    import warnings
    with warnings.catch_warnings(record=True):
        records = read_records(path)
    assert len(records) == 2
    assert records[0].suffix == "Q3"
    assert records[1].suffix == "Q1"


def test_run_result_rejects_invalid_status():
    with pytest.raises(ValueError, match="status"):
        RunResult(
            workbook_id="wb1",
            filename="Report.xlsx",
            status="FAIL",
            message="",
            output_filename=None,
            rows_written=0,
            duration_ms=0,
        )


def test_run_result_error_status_rejects_non_none_output_filename():
    with pytest.raises(ValueError, match="output_filename"):
        RunResult(
            workbook_id="wb1",
            filename="Report.xlsx",
            status="error",
            message="failed",
            output_filename="Report_Q1.xlsx",
            rows_written=0,
            duration_ms=0,
        )


def test_run_result_error_status_rejects_nonzero_rows_written():
    with pytest.raises(ValueError, match="rows_written"):
        RunResult(
            workbook_id="wb1",
            filename="Report.xlsx",
            status="error",
            message="failed",
            output_filename=None,
            rows_written=5,
            duration_ms=0,
        )
