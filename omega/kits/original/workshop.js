<script>/* ═══ STRATEGY WORKSHOP (v6.5.49) — OMEGA proposes new rules from what it observes, and tests them honestly ═══
   Each round has three steps that never mix:
   1. OBSERVE, on the design window only (history before the round's design cut). Every closed hourly bar of every
      studied market is placed in fixed bins, written before any result, of 8 measurements: RSI, distance from the
      20 EMA, EMA20 minus EMA50, place in the 50-bar range, 10-bar change, volatility percentile, relative volume and
      taker flow (the last two crypto only). For every pair of measurements and every pair of bins (28 × 25 = 700
      cells), what followed over the next 24 hours (in ATR, after costs) is added up, long and short.
   2. PROPOSE. The 10 cells with the strongest result (weeks as the sample; at least 200 bars over 30 weeks; at most
      two per pair of measurements) become rules: written down with the date, never re-tuned.
   3. TEST ONCE on the validation window — data after the design cut that the observation never touched. Entered at
      the close of the bar, 2 ATR stop, out after 24 hours, one trade at a time per rule per market, costs as the
      Research Lab charges them. A rule passes with 50+ trades over 15+ weeks, an average above zero also with costs
      doubled, and z (weeks as the sample) at or above the one-sided Bonferroni bar over EVERY rule the workshop has
      ever proposed (so proposing more raises the bar for all).
   Passed rules are then judged only on trades after the round (forward), every 7 days: 50+ trades over 8+ weeks and
   z at or above the bar for every rule that reached the forward stage. After qualifying, the demotion rule applies.
   A new round needs 90 days of data no earlier round has used; its design window ends where the last one's test ended.
   Paper only: nothing here places an order, blocks a trade or changes CREED. */
(function(){
  'use strict';
  var KEY = 'omega_workshop_v1', ALPHA = 0.05, K_ROUND = 10, MIN_CELL_N = 200, MIN_CELL_W = 30, ROUND_GAP = 90*86400e3, FWD_EVERY = 7*86400e3, WEEK = 7*86400e3;
  var FEATS = [
    { k:'rsi',   name:'RSI(14)',                       cuts:[30, 45, 55, 70],          get:function(F, i){ return F.rsi[i]; } },
    { k:'ext',   name:'distance from the 20 EMA (ATR)', cuts:[-1.5, -0.5, 0.5, 1.5],   get:function(F, i){ return F.atr[i] > 0 ? (F.c[i] - F.e20[i])/F.atr[i] : null; } },
    { k:'trend', name:'EMA20 minus EMA50 (ATR)',        cuts:[-1, -0.3, 0.3, 1],       get:function(F, i){ return F.atr[i] > 0 ? (F.e20[i] - F.e50[i])/F.atr[i] : null; } },
    { k:'rpos',  name:'place in the 50-bar range',      cuts:[0.2, 0.4, 0.6, 0.8],     get:function(F, i){ return F.rpos[i]; } },
    { k:'roc',   name:'10-bar change (ATR)',            cuts:[-2, -0.7, 0.7, 2],       get:function(F, i){ return F.roc[i]; } },
    { k:'volp',  name:'volatility percentile',          cuts:[0.2, 0.4, 0.6, 0.8],     get:function(F, i){ return F.volPct[i]; } },
    { k:'rvol',  name:'relative volume',                cuts:[0.6, 0.9, 1.2, 1.8],     get:function(F, i){ return F.relVol[i]; } },
    { k:'flow',  name:'taker flow (−1…+1)',             cuts:[-0.2, -0.07, 0.07, 0.2], get:function(F, i){ return F.flow[i]; } } ];
  var PAIRS = []; for(var a=0;a<FEATS.length;a++) for(var b=a+1;b<FEATS.length;b++) PAIRS.push([a, b]);
  var NC = PAIRS.length*25, WB = 8;   // 700 cells; weeks kept as bits (8 × 32 = 256 weeks)
  function el(id){ return document.getElementById(id); }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function L(){ return window.OMEGA_LAB; } function H(){ return window.OMEGA_HISTORY; }
  function Y(){ return window.OMEGA_CALM && window.OMEGA_CALM.y ? window.OMEGA_CALM.y() : null; }
  function sgn(v){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '') + v.toFixed(2) + 'R'; }
  function day(t){ return t ? new Date(t).toISOString().slice(0, 10) : '—'; }
  function ncdf(z){ var N = safe(function(){ return L().ncdf; }); return N ? N(z) : 0.5; }
  function zFor(p){ var lo = 0, hi = 9; for(var k=0;k<60;k++){ var m = (lo + hi)/2; if(1 - ncdf(m) > p) lo = m; else hi = m; } return (lo + hi)/2; }
  function feed(text){ safe(function(){ var B = window.OMEGA_BRAIN; if(B && B.feedObservation) B.feedObservation({ strat:'omega', tf:'1h', symbol:'*', text:text }); }); }
  function load(){ var s = null; try{ s = JSON.parse(localStorage.getItem(KEY) || 'null'); }catch(e){} s = s && typeof s === 'object' ? s : {}; if(!Array.isArray(s.rules)) s.rules = []; if(!Array.isArray(s.log)) s.log = []; s.proposed = s.proposed | 0; return s; }
  var st = load();
  function save(){ if(st.log.length > 40) st.log.length = 40; try{ localStorage.setItem(KEY, JSON.stringify(st)); }catch(e){} }
  function log(t){ st.log.unshift({ at:Date.now(), text:t }); }
  function binOf(v, cuts){ if(v == null || !isFinite(v)) return -1; var q = 0; while(q < 4 && v >= cuts[q]) q++; return q; }
  function binText(f, q){ var c = f.cuts; return q === 0 ? 'below ' + c[0] : q === 4 ? c[3] + ' or more' : c[q-1] + ' to ' + c[q]; }
  function ruleText(r){ return FEATS[r.fa].name + ' ' + binText(FEATS[r.fa], r.qa) + ', and ' + FEATS[r.fb].name + ' ' + binText(FEATS[r.fb], r.qb) + ' → ' + r.dir + ' (2 ATR stop, out after 24 h)'; }
  function cstat(list){ var n = list.length; if(!n) return { n:0, mean:null, z:null, weeks:0 }; var s = 0; list.forEach(function(q){ s += q.r; }); var m = s/n, wk = {};
    list.forEach(function(q){ var w = Math.floor(q.t/WEEK); wk[w] = (wk[w] || 0) + (q.r - m); }); var W = Object.keys(wk).length, v = 0; Object.keys(wk).forEach(function(w){ v += wk[w]*wk[w]; });
    return { n:n, mean:m, z: W >= 2 && v > 0 ? s/Math.sqrt(v*W/(W-1)) : null, weeks:W }; }
  function markets(){ var R = safe(function(){ return L().results(); }); return R && R.markets ? R.markets.filter(function(m){ return !m.skipped && m.sym; }).map(function(m){ return { sym:m.sym, from:m.from, to:m.to }; }) : []; }
  // one market's closed hourly bars and features, with the same cleaning and costs the Research Lab uses
  async function prep(sym){ var h = H(), lab = L(); var s = await h.load(sym, { stitch:true }), sm = h.summary(sym) || {};
    if(!s || !s.n) return null; if(lab.cleanSeries){ var cs = await lab.cleanSeries(sym, s, sm); if(!cs || (cs.dq && cs.dq.score < (lab.DQ_MIN || 60))) return null; s = cs.s; }
    await Y(); var h1 = (await h.resampleA(s, 60)).filter(function(r){ return !r.partial; }); if(h1.length < 500) return null;
    await Y(); var F = await lab.featureSeriesA(h1); return { s:s, src:sm.src || '', h1:h1, F:F }; }
  // ── a round ──
  function newRound(){ var M = markets(); if(M.length < 5) return false; var from = Math.min.apply(null, M.map(function(m){ return m.from; })), to = Math.max.apply(null, M.map(function(m){ return m.to; }));
    var last = st.rounds && st.rounds.length ? st.rounds[st.rounds.length-1] : null, cut = last ? last.validEnd : Math.round(from + 0.6*(to - from));
    if(last && to - last.validEnd < ROUND_GAP) return false;
    var R = { n:(last ? last.n : 0) + 1, at:Date.now(), designCut:cut, validEnd:to, phase:'observe', markets:M.map(function(m){ return m.sym; }), done:{},
      cells:{ n:new Array(NC).fill(0), s:new Array(NC).fill(0), sc:new Array(NC).fill(0), ss:new Array(NC).fill(0), wk:new Array(NC*WB).fill(0) }, rules:[], val:{} };
    st.rounds = (st.rounds || []).concat([R]); st.cur = R.n; log('Round ' + R.n + ' started: observes ' + day(from) + ' to ' + day(cut) + ' on ' + M.length + ' markets; tests on ' + day(cut) + ' to ' + day(to) + '.'); save(); return true; }
  function cur(){ return st.rounds && st.rounds.length ? st.rounds[st.rounds.length-1] : null; }
  async function observe(R, sym){ var P = await prep(sym); if(!P) return sym + ': skipped (no clean hourly history)';
    var F = P.F, h1 = P.h1, C = R.cells, lab = L(), w0 = Math.floor(h1[0].time*1000/WEEK), used = 0, bins = new Array(FEATS.length);
    for(var i=60; i<h1.length-25; i++){ if((i & 1023) === 0) await Y();
      if((h1[i+24].time + 3600)*1000 > R.designCut) break;                                 // outcome must end before the cut
      var atr = F.atr[i]; if(!(atr > 0)) continue; var y = (F.c[i+24] - F.c[i])/atr, cc = lab.costIn(sym, P.src, F.c[i])/atr; if(!isFinite(y) || !isFinite(cc)) continue;
      for(var f=0; f<FEATS.length; f++) bins[f] = binOf(FEATS[f].get(F, i), FEATS[f].cuts);
      var wkI = Math.floor(h1[i].time*1000/WEEK) - Math.floor(R.designCut/WEEK) + 255; if(wkI < 0 || wkI > 255) wkI = -1;
      for(var p=0; p<PAIRS.length; p++){ var ba = bins[PAIRS[p][0]], bb = bins[PAIRS[p][1]]; if(ba < 0 || bb < 0) continue; var c = p*25 + ba*5 + bb;
        C.n[c]++; C.s[c] += y; C.sc[c] += cc; C.ss[c] += y*y; if(wkI >= 0) C.wk[c*WB + (wkI >> 5)] |= (1 << (wkI & 31)); }
      used++; }
    return sym + ': ' + used + ' hourly bars observed'; }
  function popc(x){ x = x - ((x >>> 1) & 0x55555555); x = (x & 0x33333333) + ((x >>> 2) & 0x33333333); return (((x + (x >>> 4)) & 0x0F0F0F0F) * 0x01010101) >>> 24; }
  function propose(R){ var C = R.cells, cand = [];
    for(var c=0; c<NC; c++){ var n = C.n[c]; if(n < MIN_CELL_N) continue; var W = 0; for(var q=0;q<WB;q++) W += popc(C.wk[c*WB+q] >>> 0); if(W < MIN_CELL_W) continue;
      var my = C.s[c]/n, mc = C.sc[c]/n, sd = Math.sqrt(Math.max(1e-12, C.ss[c]/n - my*my)), L0 = my - mc, S0 = -my - mc, dir = L0 >= S0 ? 'long' : 'short', m = Math.max(L0, S0);
      if(!(m > 0)) continue; var p = Math.floor(c/25), r = c % 25; cand.push({ cell:c, pair:p, fa:PAIRS[p][0], fb:PAIRS[p][1], qa:Math.floor(r/5), qb:r % 5, dir:dir, n:n, weeks:W, mean:m, t:m/(sd/Math.sqrt(W)) }); }
    cand.sort(function(a, b){ return b.t - a.t; }); var per = {}, pick = [];
    cand.forEach(function(x){ if(pick.length >= K_ROUND || (per[x.pair] || 0) >= 2) return; per[x.pair] = (per[x.pair] || 0) + 1; pick.push(x); });
    pick.forEach(function(x, k){ x.id = 'W' + R.n + '-' + (k + 1); x.round = R.n; x.at = Date.now(); x.status = 'PROPOSED'; x.design = { n:x.n, weeks:x.weeks, meanATR:Math.round(x.mean*1000)/1000, t:Math.round(x.t*100)/100 }; delete x.n; delete x.weeks; delete x.mean; delete x.t; st.rules.push(x); });
    st.proposed += pick.length; R.rules = pick.map(function(x){ return x.id; }); R.cells = null; R.phase = 'validate'; R.done = {};
    log('Round ' + R.n + ' proposed ' + pick.length + ' rule(s) from ' + cand.length + ' candidate cells: ' + pick.map(function(x){ return x.id; }).join(', ') + '. Each is tested once on data the observation never touched.');
    feed('Strategy Workshop round ' + R.n + ': ' + pick.length + ' new rule(s) proposed from observation (' + pick.map(ruleText).slice(0, 3).join('; ') + (pick.length > 3 ? '; …' : '') + '). Proposals, not results.'); }
  function rulesById(ids){ return st.rules.filter(function(r){ return ids.indexOf(r.id) > -1; }); }
  function tradesFor(P, sym, rule, from, to){ var F = P.F, h1 = P.h1, lab = L(), out = [], busy = 0;
    for(var i=60; i<h1.length-1; i++){ var t = (h1[i].time + 3600)*1000; if(t < from) continue; if(t + 24*3600e3 > to) break;
      if(binOf(FEATS[rule.fa].get(F, i), FEATS[rule.fa].cuts) !== rule.qa || binOf(FEATS[rule.fb].get(F, i), FEATS[rule.fb].cuts) !== rule.qb) continue;
      var em = t/60000; if(em < busy) continue; var atr = F.atr[i]; if(!(atr > 0)) continue;
      var cost = lab.costIn(sym, P.src, F.c[i]), res = lab.walk(P.s, em, rule.dir, F.c[i], atr, cost, 2, 50, 24*60); if(!res) continue;
      busy = res.exitMin; out.push({ t:t, r:Math.round(res.r*1000)/1000, c:Math.round(cost/(2*atr)*1000)/1000 }); }
    return out; }
  async function validate(R, sym){ var P = await prep(sym); if(!P) return sym + ': skipped (no clean hourly history)'; var n = 0;
    for(const rule of rulesById(R.rules)){ await Y(); var tr = tradesFor(P, sym, rule, R.designCut, R.validEnd); var si = R.markets.indexOf(sym); (R.val[rule.id] = R.val[rule.id] || []).push.apply(R.val[rule.id], tr.map(function(q){ return [q.t, q.r, q.c, si]; })); n += tr.length; }
    return sym + ': ' + n + ' test trades'; }
  function judgeValidation(R){ var bar = zFor(ALPHA/Math.max(1, st.proposed)), passed = [];
    rulesById(R.rules).forEach(function(rule){ var tr = (R.val[rule.id] || []).map(function(q){ return { t:q[0], r:q[1], c:q[2] }; }), s = cstat(tr), c2 = tr.length ? tr.reduce(function(a, q){ return a + q.r - q.c; }, 0)/tr.length : null;
      rule.test = { n:s.n, mean:s.mean, z:s.z, weeks:s.weeks, costs2x:c2, bar:bar };
      var why = s.n < 50 || s.weeks < 15 ? 'under 50 test trades or 15 weeks' : !(s.mean > 0) ? 'lost on the test data' : !(c2 > 0) ? 'loses with costs doubled' : !(s.z >= bar) ? 'positive, not beyond luck (z ' + (s.z == null ? '—' : s.z.toFixed(2)) + ' < ' + bar.toFixed(2) + ' for ' + st.proposed + ' proposals)' : null;
      if(why){ rule.status = 'FAILED THE TEST'; rule.why = why; } else { rule.status = 'PASSED — JUDGED FORWARD'; rule.why = null; rule.fwdFrom = R.validEnd; rule.fwd = { n:0 }; passed.push(rule); } });
    // the same evidence twice is one piece of evidence: a passed rule whose test trades are mostly another stronger passed rule's
    // (same market and hour, half or more of the smaller set) is noted as such and not followed separately
    passed.sort(function(a, b){ return (b.test.z || 0) - (a.test.z || 0); }); var kept = [], keys = {};
    passed.forEach(function(rule){ var mine = {}; (R.val[rule.id] || []).forEach(function(q){ mine[q[3] + '|' + q[0]] = 1; }); var nm = Object.keys(mine).length, dup = null;
      kept.forEach(function(k){ if(dup) return; var ov = 0, other = keys[k.id]; Object.keys(mine).forEach(function(x){ if(other[x]) ov++; }); if(ov >= 0.5*Math.min(nm, Object.keys(other).length)) dup = k; });
      if(dup){ rule.status = 'PASSED \u2014 SAME EVIDENCE AS ' + dup.id; rule.why = 'most of its test trades are ' + dup.id + '\u2019s'; rule.sameAs = dup.id; delete rule.fwdFrom; delete rule.fwd; } else { kept.push(rule); keys[rule.id] = mine; } });
    passed = kept;
    R.val = null; R.phase = 'done';
    log('Round ' + R.n + ' tested: ' + passed.length + ' of ' + R.rules.length + ' passed (bar z ≥ ' + bar.toFixed(2) + ' for ' + st.proposed + ' proposals)' + (passed.length ? ': ' + passed.map(function(r){ return r.id; }).join(', ') + ' — from now judged only on new trades.' : '.'));
    feed('Strategy Workshop round ' + R.n + ' tested on data its observation never saw: ' + passed.length + ' of ' + R.rules.length + ' rule(s) passed' + (passed.length ? ' (' + passed.map(ruleText).join('; ') + '); each is now judged only on new trades.' : '.')); }
  function live(){ return st.rules.filter(function(r){ return r.fwdFrom && !r.retiredAt; }); }
  async function forwardMarket(sym){ var P = await prep(sym); if(!P) return 0; var n = 0;
    live().forEach(function(rule){ var tr = tradesFor(P, sym, rule, rule.fwdFrom, Date.now()); st.fwdAcc[rule.id] = (st.fwdAcc[rule.id] || []).concat(tr.map(function(q){ return [q.t, q.r]; })); n += tr.length; }); return n; }
  function judgeForward(){ var fr = st.rules.filter(function(r){ return r.fwdFrom; }), bar = zFor(ALPHA/Math.max(1, fr.length));
    live().forEach(function(rule){ var tr = (st.fwdAcc[rule.id] || []).map(function(q){ return { t:q[0], r:q[1] }; }).sort(function(a, b){ return a.t - b.t; }), s = cstat(tr); rule.fwd = { n:s.n, mean:s.mean, z:s.z, weeks:s.weeks, bar:bar, at:Date.now() };
      if(rule.qualifiedAt){ var post = tr.filter(function(q){ return q.t >= rule.qualifiedAt; }), pm = post.length ? post.reduce(function(a, q){ return a + q.r; }, 0)/post.length : null;
        if((post.length >= 15 && post.length < 30 && pm <= -0.3) || (post.length >= 30 && !(pm > 0))){ rule.retiredAt = Date.now(); rule.status = 'RETIRED'; log('Retired under the demotion rule: ' + rule.id + ' (' + post.length + ' trades after qualifying, ' + sgn(pm) + ' each).'); } return; }
      if(s.n >= 20 && s.mean <= -0.25){ rule.status = 'STOPPED — losing on new trades'; rule.retiredAt = Date.now(); return; }
      if(s.n < 50 || s.weeks < 8){ rule.status = 'PASSED — JUDGED FORWARD'; return; }
      if(s.z != null && s.z >= bar){ rule.qualifiedAt = Date.now(); rule.status = 'QUALIFIED ON NEW TRADES'; log('Qualified on new trades: ' + rule.id + ' (' + s.n + ' trades, ' + sgn(s.mean) + ' each, z ' + s.z.toFixed(2) + ').'); feed('Strategy Workshop: ' + ruleText(rule) + ' qualified on ' + s.n + ' trades after it was frozen (' + sgn(s.mean) + ' each). Paper only; not live performance.'); return; }
      rule.status = 'NOT BEYOND LUCK YET'; }); st.fwdAcc = null; }
  // ── the job: one market per run ──
  function work(){ var R = cur(); if(R && (R.phase === 'observe' || R.phase === 'validate')) return R; return null; }
  function fwdDue(){ return live().length && Date.now() - (st.fwdAt || 0) > FWD_EVERY; }
  async function runNext(){
    var R = work();
    if(!R){ if(fwdDue() || st.fwdQ){ if(!st.fwdQ){ st.fwdQ = markets().map(function(m){ return m.sym; }); st.fwdAcc = {}; } var sym = st.fwdQ.shift(); var n = sym ? await forwardMarket(sym) : 0;
        if(!st.fwdQ.length){ st.fwdQ = null; st.fwdAt = Date.now(); judgeForward(); save(); render(); return 'Forward check done for ' + live().length + ' rule(s).'; } save(); return (sym || '') + ': ' + n + ' new trade(s) for the forward check.'; }
      if(!newRound()) return st.rounds && st.rounds.length ? 'Nothing due: the next round needs 90 days of unused data (from ' + day(cur().validEnd) + ').' : 'Waiting for the Research Lab to study 5+ markets.';
      R = cur(); }
    var left = R.markets.filter(function(s){ return !R.done[s]; }), sym = left[0];
    if(!sym){ if(R.phase === 'observe') propose(R); else judgeValidation(R); save(); render(); return 'Round ' + R.n + ': ' + (R.phase === 'validate' ? 'proposed ' + R.rules.length + ' rule(s); testing next.' : 'tested.'); }
    var msg = R.phase === 'observe' ? await observe(R, sym) : await validate(R, sym); R.done[sym] = 1; save();
    return 'Round ' + R.n + ' (' + (R.phase === 'observe' ? 'observing' : 'testing') + '): ' + msg + '; ' + (left.length - 1) + ' market(s) left.'; }
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'workshop'; })) return true;
    J.push({ id:'workshop', lane:'heavy', prio:1, label:'Strategy Workshop: propose new rules from data, test them once',
      what:'Observes how 700 combinations of 8 measurements were followed on the earlier part of history, proposes the 10 strongest as frozen rules, tests each once on later data the observation never saw (corrected for every rule ever proposed), and follows survivors on new trades only. A new round every 90 days of new data. Paper only.',
      every:function(){ return work() || st.fwdQ ? 5*60e3 : 24*3600e3; }, run:runNext }); return true; }
  if(!register()) setTimeout(function(){ if(!register()) setTimeout(register, 5000); }, 3000);

  // ── the page: everything the Autopilot researches, and the workshop's rounds ──
  var RJ = ['lab','backtests','explore','portfolio','edge','creed','context','entry','patterns','workshop'];
  function ago(t){ if(!t) return 'not yet'; var m = Math.round((Date.now() - t)/60000); return m < 60 ? m + ' min ago' : m < 2880 ? Math.round(m/60) + ' h ago' : Math.round(m/1440) + ' days ago'; }
  function render(){ var pg = el('page-ostrat'); if(!pg) return; var host = el('workshopCard');
    if(!host){ host = document.createElement('div'); host.id = 'workshopCard'; var pc = el('portfolioCard'); if(pc && pc.parentNode === pg) pg.insertBefore(host, pc.nextSibling); else pg.insertBefore(host, pg.firstChild); }
    var O = window.OMEGA_OPERATOR, J = safe(function(){ return O.jobs(); }) || [], S = safe(function(){ return O.state(); }) || {}, jobs = S.jobs || {};
    var rows = RJ.map(function(id){ var j = J.filter(function(x){ return x.id === id; })[0]; if(!j) return ''; var x = jobs[id] || {};
      return '<tr><td>' + esc(j.label) + (x.enabled === false ? ' <span class="dim">(paused)</span>' : '') + '</td><td class="mono">' + ago(x.last) + '</td><td class="dim">' + esc(String(x.result || '—').slice(0, 220)) + '</td></tr>'; }).join('');
    var rr = st.rules.slice().reverse().slice(0, 30).map(function(r){ var t = r.test, f = r.fwd;
      return '<tr><td class="mono">' + esc(r.id) + '</td><td>' + esc(ruleText(r)) + '<br><span class="dim">observed: ' + r.design.n + ' bars over ' + r.design.weeks + ' weeks, ' + (r.design.meanATR >= 0 ? '+' : '') + r.design.meanATR + ' ATR a day after costs</span></td><td class="mono">' + (t ? t.n + ' · ' + sgn(t.mean) + (t.z != null ? ' · z ' + t.z.toFixed(1) : '') : 'testing next') + '</td><td class="mono">' + (f && f.n ? f.n + ' · ' + sgn(f.mean) : r.fwdFrom ? '0 so far' : '—') + '</td><td class="dim">' + esc(r.status + (r.why ? ' — ' + r.why : '')) + '</td></tr>'; }).join('');
    var R = cur();
    host.innerHTML = '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">Everything the Autopilot researches</h2><p class="hint" style="margin-top:0;">Each strategy family runs as its own Autopilot job while the app is open; the latest result of each is below. Details are on each one’s page.</p><div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Job</th><th>Last run</th><th>Latest result</th></tr></thead><tbody>' + rows + '</tbody></table></div></div>' +
      '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">Strategy Workshop — new rules OMEGA proposes from what it observes</h2><p class="hint" style="margin-top:0;">' +
      (R ? 'Round ' + R.n + ': observes ' + day(Math.min.apply(null, markets().map(function(m){ return m.from; }).concat([R.designCut]))) + ' to ' + day(R.designCut) + ', tests ' + day(R.designCut) + ' to ' + day(R.validEnd) + ' · ' + (R.phase === 'observe' ? 'observing (' + Object.keys(R.done).length + ' of ' + R.markets.length + ' markets)' : R.phase === 'validate' ? 'testing (' + Object.keys(R.done).length + ' of ' + R.markets.length + ' markets)' : 'done') + '. ' : 'The first round starts once the Research Lab has studied 5+ markets. ') +
      st.proposed + ' rule(s) proposed so far; each one raises the bar for all. A rule is proposed from the earlier data only, tested once on later data, and then judged only on new trades. Proposals are not results.</p>' +
      (rr ? '<div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Rule</th><th>What it does</th><th>Test (data it never saw)</th><th>New trades</th><th>Status</th></tr></thead><tbody>' + rr + '</tbody></table></div>' : '') +
      (st.log.length ? '<details style="margin-top:8px;"><summary class="hint">Workshop log</summary>' + st.log.slice(0, 12).map(function(x){ return '<div class="hint" style="margin:4px 0;">' + esc(day(x.at)) + ' — ' + esc(x.text) + '</div>'; }).join('') + '</details>' : '') + '</div>';
  }
  setInterval(function(){ var pg = el('page-ostrat'); if(pg && pg.classList.contains('active')) safe(render); }, 5000);
  window.OMEGA_WORKSHOP = { runNext:runNext, state:function(){ return st; }, render:render, FEATS:FEATS, PAIRS:PAIRS, binOf:binOf, ruleText:ruleText, tradesFor:tradesFor, propose:propose, judgeValidation:judgeValidation, judgeForward:judgeForward, newRound:newRound,
    report:function(){ return { proposed:st.proposed, rounds:(st.rounds || []).map(function(R){ return { n:R.n, at:R.at, designCut:R.designCut, validEnd:R.validEnd, phase:R.phase, markets:R.markets.length, rules:R.rules }; }), rules:st.rules }; },
    __reset:function(){ st = { rules:[], log:[], proposed:0 }; save(); } };
})();
</script>
