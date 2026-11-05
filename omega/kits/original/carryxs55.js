<script>/* ═══ FUNDING CARRY, WEEKLY (v6.5.55) — the one rule that passed the off-phone research; frozen, paper only, judged forward ═══
   Rule carry-xs-7d, frozen 18 Oct 2026. It was chosen on 2024–25 and then passed its one test on 2026, data it had never
   been run on. At each Sunday's daily close (00:00 UTC Monday) it ranks the 25 crypto markets below by the funding paid
   over the last 7 days. It shorts the 5 highest (where leveraged buyers pay the most) and buys the 5 lowest, each 1/5 of
   the account (gross 2x), and holds for the week. With fewer than 15 rankable markets it holds nothing. Tied markets
   share their average rank, as in the research, so a side can hold a few more or fewer than 5. Costs are 0.06% a side on
   every change, and funding is paid and received on the held positions. Weeks decided at or after the close of Sunday
   18 Oct 2026 form the forward record.
   Paper only: OMEGA never places an order, and this changes nothing in CREED, the Autopilot or any other strategy. */
(function(){
  'use strict';
  var KEY = 'omega_carryxs_v1', DAY = 86400e3, LB = 7, K = 5, MIN_N = 15, COST_SIDE = 0.0006,
      FREEZE_DAY = Date.UTC(2026, 9, 18)/DAY,                  // Sunday 18 Oct 2026: decisions at its close or later are forward
      FWD_MIN = 26, FWD_FULL = 52, FWD_BAR = 1.96, FWD_STOP = -0.25;
  var UNIVERSE = ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','TRXUSDT','DOTUSDT','BCHUSDT',
    'NEARUSDT','ATOMUSDT','UNIUSDT','APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','FILUSDT','ICPUSDT','ETCUSDT','XLMUSDT','INJUSDT'];
  // What the research found, fixed here as it was reported (18 Oct 2026). "Research" = the test as run; "as the app runs it" =
  // the same rule computed the way this module computes it (positions held all week, exact ties), on the same data.
  var RESEARCH = {
    rule:'carry-xs-7d', frozenAt:'2026-10-18', data:'25 crypto markets, hourly prices and 8-hourly funding, Oct 2023 – 17 Oct 2026 (your exported history)',
    chosen:'Round 4 (funding), 6 variants. Chosen on 30 Dec 2023 – 31 Dec 2025: the best of its type, positive after costs in both 2024 and 2025.',
    design:{ period:'2024–25', annPct:54.4, t:2.57, worstFallPct:-20.0, pricePct:48, fundingPct:11, costsPct:-6 },
    test:{ period:'2026 (5 Jan \u2013 18 Oct, 41 weeks; the last week had 6 days of data)', annPct:105.8, t:2.88, bar:2.58, barWhy:'one-sided 5%, Bonferroni over every look at 2026 (10)', costs2xPct:99.3, worstFallPct:-6.2, passed:true },
    asApp:{ design:{ annPct:61.6, t:2.93, worstFallPct:-17.2 }, test:{ annPct:117.0, t:2.77, worstFallPct:-5.9 } },
    robustness:[ 'Rebalancing on Monday, Wednesday or Friday instead of Sunday: 2026 +62%, +20%, +66% a year (Sunday was one of the luckier days)',
      'Holding 3, 4, 6 or 8 markets a side instead of 5: +60% to +111% a year in 2026',
      'Funding averaged over 3 or 14 days instead of 7: +102% and +54%',
      'Acting a day late: +45%', 'Without its best 3 weeks of 2026: +43.5%', 'For scale: holding all 25 markets equally made +8.5% in 2026' ],
    caveats:[ 'Gross exposure is 2× the account (each side 100%). A bad week for this rule is a bad week for the whole account.',
      'Most of the profit came from price, not from collecting funding: shorting the most crowded markets and holding the least crowded. Funding added about 11% a year.',
      'Its worst fall was −17% to −20% in 2024–25. The −6% of 2026 is not its normal worst.',
      'The 25 markets are the ones listed today; coins that collapsed and were delisted are missing from the test (survivorship).',
      'The decisive check is still open: the same rule on Jan 2019 – Sep 2023, which nothing here has ever been tested on.' ],
    older:null };   // the 2019–2023 result goes here when that test is run
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function el(id){ return document.getElementById(id); }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function lsGet(k, d){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v && typeof v === 'object' && !Array.isArray(v) ? v : d; }catch(e){ return d; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function Y(){ return window.OMEGA_CALM && window.OMEGA_CALM.y ? window.OMEGA_CALM.y() : new Promise(function(r){ setTimeout(r, 0); }); }
  function dayStr(d){ return new Date(d*DAY).toISOString().slice(0, 10); }
  function dayName(d){ return ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][new Date(d*DAY).getUTCDay()] + ' ' + new Date(d*DAY).getUTCDate() + ' ' + ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][new Date(d*DAY).getUTCMonth()]; }
  var st = lsGet(KEY, null) || { v:1, rec:{}, res:null, retired:null, noted:'' }, run = { busy:false, msg:'' };
  if(!st.rec) st.rec = {};

  // ── the rule (pure: data in, weeks out) ──
  // data: { SYM: { k0: first UTC day number (ms/DAY), c: [daily close or null, one per day from k0], fund: [[ms, rate], ...] } }
  function nwT(x, lag){ lag = lag || 2; x = x.filter(function(v){ return isFinite(v); }); var n = x.length; if(n < 8) return null;
    var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g0 = e.reduce(function(a, v){ return a + v*v; }, 0)/n, lrv = g0;
    for(var k=1; k<=lag; k++){ var s = 0; for(var i=k; i<n; i++) s += e[i]*e[i-k]; lrv += 2*(1 - k/(lag + 1))*s/(n - k); }
    return lrv > 0 ? m/Math.sqrt(lrv/n) : null; }
  function prep(data){ var P = {};
    Object.keys(data || {}).forEach(function(s){ var x = data[s]; if(!x || !x.c || !x.c.length) return; var fi = {}, ff = {}, f0 = null, f1 = null;
      (x.fund || []).forEach(function(q){ var t = +q[0], r = +q[1]; if(!isFinite(t) || !isFinite(r)) return; var d = Math.floor(t/DAY);
        fi[d] = (fi[d] || 0) + Math.round(r*1e8); ff[d] = (ff[d] || 0) + r; if(f0 == null || t < f0) f0 = t; if(f1 == null || t > f1) f1 = t; });
      P[s] = { k0:x.k0, c:x.c, fi:fi, ff:ff, f0:f0, f1:f1 }; });
    return P; }
  function close(p, d){ if(!p) return null; var i = d - p.k0, v = i >= 0 && i < p.c.length ? p.c[i] : null; return v > 0 ? v : null; }
  function fundedThrough(p, d){ return p.f1 != null && p.f1 >= d*DAY + 16*3600e3; }          // the day's 16:00 UTC settlement is in
  function rankable(p, a){ return close(p, a) != null && p.f0 != null && p.f0 <= (a - LB + 1)*DAY && fundedThrough(p, a); }
  function sum7(p, a){ var s = 0; for(var d=a-LB+1; d<=a; d++) s += p.fi[d] || 0; return s; }
  function basketAt(P, U, a){ var E = U.filter(function(s){ return rankable(P[s], a); }), n = E.length, v = {}, rk = {}, w = {};
    if(n < MIN_N) return { n:n, w:w, s7:v };
    E.forEach(function(s){ v[s] = sum7(P[s], a); });
    var ord = E.slice().sort(function(x, y){ return (v[y] - v[x]) || (x < y ? -1 : 1); }), i = 0;
    while(i < n){ var j = i; while(j + 1 < n && v[ord[j + 1]] === v[ord[i]]) j++; for(var q=i; q<=j; q++) rk[ord[q]] = (i + j + 2)/2; i = j + 1; }   // average rank of a tie
    E.forEach(function(s){ if(rk[s] <= K) w[s] = -1/K; else if(rk[s] > n - K) w[s] = 1/K; });
    return { n:n, w:w, s7:v }; }
  // a decision is ready when every market that traded that day has its funding through 16:00 UTC (or 4 days have passed)
  function ready(P, U, a, now){ if(now >= (a + 4)*DAY) return true;
    return U.every(function(s){ var p = P[s], last = p.k0 + p.c.length - 1; if(p.k0 > a || last < a - 3) return true;   // not listed yet, or its history stopped days ago
      return close(p, a) != null && fundedThrough(p, a); }); }
  function complete(P, w, b, now){ var ks = Object.keys(w); if(now < (b + 1)*DAY) return false;
    var ok = ks.every(function(s){ return close(P[s], b) != null && fundedThrough(P[s], b); });
    return ok || now >= (b + 4)*DAY; }
  function weekResult(P, a, w, prev){ var b = a + 7, g = 0, fd = 0, drift = {}, miss = [];
    Object.keys(w).forEach(function(s){ var p = P[s], x = w[s], p0 = close(p, a), p1 = close(p, b); if(p0 == null) return;
      if(p1 == null){ for(var d=b-1; d>a && p1 == null; d--) p1 = close(p, d); if(p1 == null) p1 = p0; miss.push(s); }
      g += x*(p1/p0 - 1);
      for(var e=a+1; e<=b; e++){ var pc = close(p, e - 1); fd += x*(p.ff[e] || 0)*((pc == null ? p0 : pc)/p0); }   // a long pays positive funding
      drift[s] = x*p1/p0; });
    var keys = {}; Object.keys(w).concat(Object.keys(prev)).forEach(function(s){ keys[s] = 1; });
    var turn = 0; Object.keys(keys).forEach(function(s){ turn += Math.abs((w[s] || 0) - (prev[s] || 0)); });
    var cost = turn*COST_SIDE, r = g - fd - cost, nx = {}; Object.keys(drift).forEach(function(s){ nx[s] = drift[s]/(1 + r); });
    return { a:a, r:r, gross:g, fund:fd, cost:cost, next:nx, miss:miss }; }
  function stats(list){ var n = list.length; if(!n) return { n:0 };
    var x = list.map(function(q){ return q.r; }), m = x.reduce(function(a, b){ return a + b; }, 0)/n, eq = 1, pk = 1, dd = 0;
    x.forEach(function(r){ eq *= 1 + r; if(eq > pk) pk = eq; if(eq/pk - 1 < dd) dd = eq/pk - 1; });
    function avg(k){ return list.reduce(function(a, q){ return a + q[k]; }, 0)/n*52; }
    return { n:n, mean:m, ann:m*52, t:nwT(x), cum:eq - 1, worstFall:dd, posWeeks:x.filter(function(r){ return r > 0; }).length/n, price:avg('gross'), funding:-avg('fund'), costs:-avg('cost') }; }
  function compute(data, opt){ opt = opt || {}; var now = opt.now || Date.now(), P = prep(data), U = (opt.universe || UNIVERSE).filter(function(s){ return P[s]; }), rec = opt.rec || {};
    if(U.length < MIN_N) return { at:now, markets:U.length, error:'needs at least ' + MIN_N + ' of the ' + UNIVERSE.length + ' carry markets with stored history (has ' + U.length + ')' };
    var k0 = Infinity, k1 = -Infinity; U.forEach(function(s){ var p = P[s]; if(p.k0 < k0) k0 = p.k0; if(p.k0 + p.c.length - 1 > k1) k1 = p.k0 + p.c.length - 1; });
    var a = k0 + LB - 1; while(new Date(a*DAY).getUTCDay() !== 0) a++;
    var weeks = [], prev = {}, started = false, cur = null, mism = 0, newRec = {};
    for(; a <= k1; a += 7){
      if(!ready(P, U, a, now)) break;
      var B = basketAt(P, U, a), w = B.w;
      if(!started){ if(B.n < MIN_N) continue; started = true; }
      if(a >= FREEZE_DAY){ var R0 = rec[a]; if(R0 && R0.w){ if(JSON.stringify(sortObj(R0.w)) !== JSON.stringify(sortObj(w))) mism++; w = R0.w; } else newRec[a] = { w:w, n:B.n, at:now }; }
      if(!complete(P, w, a + 7, now)){ cur = { a:a, w:w, n:B.n, s7:B.s7 }; break; }
      var R = weekResult(P, a, w, prev); prev = R.next;
      weeks.push({ a:a, end:a + 7, r:R.r, gross:R.gross, fund:R.fund, cost:R.cost, nS:Object.keys(w).filter(function(s){ return w[s] < 0; }).length, nL:Object.keys(w).filter(function(s){ return w[s] > 0; }).length, miss:R.miss.length ? R.miss : undefined, fwd:a >= FREEZE_DAY }); }
    if(!cur && started){ var aN = a; if(aN <= k1 && ready(P, U, aN, now)){ var BN = basketAt(P, U, aN); cur = { a:aN, w:BN.w, n:BN.n, s7:BN.s7 }; } }
    function inEnd(lo, hi){ return weeks.filter(function(q){ var t = q.end*DAY; return t >= lo && t < hi; }); }
    var fwd = weeks.filter(function(q){ return q.fwd; });
    return { at:now, markets:U.length, lastDay:k1, from:k0, weeks:weeks, current:cur, newRec:newRec, recMismatch:mism,
      before:{ y2425:stats(inEnd(Date.UTC(2024, 0, 1), Date.UTC(2026, 0, 1))), y26:stats(weeks.filter(function(q){ return !q.fwd && q.end*DAY >= Date.UTC(2026, 0, 1); })), all:stats(weeks.filter(function(q){ return !q.fwd; })) },
      forward:stats(fwd) }; }
  function sortObj(o){ var r = {}; Object.keys(o || {}).sort().forEach(function(k){ r[k] = Math.round(o[k]*1e6)/1e6; }); return r; }
  // ── the forward judgement, written 18 Oct 2026 before any forward week ──
  function verdict(F, retired){ if(retired) return { code:'RETIRED', text:'Retired on ' + retired.at.slice(0, 10) + ': ' + retired.why + '. A retired rule never returns.' };
    if(!F || !F.n) return { code:'WAIT', text:'No forward week has finished yet. The first one runs from the close of Sunday 18 Oct 2026 to the close of Sunday 25 Oct.' };
    if(F.worstFall <= FWD_STOP) return { code:'RETIRE', why:'fell ' + Math.round(-F.worstFall*100) + '% from its forward peak (limit 25%, more than any fall in its 2.8 tested years)' };
    if(F.n < FWD_MIN) return { code:'COLLECT', text:F.n + ' of ' + FWD_MIN + ' forward weeks. Too early to judge; a few weeks prove nothing either way.' };
    if(F.mean <= 0) return { code:'RETIRE', why:'its ' + F.n + ' forward weeks average zero or less' };
    if(F.t != null && F.t >= FWD_BAR) return { code:'CONFIRMED', text:'Confirmed on ' + F.n + ' forward weeks (z ' + F.t.toFixed(2) + ' ≥ ' + FWD_BAR + '). Still paper only; the next check is at ' + (F.n < FWD_FULL ? FWD_FULL + ' weeks' : 'every new week') + '.' };
    if(F.n < FWD_FULL) return { code:'HOLDING', text:'Positive on ' + F.n + ' forward weeks but not yet clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + ', needs ' + FWD_BAR + '). Judged again at ' + FWD_FULL + ' weeks.' };
    return { code:'UNPROVEN', text:'Positive after ' + F.n + ' forward weeks but not clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + '). Stays on paper, unproven.' }; }

  // ── data from the app's own stores ──
  async function loadData(onMsg){ var H = window.OMEGA_HISTORY, D = window.OMEGA_DERIV, out = {}; if(!H) throw new Error('history store not ready');
    var idx = safe(function(){ return H.index(); }) || {};
    for(var q=0; q<UNIVERSE.length; q++){ var s = UNIVERSE[q]; if(!idx[s]) continue; if(onMsg) onMsg('Reading ' + s + ' (' + (q + 1) + ' of ' + UNIVERSE.length + ')');
      var ser = null; try{ ser = await H.load(s, { stitch:true }); }catch(e){} if(!ser || !ser.n) continue;
      var d = (await H.resampleA(ser, 1440)).filter(function(r){ return !r.partial; }); ser = null; await Y(); if(d.length < 14) continue;
      var k0 = Math.round(d[0].time/86400), c = [];
      d.forEach(function(r){ var k = Math.round(r.time/86400) - k0; if(k >= 0) c[k] = +r.c; }); for(var i=0; i<c.length; i++) if(!(c[i] > 0)) c[i] = null;
      var fund = []; try{ if(D && D.load){ var rc = await D.load(s); if(rc && rc.fund) fund = rc.fund.slice(); } }catch(e){}
      out[s] = { k0:k0, c:c, fund:fund }; }
    return out; }
  function compact(res){ if(!res || res.error) return res;
    return { at:res.at, markets:res.markets, lastDay:res.lastDay, from:res.from, before:res.before, forward:res.forward, recMismatch:res.recMismatch,
      weeks:res.weeks.map(function(q){ return [q.end, +q.r.toFixed(6), +q.gross.toFixed(6), +q.fund.toFixed(6), +q.cost.toFixed(6), q.nS, q.nL, q.fwd ? 1 : 0]; }),
      current:res.current ? { a:res.current.a, n:res.current.n, w:res.current.w, s7:res.current.s7 } : null }; }
  async function runNow(){ if(run.busy) return { skip:true, text:'already running' }; run.busy = true; run.msg = 'Starting'; render();
    try{ var data = await loadData(function(m){ run.msg = m; render(); });
      var res = compute(data, { now:Date.now(), rec:st.rec });
      if(res.error){ st.res = { at:res.at, error:res.error, markets:res.markets }; lsSet(KEY, st); return { skip:true, text:res.error, retryIn:6*3600e3 }; }
      Object.keys(res.newRec).forEach(function(a){ st.rec[a] = res.newRec[a]; });
      var V = verdict(res.forward, st.retired);
      if(V.code === 'RETIRE' && !st.retired){ st.retired = { at:new Date().toISOString(), why:V.why, weeks:res.forward.n }; V = verdict(res.forward, st.retired); }
      st.res = compact(res); st.verdict = V; lsSet(KEY, st); note(res, V);
      return { text:summaryText() }; }
    catch(e){ return { error:(e && e.message) || String(e) }; }
    finally{ run.busy = false; run.msg = ''; render(); } }
  function pct(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(100*v).toFixed(d == null ? 1 : d) + '%'; }
  function summaryText(){ var r = st.res, V = st.verdict || {}; if(!r || r.error) return 'Funding carry: ' + ((r && r.error) || 'not run yet');
    var F = r.forward || {}; return 'Funding carry (weekly): ' + (F.n ? F.n + ' forward week' + (F.n === 1 ? '' : 's') + ', ' + pct(F.cum) + ' so far' : 'no forward week finished yet') + '; ' + (V.code || '').toLowerCase() + (r.current ? '; basket decided ' + dayStr(r.current.a) : '') + '.'; }
  function note(res, V){ if(st.noted === V.code) return;
    safe(function(){ var B = window.OMEGA_BRAIN; if(!B || !B.feedObservation) return; if(B.retract) B.retract(['Funding carry, weekly (carry-xs-7d)']);
      B.feedObservation({ pinned:true, strat:'omega', tf:'1d', symbol:'*', text:'Funding carry, weekly (carry-xs-7d): the one rule that passed the off-phone research (chosen on 2024–25, then +106% a year on 2026, z 2.88 against a bar of 2.58; worst fall −20% in 2024–25). Each Sunday close: short the 5 of 25 markets paying the most funding over 7 days, buy the 5 paying least, each 1/5 of the account. Frozen 18 Oct 2026; paper only. Forward: ' + ((V.text || V.why || V.code) + '') + ' The 2019–2023 test is still to be run.' }); });
    st.noted = V.code; lsSet(KEY, st); }

  // ── the card ──
  function render(){ var host = el('carryxsCard'); if(!host){ var pg = el('page-ostrat'); if(!pg) return; host = document.createElement('div'); host.id = 'carryxsCard'; pg.insertBefore(host, pg.firstChild); }
    var r = st.res, V = st.verdict || verdict(null, st.retired), eq = safe(function(){ return window.OMEGA_AUTOPILOT.cfg().startEquity; }) || 100, Rz = RESEARCH;
    var lab = { WAIT:['Paper \u00b7 forward record starts at Sunday 18 Oct\u2019s close','warn'], COLLECT:['Paper · collecting forward weeks','warn'], HOLDING:['Paper · positive, not yet proven','warn'], CONFIRMED:['Paper · confirmed forward','bull'], UNPROVEN:['Paper · unproven','warn'], RETIRED:['Retired','bear'] }[V.code] || ['Paper','warn'];
    var h = '<div class="card" style="margin-bottom:14px;border-color:var(--gold);"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;"><div><h2 style="color:var(--gold);margin-bottom:4px;">Funding carry, weekly — the one rule that passed the research</h2><span class="bt-lab ' + lab[1] + '">' + esc(lab[0]) + '</span></div>' +
      '<button class="btn-outline" type="button" id="carryxsRun"' + (run.busy ? ' disabled' : '') + '>' + (run.busy ? esc(run.msg || 'Working') : 'Update now') + '</button></div>' +
      '<p class="hint" style="margin-top:8px;">Every Sunday at the daily close (00:00 UTC Monday): of the 25 crypto markets OMEGA studies, <b>short the 5 where leveraged buyers paid the most funding over the last 7 days</b> and <b>buy the 5 that paid the least</b>, each 1/5 of the account, and hold for the week. The idea: when buyers crowd a coin with borrowed money, they pay to hold it, and crowded coins tend to lag. Frozen on ' + esc(Rz.frozenAt) + '. <b>Paper only.</b> OMEGA places no orders and this changes nothing else.</p>';
    if(!r){ h += '<p class="hint">' + (run.busy ? esc(run.msg) : 'Not worked out yet. It reads daily closes from the stored history and funding from the positioning store. The Autopilot runs it twice a day and right after each Sunday close.') + '</p>'; }
    else if(r.error){ h += '<p class="hint">' + esc(r.error) + '.</p>'; }
    else {
      var c = r.current;
      if(c && c.w && Object.keys(c.w).length){ var ks = Object.keys(c.w), sh = ks.filter(function(s){ return c.w[s] < 0; }).sort(function(x, y){ return c.s7[y] - c.s7[x]; }), lg = ks.filter(function(s){ return c.w[s] > 0; }).sort(function(x, y){ return c.s7[x] - c.s7[y]; });
        var row = function(s){ return '<tr><td class="mono">' + esc(s.replace(/USDT$/, '')) + '</td><td class="mono">' + (c.s7[s] < 0 ? '\u2212' : '') + Math.abs(c.s7[s]/7/1e8*100).toFixed(4) + '%</td><td class="mono">' + (Math.abs(c.w[s])*eq).toFixed(2) + '</td></tr>'; };
        var fwdTag = c.a >= FREEZE_DAY ? '' : ' <span class="dim">(decided before the freeze, so not part of the forward record)</span>';
        h += '<h3 style="font-size:14px;margin:12px 0 4px;">This week’s basket: decided at the close of ' + esc(dayName(c.a)) + ', held to the close of ' + esc(dayName(c.a + 7)) + fwdTag + '</h3>' +
          '<div style="display:flex;gap:14px;flex-wrap:wrap;"><div style="flex:1;min-width:200px;"><b style="color:var(--bear);">Short (' + sh.length + ')</b><table class="creed-events"><thead><tr><th>Market</th><th>Funding a day</th><th>USDT at ' + eq + '</th></tr></thead><tbody>' + sh.map(row).join('') + '</tbody></table></div>' +
          '<div style="flex:1;min-width:200px;"><b style="color:var(--bull);">Long (' + lg.length + ')</b><table class="creed-events"><thead><tr><th>Market</th><th>Funding a day</th><th>USDT at ' + eq + '</th></tr></thead><tbody>' + lg.map(row).join('') + '</tbody></table></div></div>' +
          (c.a + 7 <= lastSunday() ? '<p class="hint" style="color:var(--amber);">This basket\u2019s week has ended. The next one is worked out as soon as Sunday\u2019s close and funding are stored (the Autopilot\u2019s history and positioning jobs).</p>' : '') +
          '<p class="hint">Ranked ' + c.n + ' markets. Sizes are 1/5 of the Autopilot’s ' + eq + ' USDT each, so the total held is ' + (eq*(sh.length + lg.length)/5).toFixed(0) + ' USDT (2× the account). "Funding a day" is the 7-day average of what a long paid per day (a negative figure means shorts paid longs). Next basket: at the close of ' + esc(dayName(c.a + 7)) + '.</p>'; }
      else if(c){ h += '<p class="hint">The week from the close of ' + esc(dayName(c.a)) + ' holds nothing (only ' + c.n + ' markets could be ranked; the rule needs ' + MIN_N + ').</p>'; }
      else h += '<p class="hint">Waiting for Sunday’s close and funding to be stored before the next basket can be worked out.</p>';
      var F = r.forward || {};
      h += '<h3 style="font-size:14px;margin:12px 0 4px;">Forward record (weeks decided after the freeze)</h3><p class="hint" style="margin-top:0;"><b>' + esc(V.text || V.why || '') + '</b>' +
        (F.n ? ' ' + F.n + ' week' + (F.n === 1 ? '' : 's') + ': ' + pct(F.cum) + ' in all (' + (F.cum >= 0 ? '+' : '\u2212') + Math.abs(F.cum*eq).toFixed(2) + ' USDT on ' + eq + '), ' + pct(F.ann, 0) + ' a year at this pace, worst fall ' + pct(F.worstFall) + ', ' + Math.round(F.posWeeks*100) + '% of weeks up' + (F.t != null ? ', z ' + F.t.toFixed(2) : '') + '.' : '') +
        (r.recMismatch ? ' Note: ' + r.recMismatch + ' recorded basket(s) differ from a recount on later data; the record keeps the basket as it was first decided.' : '') + '</p>';
      var fw = (r.weeks || []).filter(function(q){ return q[7]; }).slice(-8).reverse();
      if(fw.length) h += '<div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Week to</th><th>Result</th><th>Price</th><th>Funding</th><th>Costs</th></tr></thead><tbody>' + fw.map(function(q){ return '<tr><td class="mono">' + dayStr(q[0]) + '</td><td class="mono" style="color:' + (q[1] >= 0 ? 'var(--bull)' : 'var(--bear)') + ';">' + pct(q[1], 2) + '</td><td class="mono">' + pct(q[2], 2) + '</td><td class="mono">' + pct(-q[3], 2) + '</td><td class="mono">' + pct(-q[4], 2) + '</td></tr>'; }).join('') + '</tbody></table></div>';
      var b = r.before || {};
      function line(lab0, S){ return S && S.n ? '<tr><td>' + lab0 + '</td><td class="mono">' + S.n + '</td><td class="mono">' + pct(S.ann, 0) + '</td><td class="mono">' + (S.t == null ? '—' : S.t.toFixed(2)) + '</td><td class="mono">' + pct(S.worstFall) + '</td><td class="mono">' + pct(S.price, 0) + ' / ' + pct(S.funding, 0) + ' / ' + pct(S.costs, 0) + '</td></tr>' : ''; }
      h += '<h3 style="font-size:14px;margin:12px 0 4px;">Before the freeze, worked out by this app on your stored history</h3><div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Period</th><th>Weeks</th><th>A year</th><th>z</th><th>Worst fall</th><th>Price / funding / costs a year</th></tr></thead><tbody>' +
        line('2024–25 (chosen here)', b.y2425) + line('2026 to the freeze (the test)', b.y26) + '</tbody></table></div>' +
        '<p class="hint">Data to ' + dayStr(r.lastDay) + ', ' + r.markets + ' markets. Worked out ' + new Date(r.at).toISOString().slice(0, 16).replace('T', ' ') + ' UTC. These should match the research below closely; a large gap means the stored data differ from what was studied.</p>'; }
    h += '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;"><b>How it was found, and what could still be wrong</b></summary>' +
      '<p class="hint">' + esc(Rz.chosen) + ' Test on ' + esc(Rz.test.period) + ', run once: <b>' + pct(Rz.test.annPct/100, 1) + ' a year, z ' + Rz.test.t.toFixed(2) + '</b> against a bar of ' + Rz.test.bar.toFixed(2) + ' (' + esc(Rz.test.barWhy) + '); with costs doubled ' + pct(Rz.test.costs2xPct/100, 1) + '; worst fall ' + pct(Rz.test.worstFallPct/100) + '. In 2024–25: ' + pct(Rz.design.annPct/100) + ' a year (z ' + Rz.design.t.toFixed(2) + '), worst fall ' + pct(Rz.design.worstFallPct/100) + '; from price ' + pct(Rz.design.pricePct/100, 0) + ', funding ' + pct(Rz.design.fundingPct/100, 0) + ', costs ' + pct(Rz.design.costsPct/100, 0) + '. Data: ' + esc(Rz.data) + '. No other idea tested passed (see the outside research record below).</p>' +
      '<p class="hint"><b>Checks that changed one thing at a time</b> (all stayed positive in 2024–25 and in 2026):</p><ul class="hint" style="margin:0;padding-left:18px;">' + Rz.robustness.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
      '<p class="hint"><b>Read it the right way</b></p><ul class="hint" style="margin:0;padding-left:18px;">' + Rz.caveats.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
      '<p class="hint"><b>Forward judgement, fixed on 18 Oct 2026 before any forward week:</b> nothing is judged before ' + FWD_MIN + ' forward weeks. At ' + FWD_MIN + ' weeks or more it is <b>retired</b> if its forward weeks average zero or less. It is <b>confirmed</b> when z (weekly, Newey-West) is ' + FWD_BAR + ' or more, which allows for looking at both ' + FWD_MIN + ' and ' + FWD_FULL + ' weeks. At any time it is retired if it falls ' + Math.round(-FWD_STOP*100) + '% from its forward peak. A retired rule never returns. ' + (Rz.older ? 'Jan 2019 – Sep 2023: ' + esc(Rz.older) : 'The test on Jan 2019 – Sep 2023 has not been run yet: it needs the older-history file (button under Report for review).') + '</p></details></div>';
    host.innerHTML = h; var bt = el('carryxsRun'); if(bt) bt.onclick = function(){ var O = window.OMEGA_OPERATOR; if(O && O.runNow) safe(function(){ O.runNow('carryxs'); }); else runNow(); }; }
  function report(){ var r = st.res; return { rule:'carry-xs-7d', text:'Each Sunday close (00:00 UTC Monday): rank the 25 markets by funding paid over 7 days; short the 5 highest, long the 5 lowest, 1/5 of the account each, hold a week; under 15 rankable: flat; ties share their average rank; costs 0.06% a side; funding on held positions. Paper only.',
    universe:UNIVERSE, frozenAt:RESEARCH.frozenAt, research:RESEARCH, judgement:{ minWeeks:FWD_MIN, fullWeeks:FWD_FULL, bar:FWD_BAR, stopFall:FWD_STOP }, verdict:st.verdict || null, retired:st.retired || null,
    result:r || null, recordedBaskets:st.rec }; }
  function lastSunday(now){ var today = Math.floor((now || Date.now())/DAY), dow = new Date(today*DAY).getUTCDay(); return dow === 0 ? today - 7 : today - dow; }   // the latest Sunday whose close has passed
  function every(){ var r = st.res, lastSun = lastSunday();
    if(r && !r.error && r.current && r.current.a < lastSun) return 30*60e3;                 // a new week has begun: catch up soon
    if(r && !r.error && !r.current) return 2*3600e3;                                         // waiting for Sunday's data
    return 12*3600e3; }
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'carryxs'; })) return true;
    J.push({ id:'carryxs', lane:'heavy', prio:2, label:'Funding carry, weekly (the rule that passed)', what:'Twice a day and soon after each Sunday close: this week’s basket for the frozen funding-carry rule and its forward record, from the stored daily closes and funding. Paper only.', every:every, run:runNow }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var nav0 = window.navigate; if(typeof nav0 === 'function') window.navigate = function(p){ var rr = nav0.apply(this, arguments); if(p === 'ostrat') setTimeout(render, 60); return rr; };
  setTimeout(function(){ try{ render(); }catch(e){} }, 1500);
  window.OMEGA_CARRYXS = { compute:compute, prep:prep, basketAt:basketAt, weekResult:weekResult, verdict:verdict, nwT:nwT, stats:stats, runNow:runNow, render:render, report:report, state:function(){ return st; },
    UNIVERSE:UNIVERSE, RESEARCH:RESEARCH, FREEZE_DAY:FREEZE_DAY, __set:function(s){ st = s; } };
})();
</script>
