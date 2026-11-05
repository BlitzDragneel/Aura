<script>/* ═══ ROUND 12 WINNERS (v6.5.69) — the funding harvest plus RSI(5) dip-buying: the only 2 of 600 known strategies and 100 combinations to pass on 125 untouched coins; frozen, paper only ═══
   Round 12 (PLAN12) tested 600 published rules on the 25 studied coins, the 140 survivors' best on 140 other coins, then
   100 combinations and 5 own ideas, and finally the 100 finalists once on 125 coins no round had touched (bar z 3.29).
   Two passed, both built from the same two parts:
   · C028 "harvest + dip-buying": half the account in the 10-pair funding harvest (spot + short perpetual), half in RSI(5)
     dip-buying (long a coin's perpetual when its 5-day RSI falls under 10, sell when it rises over 50; sized to 20%
     yearly volatility, 1/N of that half per coin). Untouched coins: +4.0% a year over the market, z 3.31, worst −3.6%.
   · C016 "five-part blend" (weights fixed from volatility on the design data): harvest 15 pairs at a 0.20% hurdle 53.6%,
     dip-buying 23.4%, long when a coin's 3-day funding is negative 12.7%, Supertrend 7/2 long/short 5.2%, SMA 10/50
     long/short 5.1%. Untouched coins: +4.1% a year, z 3.90, worst −2.6%.
   Computed here exactly as in the research code (r12lib/r12engine: same indicators, same pandas smoothing, same costs:
   0.06% a side on perpetuals, 0.11% + 0.06% on harvest pairs, funding paid by longs), on the 25 coins' stored daily bars
   and funding. Frozen 18 Oct 2026; judged on forward weeks. Paper only: OMEGA never places an order. */
(function(){
  'use strict';
  var KEY = 'omega_r12_v1', DAY = 86400e3, PERP = 0.0006, SPOT = 0.0011, FREEZE_DAY = Date.UTC(2026, 9, 18)/DAY, FWD_MIN = 26, FWD_FULL = 52, FWD_BAR = 1.96, FWD_STOP = -0.10, S0_DAY = Date.UTC(2020, 0, 1)/DAY;
  var PARTS = { H10:{ name:'funding harvest, 10 pairs (0.10% hurdle)', kind:'harvest', k:10, hurdle:0.001 }, H15:{ name:'funding harvest, 15 pairs (0.20% hurdle)', kind:'harvest', k:15, hurdle:0.002 },
    DIP:{ name:'RSI(5) dip-buying, long only', kind:'ts' }, FNEG:{ name:'long when 3-day funding is negative', kind:'ts' }, ST:{ name:'Supertrend 7/2, long/short', kind:'ts' }, SMA:{ name:'SMA 10/50, long/short', kind:'ts' } };
  var BLENDS = {
    C028:{ title:'Harvest + dip-buying', parts:[['H10', 0.5], ['DIP', 0.5]], final:{ alpha:3.95, z:3.31, costs2x:2.73, worst:-3.6, years:[['2022', -1.2], ['2023', 5.2], ['2024', 9.0], ['2025', 5.8], ['2026*', -0.4]] }, design:{ alpha:7.6, z:7.11 }, valid:{ alpha:7.0, z:5.37, worst:-1.8 } },
    C016:{ title:'Five-part blend', parts:[['H15', 0.5356612887226874], ['DIP', 0.234405227849473], ['FNEG', 0.12729183230240926], ['ST', 0.05171081473777347], ['SMA', 0.050930836387656796]], final:{ alpha:4.12, z:3.9, costs2x:3.12, worst:-2.6, years:[['2022', 0.4], ['2023', 5.6], ['2024', 8.3], ['2025', 5.0], ['2026*', -0.2]] }, design:{ alpha:8.2, z:6.99 }, valid:{ alpha:8.4, z:5.57, worst:-0.8 } } };
  var RESEARCH = { plan:'PLAN12, written 18 Oct 2026 before any market data was run; the untouched coins’ file was opened once, after the 100 finalists were frozen', stages:[
      ['600 known strategies (52 families) on the 25 studied coins', '140 passed the screen (alpha z ≥ 1.65, up in 4 of 7 years, costs doubled positive)'],
      ['the 140 on 140 other coins', '14 passed (z ≥ 3.38): 12 harvest variants, carry on 1-day funding, RSI(5) dip-buying'],
      ['100 combinations + 5 own ideas, built from those results', '84 + 4 passed the design check; 100 unique finalists'],
      ['the 100 finalists once on 125 untouched coins (Mar 2022 – Oct 2026)', '2 passed (z ≥ 3.29): both harvest + dip-buying'] ],
    failedFinal:'On the untouched coins: carry on 1-day funding lost 4% a year with a −78% fall (its stage-2 pass did not hold); the harvest alone made +5.7% (z 2.75); dip-buying alone +2.2% (z 1.76); every trend combination +2 to +12% a year but z under 2.3.',
    caution:'About 4% a year over the market, very steady: real but modest. In July 2026 one small coin’s funding turned violently negative during a squeeze (−77% in a week, charged hourly) and cost the 10-pair harvest 7.7% of the account in one week on the untouched coins; this card flags a held coin whose funding turns sharply negative.' };
  function el(id){ return document.getElementById(id); }
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function lsGet(k, d){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v && typeof v === 'object' && !Array.isArray(v) ? v : d; }catch(e){ return d; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function pct(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(100*v).toFixed(d == null ? 1 : d) + '%'; }
  function dayStr(d){ return new Date(d*DAY).toISOString().slice(0, 10); }
  var st = lsGet(KEY, null) || { v:1, rec:{ C028:{}, C016:{} }, retired:{}, res:null, noted:'' }, run = { busy:false, msg:'' };
  if(!st.rec) st.rec = { C028:{}, C016:{} }; if(!st.retired) st.retired = {};

  // ── the day grid: every coin on the same days (as the research code's DataFrames) ──
  function grid(data, endDay){
    var syms = Object.keys(data || {}).filter(function(s){ var x = data[s]; return x && x.c && x.c.length; }).sort(), K0 = Infinity, K1 = -Infinity;
    syms.forEach(function(s){ var x = data[s]; if(x.k0 < K0) K0 = x.k0; if(x.k0 + x.c.length - 1 > K1) K1 = x.k0 + x.c.length - 1; });
    if(endDay != null && K1 > endDay - 1) K1 = endDay - 1;
    var T = K1 - K0 + 1, G = { syms:syms, K0:K0, T:T, c:[], h:[], l:[], ff:[], fc:[], E:[], fund:[], f1:[] };
    syms.forEach(function(s){ var x = data[s], c = new Float64Array(T).fill(NaN), h = new Float64Array(T).fill(NaN), l = new Float64Array(T).fill(NaN), ff = new Float64Array(T), fc = new Float64Array(T), E = new Uint8Array(T);
      for(var i=0; i<x.c.length; i++){ var t = x.k0 + i - K0; if(t < 0 || t >= T) continue; var v = x.c[i]; if(v > 0) c[t] = +v; if(x.h && x.h[i] > 0) h[t] = +x.h[i]; if(x.l && x.l[i] > 0) l[t] = +x.l[i]; }
      var f0 = null, f1 = null, ev = (x.fund || []).filter(function(q){ return q && isFinite(+q[0]) && isFinite(+q[1]); });
      ev.forEach(function(q){ var tm = +q[0], d = Math.floor(tm/DAY), t = d - K0; if(f0 == null || tm < f0) f0 = tm; if(f1 == null || tm > f1) f1 = tm; if(t >= 0 && t < T){ ff[t] += +q[1]; fc[t] += 1; } });
      var f0d = f0 == null ? null : Math.floor(f0/DAY);
      for(var t2=0; t2<T; t2++) E[t2] = (f0d != null && t2 + K0 > f0d && c[t2] === c[t2]) ? 1 : 0;
      G.c.push(c); G.h.push(h); G.l.push(l); G.ff.push(ff); G.fc.push(fc); G.E.push(E); G.fund.push(ev); G.f1.push(f1); });
    G.N = new Float64Array(T); for(var t=0; t<T; t++){ var n = 0; for(var j=0; j<syms.length; j++) n += G.E[j][t]; G.N[t] = n; }
    return G; }
  // ── indicators (pandas semantics: rolling windows need every value present; ewm adjust=False as pandas computes it) ──
  function rollMean(x, n){ var T = x.length, o = new Float64Array(T).fill(NaN); for(var t=n-1; t<T; t++){ var s = 0, ok = true; for(var i=t-n+1; i<=t; i++){ if(x[i] !== x[i]){ ok = false; break; } s += x[i]; } if(ok) o[t] = s/n; } return o; }
  function rollStd(x, n){ var T = x.length, o = new Float64Array(T).fill(NaN); for(var t=n-1; t<T; t++){ var s = 0, ok = true; for(var i=t-n+1; i<=t; i++){ if(x[i] !== x[i]){ ok = false; break; } s += x[i]; } if(!ok) continue; var m = s/n, q = 0; for(var k=t-n+1; k<=t; k++) q += (x[k] - m)*(x[k] - m); o[t] = Math.sqrt(q/(n - 1)); } return o; }
  function rollSum(x, n){ var T = x.length, o = new Float64Array(T).fill(NaN); for(var t=n-1; t<T; t++){ var s = 0; for(var i=t-n+1; i<=t; i++) s += x[i]; o[t] = s; } return o; }
  function ewmA(x, alpha, minp){ var T = x.length, o = new Float64Array(T).fill(NaN); if(!T) return o; var w = x[0], oldwt = 1, nobs = (x[0] === x[0]) ? 1 : 0; o[0] = nobs >= minp ? w : NaN;
    for(var i=1; i<T; i++){ var cur = x[i], obs = cur === cur; if(obs) nobs++;
      if(w === w){ oldwt *= (1 - alpha); if(obs){ if(w !== cur) w = (oldwt*w + alpha*cur)/(oldwt + alpha); oldwt = 1; } }
      else if(obs) w = cur;
      o[i] = nobs >= minp ? w : NaN; }
    return o; }
  function pchg(c){ var T = c.length, r = new Float64Array(T).fill(NaN); for(var t=1; t<T; t++) if(c[t] === c[t] && c[t-1] === c[t-1]) r[t] = c[t]/c[t-1] - 1; return r; }
  function rsi(c, p){ var T = c.length, up = new Float64Array(T).fill(NaN), dn = new Float64Array(T).fill(NaN);
    for(var t=1; t<T; t++) if(c[t] === c[t] && c[t-1] === c[t-1]){ var d = c[t] - c[t-1]; up[t] = d > 0 ? d : 0; dn[t] = d < 0 ? -d : 0; }
    var U = ewmA(up, 1/p, p), D = ewmA(dn, 1/p, p), o = new Float64Array(T).fill(NaN); for(var i=0; i<T; i++){ var dd = D[i] === 0 ? NaN : D[i]; o[i] = 100 - 100/(1 + U[i]/dd); } return o; }
  function state(T, el, xl, es, xs){ var o = new Float64Array(T), p = 0; for(var t=0; t<T; t++){ if(p === 1 && xl(t)) p = 0; if(p === -1 && xs(t)) p = 0; if(p === 0){ if(el(t)) p = 1; else if(es(t)) p = -1; } o[t] = p; } return o; }
  function atr(c, h, l, n){ var T = c.length, tr = new Float64Array(T).fill(NaN);
    for(var t=0; t<T; t++){ var c1 = t ? c[t-1] : NaN, a = h[t] - l[t], b = Math.abs(h[t] - c1), d = Math.abs(l[t] - c1), m = NaN; [a, b, d].forEach(function(v){ if(v === v && !(m >= v)) m = v; }); tr[t] = m; }
    return ewmA(tr, 1/n, n); }
  // ── the parts' signals per coin (long/short form before the long-only clip) ──
  var SIG = {
    DIP:function(G, j){ var R = rsi(G.c[j], 5); return state(G.T, function(t){ return R[t] < 10; }, function(t){ return R[t] > 50; }, function(t){ return R[t] > 90; }, function(t){ return R[t] < 50; }); },
    FNEG:function(G, j){ var ff = G.ff[j], fc = G.fc[j], s3 = rollSum(ff, 3), n3 = rollSum(fc, 3), o = new Float64Array(G.T).fill(NaN); for(var t=0; t<G.T; t++) if(s3[t] === s3[t] && n3[t] > 0) o[t] = s3[t] < 0 ? 1 : 0; return o; },
    ST:function(G, j){ var c = G.c[j], h = G.h[j], l = G.l[j], A = atr(c, h, l, 7), T = G.T, o = new Float64Array(T).fill(NaN), fu = NaN, fl = NaN, dir = 1, k = 2;
      for(var t=0; t<T; t++){ var mid = (h[t] + l[t])/2, u = mid + k*A[t], b = mid - k*A[t], cc = c[t], pc = t ? c[t-1] : NaN;
        fu = (fu !== fu || u < fu || pc > fu) ? u : fu; fl = (fl !== fl || b > fl || pc < fl) ? b : fl;
        dir = cc > fu ? 1 : (cc < fl ? -1 : dir); o[t] = (isFinite(A[t]) && isFinite(cc)) ? dir : NaN; }
      return o; },
    SMA:function(G, j){ var a = rollMean(G.c[j], 10), b = rollMean(G.c[j], 50), o = new Float64Array(G.T).fill(NaN); for(var t=0; t<G.T; t++){ var d = a[t] - b[t]; if(d === d) o[t] = d > 0 ? 1 : (d < 0 ? -1 : 0); } return o; } };
  var LONG_ONLY = { DIP:1, FNEG:1 };
  // ── a time-series part's weights (vol-sized, re-sized only on a sign change or a change over 0.15, 1/N per coin) and daily returns ──
  function tsPart(G, name){ var T = G.T, n = G.syms.length, W = [], ret = new Float64Array(T);
    for(var j=0; j<n; j++){ var s = SIG[name](G, j), r = pchg(G.c[j]), v = rollStd(r, 20), w = new Float64Array(T), prev = 0;
      for(var t=0; t<T; t++){ var sz = 0.2/(v[t]*Math.sqrt(365.25)); sz = sz !== sz ? NaN : Math.min(1.5, Math.max(0.25, sz)); var sv = s[t]; if(LONG_ONLY[name] && sv < 0) sv = 0;
        var want = (G.E[j][t] && sv === sv) ? sv*sz : NaN, cur = prev;
        if(want !== want) cur = 0; else if(Math.sign(want) !== Math.sign(prev) || Math.abs(want - prev) > 0.15) cur = want;
        prev = cur; w[t] = G.N[t] > 0 ? cur/G.N[t] : 0; }
      W.push(w);
      for(var t2=1; t2<T; t2++){ var P = w[t2-1]; if(P){ var rr = r[t2]; ret[t2] += P*(rr === rr ? rr : 0) - P*G.ff[j][t2]; } } }
    for(var t3=2; t3<T; t3++){ var tu = 0; for(var q=0; q<n; q++) tu += Math.abs(W[q][t3-1] - W[q][t3-2]); ret[t3] -= tu*PERP; }
    if(T > 1){ var tu1 = 0; for(var q1=0; q1<n; q1++) tu1 += Math.abs(W[q1][0]); ret[1] -= tu1*PERP; }
    return { ret:ret, W:W }; }
  // ── a harvest part (as r12lib.harvest: weekly at Sunday close, spot + short perpetual, P&L = funding − costs) ──
  function harvestPart(G, k, hurdle){ var T = G.T, n = G.syms.length, ret = new Float64Array(T), S30 = [], cov = [], held = {}, baskets = [];
    for(var j=0; j<n; j++){ var s = rollSum(G.ff[j], 30); for(var t=0; t<T; t++) s[t] = s[t]*7/30; S30.push(s); var has = new Float64Array(T); for(var t1=0; t1<T; t1++) has[t1] = G.fc[j][t1] > 0 ? 1 : 0; var cv = rollSum(has, 7); cov.push(cv); }
    var sund = []; for(var t2=0; t2<T; t2++) if(new Date((t2 + G.K0)*DAY).getUTCDay() === 0) sund.push(t2);
    function choose(a){ var el = []; for(var j=0; j<n; j++) if(G.E[j][a] && cov[j][a] >= 6 && isFinite(S30[j][a])) el.push(j);
      if(el.length < 5) return {};
      var ord = el.slice().sort(function(x, y){ return S30[y][a] - S30[x][a]; }), rk = {}, i = 0;
      while(i < ord.length){ var e = i; while(e + 1 < ord.length && S30[ord[e+1]][a] === S30[ord[i]][a]) e++; for(var q=i; q<=e; q++) rk[ord[q]] = (i + e + 2)/2; i = e + 1; }
      var want = {}; el.forEach(function(j){ var v = S30[j][a]; if(rk[j] <= k && v > hurdle) want[j] = 1; if(held[j] && rk[j] <= 2*k && v > 0) want[j] = 1; });
      var ks = Object.keys(want).map(Number); if(ks.length > k){ ks.sort(function(x, y){ return (S30[y][a] - S30[x][a]) || ((held[x] ? 0 : 1) - (held[y] ? 0 : 1)) || (G.syms[x] < G.syms[y] ? -1 : 1); }); ks = ks.slice(0, k); }
      var o = {}; ks.forEach(function(j){ o[j] = 1; }); return o; }
    for(var q=0; q+1<sund.length; q++){ var a = sund[q], b = sund[q+1], want = choose(a), ch = 0;
      Object.keys(want).forEach(function(j){ if(!held[j]) ch++; }); Object.keys(held).forEach(function(j){ if(!want[j]) ch++; });
      ret[a+1] -= ch*(1/k)*(SPOT + PERP); Object.keys(want).forEach(function(j){ for(var t=a+1; t<=b; t++) ret[t] += (1/k)*G.ff[j][t]; });
      baskets.push({ a:a + G.K0, hold:Object.keys(want).map(function(j){ return G.syms[j]; }).sort() }); held = want; }
    var last = sund.length ? sund[sund.length - 1] : null, cur = null;
    if(last != null){ var prevHeld = held, w = choose(last); cur = { a:last + G.K0, hold:Object.keys(w).map(function(j){ return G.syms[j]; }).sort(), prev:Object.keys(prevHeld).map(function(j){ return G.syms[j]; }).sort(), v:{} };
      Object.keys(w).forEach(function(j){ cur.v[G.syms[j]] = S30[j][last]; }); }
    return { ret:ret, baskets:baskets, current:cur }; }
  // ── everything ──
  function parts(G){ var P = {}; Object.keys(PARTS).forEach(function(nm){ var p = PARTS[nm]; P[nm] = p.kind === 'harvest' ? harvestPart(G, p.k, p.hurdle) : tsPart(G, nm); }); return P; }
  function weekEnd(day){ var dow = new Date(day*DAY).getUTCDay(); return dow === 0 ? day : day + (7 - dow); }
  function nwT(x, lag){ lag = lag || 2; x = x.filter(function(v){ return isFinite(v); }); var n = x.length; if(n < 8) return null;
    var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g0 = e.reduce(function(a, v){ return a + v*v; }, 0)/n, lrv = g0;
    for(var k=1; k<=lag; k++){ var s = 0; for(var i=k; i<n; i++) s += e[i]*e[i-k]; lrv += 2*(1 - k/(lag + 1))*s/(n - k); }
    return lrv > 0 ? m/Math.sqrt(lrv/n) : null; }
  function stats(x){ var n = x.length; if(!n) return { n:0 }; var m = x.reduce(function(a, b){ return a + b; }, 0)/n, eq = 1, pk = 1, dd = 0; x.forEach(function(r){ eq *= 1 + r; if(eq > pk) pk = eq; if(eq/pk - 1 < dd) dd = eq/pk - 1; });
    return { n:n, mean:m, ann:m*52, t:nwT(x), cum:eq - 1, worstFall:dd }; }
  function verdict(F, retired){ if(retired) return { code:'RETIRED', text:'Retired on ' + retired.at.slice(0, 10) + ': ' + retired.why + '. A retired rule never returns.' };
    if(!F || !F.n) return { code:'WAIT', text:'No forward week has finished yet. The first runs from the close of Sunday 18 Oct 2026 to the close of Sunday 25 Oct.' };
    if(F.worstFall <= FWD_STOP) return { code:'RETIRE', why:'fell ' + Math.round(-F.worstFall*100) + '% from its forward peak (limit 10%; its worst on untouched coins was under 4%)' };
    if(F.n < FWD_MIN) return { code:'COLLECT', text:F.n + ' of ' + FWD_MIN + ' forward weeks. Too early to judge.' };
    if(F.mean <= 0) return { code:'RETIRE', why:'its ' + F.n + ' forward weeks average zero or less after costs' };
    if(F.t != null && F.t >= FWD_BAR) return { code:'CONFIRMED', text:'Confirmed on ' + F.n + ' forward weeks (z ' + F.t.toFixed(2) + ' ≥ ' + FWD_BAR + '). Still paper only.' };
    if(F.n < FWD_FULL) return { code:'HOLDING', text:'Positive on ' + F.n + ' forward weeks but not yet clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + '). Judged again at ' + FWD_FULL + ' weeks.' };
    return { code:'UNPROVEN', text:'Positive after ' + F.n + ' forward weeks but not clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + '). Stays on paper.' }; }
  function compute(data, opt){ opt = opt || {}; var now = opt.now || Date.now(), today = Math.floor(now/DAY), G = grid(data, opt.endDay != null ? opt.endDay : today);
    if(G.syms.length < 10 || !(G.T > 60)) return { at:now, error:'needs stored daily bars and funding for at least 10 coins (has ' + G.syms.length + ')' };
    var P = parts(G), out = { at:now, coins:G.syms.length, lastDay:G.K0 + G.T - 1, blends:{}, parts:{} };
    Object.keys(BLENDS).forEach(function(id){ var B = BLENDS[id], daily = new Float64Array(G.T);
      B.parts.forEach(function(pw){ var r = P[pw[0]].ret; for(var t=0; t<G.T; t++) daily[t] += pw[1]*r[t]; });
      var wk = {}, lastDay = G.K0 + G.T - 1; for(var t=0; t<G.T; t++){ var d = G.K0 + t; if(d < S0_DAY) continue; var we = weekEnd(d); wk[we] = (wk[we] || 0) + daily[t]; }
      var weeks = Object.keys(wk).map(Number).sort(function(a, b){ return a - b; }).filter(function(we){ return we <= lastDay; }).map(function(we){ return [we, wk[we]]; });
      out.blends[id] = { daily:daily, weeks:weeks }; });
    out.G = G; out.P = P; return out; }
  // ── positions now, as orders (the latest close's targets against the day before's) ──
  function positions(res, id, eq){ var G = res.G, P = res.P, B = BLENDS[id], T = G.T, dir = {}, dirPrev = {}, pairs = null;
    B.parts.forEach(function(pw){ var nm = pw[0], w = pw[1], p = P[nm];
      if(PARTS[nm].kind === 'harvest'){ var c = p.current; if(c) pairs = { a:c.a, hold:c.hold, prev:c.prev, each:eq*w/PARTS[nm].k, k:PARTS[nm].k, v:c.v }; return; }
      G.syms.forEach(function(s, j){ var a = p.W[j][T-1]*w*eq, b = T > 1 ? p.W[j][T-2]*w*eq : 0; if(a) dir[s] = (dir[s] || 0) + a; if(b) dirPrev[s] = (dirPrev[s] || 0) + b; }); });
    return { day:G.K0 + T - 1, dir:dir, dirPrev:dirPrev, pairs:pairs }; }
  function flags(res, hold){ var G = res.G, newest = -Infinity, out = { stale:[], negative:[] }; G.f1.forEach(function(f){ if(f != null && f > newest) newest = f; });
    (hold || []).forEach(function(s){ var j = G.syms.indexOf(s); if(j < 0) return; var f1 = G.f1[j]; if(isFinite(newest) && (f1 == null || f1 < newest - 16*3600e3)) out.stale.push(s);
      var sum = 0; G.fund[j].forEach(function(q){ if(+q[0] > newest - 24*3600e3) sum += +q[1]; }); if(sum < -0.003) out.negative.push([s, sum]); });
    return out; }
  // ── forward record: a finished forward week is stored once and never recomputed ──
  function record(res){ var changed = false; Object.keys(BLENDS).forEach(function(id){ var R = st.rec[id] = st.rec[id] || {};
      res.blends[id].weeks.forEach(function(w){ if(w[0] > FREEZE_DAY && R[w[0]] == null){ R[w[0]] = +w[1].toFixed(8); changed = true; } }); });
    return changed; }
  function forward(id){ var R = st.rec[id] || {}; return stats(Object.keys(R).map(Number).sort(function(a, b){ return a - b; }).map(function(k){ return R[k]; })); }
  function compact(res){ if(!res || res.error) return res; var o = { at:res.at, coins:res.coins, lastDay:res.lastDay, blends:{} }, eq = safe(function(){ return window.OMEGA_AUTOPILOT.cfg().startEquity; }) || 100;
    Object.keys(BLENDS).forEach(function(id){ var b = res.blends[id], pre = b.weeks.filter(function(w){ return w[0] <= FREEZE_DAY; }).map(function(w){ return w[1]; }), yrs = {};
      b.weeks.forEach(function(w){ if(w[0] > FREEZE_DAY) return; var y = new Date(w[0]*DAY).getUTCFullYear(); yrs[y] = (yrs[y] || 0) + w[1]; });
      var pos = positions(res, id, eq); o.blends[id] = { before:stats(pre), beforeYears:yrs, pos:pos, flags:flags(res, pos.pairs ? pos.pairs.hold : []) }; });
    return o; }
  async function runNow(){ if(run.busy) return { skip:true, text:'already running' }; run.busy = true; run.msg = 'Reading stored daily bars and funding'; render();
    try{ var X = window.OMEGA_CARRYXS; if(!X || !X.getData) throw new Error('data loader not ready');
      var data = await X.getData(30*60e3), res = compute(data, { now:Date.now() });
      if(res.error){ st.res = { at:res.at, error:res.error }; lsSet(KEY, st); return { skip:true, text:res.error, retryIn:6*3600e3 }; }
      record(res); st.res = compact(res); st.verdict = {};
      Object.keys(BLENDS).forEach(function(id){ var V = verdict(forward(id), st.retired[id]); if(V.code === 'RETIRE' && !st.retired[id]){ st.retired[id] = { at:new Date().toISOString(), why:V.why }; V = verdict(forward(id), st.retired[id]); } st.verdict[id] = V; });
      lsSet(KEY, st); note();
      return { text:'Round 12 winners: ' + Object.keys(BLENDS).map(function(id){ var F = forward(id); return BLENDS[id].title + ' ' + (F.n ? F.n + ' forward weeks, ' + pct(F.cum) : 'no forward week yet'); }).join('; ') + '.' }; }
    catch(e){ return { error:(e && e.message) || String(e) }; }
    finally{ run.busy = false; run.msg = ''; render(); } }
  function note(){ var code = Object.keys(BLENDS).map(function(id){ return (st.verdict && st.verdict[id] || {}).code; }).join(','); if(st.noted === code) return;
    safe(function(){ var B = window.OMEGA_BRAIN; if(!B || !B.feedObservation) return; if(B.retract) B.retract(['Round 12 winners']);
      B.feedObservation({ pinned:true, strat:'omega', tf:'1w', symbol:'*', text:'Round 12 winners (harvest + dip-buying): of 600 known strategies, 100 combinations and 5 own ideas, only two passed on 125 untouched coins (bar z 3.29), both the funding harvest plus RSI(5) dip-buying: harvest + dip-buying half each (+4.0% a year over the market, z 3.31, worst −3.6%) and a five-part blend (+4.1%, z 3.90, worst −2.6%). Modest and steady. Carry on 1-day funding, trend and every other directional rule failed there. Frozen 18 Oct 2026; paper only.' }); });
    st.noted = code; lsSet(KEY, st); }
  // ── the card (OMEGA Strategy, under the harvest card) ──
  function ordersHtml(p, eq){ if(!p) return ''; var h = '', nm = function(s){ return '<b>' + esc(s.replace(/USDT$/, '')) + '</b>'; };
    if(p.pairs){ var Q = p.pairs, open = Q.hold.filter(function(s){ return Q.prev.indexOf(s) < 0; }), shut = Q.prev.filter(function(s){ return Q.hold.indexOf(s) < 0; }), keep = Q.hold.filter(function(s){ return Q.prev.indexOf(s) > -1; });
      h += '<div class="hint" style="margin:4px 0;border-left:3px solid var(--gold);padding-left:8px;"><b>Harvest pairs</b> (decided at the close of ' + dayStr(Q.a) + '; each pair ' + Q.each.toFixed(2) + ' USDT of the coin and the same short in its perpetual): ' + (Q.hold.length ? Q.hold.map(nm).join(', ') : 'none (no coin pays enough)') +
        (open.length ? '<br>Open ' + open.map(nm).join(', ') : '') + (shut.length ? '<br>Close ' + shut.map(nm).join(', ') + ' (both legs)' : '') + (keep.length && (open.length || shut.length) ? '<br>Keep ' + keep.map(nm).join(', ') : '') + '</div>'; }
    var ks = Object.keys(p.dir).concat(Object.keys(p.dirPrev)).filter(function(s, i, a){ return a.indexOf(s) === i; }).sort(), rows = [];
    ks.forEach(function(s){ var a = p.dir[s] || 0, b = p.dirPrev[s] || 0; if(Math.abs(a) < 0.005 && Math.abs(b) < 0.005) return;
      var act = Math.abs(a - b) < 0.005 ? 'hold' : (b === 0 || Math.abs(b) < 0.005 ? 'open' : (Math.abs(a) < 0.005 ? 'close' : 'resize'));
      rows.push('<tr><td>' + nm(s) + '</td><td class="mono">' + (Math.abs(a) < 0.005 ? '—' : (a > 0 ? 'long ' : 'short ') + Math.abs(a).toFixed(2)) + '</td><td>' + act + (act === 'resize' ? ' (from ' + (b > 0 ? 'long ' : 'short ') + Math.abs(b).toFixed(2) + ')' : '') + '</td></tr>'); });
    h += '<div class="hint" style="margin:4px 0;"><b>Perpetual positions after the close of ' + dayStr(p.day) + '</b> (USDT, for ' + eq + ' USDT; you place them, OMEGA places none): ' + (rows.length ? '</div><div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Coin</th><th>Position</th><th>Today</th></tr></thead><tbody>' + rows.join('') + '</tbody></table></div>' : 'none.</div>');
    var small = Object.keys(p.dir).some(function(s){ return Math.abs(p.dir[s]) >= 0.005 && Math.abs(p.dir[s]) < 5; }) || (p.pairs && p.pairs.hold.length && p.pairs.each < 5);
    if(small) h += '<p class="hint" style="color:var(--amber);">Some amounts are below an exchange’s minimum order size (often 5 USDT or more). Each position is a small slice of the account by design (1/N per coin, sized to its volatility), so following this for real needs a larger account; the amounts scale with the account size set in the Autopilot.</p>';
    return h; }
  function flagHtml(f){ if(!f) return ''; var h = '';
    if(f.stale.length) h += '<p class="hint" style="color:var(--bear);border:1px solid var(--bear);border-radius:6px;padding:6px 8px;"><b>Funding has stopped for ' + f.stale.map(function(s){ return esc(s.replace(/USDT$/, '')); }).join(', ') + '</b> while the rule holds the pair. A perpetual stops paying funding when it is delisted: check Binance’s announcements and, if so, close that pair now, both legs.</p>';
    if(f.negative.length) h += '<p class="hint" style="color:var(--bear);border:1px solid var(--bear);border-radius:6px;padding:6px 8px;"><b>Funding has turned sharply negative on ' + f.negative.map(function(x){ return esc(x[0].replace(/USDT$/, '')) + ' (' + pct(x[1], 2) + ' in 24 hours)'; }).join(', ') + '</b>: the short side is now paying, as in the squeeze that cost the harvest 7.7% in one week on the untouched coins. The frozen rule keeps the pair until Sunday; you may close it early (the paper record follows the rule).</p>';
    return h; }
  function render(){ var host = el('r12Card'); if(!host){ var pg = el('page-ostrat'); if(!pg) return; host = document.createElement('div'); host.id = 'r12Card'; var hv = el('harvestCard'); if(hv && hv.parentNode === pg) pg.insertBefore(host, hv.nextSibling); else pg.insertBefore(host, pg.firstChild); }
    var r = st.res, eq = safe(function(){ return window.OMEGA_AUTOPILOT.cfg().startEquity; }) || 100, Z = RESEARCH;
    var h = '<div class="card" style="margin-bottom:14px;border-color:var(--bull);"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;"><div><h2 style="color:var(--gold);margin-bottom:4px;">Round 12 winners — harvest + dip-buying</h2><span class="bt-lab bull">Paper · passed on 125 untouched coins · forward record starts at Sunday 18 Oct’s close</span></div>' +
      '<button class="btn-outline" type="button" id="r12Run"' + (run.busy ? ' disabled' : '') + '>' + (run.busy ? esc(run.msg || 'Working') : 'Update now') + '</button></div>' +
      '<p class="hint" style="margin-top:8px;">' + esc(Z.plan) + '. ' + Z.stages.map(function(s, i){ return '<b>' + (i + 1) + '.</b> ' + esc(s[0]) + ': ' + esc(s[1]); }).join(' ') + '</p>' +
      '<p class="hint">' + esc(Z.failedFinal) + '</p><p class="hint" style="color:var(--amber);"><b>Read it the right way:</b> ' + esc(Z.caution) + '</p>';
    Object.keys(BLENDS).forEach(function(id){ var B = BLENDS[id], R = r && !r.error ? r.blends[id] : null, V = (st.verdict && st.verdict[id]) || verdict(forward(id), st.retired[id]), F = forward(id);
      h += '<h3 style="font-size:14px;margin:14px 0 4px;border-top:1px solid var(--border);padding-top:10px;">' + esc(B.title) + ' <span class="dim">(' + id + ')</span></h3>' +
        '<p class="hint" style="margin-top:0;">' + B.parts.map(function(pw){ return Math.round(pw[1]*1000)/10 + '% ' + esc(PARTS[pw[0]].name); }).join(' · ') + '.</p>' +
        '<p class="hint" style="color:var(--bull);"><b>Untouched coins (Mar 2022 – Oct 2026):</b> ' + pct(B.final.alpha/100) + ' a year over the market, z ' + B.final.z.toFixed(2) + ' against 3.29, ' + pct(B.final.costs2x/100) + ' with costs doubled, worst fall ' + pct(B.final.worst/100) + '; by year ' + B.final.years.map(function(y){ return esc(y[0]) + ' ' + pct(y[1]/100); }).join(', ') + ' (*to Oct). Where it was built: 25 coins ' + pct(B.design.alpha/100) + ' (z ' + B.design.z.toFixed(2) + '), 140 coins ' + pct(B.valid.alpha/100) + ' (z ' + B.valid.z.toFixed(2) + ').</p>';
      if(R){ h += flagHtml(R.flags) + ordersHtml(R.pos, eq);
        h += '<p class="hint"><b>Forward:</b> ' + esc(V.text || V.why || '') + (F.n ? ' ' + F.n + ' week' + (F.n === 1 ? '' : 's') + ': ' + pct(F.cum, 2) + ' (' + (F.cum >= 0 ? '+' : '−') + Math.abs(F.cum*eq).toFixed(2) + ' USDT on ' + eq + '), worst fall ' + pct(F.worstFall, 2) + '.' : '') + ' On your stored history before the freeze (2020 on, worked out by this app): ' + pct(R.before.cum, 1) + ' over ' + R.before.n + ' weeks, worst fall ' + pct(R.before.worstFall, 2) + '; by year ' + Object.keys(R.beforeYears).map(function(y){ return y + ' ' + pct(R.beforeYears[y], 1); }).join(', ') + '.</p>'; }
    });
    if(!r) h += '<p class="hint">' + (run.busy ? esc(run.msg) : 'Not worked out yet. It reads the stored daily bars and funding of the 25 coins; the Autopilot runs it twice a day.') + '</p>';
    else if(r.error) h += '<p class="hint">' + esc(r.error) + '.</p>';
    h += '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;"><b>How it is judged, and what could still be wrong</b></summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;">' +
      '<li>Fixed 18 Oct 2026 before any forward week: nothing is judged before ' + FWD_MIN + ' weeks; then retired if they average zero or less, confirmed at z ≥ ' + FWD_BAR + '; retired at any time on a ' + Math.round(-FWD_STOP*100) + '% fall from its forward peak. A retired rule never returns.</li>' +
      '<li>The untouched test covers Mar 2022 – Oct 2026 only; 2022 and 2026 were flat to slightly negative for both.</li>' +
      '<li>The dip-buying part trades daily: a long perpetual after a sharp 5-day fall, closed when the 5-day RSI is back over 50. It pays funding while long.</li>' +
      '<li>Doing the harvest for real needs the coin and its perpetual on the same exchange, margin for the short, and trust in the exchange. This app places no orders.</li></ul></details></div>';
    host.innerHTML = h; var bt = el('r12Run'); if(bt) bt.onclick = function(){ var O = window.OMEGA_OPERATOR; if(O && O.runNow) safe(function(){ O.runNow('r12'); }); else runNow(); }; }
  function report(){ return { rules:BLENDS, parts:PARTS, research:RESEARCH, judgement:{ minWeeks:FWD_MIN, fullWeeks:FWD_FULL, bar:FWD_BAR, stopFall:FWD_STOP, frozen:'2026-10-18' }, verdicts:st.verdict || null, retired:st.retired, forwardWeeks:st.rec, result:st.res || null }; }
  function every(){ return 12*3600e3; }
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'r12'; })) return true;
    J.push({ id:'r12', lane:'heavy', prio:2, label:'Round 12 winners (harvest + dip-buying)', what:'Twice a day: the positions of the two frozen round-12 winners and their forward records, from the stored daily bars and funding. Paper only.', every:every, run:runNow }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var nav0 = window.navigate; if(typeof nav0 === 'function') window.navigate = function(p){ var rr = nav0.apply(this, arguments); if(p === 'ostrat') setTimeout(render, 80); return rr; };
  setTimeout(function(){ try{ render(); }catch(e){} }, 1800);
  window.OMEGA_R12 = { compute:compute, grid:grid, parts:parts, positions:positions, flags:flags, verdict:verdict, runNow:runNow, render:render, report:report, state:function(){ return st; }, BLENDS:BLENDS, PARTS:PARTS, RESEARCH:RESEARCH, FREEZE_DAY:FREEZE_DAY, _:{ ewmA:ewmA, rsi:rsi, atr:atr, tsPart:tsPart, harvestPart:harvestPart } };
})();
</script>
