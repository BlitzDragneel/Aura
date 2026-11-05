<script>/* ═══ CAPITULATION WATCH (v6.5.72) — round 14's candidate rule, watched live on the research coins' perpetuals ═══
   v6.5.74: FAILED its final test on 19 Oct 2026 (324 untouched coins: −1.5% a year over the market, z −0.27); the watch
   is off by default and, switched on, only records. The rule (PLAN14, family 1; passed validation on 140 coins, z 3.04): at the close of
   an hour, a coin's hourly log return is 5 or more of its own standard deviations below zero (σ over the 168 hours
   before), and its perpetual's premium index closes at or below its 5th percentile of the 720 hours before (forced
   selling). Buy the perpetual at the next hour's open and close it 12 hours later. 20 slots of 5% of the account; a coin
   already held is not bought again; when more coins fire in one hour than slots are free, the deepest falls go first.
   Speed matters: in research, entering one hour late kept about 60% of the edge, four hours late none.
   Every signal is recorded on paper from 19 Oct 2026 and judged week by week against the market of the watched coins
   (alpha, Newey-West t), like the Edge Lab's shadow book. OMEGA places no orders. Runs while the app is open. */
(function(){
  'use strict';
  var FAPI = 'https://fapi.binance.com', DBN = 'omega_cap', KEEP = 950, H = 3600e3, CFG_KEY = 'omega_capwatch_cfg_v2';   // v6.5.74: off by default once the rule failed its final test
  var RULE = { k:5, q:0.05, hold:12, slots:20, w:0.05, cost:0.001, sigN:168, sigMin:120, prN:720, prMin:500, age:720 };
  var FREEZE_H = Date.UTC(2026, 9, 19)/H;   // the forward record counts decisions from this hour on
  var STATUS = 'FAILED';                     // CANDIDATE (final test pending) · EDGE (final test passed) · FAILED (final test failed) — v6.5.74: FAILED on 19 Oct 2026
  var EVIDENCE = { design:{ coins:25, alpha:9.43, z:2.70, c2x:8.36, trades:722, years:'6 of 7' }, valid:{ coins:140, alpha:19.36, z:3.04, bar:2.90, c2x:17.00, trades:1582, years:'6 of 7' },
    delay:[[0, 19.4, 3.04], [1, 11.8, 2.09], [2, 7.2, 1.31], [4, 2.3, 0.43]], meanTrade:1.57, win:60,
    final:{ coins:324, older:125, young:199, alpha:-1.49, z:-0.27, bar:1.645, c2x:-4.51, trades:2034, meanTrade:-0.19, y2025:-27.3, worst:-46.6, olderAlpha:4.18, olderZ:1.45, youngAlpha:-3.38, youngZ:-0.75 } };
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function cfg(){ try{ var v = JSON.parse(localStorage.getItem(CFG_KEY) || 'null'); return v && typeof v === 'object' ? v : { on:STATUS !== 'FAILED' }; }catch(e){ return { on:STATUS !== 'FAILED' }; } }
  function setCfg(v){ try{ localStorage.setItem(CFG_KEY, JSON.stringify(v)); }catch(e){} }

  // ── the rule's arithmetic, pure (the same as the research code: h14data.derive + run_events) ──
  // D = { syms, h0, c:[[]], o:[[]], pr:[[]], F:[[]], first:[] } — arrays per coin aligned on hours h0, h0+1, …; null = no bar
  function lr(c, i){ var a = c[i], b = c[i-1]; return (a > 0 && b > 0) ? Math.log(a/b) : null; }
  function sigmaAt(c, t){ var s = 0, s2 = 0, n = 0; for(var i = Math.max(1, t - RULE.sigN); i < t; i++){ var x = lr(c, i); if(x == null) continue; s += x; s2 += x*x; n++; }
    if(n < RULE.sigMin) return null; var m = s/n, v = (s2 - n*m*m)/(n - 1); return v > 0 ? Math.sqrt(v) : null; }
  function quantileAt(p, t, q){ var xs = []; for(var i = Math.max(0, t - RULE.prN); i < t; i++){ var x = p[i]; if(x != null && isFinite(x)) xs.push(x); }
    if(xs.length < RULE.prMin) return null; xs.sort(function(a, b){ return a - b; }); var pos = (xs.length - 1)*q, lo = Math.floor(pos), hi = Math.ceil(pos); return xs[lo] + (xs[hi] - xs[lo])*(pos - lo); }
  function zAt(D, j, t){ var c = D.c[j]; if(t < 1 || !(c[t] > 0) || D.first[j] == null || t < D.first[j] + RULE.age) return null; var x = lr(c, t); if(x == null) return null; var s = sigmaAt(c, t); return s ? x/s : null; }
  // the coins that fire at hour t (index into D), deepest first; needPr(j) can fetch premium on demand (async) — here pure
  function firesAt(D, t){ var out = [];
    for(var j=0; j<D.syms.length; j++){ var z = zAt(D, j, t); if(z == null || z > -RULE.k) continue; var p = D.pr[j]; if(!p || p[t] == null) continue; var q = quantileAt(p, t, RULE.q); if(q == null || !(p[t] <= q)) continue;
      out.push({ j:j, sym:D.syms[j], t:t, z:z, prem:p[t], q05:q }); }
    return out.sort(function(a, b){ return a.z - b.z || (a.j - b.j); }); }
  function lastIdx(c){ for(var i=c.length-1; i>=0; i--) if(c[i] > 0) return i; return -1; }
  // the book: decisions in hour order; returns trades with research P&L (before costs, funding included) once closed
  function book(D, fired, open0){ var open = (open0 || []).slice(), trades = [];
    var hours = Object.keys(fired).map(Number).sort(function(a, b){ return a - b; });
    hours.forEach(function(t){ var e = t + 1; open = open.filter(function(o){ return o.x >= e; }); var free = RULE.slots - open.length;
      fired[t].forEach(function(f){ if(free <= 0) return; if(open.some(function(o){ return o.sym === f.sym; })) return; var j = f.j, c = D.c[j], o = D.o[j];
        if(e < c.length && !(o[e] > 0 && c[e] > 0)) return;   // no bar to enter on (not yet known in live use: then it waits)
        var tr = { sym:f.sym, t:t, z:f.z, prem:f.prem, q05:f.q05, e:e, x:t + RULE.hold }; trades.push(tr); open.push(tr); free--; }); });
    trades.forEach(function(tr){ settle(D, tr); }); return trades; }
  function settle(D, tr){ var j = D.syms.indexOf(tr.sym); if(j < 0) return tr; var c = D.c[j], o = D.o[j], F = D.F[j] || [], L = lastIdx(c), x = Math.min(tr.x, L);
    if(!(tr.e < c.length && o[tr.e] > 0 && c[tr.e] > 0)) return tr;                         // entry bar not closed yet
    if(tr.x >= c.length && L < c.length - 72){ x = L; }                                     // no bars for 3 days (delisted): close at the last one
    else if(tr.x >= c.length){ tr.status = 'open'; tr.entry = o[tr.e]; var cl = null; for(var q = Math.min(L, c.length - 1); q >= tr.e; q--) if(c[q] > 0){ cl = c[q]; break; } tr.now = cl; tr.markRet = cl ? cl/o[tr.e] - 1 : null; return tr; }
    var r = c[tr.e]/o[tr.e] - 1, fu = 0, prev = c[tr.e];
    for(var h = tr.e + 1; h <= x; h++){ if(c[h] > 0){ r += c[h]/prev - 1; prev = c[h]; } fu += F[h] || 0; }
    tr.entry = o[tr.e]; tr.exit = prev; tr.fund = fu; tr.ret = r - fu; tr.net = tr.ret - 2*RULE.cost; tr.status = 'closed'; tr.xs = x; return tr; }
  // hourly P&L of the book (as a fraction of the account) and the equal-weight market, for forward weeks
  function hourlyPnl(D, trades, from, to){ var out = {}; trades.forEach(function(tr){ if(tr.status !== 'closed' && tr.status !== 'open') return; var j = D.syms.indexOf(tr.sym); if(j < 0) return; var c = D.c[j], o = D.o[j], F = D.F[j] || [], w = RULE.w;
      if(!(o[tr.e] > 0 && c[tr.e] > 0)) return; var add = function(h, v){ if(h < from || h >= to) return; out[h] = (out[h] || 0) + v; };
      add(tr.e, w*(c[tr.e]/o[tr.e] - 1) - w*RULE.cost); var prev = c[tr.e], end = Math.min(tr.xs != null ? tr.xs : tr.x, c.length - 1);
      for(var h = tr.e + 1; h <= end; h++){ var v = 0; if(c[h] > 0){ v += c[h]/prev - 1; prev = c[h]; } v -= (F[h] || 0); add(h, w*v); }
      if(tr.status === 'closed') add(tr.xs, -w*RULE.cost); });
    return out; }
  function marketPnl(D, from, to){ var out = {}; for(var h = Math.max(1, from); h < to; h++){ var s = 0, n = 0; for(var j=0; j<D.syms.length; j++){ var c = D.c[j]; if(D.first[j] == null || h - 1 < D.first[j] + RULE.age) continue; if(c[h] > 0 && c[h-1] > 0){ s += c[h]/c[h-1] - 1; n++; } } if(n) out[h] = s/n; } return out; }
  function weekOf(hAbs){ var d = Math.floor(hAbs/24), wd = (d + 4) % 7; return d + ((7 - wd) % 7); }   // the Sunday ending the week (day number)
  function nwT(x){ var E = window.OMEGA_EDGELIB; if(E && E.nwT) return E.nwT(x, 2); var n = x.length; if(n < 8) return null; var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g = e.reduce(function(a, v){ return a + v*v; }, 0)/n;
    for(var k=1; k<=2; k++){ var s = 0; for(var q=k; q<n; q++) s += e[q]*e[q-k]; g += 2*(1 - k/3)*s/(n - k); } return g > 0 ? m/Math.sqrt(g/n) : null; }
  function forward(D, trades, nowH){ var from = Math.max(FREEZE_H - D.h0, 1), to = Math.min(nowH - D.h0, D.c.reduce(function(a, c){ return Math.max(a, c.length); }, 0)), P = hourlyPnl(D, trades.filter(function(tr){ return tr.t + D.h0 >= FREEZE_H; }), from, to), M = marketPnl(D, from, to), wk = {};
    for(var h = from; h < to; h++){ var w = weekOf(h + D.h0); var x = wk[w] || (wk[w] = { x:0, m:0 }); x.x += P[h] || 0; x.m += M[h] || 0; }
    var thisWeek = weekOf(nowH), ks = Object.keys(wk).map(Number).filter(function(w){ return w < thisWeek; }).sort(function(a, b){ return a - b; });   // finished weeks only
    var xs = ks.map(function(k){ return wk[k].x; }), ms = ks.map(function(k){ return wk[k].m; }), n = xs.length;
    var closed = trades.filter(function(tr){ return tr.status === 'closed' && tr.t + D.h0 >= FREEZE_H; });
    var out = { weeks:n, trades:closed.length, meanNet: closed.length ? closed.reduce(function(a, tr){ return a + tr.net; }, 0)/closed.length : null, win: closed.length ? closed.filter(function(tr){ return tr.net > 0; }).length/closed.length : null };
    if(n >= 2){ var mx = xs.reduce(function(a, b){ return a + b; }, 0)/n, mm = ms.reduce(function(a, b){ return a + b; }, 0)/n, cv = 0, vm = 0; for(var i=0; i<n; i++){ cv += (xs[i] - mx)*(ms[i] - mm); vm += (ms[i] - mm)*(ms[i] - mm); }
      var b = vm > 0 ? cv/vm : 0, a = xs.map(function(x, i){ return x - b*ms[i]; }); out.beta = b; out.alpha = 52*a.reduce(function(s, v){ return s + v; }, 0)/n; out.z = n >= 8 ? nwT(a) : null; out.total = xs.reduce(function(s, v){ return s + v; }, 0); }
    return out; }

  // ── live data: one IndexedDB store of hourly perpetual bars per coin ──
  function open(){ return new Promise(function(res, rej){ var r = indexedDB.open(DBN, 1); r.onupgradeneeded = function(){ var d = r.result; if(!d.objectStoreNames.contains('coins')) d.createObjectStore('coins', { keyPath:'sym' }); if(!d.objectStoreNames.contains('meta')) d.createObjectStore('meta'); };
    r.onsuccess = function(){ res(r.result); }; r.onerror = function(){ rej(r.error); }; }); }
  var dbp = null; function db(){ return dbp || (dbp = open()); }
  function tx(store, mode, fn){ return db().then(function(d){ return new Promise(function(res, rej){ var t = d.transaction(store, mode), s = t.objectStore(store), out = fn(s);
    t.oncomplete = function(){ res(out && typeof out === 'object' && 'onsuccess' in out ? out.result : out); }; t.onerror = function(){ rej(t.error); }; t.onabort = function(){ rej(t.error); }; }); }); }
  function getAll(){ return tx('coins', 'readonly', function(s){ return s.getAll(); }); }
  function putCoin(r){ return tx('coins', 'readwrite', function(s){ s.put(r); }); }
  function getMeta(k){ return tx('meta', 'readonly', function(s){ return s.get(k); }); }
  function putMeta(k, v){ return tx('meta', 'readwrite', function(s){ s.put(v, k); }); }
  async function getJSON(url){ for(var a=0; a<4; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(15000*(a+1)); continue; } if(r.status === 400) return null; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 3) throw e; await sleep(1500*(a+1)); } } return null; }
  var state = { busy:false, last:null, msg:'', coins:0, fired:[], trades:[], fwd:null, err:null };
  async function perps(){ var m = await getMeta('perps'); if(m && Date.now() - m.at < 24*H) return m.map;
    var info = await getJSON(FAPI + '/fapi/v1/exchangeInfo'), map = {}; ((info && info.symbols) || []).forEach(function(x){ if(x.contractType === 'PERPETUAL' && x.quoteAsset === 'USDT' && x.status === 'TRADING') map[x.symbol] = +x.onboardDate || 0; });
    if(Object.keys(map).length) await putMeta('perps', { at:Date.now(), map:map }); return map; }
  function watchList(map){ var W = window.OMEGA_WIDE, L = W && W.list ? W.list() : []; return L.filter(function(s){ return map[s] != null; }); }
  // bring one coin's hourly bars up to the last closed hour (and keep the last KEEP hours)
  async function topUp(rec, sym, nowH){ var startH = rec && rec.c.length ? rec.h0 + rec.c.length : nowH - KEEP; if(startH < nowH - KEEP) startH = nowH - KEEP; if(startH >= nowH) return rec;
    var d = await getJSON(FAPI + '/fapi/v1/klines?symbol=' + sym + '&interval=1h&startTime=' + startH*H + '&limit=' + Math.min(1000, nowH - startH + 1)); if(!Array.isArray(d)) return rec;
    rec = rec || { sym:sym, h0:startH, o:[], c:[], v:[], tb:[], pr:{} };
    d.forEach(function(k){ var h = Math.round(+k[0]/H); if(h >= nowH || h < rec.h0) return; var i = h - rec.h0; while(rec.c.length < i) { rec.o.push(null); rec.c.push(null); rec.v.push(null); rec.tb.push(null); }
      if(i === rec.c.length){ rec.o.push(+k[1]); rec.c.push(+k[4]); rec.v.push(+k[5]); rec.tb.push(+k[5] > 0 ? +k[9]/+k[5] : null); } else { rec.o[i] = +k[1]; rec.c[i] = +k[4]; rec.v[i] = +k[5]; rec.tb[i] = +k[5] > 0 ? +k[9]/+k[5] : null; } });
    var cut = rec.c.length - KEEP; if(cut > 0){ ['o', 'c', 'v', 'tb'].forEach(function(f){ rec[f] = rec[f].slice(cut); }); rec.h0 += cut; }
    rec.at = Date.now(); return rec; }
  async function premiumAround(sym, tH){ var d = await getJSON(FAPI + '/fapi/v1/premiumIndexKlines?symbol=' + sym + '&interval=1h&startTime=' + (tH - RULE.prN)*H + '&endTime=' + ((tH + 1)*H - 1) + '&limit=' + (RULE.prN + 2)), out = {};
    (Array.isArray(d) ? d : []).forEach(function(k){ out[Math.round(+k[0]/H)] = +k[4]; }); return out; }
  async function fundingBetween(sym, aH, bH){ var d = await getJSON(FAPI + '/fapi/v1/fundingRate?symbol=' + sym + '&startTime=' + aH*H + '&endTime=' + ((bH + 1)*H - 1) + '&limit=1000'), out = {};
    (Array.isArray(d) ? d : []).forEach(function(x){ var h = Math.floor(+x.fundingTime/H); out[h] = (out[h] || 0) + (+x.fundingRate); }); return out; }
  function align(recs, map){ var h0 = Infinity, h1 = -Infinity; recs.forEach(function(r){ if(r.c.length){ h0 = Math.min(h0, r.h0); h1 = Math.max(h1, r.h0 + r.c.length); } }); if(!isFinite(h0)) return null;
    var D = { h0:h0, syms:[], c:[], o:[], pr:[], F:[], first:[] }, n = h1 - h0;
    recs.forEach(function(r){ var c = new Array(n).fill(null), o = new Array(n).fill(null), p = new Array(n).fill(null), F = new Array(n).fill(0); for(var i=0; i<r.c.length; i++){ c[r.h0 - h0 + i] = r.c[i]; o[r.h0 - h0 + i] = r.o[i]; }
      Object.keys(r.pr || {}).forEach(function(k){ var i = +k - h0; if(i >= 0 && i < n) p[i] = r.pr[k]; }); Object.keys(r.fund || {}).forEach(function(k){ var i = +k - h0; if(i >= 0 && i < n) F[i] = r.fund[k]; });
      var ob = map[r.sym]; D.syms.push(r.sym); D.c.push(c); D.o.push(o); D.pr.push(p); D.F.push(F); D.first.push(ob ? Math.floor(ob/H) - h0 : null); });
    return D; }
  function notify(title, body){ try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification(title, { body:body }); }catch(e){}
    try{ var A = window.OMEGA_ALERTS, c = JSON.parse(localStorage.getItem('omega_alerts_v1') || 'null'); if(A && A.push && c && c.url) A.push(title, body); }catch(e){} }
  // one check: top up every watched coin, find what fired on the hours not yet looked at, settle the book
  async function check(force){ if(state.busy) return 'busy'; if(!force && !cfg().on) return 'off'; state.busy = true; state.err = null; render();
    try{ var nowH = Math.floor(Date.now()/H), map = await perps(), list = watchList(map); if(!list.length) throw new Error('no coins to watch yet (the Edge Lab’s coin list is not ready)');
      var recs = await getAll(), byS = {}; (recs || []).forEach(function(r){ byS[r.sym] = r; }); var done = 0;
      for(var i=0; i<list.length; i++){ var s = list[i]; var r = byS[s]; if(r && r.h0 + r.c.length >= nowH){ done++; continue; }
        try{ r = await topUp(r, s, nowH); if(r){ byS[s] = r; await putCoin(r); } }catch(e){}
        done++; if(i % 10 === 0){ state.msg = 'Checking ' + done + ' of ' + list.length + ' perpetuals…'; render(); } await sleep(r && r.c.length > 50 ? 120 : 260); }
      var meta = (await getMeta('book')) || { lastH:null, trades:[], fired:[] }, recsL = list.map(function(s){ return byS[s]; }).filter(Boolean);
      var D = align(recsL, map); if(!D) throw new Error('no bars yet');
      var lastClosed = nowH - 1 - D.h0, fromT = meta.lastH != null ? Math.max(meta.lastH - D.h0 + 1, 1) : lastClosed; if(fromT < RULE.sigN + 2) fromT = RULE.sigN + 2;   // sigma needs the 168 hours before
      // which coins fall 5+ sigma on the new hours; their premium is fetched only then
      var fired = {};
      for(var t = fromT; t <= lastClosed; t++){ for(var j=0; j<D.syms.length; j++){ var z = zAt(D, j, t); if(z == null || z > -RULE.k) continue; var sym = D.syms[j], rr = byS[sym];
          if(!rr.pr || rr.pr[t + D.h0] == null){ var pm = await premiumAround(sym, t + D.h0); rr.pr = Object.assign(rr.pr || {}, pm); await putCoin(rr); Object.keys(pm).forEach(function(k){ var q = +k - D.h0; if(q >= 0 && q < D.pr[j].length) D.pr[j][q] = pm[k]; }); } }
        var f = firesAt(D, t); if(f.length) fired[t] = f; }
      // re-run the book on every decision since it started (the open trades carry over)
      var prevT = (meta.trades || []).map(function(x){ return Object.assign({}, x); }), openPrev = prevT.filter(function(x){ return x.t + 0 < fromT + D.h0; }).map(function(x){ return { sym:x.sym, x:x.x - D.h0 }; });
      var newT = book(D, fired, openPrev).map(function(tr){ tr.t += D.h0; tr.e += D.h0; tr.x += D.h0; return tr; });
      var all = prevT.concat(newT);
      // settle open trades now that more bars are known (funding fetched once, at the close)
      for(var q=0; q<all.length; q++){ var tr = all[q]; if(tr.status === 'closed') continue; var jj = D.syms.indexOf(tr.sym); if(jj < 0) continue;
        if(tr.x - D.h0 < D.c[jj].length && D.c[jj][tr.x - D.h0] != null && !tr.fundDone){ var fr = await fundingBetween(tr.sym, tr.e + 1, tr.x); var rr2 = byS[tr.sym]; rr2.fund = Object.assign(rr2.fund || {}, fr); await putCoin(rr2); Object.keys(fr).forEach(function(k){ var ii = +k - D.h0; if(ii >= 0 && ii < D.F[jj].length) D.F[jj][ii] = fr[k]; }); tr.fundDone = true; }
        var loc = { sym:tr.sym, t:tr.t - D.h0, e:tr.e - D.h0, x:tr.x - D.h0 }; settle(D, loc); ['status', 'entry', 'exit', 'fund', 'ret', 'net', 'now', 'markRet'].forEach(function(k){ if(loc[k] !== undefined) tr[k] = loc[k]; }); if(loc.xs != null) tr.xs = loc.xs + D.h0; }
      var newFired = []; Object.keys(fired).forEach(function(k){ fired[k].forEach(function(f){ newFired.push({ sym:f.sym, t:+k + D.h0, z:f.z, prem:f.prem, q05:f.q05, taken:newT.some(function(tr){ return tr.sym === f.sym && tr.t === +k + D.h0; }) }); }); });
      meta.trades = all.slice(-2000); meta.fired = (meta.fired || []).concat(newFired).slice(-500); meta.lastH = lastClosed + D.h0; meta.at = Date.now(); await putMeta('book', meta);
      if(STATUS !== 'FAILED') newT.filter(function(tr){ return tr.t === nowH - 1; }).forEach(function(tr){ notify('OMEGA capitulation signal: ' + tr.sym, 'Fell ' + (-tr.z).toFixed(1) + ' standard deviations in the last hour with the perpetual at a discount. Research rule: buy now, 5% of the account, close at ' + new Date((tr.x + 1)*H).toISOString().slice(11, 16) + ' UTC. Paper candidate (final test pending).'); });
      var Dg = Object.assign({}, D); var tl = all.map(function(tr){ return Object.assign({}, tr, { t:tr.t - D.h0, e:tr.e - D.h0, x:tr.x - D.h0, xs: tr.xs != null ? tr.xs - D.h0 : null }); });
      state.fwd = forward(Dg, tl, nowH); state.trades = all; state.fired = meta.fired; state.coins = list.length; state.last = Date.now(); state.lastH = meta.lastH;
      state.msg = 'Checked ' + list.length + ' perpetuals up to the hour ending ' + new Date((meta.lastH + 1)*H).toISOString().slice(11, 16) + ' UTC' + (newFired.length ? ': ' + newFired.length + ' fired.' : ': nothing fired.');
      return state.msg; }
    catch(e){ state.err = String(e && e.message || e); state.msg = 'Capitulation watch stopped: ' + state.err; return state.msg; }
    finally{ state.busy = false; render(); } }
  async function load(){ try{ var m = await getMeta('book'); if(m){ state.trades = m.trades || []; state.fired = m.fired || []; state.lastH = m.lastH; } }catch(e){} render(); }

  // ── the card ──
  function pct(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '') + (100*v).toFixed(d == null ? 2 : d) + '%'; }
  function hm(h){ return new Date(h*H).toISOString().slice(5, 16).replace('T', ' ') + ' UTC'; }
  function render(){ var host = el('capwatchBody'); if(!host) return; var c = cfg(), nowH = Math.floor(Date.now()/H), tr = state.trades || [], f = state.fwd;
    var live = tr.filter(function(x){ return x.status !== 'closed' && x.t >= nowH - 1 - RULE.hold; }), fresh = tr.filter(function(x){ return x.t === nowH - 1; });
    var chip = STATUS === 'EDGE' ? '<span class="es-chip good">EDGE — passed its final test</span>' : STATUS === 'FAILED' ? '<span class="es-chip bad">FAILED its final test — recorded only</span>' : '<span class="es-chip warn">CANDIDATE — final test pending</span>';
    var h = '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">Capitulation watch — round 14’s candidate' + (STATUS === 'FAILED' ? ' (failed its final test)' : ' (paper)') + '</h2>' +
      '<p style="margin:0 0 8px;">' + chip + '</p>' +
      '<p class="hint" style="margin:0 0 8px;color:var(--text);"><b>The rule.</b> When a coin falls 5 or more of its own hourly standard deviations in one hour <i>and</i> its perpetual trades at an unusual discount to spot (forced selling), buy the perpetual at the next hour’s open and close it 12 hours later. 5% of the account a trade, at most 20 at once, the deepest falls first.</p>' +
      '<p class="hint" style="margin:0 0 8px;">Research: on 25 coins +' + EVIDENCE.design.alpha + '% a year over the market (z ' + EVIDENCE.design.z + '); on 140 other coins +' + EVIDENCE.valid.alpha + '% (z ' + EVIDENCE.valid.z + ', bar ' + EVIDENCE.valid.bar + '), +' + EVIDENCE.valid.c2x + '% with costs doubled, ' + EVIDENCE.valid.years + ' years positive. Typical trade +' + EVIDENCE.meanTrade + '% before costs, ' + EVIDENCE.win + '% winners. <b>Speed matters:</b> ' + EVIDENCE.delay.map(function(d){ return (d[0] ? d[0] + ' h late' : 'on time') + ' ' + d[1] + '% a year'; }).join(' · ') + '.</p>' +
      (STATUS === 'FAILED' ? '<p class="hint" style="margin:0 0 8px;color:var(--text);"><b>Final test (19 Oct 2026, run once):</b> on ' + EVIDENCE.final.coins + ' coins nothing had touched (' + EVIDENCE.final.older + ' untouched coins with a perpetual and ' + EVIDENCE.final.young + ' listed since April 2025) it made ' + EVIDENCE.final.alpha + '% a year over the market, z ' + EVIDENCE.final.z + ' (it needed ' + EVIDENCE.final.bar + '); ' + EVIDENCE.final.c2x + '% with costs doubled; 2025 ' + EVIDENCE.final.y2025 + '%; worst fall ' + EVIDENCE.final.worst + '%. The older coins alone: +' + EVIDENCE.final.olderAlpha + '% (z ' + EVIDENCE.final.olderZ + '); new listings ' + EVIDENCE.final.youngAlpha + '%, because freshly listed coins that crashed kept falling. <b>Not an edge.</b> The watch is off; switched on, it only records what fires, for information.</p>' : '') +
      '<div class="fl-sum"><div><span>Coins watched</span><b>' + (state.coins || '—') + '</b></div><div><span>Signals now</span><b>' + fresh.length + '</b></div><div><span>Open paper trades</span><b>' + live.length + '</b></div><div><span>Forward trades closed</span><b>' + (f ? f.trades : '—') + '</b></div></div>';
    if(fresh.length) h += '<div class="rd-diag" style="margin-top:10px;"><span class="rd-pri ' + (STATUS === 'FAILED' ? 'med">FIRED (recorded only)' : 'low">BUY NOW') + '</span><div>' + fresh.map(function(x){ return '<b>' + esc(x.sym) + '</b> fell ' + (-x.z).toFixed(1) + 'σ in the hour to ' + hm(x.t + 1).slice(6) + ', premium ' + pct(x.prem, 3) + ' (5th percentile ' + pct(x.q05, 3) + '). ' + (STATUS === 'FAILED' ? 'Recorded for information; not a trade signal.' : 'Buy the perpetual now with 5% of the account; close at ' + hm(x.x + 1) + '.'); }).join('<br>') + '<br><span class="hint">' + (STATUS === 'EDGE' ? 'Passed its final test. ' : STATUS === 'FAILED' ? 'This rule failed its final test on untouched coins. ' : 'A candidate: it has not yet passed its final test. ') + 'Paper only; OMEGA places no orders.</span></div></div>';
    if(live.length) h += '<p class="hint" style="margin:10px 0 4px;"><b>Open paper trades</b></p><ul class="hint" style="margin:0;padding-left:18px;">' + live.map(function(x){ return '<li>' + esc(x.sym) + (x.entry ? ': bought at the ' + hm(x.e) + ' open, ' + (+x.entry).toPrecision(6) : ': buys at the ' + hm(x.e) + ' open (its price is recorded when that hour closes)') + ', closes ' + hm(x.x + 1) + (x.markRet != null ? ' · now ' + pct(x.markRet) : '') + '</li>'; }).join('') + '</ul>';
    if(f) h += '<p class="hint" style="margin:10px 0 0;"><b>Forward record since 19 Oct 2026</b> (decisions after the rule was frozen): ' + f.trades + ' trades closed' + (f.trades ? ', ' + pct(f.meanNet) + ' a trade after costs, ' + Math.round(100*f.win) + '% winners' : '') + '; ' + f.weeks + ' finished week' + (f.weeks === 1 ? '' : 's') + (f.alpha != null ? ', ' + pct(f.alpha, 1) + ' a year over the market' + (f.z != null ? ', z ' + f.z.toFixed(2) : ' (z after 8 weeks)') : '') + '.</p>';
    var closed = tr.filter(function(x){ return x.status === 'closed'; }).slice(-8).reverse();
    if(closed.length) h += '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;">Last closed paper trades</summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;">' + closed.map(function(x){ return '<li>' + esc(x.sym) + ' ' + hm(x.e) + ': ' + pct(x.net) + ' after costs and funding</li>'; }).join('') + '</ul></details>';
    h += '<p class="hint" style="margin:10px 0 0;">' + esc(state.msg || (state.lastH ? 'Last checked up to ' + hm(state.lastH + 1) + '.' : 'Not checked yet.')) + '</p>' +
      '<label class="checkbox-row" style="margin:8px 0 0;"><input type="checkbox" id="capwatchOn"' + (c.on ? ' checked' : '') + '> Watch every hour while the app is open (about one request per coin an hour)</label>' +
      '<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;"><button class="btn-outline" type="button" id="capwatchNow"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Checking…' : 'Check now') + '</button>' +
      (typeof Notification !== 'undefined' && Notification.permission !== 'granted' ? '<button class="btn-outline" type="button" id="capwatchAlerts">Turn on alerts</button>' : '') + '</div>' +
      '<p class="hint" style="margin:8px 0 0;">The app can only watch while it is open; a signal seen hours late is recorded on paper but is worth little. A server would be needed to catch every hour.</p></div>';
    host.innerHTML = h;
    var b = el('capwatchNow'); if(b) b.onclick = function(){ check(true); };
    var o = el('capwatchOn'); if(o) o.onchange = function(){ var v = cfg(); v.on = !!o.checked; setCfg(v); };
    var a = el('capwatchAlerts'); if(a) a.onclick = function(){ try{ Notification.requestPermission().then(function(){ render(); }); }catch(e){} }; }
  // the clock: a check one minute after each hour closes (and on opening, when an hour was missed)
  function due(){ var nowH = Math.floor(Date.now()/H); return cfg().on && !state.busy && (state.lastH == null || state.lastH < nowH - 1) && (Date.now() % H) > 60e3; }
  var started = false; function start(){ if(started) return; started = true; load().then(function(){ setInterval(function(){ if(due()) check(false); }, 60e3); setTimeout(function(){ if(due()) check(false); }, 45e3); }); }
  function wire(){ var p = el('page-edgelab'), b = el('edgelabBody'); if(!p || !b) return false; if(!el('capwatchBody')){ var d = document.createElement('div'); d.id = 'capwatchBody'; b.parentNode.insertBefore(d, b); } render(); start(); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_CAPWATCH = { check:check, render:render, state:function(){ return state; }, RULE:RULE, STATUS:function(){ return STATUS; }, EVIDENCE:EVIDENCE, FREEZE_H:FREEZE_H,
    _:{ sigmaAt:sigmaAt, quantileAt:quantileAt, zAt:zAt, firesAt:firesAt, book:book, settle:settle, hourlyPnl:hourlyPnl, marketPnl:marketPnl, forward:forward, weekOf:weekOf, align:align, topUp:topUp, getAll:getAll, getMeta:getMeta } };
})();
</script>
