import time
from datetime import datetime
from pathlib import Path

import openpyxl
from PySide6.QtCore import QThread, Signal

from src.config import Config, Workbook, DEFAULT_LOG_PATH
from src.log import RunRecord, RunResult, append_record


def _output_path(wb: Workbook, suffix: str) -> Path:
    """Canonical output path for a workbook: {folder}/{stem}_{suffix}.xlsx."""
    return Path(wb.folder) / f"{Path(wb.filename).stem}_{suffix}.xlsx"


def check_conflicts(config: Config, selected_ids: list[str], suffix: str) -> list[str]:
    """Return output filenames that already exist on disk for the given selection."""
    wb_map = {wb.id: wb for wb in config.workbooks}
    conflicts = []
    for wb_id in selected_ids:
        wb = wb_map.get(wb_id)
        if wb is None:
            continue
        out = _output_path(wb, suffix)
        if out.exists():
            conflicts.append(out.name)
    return conflicts


class WorkbookProcessor(QThread):
    workbook_started = Signal(str)
    workbook_finished = Signal(RunResult)
    run_complete = Signal(list)
    run_error = Signal(str)

    def configure(
        self,
        config: Config,
        input_filename: str,
        suffix: str,
        selected_ids: list[str],
    ) -> None:
        self._config = config
        self._input_filename = input_filename
        self._suffix = suffix
        self._selected_ids = selected_ids

    def run(self) -> None:
        config = self._config
        suffix = self._suffix
        input_filename = self._input_filename
        selected_ids = self._selected_ids

        # 1. Validate master file
        master_path = Path(config.input_folder) / input_filename
        if not master_path.exists():
            self.run_error.emit(f"Master file not found: {master_path}")
            return

        # 2. Open master read-only; data_only=True returns cached values, not formulas
        try:
            master_wb = openpyxl.load_workbook(master_path, read_only=True, data_only=True)
        except Exception as exc:
            self.run_error.emit(f"Could not open master file: {exc}")
            return

        wb_map = {wb.id: wb for wb in config.workbooks}
        results: list[RunResult] = []

        # 3. Process each selected workbook in order; finally ensures handle is always closed
        try:
            for wb_id in selected_ids:
                self.workbook_started.emit(wb_id)
                t0 = time.monotonic()

                wb_cfg = wb_map.get(wb_id)
                if wb_cfg is None:
                    r = RunResult(
                        workbook_id=wb_id,
                        filename=wb_id,
                        status="error",
                        message=f"Workbook '{wb_id}' not found in config",
                        output_filename=None,
                        rows_written=0,
                        duration_ms=int((time.monotonic() - t0) * 1000),
                    )
                    self.workbook_finished.emit(r)
                    results.append(r)
                    continue

                output_path = _output_path(wb_cfg, suffix)
                target_path = Path(wb_cfg.folder) / wb_cfg.filename

                def _error(msg: str, _id=wb_id, _cfg=wb_cfg, _t0=t0) -> RunResult:
                    return RunResult(
                        workbook_id=_id,
                        filename=_cfg.filename,
                        status="error",
                        message=msg,
                        output_filename=None,
                        rows_written=0,
                        duration_ms=int((time.monotonic() - _t0) * 1000),
                    )

                # b. Check target exists
                if not target_path.exists():
                    r = _error(f"Target file not found: {wb_cfg.filename}")
                    self.workbook_finished.emit(r)
                    results.append(r)
                    continue

                # c. Detect file lock via exclusive open attempt
                try:
                    fh = open(target_path, "r+b")
                    fh.close()
                except PermissionError:
                    r = _error("File is open in another application — close it and re-run")
                    self.workbook_finished.emit(r)
                    results.append(r)
                    continue

                target_wb = None
                try:
                    try:
                        target_wb = openpyxl.load_workbook(target_path)
                    except Exception as exc:
                        r = _error(f"Could not open target file: {exc}")
                        self.workbook_finished.emit(r)
                        results.append(r)
                        continue

                    # d. Apply each tab mapping
                    any_skipped = False
                    rows_written = 0

                    for mapping in wb_cfg.mappings:
                        if mapping.input not in master_wb.sheetnames:
                            any_skipped = True
                            continue
                        if mapping.target not in target_wb.sheetnames:
                            any_skipped = True
                            continue

                        master_ws = master_wb[mapping.input]
                        target_ws = target_wb[mapping.target]

                        # Read master dimensions before iterating (read-only streams)
                        master_max_col = master_ws.max_column or 0
                        master_max_row = master_ws.max_row or 0
                        target_max_row = target_ws.max_row or 0

                        # Clear paste zone: A1 → target.max_row × master.max_column
                        for row in range(1, target_max_row + 1):
                            for col in range(1, master_max_col + 1):
                                target_ws.cell(row=row, column=col).value = None

                        # Write values only (data_only=True already strips formulas)
                        for r_i, row_vals in enumerate(
                            master_ws.iter_rows(values_only=True), start=1
                        ):
                            for c_i, value in enumerate(row_vals, start=1):
                                target_ws.cell(row=r_i, column=c_i).value = value

                        rows_written += master_max_row

                    # e. Save output file
                    try:
                        target_wb.save(output_path)
                    except (PermissionError, OSError) as exc:
                        r = _error(f"Could not save output: {exc}")
                        self.workbook_finished.emit(r)
                        results.append(r)
                        continue

                    status = "skipped" if any_skipped else "success"
                    r = RunResult(
                        workbook_id=wb_id,
                        filename=wb_cfg.filename,
                        status=status,
                        message="",
                        output_filename=output_path.name,
                        rows_written=rows_written,
                        duration_ms=int((time.monotonic() - t0) * 1000),
                    )
                    self.workbook_finished.emit(r)
                    results.append(r)
                finally:
                    if target_wb is not None:
                        target_wb.close()

        finally:
            master_wb.close()

        # 4. Persist run record before notifying UI so a write failure surfaces as run_error
        try:
            record = RunRecord(
                timestamp=datetime.now().isoformat(timespec="seconds"),
                input_filename=input_filename,
                suffix=suffix,
                results=results,
            )
            append_record(DEFAULT_LOG_PATH, record)
        except Exception as exc:
            self.run_error.emit(f"Could not write run log: {exc}")
            return

        self.run_complete.emit(results)
