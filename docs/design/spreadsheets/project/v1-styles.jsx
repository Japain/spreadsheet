// V1 "Quarterly" — Polished Windows 11 Fluent-inspired desktop app.
// Single interactive component containing all states/views. Each state lives
// in useState; views switch within the same window chrome.

const V1_STYLES = `
  .v1-root {
    width: 1280px; height: 820px;
    font-family: "Segoe UI Variable", "Segoe UI", system-ui, -apple-system, sans-serif;
    background: linear-gradient(180deg, #f4f5f9 0%, #ecedf2 100%);
    color: #1b1d22;
    border-radius: 8px;
    overflow: hidden;
    display: flex; flex-direction: column;
    box-shadow: 0 30px 80px -20px rgba(20, 24, 40, 0.22), 0 0 0 1px rgba(0,0,0,0.06);
    position: relative;
    font-feature-settings: "ss01", "cv11";
    font-variant-numeric: tabular-nums;
  }
  .v1-titlebar {
    height: 32px; flex: 0 0 32px;
    display: flex; align-items: stretch;
    background: rgba(245,246,250,0.72);
    backdrop-filter: blur(20px);
    -webkit-app-region: drag;
    border-bottom: 1px solid rgba(0,0,0,0.04);
  }
  .v1-titlebar-title {
    flex: 1; display: flex; align-items: center; gap: 8px;
    padding-left: 12px; font-size: 12px; color: #4b4f5a; letter-spacing: 0.01em;
  }
  .v1-titlebar-title svg { color: #1f7a3b; }
  .v1-titlebar-controls { display: flex; }
  .v1-titlebar-controls button {
    width: 46px; height: 32px; border: 0; background: transparent;
    color: #1b1d22; cursor: pointer; display: grid; place-items: center;
    -webkit-app-region: no-drag;
  }
  .v1-titlebar-controls button:hover { background: rgba(0,0,0,0.06); }
  .v1-titlebar-controls button.close:hover { background: #c42b1c; color: #fff; }

  .v1-body { flex: 1; min-height: 0; display: flex; }
  .v1-sidebar {
    width: 220px; flex: 0 0 220px;
    background: rgba(245,246,250,0.55);
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(0,0,0,0.05);
    padding: 8px;
    display: flex; flex-direction: column;
  }
  .v1-side-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 12px 18px;
  }
  .v1-side-mark {
    width: 28px; height: 28px; border-radius: 6px;
    background: linear-gradient(135deg, oklch(0.62 0.13 250), oklch(0.48 0.16 256));
    display: grid; place-items: center; color: white;
    font-weight: 700; font-size: 13px; letter-spacing: -0.02em;
    box-shadow: 0 1px 0 rgba(255,255,255,0.4) inset, 0 1px 2px rgba(0,0,0,0.15);
  }
  .v1-side-brand-name { font-weight: 600; font-size: 14px; }
  .v1-side-brand-sub { font-size: 11px; color: #6b7080; margin-top: 1px; }
  .v1-side-section { font-size: 11px; color: #8a8e9b; padding: 8px 12px 4px; text-transform: uppercase; letter-spacing: 0.06em; }
  .v1-side-item {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 12px; border-radius: 6px; cursor: pointer;
    font-size: 13px; color: #2a2d35;
    position: relative;
  }
  .v1-side-item:hover { background: rgba(0,0,0,0.04); }
  .v1-side-item.active { background: rgba(0,0,0,0.05); font-weight: 600; }
  .v1-side-item.active::before {
    content: ''; position: absolute; left: 2px; top: 9px; bottom: 9px; width: 3px;
    background: oklch(0.55 0.16 254); border-radius: 2px;
  }
  .v1-side-spacer { flex: 1; }
  .v1-side-footer {
    padding: 12px; font-size: 11px; color: #8a8e9b;
    border-top: 1px solid rgba(0,0,0,0.05);
    display: flex; flex-direction: column; gap: 4px;
  }

  .v1-content {
    flex: 1; min-width: 0; padding: 24px 32px 0;
    overflow: hidden; display: flex; flex-direction: column;
    background: rgba(255,255,255,0.4);
  }
  .v1-h1 { font-size: 22px; font-weight: 600; letter-spacing: -0.01em; margin: 0; }
  .v1-sub { font-size: 13px; color: #6b7080; margin-top: 4px; }

  .v1-card {
    background: #ffffff; border-radius: 8px;
    box-shadow: 0 0 0 1px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.02);
  }

  .v1-runbar { display: grid; grid-template-columns: 1fr 220px auto; gap: 12px; align-items: end; padding: 16px; }
  .v1-field { display: flex; flex-direction: column; gap: 6px; }
  .v1-label { font-size: 12px; color: #4b4f5a; font-weight: 500; }
  .v1-input-wrap { display: flex; align-items: stretch; height: 32px; border-radius: 6px; box-shadow: 0 0 0 1px rgba(0,0,0,0.12), 0 1px 0 rgba(0,0,0,0.04); background: #fff; transition: box-shadow .12s; }
  .v1-input-wrap:focus-within { box-shadow: 0 0 0 1px oklch(0.55 0.16 254), 0 0 0 3px oklch(0.55 0.16 254 / 0.16); }
  .v1-input { flex: 1; min-width: 0; border: 0; outline: 0; padding: 0 10px; font: inherit; background: transparent; font-size: 13px; color: #1b1d22; font-variant-numeric: tabular-nums; }
  .v1-input::placeholder { color: #9aa0ad; }
  .v1-input-suffix { display: flex; align-items: center; padding: 0 10px; font-size: 12px; color: #6b7080; border-left: 1px solid rgba(0,0,0,0.06); background: rgba(0,0,0,0.015); }
  .v1-browse-btn { border: 0; background: transparent; padding: 0 10px; cursor: pointer; display: grid; place-items: center; color: #4b4f5a; border-left: 1px solid rgba(0,0,0,0.06); }
  .v1-browse-btn:hover { background: rgba(0,0,0,0.04); }

  .v1-btn { height: 32px; padding: 0 16px; border-radius: 6px; border: 0; cursor: pointer; font: inherit; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; transition: background .12s, box-shadow .12s, transform .04s; }
  .v1-btn-primary { background: oklch(0.55 0.16 254); color: white; box-shadow: 0 1px 0 rgba(255,255,255,0.25) inset, 0 1px 2px rgba(0,0,0,0.12); }
  .v1-btn-primary:hover { background: oklch(0.5 0.17 254); }
  .v1-btn-primary:active { transform: translateY(0.5px); }
  .v1-btn-primary:disabled { background: #c8ccd6; cursor: not-allowed; box-shadow: none; }
  .v1-btn-secondary { background: #fff; color: #1b1d22; box-shadow: 0 0 0 1px rgba(0,0,0,0.12), 0 1px 0 rgba(0,0,0,0.04); }
  .v1-btn-secondary:hover { background: rgba(0,0,0,0.03); }
  .v1-btn-ghost { background: transparent; color: #2a2d35; }
  .v1-btn-ghost:hover { background: rgba(0,0,0,0.05); }
  .v1-btn-danger-ghost { background: transparent; color: #c42b1c; }
  .v1-btn-danger-ghost:hover { background: rgba(196,43,28,0.08); }
  .v1-btn-sm { height: 26px; padding: 0 10px; font-size: 12px; }

  .v1-table-card { margin-top: 16px; flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
  .v1-table-header {
    display: grid; grid-template-columns: 48px minmax(220px, 1.6fr) 1fr 1fr 1.2fr 40px;
    align-items: center; gap: 12px;
    padding: 10px 16px;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
    color: #6b7080; font-weight: 600;
  }
  .v1-table-body { flex: 1; min-height: 0; overflow: auto; }
  .v1-row {
    display: grid; grid-template-columns: 48px minmax(220px, 1.6fr) 1fr 1fr 1.2fr 40px;
    align-items: center; gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
    font-size: 13px;
    transition: background .1s;
  }
  .v1-row:last-child { border-bottom: 0; }
  .v1-row:hover { background: rgba(0,0,0,0.02); }
  .v1-row.unchecked { color: #9aa0ad; }
  .v1-row.unchecked .v1-fn { color: #6b7080; }
  .v1-fn { font-weight: 600; display: flex; align-items: center; gap: 8px; }
  .v1-fn-icon { width: 18px; height: 18px; flex: 0 0 18px; color: #1f7a3b; }
  .v1-tabs { display: flex; flex-wrap: wrap; gap: 4px; }
  .v1-tab-chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 2px 7px; border-radius: 4px;
    background: rgba(0,0,0,0.045); font-size: 12px; color: #2a2d35;
    font-family: "Cascadia Mono", "Consolas", monospace;
  }
  .v1-row.unchecked .v1-tab-chip { background: rgba(0,0,0,0.025); color: #9aa0ad; }
  .v1-path {
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 11.5px; color: #6b7080;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    direction: rtl; text-align: left;
  }
  .v1-row.unchecked .v1-path { color: #b0b4bf; }

  /* Checkbox */
  .v1-check { width: 18px; height: 18px; border-radius: 4px; box-shadow: 0 0 0 1.5px rgba(0,0,0,0.25); background: #fff; display: grid; place-items: center; cursor: pointer; transition: background .1s, box-shadow .1s; }
  .v1-check:hover { box-shadow: 0 0 0 1.5px rgba(0,0,0,0.4); }
  .v1-check.on { background: oklch(0.55 0.16 254); box-shadow: 0 0 0 1.5px oklch(0.55 0.16 254); color: #fff; }

  /* Log panel */
  .v1-log-card { margin-top: 12px; margin-bottom: 16px; padding: 0; overflow: hidden; }
  .v1-log-header { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-bottom: 1px solid rgba(0,0,0,0.05); }
  .v1-log-title { font-weight: 600; font-size: 13px; flex: 1; display: flex; align-items: center; gap: 10px; }
  .v1-log-body { max-height: 220px; overflow: auto; }
  .v1-log-row { display: grid; grid-template-columns: 24px 1fr 1fr auto 90px; gap: 12px; align-items: center; padding: 10px 16px; border-bottom: 1px solid rgba(0,0,0,0.04); font-size: 12.5px; }
  .v1-log-row:last-child { border-bottom: 0; }
  .v1-log-msg { color: #6b7080; font-size: 12px; }
  .v1-log-out { font-family: "Cascadia Mono", "Consolas", monospace; font-size: 11.5px; color: #2a2d35; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .v1-pill { display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; letter-spacing: 0.01em; }
  .v1-pill.success { background: oklch(0.94 0.07 145); color: oklch(0.36 0.13 145); }
  .v1-pill.error { background: oklch(0.94 0.06 25); color: oklch(0.4 0.16 25); }
  .v1-pill.warn { background: oklch(0.95 0.08 80); color: oklch(0.42 0.13 70); }
  .v1-pill.neutral { background: rgba(0,0,0,0.05); color: #4b4f5a; }

  /* Modal overlay */
  .v1-scrim { position: absolute; inset: 0; background: rgba(20,22,30,0.32); backdrop-filter: blur(2px); display: grid; place-items: center; z-index: 50; animation: v1-fade .14s ease; }
  @keyframes v1-fade { from { opacity: 0; } to { opacity: 1; } }
  .v1-modal { width: 520px; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 30px 80px -20px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,0,0,0.06); animation: v1-pop .14s cubic-bezier(.2,.7,.3,1.2); }
  @keyframes v1-pop { from { transform: scale(0.96) translateY(4px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
  .v1-modal-lg { width: 680px; }
  .v1-modal-header { padding: 20px 24px 0; }
  .v1-modal-title { font-size: 18px; font-weight: 600; margin: 0 0 6px; display: flex; align-items: center; gap: 10px; }
  .v1-modal-sub { font-size: 13px; color: #4b4f5a; line-height: 1.5; }
  .v1-modal-body { padding: 16px 24px 0; }
  .v1-modal-footer { display: flex; gap: 8px; justify-content: flex-end; padding: 20px 24px 20px; }

  /* Progress dialog */
  .v1-progress-list { padding: 0; list-style: none; margin: 0; }
  .v1-progress-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.05); font-size: 13px; }
  .v1-progress-row:last-child { border-bottom: 0; }
  .v1-progress-fname { flex: 1; font-weight: 500; display: flex; align-items: center; gap: 8px; }
  .v1-spinner { width: 16px; height: 16px; border: 2px solid rgba(0,0,0,0.12); border-top-color: oklch(0.55 0.16 254); border-radius: 50%; animation: v1-spin .7s linear infinite; }
  @keyframes v1-spin { to { transform: rotate(360deg); } }
  .v1-bar { height: 4px; background: rgba(0,0,0,0.06); border-radius: 2px; overflow: hidden; margin-top: 12px; }
  .v1-bar-fill { height: 100%; background: oklch(0.55 0.16 254); transition: width .25s linear; }

  /* Empty state */
  .v1-empty { flex: 1; display: grid; place-items: center; padding: 40px; }
  .v1-empty-card { max-width: 520px; text-align: center; }
  .v1-empty-icon { width: 64px; height: 64px; margin: 0 auto 16px; border-radius: 12px; display: grid; place-items: center; background: linear-gradient(135deg, oklch(0.95 0.04 254), oklch(0.92 0.06 254)); color: oklch(0.45 0.16 254); }
  .v1-empty-h { font-size: 18px; font-weight: 600; margin: 0; }
  .v1-empty-p { color: #4b4f5a; font-size: 13px; margin: 6px 0 20px; line-height: 1.55; }
  .v1-empty-actions { display: flex; gap: 8px; justify-content: center; }

  /* Settings */
  .v1-set-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 16px; flex: 1; min-height: 0; }
  .v1-set-list { display: flex; flex-direction: column; min-height: 0; }
  .v1-set-list-header { padding: 12px 16px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid rgba(0,0,0,0.05); }
  .v1-set-list-title { font-weight: 600; font-size: 13px; flex: 1; }
  .v1-set-list-body { flex: 1; min-height: 0; overflow: auto; }
  .v1-set-row { padding: 12px 16px; border-bottom: 1px solid rgba(0,0,0,0.04); cursor: pointer; display: flex; align-items: flex-start; gap: 10px; transition: background .1s; }
  .v1-set-row:last-child { border-bottom: 0; }
  .v1-set-row:hover { background: rgba(0,0,0,0.02); }
  .v1-set-row.active { background: oklch(0.96 0.03 254); }
  .v1-set-row-info { flex: 1; min-width: 0; }
  .v1-set-fn { font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 8px; }
  .v1-set-meta { font-size: 11.5px; color: #6b7080; margin-top: 3px; font-family: "Cascadia Mono", "Consolas", monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .v1-set-detail { padding: 20px 24px; overflow: auto; }
  .v1-set-detail-h { font-size: 14px; font-weight: 600; margin: 0 0 4px; }
  .v1-set-detail-sub { font-size: 12px; color: #6b7080; margin-bottom: 16px; }
  .v1-set-mapping { display: grid; grid-template-columns: 1fr 16px 1fr 24px; gap: 8px; align-items: center; margin-bottom: 8px; }
  .v1-set-mapping-arrow { color: #9aa0ad; display: grid; place-items: center; }
  .v1-set-divider { height: 1px; background: rgba(0,0,0,0.06); margin: 16px 0; }
  .v1-set-form-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }

  /* Toast */
  .v1-toast { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: #1b1d22; color: #fff; padding: 10px 16px; border-radius: 6px; font-size: 13px; display: flex; align-items: center; gap: 10px; box-shadow: 0 12px 30px rgba(0,0,0,0.3); z-index: 60; animation: v1-toast-in .2s ease; }
  @keyframes v1-toast-in { from { transform: translate(-50%, 10px); opacity: 0; } to { transform: translate(-50%, 0); opacity: 1; } }

  /* Hide scrollbars subtly */
  .v1-root *::-webkit-scrollbar { width: 10px; height: 10px; }
  .v1-root *::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.18); border-radius: 5px; border: 2px solid transparent; background-clip: padding-box; }
  .v1-root *::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.3); background-clip: padding-box; border: 2px solid transparent; }
  .v1-root *::-webkit-scrollbar-track { background: transparent; }
`;

// ---------- Icons (small inline SVGs) ----------
const IcXlsx = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <rect x="3" y="3" width="18" height="18" rx="2.5" fill="currentColor" opacity="0.12"/>
    <rect x="3" y="3" width="18" height="18" rx="2.5" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M8.5 8.5l7 7M15.5 8.5l-7 7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
  </svg>
);
const IcFolder = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M3 7a2 2 0 012-2h3.6l2 2H19a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
  </svg>
);
const IcPlay = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M7 5l12 7-12 7V5z" fill="currentColor"/>
  </svg>
);
const IcGear = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M12 9.5a2.5 2.5 0 100 5 2.5 2.5 0 000-5z" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M19.4 13.5l1.5.9-1.5 2.6-1.7-.6a7.8 7.8 0 01-1.8 1l-.3 1.8h-3l-.3-1.8a7.8 7.8 0 01-1.8-1l-1.7.6-1.5-2.6 1.5-.9a7.8 7.8 0 010-2l-1.5-.9 1.5-2.6 1.7.6a7.8 7.8 0 011.8-1L10 5.7h3l.3 1.8a7.8 7.8 0 011.8 1l1.7-.6 1.5 2.6-1.5.9a7.8 7.8 0 010 2z" stroke="currentColor" strokeWidth="1.4"/>
  </svg>
);
const IcHome = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M3.5 11L12 4l8.5 7v8a1.5 1.5 0 01-1.5 1.5h-3.5V14h-7v6.5H5A1.5 1.5 0 013.5 19v-8z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
  </svg>
);
const IcHistory = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M4 12a8 8 0 108-8 8 8 0 00-5.8 2.5L4 4M4 4v3.5h3.5M12 8v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const IcCheck = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M5 12.5L10 17l9-10" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const IcWarn = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M12 3.5L22 20H2L12 3.5z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
    <path d="M12 10v4M12 17v.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
  </svg>
);
const IcX = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);
const IcArrow = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const IcCopy = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <rect x="8" y="8" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.6"/>
    <path d="M16 8V5a1 1 0 00-1-1H5a1 1 0 00-1 1v10a1 1 0 001 1h3" stroke="currentColor" strokeWidth="1.6"/>
  </svg>
);
const IcPlus = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);
const IcTrash = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M4 7h16M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2M6 7l1 13a1 1 0 001 1h8a1 1 0 001-1l1-13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const IcExcel = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <rect x="3" y="3" width="18" height="18" rx="2" fill="#1f7a3b"/>
    <path d="M8 8l8 8M16 8l-8 8" stroke="#fff" strokeWidth="1.8" strokeLinecap="round"/>
  </svg>
);

// ---------- Helpers ----------
function basename(path) {
  if (!path) return '';
  return path.split(/[\\/]/).filter(Boolean).pop() || path;
}
function shortPath(path, max = 32) {
  if (!path || path.length <= max) return path;
  return '…' + path.slice(-(max - 1));
}

Object.assign(window, {
  V1_STYLES,
  IcXlsx, IcFolder, IcPlay, IcGear, IcHome, IcHistory,
  IcCheck, IcWarn, IcX, IcArrow, IcCopy, IcPlus, IcTrash, IcExcel,
  basename, shortPath,
});
