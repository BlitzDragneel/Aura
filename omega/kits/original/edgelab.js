<script>/* ═══ EDGE LAB (v6.5.70) — OMEGA looks for the edges research has not tested, with research's discipline ═══
   PLAN13. Built-in knowledge: every rule research tested (rounds 1–12, the outside study, the other assistants' tests),
   with its results, verdict and the lessons; nothing in it is ever tested again, and the winners run from day one.
   The explorer works only on untested ground: about 40 representative rules × market and coin conditions × exits
   (tier 1: one condition; tier 2: two), plus new families drawn from the lessons (harvest guards, coin age, funding
   against price). Discipline: screened on half the coins (A: alpha z ≥ 1.65, costs doubled positive, up in 60% of
   years), then checked once on the other half (B: z ≥ the one-sided 5% Bonferroni bar over every screen survivor so far),
   then frozen into the shadow book and tracked forward week by week on all coins. A rule becomes an EDGE only when its
   forward weeks clear the Bonferroni bar over the whole book (8 weeks at least). Retired after 26 flat weeks or a 15%
   fall. Paper only: OMEGA never places an order. */
(function(){
  'use strict';
  var KN = __KNOWLEDGE__;
  var DAY = 86400e3, FREEZE = Date.UTC(2026, 9, 18)/DAY, S0 = Date.UTC(2020, 0, 1)/DAY, MIN_FWD = 8, RETIRE_WEEKS = 26, RETIRE_FALL = -0.15, MIN_COINS = 150, META = 'edgelab';
  var RESEARCH_BOOK = {
    'research: harvest + dip-buying (C028)':{ cand:{ kind:'blend', parts:[[{ kind:'harvest', h:{ k:10, hurdle:0.001 } }, 0.5], [{ base:'RSI(5) 10/90 revert LF' }, 0.5]] }, origin:'round 12 final test (z 3.31 on 125 untouched coins)' },
    'research: five-part blend (C016)':{ cand:{ kind:'blend', parts:[[{ kind:'harvest', h:{ k:15, hurdle:0.002 } }, 0.5356612887226874], [{ base:'RSI(5) 10/90 revert LF' }, 0.234405227849473], [{ base:'long when 3d funding is negative' }, 0.12729183230240926], [{ base:'Supertrend 7/2 LS' }, 0.05171081473777347], [{ base:'SMA 10/50 LS' }, 0.050930836387656796]] }, origin:'round 12 final test (z 3.90 on 125 untouched coins)' },
    'research: funding harvest, 10 pairs':{ cand:{ kind:'harvest', h:{ k:10, hurdle:0.001 } }, origin:'rounds 7, 8 and 10 (three untouched tests)' },
    'research: model across coins (round 14)':{ cand:{ kind:'model', from:Date.UTC(2026, 9, 11)/DAY, key:'model across coins (round 14)' }, origin:'round 14: +37.8% a year over the market on 125 untouched coins (z 2.89), below the strict bar of 3.29; judged only on new weeks' } };
  function el(id){ return document.getElementById(id); }
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function f1(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(d == null ? 1 : d); }
  function dayStr(d){ return new Date(d*DAY).toISOString().slice(0, 10); }
  function sleep0(){ return new Promise(function(r){ setTimeout(r, 0); }); }
  // one-sided normal quantile (Acklam)
  function invNorm(p){ var a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239], b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572], c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783], d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416], q, r;
    if(p < 0.02425){ q = Math.sqrt(-2*Math.log(p)); return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5])/((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1); }
    if(p > 1 - 0.02425){ q = Math.sqrt(-2*Math.log(1 - p)); return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5])/((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1); }
    q = p - 0.5; r = q*q; return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q/(((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1); }
  function bar(n){ return invNorm(1 - 0.05/Math.max(1, n)); }
  function fnv(s){ var h = 2166136261; for(var i=0; i<s.length; i++){ h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return h; }
  function half(sym){ return (fnv(sym) & 1) ? 'B' : 'A'; }
  var st = null, run = { busy:false, stop:false, msg:'' }, gridCache = null, candCache = null;
  function blank(){ return { v:1, tier:1, s1:{}, surv:[], s2:{}, book:{}, fwd:{}, stat:{}, fwdWeek:0, coins:null, log:[], phase:'screen', started:new Date().toISOString() }; }
  async function load(){ if(st) return st; var W = window.OMEGA_WIDE; var v = W ? await W.getMeta(META).catch(function(){ return null; }) : null; st = v && v.v === 1 ? v : blank();
    Object.keys(RESEARCH_BOOK).forEach(function(k){ if(!st.book[k]) st.book[k] = { start:FREEZE, cand:RESEARCH_BOOK[k].cand, origin:RESEARCH_BOOK[k].origin, entered:'2026-10-18', research:true }; });
    return st; }
  function save(){ var W = window.OMEGA_WIDE; if(W && st) return W.putMeta(META, st).catch(function(){}); }
  function logLine(t){ st.log.unshift(new Date().toISOString().slice(0, 16).replace('T', ' ') + ' ' + t); st.log = st.log.slice(0, 40); }
  // ── knowledge ──
  function priority(){ var p = {}; Object.keys(KN.tested).forEach(function(k){ var r = KN.tested[k], nm = k.split('|')[0]; if(!/\|none\|own$/.test(k)) return; var z = r.s2 ? r.s2[1] : (r.s1 ? r.s1[1] : 0); p[nm] = z || 0; }); return p; }
  function cands(){ var t = st.tier; if(candCache && candCache.t === t) return candCache.list; var L = window.OMEGA_EDGELIB; candCache = { t:t, list:L.candidates(KN.tested, priority(), t) }; return candCache.list; }
  // ── grids: all coins with a perpetual; halves A and B by a fixed hash of the name ──
  async function grids(){ var W = window.OMEGA_WIDE, L = window.OMEGA_EDGELIB, ver = W.version(), today = Math.floor(Date.now()/DAY);
    if(gridCache && gridCache.ver === ver && gridCache.today === today) return gridCache;
    var recs = (await W.all()).filter(function(r){ return r && r.f1 && r.c && r.c.length; }); if(recs.length < MIN_COINS) return { short:recs.length };
    var G = L.grid(recs, today), A = [], B = []; G.syms.forEach(function(s, j){ (half(s) === 'A' ? A : B).push(j); });
    gridCache = { ver:ver, today:today, G:G, GA:L.subgrid(G, A), GB:L.subgrid(G, B), lastDay:G.K0 + G.T - 1 }; recs = null; if(W.release) W.release(); return gridCache; }
  function r2(v){ return Math.round(v*100)/100; }
  function pack(S){ return [r2(S.alpha), r2(S.z), S.ypos, S.ny, r2(S.costs2x), S.weeks]; }
  function pass1(S){ return S.alpha > 0 && S.costs2x > 0 && S.z >= 1.65 && S.ny > 0 && S.ypos >= Math.ceil(0.6*S.ny); }
  function pass2(S, b){ return S.alpha > 0 && S.costs2x > 0 && S.z >= b && S.ypos >= Math.ceil(S.ny/2); }
  // ── the explorer: screen on A, then validate on B, then the coin-by-coin view ──
  async function explore(gc, budget, t0){ var L = window.OMEGA_EDGELIB, list = cands(), endDay = gc.lastDay + 1, sig = { base:null, cache:{} }, n = 0;
    if(st.phase === 'screen'){ var todo = list.filter(function(c){ return !st.s1[c.key]; });
      for(var i=0; i<todo.length && !run.stop; i++){ if(Date.now() - t0 > budget) return n; var c = todo[i];
        if(c.base !== sig.base){ sig = { base:c.base, cache:{} }; }
        run.msg = 'Screening ' + (Object.keys(st.s1).length + 1) + ' of ' + list.length + ' (tier ' + st.tier + ')'; renderSoon();
        try{ var S = L.judge(gc.GA, L.run(gc.GA, c, { sigCache:c.base ? sig.cache : null }), S0, endDay); st.s1[c.key] = pack(S); if(pass1(S)){ st.surv.push(c.key); logLine('screen survivor: ' + L.label(c) + ' (A: ' + f1(S.alpha) + '% a year, z ' + S.z.toFixed(2) + ')'); } }
        catch(e){ st.s1[c.key] = [0, 0, 0, 0, 0, 0, 'error']; }
        n++; if(n % 3 === 0) await sleep0(); }
      if(list.every(function(c){ return st.s1[c.key]; })){ st.phase = 'validate'; logLine('tier ' + st.tier + ' screened: ' + list.length + ' candidates, ' + st.surv.length + ' survivors so far'); } }
    if(st.phase === 'validate'){ var b = bar(st.surv.length), byKey = {}; list.forEach(function(c){ byKey[c.key] = c; });
      var todo2 = st.surv.filter(function(k){ return !st.s2[k] && byKey[k]; });
      for(var q=0; q<todo2.length && !run.stop; q++){ if(Date.now() - t0 > budget) return n; var k = todo2[q], cc = byKey[k]; run.msg = 'Checking survivor ' + (q + 1) + ' of ' + todo2.length + ' on the other half (bar z ' + b.toFixed(2) + ')'; renderSoon();
        try{ var S2 = L.judge(gc.GB, L.run(gc.GB, cc), S0, endDay); st.s2[k] = pack(S2).concat([r2(b)]);
          if(pass2(S2, b)){ st.book[k] = { start:gc.lastDay + 1, cand:cc, origin:'explorer, tier ' + st.tier + ' (A: z ' + st.s1[k][1] + '; B: z ' + st.s2[k][1] + ' against ' + b.toFixed(2) + ')', entered:new Date().toISOString().slice(0, 10) }; logLine('NEW in the shadow book: ' + L.label(cc)); note('new', cc); } }
        catch(e){ st.s2[k] = [0, 0, 0, 0, 0, 0, r2(b), 'error']; }
        n++; await sleep0(); }
      if(st.surv.every(function(k){ return st.s2[k] || !byKey[k]; })){ st.phase = 'coins'; } }
    if(st.phase === 'coins'){ if(Date.now() - t0 > budget) return n; run.msg = 'Coin-by-coin view'; renderSoon(); st.coins = await coinView(gc.G); st.phase = 'done'; logLine('coin-by-coin view refreshed'); }
    if(st.phase === 'done' && st.tier < 2){ st.tier = 2; candCache = null; st.phase = 'screen'; logLine('tier 2 opened: two conditions at once'); }
    return n; }
  // ── coin by coin: the best time-series rule on each coin over the last 365 days, and whether such picks persisted ──
  async function coinView(G){ var L = window.OMEGA_EDGELIB, bases = L.BASES.filter(function(b){ return b.kind === 'ts'; }), T = G.T, yrs = {}, last = {}, ycount = {};
    for(var j=0; j<G.syms.length; j++){ var sg = L.subgrid(G, [j]); sg.ctx = G.ctx;
      for(var q=0; q<bases.length; q++){ var R = L.run(sg, { base:bases[q].name }), y = {}, l365 = 0;
        for(var t=1; t<T; t++){ if(!sg.E[0][t-1]) continue; var x = R.gross[t] - R.cost[t], d = t + G.K0, yr = new Date(d*DAY).getUTCFullYear(); y[yr] = (y[yr] || 0) + x; if(d > G.K0 + T - 1 - 365) l365 += x; if(q === 0) ycount[G.syms[j] + yr] = (ycount[G.syms[j] + yr] || 0) + 1; }
        (yrs[G.syms[j]] = yrs[G.syms[j]] || []).push(y); (last[G.syms[j]] = last[G.syms[j]] || []).push(l365); }
      if(j % 5 === 4) await sleep0(); }
    var hits = 0, n = 0, pctSum = 0, rows = [];
    G.syms.forEach(function(s){ var Y = yrs[s]; if(!Y) return; var years = Object.keys(Y[0]).map(Number).filter(function(y){ return (ycount[s + y] || 0) >= 300; }).sort();
      for(var i=0; i+1<years.length; i++){ var y0 = years[i], y1 = years[i+1]; var best = 0; for(var q=1; q<Y.length; q++) if((Y[q][y0] || 0) > (Y[best][y0] || 0)) best = q;
        var v = Y[best][y1] || 0, below = Y.filter(function(o){ return (o[y1] || 0) < v; }).length, pct = below/(Y.length - 1); pctSum += pct; n++; if(pct > 0.5) hits++; }
      var Ls = last[s], bi = 0; for(var k=1; k<Ls.length; k++) if(Ls[k] > Ls[bi]) bi = k; rows.push([s, bases[bi].name, r2(100*Ls[bi])]); });
    rows.sort(function(a, b){ return b[2] - a[2]; });
    return { asOf:dayStr(G.K0 + G.T - 1), rows:rows.slice(0, 40), persistence:{ n:n, hits:hits, avgPct:n ? r2(100*pctSum/n) : null } }; }
  // ── the shadow book, forward week by week on all coins ──
  async function forward(gc, budget, t0){ var L = window.OMEGA_EDGELIB, G = gc.G, lastSun = gc.lastDay; while(new Date(lastSun*DAY).getUTCDay() !== 0) lastSun--;
    var keys = Object.keys(st.book).filter(function(k){ return !(st.stat[k] && st.stat[k].code === 'RETIRED'); }), todo = keys.filter(function(k){ return !(st.fwd[k] && st.fwd[k]._to >= lastSun); });
    for(var i=0; i<todo.length; i++){ if(Date.now() - t0 > budget) break; var k = todo[i], E = st.book[k], F = st.fwd[k] = st.fwd[k] || {}; run.msg = 'Forward record: ' + (i + 1) + ' of ' + todo.length; renderSoon();
      try{ var R = L.run(G, E.cand), wk = {};
        for(var t=0; t<G.T; t++){ var d = t + G.K0; if(d <= E.start || d > lastSun) continue; var we = L.weekEnd(d); var w = wk[we] = wk[we] || [0, 0]; w[0] += R.gross[t] - R.cost[t]; w[1] += G.m[t]; }
        Object.keys(wk).forEach(function(we){ if(F[we] == null) F[we] = [+wk[we][0].toFixed(8), +wk[we][1].toFixed(8)]; }); F._to = lastSun; }
      catch(e){ F._err = String(e && e.message || e); F._to = lastSun; }
      await sleep0(); }
    Object.keys(st.book).forEach(function(k){ st.stat[k] = judgeFwd(k); }); }
  function fwdStats(k){ var F = st.fwd[k] || {}, ws = Object.keys(F).filter(function(x){ return x[0] !== '_'; }).map(Number).sort(function(a, b){ return a - b; }), x = ws.map(function(w){ return F[w][0]; }), m = ws.map(function(w){ return F[w][1]; }), n = x.length;
    if(!n) return { n:0 }; var mx = x.reduce(function(a, b){ return a + b; }, 0)/n, mm = m.reduce(function(a, b){ return a + b; }, 0)/n, c = 0, v = 0; for(var i=0; i<n; i++){ c += (x[i] - mx)*(m[i] - mm); v += (m[i] - mm)*(m[i] - mm); }
    var b = n >= MIN_FWD && v > 0 ? c/v : 0, a = x.map(function(xi, i){ return xi - b*m[i]; }), ma = a.reduce(function(p, q){ return p + q; }, 0)/n, eq = 1, pk = 1, dd = 0; x.forEach(function(r){ eq *= 1 + r; if(eq > pk) pk = eq; if(eq/pk - 1 < dd) dd = eq/pk - 1; });
    return { n:n, alpha:100*ma*52, z:window.OMEGA_EDGELIB.nwT(a) || 0, cum:eq - 1, worst:dd, from:ws[0], to:ws[n-1] }; }
  function judgeFwd(k){ var prev = st.stat[k] || {}; if(prev.code === 'RETIRED') return prev; var S = fwdStats(k), nb = Object.keys(st.book).length, b = bar(nb);
    if(S.n && (S.worst <= RETIRE_FALL || (S.n >= RETIRE_WEEKS && S.alpha <= 0))){ var r = { code:'RETIRED', at:new Date().toISOString().slice(0, 10), why:S.worst <= RETIRE_FALL ? 'fell ' + Math.round(-100*S.worst) + '% from its forward peak' : S.n + ' forward weeks averaging zero or less', S:S, bar:b }; logLine('retired: ' + label(k) + ' (' + r.why + ')'); return r; }
    if(S.n >= MIN_FWD && S.alpha > 0 && S.z >= b){ if(prev.code !== 'EDGE'){ logLine('EDGE: ' + label(k) + ' (forward z ' + S.z.toFixed(2) + ' ≥ ' + b.toFixed(2) + ')'); note('edge', st.book[k].cand, k); } return { code:'EDGE', S:S, bar:b }; }
    return { code:'SHADOW', S:S, bar:b }; }
  function label(k){ var E = st.book[k]; if(!E) return k; return /^research: /.test(k) ? k.replace(/^research: /, '') : window.OMEGA_EDGELIB.label(E.cand); }
  // ── positions now, for an edge (paper; you place the orders) ──
  function positions(G, cand, eq){ var L = window.OMEGA_EDGELIB, out = { pairs:[], dir:{} };
    (function walk(c, w){ if(c.kind === 'blend'){ c.parts.forEach(function(p){ walk(p[0], w*p[1]); }); return; }
      if(c.kind === 'harvest'){ var H = L.harvest(G, c.h); if(H.current) out.pairs.push({ hold:H.current.hold, prev:H.current.prev, each:eq*w/c.h.k, a:H.current.a }); return; }
      var R = L.run(G, c, { wantW:true }); if(!R.W) return; var T = G.T; G.syms.forEach(function(s, j){ var v = R.W[j][T-1]*w*eq; if(Math.abs(v) >= 0.005) out.dir[s] = (out.dir[s] || 0) + v; }); })(cand, 1);
    return out; }
  function note(kind, cand, k){ safe(function(){ var B = window.OMEGA_BRAIN; if(!B || !B.feedObservation) return; var t = window.OMEGA_EDGELIB.label(cand);
    B.feedObservation({ pinned:kind === 'edge', strat:'omega', tf:'1d', symbol:'*', text:kind === 'edge' ? 'Edge Lab: forward-confirmed EDGE — ' + t + '. It passed the screen, the other-half check and its forward weeks cleared the bar over the whole shadow book. Paper only.' : 'Edge Lab: new shadow-book entry — ' + t + ' (passed the screen on half the coins and the check on the other half; now tracked forward, not yet an edge).' }); }); }
  // ── run ──
  async function runNow(budgetMs){ if(run.busy) return { skip:true, text:'already running' }; run.busy = true; run.stop = false; var t0 = Date.now(), budget = budgetMs || 40e3;
    try{ await load(); if(!window.OMEGA_WIDE || !window.OMEGA_EDGELIB) throw new Error('modules not ready');
      run.msg = 'Reading coin data'; renderSoon(); var gc = await grids();
      if(gc.short != null){ return { skip:true, text:'Edge Lab waiting for coin data (' + gc.short + ' coins with a perpetual stored; needs ' + MIN_COINS + ')', retryIn:10*60e3 }; }
      await forward(gc, budget, t0); var n = await explore(gc, budget, t0); st.at = new Date().toISOString(); await save();
      var edges = Object.keys(st.stat).filter(function(k){ return st.stat[k].code === 'EDGE'; }).length;
      return { text:'Edge Lab: ' + Object.keys(st.s1).length + ' of ' + cands().length + ' candidates screened (tier ' + st.tier + '), ' + st.surv.length + ' survivors, ' + Object.keys(st.book).length + ' in the shadow book, ' + edges + ' forward-confirmed edges; this run ' + n + '.' }; }
    catch(e){ return { error:(e && e.message) || String(e) }; }
    finally{ run.busy = false; run.msg = ''; render(); } }
  async function exploreAll(){ if(run.busy){ run.stop = true; return; } var r; do { r = await runNow(25e3); await new Promise(function(res){ setTimeout(res, 300); }); } while(!run.stop && r && !r.skip && !r.error && st && st.phase !== 'done' && el('page-edgelab') && el('page-edgelab').classList.contains('active')); render(); }
  // ── the page ──
  var rq = null; function renderSoon(){ if(rq) return; rq = setTimeout(function(){ rq = null; render(); }, 400); }
  function card(t, b, id){ return '<div class="card" style="margin-bottom:14px;"' + (id ? ' id="' + id + '"' : '') + '><h2 style="color:var(--gold);">' + t + '</h2>' + b + '</div>'; }
  var ui = { q:'' };
  async function render(){ var host = el('edgelabBody'); if(!host) return; var pg = el('page-edgelab'); if(pg && !pg.classList.contains('active') && host.innerHTML.length > 100) return;
    await load().catch(function(){}); var L = window.OMEGA_EDGELIB, W = window.OMEGA_WIDE, ws = W ? await W.status().catch(function(){ return null; }) : null, eq = safe(function(){ return window.OMEGA_AUTOPILOT.cfg().startEquity; }) || 100, h = '';
    // 1. what OMEGA knows
    var fam = {}; Object.keys(KN.tested).forEach(function(k){ var r = KN.tested[k], f = r.f || 'other', o = fam[f] = fam[f] || [0, 0, 0, 0]; o[0]++; if(r.v !== 'screen' && r.v !== 'design') o[1]++; if(/final|PASS/.test(r.v)) o[2]++; if(/PASS|part/.test(r.v) && /final\+part|PASS/.test(r.v)) o[3]++; });
    var q = ui.q.trim().toLowerCase(), hits = q ? Object.keys(KN.tested).filter(function(k){ return k.toLowerCase().indexOf(q) > -1; }).slice(0, 40) : [];
    h += card('What OMEGA already knows (built in, never re-tested)', '<p class="hint" style="margin-top:0;">' + Object.keys(KN.tested).length + ' rules and regime variants from round 12 with their results at every stage, ' + Object.keys(KN.combos).length + ' combinations, and ' + KN.earlier.length + ' earlier studies (rounds 1–11, the outside study and the other assistants’ tests: about 1,300 more configurations). The winners run from day one (the harvest and the two round-12 blends, in the shadow book below).</p>' +
      '<details><summary class="hint" style="cursor:pointer;"><b>The lessons</b></summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;">' + KN.lessons.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></details>' +
      '<details><summary class="hint" style="cursor:pointer;"><b>Round 12 by family</b> (tried · past the screen · reached the final · part of a winner)</summary><div class="hint" style="margin-top:6px;">' + Object.keys(fam).sort().map(function(f){ var o = fam[f]; return esc(f) + ': ' + o[0] + ' · ' + o[1] + ' · ' + o[2] + ' · ' + o[3]; }).join('<br>') + '</div></details>' +
      '<details><summary class="hint" style="cursor:pointer;"><b>Earlier studies</b></summary><div class="hint" style="margin-top:6px;">' + KN.earlier.map(function(e){ return '<b>Round ' + esc(e.r) + ':</b> ' + esc(e.name) + ' — ' + esc(e.v); }).join('<br>') + '</div></details>' +
      '<div style="margin-top:8px;"><input id="elabSearch" type="text" placeholder="Search what was tested (e.g. RSI, carry, Donchian)" value="' + esc(ui.q) + '" style="width:100%;max-width:420px;" aria-label="Search tested rules"></div>' +
      (q ? '<div class="hint" style="margin-top:6px;">' + (hits.length ? hits.map(function(k){ var r = KN.tested[k], nm = k.replace(/\|none\|own$/, '').replace(/\|/g, ' · '); return '<div style="border-top:1px solid var(--border);padding:4px 0;"><b>' + esc(nm) + '</b> — ' + esc(verdictText(r)) + '</div>'; }).join('') : 'Nothing tested matches.') + '</div>' : ''));
    // 2. coin data
    h += card('Coin data', ws ? '<p class="hint" style="margin-top:0;">' + ws.stored + ' of ' + ws.coins + ' coins stored (' + ws.withPerp + ' with a perpetual; ' + ws.fresh + ' up to date' + (ws.lastDay ? ', to ' + dayStr(ws.lastDay) : '') + '). The Autopilot fills and tops this up by itself; the first fill takes about 15–25 minutes with the app open.</p>' +
      '<button class="btn-outline" type="button" id="elabData">' + (ws.busy ? esc(ws.msg || 'Downloading…') : (ws.complete ? 'Update coin data now' : 'Download coin data now')) + '</button>' : '<p class="hint">Data store not ready.</p>');
    // 3. explorer
    var list = st ? safe(cands) || [] : [], screened = st ? Object.keys(st.s1).length : 0, nsurv = st ? st.surv.length : 0, nval = st ? Object.keys(st.s2).length : 0, nbookX = st ? Object.keys(st.book).filter(function(k){ return !st.book[k].research; }).length : 0;
    var top = st ? Object.keys(st.s1).filter(function(k){ return st.s1[k].length === 6; }).sort(function(a, b){ return st.s1[b][1] - st.s1[a][1]; }).slice(0, 12) : [], byKey = {}; list.forEach(function(c){ byKey[c.key] = c; });
    h += card('Explorer — untested ground only', '<p class="hint" style="margin-top:0;">Tier ' + (st ? st.tier : 1) + ': ' + list.length + ' untested candidates (rules × conditions × exits, and new families from the lessons). Screened ' + screened + '; survivors ' + nsurv + ' (A: alpha z ≥ 1.65, costs doubled positive, up in 60% of years); checked on the other half ' + nval + ' (bar now z ≥ ' + bar(Math.max(1, nsurv)).toFixed(2) + ', rising with every survivor); entered the shadow book ' + nbookX + '.</p>' +
      '<button class="btn-outline" type="button" id="elabRun">' + (run.busy ? 'Stop' : 'Explore now') + '</button> <span class="hint">' + esc(run.msg || (st && st.at ? 'Last run ' + st.at.slice(0, 16).replace('T', ' ') + ' UTC. The Autopilot keeps exploring in the background.' : 'The Autopilot explores in the background once the coin data is in.')) + '</span>' +
      (top.length ? '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;"><b>Best screen results so far</b> (half A, a year over the market; most will not survive the other half)</summary><div class="hint" style="margin-top:6px;">' + top.map(function(k){ var r = st.s1[k], v = st.s2[k]; return '<div style="border-top:1px solid var(--border);padding:4px 0;">' + esc(byKey[k] ? L.label(byKey[k]) : k) + '<br><span class="mono">A ' + f1(r[0]) + '% z ' + r[1].toFixed(2) + (v ? ' · B ' + f1(v[0]) + '% z ' + (+v[1]).toFixed(2) + ' (bar ' + (+v[6]).toFixed(2) + ')' + (st.book[k] ? ' → shadow book' : ' → failed') : '') + '</span></div>'; }).join('') + '</div></details>' : '') +
      (st && st.log.length ? '<details style="margin-top:6px;"><summary class="hint" style="cursor:pointer;"><b>Log</b></summary><div class="hint mono" style="margin-top:6px;">' + st.log.map(esc).join('<br>') + '</div></details>' : ''));
    // 4. the shadow book and edges
    var bk = st ? Object.keys(st.book) : [], gc = gridCache;
    h += card('Edges and the shadow book', '<p class="hint" style="margin-top:0;">Every rule that passed both halves, plus the research winners, tracked forward on all coins from the day it entered. It becomes an <b>EDGE</b> when at least ' + MIN_FWD + ' forward weeks clear z ≥ ' + bar(bk.length).toFixed(2) + ' (the bar over the ' + bk.length + ' entries). Retired after ' + RETIRE_WEEKS + ' flat weeks or a ' + Math.round(-100*RETIRE_FALL) + '% fall.</p>' +
      (function(){ var rank = function(k){ var c = (st.stat[k] || {}).code; return c === 'EDGE' ? 0 : (st.book[k].research ? 1 : (c === 'RETIRED' ? 3 : 2)); }, bz = function(k){ var S = (st.stat[k] || {}).S || {}; return (S.n ? S.z : 0) + (st.s2[k] ? +st.s2[k][1]/100 : 0); };
        var ord = bk.sort(function(a, b){ return (rank(a) - rank(b)) || (bz(b) - bz(a)); }), shown = ord.filter(function(k, i){ return rank(k) < 2 || i < 25 + ord.filter(function(x){ return rank(x) < 2; }).length; }), rest = ord.filter(function(k){ return shown.indexOf(k) < 0; });
        return shown.map(row).join('') + (rest.length ? '<details style="margin-top:6px;"><summary class="hint" style="cursor:pointer;"><b>' + rest.length + ' more in the shadow book</b> (no forward week stands out yet)</summary><div class="hint" style="margin-top:6px;">' + rest.slice(0, 300).map(function(k){ var S = (st.stat[k] || {}).S || {}; return esc(label(k)) + (S.n ? ' · ' + S.n + ' wk, z ' + S.z.toFixed(2) : (st.s2[k] ? ' · B z ' + (+st.s2[k][1]).toFixed(2) : '')); }).join('<br>') + (rest.length > 300 ? '<br>…' : '') + '</div></details>' : ''); })());
    function row(k){ var E = st.book[k], S = (st.stat[k] || {}).S || {}, code = (st.stat[k] || {}).code || 'SHADOW', col = code === 'EDGE' ? 'var(--bull)' : code === 'RETIRED' ? 'var(--bear)' : 'var(--text)';
        var out = '<div style="border-top:1px solid var(--border);padding:7px 0;"><div><b style="color:' + col + ';">' + code + '</b> · <b>' + esc(label(k)) + '</b></div><div class="hint" style="margin:2px 0 0;">' + esc(E.origin) + '; forward from ' + dayStr(E.start) + ': ' + (S.n ? S.n + ' week' + (S.n === 1 ? '' : 's') + ', ' + f1(100*S.cum, 2) + '% in all, ' + f1(S.alpha) + '% a year over the market, z ' + S.z.toFixed(2) + ', worst fall ' + f1(100*S.worst, 1) + '%' : 'no forward week finished yet') + '</div>';
        if(code === 'EDGE' && gc && gc.G){ var P = safe(function(){ return positions(gc.G, E.cand, eq); }); if(P) out += ordersHtml(P, eq, gc.lastDay); }
        return out + '</div>'; }
    // 5. coin by coin
    var cv = st && st.coins;
    h += card('Coin by coin', cv ? '<p class="hint" style="margin-top:0;color:var(--amber);"><b>Information, not an edge.</b> On this data a coin’s best rule of one year ranked, on average, at the ' + (cv.persistence.avgPct == null ? '—' : cv.persistence.avgPct.toFixed(0)) + 'th percentile the next year (50 = chance; ' + cv.persistence.hits + ' of ' + cv.persistence.n + ' coin-years above the median). Research found the same in round 9 (40%).</p>' +
      '<div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Coin</th><th>Best rule, last 365 days (as of ' + esc(cv.asOf) + ')</th><th>Its return</th></tr></thead><tbody>' + cv.rows.slice(0, 25).map(function(r){ return '<tr><td><b>' + esc(r[0].replace(/USDT$/, '')) + '</b></td><td>' + esc(r[1]) + '</td><td class="mono">' + f1(r[2]) + '%</td></tr>'; }).join('') + '</tbody></table></div>' : '<p class="hint" style="margin-top:0;">Worked out after the explorer’s first full pass.</p>');
    // 6. how it decides
    h += card('How it decides', '<ul class="hint" style="margin:0;padding-left:18px;"><li>Never re-tests anything in the built-in knowledge; explores only new combinations and new families.</li><li>Screened on half the coins, checked once on the other half; the bar rises with every survivor, so luck does not pass.</li><li>Only forward weeks make an EDGE; the bar rises with every rule in the book.</li><li>The coins’ history was seen by research for the base rules; the combinations are new, but forward weeks are the only truly new evidence.</li><li>Paper only: OMEGA shows orders, you place them.</li></ul>');
    host.innerHTML = h;
    var s = el('elabSearch'); if(s){ s.oninput = function(){ ui.q = s.value; clearTimeout(s._t); s._t = setTimeout(function(){ render().then(function(){ var x = el('elabSearch'); if(x){ x.focus(); x.setSelectionRange(x.value.length, x.value.length); } }); }, 250); }; }
    var bd = el('elabData'); if(bd) bd.onclick = function(){ var W2 = window.OMEGA_WIDE; if(!W2) return; bd.disabled = true; (async function(){ var r; do { r = await W2.runNow(30e3, function(m){ var b2 = el('elabData'); if(b2) b2.textContent = m; }); render(); } while(r && !r.error && !(await W2.status()).complete && el('page-edgelab').classList.contains('active')); render(); })(); };
    var br = el('elabRun'); if(br) br.onclick = function(){ exploreAll(); }; }
  function verdictText(r){ var v = r.v || '', s1 = r.s1 ? 'design ' + f1(r.s1[0]) + '% (z ' + r.s1[1] + ')' : '', s2 = r.s2 ? '; 140 coins ' + f1(r.s2[0]) + '% (z ' + r.s2[1] + ')' : '', fin = r.fin ? '; untouched ' + f1(r.fin[0]) + '% (z ' + r.fin[1] + ')' : '';
    var t = { screen:'failed the screen', validation:'failed the check on 140 coins', final:'failed on the untouched coins', PASS:'PASSED', design:'failed the design check', duplicate:'duplicate' }[v.replace('+part', '')] || v; return 'round ' + r.r + ': ' + t + (/part/.test(v) ? ' (part of a winning blend)' : '') + (s1 || s2 || fin ? ' — ' + s1 + s2 + fin : ''); }
  function ordersHtml(P, eq, lastDay){ var h = '', nm = function(s){ return '<b>' + esc(s.replace(/USDT$/, '')) + '</b>'; };
    P.pairs.forEach(function(Q){ var open = Q.hold.filter(function(s){ return Q.prev.indexOf(s) < 0; }), shut = Q.prev.filter(function(s){ return Q.hold.indexOf(s) < 0; });
      h += '<div class="hint" style="margin:4px 0;border-left:3px solid var(--gold);padding-left:8px;"><b>Harvest pairs</b> (decided ' + dayStr(Q.a) + '; ' + Q.each.toFixed(2) + ' USDT of the coin + the same short perpetual each): ' + (Q.hold.length ? Q.hold.map(nm).join(', ') : 'none') + (open.length ? '<br>Open ' + open.map(nm).join(', ') : '') + (shut.length ? '<br>Close ' + shut.map(nm).join(', ') : '') + '</div>'; });
    var ks = Object.keys(P.dir).sort(function(a, b){ return Math.abs(P.dir[b]) - Math.abs(P.dir[a]); });
    h += '<div class="hint" style="margin:4px 0;"><b>Perpetual positions after the close of ' + dayStr(lastDay) + '</b> (USDT for ' + eq + '; you place them, OMEGA places none): ' + (ks.length ? ks.map(function(s){ var v = P.dir[s]; return nm(s) + ' ' + (v > 0 ? 'long ' : 'short ') + Math.abs(v).toFixed(2); }).join(' · ') : 'none') + '</div>';
    return h; }
  function report(){ if(!st) return null; var S = {}; Object.keys(st.book).forEach(function(k){ S[k] = { origin:st.book[k].origin, start:dayStr(st.book[k].start), status:(st.stat[k] || {}).code || 'SHADOW', forward:(st.stat[k] || {}).S || null }; });
    return { plan:'PLAN13', tier:st.tier, screened:Object.keys(st.s1).length, survivors:st.surv.length, checked:Object.keys(st.s2).length, book:S, coinView:st.coins ? { asOf:st.coins.asOf, persistence:st.coins.persistence } : null, knowledge:{ tested:Object.keys(KN.tested).length, combos:Object.keys(KN.combos).length, earlier:KN.earlier.length } }; }
  function every(){ if(!st) return 10*60e3; if(st.phase !== 'done') return 4*60e3; return 3*3600e3; }
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'edgelab'; })) return true;
    J.push({ id:'edgelab', lane:'heavy', prio:3, label:'Edge Lab (looks for untested edges)', what:'Screens untested rule combinations on half the coins, checks survivors on the other half, and tracks the shadow book forward on all coins. Paper only.', every:every, run:function(){ return runNow(40e3); } }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var nav0 = window.navigate; if(typeof nav0 === 'function') window.navigate = function(p){ var r = nav0.apply(this, arguments); if(p === 'edgelab') setTimeout(render, 60); return r; };
  setTimeout(function(){ load().then(function(){ var pg = el('page-edgelab'); if(pg && pg.classList.contains('active')) render(); }).catch(function(){}); }, 2500);
  window.OMEGA_EDGELAB = { runNow:runNow, render:render, report:report, state:function(){ return st; }, reset:function(){ st = blank(); candCache = null; return save(); }, KNOWLEDGE:KN, bar:bar, invNorm:invNorm, half:half, _:{ fwdStats:fwdStats, judgeFwd:judgeFwd, explore:explore, forward:forward, grids:grids, positions:positions, coinView:coinView, load:load } };
})();
</script>
