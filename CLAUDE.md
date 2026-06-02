# spreadsheet — Claude Instructions

## Git Workflow
- **Never commit directly to `main`** — always create a feature branch first

## Project Overview
- PySide6 desktop app that copies Excel tab data between workbooks, packaged as a Windows `.exe` via PyInstaller (app name: `quarterly`)
- Dev environment is Linux/WSL; Windows-specific paths only matter in config resolution and Phase 11 packaging

## Development Setup
- Activate venv before running anything: `source venv/bin/activate`
- Run tests: `pytest` from project root
- Phase tracker: `IMPLEMENTATION_PLAN.md` — check off items as they're completed; always verify which phase is next before starting

## Testing Rules
- Every phase uses TDD: write failing tests first, then implement to pass
- Qt widget tests use `pytest-qt` (`qtbot` fixture); test files live under `tests/ui/`
- Processor tests (`tests/test_processor.py`) use `tmp_path` and real `.xlsx` files — no mocking of file I/O
