# Product Requirements Document
## Excel Workbook Update & Export Tool
**Version:** 0.7 — Draft for Review
**Date:** 2026-05-25
**Author:** Jarred Payne, Jenny Guo
**Status:** 🟡 In Review

---

## 1. Overview

### 1.1 Purpose
A lightweight desktop automation tool that allows a user to load a master Excel workbook, copy specific sheets from it into a set of pre-configured target workbooks (overwriting only the designated data range while preserving surrounding formulas and formatting), and export the updated workbooks with a customizable naming suffix.

### 1.2 Problem Statement
At the end of each quarter, a user must manually copy data from a single master spreadsheet into multiple separate target workbooks. Each target workbook has one or more tabs that must receive updated data while other parts of those workbooks (formulas, formatting, adjacent columns) must remain intact. This process is repetitive, error-prone, and time-consuming when done manually.

### 1.3 Goals
- Reduce manual copy-paste effort during quarter-end processing
- Prevent accidental overwriting of formulas or formatting in target workbooks
- Enable selective, per-run control over which workbooks are updated
- Produce consistently named output files with a user-defined suffix

### 1.4 Non-Goals (v1)
- Multi-user / cloud deployment
- Support for charts, pivot tables, or merged cells in source/target
- Scheduling or automated/unattended runs
- Integration with external systems (SharePoint, OneDrive sync, etc.)
- Mac OS support

---

## 2. Users

| User | Description |
|---|---|
| **Primary** | Individual analyst running quarter-end processing on Windows |
| **Future** | Other team members running the same or similar workflows |

For v1 the tool is single-user. The design should not preclude adding multi-user or shared-config support later.

---

## 3. Core Concepts & Terminology

| Term | Definition |
|---|---|
| **Master Workbook** | The source Excel file containing updated input data |
| **Input Tab** | A sheet within the Master Workbook whose data will be copied |
| **Target Workbook** | A pre-existing Excel file that receives updated data |
| **Target Tab** | A sheet within a Target Workbook that maps to an Input Tab |
| **Paste Zone** | The rectangular data region in a Target Tab that gets overwritten (starts at A1) |
| **Preserved Zone** | Columns, rows, or sheets outside the Paste Zone — never modified by the tool |
| **Tab Mapping** | The configured link between one Input Tab and one Target Tab within a specific Target Workbook |
| **Fixed Config** | Settings that persist across runs and are only updated between quarters |
| **Run Parameters** | Settings the user re-enters at the start of each processing run |
| **Suffix** | A user-defined string appended to the output filename (e.g., `_v1_052226`) |

---

## 4. Functional Requirements

### 4.1 Configuration — Two-Tier Model

The tool maintains a persistent **project configuration** that separates stable settings from per-run inputs.

#### 4.1.1 Fixed Configuration (persists between runs, updated ~quarterly)

| Setting | Description |
|---|---|
| Target Workbook list | Display name and source filename (e.g., `Report_A_v1.xlsx`) per workbook |
| Target Folder path | Folder where both the source and exported output files reside, per workbook |
| Tab Mappings | For each Target Workbook: one or more (Input Tab name → Target Tab name) pairs |
| Input File Folder Path | Folder where the Master Workbook resides — used as the default browse location when picking an input file each run |

**Rules:**
- Tab mappings are configured once and reused across all runs
- Each Target Workbook can have 1–2 tab mappings
- There are 2–8 Target Workbooks per configuration
- The tool must provide a UI to add, edit, and remove workbooks and their mappings
- Fixed Config is persisted as a human-readable **JSON file** stored locally alongside the application; it may be hand-edited outside the UI if needed

#### 4.1.2 Run Parameters (re-entered at the start of each run)

| Setting | Description |
|---|---|
| **Input File Name** | Filename of the Master Workbook for this run (e.g. `Master_Q1_2026.xlsx`) — combined with the fixed Input File Folder Path to resolve the full file path |
| **Output Suffix** | User-typed string appended to each exported filename, without a leading underscore (e.g., `v1_Test`, `v1_052226`) — the tool inserts the `_` separator automatically |
| **Run checkboxes** | Per-workbook toggle — whether this workbook is included in the current run |

**Rules:**
- Run Parameters are not saved between sessions
- The Input File Name field should support a file browser picker in addition to manual entry; the picker opens pre-navigated to the configured Input File Folder Path but allows browsing elsewhere on the filesystem
- The Output Suffix field must accept any alphanumeric string including underscores and hyphens; no file-system-illegal characters

---

### 4.2 Master Workbook Handling

- The tool reads the Master Workbook in **read-only** mode; it must never modify or save the source file
- Only the Input Tabs specified in the Tab Mappings are read; all other sheets in the Master Workbook are ignored
- Master Workbook sheets contain tabular data with a header row in row 1 and data starting at row 2; no charts, merged cells, or pivot tables
- The full data range (headers + all data rows) from each Input Tab is extracted

---

### 4.3 Data Paste Behavior

When writing to a Target Tab:

1. **Clear the Paste Zone first** — before writing, clear all cell values in the region previously occupied by data (from A1 to the last used row/column from the prior run), to prevent stale rows from persisting when the new dataset is smaller
2. **Paste values only** — write cell values as static data; do not paste formulas from the master sheet
3. **Paste starting at A1** — all Target Tabs receive data beginning at cell A1 (including the header row)
4. **Preserve everything outside the Paste Zone** — columns to the right of the pasted data table, rows below the data table (if any), other sheets in the same workbook, and all cell formatting within the target tab must remain untouched
5. **Paste Zone width is dynamic** — the width of the cleared and written region is determined by the column count of the incoming master data, not a fixed boundary; adjacent formula columns are never touched

---

### 4.4 Export & Naming

- The tool **does not overwrite** the source target file (`_v1`); it creates a new output file
- Output filename format: `{source_filename_without_extension}_{output_suffix}.xlsx`
  - The source filename (minus `.xlsx`) is used as the base; the tool appends `_` and the user-entered suffix
  - Example: Source = `Report_A_v1.xlsx`, Suffix entered = `052226` → Output = `Report_A_v1_052226.xlsx`
  - The user types the suffix **without** a leading underscore; the tool adds it
- Output files are saved to the **same folder** as their corresponding source target file
- Output format is always `.xlsx`
- **Pre-run conflict check** — before starting a run, the tool checks whether any output file for a selected workbook already exists in its target folder. If one or more conflicts are found, the tool displays a warning listing the conflicting filenames and prompts the user to confirm or cancel before any processing begins; cancelling allows the user to change the suffix and re-run

---

### 4.5 Error Handling

| Error Condition | Behavior |
|---|---|
| Master Workbook file not found | Halt entire run before starting; show error |
| Target Workbook file not found | Skip that workbook; log error; continue with remaining workbooks |
| Mapped Input Tab not found in Master | Skip that mapping; log error; continue with other mappings in that workbook |
| Mapped Target Tab not found in Target Workbook | Skip that tab mapping; log error; continue with other mappings in that workbook |
| Output folder does not exist or is not writable | Skip that workbook; log error; continue |
| Target file is open in Excel (file lock) | Skip that workbook; log a clear error ("file is open — please close it and re-run") |

All errors are surfaced in the UI at the end of the run in a results/log panel — the run never silently fails.

---

### 4.6 Run Logging

- The tool maintains an application log capturing: run timestamp, input file used, suffix applied, which workbooks were processed vs. skipped, and any errors encountered
- Log is viewable within the application and persists to a local log file
- No external log shipping or alerting required for v1

---

## 5. UI Requirements

### 5.1 Layout (based on approved sketch)

The application has a single main screen with three logical sections:

**Section A — Run Parameters (top bar)**
- Input File Name: text field + file browser button (opens pre-navigated to the fixed Input File Folder Path)
- Output Suffix: text field
- "Run" action button

**Section B — Workbook Table (main area)**
A table with one row per configured Target Workbook and the following columns:

| Column | Type | Tier |
|---|---|---|
| Run | Checkbox | Per-run |
| Filename | Display (base name) | Fixed |
| Input Tab(s) | Display | Fixed |
| Target Tab(s) | Display | Fixed |
| Target Folder | Display (truncated path) | Fixed |

**Section C — Results / Log Panel (bottom)**
- Appears after a run completes
- Shows per-workbook status: ✅ Success / ⚠️ Skipped / ❌ Error
- Shows error messages inline
- Option to copy log to clipboard

### 5.2 Configuration Management
- A separate "Settings / Configure" view (accessible via a menu or button) allows editing the Fixed Config: add/remove workbooks, edit paths, edit tab mappings
- Changes to Fixed Config are saved immediately to a local config file

### 5.3 Platform
- Windows desktop application built with **PySide6** (native Python GUI)
- Packaged as a self-contained Windows executable (PyInstaller) — no Python installation required on the end-user machine
- Must not require admin privileges to install or run

---

## 6. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Performance | Process a full run (8 workbooks, 2 tabs each) in under 60 seconds |
| Reliability | Must not corrupt target workbooks; always writes to a new output file |
| Data safety | Never modifies the Master Workbook or the source `_v1` target files |
| Portability | Runs on Windows without requiring an existing Python or Node installation (self-contained executable or simple installer for v1) |
| Extensibility | Config model and processing logic should be structured to support additional users or workbooks without architectural changes |

---

## 7. Out of Scope — v1

- Mac / Linux support
- Charts, pivot tables, or merged cell handling
- Multi-user shared configuration
- Scheduling / automated runs
- Cloud storage integration (SharePoint, OneDrive, Google Drive)
- Email or notification on run completion
- Undo / rollback of a completed run

---

## 8. Open Questions for Team Review

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | How is the Paste Zone width determined — dynamic (matches master column count) or fixed per mapping? | — | 🟢 Resolved: dynamic, matches master column count |
| 2 | Should the tool warn before overwriting an existing output file with the same name? | — | 🟢 Resolved: pre-run warning listing conflicts; user must confirm or cancel before processing begins |
| 3 | Delivery format preference: local web app (React/Python backend) vs. native Python GUI (Tkinter/PyQt)? | — | 🟢 Resolved: native Python GUI using PySide6, packaged with PyInstaller |
| 4 | Should the Fixed Config be stored as a human-readable file (JSON/YAML) that can be hand-edited, or opaque? | — | 🟢 Resolved: human-readable JSON file, stored locally alongside the application |

---

## 9. Assumptions

- All files are standard `.xlsx` format (not `.xlsm`, `.xls`, or `.xlsb`)
- The user has Excel installed on the machine (may or may not be required depending on library choice — to be confirmed in technical planning)
- One configuration ("project") is sufficient for v1; multi-project support is deferred
- The tool runs on demand only — no background processes

---

## Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 0.1 | 2026-05-24 | Jarred Payne, Jenny Guo | Initial draft for team review |
| 0.2 | 2026-05-24 | Jarred Payne | Resolve PR review comments: clarify naming format (tool adds `_` separator, user types suffix without leading underscore), align error-handling for missing input/target tabs, fix `_v2` wording in Fixed Config |
| 0.3 | 2026-05-25 | Jarred Payne | Move Input File Folder Path to Fixed Config; change Run Parameter from full file path to filename only; file browser opens pre-navigated to fixed folder |
| 0.4 | 2026-05-25 | Jarred Payne | Resolve Q1: Paste Zone width is dynamic, determined by master column count |
| 0.5 | 2026-05-25 | Jarred Payne | Resolve Q2: pre-run conflict check warns on existing output filenames; user must confirm or cancel |
| 0.6 | 2026-05-25 | Jarred Payne | Resolve Q3: native Python GUI using PySide6, packaged as self-contained Windows executable via PyInstaller |
| 0.7 | 2026-05-25 | Jarred Payne | Resolve Q4: Fixed Config stored as human-readable JSON file alongside the application |
