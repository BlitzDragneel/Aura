<script>/* ═══ BREAKOUT DESK (v6.5.83, v6.5.84) — two setups from the 19–20 Oct edge hunt. BOTH FAILED a clean test (plan E1). ═══
   v6.5.84: (1) plan E1, written and fingerprinted before the run (md5 d1c0b7d7e0085060681320dc8e381b9d), tested the frozen
   rules once on 2021–2023 (14 older perpetuals, true 1% risk, one market at a time; pass = end above 100 and beat 95% of
   100 coin-flip accounts): A 100 → 49.1 (beat 9%), B 100 → 27.2 (beat 2%). Both FAILED; they stay on paper as a forward
   record only, with no alerts. (2) Correction: A's 180.5 below was on a 100 USDT account where Binance's 5 USDT minimum
   rounded 238 of 623 trades above 1% risk; at a true 1% it is ×1.08. B is barely affected (about 150 at a true 1%).
   Found outside the app (research files edge/*.py, 19–20 Oct 2026) on Binance USD-M perpetuals, hourly, Jan 2024 – Oct 2026.
   792 combinations (22 entry families × 6 filters × 6 ways to manage a trade) were chosen on Jan 2024 – Jun 2025 and judged
   on Jul 2025 – Oct 2026; the best were then played as a live account: ONE market at a time, Binance rules (5 USDT minimum
   order, 20× cap, liquidation only on a gap past both stop and margin), 0.10% a side, funding every hour.
   A. 72-hour breakout, US hours, managed the owner's way: at the close of an hour that opened 13:00–20:00 UTC, a coin's
      perpetual closes above the highest high of the 72 hours before (below the lowest low: short) on at least 2× the median
      volume of the 168 hours before. Enter at the next open with 5 units, stop 2 ATR(14). At +1R close 3 units, stop to the
      entry, add 1 unit; add 1 more at +2R and +3R (stop to the last add − 1R); trail 3 ATR from the best price; out after
      168 hours. Unseen half, 100 USDT, 1% risk: 180.5 (623 trades); beat 96% of 100 coin-flip-direction accounts.
   B. Momentum burst, US hours, pyramid: the hour's log return is 3+ of its own standard deviations (168 hours before) on 3×+
      the median volume and closes in the top 40% of its range (down 3σ, bottom 40%: short). 1 unit, stop 2 ATR; add 1
      unit at each +1R (up to 3; stop to the last add − 1R); trail 3 ATR; out after 168 hours. Unseen half: 144.3 (403
      trades); beat 91% of coin-flip accounts.
   Why not an edge: each was the best of 10 setup-and-method pairs, and luck alone gives a result that good about 1 time in
   3; counted week by week (trades in one week share the market's move) the sweep's finalists were indistinguishable from
   chance (t ≈ 0.5). The worst fall at 1% risk was 31% (A) and 37% (B). So they go on paper and are judged only on new weeks.
   Liquidity: average daily volume over the last 480 hours ≥ $5M; listed ≥ 820 hours. Bars come from the climax watch's
   hourly store (one download for both). OMEGA places no orders; runs while the app is open. */
(function(){
  'use strict';
  var H = 3600e3, FAPI = 'https://fapi.binance.com', CFG_KEY = 'omega_bdesk_cfg_v1', DBN = 'omega_bdesk', CDB = 'omega_climax';
  var FREEZE_H = Date.UTC(2026, 9, 20, 3)/H;          // forward record: decisions from 20 Oct 2026 03:00 UTC on
  var C = { liq:5e6, liqN:480, age:820, sigN:168, vN:168, look:72, from:13, to:20, fee:0.001, minN:5, maxLev:20, maint:0.005, start:100, risk:0.01, weeks:26, zBar:1.96 };
  var SETUPS = {
    A:{ key:'A', name:'72-hour breakout', sub:'US hours · your 5-unit method', vr:2,
        M:{ init:[0.2, 0.2, 0.2, 0.2, 0.2], stop_atr:2, trail_atr:3, sc_frac:0.6, sc_R:1, be_after_scale:true, pyr_R:1, pyr_max:3, add_size:0.2, max_bars:168 },
        retire:0.46, failed:{ end:49.1, beat:9, yrs:'78 / 95 / 66' }, ev:{ true1:108, end:180.5, trades:623, dd:31, flip:96, flipMed:74.7, win6:'9 of 10', med6:1.42, worst6:0.95, best6:1.67, mPos:62, mAvg:4.6, mWorst:-18.6, ladder:'1%: 180 · 2%: 142 · 5%: 75 · 10%: 15', other:'plain pyramid 131 · fixed 2R target 87' } },
    B:{ key:'B', name:'Momentum burst', sub:'US hours · pyramid', k:3, vr:3, hiLoc:0.6, loLoc:0.4,
        M:{ init:[1], stop_atr:2, trail_atr:3, pyr_R:1, pyr_max:3, add_size:1, max_bars:168 },
        retire:0.56, failed:{ end:27.2, beat:2, yrs:'80 / 58 / 59' }, ev:{ true1:150, end:144.3, trades:403, dd:37, flip:91, flipMed:73.9, win6:'7 of 10', med6:1.40, worst6:0.79, best6:2.35, mPos:50, mAvg:4.0, mWorst:-21.0, ladder:'1%: 144 · 2%: 137 · 5%: 32 · 10%: 1', other:'your 5-unit method 110 · fixed 2R target 94' } }
  };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function cfg(){ try{ var v = JSON.parse(localStorage.getItem(CFG_KEY) || 'null'); if(v && typeof v === 'object') return v; }catch(e){} return { on:true, acct:100, risk:1, focus:'A' }; }
  function setCfg(v){ try{ localStorage.setItem(CFG_KEY, JSON.stringify(v)); }catch(e){} }

  // ── the arithmetic, pure: the same as the research code (edge/engine2.py base/signal, edge/live.py trade/account) ──
  // rec = { sym, h0, o:[], h:[], l:[], c:[], v:[] (base volume) or qv:[] (quote volume), first: listing hour }
  function qvAt(r, i){ if(r.qv) return r.qv[i]; var v = r.v[i], c = r.c[i]; return v == null || c == null ? null : v*c; }
  function atrOf(r){ if(r._atr && r._atrN === r.c.length) return r._atr; var n = r.c.length, a = new Array(n), prev = null;
    for(var i=0; i<n; i++){ var hi = r.h[i], lo = r.l[i], pc = i ? r.c[i-1] : r.c[0]; if(hi == null || lo == null || pc == null){ a[i] = prev; continue; }
      var tr = Math.max(hi - lo, Math.abs(hi - pc), Math.abs(lo - pc)); prev = prev == null ? tr : prev + (tr - prev)/14; a[i] = prev; }
    r._atr = a; r._atrN = n; return a; }
  function median(xs){ xs.sort(function(a, b){ return a - b; }); var n = xs.length; return n % 2 ? xs[(n - 1)/2] : (xs[n/2 - 1] + xs[n/2])/2; }
  function measure(r, i){                         // everything known at the close of bar i
    if(i < C.liqN - 1 || i < C.sigN + 1 || !(r.c[i] > 0)) return null;
    var q = qvAt(r, i); if(q == null) return null;
    var w = []; for(var k = i - C.vN; k < i; k++){ var x = qvAt(r, k); if(x == null) return null; w.push(x); } var md = median(w);
    var vr = md > 0 ? q/md : (q > 0 ? Infinity : NaN);
    var s = 0, n = 0, L = []; for(k = i - C.sigN; k < i; k++){ var a = r.c[k], b = r.c[k-1]; if(!(a > 0) || !(b > 0)) return null; var x2 = Math.log(a/b); L.push(x2); s += x2; n++; }
    var m = s/n, ss = 0; L.forEach(function(x3){ ss += (x3 - m)*(x3 - m); }); var sg = Math.sqrt(ss/(n - 1)), lr = r.c[i-1] > 0 ? Math.log(r.c[i]/r.c[i-1]) : NaN, z = lr/sg;
    var hi = -Infinity, lo = Infinity; for(k = i - C.look; k < i; k++){ if(r.h[k] == null || r.l[k] == null) return null; if(r.h[k] > hi) hi = r.h[k]; if(r.l[k] < lo) lo = r.l[k]; }
    var sum = 0; for(k = i - C.liqN + 1; k <= i; k++){ var y = qvAt(r, k); if(y == null) return null; sum += y; }
    var rg = r.h[i] - r.l[i], cl = rg > 0 ? (r.c[i] - r.l[i])/rg : NaN, atr = atrOf(r)[i];
    return { vr:vr, z:z, cl:cl, hi72:hi, lo72:lo, liq:sum/20, atr:atr, c:r.c[i] }; }
  function eligible(r, i){ var t = r.h0 + i, hr = ((t % 24) + 24) % 24; return hr >= C.from && hr <= C.to && r.first != null && t - r.first >= C.age; }
  function signalAt(r, i, key){ if(!eligible(r, i)) return null; var m = measure(r, i); if(!m || !(m.liq >= C.liq) || !(m.atr > 0)) return null; var S = SETUPS[key], d = 0, pr = 0;
    if(key === 'A'){ if(!(m.vr >= S.vr)) return null; d = m.c > m.hi72 ? 1 : (m.c < m.lo72 ? -1 : 0); pr = m.vr; }
    else { if(!(m.vr >= S.vr)) return null; d = (m.z >= S.k && m.cl >= S.hiLoc) ? 1 : ((m.z <= -S.k && m.cl <= S.loLoc) ? -1 : 0); pr = Math.abs(m.z); }
    if(!d) return null; return { sym:r.sym, t:r.h0 + i, d:d, pr:pr, m:m }; }
  // the position: resumable bar by bar, in USDT (live.py trade())
  function sumQ(p){ var s = 0; p.lots.forEach(function(x){ s += x[0]; }); return s; }
  function upnl(p, px){ var s = 0; p.lots.forEach(function(x){ s += p.d*x[0]*(px - x[1]); }); return s; }
  function eqNow(p, px){ return p.eq0 - p.fees - p.fund + upnl(p, px) + p.real; }
  function openLot(p, px, size){ var n = size*p.base; if(n < C.minN){ n = C.minN; p.bumped = true; } var tot = 0; p.lots.forEach(function(x){ tot += x[0]*px; });
    var cap = C.maxLev*Math.max(eqNow(p, px), 0); if(tot + n > cap){ n = cap - tot; if(n < C.minN) return false; } p.lots.push([n/px, px]); p.fees += n*C.fee; return true; }
  function closeQty(p, qty, px){ while(qty > 1e-12 && p.lots.length){ var L0 = p.lots[0], take = Math.min(L0[0], qty); p.real += p.d*take*(px - L0[1]); p.fees += take*px*C.fee; L0[0] -= take; qty -= take; if(L0[0] <= 1e-12) p.lots.shift(); } }
  function openPos(r, i, d, eq, risk, key){ var M = SETUPS[key].M, e = r.o[i+1], a = atrOf(r)[i], Rd = M.stop_atr*a; if(!(e > 0) || !(Rd > 0.001*e)) return null;
    var p = { key:key, sym:r.sym, d:d, iH:r.h0 + i, eH:r.h0 + i + 1, e:e, Rd:Rd, atr:a, eq0:eq, risk:risk, base:risk*eq/(Rd/e), lots:[], fees:0, fund:0, real:0, bumped:false,
      stop:e - d*Rd, best:e, lastAdd:e, adds:0, scaled:false, jH:r.h0 + i + 1, units0:M.init.length };
    M.init.forEach(function(sz){ openLot(p, e, sz); }); return p.lots.length ? p : null; }
  function finish(p, jH, why){ var nw = Math.max(p.eq0 + p.real - p.fees - p.fund, 0); p.out = jH; p.why = why; p.eq1 = nw; p.pnl = nw - p.eq0; p.R = p.eq0 > 0 ? p.pnl/(p.risk*p.eq0) : 0; p.closed = true; return p; }
  // advance through bars up to absolute hour lastH; fundAt(hour) gives the funding rate charged in that hour
  function advance(p, r, fundAt, lastH){ var M = SETUPS[p.key].M, d = p.d;
    while(p.jH <= lastH){ var j = p.jH - r.h0; if(j < 0 || j >= r.c.length) return p;
      var o = r.o[j], hi = r.h[j], lo = r.l[j], c = r.c[j];
      if(o == null || hi == null || lo == null || c == null){ p.jH++; continue; }
      var gross = 0; p.lots.forEach(function(x){ gross += x[0]*o; });
      if(eqNow(p, o) <= C.maint*gross){ p.real = -(p.eq0 - p.fees - p.fund); p.lots = []; return finish(p, p.jH, 'liquidated'); }
      if(d === 1 ? lo <= p.stop : hi >= p.stop){ var px = d === 1 ? Math.min(o, p.stop) : Math.max(o, p.stop); closeQty(p, sumQ(p), px); return finish(p, p.jH, 'stop'); }
      if(M.sc_frac && !p.scaled){ var lv = p.e + d*M.sc_R*p.Rd; if(d === 1 ? hi >= lv : lo <= lv){ closeQty(p, M.sc_frac*sumQ(p), lv); p.scaled = true;
          if(M.be_after_scale && (d === 1 ? p.e > p.stop : p.e < p.stop)) p.stop = p.e; } }
      if(M.pyr_R && p.adds < M.pyr_max){ var la = p.lastAdd + d*M.pyr_R*p.Rd; if(d === 1 ? hi >= la : lo <= la){ if(openLot(p, la, M.add_size)){ p.adds++; p.lastAdd = la; var ns = la - d*p.Rd; if(d === 1 ? ns > p.stop : ns < p.stop) p.stop = ns; } } }
      p.fund += d*sumQ(p)*c*(fundAt(p.jH) || 0);
      p.best = d === 1 ? Math.max(p.best, hi) : Math.min(p.best, lo);
      if(M.trail_atr){ var nt = p.best - d*M.trail_atr*p.atr; if(d === 1 ? nt > p.stop : nt < p.stop) p.stop = nt; }
      if(p.jH - p.iH >= M.max_bars){ closeQty(p, sumQ(p), c); return finish(p, p.jH, 'time'); }
      p.jH++; }
    return p; }
  // full replay over a window, exactly as the research account (one market at a time; strongest signal first)
  function replay(recs, key, tFrom, tTo, start, risk){ var book = [];
    recs.forEach(function(r, ri){ for(var i = Math.max(0, tFrom - r.h0); i < r.c.length && r.h0 + i < tTo; i++){ if(i + 2 >= r.c.length) continue; var s = signalAt(r, i, key); if(s){ s.i = i; s.ri = ri; book.push(s); } } });
    book.sort(function(a, b){ return a.t - b.t || b.pr - a.pr || a.ri - b.ri; });
    var eq = start == null ? C.start : start, rk = risk == null ? C.risk : risk, free = tFrom, out = [];
    for(var k=0; k<book.length; k++){ var s = book[k]; if(s.t >= tTo || eq < 1) break; if(s.t < free) continue; var r = recs[s.ri];
      var p = openPos(r, s.i, s.d, eq, rk, key); if(!p) continue; var F = r.fund || [];
      advance(p, r, function(h){ return F[h - r.h0] || 0; }, r.h0 + r.c.length - 1); if(!p.closed){ closeQty(p, sumQ(p), r.c[r.c.length - 1]); finish(p, r.h0 + r.c.length - 1, 'end'); }
      eq = p.eq1; free = p.out; out.push({ sym:p.sym, hr:p.iH, out:p.out, R:p.R, pnl:p.pnl, eq:p.eq1, why:p.why, adds:p.adds, bumped:p.bumped }); }
    return { end:eq, trades:out }; }
  // the plan for any account: what each unit is, where each level sits
  function plan(key, price, atr, d, acct, riskPct){ var S = SETUPS[key], M = S.M, Rd = M.stop_atr*atr, rp = Rd/price, base = (riskPct/100)*acct/rp;
    var units = M.init.map(function(sz){ var n = sz*base; return { n:Math.max(n, C.minN), bumped:n < C.minN }; }), tot = units.reduce(function(a, u){ return a + u.n; }, 0);
    var add = Math.max(M.add_size*base, C.minN), lv = function(k){ return price + d*k*Rd; };
    return { key:key, d:d, entry:price, Rd:Rd, rp:rp, stop:lv(-1), r1:lv(1), r2:lv(2), r3:lv(3), units:units, unitN:units[0].n, total:tot, add:add, addBumped:M.add_size*base < C.minN,
      riskUsd:tot*rp, riskEff:acct > 0 ? 100*tot*rp/acct : null, lev:acct > 0 ? tot/acct : null, trailDist:M.trail_atr*atr }; }

  // ── live: hourly bars from the climax watch's store; one paper account per setup ──
  function idb(name, stores){ return new Promise(function(res, rej){ var q = indexedDB.open(name, 1);
    q.onupgradeneeded = function(){ var d = q.result; stores.forEach(function(s){ if(!d.objectStoreNames.contains(s[0])) d.createObjectStore(s[0], s[1] ? { keyPath:s[1] } : undefined); }); };
    q.onsuccess = function(){ res(q.result); }; q.onerror = function(){ rej(q.error); }; }); }
  function req(dbp, store, mode, fn){ return dbp.then(function(d){ return new Promise(function(res, rej){ var t = d.transaction(store, mode), s = t.objectStore(store), out = fn(s);
    t.oncomplete = function(){ res(out && typeof out === 'object' && 'onsuccess' in out ? out.result : out); }; t.onerror = function(){ rej(t.error); }; t.onabort = function(){ rej(t.error); }; }); }); }
  var cdb = null, mdb = null;
  function climaxDb(){ return cdb || (cdb = idb(CDB, [['coins', 'sym'], ['meta']])); }    // same stores the climax watch creates
  function ownDb(){ return mdb || (mdb = idb(DBN, [['meta']])); }
  function getMeta(k){ return req(ownDb(), 'meta', 'readonly', function(s){ return s.get(k); }); }
  function putMeta(k, v){ return req(ownDb(), 'meta', 'readwrite', function(s){ s.put(v, k); }); }
  async function getJSON(url){ for(var a=0; a<3; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(10000*(a+1)); continue; } if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 2) throw e; await sleep(1200*(a+1)); } } }
  var state = { busy:false, msg:'', err:null, recs:null, accts:null, coins:0, lastH:null, sig:{} };
  function newAcct(key){ return { key:key, eq:C.start, peak:C.start, pos:null, pend:null, free:FREEZE_H, lastH:FREEZE_H - 1, log:[], weeks:{}, retired:null, gap:0 }; }
  function weekOf(h){ var d = Math.floor(h/24), wd = (d + 3) % 7; return d - wd; }       // Monday 00:00 UTC
  async function fundFor(p){ if(!p.fmap) p.fmap = {}; var from = p.fTo != null ? p.fTo + 1 : p.eH, to = Math.floor(Date.now()/H) - 1; if(from > to) return true;
    var d = await getJSON(FAPI + '/fapi/v1/fundingRate?symbol=' + p.sym + '&startTime=' + from*H + '&endTime=' + ((to + 1)*H - 1) + '&limit=1000');
    if(!Array.isArray(d)) return false; d.forEach(function(x){ var h = Math.floor(+x.fundingTime/H); p.fmap[h] = (p.fmap[h] || 0) + (+x.fundingRate); }); p.fTo = to; return true; }
  function mark(A, h, r){ var v = A.eq; if(A.pos && r){ var j = h - r.h0; if(j >= 0 && j < r.c.length && r.c[j] > 0) v = Math.max(eqNow(A.pos, r.c[j]), 0); } A.weeks[weekOf(h)] = v; A.peak = Math.max(A.peak, v);
    var fall = A.peak > 0 ? 1 - v/A.peak : 0; if(!A.retired && fall >= SETUPS[A.key].retire) A.retired = { h:h, why:'fell ' + Math.round(100*fall) + '% from its peak (limit ' + Math.round(100*SETUPS[A.key].retire) + '%)' }; }
  // process every closed hour since the last check, in order (the paper record enters at the next open even when the app saw it later)
  async function stepAcct(A, recs, by, lastClosed){
    if(A.lastH < lastClosed - 900){ A.gap += lastClosed - 900 - A.lastH; A.lastH = lastClosed - 900; if(A.pos){ A.pos = null; } A.pend = null; }   // bars older than the store keeps: the record notes the gap
    for(var t = A.lastH + 1; t <= lastClosed; t++){
      if(A.pend && t === A.pend.t + 1){ var got = null;
        for(var q=0; q<A.pend.c.length && !got; q++){ var cd = A.pend.c[q], r0 = by[cd.sym]; if(!r0) continue; var i0 = cd.t - r0.h0; if(i0 + 1 >= r0.c.length || !(r0.o[i0 + 1] > 0)) continue; got = openPos(r0, i0, cd.d, A.eq, C.risk, A.key); }
        A.pend = null; if(got){ A.pos = got; } }
      if(A.pos){ var r = by[A.pos.sym]; if(!r){ A.lastH = t; continue; }
        if(!(await fundFor(A.pos))){ return false; }
        var fm = A.pos.fmap; advance(A.pos, r, function(h){ return fm[h] || 0; }, t);
        if(A.pos.closed){ var p = A.pos; A.eq = p.eq1; A.free = p.out; A.log.push({ sym:p.sym, d:p.d, hr:p.iH, e:p.e, out:p.out, R:p.R, pnl:p.pnl, eq:p.eq1, why:p.why, adds:p.adds, bumped:p.bumped, fund:p.fund, fees:p.fees }); A.log = A.log.slice(-1500); A.pos = null; } }
      if(!A.pos && !A.pend && t >= A.free && A.eq >= 1 && !A.retired){ var c = [];
        recs.forEach(function(r2){ var i = t - r2.h0; if(i < 1 || i >= r2.c.length) return; var s = signalAt(r2, i, A.key); if(s) c.push(s); });
        c.sort(function(a, b){ return b.pr - a.pr; }); if(c.length) A.pend = { t:t, c:c.slice(0, 12).map(function(s){ return { sym:s.sym, t:s.t, d:s.d, pr:s.pr }; }) }; }
      mark(A, t, A.pos ? by[A.pos.sym] : null); A.lastH = t; }
    return true; }
  function nwT(x){ var E = window.OMEGA_EDGELIB; if(E && E.nwT) return E.nwT(x, 2); var n = x.length; if(n < 8) return null; var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g = e.reduce(function(a, v){ return a + v*v; }, 0)/n;
    for(var k=1; k<=2; k++){ var s = 0; for(var q=k; q<n; q++) s += e[q]*e[q-k]; g += 2*(1 - k/3)*s/(n - k); } return g > 0 ? m/Math.sqrt(g/n) : null; }
  function verdict(A){ var ks = Object.keys(A.weeks).map(Number).sort(function(a, b){ return a - b; }), thisW = weekOf(Math.floor(Date.now()/H)), done = ks.filter(function(w){ return w < thisW; });
    var vals = [C.start].concat(done.map(function(w){ return A.weeks[w]; })), rets = []; for(var i=1; i<vals.length; i++) if(vals[i-1] > 0) rets.push(vals[i]/vals[i-1] - 1);
    var n = rets.length, mean = n ? rets.reduce(function(a, b){ return a + b; }, 0)/n : null, z = n >= 8 ? nwT(rets) : null, out = { weeks:n, mean:mean, z:z };
    var Fd = SETUPS[A.key].failed; if(Fd){ out.status = 'FAILED'; out.why = 'failed a clean test fixed in advance on 2021–2023 (100 → ' + Fd.end + ', beat ' + Fd.beat + '% of coin-flip accounts); kept as a record, ' + n + ' new weeks so far'; return out; }
    if(A.retired){ out.status = 'RETIRED'; out.why = A.retired.why; }
    else if(n < C.weeks){ out.status = 'TOO EARLY'; out.why = n + ' of ' + C.weeks + ' weeks — nothing is judged before 26'; }
    else if(mean <= 0){ out.status = 'RETIRED'; out.why = 'its weeks average ≤ 0 after ' + n + ' weeks'; A.retired = { h:Math.floor(Date.now()/H), why:out.why }; }
    else if(z != null && z >= C.zBar){ out.status = 'CONFIRMED'; out.why = 'z ' + z.toFixed(2) + ' ≥ 1.96 on ' + n + ' new weeks'; }
    else { out.status = 'RUNNING'; out.why = 'z ' + (z == null ? '—' : z.toFixed(2)) + ' on ' + n + ' weeks; confirmed at 1.96'; }
    return out; }
  async function loadRecs(){ var d = await climaxDb(); var recs = await req(Promise.resolve(d), 'coins', 'readonly', function(s){ return s.getAll(); }), meta = await req(Promise.resolve(d), 'meta', 'readonly', function(s){ return s.get('perps'); });
    var map = (meta && meta.map) || {}; return (recs || []).filter(function(r){ return r && r.c && r.c.length && map[r.sym] != null; }).map(function(r){ r.first = Math.floor(map[r.sym]/H); return r; }); }
  function notify(title, body){ try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification(title, { body:body }); }catch(e){}
    try{ var Al = window.OMEGA_ALERTS, c2 = JSON.parse(localStorage.getItem('omega_alerts_v1') || 'null'); if(Al && Al.push && c2 && c2.url) Al.push(title, body); }catch(e){} }
  async function check(force){ if(state.busy) return 'busy'; if(!force && !cfg().on) return 'off'; state.busy = true; state.err = null; render();
    try{ var nowH = Math.floor(Date.now()/H), lastClosed = nowH - 1, X = window.OMEGA_CLIMAX;
      if(X && X.state){ var cs = X.state(); if((cs.lastH == null || cs.lastH < lastClosed) && !cs.busy){ state.msg = 'Reading the hourly bars (shared with the climax watch)…'; render(); await X.check(true); } }
      var recs = await loadRecs(); if(!recs.length) throw new Error('no hourly bars yet — the climax watch downloads them on its first check');
      var by = {}; recs.forEach(function(r){ by[r.sym] = r; }); state.recs = recs; state.coins = recs.length;
      var saved = await getMeta('accts'), accts = saved && saved.A ? saved : { A:newAcct('A'), B:newAcct('B') };
      var before = { A:(accts.A.pend || {}).t, B:(accts.B.pend || {}).t }, okAll = true;
      for(var k in SETUPS){ var ok1 = await stepAcct(accts[k], recs, by, lastClosed); okAll = okAll && ok1; }
      accts.at = Date.now(); await putMeta('accts', accts); state.accts = accts; state.lastH = lastClosed;
      ['A', 'B'].forEach(function(k2){ var P = accts[k2].pend; if(P && P.t !== before[k2] && P.t >= nowH - 2 && !SETUPS[k2].failed){ var s = P.c[0];
        notify('OMEGA Breakout Desk: ' + s.sym + (s.d > 0 ? ' LONG' : ' SHORT'), SETUPS[k2].name + ' (paper). Enter at the ' + new Date((P.t + 1)*H).toISOString().slice(11, 16) + ' UTC open; the 5-unit plan is on the Breakout Desk.'); } });
      state.msg = 'Checked ' + recs.length + ' perpetuals up to the hour ending ' + new Date((lastClosed + 1)*H).toISOString().slice(11, 16) + ' UTC' + (okAll ? '.' : ' — waiting for funding data for the open trade; it continues on the next check.');
      return state.msg; }
    catch(e){ state.err = String(e && e.message || e); state.msg = 'Breakout Desk stopped: ' + state.err; return state.msg; }
    finally{ state.busy = false; render(); } }
  async function loadSaved(){ try{ var a = await getMeta('accts'); if(a && a.A) state.accts = a; }catch(e){} try{ state.recs = await loadRecs(); state.coins = state.recs.length; }catch(e){} render(); }

  // ── the page ──
  function fmt(x){ if(x == null || !isFinite(x)) return '—'; var a = Math.abs(x); return a >= 1000 ? x.toFixed(1) : a >= 100 ? x.toFixed(2) : a >= 1 ? x.toFixed(4) : x.toPrecision(4); }
  function usd(x){ return x == null || !isFinite(x) ? '—' : x.toFixed(2) + ' USDT'; }
  function hm(h){ return new Date(h*H).toISOString().slice(5, 16).replace('T', ' ') + ' UTC'; }
  function tob(h){ var d = new Date((h - 4)*H); return String(d.getUTCHours()).padStart(2, '0') + ':00 Tobago'; }
  function recOf(sym){ var R = state.recs || []; for(var i=0; i<R.length; i++) if(R[i].sym === sym) return R[i]; return null; }
  // candles + the plan's levels, drawn from the stored bars
  function chart(r, focusH, P, live){ if(!r) return '<div class="bd-nochart">No bars for this coin yet.</div>';
    var end = Math.min(r.c.length - 1, (live && live.closed ? live.out : (focusH != null ? Math.max(focusH, r.h0 + r.c.length - 1) : r.h0 + r.c.length - 1)) - r.h0), beg = Math.max(0, end - 95);
    var lo = Infinity, hi = -Infinity; for(var i=beg; i<=end; i++){ if(r.l[i] != null && r.l[i] < lo) lo = r.l[i]; if(r.h[i] != null && r.h[i] > hi) hi = r.h[i]; }
    var lv = []; if(P){ lv.push(['entry', P.entry, 'var(--text)', 'Entry: ' + (P.key === 'A' ? '5 units' : '1 unit')], ['stop', P.stop, 'var(--bear)', 'Stop −1R'], ['r1', P.r1, 'var(--gold)', P.key === 'A' ? '+1R: close 3, stop to entry, add 1' : '+1R: add 1, stop to entry'], ['r2', P.r2, 'var(--gold)', '+2R: add 1'], ['r3', P.r3, 'var(--gold)', '+3R: add 1']);
      if(live && !live.closed) lv.push(['now', live.stop, 'var(--bear)', 'Stop now']); if(P.box != null) lv.push(['box', P.box, 'var(--violet)', P.d > 0 ? '72h high' : '72h low']); }
    lv.forEach(function(x){ if(x[1] > 0){ lo = Math.min(lo, x[1]); hi = Math.max(hi, x[1]); } }); if(!(hi > lo)) return '<div class="bd-nochart">Not enough bars to draw.</div>';
    var W = 360, Hh = 250, padR = 8, padL = 4, top = 8, bot = 14, n = end - beg + 1, cw = (W - padL - padR)/Math.max(n, 1), pad = (hi - lo)*0.06; lo -= pad; hi += pad;
    var Y = function(v){ return top + (hi - v)/(hi - lo)*(Hh - top - bot); }, X = function(i){ return padL + (i - beg + 0.5)*cw; }, s = '';
    for(i = beg; i <= end; i++){ var o = r.o[i], c = r.c[i], h = r.h[i], l = r.l[i]; if(o == null || c == null || h == null || l == null) continue; var up = c >= o, col = up ? 'var(--bull)' : 'var(--bear)', x = X(i);
      s += '<line x1="' + x.toFixed(1) + '" x2="' + x.toFixed(1) + '" y1="' + Y(h).toFixed(1) + '" y2="' + Y(l).toFixed(1) + '" stroke="' + col + '" stroke-width="0.8"/>' +
        '<rect x="' + (x - cw*0.36).toFixed(1) + '" y="' + Y(Math.max(o, c)).toFixed(1) + '" width="' + Math.max(cw*0.72, 0.8).toFixed(1) + '" height="' + Math.max(Math.abs(Y(o) - Y(c)), 0.8).toFixed(1) + '" fill="' + col + '"' + (up ? ' fill-opacity="0.85"' : '') + '/>'; }
    if(focusH != null && focusH - r.h0 >= beg && focusH - r.h0 <= end){ var fx = X(focusH - r.h0); s += '<line x1="' + fx.toFixed(1) + '" x2="' + fx.toFixed(1) + '" y1="' + top + '" y2="' + (Hh - bot) + '" stroke="var(--violet)" stroke-dasharray="2 3" stroke-width="1"/><text x="' + (fx + 3).toFixed(1) + '" y="' + (Hh - 3) + '" class="bd-ax">signal</text>'; }
    if(P && P.entry > 0 && focusH != null){ var zx = Math.max(X(Math.max(focusH - r.h0, beg)) - cw/2, padL), zw = (W - padR) - zx;
      if(zw > 2){ s = '<rect x="' + zx.toFixed(1) + '" y="' + Math.min(Y(P.entry), Y(P.stop)).toFixed(1) + '" width="' + zw.toFixed(1) + '" height="' + Math.abs(Y(P.entry) - Y(P.stop)).toFixed(1) + '" fill="var(--bear)" fill-opacity="0.10"/>' +
        '<rect x="' + zx.toFixed(1) + '" y="' + Math.min(Y(P.entry), Y(P.r3)).toFixed(1) + '" width="' + zw.toFixed(1) + '" height="' + Math.abs(Y(P.entry) - Y(P.r3)).toFixed(1) + '" fill="var(--bull)" fill-opacity="0.07"/>' + s; } }
    var lab = '', used = [];
    lv.forEach(function(x2){ if(!(x2[1] > 0)) return; var y = Y(x2[1]); s += '<line data-level="' + x2[0] + '" x1="' + padL + '" x2="' + (W - padR) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" stroke="' + x2[2] + '" stroke-width="' + (x2[0] === 'entry' ? 1.3 : 1) + '"' + (x2[0] === 'now' || x2[0] === 'box' ? ' stroke-dasharray="5 3"' : (x2[0][0] === 'r' ? ' stroke-dasharray="1.5 2.5"' : '')) + '/>';
      var ty = y - 3; used.forEach(function(u){ if(Math.abs(u - ty) < 10) ty = u - 10; }); used.push(ty); lab += '<text x="' + (W - padR - 2) + '" y="' + Math.max(ty, 9).toFixed(1) + '" text-anchor="end" class="bd-lv" fill="' + x2[2] + '">' + esc(x2[3]) + ' ' + esc(fmt(x2[1])) + '</text>'; });
    return '<svg class="bd-chart" viewBox="0 0 ' + W + ' ' + Hh + '" role="img" aria-label="' + esc(r.sym) + ' hourly candles with the plan">' + s + lab + '<text x="' + padL + '" y="' + (top + 2) + '" class="bd-ax" dominant-baseline="hanging">' + esc(r.sym) + ' · 1h · last ' + n + ' hours</text></svg>'; }
  function pill(t, cls){ return '<span class="bd-pill ' + cls + '">' + t + '</span>'; }
  function setupCard(key){ var S = SETUPS[key], A = state.accts && state.accts[key], c = cfg(), v = A ? verdict(A) : (S.failed ? { status:'FAILED', why:'failed a clean test fixed in advance on 2021–2023 (100 → ' + S.failed.end + ')', weeks:0 } : { status:'TOO EARLY', why:'not started', weeks:0 }), h = '', nowH = Math.floor(Date.now()/H);
    var pos = A && A.pos, pend = A && A.pend, last = A && A.log.length ? A.log[A.log.length - 1] : null, sig = null, r = null, P = null, live = null, focusH = null, head = '';
    if(pend){ sig = pend.c[0]; r = recOf(sig.sym); var i = r ? sig.t - r.h0 : -1; if(r && i >= 0 && i < r.c.length){ var a = atrOf(r)[i]; P = plan(key, r.c[i], a, sig.d, +c.acct || 100, +c.risk || 1); if(key === 'A'){ var m = measure(r, i); if(m) P.box = sig.d > 0 ? m.hi72 : m.lo72; } }
      focusH = sig.t; head = pill('SIGNAL — ' + (sig.d > 0 ? 'LONG ' : 'SHORT ') + esc(sig.sym), sig.d > 0 ? 'go' : 'short') + '<div class="bd-when">Enter at the <b>' + hm(sig.t + 1).slice(6) + '</b> open (' + tob(sig.t + 1) + ').' + (pend.c.length > 1 ? ' Strongest of ' + pend.c.length + ' setups that hour.' : '') + '</div>'; }
    else if(pos){ r = recOf(pos.sym); live = pos; P = plan(key, pos.e, pos.atr, pos.d, +c.acct || 100, +c.risk || 1); var j = r ? r.c.length - 1 : -1, cl = r && j >= 0 ? r.c[j] : null;
      focusH = pos.iH; head = pill('IN A TRADE — ' + (pos.d > 0 ? 'LONG ' : 'SHORT ') + esc(pos.sym), 'live') + '<div class="bd-when">Entered ' + hm(pos.eH) + ' at ' + fmt(pos.e) + (cl ? '; now ' + fmt(cl) + ' (' + (pos.d*(cl/pos.e - 1)*100).toFixed(2) + '%)' : '') + '. Units held: ' + sumQ(pos).toPrecision(3) + ' coins' + (pos.scaled ? ', 3 of 5 banked' : '') + (pos.adds ? ', ' + pos.adds + ' added' : '') + '. Stop now ' + fmt(pos.stop) + '. Closes by ' + hm(pos.iH + S.M.max_bars + 1) + '.</div>'; }
    else { head = pill(S.failed ? 'RECORD ONLY' : (A && A.retired ? 'RETIRED' : 'WAITING'), S.failed || (A && A.retired) ? 'off' : 'wait') + '<div class="bd-when">' + (A && A.retired ? esc(A.retired.why) + '.' : 'No setup on the last checked hour. It only fires on hours opening 13:00–20:00 UTC (09:00–16:00 Tobago).') + '</div>';
      if(last){ r = recOf(last.sym); focusH = last.hr; var i2 = r ? last.hr - r.h0 : -1; if(r && i2 >= 0 && i2 < r.c.length){ P = plan(key, last.e, atrOf(r)[i2], last.d, +c.acct || 100, +c.risk || 1); live = { closed:true, out:last.out }; } } }
    h += '<div class="bd-setup" data-setup="' + key + '"><div class="bd-shead"><div><div class="bd-kicker">Setup ' + key + ' · ' + esc(S.sub) + '</div><h3>' + esc(S.name) + '</h3></div>' + pill(v.status, v.status === 'CONFIRMED' ? 'go' : (v.status === 'RETIRED' || v.status === 'FAILED') ? 'off' : 'wait') + '</div>' + head;
    h += chart(r, focusH, P, live);
    if(P && (pend || pos)){ var bump = P.units.some(function(u){ return u.bumped; });
      h += '<div class="bd-plan"><div class="bd-ptitle">Your plan for ' + usd(+c.acct || 100) + ' at ' + (+c.risk || 1) + '% risk' + (pos ? ' (levels from the paper entry)' : ' (levels from the signal close; your entry is the next open)') + '</div><table class="bd-tab"><tr><th>Step</th><th>Price</th><th>Order</th></tr>' +
        '<tr><td>Entry</td><td>' + fmt(P.entry) + '</td><td>' + (key === 'A' ? '5 × ' + usd(P.unitN) : usd(P.unitN)) + (P.d > 0 ? ' buy' : ' sell') + '</td></tr>' +
        '<tr class="bd-r"><td>Stop (−1R)</td><td>' + fmt(P.stop) + '</td><td>stop-market for everything</td></tr>' +
        '<tr><td>+1R</td><td>' + fmt(P.r1) + '</td><td>' + (key === 'A' ? 'close 3 units; stop to entry; add 1 (' + usd(P.add) + ')' : 'add 1 (' + usd(P.add) + '); stop to entry') + '</td></tr>' +
        '<tr><td>+2R</td><td>' + fmt(P.r2) + '</td><td>add 1; stop to +1R</td></tr><tr><td>+3R</td><td>' + fmt(P.r3) + '</td><td>add 1; stop to +2R</td></tr></table>' +
        '<p class="hint">Trail: the stop never sits more than ' + fmt(P.trailDist) + ' (3 ATR) from the best price since entry. Out after 7 days whatever happens. Risk if the first stop is hit: ' + usd(P.riskUsd) + ' (' + (P.riskEff == null ? '—' : P.riskEff.toFixed(1)) + '% of the account); position ' + usd(P.total) + ' (' + (P.lev == null ? '—' : P.lev.toFixed(1)) + '× the account).' +
        (bump || P.addBumped ? ' <b class="bd-warn">Binance’s 5 USDT minimum order makes this bigger than ' + (+c.risk || 1) + '%: on a small account the minimum, not your plan, sets the risk.</b>' : '') + '</p></div>'; }
    var E = S.ev; h += '<div class="bd-acct">' + acctLine(A, v) + '</div>' +
      (S.failed ? '<div class="bd-fail"><b>FAILED a clean test.</b> Run once on 2021–2023 with the rules frozen and the pass mark written down first: 100 → <b>' + S.failed.end + '</b> USDT (each year from 100: ' + S.failed.yrs + '), beating only ' + S.failed.beat + '% of coin-flip accounts (needed 95%). Do not trade it. The paper account keeps running as a record only.</div>' : '') +
      '<details class="bd-ev"><summary>What the research found before the clean test</summary><p class="hint">Unseen half (Jul 2025 – Oct 2026), 100 USDT, one market at a time: <b>' + E.end + '</b> after ' + E.trades + ' trades; worst fall ' + E.dd + '%. <b>Correction:</b> ' + (S.key === 'A' ? 'that figure came from Binance’s 5 USDT minimum rounding 238 of 623 trades above 1% risk; at a true 1% it was about ' + E.true1 + '.' : 'at a true 1% it was about ' + E.true1 + ' (the minimum barely mattered here).') + ' 6-month accounts started each month: ' + E.win6 + ' grew (typical ×' + E.med6 + ', worst ×' + E.worst6 + ', best ×' + E.best6 + '). Months: ' + E.mPos + '% positive, average ' + (E.mAvg > 0 ? '+' : '') + E.mAvg + '%, worst ' + E.mWorst + '%. Same signals with the direction chosen by coin flip: typical end ' + E.flipMed + '; the real one beat ' + E.flip + '% of 100. Risk per trade: ' + E.ladder + ' — more risk, less money. Other management on this entry: ' + E.other + '.</p>' +
      '<p class="hint"><b>Not proven:</b> it was the best of 10 setup-and-method pairs, and luck alone gives a result this good about 1 time in 3. Counted week by week, the sweep’s finalists were indistinguishable from chance. Judged only on weeks after ' + hm(FREEZE_H).slice(0, 5) + ' 2026: confirmed at z ≥ 1.96 after 26 weeks; retired if the weeks average ≤ 0, or on a fall of ' + Math.round(100*S.retire) + '% from the peak (1.5× the worst research fall).</p></details>';
    return h + '</div>'; }
  function acctLine(A, v){ if(!A) return '<div class="bd-stat"><span>Paper account</span><b>' + usd(C.start) + '</b></div><p class="hint">Starts on the first check.</p>';
    var L = A.log, n = L.length, wins = L.filter(function(x){ return x.pnl > 0; }).length, avgR = n ? L.reduce(function(a, x){ return a + x.R; }, 0)/n : null, ks = Object.keys(A.weeks).map(Number).sort(function(a, b){ return a - b; });
    var pts = [C.start].concat(ks.map(function(k){ return A.weeks[k]; })), spark = '';
    if(pts.length > 1){ var mn = Math.min.apply(null, pts), mx = Math.max.apply(null, pts); if(mx === mn){ mx += 1; mn -= 1; } spark = '<svg class="bd-spark" viewBox="0 0 120 30" preserveAspectRatio="none"><polyline fill="none" stroke="var(--gold)" stroke-width="1.5" points="' + pts.map(function(p, i){ return (i*120/(pts.length - 1)).toFixed(1) + ',' + (28 - (p - mn)/(mx - mn)*26).toFixed(1); }).join(' ') + '"/></svg>'; }
    return '<div class="bd-stats"><div class="bd-stat"><span>Paper account</span><b>' + usd(A.eq) + '</b></div><div class="bd-stat"><span>Trades</span><b>' + n + '</b></div><div class="bd-stat"><span>Winners</span><b>' + (n ? Math.round(100*wins/n) + '%' : '—') + '</b></div><div class="bd-stat"><span>Average</span><b>' + (avgR == null ? '—' : (avgR >= 0 ? '+' : '') + avgR.toFixed(2) + 'R') + '</b></div></div>' + spark +
      '<p class="hint">Since ' + hm(FREEZE_H).slice(0, 5) + ' 2026, 1% risk, one market at a time. ' + esc(v.why) + '.' + (A.gap ? ' ' + A.gap + ' hours were missed while the app was closed for more than 37 days.' : '') + '</p>' +
      (n ? '<details><summary class="hint">Last paper trades</summary><ul class="hint bd-list">' + L.slice(-8).reverse().map(function(x){ return '<li>' + esc(x.sym) + ' ' + (x.d > 0 ? 'long' : 'short') + ' ' + hm(x.hr + 1) + ': ' + (x.R >= 0 ? '+' : '') + x.R.toFixed(2) + 'R, ' + (x.pnl >= 0 ? '+' : '') + x.pnl.toFixed(2) + ' USDT (' + x.why + (x.adds ? ', ' + x.adds + ' adds' : '') + ')</li>'; }).join('') + '</ul></details>' : ''); }
  function css(){ if(el('bdeskCss')) return; var st = document.createElement('style'); st.id = 'bdeskCss';
    st.textContent = '.bd-start{border:1px solid var(--gold);border-radius:12px;padding:12px 14px;margin:0 0 14px;background:linear-gradient(135deg,rgba(201,162,75,.10),rgba(155,140,255,.05));}' +
      '.bd-start h3{margin:0 0 6px;color:var(--gold);font-size:15px;}.bd-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;}' +
      '.bd-setup{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:12px 12px 8px;min-width:0;}.bd-shead{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;}' +
      '.bd-shead h3{margin:2px 0 6px;font-size:16px;color:var(--text);}.bd-kicker{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim);}' +
      '.bd-pill{display:inline-block;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.04em;white-space:nowrap;}.bd-pill.go{background:rgba(37,211,139,.16);color:var(--bull);}' +
      '.bd-pill.short{background:rgba(255,77,94,.16);color:var(--bear);}.bd-pill.live{background:rgba(201,162,75,.18);color:var(--gold);}.bd-pill.wait{background:var(--panel2);color:var(--text-dim);}.bd-pill.off{background:rgba(255,77,94,.10);color:var(--bear);}' +
      '.bd-when{font-size:13px;color:var(--text);margin:6px 0 8px;line-height:1.45;}.bd-chart{width:100%;height:auto;display:block;background:var(--bg);border:1px solid var(--border);border-radius:8px;}' +
      '.bd-lv{font-size:8px;font-weight:600;paint-order:stroke;stroke:var(--bg);stroke-width:2.5px;}.bd-ax{font-size:8px;fill:var(--text-dim);}.bd-nochart{padding:28px 8px;text-align:center;color:var(--text-dim);font-size:12px;border:1px dashed var(--border);border-radius:8px;}' +
      '.bd-plan{margin-top:10px;}.bd-ptitle{font-size:12px;color:var(--text-dim);margin-bottom:4px;}.bd-tab{width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed;}.bd-tab th:nth-child(1){width:23%;}.bd-tab th:nth-child(2){width:22%;}.bd-tab th{text-align:left;color:var(--text-dim);font-weight:600;border-bottom:1px solid var(--border);padding:4px 4px;}' +
      '.bd-tab td{padding:4px 4px;border-bottom:1px solid var(--border);vertical-align:top;overflow-wrap:anywhere;white-space:normal;}.bd-tab tr.bd-r td{color:var(--bear);}.bd-warn{color:var(--amber);}.bd-fail{margin:10px 0 0;padding:8px 10px;border:1px solid var(--bear);border-radius:8px;background:rgba(255,77,94,.08);font-size:12.5px;line-height:1.5;}' +
      '.bd-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:10px;}.bd-stat{background:var(--panel2);border-radius:8px;padding:6px 8px;}.bd-stat span{display:block;font-size:10px;color:var(--text-dim);}.bd-stat b{font-size:13px;}' +
      '.bd-spark{width:100%;height:30px;margin-top:6px;}.bd-ev summary,.bd-acct summary{cursor:pointer;font-size:12px;color:var(--text-dim);margin-top:6px;}.bd-list{margin:4px 0 0;padding-left:18px;}' +
      '.bd-calc{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin:8px 0 0;}.bd-calc label{font-size:11px;color:var(--text-dim);display:flex;flex-direction:column;gap:3px;}.bd-calc input{width:110px;}';
    document.head.appendChild(st); }
  function startHere(){ var A = state.accts, c = cfg(), sigs = [], live = [];
    if(A) ['A', 'B'].forEach(function(k){ if(A[k].pend) sigs.push(k); if(A[k].pos) live.push(k); });
    var t = sigs.length ? '<b>' + sigs.map(function(k){ var s = A[k].pend.c[0]; return 'Setup ' + k + ' (failed, record only): ' + (s.d > 0 ? 'LONG ' : 'SHORT ') + esc(s.sym) + ' at the ' + hm(A[k].pend.t + 1).slice(6) + ' open'; }).join(' · ') + '</b>. The paper account takes it; do not trade it.'
      : live.length ? 'A paper trade is open (' + live.map(function(k){ return 'Setup ' + k + ' ' + esc(A[k].pos.sym); }).join(', ') + '). Its stop moves as the chart shows; nothing new is taken until it closes.'
      : 'Nothing to do. Both setups wait for a closed hour between 13:00 and 20:00 UTC (09:00–16:00 Tobago). Keep the app open in those hours, or turn on alerts.';
    return '<div class="bd-start"><h3>Start here</h3><div class="bd-when" style="margin:0 0 6px;">' + t + '</div>' +
      '<div class="bd-calc"><label>Your account (USDT)<input type="number" min="5" step="1" data-bdesk="acct" value="' + esc(c.acct || 100) + '"></label><label>Risk per trade (%)<input type="number" min="0.1" max="10" step="0.1" data-bdesk="risk" value="' + esc(c.risk || 1) + '"></label>' +
      '<button class="btn-outline" type="button" data-bdesk="now"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Checking…' : 'Check now') + '</button>' + (typeof Notification !== 'undefined' && Notification.permission !== 'granted' ? '<button class="btn-outline" type="button" data-bdesk="alerts">Turn on alerts</button>' : '') + '</div>' +
      '<p class="hint" style="margin:8px 0 0;">Paper only — OMEGA places no orders. <b>FAILED a clean test:</b> both setups lost money on 2021–2023 when tested once with frozen rules (A 100 → 49, B 100 → 27), worse than most coin-flip accounts. They stay here as a record and as a tool for drawing a plan, not as signals to trade. Research: 1% risk did best; 5% and 10% lost money; from 10 USDT the 5 USDT minimum order forces about 10% risk and half the starts went to zero. The next clean test, gold hourly, is below.</p></div>'; }
  function html(){ var c = cfg();
    return startHere() + '<div class="bd-grid">' + setupCard('A') + setupCard('B') + '</div>' +
      '<p class="hint" style="margin:10px 0 0;">' + esc(state.msg || (state.lastH ? 'Last checked up to ' + hm(state.lastH + 1) + '.' : 'Not checked yet.')) + ' Watching ' + (state.coins || '—') + ' perpetuals with the climax watch’s hourly bars.</p>' +
      '<label class="checkbox-row" style="margin:8px 0 0;"><input type="checkbox" data-bdesk="on"' + (c.on ? ' checked' : '') + '> Check every hour while the app is open</label>'; }
  function sigLine(){ var A = state.accts; if(!A) return ''; var p = []; ['A', 'B'].forEach(function(k){ if(A[k].pend){ var s = A[k].pend.c[0]; p.push('<b>' + SETUPS[k].name + '</b>: ' + (s.d > 0 ? 'LONG ' : 'SHORT ') + esc(s.sym) + ' at the ' + hm(A[k].pend.t + 1).slice(6) + ' open'); } else if(A[k].pos) p.push('<b>' + SETUPS[k].name + '</b>: in ' + esc(A[k].pos.sym)); });
    return '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">Breakout Desk — two setups that FAILED a clean test (record only)</h2><p class="hint" style="margin:0 0 8px;">' + (p.length ? p.join(' · ') : 'No breakout or burst signal on the last checked hour.') + ' Both failed a one-shot test on 2021–2023; not signals to trade.</p><button class="btn-outline" type="button" onclick="navigate(\'bdesk\')">Open the Breakout Desk</button></div>'; }
  function render(){ var host = el('bdeskBody'); if(host){ css(); host.innerHTML = html();
      Array.prototype.forEach.call(host.querySelectorAll('[data-bdesk]'), function(b){ var k = b.getAttribute('data-bdesk');
        if(k === 'now') b.onclick = function(){ check(true); }; if(k === 'on') b.onchange = function(){ var v = cfg(); v.on = !!b.checked; setCfg(v); render(); };
        if(k === 'acct' || k === 'risk') b.onchange = function(){ var v = cfg(), x = parseFloat(b.value); if(isFinite(x) && x > 0){ v[k] = k === 'risk' ? Math.min(Math.max(x, 0.1), 10) : Math.max(x, 1); setCfg(v); } render(); };
        if(k === 'alerts') b.onclick = function(){ try{ Notification.requestPermission().then(function(){ render(); }); }catch(e){} }; }); }
    var s2 = el('bdeskSigBody'); if(s2) s2.innerHTML = sigLine();
    var badge = el('sbBadge-bdesk'); if(badge){ var A = state.accts, n = A ? ['A', 'B'].filter(function(k){ return A[k].pend && !SETUPS[k].failed; }).length : 0; badge.textContent = n ? String(n) : ''; } }
  function due(){ var nowH = Math.floor(Date.now()/H); return cfg().on && !state.busy && (state.lastH == null || state.lastH < nowH - 1) && (Date.now() % H) > 140e3; }
  var started = false; function start(){ if(started) return; started = true; loadSaved().then(function(){ setInterval(function(){ if(due()) check(false); }, 60e3); setTimeout(function(){ if(due()) check(false); }, 90e3); }); }
  function wire(){ if(el('bdeskBody')){ render(); start(); return true; } return false; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_BDESK = { check:check, render:render, state:function(){ return state; }, SETUPS:SETUPS, C:C, FREEZE_H:FREEZE_H,
    _:{ measure:measure, signalAt:signalAt, openPos:openPos, advance:advance, replay:replay, plan:plan, atrOf:atrOf, stepAcct:stepAcct, newAcct:newAcct, verdict:verdict, weekOf:weekOf, chart:chart, html:html, setupCard:setupCard } };
})();
</script>
