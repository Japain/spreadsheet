// V1 "Quarterly" — App component with full state machine.

const { useState, useEffect, useRef, useMemo } = React;

function V1WindowChrome({ children, title = 'Quarterly — Workbook Updater' }) {
  return (
    <div className="v1-root">
      <div className="v1-titlebar">
        <div className="v1-titlebar-title">
          <IcExcel size={14} />
          <span>{title}</span>
        </div>
        <div className="v1-titlebar-controls">
          <button title="Minimize">
            <svg width="11" height="11" viewBox="0 0 11 11"><path d="M0 5.5h11" stroke="currentColor"/></svg>
          </button>
          <button title="Maximize">
            <svg width="11" height="11" viewBox="0 0 11 11"><rect x="0.5" y="0.5" width="10" height="10" fill="none" stroke="currentColor"/></svg>
          </button>
          <button className="close" title="Close">
            <svg width="11" height="11" viewBox="0 0 11 11"><path d="M0 0l11 11M11 0L0 11" stroke="currentColor"/></svg>
          </button>
        </div>
      </div>
      {children}
    </div>
  );
}

function V1Sidebar({ view, setView }) {
  const items = [
    { id: 'main', label: 'Run', icon: <IcHome /> },
    { id: 'settings', label: 'Configure', icon: <IcGear /> },
    { id: 'history', label: 'Run history', icon: <IcHistory /> },
  ];
  return (
    <aside className="v1-sidebar">
      <div className="v1-side-brand">
        <div className="v1-side-mark">Q</div>
        <div>
          <div className="v1-side-brand-name">Quarterly</div>
          <div className="v1-side-brand-sub">Workbook Updater</div>
        </div>
      </div>
      <div className="v1-side-section">Workspace</div>
      {items.map(it => (
        <div key={it.id} className={'v1-side-item ' + (view === it.id ? 'active' : '')} onClick={() => setView(it.id)}>
          {it.icon}
          <span>{it.label}</span>
        </div>
      ))}
      <div className="v1-side-spacer" />
      <div className="v1-side-footer">
        <div>Project: <strong style={{color:'#2a2d35'}}>FP&amp;A Quarterly</strong></div>
        <div>Config: %USERPROFILE%\.quarterly\config.json</div>
        <div>v1.2.0 · Build 4421</div>
      </div>
    </aside>
  );
}

function V1Check({ on, onClick }) {
  return (
    <div className={'v1-check ' + (on ? 'on' : '')} onClick={onClick} role="checkbox" aria-checked={on}>
      {on && <IcCheck size={12} />}
    </div>
  );
}

function V1RunBar({ inputFile, setInputFile, suffix, setSuffix, onRun, canRun }) {
  return (
    <div className="v1-card v1-runbar" style={{marginTop: 16}}>
      <div className="v1-field">
        <div className="v1-label">Master input file</div>
        <div className="v1-input-wrap">
          <input className="v1-input" value={inputFile} onChange={e => setInputFile(e.target.value)} placeholder="Master_Q1_2026.xlsx"/>
          <button className="v1-browse-btn" title="Browse… (opens at configured input folder)">
            <IcFolder size={14}/>
          </button>
        </div>
      </div>
      <div className="v1-field">
        <div className="v1-label">Output suffix</div>
        <div className="v1-input-wrap">
          <span className="v1-input-suffix" style={{borderLeft:0, borderRight:'1px solid rgba(0,0,0,0.06)'}}>_</span>
          <input className="v1-input" value={suffix} onChange={e => setSuffix(e.target.value)} placeholder="v2_052526"/>
          <span className="v1-input-suffix">.xlsx</span>
        </div>
      </div>
      <button className="v1-btn v1-btn-primary" onClick={onRun} disabled={!canRun} title={canRun ? 'Start run' : 'Enter input file, suffix, and select at least one workbook'}>
        <IcPlay/>
        Run
      </button>
    </div>
  );
}

function V1WorkbookTable({ workbooks, setWorkbooks }) {
  const toggle = (id) => setWorkbooks(wbs => wbs.map(w => w.id === id ? {...w, run: !w.run} : w));
  const toggleAll = () => {
    const allOn = workbooks.every(w => w.run);
    setWorkbooks(wbs => wbs.map(w => ({...w, run: !allOn})));
  };
  const allOn = workbooks.length > 0 && workbooks.every(w => w.run);
  const selectedCount = workbooks.filter(w => w.run).length;
  return (
    <div className="v1-card v1-table-card">
      <div className="v1-table-header">
        <div onClick={toggleAll} style={{cursor:'pointer', display:'flex', alignItems:'center'}}>
          <V1Check on={allOn} onClick={(e) => { e.stopPropagation(); toggleAll(); }}/>
        </div>
        <div>Workbook · {selectedCount}/{workbooks.length} selected</div>
        <div>Input tab(s)</div>
        <div>Target tab(s)</div>
        <div>Folder</div>
        <div></div>
      </div>
      <div className="v1-table-body">
        {workbooks.map(wb => (
          <div key={wb.id} className={'v1-row ' + (wb.run ? '' : 'unchecked')}>
            <V1Check on={wb.run} onClick={() => toggle(wb.id)}/>
            <div className="v1-fn"><span className="v1-fn-icon"><IcExcel size={18}/></span>{wb.filename}</div>
            <div className="v1-tabs">{wb.mappings.map((m,i) => <span key={i} className="v1-tab-chip">{m.input}</span>)}</div>
            <div className="v1-tabs">{wb.mappings.map((m,i) => <span key={i} className="v1-tab-chip">{m.target}</span>)}</div>
            <div className="v1-path" title={wb.folder}>{wb.folder}</div>
            <div></div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------- Conflict dialog ----------
function V1ConflictDialog({ conflicts, onCancel, onConfirm }) {
  return (
    <div className="v1-scrim" onClick={onCancel}>
      <div className="v1-modal" onClick={e => e.stopPropagation()}>
        <div className="v1-modal-header">
          <h2 className="v1-modal-title">
            <span style={{color:'oklch(0.55 0.13 70)'}}><IcWarn/></span>
            Existing files will be overwritten
          </h2>
          <div className="v1-modal-sub">
            {conflicts.length} output file{conflicts.length === 1 ? '' : 's'} already exist in the target folder with the suffix you entered. Continuing will overwrite them.
          </div>
        </div>
        <div className="v1-modal-body">
          <div style={{background:'rgba(0,0,0,0.025)', borderRadius:6, padding:'10px 12px', maxHeight:160, overflow:'auto'}}>
            {conflicts.map((c,i) => (
              <div key={i} style={{fontFamily:'Cascadia Mono, Consolas, monospace', fontSize:12, color:'#2a2d35', padding:'3px 0'}}>{c}</div>
            ))}
          </div>
          <div style={{fontSize:12, color:'#6b7080', marginTop:10}}>To avoid overwriting, cancel and change the suffix — e.g. add today's date or a version tag.</div>
        </div>
        <div className="v1-modal-footer">
          <button className="v1-btn v1-btn-secondary" onClick={onCancel}>Cancel &amp; change suffix</button>
          <button className="v1-btn v1-btn-primary" style={{background: 'oklch(0.52 0.16 30)'}} onClick={onConfirm}>Overwrite and continue</button>
        </div>
      </div>
    </div>
  );
}

// ---------- Progress dialog ----------
function V1ProgressDialog({ workbooks, progress }) {
  const total = workbooks.length;
  const done = progress.filter(p => p.state === 'done').length;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  return (
    <div className="v1-scrim">
      <div className="v1-modal" onClick={e => e.stopPropagation()}>
        <div className="v1-modal-header">
          <h2 className="v1-modal-title">Updating workbooks…</h2>
          <div className="v1-modal-sub">{done} of {total} complete · do not edit target files while running</div>
        </div>
        <div className="v1-modal-body">
          <ul className="v1-progress-list">
            {workbooks.map((wb, i) => {
              const state = progress[i]?.state || 'pending';
              return (
                <li key={wb.id} className="v1-progress-row">
                  <div className="v1-progress-fname">
                    {state === 'running' && <span className="v1-spinner"/>}
                    {state === 'done' && <span style={{color:'oklch(0.5 0.16 145)'}}><IcCheck size={16}/></span>}
                    {state === 'pending' && <span style={{width:16, height:16, display:'inline-block', border:'1.5px dashed rgba(0,0,0,0.18)', borderRadius:'50%'}}/>}
                    {wb.filename}
                  </div>
                  <div style={{fontSize:12, color:'#6b7080'}}>
                    {state === 'running' && 'writing…'}
                    {state === 'done' && `${progress[i].rows} rows`}
                    {state === 'pending' && 'queued'}
                  </div>
                </li>
              );
            })}
          </ul>
          <div className="v1-bar"><div className="v1-bar-fill" style={{width: pct + '%'}}/></div>
        </div>
        <div className="v1-modal-footer">
          <button className="v1-btn v1-btn-ghost" disabled style={{opacity:0.5}}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

// ---------- Log panel ----------
function V1LogPanel({ results, suffix, onCopyLog, onDismiss }) {
  const counts = {
    success: results.filter(r => r.status === 'success').length,
    skipped: results.filter(r => r.status === 'skipped').length,
    error: results.filter(r => r.status === 'error').length,
  };
  const ts = '2026-05-25 14:32:08';
  return (
    <div className="v1-card v1-log-card">
      <div className="v1-log-header">
        <div className="v1-log-title">
          <IcHistory/>
          <span>Run complete</span>
          <span style={{color:'#6b7080', fontWeight:400}}>· {ts} · suffix _{suffix}</span>
        </div>
        <span className="v1-pill success">{counts.success} ok</span>
        {counts.skipped > 0 && <span className="v1-pill warn">{counts.skipped} skipped</span>}
        {counts.error > 0 && <span className="v1-pill error">{counts.error} error</span>}
        <button className="v1-btn v1-btn-secondary v1-btn-sm" onClick={onCopyLog}><IcCopy/> Copy log</button>
        <button className="v1-btn v1-btn-ghost v1-btn-sm" onClick={onDismiss} title="Dismiss"><IcX/></button>
      </div>
      <div className="v1-log-body">
        {results.map(r => (
          <div key={r.id} className="v1-log-row">
            <div>
              {r.status === 'success' && <span style={{color:'oklch(0.5 0.16 145)'}}><IcCheck size={16}/></span>}
              {r.status === 'skipped' && <span style={{color:'oklch(0.55 0.13 70)'}}><IcWarn size={16}/></span>}
              {r.status === 'error' && <span style={{color:'oklch(0.55 0.18 25)'}}><IcX size={16}/></span>}
            </div>
            <div>
              <div style={{fontWeight:600}}>{r.filename}</div>
              <div className="v1-log-msg">{r.message}</div>
            </div>
            <div className="v1-log-out" title={r.output || ''}>{r.output ? '→ ' + r.output : '—'}</div>
            <div style={{fontSize:11.5, color:'#6b7080', fontFamily:'Cascadia Mono, Consolas, monospace'}}>{r.rowsWritten ? r.rowsWritten + ' rows' : ''}</div>
            <div style={{fontSize:11.5, color:'#6b7080', textAlign:'right'}}>{r.durationMs ? (r.durationMs/1000).toFixed(2) + 's' : ''}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------- Empty state ----------
function V1EmptyState({ onAdd }) {
  return (
    <div className="v1-card v1-empty" style={{marginTop:16, flex:1}}>
      <div className="v1-empty-card">
        <div className="v1-empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M3 7a2 2 0 012-2h3.6l2 2H19a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" stroke="currentColor" strokeWidth="1.6"/>
          </svg>
        </div>
        <h3 className="v1-empty-h">No target workbooks configured</h3>
        <p className="v1-empty-p">
          Quarterly copies sheets from your master input file into pre-configured target workbooks. Add the first one to get started — you can map up to two tabs per workbook.
        </p>
        <div className="v1-empty-actions">
          <button className="v1-btn v1-btn-primary" onClick={onAdd}><IcPlus/> Add target workbook</button>
          <button className="v1-btn v1-btn-secondary">Import from config.json</button>
        </div>
      </div>
    </div>
  );
}

// ---------- Settings view ----------
function V1Settings({ workbooks, setWorkbooks, inputFolder, setInputFolder, onBack }) {
  const [selectedId, setSelectedId] = useState(workbooks[0]?.id || null);
  const selected = workbooks.find(w => w.id === selectedId) || null;

  const updateSelected = (patch) => {
    setWorkbooks(wbs => wbs.map(w => w.id === selectedId ? {...w, ...patch} : w));
  };
  const updateMapping = (idx, key, val) => {
    if (!selected) return;
    const next = [...selected.mappings];
    next[idx] = {...next[idx], [key]: val};
    updateSelected({ mappings: next });
  };
  const addMapping = () => {
    if (!selected || selected.mappings.length >= 2) return;
    updateSelected({ mappings: [...selected.mappings, { input: '', target: '' }] });
  };
  const removeMapping = (idx) => {
    if (!selected) return;
    updateSelected({ mappings: selected.mappings.filter((_,i) => i !== idx) });
  };
  const addWorkbook = () => {
    const id = 'wb-' + Date.now();
    const nw = { id, filename: 'New_Workbook_v1.xlsx', folder: inputFolder, mappings: [{ input: '', target: '' }], run: true };
    setWorkbooks([...workbooks, nw]);
    setSelectedId(id);
  };
  const removeWorkbook = (id) => {
    const idx = workbooks.findIndex(w => w.id === id);
    const next = workbooks.filter(w => w.id !== id);
    setWorkbooks(next);
    setSelectedId(next[Math.max(0, idx - 1)]?.id || null);
  };

  return (
    <>
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
        <div>
          <h1 className="v1-h1">Configure</h1>
          <p className="v1-sub">Target workbooks and tab mappings persist between runs. Stored as JSON in <code style={{fontFamily:'Cascadia Mono, Consolas, monospace', background:'rgba(0,0,0,0.04)', padding:'1px 6px', borderRadius:4}}>~/.quarterly/config.json</code>.</p>
        </div>
        <button className="v1-btn v1-btn-secondary" onClick={onBack}>Back to run</button>
      </div>

      <div className="v1-card" style={{marginTop:16, padding:16, display:'flex', gap:24, alignItems:'flex-end'}}>
        <div className="v1-field" style={{flex:1}}>
          <div className="v1-label">Default input folder</div>
          <div className="v1-input-wrap">
            <input className="v1-input" value={inputFolder} onChange={e => setInputFolder(e.target.value)}/>
            <button className="v1-browse-btn"><IcFolder size={14}/></button>
          </div>
        </div>
        <div style={{fontSize:12, color:'#6b7080', paddingBottom:8}}>
          The file picker opens here, but you can browse anywhere.
        </div>
      </div>

      <div className="v1-card v1-set-grid" style={{marginTop:16, marginBottom:16}}>
        <div className="v1-set-list" style={{borderRight:'1px solid rgba(0,0,0,0.05)'}}>
          <div className="v1-set-list-header">
            <div className="v1-set-list-title">Target workbooks ({workbooks.length})</div>
            <button className="v1-btn v1-btn-secondary v1-btn-sm" onClick={addWorkbook}><IcPlus/> Add</button>
          </div>
          <div className="v1-set-list-body">
            {workbooks.map(wb => (
              <div key={wb.id} className={'v1-set-row ' + (wb.id === selectedId ? 'active' : '')} onClick={() => setSelectedId(wb.id)}>
                <IcExcel size={16}/>
                <div className="v1-set-row-info">
                  <div className="v1-set-fn">{wb.filename}</div>
                  <div className="v1-set-meta">{wb.folder}</div>
                  <div style={{display:'flex', gap:4, marginTop:6, flexWrap:'wrap'}}>
                    {wb.mappings.map((m,i) => <span key={i} className="v1-tab-chip">{m.input || '—'} → {m.target || '—'}</span>)}
                  </div>
                </div>
              </div>
            ))}
            {workbooks.length === 0 && (
              <div style={{padding:'40px 16px', textAlign:'center', color:'#9aa0ad', fontSize:12}}>
                No workbooks yet. Click <strong>Add</strong> to create one.
              </div>
            )}
          </div>
        </div>

        <div className="v1-set-detail">
          {!selected && (
            <div style={{color:'#9aa0ad', fontSize:13}}>Select a workbook to edit its mappings, or add a new one.</div>
          )}
          {selected && (
            <>
              <h3 className="v1-set-detail-h">Edit workbook</h3>
              <div className="v1-set-detail-sub">Up to two tab mappings per workbook.</div>

              <div className="v1-set-form-field">
                <div className="v1-label">Filename</div>
                <div className="v1-input-wrap">
                  <input className="v1-input" value={selected.filename} onChange={e => updateSelected({ filename: e.target.value })}/>
                </div>
              </div>
              <div className="v1-set-form-field">
                <div className="v1-label">Target folder</div>
                <div className="v1-input-wrap">
                  <input className="v1-input" value={selected.folder} onChange={e => updateSelected({ folder: e.target.value })}/>
                  <button className="v1-browse-btn"><IcFolder size={14}/></button>
                </div>
              </div>

              <div className="v1-set-divider"/>
              <div style={{display:'flex', alignItems:'center', marginBottom:10}}>
                <div className="v1-label" style={{flex:1}}>Tab mappings · {selected.mappings.length}/2</div>
                <button className="v1-btn v1-btn-ghost v1-btn-sm" onClick={addMapping} disabled={selected.mappings.length >= 2}><IcPlus/> Add mapping</button>
              </div>
              <div style={{display:'grid', gridTemplateColumns:'1fr 16px 1fr 24px', gap:8, fontSize:11, color:'#6b7080', marginBottom:4, paddingLeft:2}}>
                <div>Input tab (master)</div>
                <div></div>
                <div>Target tab (this workbook)</div>
                <div></div>
              </div>
              {selected.mappings.map((m,i) => (
                <div key={i} className="v1-set-mapping">
                  <div className="v1-input-wrap"><input className="v1-input" value={m.input} placeholder="e.g. Revenue" onChange={e => updateMapping(i,'input',e.target.value)}/></div>
                  <div className="v1-set-mapping-arrow"><IcArrow size={14}/></div>
                  <div className="v1-input-wrap"><input className="v1-input" value={m.target} placeholder="e.g. Q_Data" onChange={e => updateMapping(i,'target',e.target.value)}/></div>
                  <button className="v1-btn v1-btn-danger-ghost v1-btn-sm" style={{padding:'0 6px'}} onClick={() => removeMapping(i)} title="Remove mapping"><IcTrash/></button>
                </div>
              ))}

              <div className="v1-set-divider"/>
              <div style={{display:'flex', justifyContent:'flex-end'}}>
                <button className="v1-btn v1-btn-danger-ghost v1-btn-sm" onClick={() => removeWorkbook(selected.id)}><IcTrash/> Remove workbook</button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

// ---------- Main app ----------
function V1App({ initialEmpty = false }) {
  const [view, setView] = useState('main'); // main, settings, history
  const [workbooks, setWorkbooks] = useState(initialEmpty ? [] : DEFAULT_WORKBOOKS);
  const [inputFile, setInputFile] = useState(initialEmpty ? '' : DEFAULT_INPUT_FILENAME);
  const [inputFolder, setInputFolder] = useState(DEFAULT_INPUT_FOLDER);
  const [suffix, setSuffix] = useState(initialEmpty ? '' : DEFAULT_SUFFIX);
  const [runState, setRunState] = useState('idle'); // idle, conflict, running, done
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState([]);
  const [toast, setToast] = useState(null);

  const selectedWbs = workbooks.filter(w => w.run);
  const canRun = inputFile.trim() && suffix.trim() && selectedWbs.length > 0;

  const conflicts = useMemo(() => {
    // Pretend two of the selected workbooks already have an output with this suffix
    return selectedWbs.slice(0, 2).map(wb => wb.filename.replace(/\.xlsx$/, `_${suffix}.xlsx`));
  }, [selectedWbs, suffix]);

  const startRun = () => {
    if (!canRun) return;
    setRunState('conflict');
  };
  const confirmRun = () => {
    setRunState('running');
    setProgress(selectedWbs.map(() => ({ state: 'pending' })));
    // Simulate streaming progress
    selectedWbs.forEach((wb, i) => {
      setTimeout(() => {
        setProgress(p => p.map((row, j) => j === i ? { state: 'running' } : row));
      }, 200 + i * 600);
      setTimeout(() => {
        setProgress(p => p.map((row, j) => j === i ? { state: 'done', rows: 200 + i * 380 } : row));
      }, 800 + i * 600);
    });
    setTimeout(() => {
      setRunState('done');
      setResults(buildResults(workbooks, suffix));
    }, 1100 + selectedWbs.length * 600);
  };

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2200);
  };

  return (
    <V1WindowChrome>
      <div className="v1-body">
        <V1Sidebar view={view} setView={setView}/>
        <main className="v1-content">
          {view === 'main' && (
            <>
              <div style={{display:'flex', alignItems:'flex-end', justifyContent:'space-between'}}>
                <div>
                  <h1 className="v1-h1">Quarter-end run</h1>
                  <p className="v1-sub">Project · <strong style={{color:'#2a2d35'}}>FP&amp;A Quarterly</strong> · 6 target workbooks configured</p>
                </div>
                <div style={{display:'flex', gap:8}}>
                  <button className="v1-btn v1-btn-ghost v1-btn-sm" onClick={() => setView('history')}><IcHistory/> History</button>
                  <button className="v1-btn v1-btn-secondary v1-btn-sm" onClick={() => setView('settings')}><IcGear/> Configure</button>
                </div>
              </div>

              {workbooks.length === 0 ? (
                <V1EmptyState onAdd={() => { setView('settings'); }}/>
              ) : (
                <>
                  <V1RunBar
                    inputFile={inputFile} setInputFile={setInputFile}
                    suffix={suffix} setSuffix={setSuffix}
                    onRun={startRun} canRun={canRun}
                  />
                  <V1WorkbookTable workbooks={workbooks} setWorkbooks={setWorkbooks}/>
                  {results && (
                    <V1LogPanel results={results} suffix={suffix} onCopyLog={() => showToast('Log copied to clipboard')} onDismiss={() => setResults(null)}/>
                  )}
                  {!results && <div style={{height:16, flex:'0 0 16px'}}/>}
                </>
              )}
            </>
          )}

          {view === 'settings' && (
            <V1Settings
              workbooks={workbooks} setWorkbooks={setWorkbooks}
              inputFolder={inputFolder} setInputFolder={setInputFolder}
              onBack={() => setView('main')}
            />
          )}

          {view === 'history' && (
            <>
              <div style={{display:'flex', alignItems:'center', justifyContent:'space-between'}}>
                <div>
                  <h1 className="v1-h1">Run history</h1>
                  <p className="v1-sub">Last 30 runs. Logs persist to <code style={{fontFamily:'Cascadia Mono, Consolas, monospace', background:'rgba(0,0,0,0.04)', padding:'1px 6px', borderRadius:4}}>~/.quarterly/runs.log</code>.</p>
                </div>
                <button className="v1-btn v1-btn-secondary v1-btn-sm" onClick={() => setView('main')}>Back to run</button>
              </div>
              <div className="v1-card" style={{marginTop:16, overflow:'hidden'}}>
                {[
                  { ts: '2026-05-25 14:32:08', suffix: 'v2_052526', ok: 3, warn: 1, err: 1 },
                  { ts: '2026-05-25 11:04:51', suffix: 'v1_Test', ok: 4, warn: 0, err: 0 },
                  { ts: '2026-04-30 16:18:22', suffix: 'q1final_043026', ok: 6, warn: 0, err: 0 },
                  { ts: '2026-04-29 09:50:12', suffix: 'q1draft_042926', ok: 5, warn: 1, err: 0 },
                  { ts: '2026-02-01 17:11:03', suffix: 'eoq_020126', ok: 6, warn: 0, err: 0 },
                ].map((r,i) => (
                  <div key={i} style={{padding:'14px 16px', borderBottom:'1px solid rgba(0,0,0,0.04)', display:'grid', gridTemplateColumns:'180px 1fr auto', alignItems:'center', gap:16}}>
                    <div style={{fontFamily:'Cascadia Mono, Consolas, monospace', fontSize:12, color:'#4b4f5a'}}>{r.ts}</div>
                    <div style={{display:'flex', alignItems:'center', gap:8}}>
                      <span style={{fontWeight:600, fontSize:13}}>suffix _{r.suffix}</span>
                      <span style={{color:'#6b7080', fontSize:12}}>· Master_Q1_2026.xlsx</span>
                    </div>
                    <div style={{display:'flex', gap:6}}>
                      <span className="v1-pill success">{r.ok} ok</span>
                      {r.warn > 0 && <span className="v1-pill warn">{r.warn} skipped</span>}
                      {r.err > 0 && <span className="v1-pill error">{r.err} error</span>}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </main>
      </div>

      {runState === 'conflict' && (
        <V1ConflictDialog conflicts={conflicts} onCancel={() => setRunState('idle')} onConfirm={confirmRun}/>
      )}
      {runState === 'running' && (
        <V1ProgressDialog workbooks={selectedWbs} progress={progress}/>
      )}
      {toast && <div className="v1-toast"><IcCheck size={14}/>{toast}</div>}
    </V1WindowChrome>
  );
}

Object.assign(window, { V1App, V1WindowChrome });
