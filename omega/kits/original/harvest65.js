<script>/* ═══ FUNDING HARVEST (v6.5.59; 10-coin version added in v6.5.62) — the one idea that passed untouched tests; market-neutral, frozen, paper only ═══
   Rule harvest-30d (PLAN7 T3), frozen 18 Oct 2026. It passed its single test on 51 coins no rule had ever been run on
   (Jan 2020 – Oct 2026): +12.0% a year, z 4.14 against a bar of 2.13, +6.5% with costs doubled, worst fall −2.3%.
   At each Sunday's daily close (00:00 UTC Monday), among the 25 coins OMEGA studies, it holds a coin and shorts its
   perpetual, 1/5 of the account per pair, in the 5 coins whose funding over the last 30 days (scaled to a week) is
   highest and above 0.1% a week. A coin already held stays while it is in the top 10 and its funding is positive.
   Price moves cancel (long spot, short perpetual), and the short collects the funding that leveraged buyers pay.
   Costs are 0.11% (spot) + 0.06% (perpetual) a side on every change. P&L = funding received − costs. The price gap
   between spot and perpetual (basis) is not in the data and is ignored. When funding is low it holds nothing.
   Paper only: OMEGA never places an order, and this changes nothing in CREED or any other strategy. */
(function(){
  'use strict';
  var KEY = 'omega_harvest_v1', DAY = 86400e3, K = 5, KEEP = 10, L = 30, HURDLE = 0.001, SPOT = 0.0011, PERP = 0.0006, MIN_RANKABLE = 5,
      FREEZE_DAY = Date.UTC(2026, 9, 18)/DAY, FWD_MIN = 26, FWD_FULL = 52, FWD_BAR = 1.96, FWD_STOP = -0.10;
  var RESEARCH = {
    rule:'harvest-30d', frozenAt:'2026-10-18',
    fresh:{ data:'51 coins never used in any design or test (AAVE, ALGO, SAND, LDO, …), Jan 2020 – 11 Oct 2026', weeks:346, annPct:12.0, t:4.14, bar:2.13, barWhy:'one-sided 5%, Bonferroni over the 3 rules planned for these coins', costs2xPct:6.5, worstFallPct:-2.3, passed:true,
      years:[ ['2020', 19.4], ['2021', 48.8], ['2022', -1.6], ['2023', 3.9], ['2024', 10.1], ['2025', 1.0], ['2026 (to Oct)', -1.6] ] },
    design:{ data:'the 25 studied coins, Sep 2020 – Oct 2026 (in-sample; this is where the rule was shaped)', annPct:12.1, worstFallPct:-0.6, years:[ ['2020 (Sep–Dec)', 4.6], ['2021', 45.3], ['2022', 2.8], ['2023', 6.6], ['2024', 11.4], ['2025', 1.7], ['2026 (to Oct)', 1.4] ] },
    wide:{ rule:'harvest-wide (R3)', fresh2:{ data:'90 more coins never used before (TRB, SEI, TIA, PENDLE, ENA, …), Jan 2021 \u2013 11 Oct 2026', annPct:8.8, t:3.38, bar:2.45, barWhy:'one-sided 5%, Bonferroni over the 7 round-8 rules that reached the final test', costs2xPct:4.7, worstFallPct:-4.4,
      years:[ ['2021', 36.3], ['2022', 0.2], ['2023', 4.4], ['2024', 12.1], ['2025', -0.8], ['2026 (to Oct)', -2.1] ] }, fresh:{ annPct:12.6, t:4.68, worstFallPct:-2.1 }, design:{ annPct:13.4, worstFallPct:-0.6 },
      others:'Of the ten round-8 strategies, it was the only one to pass all three stages; the crowding and trend rules lost 20\u201336% a year on the 90 new coins.' },
    others:'On the same fresh coins the carry rule (+50% a year, z 1.70, worst fall −83%), carry over 8 coins (+33%, z 1.39, −76%) and 14-day trend (+39%, z 1.58, −65%) all failed.',
    caveats:[ 'Almost all of its money came in boom years, when leveraged buyers pay a lot (2021: +49% on the fresh coins). In 2025 it made +1.0% and in 2026 so far −1.6%. When funding is low it mostly sits out.',
      'The basis (the gap between the perpetual’s price and the coin’s) is not in the data. It is usually small and tends to close, but it can move against the position for a while.',
      'Doing this for real needs the coin and its perpetual on the same exchange, margin for the short perpetual, and trust in that exchange: if the exchange fails, both legs are lost. This app places no orders.',
      'The 51 fresh coins are ones Binance still lists; coins that were delisted are mostly missing (EOS and ICX were included until they stopped trading).' ] };
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function el(id){ return document.getElementById(id); }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function lsGet(k, d){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v && typeof v === 'object' && !Array.isArray(v) ? v : d; }catch(e){ return d; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function dayStr(d){ return new Date(d*DAY).toISOString().slice(0, 10); }
  function dayName(d){ var x = new Date(d*DAY); return ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][x.getUTCDay()] + ' ' + x.getUTCDate() + ' ' + ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][x.getUTCMonth()]; }
  function pct(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(100*v).toFixed(d == null ? 1 : d) + '%'; }
  var st = lsGet(KEY, null) || { v:1, rec:{}, res:null, retired:null, noted:'' }, run = { busy:false, msg:'' };
  if(!st.rec) st.rec = {}; if(!st.rec10) st.rec10 = {};
  // ── the rule (pure) ──
  function prep(data){ var P = {};
    Object.keys(data || {}).forEach(function(s){ var x = data[s]; if(!x || !x.c || !x.c.length) return; var fi = {}, ff = {}, cnt = {}, f0 = null, f1 = null;
      (x.fund || []).forEach(function(q){ var t = +q[0], r = +q[1]; if(!isFinite(t) || !isFinite(r)) return; var d = Math.floor(t/DAY);
        fi[d] = (fi[d] || 0) + Math.round(r*1e8); ff[d] = (ff[d] || 0) + r; cnt[d] = (cnt[d] || 0) + 1; if(f0 == null || t < f0) f0 = t; if(f1 == null || t > f1) f1 = t; });
      P[s] = { k0:x.k0, c:x.c, fi:fi, ff:ff, cnt:cnt, f0:f0, f1:f1 }; });
    return P; }
  function close(p, d){ if(!p) return null; var i = d - p.k0, v = i >= 0 && i < p.c.length ? p.c[i] : null; return v > 0 ? v : null; }
  function fundedThrough(p, d){ return p.f1 != null && p.f1 >= d*DAY + 16*3600e3; }
  function rankable(p, a){ if(close(p, a) == null || p.f0 == null || p.f0 > (a - 6)*DAY) return false; var n = 0; for(var d=a-6; d<=a; d++) if(p.cnt[d]) n++; return n >= 6; }
  function weekly(p, a){ var s = 0; for(var d=a-L+1; d<=a; d++) s += p.fi[d] || 0; return s/1e8*7/L; }   // funding a long paid over 30 days, scaled to a week
  function ready(P, U, a, now){ if(now >= (a + 4)*DAY) return true;
    return U.every(function(s){ var p = P[s], last = p.k0 + p.c.length - 1; if(p.k0 > a || last < a - 3) return true; return close(p, a) != null && fundedThrough(p, a); }); }
  function choose(P, U, a, held, k, keep){ k = k || K; keep = keep || KEEP; var E = U.filter(function(s){ return rankable(P[s], a); }), n = E.length, v = {}, rk = {};
    E.forEach(function(s){ v[s] = weekly(P[s], a); });
    var ord = E.slice().sort(function(x, y){ return (v[y] - v[x]) || (x < y ? -1 : 1); }), i = 0;
    while(i < n){ var j = i; while(j + 1 < n && v[ord[j + 1]] === v[ord[i]]) j++; for(var q=i; q<=j; q++) rk[ord[q]] = (i + j + 2)/2; i = j + 1; }
    var want = {}; E.forEach(function(s){ if(rk[s] <= k && v[s] > HURDLE) want[s] = 1; });
    Object.keys(held || {}).forEach(function(s){ if(v[s] != null && rk[s] <= keep && v[s] > 0) want[s] = 1; });
    // more than 5: keep the highest; an exact tie (common at the base rate of 0.01% every 8 hours) keeps a coin already held, then goes by name
    var hd = held || {}, w = Object.keys(want).sort(function(x, y){ return (v[y] - v[x]) || ((hd[y] ? 1 : 0) - (hd[x] ? 1 : 0)) || (x < y ? -1 : 1); }).slice(0, k), out = {}; w.forEach(function(s){ out[s] = 1; });
    return { n:n, hold:out, v:v }; }
  function weekResult(P, a, hold, prev, k){ k = k || K; var b = a + 7, inc = 0;
    Object.keys(hold).forEach(function(s){ for(var d=a+1; d<=b; d++) inc += (1/k)*(P[s].ff[d] || 0); });   // the short perpetual receives positive funding
    var ch = 0; Object.keys(hold).forEach(function(s){ if(!prev[s]) ch++; }); Object.keys(prev).forEach(function(s){ if(!hold[s]) ch++; });
    var cost = ch*(1/k)*(SPOT + PERP); return { r:inc - cost, inc:inc, cost:cost }; }
  function nwT(x, lag){ lag = lag || 2; x = x.filter(function(v){ return isFinite(v); }); var n = x.length; if(n < 8) return null;
    var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g0 = e.reduce(function(a, v){ return a + v*v; }, 0)/n, lrv = g0;
    for(var k=1; k<=lag; k++){ var s = 0; for(var i=k; i<n; i++) s += e[i]*e[i-k]; lrv += 2*(1 - k/(lag + 1))*s/(n - k); }
    return lrv > 0 ? m/Math.sqrt(lrv/n) : null; }
  function stats(list){ var n = list.length; if(!n) return { n:0 }; var x = list.map(function(q){ return q.r; }), m = x.reduce(function(a, b){ return a + b; }, 0)/n, eq = 1, pk = 1, dd = 0;
    x.forEach(function(r){ eq *= 1 + r; if(eq > pk) pk = eq; if(eq/pk - 1 < dd) dd = eq/pk - 1; });
    return { n:n, mean:m, ann:m*52, t:nwT(x), cum:eq - 1, worstFall:dd, posWeeks:x.filter(function(r){ return r > 0; }).length/n, income:list.reduce(function(a, q){ return a + q.inc; }, 0)/n*52, costs:-list.reduce(function(a, q){ return a + q.cost; }, 0)/n*52 }; }
  function compute(data, opt){ opt = opt || {}; var kk = opt.k || K, kp = opt.keep || KEEP, now = opt.now || Date.now(), P = prep(data), U = Object.keys(P).sort(), rec = opt.rec || {};
    if(U.length < MIN_RANKABLE) return { at:now, error:'needs stored history and funding for at least ' + MIN_RANKABLE + ' coins (has ' + U.length + ')' };
    var k0 = Infinity, k1 = -Infinity; U.forEach(function(s){ var p = P[s]; if(p.k0 < k0) k0 = p.k0; if(p.k0 + p.c.length - 1 > k1) k1 = p.k0 + p.c.length - 1; });
    var a = k0 + 35; while(new Date(a*DAY).getUTCDay() !== 0) a++;
    var weeks = [], held = {}, started = false, cur = null, newRec = {}, mism = 0;
    for(; a <= k1; a += 7){
      if(!ready(P, U, a, now)) break;
      var Ch = choose(P, U, a, held, kk, kp), hold = Ch.hold;
      if(!started){ if(Ch.n < MIN_RANKABLE) continue; started = true; }
      if(a >= FREEZE_DAY){ var R0 = rec[a]; if(R0 && R0.hold){ if(Object.keys(R0.hold).sort().join() !== Object.keys(hold).sort().join()) mism++; hold = R0.hold; } else newRec[a] = { hold:hold, at:now, n:Ch.n }; }
      var b = a + 7, done = now >= (b + 1)*DAY && (Object.keys(hold).every(function(s){ return fundedThrough(P[s], b); }) || now >= (b + 4)*DAY);
      if(!done){ cur = { a:a, hold:hold, v:Ch.v, n:Ch.n }; break; }
      var R = weekResult(P, a, hold, held, kk); weeks.push({ a:a, end:b, r:R.r, inc:R.inc, cost:R.cost, held:Object.keys(hold).length, fwd:a >= FREEZE_DAY }); held = hold; }
    if(!cur && started && a <= k1 && ready(P, U, a, now)){ var CN = choose(P, U, a, held, kk, kp); cur = { a:a, hold:CN.hold, v:CN.v, n:CN.n }; }
    var act = function(q){ return q.held > 0 || q.cost > 0; };
    return { k:kk, at:now, coins:U.length, lastDay:k1, weeks:weeks, current:cur, newRec:newRec, recMismatch:mism,
      before:stats(weeks.filter(function(q){ return !q.fwd; })), beforeYears:(function(){ var o = {}; weeks.filter(function(q){ return !q.fwd; }).forEach(function(q){ var y = new Date(q.end*DAY).getUTCFullYear(); o[y] = (o[y] || 0) + q.r; }); return o; })(),
      forward:stats(weeks.filter(function(q){ return q.fwd && act(q); })), forwardAll:stats(weeks.filter(function(q){ return q.fwd; })) }; }
  // ── forward judgement, written 18 Oct 2026 before any forward week (weeks that held nothing are not counted) ──
  function verdict(F, retired){ if(retired) return { code:'RETIRED', text:'Retired on ' + retired.at.slice(0, 10) + ': ' + retired.why + '. A retired rule never returns.' };
    if(!F || !F.n) return { code:'WAIT', text:'No forward week with positions has finished yet. The first possible one runs from the close of Sunday 18 Oct 2026 to the close of Sunday 25 Oct.' };
    if(F.worstFall <= FWD_STOP) return { code:'RETIRE', why:'fell ' + Math.round(-F.worstFall*100) + '% from its forward peak (limit 10%; its worst on unseen coins was 2.3%)' };
    if(F.n < FWD_MIN) return { code:'COLLECT', text:F.n + ' of ' + FWD_MIN + ' forward weeks with positions. Too early to judge.' };
    if(F.mean <= 0) return { code:'RETIRE', why:'its ' + F.n + ' forward weeks with positions average zero or less after costs' };
    if(F.t != null && F.t >= FWD_BAR) return { code:'CONFIRMED', text:'Confirmed on ' + F.n + ' forward weeks (z ' + F.t.toFixed(2) + ' ≥ ' + FWD_BAR + '). Still paper only.' };
    if(F.n < FWD_FULL) return { code:'HOLDING', text:'Positive on ' + F.n + ' forward weeks but not yet clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + '). Judged again at ' + FWD_FULL + ' weeks.' };
    return { code:'UNPROVEN', text:'Positive after ' + F.n + ' forward weeks but not clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + '). Stays on paper.' }; }
  function compact(res){ if(!res || res.error) return res;
    return { k:res.k, at:res.at, coins:res.coins, lastDay:res.lastDay, before:res.before, beforeYears:res.beforeYears, forward:res.forward, forwardAll:res.forwardAll, recMismatch:res.recMismatch,
      weeks:res.weeks.map(function(q){ return [q.end, +q.r.toFixed(7), +q.inc.toFixed(7), +q.cost.toFixed(7), q.held, q.fwd ? 1 : 0]; }),
      current:res.current ? { a:res.current.a, n:res.current.n, hold:res.current.hold, v:res.current.v } : null }; }
  async function runNow(){ if(run.busy) return { skip:true, text:'already running' }; run.busy = true; run.msg = 'Reading stored closes and funding'; render();
    try{ var X = window.OMEGA_CARRYXS; if(!X || !X.getData) throw new Error('carry module (data loader) not ready');
      var data = await X.getData(30*60e3), res = compute(data, { now:Date.now(), rec:st.rec });
      if(res.error){ st.res = { at:res.at, error:res.error }; lsSet(KEY, st); return { skip:true, text:res.error, retryIn:6*3600e3 }; }
      Object.keys(res.newRec).forEach(function(a){ st.rec[a] = res.newRec[a]; });
      var V = verdict(res.forward, st.retired);
      if(V.code === 'RETIRE' && !st.retired){ st.retired = { at:new Date().toISOString(), why:V.why, weeks:res.forward.n }; V = verdict(res.forward, st.retired); }
      st.res = compact(res); st.verdict = V;
      var r10 = compute(data, { now:Date.now(), rec:st.rec10, k:10, keep:20 });   // v6.5.62: the 10-coin version (R3), which passed the final test on 90 new coins
      if(!r10.error){ Object.keys(r10.newRec).forEach(function(a){ st.rec10[a] = r10.newRec[a]; }); var V10 = verdict(r10.forward, st.retired10);
        if(V10.code === 'RETIRE' && !st.retired10){ st.retired10 = { at:new Date().toISOString(), why:V10.why, weeks:r10.forward.n }; V10 = verdict(r10.forward, st.retired10); }
        st.res10 = compact(r10); st.verdict10 = V10; }
      lsSet(KEY, st); note(V);
      return { text:'Funding harvest: ' + (res.forward.n ? res.forward.n + ' forward weeks with positions, ' + pct(res.forward.cum) : 'no forward week yet') + '; holding ' + (res.current ? Object.keys(res.current.hold).length : 0) + ' coins.' }; }
    catch(e){ return { error:(e && e.message) || String(e) }; }
    finally{ run.busy = false; run.msg = ''; render(); } }
  function note(V){ if(st.noted === 'r8:' + V.code) return;
    safe(function(){ var B = window.OMEGA_BRAIN; if(!B || !B.feedObservation) return; if(B.retract) B.retract(['Funding harvest (harvest-30d)']);
      B.feedObservation({ pinned:true, strat:'omega', tf:'1w', symbol:'*', text:'Funding harvest (harvest-30d, and its 10-coin version from round 8): the one idea that passed untouched tests, twice (5 coins on 51 fresh coins: +12.0% a year, z 4.14; 10 coins on 90 new coins: +8.8% a year, z 3.38, worst fall −4.4%). Market-neutral: hold the coin and short its perpetual in the 5 coins whose longs paid the most funding over 30 days (above 0.1% a week); collects funding, not price. Paid mostly in boom years (2021 +49%), about 0% in 2025–26. Frozen 18 Oct 2026; paper only. Forward: ' + (V.text || V.why || V.code) }); });
    st.noted = 'r8:' + V.code; lsSet(KEY, st); }
  // ── the card (top of OMEGA Strategy) ──
  function render(){ var host = el('harvestCard'); if(!host){ var pg = el('page-ostrat'); if(!pg) return; host = document.createElement('div'); host.id = 'harvestCard'; pg.insertBefore(host, pg.firstChild); }
    var r = st.res, V = st.verdict || verdict(null, st.retired), eq = safe(function(){ return window.OMEGA_AUTOPILOT.cfg().startEquity; }) || 100, Z = RESEARCH;
    var lab = { WAIT:['Paper · passed its untouched test · forward record starts at Sunday 18 Oct’s close','bull'], COLLECT:['Paper · collecting forward weeks','warn'], HOLDING:['Paper · positive, not yet proven forward','warn'], CONFIRMED:['Paper · confirmed forward','bull'], UNPROVEN:['Paper · unproven forward','warn'], RETIRED:['Retired','bear'] }[V.code] || ['Paper','warn'];
    var h = '<div class="card" style="margin-bottom:14px;border-color:var(--bull);"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;"><div><h2 style="color:var(--gold);margin-bottom:4px;">Funding harvest \u2014 the one idea that passed untouched tests, twice</h2><span class="bt-lab ' + lab[1] + '">' + esc(lab[0]) + '</span></div>' +
      '<button class="btn-outline" type="button" id="harvestRun"' + (run.busy ? ' disabled' : '') + '>' + (run.busy ? esc(run.msg || 'Working') : 'Update now') + '</button></div>' +
      '<p class="hint" style="margin-top:8px;">Not a bet on direction. Each Sunday close it <b>holds a coin and shorts the same coin’s perpetual</b>, so price moves cancel. The short then collects the funding that leveraged buyers pay. It picks the 5 coins (of the 25) whose buyers paid the most over 30 days, if above 0.1% a week, 1/5 of the account per pair. When funding is low it holds nothing. Frozen ' + esc(Z.frozenAt) + '. <b>Paper only.</b></p>' +
      '<p class="hint" style="color:var(--bull);"><b>Untouched test:</b> on ' + esc(Z.fresh.data) + ': ' + pct(Z.fresh.annPct/100) + ' a year, z ' + Z.fresh.t.toFixed(2) + ' against a bar of ' + Z.fresh.bar.toFixed(2) + ', ' + pct(Z.fresh.costs2xPct/100) + ' with costs doubled, worst fall ' + pct(Z.fresh.worstFallPct/100) + '. ' + esc(Z.others) + '</p>' +
      '<div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th></th>' + Z.fresh.years.map(function(y){ return '<th>' + esc(y[0]) + '</th>'; }).join('') + '</tr></thead><tbody><tr><td>Fresh coins</td>' + Z.fresh.years.map(function(y){ return '<td class="mono">' + pct(y[1]/100) + '</td>'; }).join('') + '</tr></tbody></table></div>' +
      '<p class="hint"><b>Read it the right way:</b> it pays when leveraged buyers are paying a lot, and little otherwise. 2025 made ' + pct(0.010) + ' and 2026 so far ' + pct(-0.016) + '.</p>';
    if(!r) h += '<p class="hint">' + (run.busy ? esc(run.msg) : 'Not worked out yet. It reads the stored daily closes and funding; the Autopilot runs it twice a day and after each Sunday close.') + '</p>';
    else if(r.error) h += '<p class="hint">' + esc(r.error) + '.</p>';
    else { var c = r.current;
      if(c){ var ks = Object.keys(c.hold).sort(function(x, y){ return c.v[y] - c.v[x]; }), top = Object.keys(c.v).sort(function(x, y){ return c.v[y] - c.v[x]; }).slice(0, 8);
        h += '<h3 style="font-size:14px;margin:12px 0 4px;">This week: decided at the close of ' + esc(dayName(c.a)) + (c.a >= FREEZE_DAY ? '' : ' <span class="dim">(before the freeze, not in the forward record)</span>') + '</h3>' +
          (ks.length ? '<p class="hint" style="margin-top:0;">Holding ' + ks.length + ' pair' + (ks.length === 1 ? '' : 's') + ', each ' + (eq/K).toFixed(2) + ' USDT of the coin plus a ' + (eq/K).toFixed(2) + ' USDT short perpetual: ' + ks.map(function(s){ return '<b>' + esc(s.replace(/USDT$/, '')) + '</b> (' + pct(c.v[s]*52, 1) + ' a year)'; }).join(', ') + '.</p>'
                     : '<p class="hint" style="margin-top:0;"><b>Holding nothing:</b> no coin’s buyers paid more than 0.1% a week (about 5.2% a year) over the last 30 days. This is the rule sitting out a low-funding market, as designed.</p>') +
          '<p class="hint">Highest 30-day funding now (as a yearly rate): ' + top.map(function(s){ return esc(s.replace(/USDT$/, '')) + ' ' + pct(c.v[s]*52, 1); }).join(' · ') + '.</p>'; }
      var F = r.forward || {};
      h += '<h3 style="font-size:14px;margin:12px 0 4px;">Forward record</h3><p class="hint" style="margin-top:0;"><b>' + esc(V.text || V.why || '') + '</b>' + (F.n ? ' ' + F.n + ' week' + (F.n === 1 ? '' : 's') + ' with positions: ' + pct(F.cum, 2) + ' in all (' + (F.cum >= 0 ? '+' : '−') + Math.abs(F.cum*eq).toFixed(2) + ' USDT on ' + eq + '), worst fall ' + pct(F.worstFall, 2) + '.' : '') + (r.forwardAll && r.forwardAll.n > (F.n || 0) ? ' Weeks that held nothing: ' + (r.forwardAll.n - (F.n || 0)) + '.' : '') + '</p>';
      var B = r.before || {}, yrs = r.beforeYears || {};
      h += '<p class="hint">On your stored history before the freeze (' + B.n + ' weeks to ' + dayStr(r.lastDay) + ', worked out by this app): ' + pct(B.cum, 1) + ' in all, worst fall ' + pct(B.worstFall, 2) + '; by year ' + Object.keys(yrs).map(function(y){ return y + ' ' + pct(yrs[y], 1); }).join(', ') + '.</p>'; }
    // v6.5.62: the 10-coin version (round 8, R3)
    var W = Z.wide, r10 = st.res10, V10 = st.verdict10 || verdict(null, st.retired10);
    h += '<h3 style="font-size:14px;margin:14px 0 4px;border-top:1px solid var(--border);padding-top:10px;">The 10-coin version: passed the final test on 90 new coins</h3>' +
      '<p class="hint" style="margin-top:0;color:var(--bull);">Same idea with 10 pairs instead of 5 (1/10 of the account each; a held coin stays in the top 20). On ' + esc(W.fresh2.data) + ': ' + pct(W.fresh2.annPct/100) + ' a year, z ' + W.fresh2.t.toFixed(2) + ' against ' + W.fresh2.bar.toFixed(2) + ', ' + pct(W.fresh2.costs2xPct/100) + ' with costs doubled, worst fall ' + pct(W.fresh2.worstFallPct/100) + '. By year ' + W.fresh2.years.map(function(y){ return esc(y[0]) + ' ' + pct(y[1]/100); }).join(', ') + '. ' + esc(W.others) + '</p>';
    if(r10 && !r10.error){ var c10 = r10.current, F10 = r10.forward || {}, B10 = r10.before || {};
      if(c10){ var k10 = Object.keys(c10.hold).sort(function(x, y){ return c10.v[y] - c10.v[x]; });
        h += '<p class="hint">' + (k10.length ? 'Holding ' + k10.length + ' pair' + (k10.length === 1 ? '' : 's') + ' (' + (eq/10).toFixed(2) + ' USDT each side): ' + k10.map(function(s){ return esc(s.replace(/USDT$/, '')); }).join(', ') : 'Holding nothing: no coin pays above 0.1% a week') + ' \u2014 decided at the close of ' + esc(dayName(c10.a)) + '.</p>'; }
      h += '<p class="hint"><b>Forward:</b> ' + esc(V10.text || V10.why || '') + (F10.n ? ' ' + F10.n + ' weeks with positions: ' + pct(F10.cum, 2) + ', worst fall ' + pct(F10.worstFall, 2) + '.' : '') + ' Before the freeze on your stored history: ' + pct(B10.cum, 1) + ' over ' + B10.n + ' weeks, worst fall ' + pct(B10.worstFall, 2) + '.</p>'; }
    h += '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;"><b>What could still be wrong, and how it is judged</b></summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;">' + Z.caveats.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
      '<p class="hint">Where it was shaped (' + esc(Z.design.data) + '): ' + pct(Z.design.annPct/100) + ' a year, worst fall ' + pct(Z.design.worstFallPct/100) + '; by year ' + Z.design.years.map(function(y){ return esc(y[0]) + ' ' + pct(y[1]/100); }).join(', ') + '.</p>' +
      '<p class="hint"><b>Forward judgement, fixed 18 Oct 2026 before any forward week</b> (only weeks with positions count): nothing is judged before ' + FWD_MIN + ' such weeks. At ' + FWD_MIN + ' or more it is <b>retired</b> if they average zero or less after costs, and <b>confirmed</b> at z ≥ ' + FWD_BAR + '. At any time it is retired if it falls ' + Math.round(-FWD_STOP*100) + '% from its forward peak. A retired rule never returns.</p></details></div>';
    host.innerHTML = h; var bt = el('harvestRun'); if(bt) bt.onclick = function(){ var O = window.OMEGA_OPERATOR; if(O && O.runNow) safe(function(){ O.runNow('harvest'); }); else runNow(); }; }
  function report(){ return { rule:'harvest-30d', text:'Each Sunday close: among the 25 coins, hold spot + short perpetual (1/5 of the account per pair) in the 5 with the highest 30-day funding (scaled to a week) above 0.1% a week; a held coin stays while in the top 10 with positive funding; costs 0.11% spot + 0.06% perpetual a side; P&L = funding received - costs; basis ignored. Paper only.',
    research:RESEARCH, judgement:{ minWeeks:FWD_MIN, fullWeeks:FWD_FULL, bar:FWD_BAR, stopFall:FWD_STOP }, verdict:st.verdict || null, retired:st.retired || null, result:st.res || null, recordedBaskets:st.rec,
    wide:{ rule:'harvest-wide (R3): the same with 10 pairs (1/10 each), held coins stay in the top 20', research:RESEARCH.wide, verdict:st.verdict10 || null, retired:st.retired10 || null, result:st.res10 || null, recordedBaskets:st.rec10 } }; }
  function lastSunday(){ var today = Math.floor(Date.now()/DAY), dow = new Date(today*DAY).getUTCDay(); return dow === 0 ? today - 7 : today - dow; }
  function every(){ var r = st.res; if(r && !r.error && r.current && r.current.a < lastSunday()) return 30*60e3; if(r && !r.error && !r.current) return 2*3600e3; return 12*3600e3; }
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'harvest'; })) return true;
    J.push({ id:'harvest', lane:'heavy', prio:2, label:'Funding harvest (the rule that passed its untouched test)', what:'Twice a day and soon after each Sunday close: which coins the frozen funding-harvest rule holds, and its forward record, from the stored daily closes and funding. Paper only.', every:every, run:runNow }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var nav0 = window.navigate; if(typeof nav0 === 'function') window.navigate = function(p){ var rr = nav0.apply(this, arguments); if(p === 'ostrat') setTimeout(render, 60); return rr; };
  setTimeout(function(){ try{ render(); }catch(e){} }, 1600);
  window.OMEGA_HARVEST = { compute:compute, prep:prep, choose:choose, verdict:verdict, stats:stats, runNow:runNow, render:render, report:report, state:function(){ return st; }, RESEARCH:RESEARCH, FREEZE_DAY:FREEZE_DAY };
})();
</script>
