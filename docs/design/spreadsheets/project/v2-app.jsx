// V2 "QX" — Bolder app component.

function V2Chrome({ children }) {
  return (
    <div className="v2-root">
      <div className="v2-titlebar">
        <div className="v2-titlebar-title">
          <span className="v2-tb-dot"/>
          <span>QX · Workbook Updater</span>
          <span style={{opacity:0.5}}>·</span>
          <span style={{fontFamily:'JetBrains Mono, monospace', textTransform:'none', letterSpacing:'normal'}}>FP&amp;A Quarterly</span>
        </div>
        <div className="v2-titlebar-controls">
          <button title="Minimize"><svg width="11" height="11" viewBox="0 0 11 11"><path d="M0 5.5h11" stroke="currentColor"/></svg></button>
          <button title="Maximize"><svg width="11" height="11" viewBox="0 0 11 11"><rect x="0.5" y="0.5" width="10" height="10" fill="none" stroke="currentColor"/></svg></button>
          <button className="close" title="Close"><svg width="11" height="11" viewBox="0 0 11 11"><path d="M0 0l11 11M11 0L0 11" stroke="currentColor"/></svg></button>
        </div>
      </div>
      {children}
    </div>
  );
}

function V2Check({ on, onClick }) {
  return (
    <div className={'v2-check ' + (on ? 'on' : '')} onClick={onClick}>
      {on && <IcCheck size={12}/>}
    </div>
  );
}

function V2RunStrip({ inputFile, setInputFile, suffix, setSuffix, onRun, canRun, selectedCount, totalCount }) {
  return (
    <div className="v2-run-strip">
      <div>
        <div className="v2-field-label">Master input file</div>
        <div className="v2-input-wrap">
          <span className="v2-input-prefix">~/FP&amp;A/Q1_2026/</span>
          <input className="v2-input" value={inputFile} onChange={e => setInputFile(e.target.value)} placeholder="Master_Q1_2026.xlsx"/>
          <button className="v2-browse-btn" title="Browse…"><IcFolder size={15}/></button>
        </div>
      </div>
      <div>
        <div className="v2-field-label">Output suffix</div>
        <div className="v2-input-wrap">
          <span className="v2-input-prefix">_</span>
          <input className="v2-input" value={suffix} onChange={e => setSuffix(e.target.value)} placeholder="v2_052526"/>
          <span className="v2-input-suffix">.xlsx</span>
        </div>
      </div>
      <button className="v2-btn v2-btn-primary" onClick={onRun} disabled={!canRun} style={{height:64, padding:'0 24px'}}>
        <IcPlay size={14}/>
        Run · {selectedCount}/{totalCount}
        <span className="v2-kbd" style={{background:'rgba(0,0,0,0.18)', color:'rgba(0,0,0,0.6)'}}>⌘↵</span>
      </button>
    </div>
  );
}

function V2WorkbookList({ workbooks, setWorkbooks }) {
  const toggle = (id) => setWorkbooks(wbs => wbs.map(w => w.id === id ? {...w, run: !w.run} : w));
  return (
    <div className="v2-wb-list">
      {workbooks.map((wb, i) => (
        <div key={wb.id} className={'v2-wb-row ' + (wb.run ? 'on' : 'off')}>
          <V2Check on={wb.run} onClick={() => toggle(wb.id)}/>
          <div>
            <div className="v2-wb-fn">{wb.filename}</div>
            <div style={{fontSize:11, color:'var(--text-3)', marginTop:3}}>
              {wb.mappings.length} tab mapping{wb.mappings.length === 1 ? '' : 's'} · ~{1200 + i * 230} rows last quarter
            </div>
          </div>
          <div className="v2-wb-tabs">{wb.mappings.map((m,i) => <span key={i} className="v2-wb-tab">{m.input}</span>)}</div>
          <div className="v2-wb-tabs">{wb.mappings.map((m,i) => <span key={i} className="v2-wb-tab target">{m.target}</span>)}</div>
          <div className="v2-wb-folder" title={wb.folder}>{wb.folder}</div>
          <div className="v2-wb-stat">{wb.run ? <span className="v2-pill ok">in run</span> : <span className="v2-pill muted">skip</span>}</div>
        </div>
      ))}
    </div>
  );
}

function V2ConflictDialog({ conflicts, suffix, onCancel, onConfirm }) {
  return (
    <div className="v2-scrim" onClick={onCancel}>
      <div className="v2-modal" onClick={e => e.stopPropagation()}>
        <div className="v2-modal-header">
          <div className="v2-modal-eyebrow" style={{color:'var(--warn)'}}>
            <IcWarn size={12}/> Pre-run conflict check
          </div>
          <h2 className="v2-modal-title">Overwrite {conflicts.length} existing file{conflicts.length === 1 ? '' : 's'}?</h2>
          <div className="v2-modal-sub">
            Output files matching suffix <span className="v2-mono" style={{color:'var(--text-1)'}}>_{suffix}</span> already exist in the target folders. Continuing will overwrite them in place.
          </div>
        </div>
        <div className="v2-modal-body">
          <div className="v2-conflict-list">
            {conflicts.map((c,i) => (
              <div key={i} className="v2-conflict-row">
                <span className="v2-conflict-x">●</span>
                <span style={{flex:1}}>{c}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="v2-modal-footer">
          <button className="v2-btn v2-btn-ghost v2-btn-sm" onClick={onCancel}>Cancel · change suffix</button>
          <button className="v2-btn v2-btn-primary v2-btn-sm" onClick={onConfirm} style={{height:36, padding:'0 18px'}}>Overwrite &amp; continue</button>
        </div>
      </div>
    </div>
  );
}

function V2ProgressDialog({ workbooks, progress }) {
  const total = workbooks.length;
  const done = progress.filter(p => p.state === 'done').length;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  return (
    <div className="v2-scrim">
      <div className="v2-modal" onClick={e => e.stopPropagation()}>
        <div className="v2-modal-header">
          <div className="v2-modal-eyebrow" style={{color:'var(--accent)'}}><span className="v2-spinner-2"/> Run in progress</div>
          <h2 className="v2-modal-title">Updating {total} workbooks</h2>
          <div className="v2-modal-sub">{done}/{total} complete · {pct}% · keep target files closed in Excel</div>
        </div>
        <div className="v2-modal-body">
          {workbooks.map((wb, i) => {
            const state = progress[i]?.state || 'pending';
            return (
              <div key={wb.id} className="v2-progress-row">
                <div>
                  {state === 'running' && <span className="v2-spinner-2"/>}
                  {state === 'done' && <span style={{color:'var(--success)'}}><IcCheck size={14}/></span>}
                  {state === 'pending' && <span style={{width:14, height:14, display:'inline-block', border:'1.5px dashed var(--text-3)', borderRadius:'50%'}}/>}
                </div>
                <div className="v2-progress-fn">{wb.filename}</div>
                <div className="v2-progress-state">
                  {state === 'pending' && 'queued'}
                  {state === 'running' && 'writing…'}
                  {state === 'done' && `${progress[i].rows} rows`}
                </div>
              </div>
            );
          })}
          <div className="v2-bar"><div className="v2-bar-fill" style={{width: pct + '%'}}/></div>
        </div>
      </div>
    </div>
  );
}

function V2LogPanel({ results, suffix, onCopy, onDismiss }) {
  const ok = results.filter(r => r.status === 'success').length;
  const partial = results.filter(r => r.status === 'partial').length;
  const err = results.filter(r => r.status === 'error').length;
  return (
    <div className="v2-log">
      <div className="v2-log-header">
        <div style={{flex:1, display:'flex', alignItems:'center', gap:12}}>
          <div className="v2-field-label" style={{margin:0, color:'var(--accent)'}}>Run · 14:32:08</div>
          <span style={{fontSize:13, fontWeight:600}}>{results.length} workbooks processed</span>
          <span style={{fontSize:12, color:'var(--text-3)'}}>· suffix <span className="v2-mono" style={{color:'var(--text-2)'}}>_{suffix}</span></span>
        </div>
        <span className="v2-pill ok">{ok} ok</span>
        {partial > 0 && <span className="v2-pill warn">{partial} partial</span>}
        {err > 0 && <span className="v2-pill err">{err} error</span>}
        <button className="v2-btn v2-btn-ghost v2-btn-sm" onClick={onCopy}><IcCopy size={13}/> Copy</button>
        <button className="v2-btn v2-btn-ghost v2-btn-sm" onClick={onDismiss}><IcX size={13}/></button>
      </div>
      {results.map(r => (
        <div key={r.id} className="v2-log-row">
          <div>
            {r.status === 'success' && <span style={{color:'var(--success)'}}><IcCheck size={14}/></span>}
            {r.status === 'partial' && <span style={{color:'var(--warn)'}}><IcWarn size={14}/></span>}
            {r.status === 'error' && <span style={{color:'var(--error)'}}><IcX size={14}/></span>}
          </div>
          <div className="v2-log-ts">{r.durationMs ? (r.durationMs/1000).toFixed(2) + 's' : '—'}</div>
          <div>
            <div className="v2-log-fn">{r.filename}</div>
            <div className="v2-log-msg">{r.message}</div>
          </div>
          <div className="v2-log-out" title={r.output || ''}>{r.output ? '↳ ' + r.output : '—'}</div>
          <div className="v2-log-ts" style={{textAlign:'right'}}>{r.rowsWritten ? r.rowsWritten + ' rows' : ''}</div>
        </div>
      ))}
    </div>
  );
}

function V2EmptyState({ onAdd }) {
  return (
    <div className="v2-empty">
      <div className="v2-empty-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
          <path d="M3 7a2 2 0 012-2h3.6l2 2H19a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" stroke="currentColor" strokeWidth="1.6"/>
        </svg>
      </div>
      <h3 className="v2-empty-h">No workbooks in this project yet</h3>
      <p className="v2-empty-p">
        Quarterly projects need at least one target workbook with a tab mapping. Add the first one — or paste an existing <span className="v2-mono" style={{color:'var(--text-1)'}}>config.json</span> to import a configuration from a previous quarter.
      </p>
      <div className="v2-empty-actions">
        <button className="v2-btn v2-btn-primary" onClick={onAdd}><IcPlus/> Add workbook</button>
        <button className="v2-btn v2-btn-secondary">Import config.json</button>
      </div>
    </div>
  );
}

function V2Settings({ workbooks, setWorkbooks, inputFolder, setInputFolder }) {
  const [selectedId, setSelectedId] = useState(workbooks[0]?.id || null);
  const selected = workbooks.find(w => w.id === selectedId) || null;
  const updateSelected = (patch) => setWorkbooks(wbs => wbs.map(w => w.id === selectedId ? {...w, ...patch} : w));
  const updateMapping = (idx, key, val) => {
    if (!selected) return;
    const next = [...selected.mappings]; next[idx] = {...next[idx], [key]: val};
    updateSelected({ mappings: next });
  };
  const addMapping = () => selected && selected.mappings.length < 2 && updateSelected({ mappings: [...selected.mappings, { input: '', target: '' }] });
  const removeMapping = (i) => selected && updateSelected({ mappings: selected.mappings.filter((_,j) => j !== i) });
  const addWb = () => {
    const id = 'wb-' + Date.now();
    setWorkbooks([...workbooks, { id, filename: 'New_Workbook_v1.xlsx', folder: inputFolder, mappings: [{ input: '', target: '' }], run: true }]);
    setSelectedId(id);
  };
  const removeWb = (id) => {
    const idx = workbooks.findIndex(w => w.id === id);
    const next = workbooks.filter(w => w.id !== id);
    setWorkbooks(next);
    setSelectedId(next[Math.max(0, idx-1)]?.id || null);
  };
  return (
    <>
      <div className="v2-section-h">Defaults<div className="v2-section-h-spacer"/></div>
      <div style={{background:'var(--bg-1)', border:'1px solid var(--border)', borderRadius:8, padding:18, marginBottom:28, display:'grid', gridTemplateColumns:'1fr 1fr', gap:18}}>
        <div>
          <div className="v2-field-label">Default input folder</div>
          <div className="v2-input-wrap">
            <input className="v2-input" value={inputFolder} onChange={e => setInputFolder(e.target.value)}/>
            <button className="v2-browse-btn"><IcFolder size={15}/></button>
          </div>
        </div>
        <div>
          <div className="v2-field-label">Config file</div>
          <div className="v2-input-wrap">
            <input className="v2-input" value="~/.quarterly/config.json" readOnly/>
            <button className="v2-browse-btn" title="Open in editor"><IcCopy size={14}/></button>
          </div>
        </div>
      </div>

      <div className="v2-section-h">
        Target workbooks
        <span className="v2-section-h-count">{workbooks.length}</span>
        <div className="v2-section-h-spacer"/>
        <button className="v2-btn v2-btn-secondary v2-btn-sm" onClick={addWb}><IcPlus/> New workbook</button>
      </div>
      <div className="v2-settings-grid">
        <div className="v2-set-list-card">
          <div className="v2-set-list-h">
            <div className="v2-set-list-h-title">workbooks</div>
            <span className="v2-pill muted">{workbooks.length}</span>
          </div>
          {workbooks.map(wb => (
            <div key={wb.id} className={'v2-set-row ' + (wb.id === selectedId ? 'active' : '')} onClick={() => setSelectedId(wb.id)}>
              <div className="v2-set-row-fn">{wb.filename}</div>
              <div className="v2-set-row-folder">{wb.folder}</div>
              <div className="v2-set-row-mappings">
                {wb.mappings.map((m,i) => <span key={i} className="v2-wb-tab" style={{fontSize:10.5}}>{m.input || '—'} → {m.target || '—'}</span>)}
              </div>
            </div>
          ))}
        </div>

        <div className="v2-set-detail">
          {!selected ? (
            <div style={{color:'var(--text-3)'}}>Select a workbook to edit.</div>
          ) : (
            <>
              <h3 className="v2-set-detail-h">Edit workbook</h3>
              <div style={{fontSize:12, color:'var(--text-3)', marginBottom:18}}>Settings persist to <span className="v2-mono" style={{color:'var(--text-2)'}}>config.json</span>.</div>

              <div style={{marginBottom:14}}>
                <div className="v2-field-label">Filename</div>
                <div className="v2-input-wrap">
                  <input className="v2-input" value={selected.filename} onChange={e => updateSelected({filename: e.target.value})}/>
                </div>
              </div>
              <div>
                <div className="v2-field-label">Target folder</div>
                <div className="v2-input-wrap">
                  <input className="v2-input" value={selected.folder} onChange={e => updateSelected({folder: e.target.value})}/>
                  <button className="v2-browse-btn"><IcFolder size={15}/></button>
                </div>
              </div>

              <div className="v2-set-divider"/>

              <div style={{display:'flex', alignItems:'center', marginBottom:12}}>
                <div className="v2-field-label" style={{margin:0, flex:1}}>Tab mappings · {selected.mappings.length}/2</div>
                <button className="v2-btn v2-btn-ghost v2-btn-sm" onClick={addMapping} disabled={selected.mappings.length >= 2}><IcPlus size={12}/> Add</button>
              </div>
              <div style={{display:'grid', gridTemplateColumns:'1fr 28px 1fr 28px', gap:8, marginBottom:6}}>
                <div className="v2-field-label" style={{margin:0}}>Input · master</div><div/>
                <div className="v2-field-label" style={{margin:0}}>Target · workbook</div><div/>
              </div>
              {selected.mappings.map((m,i) => (
                <div key={i} className="v2-set-mapping-row">
                  <div className="v2-input-wrap" style={{height:36}}><input className="v2-input" value={m.input} placeholder="e.g. Revenue" onChange={e => updateMapping(i,'input',e.target.value)}/></div>
                  <div className="v2-arrow"><IcArrow size={14}/></div>
                  <div className="v2-input-wrap" style={{height:36}}><input className="v2-input" value={m.target} placeholder="e.g. Q_Data" onChange={e => updateMapping(i,'target',e.target.value)}/></div>
                  <button className="v2-btn v2-btn-danger v2-btn-sm" style={{padding:'0 6px', height:30}} onClick={() => removeMapping(i)}><IcTrash size={13}/></button>
                </div>
              ))}

              <div className="v2-set-divider"/>
              <div style={{display:'flex', justifyContent:'flex-end'}}>
                <button className="v2-btn v2-btn-danger v2-btn-sm" onClick={() => removeWb(selected.id)}><IcTrash/> Remove workbook</button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

function V2App({ initialEmpty = false }) {
  const [view, setView] = useState('main');
  const [workbooks, setWorkbooks] = useState(initialEmpty ? [] : DEFAULT_WORKBOOKS);
  const [inputFile, setInputFile] = useState(initialEmpty ? '' : DEFAULT_INPUT_FILENAME);
  const [inputFolder, setInputFolder] = useState(DEFAULT_INPUT_FOLDER);
  const [suffix, setSuffix] = useState(initialEmpty ? '' : DEFAULT_SUFFIX);
  const [runState, setRunState] = useState('idle');
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState([]);
  const [toast, setToast] = useState(null);

  const selectedWbs = workbooks.filter(w => w.run);
  const canRun = inputFile.trim() && suffix.trim() && selectedWbs.length > 0;

  const conflicts = useMemo(
    () => selectedWbs.slice(0, 2).map(wb => wb.filename.replace(/\.xlsx$/, `_${suffix}.xlsx`)),
    [selectedWbs, suffix]
  );

  const startRun = () => canRun && setRunState('conflict');
  const confirmRun = () => {
    setRunState('running');
    setProgress(selectedWbs.map(() => ({ state: 'pending' })));
    selectedWbs.forEach((wb, i) => {
      setTimeout(() => setProgress(p => p.map((r,j) => j === i ? {state: 'running'} : r)), 250 + i * 500);
      setTimeout(() => setProgress(p => p.map((r,j) => j === i ? {state: 'done', rows: 240 + i * 410} : r)), 750 + i * 500);
    });
    setTimeout(() => {
      setRunState('done');
      setResults(buildResults(workbooks, suffix));
    }, 1000 + selectedWbs.length * 500);
  };

  const showToast = msg => { setToast(msg); setTimeout(() => setToast(null), 2200); };

  return (
    <V2Chrome>
      <div className="v2-hero">
        <div className="v2-hero-left">
          <div className="v2-eyebrow">{view === 'main' ? 'Quarter-end run' : view === 'settings' ? 'Configuration' : 'Run history'}</div>
          <h1 className="v2-h1">
            {view === 'main' && <>Q1 2026 <span className="v2-h1-num">/ run 014</span></>}
            {view === 'settings' && 'Project configuration'}
            {view === 'history' && 'Recent runs'}
          </h1>
          <div className="v2-meta-line">
            <span>Master · <strong className="v2-mono" style={{color:'var(--text-1)'}}>{inputFile || '—'}</strong></span>
            <span className="sep"/>
            <span>{workbooks.length} workbooks · {selectedWbs.length} selected for this run</span>
            <span className="sep"/>
            <span>Last run · <strong style={{color:'var(--text-1)'}}>11:04 today</strong></span>
          </div>
        </div>
        <div style={{display:'flex', flexDirection:'column', alignItems:'flex-end', gap:8}}>
          <div className="v2-pill ok" style={{padding:'4px 10px'}}>● Project linked</div>
          <div style={{fontSize:11, color:'var(--text-3)', fontFamily:'JetBrains Mono, monospace'}}>FP&amp;A · jpayne · Win 11</div>
        </div>
      </div>

      <div className="v2-nav">
        <div className={'v2-nav-item ' + (view === 'main' ? 'active' : '')} onClick={() => setView('main')}>
          <IcPlay size={11}/> Run
          <span className="v2-count">{selectedWbs.length}</span>
        </div>
        <div className={'v2-nav-item ' + (view === 'settings' ? 'active' : '')} onClick={() => setView('settings')}>
          <IcGear size={13}/> Configure
          <span className="v2-count">{workbooks.length}</span>
        </div>
        <div className={'v2-nav-item ' + (view === 'history' ? 'active' : '')} onClick={() => setView('history')}>
          <IcHistory size={13}/> History
          <span className="v2-count">14</span>
        </div>
        <div className="v2-nav-spacer"/>
        <div className="v2-nav-item" style={{color:'var(--text-3)', cursor:'default'}}>
          <span className="v2-mono" style={{fontSize:11}}>~/.quarterly/config.json</span>
        </div>
      </div>

      <div className="v2-content">
        {view === 'main' && (
          <>
            {workbooks.length === 0 ? (
              <V2EmptyState onAdd={() => setView('settings')}/>
            ) : (
              <>
                <V2RunStrip
                  inputFile={inputFile} setInputFile={setInputFile}
                  suffix={suffix} setSuffix={setSuffix}
                  onRun={startRun} canRun={canRun}
                  selectedCount={selectedWbs.length} totalCount={workbooks.length}
                />
                <div className="v2-section-h">
                  Target workbooks
                  <span className="v2-section-h-count">{workbooks.length}</span>
                  <div className="v2-section-h-spacer"/>
                  <span style={{fontSize:11, color:'var(--text-3)', textTransform:'none', letterSpacing:0, fontFamily:'JetBrains Mono, monospace'}}>
                    Click to toggle · {selectedWbs.length} in run
                  </span>
                </div>
                <V2WorkbookList workbooks={workbooks} setWorkbooks={setWorkbooks}/>

                {results && <V2LogPanel results={results} suffix={suffix} onCopy={() => showToast('Log copied to clipboard')} onDismiss={() => setResults(null)}/>}
              </>
            )}
          </>
        )}

        {view === 'settings' && (
          <V2Settings workbooks={workbooks} setWorkbooks={setWorkbooks} inputFolder={inputFolder} setInputFolder={setInputFolder}/>
        )}

        {view === 'history' && (
          <>
            <div className="v2-section-h">Recent runs<div className="v2-section-h-spacer"/></div>
            <div style={{display:'flex', flexDirection:'column', gap:6}}>
              {[
                { ts: '2026-05-25 14:32:08', suffix: 'v2_052526', ok: 3, warn: 1, err: 1, master: 'Master_Q1_2026.xlsx' },
                { ts: '2026-05-25 11:04:51', suffix: 'v1_Test', ok: 4, warn: 0, err: 0, master: 'Master_Q1_2026.xlsx' },
                { ts: '2026-04-30 16:18:22', suffix: 'q1final_043026', ok: 6, warn: 0, err: 0, master: 'Master_Q1_2026.xlsx' },
                { ts: '2026-04-29 09:50:12', suffix: 'q1draft_042926', ok: 5, warn: 1, err: 0, master: 'Master_Q1_2026.xlsx' },
                { ts: '2026-02-01 17:11:03', suffix: 'eoq_020126', ok: 6, warn: 0, err: 0, master: 'Master_Q4_2025.xlsx' },
              ].map((r,i) => (
                <div key={i} style={{display:'grid', gridTemplateColumns:'170px 1fr auto', alignItems:'center', gap:18, padding:'14px 18px', background:'var(--bg-1)', border:'1px solid var(--border)', borderRadius:6}}>
                  <div className="v2-log-ts">{r.ts}</div>
                  <div>
                    <div style={{fontSize:13, fontWeight:600}}><span className="v2-mono" style={{color:'var(--accent)'}}>_{r.suffix}</span></div>
                    <div className="v2-log-msg">{r.master}</div>
                  </div>
                  <div style={{display:'flex', gap:6}}>
                    <span className="v2-pill ok">{r.ok} ok</span>
                    {r.warn > 0 && <span className="v2-pill warn">{r.warn} partial</span>}
                    {r.err > 0 && <span className="v2-pill err">{r.err} err</span>}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {runState === 'conflict' && <V2ConflictDialog conflicts={conflicts} suffix={suffix} onCancel={() => setRunState('idle')} onConfirm={confirmRun}/>}
      {runState === 'running' && <V2ProgressDialog workbooks={selectedWbs} progress={progress}/>}
      {toast && <div className="v2-toast"><IcCheck size={13}/>{toast}</div>}
    </V2Chrome>
  );
}

Object.assign(window, { V2App });
