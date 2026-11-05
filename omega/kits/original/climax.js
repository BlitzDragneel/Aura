<script>/* ═══ CLIMAX REVERSAL (v6.5.78) — round 16's rule, the first direction rule to pass all three stages, on paper ═══
   The rule (PLAN16 addendum A, family G, hold 12h): at the close of an hour, a coin's perpetual
   - fell 3 or more of its own hourly standard deviations (σ of the 168 hours before), and
   - traded at least 3 times its normal volume (median of the 168 hours before), and
   - closed in the top 40% of the hour's range (buyers took back most of the fall within the hour: a selling climax met
     by buying).
   Buy at the next hour's open and close 12 hours later. 20 slots of 5% of the account; a coin already held is not bought
   again; when more coins fire in one hour than slots are free, the deepest falls go first. Costs 0.10% a side; funding
   counted. Coins listed at least 30 days.
   Evidence (weekly alpha against the equal-weight market, Newey-West t):
   - 25 studied coins: +2.5% a year, z 2.30;
   - 140 other coins: +7.4%, z 2.54 (bar 1.645);
   - final test on 324 untouched coins, run once on 19 Oct 2026: +5.3%, z 2.35 (bar 2.326), +4.6% with costs doubled.
   Average trade +1.6–1.8% before costs; 58–62% winners; most of the profit comes from the bigger rebounds. Entering 1–2
   hours late kept nearly all of it in research.
   Forward record from 19 Oct 2026 12:00 UTC on every Binance USDT coin perpetual. OMEGA places no orders. Runs while the
   app is open. */
(function(){
  'use strict';
  var FAPI = 'https://fapi.binance.com', DBN = 'omega_climax', KEEP = 950, H = 3600e3, CFG_KEY = 'omega_climax_cfg_v1';
  var RULE = { k:3, vk:3, lk:0.6, hold:12, slots:20, w:0.05, cost:0.001, sigN:168, sigMin:120, vN:168, vMin:120, age:720 };
  var FREEZE_H = Date.UTC(2026, 9, 19, 12)/H;   // the forward record counts decisions from this hour on
  var STATUS = 'EDGE';                           // passed screen, validation and its final test (19 Oct 2026)
  var EVIDENCE = { design:{ coins:25, alpha:2.50, z:2.30, c2x:2.15, trades:229, mean:1.56, win:62 }, valid:{ coins:140, alpha:7.40, z:2.54, bar:1.645, c2x:6.51, trades:600, mean:1.77, win:60 },
    final:{ coins:324, alpha:5.28, z:2.35, bar:2.326, c2x:4.62, trades:440, mean:1.78, win:58, worst:-6.5, years:'2020 −0.1%, 2021 +1.7%, 2022 −1.3%, 2023 +4.8%, 2024 +9.6%, 2025 +13.0%, 2026 +7.8%' },
    late:[[0, 5.28, 2.35], [1, 5.49, 2.31], [2, 4.91, 2.25]], spot:{ coins:25, from:'Nov 2023', trades:87, mean:2.49, win:72, alpha:3.59, z:1.58 } };
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function cfg(){ try{ var v = JSON.parse(localStorage.getItem(CFG_KEY) || 'null'); return v && typeof v === 'object' ? v : { on:true }; }catch(e){ return { on:true }; } }
  function setCfg(v){ try{ localStorage.setItem(CFG_KEY, JSON.stringify(v)); }catch(e){} }

  // ── the rule's arithmetic, pure (the same as the research code: round16.prep + run_events) ──
  // D = { syms, h0, c:[[]], o:[[]], h:[[]], l:[[]], v:[[]], F:[[]], first:[] } — arrays per coin aligned on hours h0, h0+1, …; null = no bar
  function lr(c, i){ var a = c[i], b = c[i-1]; return (a > 0 && b > 0) ? Math.log(a/b) : null; }
  function sigmaAt(c, t){ var s = 0, s2 = 0, n = 0; for(var i = Math.max(1, t - RULE.sigN); i < t; i++){ var x = lr(c, i); if(x == null) continue; s += x; s2 += x*x; n++; }
    if(n < RULE.sigMin) return null; var m = s/n, v = (s2 - n*m*m)/(n - 1); return v > 0 ? Math.sqrt(v) : null; }
  function medianAt(v, t){ var xs = []; for(var i = Math.max(0, t - RULE.vN); i < t; i++){ var x = v[i]; if(x != null && isFinite(x)) xs.push(x); }
    if(xs.length < RULE.vMin) return null; xs.sort(function(a, b){ return a - b; }); var n = xs.length; return n % 2 ? xs[(n - 1)/2] : (xs[n/2 - 1] + xs[n/2])/2; }
  function zAt(D, j, t){ var c = D.c[j]; if(t < 1 || !(c[t] > 0) || D.first[j] == null || t < D.first[j] + RULE.age) return null; var x = lr(c, t); if(x == null) return null; var s = sigmaAt(c, t); return s ? x/s : null; }
  function measure(D, j, t){ var z = zAt(D, j, t); if(z == null) return null; var v = D.v[j][t], md = medianAt(D.v[j], t), hi = D.h[j][t], lo = D.l[j][t], c = D.c[j][t];
    var vr = md == null || v == null ? null : md > 0 ? v/md : (v > 0 ? Infinity : null), loc = hi > lo ? (c - lo)/(hi - lo) : null; return { z:z, vr:vr, loc:loc }; }
  function firesAt(D, t){ var out = [];
    for(var j=0; j<D.syms.length; j++){ var m = measure(D, j, t); if(!m || m.z > -RULE.k || m.vr == null || !(m.vr >= RULE.vk) || m.loc == null || !(m.loc >= RULE.lk)) continue;
      out.push({ j:j, sym:D.syms[j], t:t, z:m.z, vr:m.vr, loc:m.loc }); }
    return out.sort(function(a, b){ return a.z - b.z || (a.j - b.j); }); }
  function lastIdx(c){ for(var i=c.length-1; i>=0; i--) if(c[i] > 0) return i; return -1; }
  function book(D, fired, open0){ var open = (open0 || []).slice(), trades = [];
    var hours = Object.keys(fired).map(Number).sort(function(a, b){ return a - b; });
    hours.forEach(function(t){ var e = t + 1; open = open.filter(function(o){ return o.x >= e; }); var free = RULE.slots - open.length;
      fired[t].forEach(function(f){ if(free <= 0) return; if(open.some(function(o){ return o.sym === f.sym; })) return; var j = f.j, c = D.c[j], o = D.o[j];
        if(e < c.length && !(o[e] > 0 && c[e] > 0)) return;
        var tr = { sym:f.sym, t:t, z:f.z, vr:f.vr, loc:f.loc, e:e, x:t + RULE.hold }; trades.push(tr); open.push(tr); free--; }); });
    trades.forEach(function(tr){ settle(D, tr); }); return trades; }
  function settle(D, tr){ var j = D.syms.indexOf(tr.sym); if(j < 0) return tr; var c = D.c[j], o = D.o[j], F = D.F[j] || [], L = lastIdx(c), x = Math.min(tr.x, L);
    if(!(tr.e < c.length && o[tr.e] > 0 && c[tr.e] > 0)) return tr;
    if(tr.x >= c.length && L < c.length - 72){ x = L; }
    else if(tr.x >= c.length){ tr.status = 'open'; tr.entry = o[tr.e]; var cl = null; for(var q = Math.min(L, c.length - 1); q >= tr.e; q--) if(c[q] > 0){ cl = c[q]; break; } tr.now = cl; tr.markRet = cl ? cl/o[tr.e] - 1 : null; return tr; }
    var r = c[tr.e]/o[tr.e] - 1, fu = 0, prev = c[tr.e];
    for(var h = tr.e + 1; h <= x; h++){ if(c[h] > 0){ r += c[h]/prev - 1; prev = c[h]; } fu += F[h] || 0; }
    tr.entry = o[tr.e]; tr.exit = prev; tr.fund = fu; tr.ret = r - fu; tr.net = tr.ret - 2*RULE.cost; tr.status = 'closed'; tr.xs = x; return tr; }
  function hourlyPnl(D, trades, from, to){ var out = {}; trades.forEach(function(tr){ if(tr.status !== 'closed' && tr.status !== 'open') return; var j = D.syms.indexOf(tr.sym); if(j < 0) return; var c = D.c[j], o = D.o[j], F = D.F[j] || [], w = RULE.w;
      if(!(o[tr.e] > 0 && c[tr.e] > 0)) return; var add = function(h, v){ if(h < from || h >= to) return; out[h] = (out[h] || 0) + v; };
      add(tr.e, w*(c[tr.e]/o[tr.e] - 1) - w*RULE.cost); var prev = c[tr.e], end = Math.min(tr.xs != null ? tr.xs : tr.x, c.length - 1);
      for(var h = tr.e + 1; h <= end; h++){ var v = 0; if(c[h] > 0){ v += c[h]/prev - 1; prev = c[h]; } v -= (F[h] || 0); add(h, w*v); }
      if(tr.status === 'closed') add(tr.xs, -w*RULE.cost); });
    return out; }
  function marketPnl(D, from, to){ var out = {}; for(var h = Math.max(1, from); h < to; h++){ var s = 0, n = 0; for(var j=0; j<D.syms.length; j++){ var c = D.c[j]; if(D.first[j] == null || h - 1 < D.first[j] + RULE.age) continue; if(c[h] > 0 && c[h-1] > 0){ s += c[h]/c[h-1] - 1; n++; } } if(n) out[h] = s/n; } return out; }
  function weekOf(hAbs){ var d = Math.floor(hAbs/24), wd = (d + 4) % 7; return d + ((7 - wd) % 7); }
  function nwT(x){ var E = window.OMEGA_EDGELIB; if(E && E.nwT) return E.nwT(x, 2); var n = x.length; if(n < 8) return null; var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g = e.reduce(function(a, v){ return a + v*v; }, 0)/n;
    for(var k=1; k<=2; k++){ var s = 0; for(var q=k; q<n; q++) s += e[q]*e[q-k]; g += 2*(1 - k/3)*s/(n - k); } return g > 0 ? m/Math.sqrt(g/n) : null; }
  function forward(D, trades, nowH){ var from = Math.max(FREEZE_H - D.h0, 1), to = Math.min(nowH - D.h0, D.c.reduce(function(a, c){ return Math.max(a, c.length); }, 0)), P = hourlyPnl(D, trades.filter(function(tr){ return tr.t + D.h0 >= FREEZE_H; }), from, to), M = marketPnl(D, from, to), wk = {};
    for(var h = from; h < to; h++){ var w = weekOf(h + D.h0); var x = wk[w] || (wk[w] = { x:0, m:0 }); x.x += P[h] || 0; x.m += M[h] || 0; }
    var thisWeek = weekOf(nowH), ks = Object.keys(wk).map(Number).filter(function(w){ return w < thisWeek; }).sort(function(a, b){ return a - b; });
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
  async function getJSON(url){ for(var a=0; a<4; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(15000*(a+1)); continue; } if(r.status === 400) return null; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 3) throw e; await sleep(1500*(a+1)); } } }
  var state = { busy:false, last:null, msg:'', coins:0, fired:[], trades:[], fwd:null, err:null };
  // every USDT perpetual on a coin (not metals, stocks or other non-coin underlyings), with its listing date
  async function perps(){ var m = await getMeta('perps'); if(m && Date.now() - m.at < 24*H) return m.map;
    var info = await getJSON(FAPI + '/fapi/v1/exchangeInfo'), map = {}; ((info && info.symbols) || []).forEach(function(x){ if(x.contractType === 'PERPETUAL' && x.quoteAsset === 'USDT' && x.status === 'TRADING' && (!x.underlyingType || x.underlyingType === 'COIN') && !/^(XAU|XAG|XPT|XPD)/.test(x.symbol)) map[x.symbol] = +x.onboardDate || 0; });
    if(Object.keys(map).length) await putMeta('perps', { at:Date.now(), map:map }); return map; }
  async function topUp(rec, sym, nowH){ var startH = rec && rec.c.length ? rec.h0 + rec.c.length : nowH - KEEP; if(startH < nowH - KEEP) startH = nowH - KEEP; if(startH >= nowH) return rec;
    var d = await getJSON(FAPI + '/fapi/v1/klines?symbol=' + sym + '&interval=1h&startTime=' + startH*H + '&limit=' + Math.min(1000, nowH - startH + 1)); if(!Array.isArray(d)) return rec;
    rec = rec || { sym:sym, h0:startH, o:[], h:[], l:[], c:[], v:[] }; ['h', 'l'].forEach(function(f){ if(!rec[f]) rec[f] = rec.c.map(function(){ return null; }); });
    d.forEach(function(k){ var hh = Math.round(+k[0]/H); if(hh >= nowH || hh < rec.h0) return; var i = hh - rec.h0; while(rec.c.length < i){ rec.o.push(null); rec.h.push(null); rec.l.push(null); rec.c.push(null); rec.v.push(null); }
      var row = [+k[1], +k[2], +k[3], +k[4], +k[5]]; if(i === rec.c.length){ rec.o.push(row[0]); rec.h.push(row[1]); rec.l.push(row[2]); rec.c.push(row[3]); rec.v.push(row[4]); } else { rec.o[i] = row[0]; rec.h[i] = row[1]; rec.l[i] = row[2]; rec.c[i] = row[3]; rec.v[i] = row[4]; } });
    var cut = rec.c.length - KEEP; if(cut > 0){ ['o', 'h', 'l', 'c', 'v'].forEach(function(f){ rec[f] = rec[f].slice(cut); }); rec.h0 += cut; }
    rec.at = Date.now(); return rec; }
  async function fundingBetween(sym, aH, bH){ var d = await getJSON(FAPI + '/fapi/v1/fundingRate?symbol=' + sym + '&startTime=' + aH*H + '&endTime=' + ((bH + 1)*H - 1) + '&limit=1000'), out = {};
    (Array.isArray(d) ? d : []).forEach(function(x){ var h = Math.floor(+x.fundingTime/H); out[h] = (out[h] || 0) + (+x.fundingRate); }); return out; }
  function align(recs, map){ var h0 = Infinity, h1 = -Infinity; recs.forEach(function(r){ if(r.c.length){ h0 = Math.min(h0, r.h0); h1 = Math.max(h1, r.h0 + r.c.length); } }); if(!isFinite(h0)) return null;
    var D = { h0:h0, syms:[], c:[], o:[], h:[], l:[], v:[], F:[], first:[] }, n = h1 - h0;
    recs.forEach(function(r){ var A = {}; ['c', 'o', 'h', 'l', 'v'].forEach(function(f){ A[f] = new Array(n).fill(null); for(var i=0; i<r.c.length; i++) A[f][r.h0 - h0 + i] = r[f] ? r[f][i] : null; });
      var F = new Array(n).fill(0); Object.keys(r.fund || {}).forEach(function(k){ var i = +k - h0; if(i >= 0 && i < n) F[i] = r.fund[k]; });
      var ob = map[r.sym]; D.syms.push(r.sym); ['c', 'o', 'h', 'l', 'v'].forEach(function(f){ D[f].push(A[f]); }); D.F.push(F); D.first.push(ob ? Math.floor(ob/H) - h0 : null); });
    return D; }
  function notify(title, body){ try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification(title, { body:body }); }catch(e){}
    try{ var A = window.OMEGA_ALERTS, c = JSON.parse(localStorage.getItem('omega_alerts_v1') || 'null'); if(A && A.push && c && c.url) A.push(title, body); }catch(e){} }
  async function check(force){ if(state.busy) return 'busy'; if(!force && !cfg().on) return 'off'; state.busy = true; state.err = null; render();
    try{ var nowH = Math.floor(Date.now()/H), map = await perps(), list = Object.keys(map).sort(); if(!list.length) throw new Error('could not read Binance’s list of perpetuals');
      var recs = await getAll(), byS = {}; (recs || []).forEach(function(r){ byS[r.sym] = r; }); var done = 0;
      for(var i=0; i<list.length; i++){ var s = list[i]; var r = byS[s]; if(r && r.h && r.h0 + r.c.length >= nowH){ done++; continue; }
        try{ r = await topUp(r && r.h ? r : null, s, nowH); if(r){ byS[s] = r; await putCoin(r); } }catch(e){}
        done++; if(i % 10 === 0){ state.msg = 'Checking ' + done + ' of ' + list.length + ' perpetuals…'; render(); } await sleep(r && r.c.length > 50 ? 120 : 260); }
      var meta = (await getMeta('book')) || { lastH:null, trades:[], fired:[] }, recsL = list.map(function(s){ return byS[s]; }).filter(function(r){ return r && r.h; });
      var D = align(recsL, map); if(!D) throw new Error('no bars yet');
      var lastClosed = nowH - 1 - D.h0, fromT = meta.lastH != null ? Math.max(meta.lastH - D.h0 + 1, 1) : lastClosed; if(fromT < RULE.sigN + 2) fromT = RULE.sigN + 2;
      var fired = {}; for(var t = fromT; t <= lastClosed; t++){ var f = firesAt(D, t); if(f.length) fired[t] = f; }
      var prevT = (meta.trades || []).map(function(x){ return Object.assign({}, x); }), openPrev = prevT.filter(function(x){ return x.t < fromT + D.h0; }).map(function(x){ return { sym:x.sym, x:x.x - D.h0 }; });
      var newT = book(D, fired, openPrev).map(function(tr){ tr.t += D.h0; tr.e += D.h0; tr.x += D.h0; return tr; });
      var all = prevT.concat(newT);
      for(var q=0; q<all.length; q++){ var tr = all[q]; if(tr.status === 'closed') continue; var jj = D.syms.indexOf(tr.sym); if(jj < 0) continue;
        if(tr.x - D.h0 < D.c[jj].length && D.c[jj][tr.x - D.h0] != null && !tr.fundDone){ var fr = await fundingBetween(tr.sym, tr.e + 1, tr.x); var rr2 = byS[tr.sym]; rr2.fund = Object.assign(rr2.fund || {}, fr); await putCoin(rr2); Object.keys(fr).forEach(function(k){ var ii = +k - D.h0; if(ii >= 0 && ii < D.F[jj].length) D.F[jj][ii] = fr[k]; }); tr.fundDone = true; }
        var loc = { sym:tr.sym, t:tr.t - D.h0, e:tr.e - D.h0, x:tr.x - D.h0 }; settle(D, loc); ['status', 'entry', 'exit', 'fund', 'ret', 'net', 'now', 'markRet'].forEach(function(k){ if(loc[k] !== undefined) tr[k] = loc[k]; }); if(loc.xs != null) tr.xs = loc.xs + D.h0; }
      var newFired = []; Object.keys(fired).forEach(function(k){ fired[k].forEach(function(f){ newFired.push({ sym:f.sym, t:+k + D.h0, z:f.z, vr:f.vr, loc:f.loc, taken:newT.some(function(tr){ return tr.sym === f.sym && tr.t === +k + D.h0; }) }); }); });
      meta.trades = all.slice(-2000); meta.fired = (meta.fired || []).concat(newFired).slice(-500); meta.lastH = lastClosed + D.h0; meta.at = Date.now(); await putMeta('book', meta);
      newT.filter(function(tr){ return tr.t >= nowH - 2; }).forEach(function(tr){ notify('OMEGA climax reversal: ' + tr.sym, 'Fell ' + (-tr.z).toFixed(1) + ' standard deviations on ' + tr.vr.toFixed(1) + '× volume and closed near the top of the hour. Paper rule: buy at the next open, 5% of the account, close at ' + new Date((tr.x + 1)*H).toISOString().slice(11, 16) + ' UTC.'); });
      var tl = all.map(function(tr){ return Object.assign({}, tr, { t:tr.t - D.h0, e:tr.e - D.h0, x:tr.x - D.h0, xs: tr.xs != null ? tr.xs - D.h0 : null }); });
      state.fwd = forward(D, tl, nowH); state.trades = all; state.fired = meta.fired; state.coins = list.length; state.last = Date.now(); state.lastH = meta.lastH;
      state.msg = 'Checked ' + list.length + ' perpetuals up to the hour ending ' + new Date((meta.lastH + 1)*H).toISOString().slice(11, 16) + ' UTC' + (newFired.length ? ': ' + newFired.length + ' fired.' : ': nothing fired.');
      return state.msg; }
    catch(e){ state.err = String(e && e.message || e); state.msg = 'Climax watch stopped: ' + state.err; return state.msg; }
    finally{ state.busy = false; render(); } }
  async function load(){ try{ var m = await getMeta('book'); if(m){ state.trades = m.trades || []; state.fired = m.fired || []; state.lastH = m.lastH; } }catch(e){} render(); }

  // ── the card (top of the Edge Lab, and a copy on Market Watch) ──
  function pct(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '') + (100*v).toFixed(d == null ? 2 : d) + '%'; }
  function hm(h){ return new Date(h*H).toISOString().slice(5, 16).replace('T', ' ') + ' UTC'; }
  function html(){ var c = cfg(), nowH = Math.floor(Date.now()/H), tr = state.trades || [], f = state.fwd, E = EVIDENCE;
    var live = tr.filter(function(x){ return x.status !== 'closed' && x.t >= nowH - 1 - RULE.hold; }), fresh = tr.filter(function(x){ return x.t >= nowH - 2; });
    var h = '<div class="card" style="margin-bottom:14px;border-color:var(--bull);"><h2 style="color:var(--gold);">Climax reversal — round 16’s rule, passed all three tests (paper)</h2>' +
      '<p style="margin:0 0 8px;"><span class="es-chip good">EDGE on paper — passed its final test on 324 untouched coins</span></p>' +
      '<p class="hint" style="margin:0 0 8px;color:var(--text);"><b>The rule.</b> A coin’s perpetual falls 3 or more of its own hourly standard deviations on at least 3× its normal volume, and buyers take most of it back within the hour: the hour closes in the top 40% of its range. That is a selling climax met by buying. <b>Buy at the next hour’s open and close 12 hours later.</b> 5% of the account a trade, at most 20 at once, deepest falls first.</p>' +
      '<p class="hint" style="margin:0 0 8px;">Research, judged week by week against the market: 25 coins +' + E.design.alpha + '% a year (z ' + E.design.z + '); 140 other coins +' + E.valid.alpha + '% (z ' + E.valid.z + '); <b>final test, run once on ' + E.final.coins + ' untouched coins: +' + E.final.alpha + '% a year, z ' + E.final.z + ' against a bar of ' + E.final.bar + '</b>, +' + E.final.c2x + '% with costs doubled, worst fall ' + E.final.worst + '%. By year: ' + esc(E.final.years) + '. Average trade +' + E.final.mean + '% before costs, ' + E.final.win + '% winners.</p>' +
      '<p class="hint" style="margin:0 0 8px;"><b>Read it honestly.</b> It passed the final bar only just (z 2.35 against 2.33). Most of the profit comes from the bigger rebounds: without the best tenth of trades the average falls to about 0.1–0.6%. It earns about 5% a year on the whole account because it trades rarely. Entering 1–2 hours late kept nearly all of it, so a phone that checks hourly is fast enough. On spot bars (25 coins, Nov 2023 on) it also worked: ' + E.spot.trades + ' trades, +' + E.spot.mean + '% a trade, ' + E.spot.win + '% winners (too few to judge alone). Only forward weeks will show whether it holds.</p>' +
      '<p class="hint" style="margin:0 0 8px;"><b>What it really catches (round 17).</b> 95% of its signals come during market-wide flushes. After them the coins rose +1.7% in 12 hours on average, but slightly less than the whole market did. So the profit is the market\u2019s rebound after a flush, entered through coins whose fall was already being bought back. A coin collapsing by 8\u03c3 or more did worst; that is usually bad news about the coin itself.</p>' +
      '<div class="fl-sum"><div><span>Coins watched</span><b>' + (state.coins || '—') + '</b></div><div><span>Signals now</span><b>' + fresh.length + '</b></div><div><span>Open paper trades</span><b>' + live.length + '</b></div><div><span>Forward trades closed</span><b>' + (f ? f.trades : '—') + '</b></div></div>';
    if(fresh.length) h += '<div class="rd-diag" style="margin-top:10px;"><span class="rd-pri low">BUY (paper)</span><div>' + fresh.map(function(x){ return '<b>' + esc(x.sym) + '</b> fell ' + (-x.z).toFixed(1) + 'σ on ' + (+x.vr).toFixed(1) + '× volume, closed at ' + Math.round(100*x.loc) + '% of the hour’s range: buy at the ' + hm(x.e) + ' open, 5% of the account, close at ' + hm(x.x + 1).slice(6); }).join('<br>') + '. OMEGA places no orders.</div></div>';
    if(live.length) h += '<p class="hint" style="margin:10px 0 4px;"><b>Open paper trades</b></p><ul class="hint" style="margin:0;padding-left:18px;">' + live.map(function(x){ return '<li>' + esc(x.sym) + (x.entry ? ': bought at the ' + hm(x.e) + ' open, ' + (+x.entry).toPrecision(6) + (x.markRet != null ? ', now ' + pct(x.markRet) : '') : ': buys at the ' + hm(x.e) + ' open') + '; closes at ' + hm(x.x + 1).slice(6) + '</li>'; }).join('') + '</ul>';
    if(f) h += '<p class="hint" style="margin:10px 0 0;"><b>Forward record since 19 Oct 2026, 12:00 UTC</b>: ' + f.trades + ' trades closed' + (f.trades ? ', ' + pct(f.meanNet) + ' a trade after costs, ' + Math.round(100*f.win) + '% winners' : '') + '; ' + f.weeks + ' finished week' + (f.weeks === 1 ? '' : 's') + (f.alpha != null ? ', ' + pct(f.alpha, 1) + ' a year over the market' + (f.z != null ? ' (z ' + f.z.toFixed(2) + ')' : '') : '') + '. Judged after 26 weeks: kept at z ≥ 1.96 week by week, retired if its weeks average zero or less.</p>';
    var closed = tr.filter(function(x){ return x.status === 'closed'; }).slice(-8).reverse();
    if(closed.length) h += '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;">Last closed paper trades</summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;">' + closed.map(function(x){ return '<li>' + esc(x.sym) + ' ' + hm(x.e) + ': ' + pct(x.net) + ' after costs and funding</li>'; }).join('') + '</ul></details>';
    h += '<p class="hint" style="margin:10px 0 0;">' + esc(state.msg || (state.lastH ? 'Last checked up to ' + hm(state.lastH + 1) + '.' : 'Not checked yet.')) + '</p>' +
      '<label class="checkbox-row" style="margin:8px 0 0;"><input type="checkbox" data-climax="on"' + (c.on ? ' checked' : '') + '> Watch every hour while the app is open (one request per perpetual an hour)</label>' +
      '<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;"><button class="btn-outline" type="button" data-climax="now"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Checking…' : 'Check now') + '</button>' +
      (typeof Notification !== 'undefined' && Notification.permission !== 'granted' ? '<button class="btn-outline" type="button" data-climax="alerts">Turn on alerts</button>' : '') + '</div>' +
      '<p class="hint" style="margin:8px 0 0;">Paper only. The app watches only while it is open. The paper record enters every signal at the next hour\u2019s open even when the app saw it later, so it measures the rule, not reaction time; in research an entry 1\u20132 hours late kept nearly all of the edge.</p></div>';
    return h; }
  function render(){ ['climaxBody', 'climaxWatchBody', 'climaxSigBody'].forEach(function(id){ var host = el(id); if(!host) return; host.innerHTML = html();
      Array.prototype.forEach.call(host.querySelectorAll('[data-climax]'), function(b){ var k = b.getAttribute('data-climax');
        if(k === 'now') b.onclick = function(){ check(true); }; if(k === 'on') b.onchange = function(){ var v = cfg(); v.on = !!b.checked; setCfg(v); render(); };
        if(k === 'alerts') b.onclick = function(){ try{ Notification.requestPermission().then(function(){ render(); }); }catch(e){} }; }); }); }
  function due(){ var nowH = Math.floor(Date.now()/H); return cfg().on && !state.busy && (state.lastH == null || state.lastH < nowH - 1) && (Date.now() % H) > 75e3; }
  var started = false; function start(){ if(started) return; started = true; load().then(function(){ setInterval(function(){ if(due()) check(false); }, 60e3); setTimeout(function(){ if(due()) check(false); }, 50e3); }); }
  function wire(){ var ok = false, b = el('edgelabBody'); if(b && !el('climaxBody')){ var d = document.createElement('div'); d.id = 'climaxBody'; b.parentNode.insertBefore(d, el('capwatchBody') || b); }
    var w = el('watchBody'); if(w && !el('climaxWatchBody')){ var d2 = document.createElement('div'); d2.id = 'climaxWatchBody'; w.parentNode.insertBefore(d2, w); }
    if(el('climaxBody')){ ok = true; render(); start(); } return ok; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_CLIMAX = { check:check, render:render, state:function(){ return state; }, RULE:RULE, STATUS:function(){ return STATUS; }, EVIDENCE:EVIDENCE, FREEZE_H:FREEZE_H,
    _:{ sigmaAt:sigmaAt, medianAt:medianAt, zAt:zAt, measure:measure, firesAt:firesAt, book:book, settle:settle, hourlyPnl:hourlyPnl, marketPnl:marketPnl, forward:forward, weekOf:weekOf, align:align, topUp:topUp, html:html } };
})();
</script>
