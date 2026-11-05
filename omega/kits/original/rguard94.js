<script>/* ═══ RISK GUARD AND GROWTH BOT (v6.5.92) — rules that protect the account, a 100 USDT bot that follows them, automatic exports ═══
   Risk is what makes money; how it is sized, managed and learned from decides whether it does (in the spirit of Sharran
   Srivatsaa's teaching on risk). The rules: 0.5% of equity risked per trade (1% after 30 trades without a rule break), at
   most 2 open, no new trades after −2% in a UTC day or −5% in a week, a pause for review at 20% below the peak.
   1. Growth Bot (plan E17, md5 27f13c9a…): a paper account of 100 USDT, forward only, that takes every NEW climax-watch trade
      (grade A) and every NEW Daily Plan paper trade (grade C) under those rules — not frightened: every valid signal within
      the limits is taken. It only READS the signals' own records (net of their costs); it never changes a signal.
      Climax trades have no stop, so their risk counts against a 10% adverse move; Daily Plan trades risk the distance to
      their stop. Binance's 5 USDT minimum order is respected (a smaller trade is skipped and the reason recorded).
   2. My trades: a pre-trade check for real trades (the size that keeps risk inside the rule, the limits now) and a journal
      that counts rule breaks, kept separate from the strategy's results.
   3. Automatic exports: when Market Watch has 3 new full days, or the metals/forex download is complete, the Autopilot
      saves the research file (browsers may ask for a tap; the page keeps a one-tap button and a notification is sent).
   OMEGA places no orders. */
(function(){
  'use strict';
  var H = 3600e3, KB = 'omega_rguard_bot_v1', KM = 'omega_rguard_mine_v1', KX = 'omega_rguard_exports_v1';
  var RULES = { risk0:0.005, risk1:0.01, upgradeAfter:30, maxOpen:2, dayStop:0.02, weekStop:0.05, reviewDD:0.20, climaxMove:0.10, minNotional:5, fee:0.0008 };
  var ui = { msg:'', check:null, form:{ sym:'BTC', side:'long', entry:'', stop:'', size:'' } };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function load(k, d){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v && typeof v === 'object' ? v : d; }catch(e){ return d; } }
  function save(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function day(ms){ return Math.floor(ms/864e5); } function week(ms){ return Math.floor((ms/864e5 + 3)/7); }
  function usd(x){ return (x < 0 ? '−' : '') + '$' + Math.abs(x).toFixed(2); }
  function newAcct(eq){ return { eq:eq, peak:eq, start0:eq, startAt:Date.now(), open:[], closed:[], seen:{}, skips:[], curve:[[Date.now(), eq]], nClean:0, breaks:0, paused:false, primed:false }; }
  // ── the rules engine (pure) ──
  function limits(A, nowMs){ var d = day(nowMs), w = week(nowMs), dP = 0, wP = 0;
    A.closed.forEach(function(c){ if(day(c.at) === d) dP += c.pnl; if(week(c.at) === w) wP += c.pnl; });
    var dayLoss = dP < 0 ? -dP/(A.eq - dP) : 0, weekLoss = wP < 0 ? -wP/(A.eq - wP) : 0, dd = A.peak > 0 ? 1 - A.eq/A.peak : 0, risk = A.nClean >= RULES.upgradeAfter ? RULES.risk1 : RULES.risk0, why = null;
    var E = 1e-9; if(A.paused || dd >= RULES.reviewDD - E) why = 'paused for review: 20% below the peak'; else if(weekLoss >= RULES.weekStop - E) why = 'weekly stop: −5% this week'; else if(dayLoss >= RULES.dayStop - E) why = 'daily stop: −2% today'; else if(A.open.length >= RULES.maxOpen) why = 'two trades already open';
    return { risk:risk, dayLoss:dayLoss, weekLoss:weekLoss, dd:dd, open:A.open.length, blocked:why }; }
  // ── the Growth Bot ──
  function sources(){ var out = [], C = window.OMEGA_CLIMAX && window.OMEGA_CLIMAX.state ? (window.OMEGA_CLIMAX.state().trades || []) : [], D = load('omega_dplan_v1', { open:[], trades:[] });
    C.forEach(function(t){ if(t && t.sym != null && t.t != null) out.push({ key:'c|' + t.sym + '|' + t.t + '|' + t.e, src:'climax', sym:t.sym, side:'long', closed:t.status === 'closed', net:t.net }); });
    (D.open || []).forEach(function(t){ out.push({ key:'d|' + t.sym + '|' + t.h, src:'plan', sym:t.sym, side:t.side, closed:false, stopPct:Math.abs(t.entry - t.stop)/t.entry }); });
    (D.trades || []).forEach(function(t){ out.push({ key:'d|' + t.sym + '|' + t.h, src:'plan', sym:t.sym, side:t.side, closed:true, R:t.R }); });
    return out; }
  function step(A, list, nowMs){ nowMs = nowMs || Date.now(); var by = {}; list.forEach(function(s){ by[s.key] = s; });
    if(!A.primed){ list.forEach(function(s){ A.seen[s.key] = 1; }); A.primed = true; return A; }          // forward only: signals before the bot started are not taken
    list.forEach(function(s){ if(A.seen[s.key]) return; A.seen[s.key] = 1; var L = limits(A, nowMs);
      if(L.blocked){ A.skips.push({ key:s.key, sym:s.sym, why:L.blocked, at:nowMs }); A.skips = A.skips.slice(-200); return; }
      var risk$ = A.eq*L.risk, notional = s.src === 'climax' ? risk$/RULES.climaxMove : (s.stopPct > 0 ? risk$/s.stopPct : risk$/0.01);
      if(notional < RULES.minNotional){ A.skips.push({ key:s.key, sym:s.sym, why:'below Binance’s 5 USDT minimum order', at:nowMs }); return; }
      A.open.push({ key:s.key, src:s.src, sym:s.sym, side:s.side, risk:risk$, notional:notional, at:nowMs }); });
    A.open = A.open.filter(function(o){ var s = by[o.key], pnl = null;
      if(s && s.closed){ pnl = o.src === 'climax' ? o.notional*(+s.net || 0) : o.risk*(+s.R || 0); }
      else if(!s && nowMs - o.at > 7*24*H){ pnl = 0; }
      if(pnl == null) return true; A.eq += pnl; A.peak = Math.max(A.peak, A.eq); A.nClean++;
      A.closed.push({ key:o.key, src:o.src, sym:o.sym, side:o.side, pnl:Math.round(pnl*1e4)/1e4, R:Math.round(pnl/o.risk*1000)/1000, at:nowMs }); A.closed = A.closed.slice(-2000);
      A.curve.push([nowMs, Math.round(A.eq*1e4)/1e4]); A.curve = A.curve.slice(-2000); return false; });
    if(1 - A.eq/A.peak >= RULES.reviewDD - 1e-9) A.paused = true; return A; }
  function stats(A){ var c = A.closed, n = c.length, w = c.filter(function(x){ return x.pnl > 0; }).length, wk = {};
    c.forEach(function(x){ var k = week(x.at); wk[k] = (wk[k] || 0) + x.pnl; }); var xs = Object.keys(wk).map(function(k){ return wk[k]; }), m = xs.length ? xs.reduce(function(a, b){ return a + b; }, 0)/xs.length : 0, sd = xs.length > 1 ? Math.sqrt(xs.reduce(function(a, b){ return a + (b - m)*(b - m); }, 0)/(xs.length - 1)) : 0;
    return { n:n, wins:w, ret:A.eq/A.start0 - 1, t:sd > 0 ? m/(sd/Math.sqrt(xs.length)) : null, dd:1 - A.eq/A.peak, weeks:xs.length,
      byA:c.filter(function(x){ return x.src === 'climax'; }).reduce(function(a, x){ return a + x.pnl; }, 0), byC:c.filter(function(x){ return x.src === 'plan'; }).reduce(function(a, x){ return a + x.pnl; }, 0) }; }
  function runBot(){ var A = load(KB, null) || newAcct(100); A = step(A, sources()); save(KB, A); return A; }
  // ── my trades: the pre-trade check and the journal ──
  function preCheck(M, entry, stop, size, nowMs){ var L = limits(M, nowMs || Date.now()), dist = Math.abs(entry - stop)/entry, risk$ = size*dist, allowed$ = M.eq*L.risk, maxSize = dist > 0 ? allowed$/dist : 0, msgs = [], ok = true;
    if(!(entry > 0 && stop > 0 && size > 0) || dist <= 0) return { ok:false, msgs:['Enter an entry, a stop and a size.'] };
    if(L.blocked){ ok = false; msgs.push('Blocked: ' + L.blocked + '.'); }
    if(risk$ > allowed$*1.05){ ok = false; msgs.push('Too big: this risks ' + usd(risk$) + ' (' + (risk$/M.eq*100).toFixed(2) + '% of the account); the rule allows ' + usd(allowed$) + '. Use a size of ' + usd(maxSize) + ' or less.'); }
    if(size < RULES.minNotional) msgs.push('Under Binance’s 5 USDT minimum order: the exchange will refuse it.');
    var ER = window.OMEGA_REVIEW && window.OMEGA_REVIEW.eventRisk ? window.OMEGA_REVIEW.eventRisk(nowMs || Date.now()) : null; if(ER && ER.active) msgs.push(window.OMEGA_REVIEW.riskText(ER));   // v6.5.94: advice for real trades; the bot's rules are unchanged
    if(ok) msgs.push('Inside the rules: risk ' + usd(risk$) + ' (' + (risk$/M.eq*100).toFixed(2) + '%), stop ' + (dist*100).toFixed(2) + '% away. Largest allowed size ' + usd(maxSize) + '.');
    return { ok:ok, msgs:msgs, risk:risk$, maxSize:maxSize, dist:dist }; }
  function logTrade(M, t){ var c = preCheck(M, t.entry, t.stop, t.size); if(!c.ok) M.breaks = (M.breaks || 0) + 1;
    M.open.push({ id:Date.now() + '' + Math.floor(Math.random()*1e3), sym:t.sym, side:t.side, entry:t.entry, stop:t.stop, size:t.size, risk:c.risk || 0, breach:!c.ok, at:Date.now() }); return M; }
  function closeTrade(M, id, exit){ M.open = M.open.filter(function(o){ if(o.id !== id) return true; var d = o.side === 'short' ? -1 : 1, pnl = d*(exit - o.entry)/o.entry*o.size - RULES.fee*o.size;
      M.eq += pnl; M.peak = Math.max(M.peak, M.eq); if(!o.breach) M.nClean++; M.closed.push({ key:o.id, sym:o.sym, side:o.side, pnl:Math.round(pnl*1e4)/1e4, R:o.risk > 0 ? Math.round(pnl/o.risk*1000)/1000 : null, breach:o.breach, at:Date.now() }); M.curve.push([Date.now(), M.eq]); return false; }); return M; }
  // ── automatic research exports ──
  async function autoExport(){ var X = load(KX, { mw:{ done:[] }, fx:{ saved:false } }), out = [], MR = window.OMEGA_MREAD, W = window.OMEGA_WATCH, G = window.OMEGA_GOLDH;
    try{ var D = MR && MR._ && MR._.checkDays ? MR._.checkDays() : { good:[] }, good = D.good || [], fresh = good.filter(function(d){ return X.mw.done.indexOf(d) < 0; });
      if(W && W.exportData && fresh.length >= 3){ await W.exportData(7); X.mw.done = X.mw.done.concat(fresh); X.mw.at = Date.now(); out.push('Market Watch: saved 7 days (' + fresh.length + ' new full days)'); notify('Market Watch export saved', 'Send the omega-watch file in the research chat (plan E13). If no file appeared, tap Save on the Risk Guard page.'); }
      else out.push('Market Watch: ' + good.length + ' full day' + (good.length === 1 ? '' : 's') + ' recorded, ' + fresh.length + ' new (exports at 3 new)'); }catch(e){ out.push('Market Watch export: ' + (e.message || e)); }
    try{ if(G && G.state && G.SYMS){ var recs = G.state().recs || {}, all = G.SYMS.every(function(k){ return recs[k] && recs[k].done; });
      if(all && !X.fx.saved && G.save){ await G.save(); X.fx.saved = true; X.fx.at = Date.now(); out.push('metals and forex file saved'); notify('Metals and forex download complete', 'Send the omega-history-metals-fx1h file in the research chat (plans E4, E15).'); }
      else out.push(all ? (X.fx.saved ? 'metals and forex file already saved' : 'metals and forex: complete') : 'metals and forex: still downloading'); } }catch(e){ out.push('metals and forex export: ' + (e.message || e)); }
    save(KX, X); return out.join('; ') + '.'; }
  function notify(title, body){ try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('OMEGA: ' + title, { body:body }); }catch(e){} }
  // ── the page ──
  function curveSvg(A){ var c = A.curve.length > 1 ? A.curve : [[A.startAt, A.start0], [Date.now(), A.eq]], ys = c.map(function(p){ return p[1]; }).concat([A.start0]), lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys), pad = (hi - lo)*0.15 || 1; lo -= pad; hi += pad;
    var W = 360, Hh = 120, X = function(i){ return 6 + i/(c.length - 1)*(W - 12); }, Y = function(v){ return 6 + (hi - v)/(hi - lo)*(Hh - 12); };
    var pts = c.map(function(p, i){ return X(i).toFixed(1) + ',' + Y(p[1]).toFixed(1); }).join(' '), up = A.eq >= A.start0;
    return '<svg class="rg-curve" viewBox="0 0 ' + W + ' ' + Hh + '" role="img" aria-label="Growth Bot equity"><line x1="0" x2="' + W + '" y1="' + Y(A.start0).toFixed(1) + '" y2="' + Y(A.start0).toFixed(1) + '" stroke="var(--text-dim)" stroke-dasharray="4 4"/><polyline points="' + pts + '" fill="none" stroke="' + (up ? 'var(--bull)' : 'var(--bear)') + '" stroke-width="2"/><text x="6" y="' + (Y(A.start0) - 4).toFixed(1) + '" class="rg-ax">start ' + A.start0 + '</text></svg>'; }
  function limitRow(L){ return '<table class="mr-tab"><tr><td>Risk per trade now</td><td>' + (L.risk*100).toFixed(1) + '%</td></tr><tr><td>Open trades</td><td>' + L.open + ' of ' + RULES.maxOpen + '</td></tr><tr><td>Today / this week</td><td>' + (L.dayLoss > 0 ? '−' + (L.dayLoss*100).toFixed(1) + '%' : 'no loss') + ' / ' + (L.weekLoss > 0 ? '−' + (L.weekLoss*100).toFixed(1) + '%' : 'no loss') + '</td></tr><tr><td>Below the peak</td><td>' + (L.dd*100).toFixed(1) + '%</td></tr><tr><td>New trades</td><td><b class="' + (L.blocked ? 'dn' : 'up') + '">' + (L.blocked ? 'not allowed: ' + esc(L.blocked) : 'allowed') + '</b></td></tr></table>'; }
  function html(){ var A = load(KB, null) || newAcct(100), M = load(KM, null) || newAcct(100), S = stats(A), LA = limits(A, Date.now()), LM = limits(M, Date.now()), X = load(KX, { mw:{ done:[] }, fx:{ saved:false } }), h = '';
    h += '<div class="mr-start"><h3>Start here</h3><p>Risk is what makes money; managing it decides whether it does. These rules are the same for the bot and for you: <b>0.5% risk per trade</b> (1% after 30 clean trades), <b>at most 2 open</b>, <b>stop for the day at −2%</b>, <b>for the week at −5%</b>, and a <b>pause for review at 20% below the peak</b>.</p><p>The Growth Bot follows the app’s signals on paper from 100 USDT, to show whether they can grow an account. Your own trades go through the pre-trade check below.</p></div>';
    h += '<div class="dp-card"><h3 class="dp-h">Growth Bot · paper · from 100 USDT</h3><div class="rg-big ' + (A.eq >= A.start0 ? 'up' : 'dn') + '">' + A.eq.toFixed(2) + ' USDT <span>(' + (S.ret >= 0 ? '+' : '') + (S.ret*100).toFixed(2) + '%)</span></div>' + curveSvg(A) +
      '<p class="dp-p">' + (S.n ? S.n + ' trades, ' + Math.round(100*S.wins/S.n) + '% winners · climax (grade A) ' + usd(S.byA) + ' · Daily Plan (grade C) ' + usd(S.byC) + (S.t != null ? ' · weekly t ' + S.t.toFixed(2) : '') : 'No trades yet: it takes signals that appear from now on.') + '</p>' + limitRow(LA) +
      (A.open.length ? '<p class="hint">Open: ' + A.open.map(function(o){ return esc(o.sym.replace('USDT', '')) + ' ' + o.side + ' (' + (o.src === 'climax' ? 'A' : 'C') + ', risk ' + usd(o.risk) + ')'; }).join(', ') + '</p>' : '') +
      (A.skips.length ? '<p class="hint">Skipped by the rules: ' + A.skips.length + ' (latest: ' + esc(A.skips[A.skips.length-1].why) + ').</p>' : '') + (A.paused ? '<p><button class="btn-outline" type="button" data-rg="resume">Reviewed: resume the bot</button></p>' : '') +
      '<p class="hint">Judged once (plan E17) after 26 weeks or 50 trades: it grows if it ends above 100 with weekly t ≥ 1.65.</p></div>';
    h += '<div class="dp-card"><h3 class="dp-h">Before a real trade</h3><div class="rg-form"><input id="rgSym" placeholder="Coin (BTC)" value="' + esc(ui.form.sym) + '"><select id="rgSide"><option value="long"' + (ui.form.side === 'long' ? ' selected' : '') + '>Long</option><option value="short"' + (ui.form.side === 'short' ? ' selected' : '') + '>Short</option></select><input id="rgEntry" inputmode="decimal" placeholder="Entry" value="' + esc(ui.form.entry) + '"><input id="rgStop" inputmode="decimal" placeholder="Stop" value="' + esc(ui.form.stop) + '"><input id="rgSize" inputmode="decimal" placeholder="Size in USDT" value="' + esc(ui.form.size) + '"></div>' +
      '<p><button class="btn-outline" type="button" data-rg="check">Check it</button> <button class="btn-outline" type="button" data-rg="log">Log the trade</button></p>' + (ui.check ? '<p class="dp-p ' + (ui.check.ok ? 'up' : 'dn') + '">' + ui.check.msgs.map(esc).join(' ') + '</p>' : '') + limitRow(LM) +
      '<p class="hint">Account ' + M.eq.toFixed(2) + ' USDT · rule breaks ' + (M.breaks || 0) + ' · clean trades ' + M.nClean + '. <button class="btn-outline" type="button" data-rg="bal">Set balance</button></p>' +
      (M.open.length ? '<table class="mr-tab"><tr><th>Open</th><th>Entry / stop</th><th></th></tr>' + M.open.map(function(o){ return '<tr><td>' + esc(o.sym) + ' ' + o.side + (o.breach ? ' <span class="dn">(rule break)</span>' : '') + '</td><td>' + o.entry + ' / ' + o.stop + '</td><td><button class="btn-outline" type="button" data-rgclose="' + o.id + '">Close</button></td></tr>'; }).join('') + '</table>' : '') +
      (M.closed.length ? '<p class="hint">Closed: ' + M.closed.length + ', total ' + usd(M.closed.reduce(function(a, c){ return a + c.pnl; }, 0)) + ', of which rule breaks ' + usd(M.closed.filter(function(c){ return c.breach; }).reduce(function(a, c){ return a + c.pnl; }, 0)) + '.</p>' : '') + '</div>';
    h += '<div class="dp-card"><h3 class="dp-h">Research exports (automatic)</h3><p class="dp-p">Market Watch: exported after every 3 new full days (' + X.mw.done.length + ' day' + (X.mw.done.length === 1 ? '' : 's') + ' exported so far). Metals and forex: ' + (X.fx.saved ? 'saved' : 'saved when the download completes') + '. Browsers may ask for a tap; a notification is sent each time.</p><p><button class="btn-outline" type="button" data-rg="mw">Save Market Watch (7 days) now</button> <button class="btn-outline" type="button" data-rg="fx">Save metals and forex now</button></p><p class="hint">' + esc(ui.msg) + '</p></div>';
    return h; }
  function num(id){ var v = el(id); return v ? parseFloat(String(v.value).replace(',', '.')) : NaN; }
  function css(){ if(el('rgCss')) return; var st = document.createElement('style'); st.id = 'rgCss';
    st.textContent = '.rg-big{font-size:24px;font-weight:700;margin:2px 0 6px;}.rg-big span{font-size:14px;font-weight:600;}.rg-curve{width:100%;height:auto;display:block;background:var(--bg);border:1px solid var(--border);border-radius:8px;margin:4px 0 8px;}.rg-ax{font-size:9px;fill:var(--text-dim);}' +
      '.rg-form{display:grid;grid-template-columns:1fr 1fr;gap:6px;}.rg-form input,.rg-form select{min-width:0;padding:8px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:14px;}';
    document.head.appendChild(st); }
  function render(){ var host = el('rguardBody'); if(!host) return; css(); host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-rg]'), function(b){ var k = b.getAttribute('data-rg'); b.onclick = async function(){ var M = load(KM, null) || newAcct(100); if(el('rgEntry')) ui.form = { sym:el('rgSym').value, side:el('rgSide').value, entry:el('rgEntry').value, stop:el('rgStop').value, size:el('rgSize').value };
      if(k === 'check'){ ui.check = preCheck(M, num('rgEntry'), num('rgStop'), num('rgSize')); render(); }
      else if(k === 'log'){ var t = { sym:(el('rgSym').value || '').toUpperCase().trim() || '?', side:el('rgSide').value, entry:num('rgEntry'), stop:num('rgStop'), size:num('rgSize') }; ui.check = preCheck(M, t.entry, t.stop, t.size); if(t.entry > 0 && t.stop > 0 && t.size > 0){ save(KM, logTrade(M, t)); } render(); }
      else if(k === 'bal'){ var v = parseFloat(prompt('Account balance in USDT', M.eq.toFixed(2)) || ''); if(v > 0){ M.eq = v; M.peak = Math.max(v, M.peak); M.start0 = M.start0 || v; save(KM, M); render(); } }
      else if(k === 'resume'){ var A = load(KB, null); if(A){ A.paused = false; A.peak = A.eq; save(KB, A); } render(); }
      else if(k === 'mw'){ try{ await window.OMEGA_WATCH.exportData(7); ui.msg = 'Market Watch file saved.'; }catch(e){ ui.msg = 'Not saved: ' + (e.message || e); } render(); }
      else if(k === 'fx'){ try{ await window.OMEGA_GOLDH.save(); ui.msg = 'Metals and forex file saved.'; }catch(e){ ui.msg = 'Not saved: ' + (e.message || e); } render(); } }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-rgclose]'), function(b){ b.onclick = function(){ var v = parseFloat(prompt('Exit price', '') || ''); if(v > 0){ save(KM, closeTrade(load(KM, null) || newAcct(100), b.getAttribute('data-rgclose'), v)); render(); } }; }); }
  var JOBS = [
    { id:'rguard', lane:'live', prio:3, label:'Growth Bot: takes the app’s signals under the risk rules (paper, from 100 USDT)', what:'Every 15 minutes: takes new climax (A) and Daily Plan (C) trades within the rules — 0.5% risk, 2 open at most, daily −2% and weekly −5% stops — and books them as their records close (plan E17).', every:15*60e3,
      run: async function(){ var A = runBot(), S = stats(A), L = limits(A, Date.now()); render(); return 'Equity ' + A.eq.toFixed(2) + ' USDT (' + (S.ret >= 0 ? '+' : '') + (S.ret*100).toFixed(2) + '%), ' + A.open.length + ' open, ' + S.n + ' closed' + (L.blocked ? '; new trades blocked: ' + L.blocked : '') + '.'; } },
    { id:'autoexp', lane:'heavy', prio:1, label:'Automatic research exports (Market Watch, metals and forex)', what:'Every 2 hours: after 3 new full days of Market Watch, or when the metals/forex download completes, saves the research file and sends a notification.', every:2*3600e3,
      run: async function(){ var r = await autoExport(); render(); return r; } }];
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); JOBS.forEach(function(j){ if(!J.some(function(x){ return x.id === j.id; })) J.push(j); }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  window.OMEGA_RGUARD = { render:render, onShow:function(){ runBot(); render(); if(window.OMEGA_REVIEW) window.OMEGA_REVIEW.render(); }, RULES:RULES, JOBS:JOBS, _:{ limits:limits, step:step, stats:stats, preCheck:preCheck, logTrade:logTrade, closeTrade:closeTrade, newAcct:newAcct, sources:sources, autoExport:autoExport, html:html } };
})();
</script>
