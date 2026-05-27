// Shared realistic Q1 2026 finance scenario fixtures

const FOLDER_FPA = 'C:\\Users\\jpayne\\OneDrive\\FP&A\\Q1_2026\\';
const FOLDER_OUT = 'C:\\Users\\jpayne\\OneDrive\\FP&A\\Q1_2026\\outputs\\';
const FOLDER_REG = 'C:\\Users\\jpayne\\OneDrive\\FP&A\\Q1_2026\\regional\\';

const DEFAULT_WORKBOOKS = [
  {
    id: 'wb-rev',
    filename: 'Revenue_Report_v1.xlsx',
    folder: FOLDER_FPA,
    mappings: [{ input: 'Revenue', target: 'Q_Data' }],
    run: true,
  },
  {
    id: 'wb-opex',
    filename: 'OpEx_Summary_v1.xlsx',
    folder: FOLDER_FPA,
    mappings: [{ input: 'OpEx', target: 'Data' }],
    run: true,
  },
  {
    id: 'wb-hc',
    filename: 'Headcount_Report_v1.xlsx',
    folder: FOLDER_FPA,
    mappings: [{ input: 'Headcount', target: 'HC_Data' }],
    run: true,
  },
  {
    id: 'wb-pnl',
    filename: 'PnL_Consolidated_v1.xlsx',
    folder: FOLDER_FPA,
    mappings: [
      { input: 'P&L', target: 'PL_Data' },
      { input: 'Bookings', target: 'BK_Data' },
    ],
    run: true,
  },
  {
    id: 'wb-cf',
    filename: 'Cash_Flow_v1.xlsx',
    folder: FOLDER_FPA,
    mappings: [{ input: 'CashFlow', target: 'CF_Data' }],
    run: false,
  },
  {
    id: 'wb-reg',
    filename: 'Regional_Breakdown_v1.xlsx',
    folder: FOLDER_REG,
    mappings: [
      { input: 'Region_NA', target: 'NA_Data' },
      { input: 'Region_EU', target: 'EU_Data' },
    ],
    run: true,
  },
];

const DEFAULT_INPUT_FOLDER = FOLDER_FPA;
const DEFAULT_INPUT_FILENAME = 'Master_Q1_2026.xlsx';
const DEFAULT_SUFFIX = 'v2_052526';

// Run-result fixture (used after "Run" finishes). Mix of success / skip / error
// to demonstrate the log panel.
function buildResults(workbooks, suffix) {
  return workbooks
    .filter((wb) => wb.run)
    .map((wb, i) => {
      const outName = wb.filename.replace(/\.xlsx$/, `_${suffix}.xlsx`);
      // Deterministic outcomes for the demo
      if (wb.id === 'wb-cf') return null; // not selected
      if (wb.id === 'wb-hc') {
        return {
          id: wb.id,
          filename: wb.filename,
          status: 'error',
          message: 'Target file is open in Excel — close it and re-run.',
          output: null,
          durationMs: 0,
          rowsWritten: 0,
        };
      }
      if (wb.id === 'wb-reg') {
        return {
          id: wb.id,
          filename: wb.filename,
          status: 'partial',
          message: 'Mapped tab "Region_EU" not found in target — skipped that mapping.',
          output: outName,
          durationMs: 3120,
          rowsWritten: 184,
        };
      }
      const rows = [2210, 842, 0, 1456, 0, 312][i % 6] || 600 + i * 90;
      return {
        id: wb.id,
        filename: wb.filename,
        status: 'success',
        message: 'Updated successfully.',
        output: outName,
        durationMs: 1400 + i * 380,
        rowsWritten: rows,
      };
    })
    .filter(Boolean);
}

Object.assign(window, {
  DEFAULT_WORKBOOKS,
  DEFAULT_INPUT_FOLDER,
  DEFAULT_INPUT_FILENAME,
  DEFAULT_SUFFIX,
  FOLDER_FPA,
  FOLDER_OUT,
  FOLDER_REG,
  buildResults,
});
