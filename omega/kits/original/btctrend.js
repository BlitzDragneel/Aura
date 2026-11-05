<script>/* ═══ BTC TREND BENCHMARK (v6.5.60) — "BTC 14-day momentum + 18% volatility target", frozen as written, judged forward ═══
   Another assistant froze this rule on 18 Oct 2026 and called it the cleanest edge. OMEGA holds it to the same standard as
   its own rules. It runs exactly as written: at each daily close (00:00 UTC), direction = the sign of BTC's 14-day
   return. Size = 18% divided by its 20-day volatility (daily returns, sample standard deviation, x sqrt(365.25)), kept
   between 0.35x and 1.80x the account. The position changes only when the direction flips or the size moves by more
   than 0.15. Costs are 0.06% a side, and funding is paid and received as a perpetual (OMEGA adds funding; the original
   left it out). What it is NOT: proven. Its 14 days was picked after looking at several horizons. Every year of BTC
   has been seen, and on 51 coins nothing had seen, the same rule made +14% a year but z 1.60, short of its 2.33 bar.
   Days decided at or after the close of 18 Oct 2026 are its forward record. Paper only: OMEGA places no orders. */
(function(){
  'use strict';
  var KEY = 'omega_btctrend_v1', DAY = 86400e3, SYM = 'BTCUSDT', L = 14, NV = 20, TGT = 0.18, LO = 0.35, HI = 1.80, THR = 0.15, COST = 0.0006,
      FREEZE_DAY = Date.UTC(2026, 9, 18)/DAY, FWD_MIN = 26, FWD_FULL = 52, FWD_BAR = 1.96, FWD_STOP = -0.35;
  var RESEARCH = { frozenBy:'another assistant, 18 Oct 2026 (OMEGA adds funding, which the original left out)',
    btc:{ data:'BTC, Jan 2019 – Oct 2026 (all of it already seen: in-sample)', annPct:23.9, t:2.58, worstFallPct:-27.5, avgSize:0.44, costs2xPct:21.4,
      periods:[ ['2019–22', 92.7, -27.5, 1.71], ['2023–24', 65.1, -20.8, 1.47], ['2025–Oct 2026', 38.2, -21.7, 1.28] ],
      noVolTarget:'without the volatility target (always 1×): +43% a year but a −62% worst fall', sameSize:'held at a constant 0.44× (its average size): +18.7% a year, −33% worst fall, so the volatility target helped a little on BTC',
      lookbacks:'other lookbacks with the same sizing: 7 days +2% a year, 10 days +8%, 21 days +14%, 28 days +23%, 42 days +23%, 60 days +17%. 14 days was one of the luckiest; 7–10 days lost in 2025.', fundingCost:'funding cost it about 2.2% a year' },
    fresh:{ data:'the same rule on each of 51 coins nothing had seen, Jan 2020 – Oct 2026', annPct:14.2, t:1.60, bar:2.33, costs2xPct:12.3, worstFallPct:-28.2, passed:false,
      years:[ ['2020', 22.6], ['2021', 28.4], ['2022', 9.2], ['2023', 9.5], ['2024', 21.9], ['2025', -8.3], ['2026 (to Oct)', 12.3] ] } };
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function el(id){ return document.getElementById(id); }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function lsGet(k, d){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v && typeof v === 'object' && !Array.isArray(v) ? v : d; }catch(e){ return d; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function pct(v, d){ return v == null || !isFinite(v) ? '—' : (v >= 0 ? '+' : '−') + Math.abs(100*v).toFixed(d == null ? 1 : d) + '%'; }
  function dayStr(d){ return new Date(d*DAY).toISOString().slice(0, 10); }
  var st = lsGet(KEY, null) || { v:1, res:null, retired:null, noted:'' }, run = { busy:false, msg:'' };
  function sign(x){ return x > 0 ? 1 : x < 0 ? -1 : 0; }
  function nwT(x, lag){ lag = lag || 2; x = x.filter(function(v){ return isFinite(v); }); var n = x.length; if(n < 8) return null;
    var m = x.reduce(function(a, b){ return a + b; }, 0)/n, e = x.map(function(v){ return v - m; }), g0 = e.reduce(function(a, v){ return a + v*v; }, 0)/n, lrv = g0;
    for(var k=1; k<=lag; k++){ var s = 0; for(var i=k; i<n; i++) s += e[i]*e[i-k]; lrv += 2*(1 - k/(lag + 1))*s/(n - k); }
    return lrv > 0 ? m/Math.sqrt(lrv/n) : null; }
  // ── the rule, day by day (pure) ──
  function compute(x, now, full){ now = now || Date.now(); if(!x || !x.c || x.c.length < L + NV + 2) return { error:'needs at least ' + (L + NV + 2) + ' stored daily closes of BTC' };
    var c = x.c, n = c.length, ff = {}, f0 = null;
    (x.fund || []).forEach(function(q){ var t = +q[0], r = +q[1]; if(!isFinite(t) || !isFinite(r)) return; var d = Math.floor(t/DAY); ff[d] = (ff[d] || 0) + r; if(f0 == null || t < f0) f0 = t; });
    var days = [], held = 0, held1 = 0, prevHeld = 0;   // held = position decided at the close of day i (held over day i+1)
    var R = new Array(n).fill(NaN); for(var i=1; i<n; i++) if(c[i] > 0 && c[i-1] > 0) R[i] = c[i]/c[i-1] - 1;
    var hist = [];   // per day: [day, pnl, held after the close, want, momentum, vol]
    var hPrev = 0, hPrev2 = 0;
    for(var i=0; i<n; i++){ var d = x.k0 + i;
      var pnl = 0; if(i >= 1){ var r = isFinite(R[i]) ? R[i] : 0; pnl = hPrev*r - hPrev*(ff[d] || 0) - Math.abs(hPrev - hPrev2)*COST; }
      var want = NaN, mom = NaN, vol = NaN;
      if(i >= L && c[i] > 0 && c[i-L] > 0 && f0 != null && d*DAY >= f0 + DAY){
        var w = []; for(var j=i-NV+1; j<=i; j++){ if(j < 1 || !isFinite(R[j])){ w = null; break; } w.push(R[j]); }
        if(w){ var m = w.reduce(function(a, b){ return a + b; }, 0)/NV, sd = Math.sqrt(w.reduce(function(a, b){ return a + (b - m)*(b - m); }, 0)/(NV - 1)); vol = sd*Math.sqrt(365.25);
          mom = c[i]/c[i-L] - 1; var sc = Math.min(HI, Math.max(LO, TGT/vol)); want = sign(mom)*sc; } }
      var cur;
      if(!isFinite(want)) cur = 0; else if(sign(want) !== sign(hPrev) || Math.abs(want - hPrev) > THR) cur = want; else cur = hPrev;
      hist.push([d, pnl, cur, want, mom, vol]); hPrev2 = hPrev; hPrev = cur; }
    // a day's result belongs to the record of the day its position was decided (the day before)
    var first = -1; for(var k=0; k<hist.length; k++) if(hist[k][1] !== 0){ first = k; break; }
    function stats(rows){ var nn = rows.length; if(!nn) return { days:0, weeks:0 }; var eq = 1, pk = 1, dd = 0; rows.forEach(function(q){ eq *= 1 + q[1]; if(eq > pk) pk = eq; if(eq/pk - 1 < dd) dd = eq/pk - 1; });
      var wk = {}; rows.forEach(function(q){ var dt = new Date(q[0]*DAY), sun = q[0] + ((7 - dt.getUTCDay()) % 7); wk[sun] = (wk[sun] || 0) + q[1]; });
      var wv = Object.keys(wk).sort(function(a, b){ return a - b; }).map(function(k){ return wk[k]; }), mean = wv.reduce(function(a, b){ return a + b; }, 0)/wv.length;
      return { days:nn, weeks:wv.length, cum:eq - 1, worstFall:dd, ann:rows.reduce(function(a, q){ return a + q[1]; }, 0)/nn*365, weekMean:mean, t:nwT(wv) }; }
    var past = first < 0 ? [] : hist.slice(first).filter(function(q){ return q[0] <= FREEZE_DAY; }), fwd = hist.filter(function(q){ return q[0] > FREEZE_DAY; });
    var last = hist[hist.length - 1];
    return { at:now, lastDay:last[0], now:{ day:last[0], held:last[2], want:last[3], momentum:last[4], vol:last[5], close:c[n-1] },
      before:stats(past), forward:stats(fwd), forwardDays:fwd.map(function(q){ return [q[0], +q[1].toFixed(6), +q[2].toFixed(3)]; }), recent:hist.slice(-30).map(function(q){ return [q[0], +q[1].toFixed(6), +q[2].toFixed(3)]; }), hist:full ? hist : undefined }; }
  // ── forward judgement, written 18 Oct 2026 before any forward day ──
  function verdict(F, retired){ if(retired) return { code:'RETIRED', text:'Retired on ' + retired.at.slice(0, 10) + ': ' + retired.why + '. A retired rule never returns.' };
    if(!F || !F.days) return { code:'WAIT', text:'Its forward record starts with the position decided at the close of 18 Oct 2026 (8 pm in Trinidad).' };
    if(F.worstFall <= FWD_STOP) return { code:'RETIRE', why:'fell ' + Math.round(-F.worstFall*100) + '% from its forward peak (limit 35%; its worst in seven years was 27.5%)' };
    if(F.weeks < FWD_MIN) return { code:'COLLECT', text:F.weeks + ' of ' + FWD_MIN + ' forward weeks. Too early to judge.' };
    if(F.weekMean <= 0) return { code:'RETIRE', why:'its ' + F.weeks + ' forward weeks average zero or less' };
    if(F.t != null && F.t >= FWD_BAR) return { code:'CONFIRMED', text:'Confirmed on ' + F.weeks + ' forward weeks (z ' + F.t.toFixed(2) + ' ≥ ' + FWD_BAR + '). Still paper only.' };
    if(F.weeks < FWD_FULL) return { code:'HOLDING', text:'Positive on ' + F.weeks + ' forward weeks but not yet clear of chance (z ' + (F.t == null ? '—' : F.t.toFixed(2)) + '). Judged again at ' + FWD_FULL + ' weeks.' };
    return { code:'UNPROVEN', text:'Positive after ' + F.weeks + ' forward weeks but not clear of chance. Stays on paper.' }; }
  async function runNow(){ if(run.busy) return { skip:true, text:'already running' }; run.busy = true; run.msg = 'Reading BTC'; render();
    try{ var X = window.OMEGA_CARRYXS; if(!X || !X.getData) throw new Error('data loader not ready'); var data = await X.getData(30*60e3), res = compute(data[SYM], Date.now());
      if(res.error){ st.res = { at:Date.now(), error:res.error }; lsSet(KEY, st); return { skip:true, text:res.error, retryIn:6*3600e3 }; }
      var V = verdict(res.forward, st.retired); if(V.code === 'RETIRE' && !st.retired){ st.retired = { at:new Date().toISOString(), why:V.why }; V = verdict(res.forward, st.retired); }
      st.res = res; st.verdict = V; lsSet(KEY, st); note(V);
      return { text:'BTC trend benchmark: ' + (res.now.held > 0 ? 'long ' : res.now.held < 0 ? 'short ' : 'flat ') + Math.abs(res.now.held).toFixed(2) + '× after the close of ' + dayStr(res.lastDay) + '.' }; }
    catch(e){ return { error:(e && e.message) || String(e) }; }
    finally{ run.busy = false; run.msg = ''; render(); } }
  function note(V){ if(st.noted === V.code) return; safe(function(){ var B = window.OMEGA_BRAIN; if(!B || !B.feedObservation) return; if(B.retract) B.retract(['BTC trend benchmark']);
    B.feedObservation({ pinned:true, strat:'omega', tf:'1d', symbol:'BTCUSDT', text:'BTC trend benchmark (14-day direction, sized to 18% volatility, frozen 18 Oct 2026 by another assistant): NOT proven. In-sample on BTC 2019–2026 with funding, +23.9% a year, worst fall −27.5%; 14 days was one of the luckiest lookbacks. On 51 unseen coins the same rule made +14% a year, z 1.60 against 2.33. Paper only, judged on new days. Forward: ' + (V.text || V.why || V.code) }); }); st.noted = V.code; lsSet(KEY, st); }
  function lastFn(){ return st.res; }
  // ── the card (OMEGA Strategy, after the harvest) ──
  function render(){ var host = el('btctrendCard'); if(!host){ var pg = el('page-ostrat'); if(!pg) return; host = document.createElement('div'); host.id = 'btctrendCard'; var h0 = el('harvestCard'); if(h0 && h0.parentNode === pg) pg.insertBefore(host, h0.nextSibling); else pg.insertBefore(host, pg.firstChild); }
    var r = st.res, V = st.verdict || verdict(null, st.retired), eq = safe(function(){ return window.OMEGA_AUTOPILOT.cfg().startEquity; }) || 100, Z = RESEARCH;
    var lab = { WAIT:['Paper · not proven · forward record starts tonight','warn'], COLLECT:['Paper · not proven · collecting forward weeks','warn'], HOLDING:['Paper · positive, not yet proven','warn'], CONFIRMED:['Paper · confirmed forward','bull'], UNPROVEN:['Paper · unproven','warn'], RETIRED:['Retired','bear'] }[V.code] || ['Paper','warn'];
    var h = '<div class="card" style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;"><div><h2 style="color:var(--gold);margin-bottom:4px;">BTC trend benchmark — 14-day direction, sized to volatility</h2><span class="bt-lab ' + lab[1] + '">' + esc(lab[0]) + '</span></div>' +
      '<button class="btn-outline" type="button" id="btctrendRun"' + (run.busy ? ' disabled' : '') + '>' + (run.busy ? esc(run.msg || 'Working') : 'Update now') + '</button></div>' +
      '<p class="hint" style="margin-top:8px;">Frozen by ' + esc(Z.frozenBy) + '. At each daily close: long if BTC is up over 14 days, short if down. Size = 18% ÷ its 20-day volatility, kept between 0.35× and 1.80× the account, changed only when the direction flips or the size moves more than 0.15. <b>Paper only.</b></p>';
    if(!r) h += '<p class="hint">' + (run.busy ? esc(run.msg) : 'Not worked out yet. It reads BTC’s stored daily closes and funding; the Autopilot updates it after each daily close.') + '</p>';
    else if(r.error) h += '<p class="hint">' + esc(r.error) + '.</p>';
    else { var N = r.now, dir = N.held > 0 ? 'LONG' : N.held < 0 ? 'SHORT' : 'FLAT', col = N.held > 0 ? 'var(--bull)' : N.held < 0 ? 'var(--bear)' : 'var(--text-dim)';
      h += '<p class="hint" style="font-size:15px;"><b style="color:' + col + ';">' + dir + ' ' + Math.abs(N.held).toFixed(2) + '×</b> after the close of ' + esc(dayStr(r.lastDay)) + ' (BTC ' + (+N.close).toLocaleString(undefined, { maximumFractionDigits:2 }) + '). That is ' + (Math.abs(N.held)*eq).toFixed(2) + ' USDT of BTC ' + (N.held < 0 ? 'short' : N.held > 0 ? 'long' : '') + ' on a ' + eq + ' USDT account.</p>' +
        '<p class="hint">14-day change ' + pct(N.momentum, 2) + ' · 20-day volatility ' + pct(N.vol, 1).replace('+', '') + ' a year · the rule’s size today ' + (isFinite(N.want) ? Math.abs(N.want).toFixed(2) + '×' : '—') + (isFinite(N.want) && Math.abs(N.want - N.held) > 1e-9 ? ' (kept at ' + Math.abs(N.held).toFixed(2) + '×: the change is under 0.15)' : '') + '. Next update: the next daily close (00:00 UTC, 8 pm in Trinidad).</p>';
      var F = r.forward || {}, B = r.before || {};
      h += '<p class="hint"><b>Forward record:</b> ' + esc(V.text || V.why || '') + (F.days ? ' ' + F.days + ' days: ' + pct(F.cum, 2) + ' (' + (F.cum >= 0 ? '+' : '−') + Math.abs(F.cum*eq).toFixed(2) + ' USDT on ' + eq + '), worst fall ' + pct(F.worstFall, 1) + '.' : '') + '</p>' +
        (B.days ? '<p class="hint">On your stored history before the freeze (worked out by this app, with funding): ' + pct(B.cum, 1) + ' in all over ' + B.weeks + ' weeks, about ' + pct(B.ann, 0) + ' a year, worst fall ' + pct(B.worstFall, 1) + '.</p>' : ''); }
    h += '<details style="margin-top:6px;"><summary class="hint" style="cursor:pointer;"><b>Why it is a benchmark, not an edge</b></summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;line-height:1.6;">' +
      '<li>On ' + esc(Z.btc.data) + ': ' + pct(Z.btc.annPct/100) + ' a year, z ' + Z.btc.t.toFixed(2) + ', worst fall ' + pct(Z.btc.worstFallPct/100) + ', average size ' + Z.btc.avgSize + '×; ' + esc(Z.btc.fundingCost) + '. By period: ' + Z.btc.periods.map(function(p){ return esc(p[0]) + ' ' + pct(p[1]/100, 0) + ' (worst ' + pct(p[2]/100, 0) + ', z ' + p[3].toFixed(2) + ')'; }).join(', ') + '. No single period is clear of chance on its own.</li>' +
      '<li>' + esc(Z.btc.noVolTarget) + '; ' + esc(Z.btc.sameSize) + '.</li><li>' + esc(Z.btc.lookbacks) + '</li>' +
      '<li><b>The untouched test:</b> ' + esc(Z.fresh.data) + ': ' + pct(Z.fresh.annPct/100) + ' a year, z ' + Z.fresh.t.toFixed(2) + ' against a bar of ' + Z.fresh.bar.toFixed(2) + ', worst fall ' + pct(Z.fresh.worstFallPct/100) + ' — <b>not passed</b>, though positive in 6 of 7 years (' + Z.fresh.years.map(function(y){ return esc(y[0]) + ' ' + pct(y[1]/100, 0); }).join(', ') + ').</li>' +
      '<li><b>Forward judgement, fixed 18 Oct 2026 before any forward day:</b> nothing is judged before ' + FWD_MIN + ' weeks. At ' + FWD_MIN + ' or more it is retired if its weeks average zero or less, and confirmed at z ≥ ' + FWD_BAR + '. At any time it is retired after a ' + Math.round(-FWD_STOP*100) + '% fall from its forward peak.</li></ul></details></div>';
    host.innerHTML = h; var bt = el('btctrendRun'); if(bt) bt.onclick = function(){ var O = window.OMEGA_OPERATOR; if(O && O.runNow) safe(function(){ O.runNow('btctrend'); }); else runNow(); }; }
  function report(){ return { rule:'btc-tsmom14-vt18', text:'Daily at the close: direction = sign(BTC close / close 14 days ago - 1); size = clamp(0.18 / (20-day sample std of daily returns x sqrt(365.25)), 0.35, 1.80); change only if direction flips or size moves > 0.15; 0.06% a side; funding as a perpetual. Paper only.', research:RESEARCH, judgement:{ minWeeks:FWD_MIN, fullWeeks:FWD_FULL, bar:FWD_BAR, stopFall:FWD_STOP }, verdict:st.verdict || null, retired:st.retired || null, result:st.res || null }; }
  function every(){ var r = st.res, today = Math.floor(Date.now()/DAY); if(r && !r.error && r.lastDay < today - 1) return 30*60e3; return 6*3600e3; }
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'btctrend'; })) return true;
    J.push({ id:'btctrend', lane:'heavy', prio:2, label:'BTC trend benchmark (not proven; judged forward)', what:'After each daily close: the frozen BTC 14-day trend rule’s position and its forward record, from the stored daily closes and funding. Paper only.', every:every, run:runNow }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var nav0 = window.navigate; if(typeof nav0 === 'function') window.navigate = function(p){ var rr = nav0.apply(this, arguments); if(p === 'ostrat') setTimeout(render, 70); return rr; };
  setTimeout(function(){ try{ render(); }catch(e){} }, 1700);
  window.OMEGA_BTCTREND = { compute:compute, verdict:verdict, runNow:runNow, render:render, report:report, state:function(){ return st; }, last:lastFn, RESEARCH:RESEARCH };
})();
</script>
