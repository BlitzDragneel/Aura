<script>/* ═══ GOLD HOURLY HISTORY (v6.5.84) — the next clean test: gold and silver hourly candles from Twelve Data ═══
   Why: every setup tested on crypto so far either failed a clean test or is too new to judge. Gold hourly history has never
   been used in any research round (round 11 used daily gold), so it can give one honest, one-shot test of the owner's
   5-unit method and the new method (plan E2, written and fingerprinted before any of this data exists).
   What it does: downloads XAU/USD and XAG/USD hourly candles (UTC) from Twelve Data with the key already set in OMEGA, 5,000
   hours a request, going back until Twelve Data has no more (or 2005), through the app's shared Twelve Data queue (7 a
   minute, counted against the day's allowance). Progress is kept on the phone (IndexedDB omega_goldh), so a stopped or
   interrupted download resumes where it stopped. Every candle is checked (numbers, high ≥ open/close ≥ low, one per hour).
   Saves one file in the research format (omega-history, tf 60, the same encoding as the other history files; metals have
   no volume at Twelve Data, so volume is 0). The key is used only in the requests; the file is checked for it and for any
   credential-like field before saving. OMEGA places no orders. */
(function(){
  'use strict';
  var SYMS = ['XAU/USD', 'XAG/USD'], H = 3600e3, DBN = 'omega_goldh', MAXPAGES = 40, OLDEST = Date.UTC(2005, 0, 1)/H;
  var WAIT = { gap:8500, retry:3000, limit:61000 };
  var state = { busy:false, stop:false, msg:'', recs:{}, err:null, saved:null };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function tdKey(){ var k = el('creedKey'); if(k && k.value && k.value.trim()) return k.value.trim(); try{ var s = localStorage.getItem('omega_td_key'); if(s) return s; }catch(e){} var a = el('apikey'); return (a && a.value) ? a.value.trim() : ''; }
  var lastTd = 0;
  async function gate(){ if(window.OMEGA_TD && typeof window.OMEGA_TD.acquire === 'function'){ await window.OMEGA_TD.acquire('history'); return; }
    var w = lastTd + WAIT.gap - Date.now(); if(w > 0) await sleep(w); lastTd = Date.now(); }
  function hourOf(dt){ var t = Date.parse(String(dt).trim().replace(' ', 'T') + (/[zZ]|[+-]\d\d:?\d\d$/.test(String(dt).trim()) ? '' : 'Z')); return isFinite(t) ? Math.round(t/H) : NaN; }
  function stamp(h){ return new Date(h*H).toISOString().slice(0, 19).replace('T', ' '); }
  function clean(msg){ return String(msg || 'error').replace(/apikey=[^&\s]+/gi, 'apikey=…').slice(0, 160); }
  // ── storage (resume) ──
  function idb(){ return new Promise(function(res, rej){ var q = indexedDB.open(DBN, 1); q.onupgradeneeded = function(){ var d = q.result; if(!d.objectStoreNames.contains('series')) d.createObjectStore('series', { keyPath:'sym' }); };
    q.onsuccess = function(){ res(q.result); }; q.onerror = function(){ rej(q.error); }; }); }
  var dbp = null; function db(){ return dbp || (dbp = idb()); }
  function tx(mode, fn){ return db().then(function(d){ return new Promise(function(res, rej){ var t = d.transaction('series', mode), s = t.objectStore('series'), out = fn(s);
    t.oncomplete = function(){ res(out && typeof out === 'object' && 'onsuccess' in out ? out.result : out); }; t.onerror = function(){ rej(t.error); }; t.onabort = function(){ rej(t.error); }; }); }); }
  function getRec(sym){ return tx('readonly', function(s){ return s.get(sym); }).catch(function(){ return null; }); }
  function putRec(r){ return tx('readwrite', function(s){ s.put(r); }).catch(function(){}); }
  function clearAll(){ return tx('readwrite', function(s){ s.clear(); }).catch(function(){}); }
  // ── checks and encoding (the research loader decodes this exactly) ──
  function guard(rows){ var hs = Object.keys(rows).map(Number).filter(isFinite).sort(function(a, b){ return a - b; }), out = { t:[], o:[], h:[], l:[], c:[], fixed:0, dropped:0 };
    hs.forEach(function(h){ var r = rows[h], o = +r[0], hi = +r[1], lo = +r[2], c = +r[3];
      if(!(o > 0 && hi > 0 && lo > 0 && c > 0) || !isFinite(o + hi + lo + c)){ out.dropped++; return; }
      var hh = Math.max(hi, o, c), ll = Math.min(lo, o, c); if(hh !== hi || ll !== lo) out.fixed++;
      out.t.push(h); out.o.push(o); out.h.push(hh); out.l.push(ll); out.c.push(c); }); return out; }
  function dpOf(x){ return x >= 100 ? 3 : x >= 1 ? 5 : 8; }
  function encode(sym, g){ var n = g.t.length, srt = g.c.slice().sort(function(a, b){ return a - b; }), med = srt[Math.floor(n/2)], dp = dpOf(med), sc = Math.pow(10, dp);
    var m = { sym:sym.replace('/', ''), src:'Twelve Data hourly (UTC)', dp:dp, n:n, t:[], c:[], o:[], h:[], l:[], v:[], tb:[] }, pt = 0, pc = 0;
    for(var i=0; i<n; i++){ var ci = Math.round(g.c[i]*sc), oi = Math.round(g.o[i]*sc), hi = Math.round(g.h[i]*sc), li = Math.round(g.l[i]*sc);
      m.t.push(i ? g.t[i] - pt : g.t[i]); pt = g.t[i]; m.c.push(i ? ci - pc : ci); pc = ci; m.o.push(oi - ci); m.h.push(Math.max(0, hi - Math.max(ci, oi))); m.l.push(Math.max(0, Math.min(ci, oi) - li)); m.v.push(0); m.tb.push(-1); }
    return m; }
  function decode(m){ var sc = Math.pow(10, -m.dp), t = 0, c = 0, out = { t:[], o:[], h:[], l:[], c:[] };
    for(var i=0; i<m.t.length; i++){ t += m.t[i]; c += m.c[i]; var o = c + m.o[i]; out.t.push(t); out.c.push(c*sc); out.o.push(o*sc); out.h.push((Math.max(c, o) + m.h[i])*sc); out.l.push((Math.min(c, o) - m.l[i])*sc); } return out; }
  // ── download one symbol, newest page first, resuming from what is stored ──
  async function series(sym, key, onMsg){ var rec = (await getRec(sym)) || { sym:sym, rows:{}, done:false, pages:0 };
    if(rec.done) return rec; var hs = Object.keys(rec.rows).map(Number), first = hs.length ? Math.min.apply(null, hs) : null, end = first != null ? stamp(first - 1) : null, pages = 0, limitHits = 0;
    while(pages < MAXPAGES && !state.stop){ await gate(); pages++;
      var url = 'https://api.twelvedata.com/time_series?symbol=' + encodeURIComponent(sym) + '&interval=1h&outputsize=5000&timezone=UTC' + (end ? '&end_date=' + encodeURIComponent(end) : '') + '&apikey=' + encodeURIComponent(key);
      var j = null; for(var a=0; a<3 && !j; a++){ try{ j = await (await fetch(url)).json(); }catch(e){ await sleep(WAIT.retry); } }
      if(!j) throw new Error('no answer from Twelve Data');
      if(j.status === 'error' || !Array.isArray(j.values)){ var em = clean(j.message || j.code);
        if(+j.code === 429 && !/day|daily/i.test(em) && limitHits < 3){ limitHits++; pages--; await sleep(WAIT.limit); continue; }
        if(+j.code === 429 || /day|daily/i.test(em)) throw new Error('Twelve Data’s allowance is used up for now (' + em + '). Press Download again later: it continues where it stopped.');
        if(!Object.keys(rec.rows).length) throw new Error(em);
        rec.done = true; break; }                                                   // older pages end with an error once the history is exhausted
      var vals = j.values, f = null, added = 0;
      vals.forEach(function(v){ var h = hourOf(v.datetime); if(!isFinite(h)) return; if(rec.rows[h] == null) added++; rec.rows[h] = [+v.open, +v.high, +v.low, +v.close]; if(f == null || h < f) f = h; });
      rec.pages = (rec.pages || 0) + 1; await putRec(rec);
      if(onMsg) onMsg(sym + ': ' + Object.keys(rec.rows).length + ' hours, back to ' + (f != null ? stamp(f).slice(0, 10) : '—'));
      if(vals.length < 5000 || f == null || f <= OLDEST || added === 0){ rec.done = true; break; }
      end = stamp(f - 1); }
    await putRec(rec); return rec; }
  async function run(){ if(state.busy){ state.stop = true; state.msg = 'Stopping after this request…'; render(); return 'stopping'; }
    state.busy = true; state.stop = false; state.err = null; state.saved = null; render();
    try{ var key = tdKey(); if(!key) throw new Error('no Twelve Data key is set in OMEGA (Settings)');
      for(var i=0; i<SYMS.length && !state.stop; i++){ var s = SYMS[i]; state.recs[s] = await series(s, key, function(t){ state.msg = (i + 1) + ' of ' + SYMS.length + ' — ' + t + '…'; render(); }); }
      state.msg = state.stop ? 'Stopped. Press Download to continue where it stopped.' : 'Done. Save the file and send it for plan E2.'; return state.msg; }
    catch(e){ state.err = clean(e && e.message || e); state.msg = 'Stopped: ' + state.err; return state.msg; }
    finally{ for(var q=0; q<SYMS.length; q++){ try{ var rr = await getRec(SYMS[q]); if(rr) state.recs[SYMS[q]] = rr; }catch(e){} } state.busy = false; state.stop = false; render(); } }
  async function build(){ var out = { format:'omega-history', v:1, tf:60, tunit:3600, exportedAt:new Date().toISOString(), src:'Twelve Data hourly candles (UTC), downloaded by OMEGA for plan E2; metals have no volume there', markets:[], checks:{}, skipped:[] };
    for(var i=0; i<SYMS.length; i++){ var s = SYMS[i], r = state.recs[s] || (await getRec(s)); if(!r || !Object.keys(r.rows).length){ out.skipped.push(s + ': not downloaded'); continue; }
      var g = guard(r.rows); if(g.t.length < 1000){ out.skipped.push(s + ': only ' + g.t.length + ' hours'); continue; }
      var gaps = 0; for(var k=1; k<g.t.length; k++) if(g.t[k] - g.t[k-1] > 72) gaps++;
      out.markets.push(encode(s, g)); out.checks[s.replace('/', '')] = { hours:g.t.length, from:stamp(g.t[0]), to:stamp(g.t[g.t.length - 1]), fixed:g.fixed, dropped:g.dropped, gapsOver72h:gaps, complete:!!r.done }; }
    return out; }
  async function save(){ var out = await build(); if(!out.markets.length) throw new Error('nothing downloaded yet');
    var txt = JSON.stringify(out), key = tdKey();
    if((key && key.length >= 8 && txt.indexOf(key) >= 0) || (window.__omegaLeak && window.__omegaLeak(txt))) throw new Error('refused: the file would contain a credential');
    var name = 'omega-history-gold1h-' + new Date().toISOString().slice(0, 10), blob;
    if(typeof CompressionStream !== 'undefined'){ var cs = new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip')); blob = await new Response(cs).blob(); name += '.json.gz'; }
    else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(url); a.remove(); }, 4000);
    state.saved = { name:name, bytes:blob.size, checks:out.checks }; render(); return state.saved; }
  async function refresh(){ for(var i=0; i<SYMS.length; i++){ var r = await getRec(SYMS[i]); if(r) state.recs[SYMS[i]] = r; } render(); }
  // ── the card (bottom of the Breakout Desk) ──
  function html(){ var key = tdKey(), rows = SYMS.map(function(s){ var r = state.recs[s]; if(!r) return '<li>' + s + ': not downloaded</li>'; var hs = Object.keys(r.rows).map(Number); if(!hs.length) return '<li>' + s + ': nothing yet</li>';
      var a = Math.min.apply(null, hs), b = Math.max.apply(null, hs); return '<li>' + s + ': <b>' + hs.length.toLocaleString() + '</b> hours, ' + stamp(a).slice(0, 10) + ' → ' + stamp(b).slice(0, 10) + (r.done ? ' (complete)' : ' (more to fetch)') + '</li>'; }).join('');
    var have = SYMS.some(function(s){ return state.recs[s] && Object.keys(state.recs[s].rows).length; });
    return '<div class="card bd-next" style="margin-top:14px;"><h2 style="color:var(--gold);">Next clean test: gold and silver hourly (plan E2)</h2>' +
      '<p class="hint" style="margin:0 0 8px;color:var(--text);">Gold hourly history has never been used in any research round, so it can give one honest test. The rules and the pass mark were written down and fingerprinted <b>before</b> this data exists: your 5-unit method and the new method, on a 72-hour breakout in US hours (no volume filter: metals have no volume at Twelve Data), a true 1% risk, 0.05% costs a side. Pass, for each method: the account ends above 100, beats 97.5% of 200 coin-flip accounts, and at least half the calendar years end positive. Run once; reported whatever happens.</p>' +
      '<ol class="hint" style="margin:0 0 8px;padding-left:18px;"><li>Press <b>Download</b> (about 20–40 requests through the shared Twelve Data queue; a few minutes; it resumes if stopped).</li><li>Press <b>Save file</b> and send the file in the next research session.</li></ol>' +
      (key ? '' : '<p class="hint" style="color:var(--amber);">No Twelve Data key is set in OMEGA yet (Settings), so the download cannot start.</p>') +
      '<ul class="hint" style="margin:0 0 6px;padding-left:18px;">' + rows + '</ul>' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;"><button class="btn-outline" type="button" data-goldh="run"' + (key ? '' : ' disabled') + '>' + (state.busy ? 'Stop' : 'Download gold & silver hourly') + '</button>' +
      '<button class="btn-outline" type="button" data-goldh="save"' + (have && !state.busy ? '' : ' disabled') + '>Save file</button>' + (have && !state.busy ? '<button class="btn-outline" type="button" data-goldh="clear">Start over</button>' : '') + '</div>' +
      (state.msg ? '<p class="hint" style="margin:8px 0 0;">' + esc(state.msg) + '</p>' : '') +
      (state.saved ? '<p class="hint" style="margin:6px 0 0;">Saved <b>' + esc(state.saved.name) + '</b> (' + Math.round(state.saved.bytes/1024) + ' KB). Checks: ' + Object.keys(state.saved.checks).map(function(k){ var c = state.saved.checks[k]; return k + ' ' + c.hours + ' hours, ' + c.from.slice(0, 10) + ' → ' + c.to.slice(0, 10) + ', ' + c.fixed + ' candles corrected, ' + c.dropped + ' dropped'; }).join('; ') + '.</p>' : '') +
      '<p class="hint" style="margin:6px 0 0;">The key is used only in the requests and is never written into the file; the file is checked for it before saving.</p></div>'; }
  function render(){ var host = el('goldhBody'); if(!host) return; host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-goldh]'), function(b){ var k = b.getAttribute('data-goldh');
      if(k === 'run') b.onclick = function(){ run(); };
      if(k === 'save') b.onclick = function(){ save().catch(function(e){ state.msg = 'Not saved: ' + clean(e && e.message || e); render(); }); };
      if(k === 'clear') b.onclick = function(){ clearAll().then(function(){ state.recs = {}; state.saved = null; state.msg = 'Cleared.'; render(); }); }; }); }
  var tries = 0, iv = setInterval(function(){ if(el('goldhBody')){ clearInterval(iv); refresh(); } else if(++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_GOLDH = { run:run, save:save, render:render, refresh:refresh, state:function(){ return state; }, SYMS:SYMS,
    _:{ hourOf:hourOf, guard:guard, encode:encode, decode:decode, build:build, series:series, html:html, setWait:function(w){ Object.assign(WAIT, w); } } };
})();
</script>
