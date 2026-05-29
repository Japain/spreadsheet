// V2 "QX" — Bolder, denser, designer-y desktop app.
// Dark warm charcoal, monospace-led, single-pane command-center layout.

const V2_STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

  .v2-root {
    width: 1280px; height: 820px;
    font-family: 'Inter', system-ui, sans-serif;
    background: #14130f;
    color: #e8e4dc;
    border-radius: 10px;
    overflow: hidden;
    display: flex; flex-direction: column;
    box-shadow: 0 30px 80px -20px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.06);
    position: relative;
    font-feature-settings: "ss01", "cv11";
    --accent: oklch(0.76 0.16 70);
    --accent-dim: oklch(0.45 0.12 70);
    --accent-bg: oklch(0.3 0.06 70);
    --bg-1: #1a1815;
    --bg-2: #211f1b;
    --border: rgba(255,255,255,0.06);
    --border-2: rgba(255,255,255,0.1);
    --text-1: #e8e4dc;
    --text-2: #a8a39a;
    --text-3: #6b665c;
    --success: oklch(0.78 0.14 145);
    --warn: oklch(0.78 0.14 75);
    --error: oklch(0.7 0.18 25);
  }
  .v2-root * { font-variant-numeric: tabular-nums; }
  .v2-mono { font-family: 'JetBrains Mono', ui-monospace, monospace; }

  .v2-titlebar {
    height: 36px; flex: 0 0 36px;
    display: flex; align-items: stretch;
    background: #100f0c;
    border-bottom: 1px solid var(--border);
  }
  .v2-titlebar-title {
    flex: 1; display: flex; align-items: center; gap: 10px;
    padding-left: 14px; font-size: 12px; color: var(--text-2); letter-spacing: 0.04em; text-transform: uppercase; font-weight: 500;
  }
  .v2-tb-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 8px var(--accent); }
  .v2-titlebar-controls { display: flex; }
  .v2-titlebar-controls button {
    width: 46px; height: 36px; border: 0; background: transparent;
    color: var(--text-2); cursor: pointer; display: grid; place-items: center;
  }
  .v2-titlebar-controls button:hover { background: rgba(255,255,255,0.05); color: var(--text-1); }
  .v2-titlebar-controls button.close:hover { background: oklch(0.55 0.2 25); color: #fff; }

  /* Top hero strip */
  .v2-hero {
    padding: 28px 36px 24px;
    background: linear-gradient(180deg, var(--bg-1) 0%, transparent 100%);
    border-bottom: 1px solid var(--border);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 24px;
    align-items: end;
  }
  .v2-hero-left { min-width: 0; }
  .v2-eyebrow { font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent); font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
  .v2-eyebrow::before { content: ''; width: 18px; height: 1px; background: var(--accent); }
  .v2-h1 { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; margin: 0; }
  .v2-h1-num { color: var(--text-3); font-weight: 500; font-family: 'JetBrains Mono', monospace; }
  .v2-h2 { font-size: 16px; font-weight: 600; letter-spacing: -0.01em; margin: 0; }
  .v2-meta-line { display: flex; align-items: center; gap: 14px; margin-top: 12px; flex-wrap: wrap; font-size: 12px; color: var(--text-2); }
  .v2-meta-line strong { color: var(--text-1); font-weight: 500; }
  .v2-meta-line .sep { width: 3px; height: 3px; border-radius: 50%; background: var(--text-3); }

  /* Nav tabs */
  .v2-nav { display: flex; gap: 2px; padding: 0 36px; border-bottom: 1px solid var(--border); }
  .v2-nav-item {
    padding: 12px 18px;
    font-size: 13px; font-weight: 500; color: var(--text-2);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    display: flex; align-items: center; gap: 8px;
    transition: color .12s;
  }
  .v2-nav-item:hover { color: var(--text-1); }
  .v2-nav-item.active { color: var(--text-1); border-bottom-color: var(--accent); }
  .v2-nav-item .v2-count { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-3); background: rgba(255,255,255,0.04); padding: 1px 6px; border-radius: 3px; }
  .v2-nav-spacer { flex: 1; }

  /* Content area */
  .v2-content { flex: 1; min-height: 0; overflow: auto; padding: 24px 36px 36px; }

  /* Run form */
  .v2-run-strip {
    display: grid;
    grid-template-columns: 1.7fr 1fr auto;
    gap: 16px;
    align-items: end;
    margin-bottom: 24px;
  }
  .v2-field-label {
    font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--text-3); font-weight: 600; margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace;
  }
  .v2-input-wrap {
    display: flex; align-items: stretch; height: 40px;
    background: var(--bg-1);
    border: 1px solid var(--border-2);
    border-radius: 6px;
    transition: border-color .12s, background .12s;
  }
  .v2-input-wrap:focus-within { border-color: var(--accent); background: var(--bg-2); }
  .v2-input {
    flex: 1; min-width: 0; border: 0; outline: 0; padding: 0 14px;
    background: transparent; color: var(--text-1);
    font: 500 14px/1 'JetBrains Mono', monospace;
  }
  .v2-input::placeholder { color: var(--text-3); }
  .v2-input-prefix, .v2-input-suffix {
    display: flex; align-items: center; padding: 0 12px;
    color: var(--text-3); font: 500 12px 'JetBrains Mono', monospace;
    background: rgba(0,0,0,0.2);
  }
  .v2-input-prefix { border-right: 1px solid var(--border-2); border-top-left-radius: 5px; border-bottom-left-radius: 5px; }
  .v2-input-suffix { border-left: 1px solid var(--border-2); border-top-right-radius: 5px; border-bottom-right-radius: 5px; }
  .v2-browse-btn { background: transparent; border: 0; border-left: 1px solid var(--border-2); padding: 0 14px; color: var(--text-2); cursor: pointer; display: grid; place-items: center; }
  .v2-browse-btn:hover { color: var(--text-1); background: rgba(255,255,255,0.04); }

  /* Buttons */
  .v2-btn {
    height: 40px; padding: 0 22px;
    border-radius: 6px; border: 0; cursor: pointer;
    font: 600 13px 'Inter', sans-serif;
    letter-spacing: 0.01em;
    display: inline-flex; align-items: center; gap: 8px;
    transition: background .12s, color .12s, box-shadow .12s, transform .04s;
  }
  .v2-btn-primary {
    background: var(--accent); color: #1c1812;
    box-shadow: 0 1px 0 rgba(255,255,255,0.3) inset, 0 8px 24px -8px var(--accent);
  }
  .v2-btn-primary:hover { background: oklch(0.82 0.16 70); }
  .v2-btn-primary:active { transform: translateY(0.5px); }
  .v2-btn-primary:disabled { background: rgba(255,255,255,0.06); color: var(--text-3); cursor: not-allowed; box-shadow: none; }
  .v2-btn-secondary {
    background: rgba(255,255,255,0.05); color: var(--text-1);
    border: 1px solid var(--border-2);
  }
  .v2-btn-secondary:hover { background: rgba(255,255,255,0.08); }
  .v2-btn-ghost { background: transparent; color: var(--text-2); }
  .v2-btn-ghost:hover { color: var(--text-1); background: rgba(255,255,255,0.04); }
  .v2-btn-danger { background: transparent; color: var(--error); }
  .v2-btn-danger:hover { background: oklch(0.4 0.18 25 / 0.18); }
  .v2-btn-sm { height: 30px; padding: 0 12px; font-size: 12px; }
  .v2-kbd { font-family: 'JetBrains Mono', monospace; font-size: 11px; padding: 1px 5px; border-radius: 3px; background: rgba(0,0,0,0.3); color: var(--text-2); margin-left: 4px; }

  /* Workbook grid (denser, card-like rows) */
  .v2-section-h {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 12px;
    font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--text-3); font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
  }
  .v2-section-h::before { content: ''; width: 14px; height: 1px; background: var(--text-3); }
  .v2-section-h-count { background: rgba(255,255,255,0.04); color: var(--text-2); padding: 2px 8px; border-radius: 3px; }
  .v2-section-h-spacer { flex: 1; }

  .v2-wb-list { display: flex; flex-direction: column; gap: 6px; }
  .v2-wb-row {
    display: grid;
    grid-template-columns: 28px 1.6fr 0.9fr 0.9fr 1.2fr 80px;
    gap: 16px;
    align-items: center;
    padding: 14px 18px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 6px;
    transition: background .1s, border-color .1s;
    position: relative;
  }
  .v2-wb-row:hover { background: var(--bg-2); }
  .v2-wb-row.on { border-left: 2px solid var(--accent); padding-left: 17px; }
  .v2-wb-row.off { opacity: 0.45; }
  .v2-wb-fn { font: 500 14px 'JetBrains Mono', monospace; color: var(--text-1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .v2-wb-tabs { display: flex; flex-wrap: wrap; gap: 4px; }
  .v2-wb-tab {
    display: inline-flex; align-items: center;
    padding: 3px 8px; border-radius: 3px;
    background: rgba(255,255,255,0.05);
    font: 500 11px 'JetBrains Mono', monospace;
    color: var(--text-1);
  }
  .v2-wb-row.on .v2-wb-tab.target { background: var(--accent-bg); color: oklch(0.92 0.1 70); }
  .v2-wb-folder { font: 400 11.5px 'JetBrains Mono', monospace; color: var(--text-3); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; direction: rtl; text-align: left; }
  .v2-wb-stat { font: 500 11px 'JetBrains Mono', monospace; color: var(--text-3); text-align: right; }

  /* Checkbox */
  .v2-check {
    width: 18px; height: 18px; border-radius: 4px;
    border: 1.5px solid var(--text-3);
    display: grid; place-items: center; cursor: pointer;
    transition: background .12s, border-color .12s;
    background: transparent;
  }
  .v2-check:hover { border-color: var(--text-2); }
  .v2-check.on { background: var(--accent); border-color: var(--accent); color: #1c1812; }

  /* Pill */
  .v2-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 8px; border-radius: 4px;
    font: 600 10px 'JetBrains Mono', monospace;
    letter-spacing: 0.06em; text-transform: uppercase;
  }
  .v2-pill.ok { background: oklch(0.35 0.1 145 / 0.35); color: var(--success); }
  .v2-pill.warn { background: oklch(0.4 0.1 75 / 0.3); color: var(--warn); }
  .v2-pill.err { background: oklch(0.4 0.12 25 / 0.35); color: var(--error); }
  .v2-pill.muted { background: rgba(255,255,255,0.05); color: var(--text-3); }

  /* Run log */
  .v2-log {
    margin-top: 28px;
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }
  .v2-log-header {
    display: flex; align-items: center; gap: 14px;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(255,255,255,0.02), transparent);
  }
  .v2-log-row {
    display: grid;
    grid-template-columns: 24px 60px 1.4fr 1.6fr 80px;
    gap: 14px; align-items: center;
    padding: 12px 18px;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
  }
  .v2-log-row:last-child { border-bottom: 0; }
  .v2-log-ts { font: 400 11px 'JetBrains Mono', monospace; color: var(--text-3); }
  .v2-log-fn { font: 500 13px 'JetBrains Mono', monospace; color: var(--text-1); }
  .v2-log-msg { font-size: 12px; color: var(--text-2); }
  .v2-log-out { font: 400 11px 'JetBrains Mono', monospace; color: var(--accent); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  /* Modal */
  .v2-scrim { position: absolute; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: grid; place-items: center; z-index: 50; animation: v2-fade .14s ease; }
  @keyframes v2-fade { from { opacity: 0; } to { opacity: 1; } }
  .v2-modal {
    width: 540px;
    background: var(--bg-2);
    border: 1px solid var(--border-2);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 30px 80px -10px rgba(0,0,0,0.6);
    animation: v2-pop .14s cubic-bezier(.2,.7,.3,1.2);
  }
  @keyframes v2-pop { from { transform: scale(0.96) translateY(4px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
  .v2-modal-header { padding: 22px 24px 18px; border-bottom: 1px solid var(--border); }
  .v2-modal-eyebrow { font-size: 10px; letter-spacing: 0.16em; text-transform: uppercase; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; }
  .v2-modal-title { font-size: 18px; font-weight: 600; letter-spacing: -0.01em; margin: 0; }
  .v2-modal-sub { font-size: 13px; color: var(--text-2); margin-top: 8px; line-height: 1.55; }
  .v2-modal-body { padding: 18px 24px; }
  .v2-modal-footer { display: flex; gap: 8px; justify-content: flex-end; padding: 18px 24px; border-top: 1px solid var(--border); background: rgba(0,0,0,0.15); }

  /* Conflict list */
  .v2-conflict-list { background: #0f0e0b; border-radius: 6px; padding: 8px 12px; border: 1px solid var(--border); max-height: 180px; overflow: auto; }
  .v2-conflict-row { display: flex; align-items: center; gap: 10px; padding: 5px 0; font: 400 12.5px 'JetBrains Mono', monospace; color: var(--text-2); }
  .v2-conflict-row .v2-conflict-x { color: var(--warn); font-size: 11px; }

  /* Progress */
  .v2-progress-row { display: grid; grid-template-columns: 22px 1fr 70px; gap: 12px; align-items: center; padding: 9px 0; font-size: 13px; border-bottom: 1px solid var(--border); }
  .v2-progress-row:last-child { border-bottom: 0; }
  .v2-progress-fn { font: 500 13px 'JetBrains Mono', monospace; color: var(--text-1); }
  .v2-progress-state { font: 400 11px 'JetBrains Mono', monospace; color: var(--text-3); text-align: right; }
  .v2-spinner-2 { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.1); border-top-color: var(--accent); border-radius: 50%; animation: v2-spin .7s linear infinite; }
  @keyframes v2-spin { to { transform: rotate(360deg); } }
  .v2-bar { height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; margin-top: 16px; }
  .v2-bar-fill { height: 100%; background: var(--accent); transition: width .25s linear; }

  /* Empty state */
  .v2-empty {
    margin-top: 8px;
    padding: 56px 36px;
    background: var(--bg-1);
    border: 1px dashed var(--border-2);
    border-radius: 10px;
    text-align: center;
  }
  .v2-empty-icon { width: 56px; height: 56px; margin: 0 auto 18px; border-radius: 12px; background: var(--accent-bg); color: var(--accent); display: grid; place-items: center; }
  .v2-empty-h { font-size: 18px; font-weight: 600; margin: 0; }
  .v2-empty-p { color: var(--text-2); font-size: 13px; margin: 8px auto 20px; max-width: 460px; line-height: 1.55; }
  .v2-empty-actions { display: flex; gap: 10px; justify-content: center; }

  /* Settings */
  .v2-settings-grid { display: grid; grid-template-columns: 360px 1fr; gap: 24px; align-items: start; }
  .v2-set-list-card { background: var(--bg-1); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
  .v2-set-list-h { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border); }
  .v2-set-list-h-title { flex: 1; font-size: 12px; color: var(--text-2); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
  .v2-set-row {
    padding: 14px 16px; border-bottom: 1px solid var(--border); cursor: pointer;
    transition: background .1s; position: relative;
  }
  .v2-set-row:last-child { border-bottom: 0; }
  .v2-set-row:hover { background: var(--bg-2); }
  .v2-set-row.active { background: var(--bg-2); }
  .v2-set-row.active::before { content: ''; position: absolute; left: 0; top: 6px; bottom: 6px; width: 2px; background: var(--accent); }
  .v2-set-row-fn { font: 500 13px 'JetBrains Mono', monospace; color: var(--text-1); }
  .v2-set-row-folder { font: 400 11px 'JetBrains Mono', monospace; color: var(--text-3); margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .v2-set-row-mappings { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }

  .v2-set-detail { background: var(--bg-1); border: 1px solid var(--border); border-radius: 8px; padding: 24px 28px; }
  .v2-set-detail-h { font-size: 16px; font-weight: 600; margin: 0 0 4px; }
  .v2-set-divider { height: 1px; background: var(--border); margin: 22px 0; }
  .v2-set-mapping-row { display: grid; grid-template-columns: 1fr 28px 1fr 28px; gap: 8px; align-items: center; margin-bottom: 8px; }
  .v2-arrow { color: var(--text-3); display: grid; place-items: center; }

  /* Toast */
  .v2-toast { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); background: var(--bg-2); color: var(--text-1); padding: 12px 18px; border-radius: 6px; font-size: 13px; display: flex; align-items: center; gap: 10px; box-shadow: 0 12px 30px rgba(0,0,0,0.5); border: 1px solid var(--border-2); z-index: 60; animation: v2-toast-in .2s ease; }
  @keyframes v2-toast-in { from { transform: translate(-50%, 10px); opacity: 0; } to { transform: translate(-50%, 0); opacity: 1; } }

  .v2-root *::-webkit-scrollbar { width: 10px; height: 10px; }
  .v2-root *::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 5px; border: 2px solid transparent; background-clip: padding-box; }
  .v2-root *::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); background-clip: padding-box; border: 2px solid transparent; }
  .v2-root *::-webkit-scrollbar-track { background: transparent; }
`;

Object.assign(window, { V2_STYLES });
