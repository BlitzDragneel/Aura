<script>/* ═══ DAILY PLAN (v6.5.91) — the market now, which side to trade, and a plan per coin, followed to its result ═══
   For BTC, ETH, SOL, BNB, XRP. The market state uses plan E8's definitions on the five coins' own daily index (Binance
   USD-M daily closes): DEPRESSED (below the 200-day average and −15% in 30 days), BOOMING (above it and +25%), CORRECTING
   (above it and −8% in 7 days), CONSOLIDATING (quiet: 30-day volatility below its yearly median and |30-day| < 10%),
   NORMAL otherwise; plus uptrend/downtrend (above/below the 200-day average) and "falling this week" (7-day ≤ −5%).
   Side: BOOMING → longs; DEPRESSED → shorts; CORRECTING → longs at the liquidity below (a dip in an uptrend); otherwise
   follow the trend when the coin agrees (above its 200-hour average for longs, below for shorts), else stand aside.
   Plan: entry at the nearest liquidity pool on the with-trend side (Market Read's levels, within 3 hourly ranges), stop
   half a range beyond it, target the nearest pool on the other side; shown only at reward-to-risk ≥ 1.5.
   GRADE C, UNPROVEN: the trend and sweep rules this resembles failed fair tests. Plan E16 (md5 884bd4e2…) follows every plan
   to its result on paper (touch of the entry → stop, target or 48 hours; 0.12% costs; R) and judges it once after 50
   trades or 26 weeks. Grade A signals come only from the climax watch (the one rule that passed). OMEGA places no orders. */
(function(){
  'use strict';
  var H = 3600e3, FAPI = 'https://fapi.binance.com', KEY = 'omega_dplan_v1', COINS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'], COST = 0.0012;
  var state = { busy:false, msg:'', S:null, reads:{}, at:0 };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function load(){ try{ var v = JSON.parse(localStorage.getItem(KEY) || 'null'); if(v && v.trades) return v; }catch(e){} return { plans:{}, open:[], trades:[] }; }
  function save(v){ try{ localStorage.setItem(KEY, JSON.stringify(v)); }catch(e){} }
  function fmtP(x){ if(x == null || !isFinite(x)) return '—'; var a = Math.abs(x); return a >= 1000 ? x.toLocaleString('en-US', { maximumFractionDigits:0 }) : a >= 10 ? x.toFixed(2) : a >= 1 ? x.toFixed(3) : x.toPrecision(4); }
  function pct(x, d){ return x == null || !isFinite(x) ? '—' : (x > 0 ? '+' : '') + (x*100).toFixed(d == null ? 1 : d) + '%'; }
  async function getJSON(url){ var r = await fetch(url); if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }
  // ── market state (pure): daily closes per coin → E8 state ──
  function marketState(daily, nowMs){ var nowD = Math.floor((nowMs || Date.now())/864e5), byDay = {};
    Object.keys(daily).forEach(function(s){ var prev = null; (daily[s] || []).forEach(function(k){ var d = Math.floor(+k[0]/864e5), c = +k[4]; if(d >= nowD || !(c > 0)) return; if(prev != null){ var r = Math.log(c/prev); (byDay[d] = byDay[d] || []).push(Math.max(-0.5, Math.min(0.5, r))); } prev = c; }); });
    var days = Object.keys(byDay).map(Number).sort(function(a, b){ return a - b; }); if(days.length < 260) return { state:'UNKNOWN', why:'not enough daily history' };
    var L = [], lv = 0, r = []; days.forEach(function(d){ var x = byDay[d].reduce(function(a, b){ return a + b; }, 0)/byDay[d].length; lv += x; L.push(Math.exp(lv)); r.push(x); });
    var n = L.length, last = L[n-1], ma200 = L.slice(n - 200).reduce(function(a, b){ return a + b; }, 0)/200, r30 = last/L[n-31] - 1, r7 = last/L[n-8] - 1, r3 = last/L[n-4] - 1;
    function sd(a){ var m = a.reduce(function(x, y){ return x + y; }, 0)/a.length; return Math.sqrt(a.reduce(function(x, y){ return x + (y - m)*(y - m); }, 0)/(a.length - 1)); }
    var vol30 = sd(r.slice(n - 30)), vols = []; for(var i = Math.max(30, n - 366); i < n - 1; i++) vols.push(sd(r.slice(i - 29, i + 1))); vols.sort(function(a, b){ return a - b; }); var volmed = vols[Math.floor(vols.length/2)];
    var up = last > ma200, st = 'NORMAL';
    if(vol30 < volmed && Math.abs(r30) < 0.10) st = 'CONSOLIDATING'; if(up && r7 <= -0.08) st = 'CORRECTING'; if(up && r30 >= 0.25) st = 'BOOMING'; if(!up && r30 <= -0.15) st = 'DEPRESSED';
    return { state:st, uptrend:up, falling:r7 <= -0.05, r7:r7, r30:r30, r3:r3, vsMa200:last/ma200 - 1, vol30:vol30, volmed:volmed, day:days[n-1] }; }
  // ── the plan for one coin (pure) ──
  function planFor(A, S){ if(!A || A.err || !S || S.state === 'UNKNOWN') return { side:'none', why:'no data' };
    var above200h = A.price > A.ema200, side = 'none', why = '';
    if(S.state === 'BOOMING'){ side = above200h ? 'long' : 'none'; why = 'Booming market' + (above200h ? ', coin above its 200-hour average' : ', but the coin is below its 200-hour average'); }
    else if(S.state === 'DEPRESSED'){ side = !above200h ? 'short' : 'none'; why = 'Depressed market' + (!above200h ? ', coin below its 200-hour average' : ', but the coin is holding above its 200-hour average'); }
    else if(S.state === 'CORRECTING'){ side = 'long'; why = 'A correction inside an uptrend: buy only at the liquidity below'; }
    else { if(S.uptrend && above200h){ side = 'long'; why = (S.state === 'CONSOLIDATING' ? 'Quiet market' : 'Market') + ' in an uptrend, coin above its 200-hour average'; }
           else if(!S.uptrend && !above200h){ side = 'short'; why = (S.state === 'CONSOLIDATING' ? 'Quiet market' : 'Market') + ' in a downtrend, coin below its 200-hour average'; }
           else { why = 'The market trend and the coin disagree: stand aside'; } }
    if(side === 'none') return { side:'none', why:why };
    var near = side === 'long' ? A.below.filter(function(p){ return p.atrs <= 3; })[0] : A.above.filter(function(p){ return p.atrs <= 3; })[0], far = side === 'long' ? A.above[0] : A.below[0];
    if(!near || !far) return { side:'none', why:why + '; no liquidity level close enough to plan from' };
    var entry = near.price, stop = side === 'long' ? entry - 0.5*A.atr : entry + 0.5*A.atr, target = far.price, risk = Math.abs(entry - stop), rr = Math.abs(target - entry)/risk;
    if(!(rr >= 1.5)) return { side:'none', why:why + '; the nearest target gives only ' + (rr ? rr.toFixed(1) : '0') + ':1, under 1.5:1' };
    return { side:side, entry:entry, stop:stop, target:target, rr:rr, why:why, near:near.label, far:far.label, grade:'C' }; }
  // ── forward record (plan E16) ──
  function follow(rec, sym, rows, nowH){ var by = {}; rows.forEach(function(r){ by[r.h] = r; });
    var P = rec.plans[sym];
    if(P && !P.trig){ for(var h = P.h + 1; h < nowH; h++){ var b = by[h]; if(!b) continue; var hit = P.side === 'long' ? b.lo <= P.entry : b.hi >= P.entry; if(hit){ rec.open.push({ sym:sym, side:P.side, entry:P.entry, stop:P.stop, target:P.target, h:h, rr:P.rr }); P.trig = h; notify(sym, P); break; } if(h - P.h >= 24) break; } }
    rec.open = rec.open.filter(function(t){ if(t.sym !== sym) return true; var d = t.side === 'long' ? 1 : -1, risk = Math.abs(t.entry - t.stop), exit = null, why = '';
      for(var h = t.h; h < nowH; h++){ var b = by[h]; if(!b) continue; var sHit = d > 0 ? b.lo <= t.stop : b.hi >= t.stop, tHit = d > 0 ? b.hi >= t.target : b.lo <= t.target;
        if(sHit){ exit = t.stop; why = 'stop'; break; } if(tHit && h > t.h){ exit = t.target; why = 'target'; break; } if(h - t.h >= 48){ exit = b.c; why = '48 hours'; break; } }
      if(exit == null) return true; var R = d*(exit - t.entry)/risk - COST*t.entry/risk; rec.trades.push({ sym:sym, side:t.side, h:t.h, out:why, R:Math.round(R*1000)/1000 }); rec.trades = rec.trades.slice(-1000); return false; });
    return rec; }
  function stats(rec){ var T = rec.trades, n = T.length, sum = T.reduce(function(a, t){ return a + t.R; }, 0), wins = T.filter(function(t){ return t.R > 0; }).length, wk = {};
    T.forEach(function(t){ var w = Math.floor(t.h/168); wk[w] = (wk[w] || 0) + t.R; }); var x = Object.keys(wk).map(function(k){ return wk[k]; }), m = x.length ? x.reduce(function(a, b){ return a + b; }, 0)/x.length : 0, sd = x.length > 1 ? Math.sqrt(x.reduce(function(a, b){ return a + (b - m)*(b - m); }, 0)/(x.length - 1)) : 0;
    return { n:n, wins:wins, avgR:n ? sum/n : null, totalR:sum, t:sd > 0 ? m/(sd/Math.sqrt(x.length)) : null, weeks:x.length }; }
  function notify(sym, P){ try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('OMEGA Daily Plan (grade C, paper): ' + sym.replace('USDT', '') + ' ' + P.side.toUpperCase(), { body:'Entry ' + fmtP(P.entry) + ' touched. Stop ' + fmtP(P.stop) + ', target ' + fmtP(P.target) + '. Unproven: paper first, 1% risk at most.' }); }catch(e){} }
  // ── run: market state + a plan per coin + follow ──
  async function run(){ if(state.busy) return 'busy'; state.busy = true; state.msg = 'Reading the market…'; render();
    try{ var MR = window.OMEGA_MREAD; if(!MR || !MR._) throw new Error('Market Read is not loaded'); var nowH = Math.floor(Date.now()/H), daily = {}, rec = load(), made = 0;
      for(var i=0; i<COINS.length; i++){ var s = COINS[i]; daily[s] = await getJSON(FAPI + '/fapi/v1/klines?symbol=' + s + '&interval=1d&limit=600'); }
      state.S = marketState(daily);
      for(i = 0; i < COINS.length; i++){ s = COINS[i];
        var D = { kl:await getJSON(FAPI + '/fapi/v1/klines?symbol=' + s + '&interval=1h&limit=500') };
        try{ D.depth = await getJSON(FAPI + '/fapi/v1/depth?symbol=' + s + '&limit=500'); }catch(e){} try{ D.prem = await getJSON(FAPI + '/fapi/v1/premiumIndex?symbol=' + s); }catch(e){}
        try{ D.oi = await getJSON(FAPI + '/futures/data/openInterestHist?symbol=' + s + '&period=1h&limit=25'); }catch(e){} try{ D.ls = await getJSON(FAPI + '/futures/data/globalLongShortAccountRatio?symbol=' + s + '&period=1h&limit=25'); }catch(e){}
        var A = MR._.analyze(s, D); state.reads[s] = A; if(MR._.remember) MR._.remember(A);
        rec = follow(rec, s, MR._.rowsOf(D.kl, nowH), nowH);
        var P = planFor(A, state.S), old = rec.plans[s];
        var hasOpen = rec.open.some(function(t){ return t.sym === s; }); if(!hasOpen){ P.h = nowH - 1; rec.plans[s] = P; } else if(old){ P = old; } if(P.side !== 'none') made++; }
      save(rec); state.at = Date.now(); state.msg = 'Read at ' + new Date().toISOString().slice(11, 16) + ' UTC: ' + made + ' plan' + (made === 1 ? '' : 's') + ' today.'; return state.msg; }
    catch(e){ state.msg = 'Could not read the market (' + (e.message || e) + ').'; return state.msg; }
    finally{ state.busy = false; render(); } }
  // ── the cards ──
  var STATE_TXT = { BOOMING:['Booming', 'go', 'Strong rise: longs only, and only on dips into liquidity.'], DEPRESSED:['Depressed', 'short', 'Falling hard: shorts only, on rallies into liquidity; capitulation bounces can be violent.'], CORRECTING:['Correcting', 'wait', 'A pullback inside an uptrend: longs only at the liquidity below.'], CONSOLIDATING:['Consolidating', 'wait', 'Quiet range: small size; follow the trend only where the coin agrees.'], NORMAL:['Normal', 'wait', 'No extreme: follow the trend only where the coin agrees.'], UNKNOWN:['Unknown', 'wait', 'Not enough data.'] };
  function session(h){ return h < 8 ? 'Asia' : h < 13 ? 'London' : h < 21 ? 'US' : 'Late'; }
  function html(){ var S = state.S, rec = load(), st = stats(rec), nowH = new Date().getUTCHours(), h = '';
    h += '<div class="dp-card"><h3 class="dp-h">Market now</h3>';
    if(!S) h += '<p class="hint">Not read yet. <button class="btn-outline" type="button" data-dp="run">Read the market</button></p>';
    else { var T = STATE_TXT[S.state] || STATE_TXT.NORMAL, B = state.reads.BTCUSDT;
      h += '<div class="dp-state ' + T[1] + '"><b>' + T[0] + '</b> · ' + (S.uptrend ? 'uptrend' : 'downtrend') + (S.falling ? ' · <b>falling this week</b>' : '') + '</div><p class="dp-p">' + esc(T[2]) + '</p>' +
        '<table class="mr-tab"><tr><td>Top-5 index, 7 days / 30 days</td><td>' + pct(S.r7) + ' / ' + pct(S.r30) + '</td></tr><tr><td>Against its 200-day average</td><td>' + pct(S.vsMa200) + '</td></tr>' +
        '<tr><td>Session now</td><td>' + session(nowH) + ' (' + nowH + ':00 UTC, ' + ((nowH + 20) % 24) + ':00 Tobago)' + (nowH >= 13 && nowH < 21 ? ' — busiest, most volatile hours' : '') + '</td></tr>' +
        (B && !B.err ? '<tr><td>BTC today</td><td>' + pct(B.chg24) + ', range ' + pct(B.range24).replace('+', '') + ' (typical ' + pct(B.typDay).replace('+', '') + ')</td></tr><tr><td>BTC positioning</td><td>' + (B.crowd === 'balanced' ? 'balanced' : B.crowd + ' crowded') + '</td></tr>' : '') + '</table>'; }
    h += '</div><div class="dp-card"><h3 class="dp-h">Today’s plan <span class="dp-grade">Grade C · unproven · paper first</span></h3>';
    if(S){ h += '<table class="mr-tab"><tr><th>Coin</th><th>Side</th><th>Entry → stop → target</th><th>R:R</th></tr>' + COINS.map(function(s){ var P = rec.plans[s] || { side:'none', why:'not read yet' }, open = rec.open.filter(function(t){ return t.sym === s; })[0];
        return '<tr><td><b>' + s.replace('USDT', '') + '</b></td><td class="' + (P.side === 'long' ? 'up' : P.side === 'short' ? 'dn' : '') + '">' + (P.side === 'none' ? 'stand aside' : P.side.toUpperCase()) + (open ? ' · in a paper trade' : P.trig ? ' · triggered' : '') + '</td><td>' + (P.side === 'none' ? '<span class="hint">' + esc(P.why) + '</span>' : fmtP(P.entry) + ' → ' + fmtP(P.stop) + ' → ' + fmtP(P.target) + '<br><span class="hint">' + esc(P.why) + '. Entry at ' + esc(P.near) + ', target ' + esc(P.far) + '.</span>') + '</td><td>' + (P.rr ? P.rr.toFixed(1) + ':1' : '—') + '</td></tr>'; }).join('') + '</table>'; }
    h += '<p class="hint">How to use it: wait for price to reach the entry; risk 1% at most; the stop and target are levels, not guesses. <b>Unproven:</b> the trend and sweep rules this resembles failed fair tests, so every plan is followed on paper (plan E16) and judged once after 50 trades. Grade A signals come only from the climax watch (Edge Lab), the one rule that passed.</p>';
    h += '<p class="dp-rec"><b>Forward record:</b> ' + (st.n ? st.n + ' paper trades, ' + Math.round(100*st.wins/st.n) + '% winners, average ' + (st.avgR >= 0 ? '+' : '') + st.avgR.toFixed(2) + 'R, total ' + (st.totalR >= 0 ? '+' : '') + st.totalR.toFixed(1) + 'R' + (st.t != null ? ', t ' + st.t.toFixed(2) : '') + '. Judged at 50 trades.' : 'no closed paper trades yet.') + '</p>';
    h += '<p class="hint" style="margin:6px 0 0;">' + esc(state.msg || '') + ' <button class="btn-outline" type="button" data-dp="run"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Reading…' : 'Read again') + '</button></p></div>';
    return h; }
  function css(){ if(el('dplanCss')) return; var st = document.createElement('style'); st.id = 'dplanCss';
    st.textContent = '.dp-card{background:var(--panel);border:1px solid var(--gold);border-radius:12px;padding:12px;margin:0 0 12px;}.dp-h{margin:0 0 8px;font-size:16px;color:var(--gold);}.dp-grade{font-size:11px;font-weight:600;color:var(--amber);margin-left:6px;}' +
      '.dp-state{display:inline-block;padding:4px 10px;border-radius:999px;font-size:13px;background:var(--panel2);}.dp-state.go{background:rgba(37,211,139,.16);color:var(--bull);}.dp-state.short{background:rgba(255,77,94,.16);color:var(--bear);}.dp-p{font-size:13px;margin:8px 0;line-height:1.5;}.dp-rec{font-size:13px;margin:8px 0 0;}' +
      '.mr-tab{width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed;margin:6px 0;}.mr-tab th{text-align:left;color:var(--text-dim);font-weight:600;border-bottom:1px solid var(--border);padding:4px;}.mr-tab td{padding:4px;border-bottom:1px solid var(--border);white-space:normal;overflow-wrap:anywhere;}.up{color:var(--bull);}.dn{color:var(--bear);}';
    document.head.appendChild(st); }
  function render(){ ['dplanBody', 'dplanAnaBody'].forEach(function(id){ var host = el(id); if(!host) return; css(); host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-dp="run"]'), function(b){ b.onclick = function(){ run(); }; }); }); }
  function onShow(){ render(); if(!state.S || Date.now() - state.at > 30*60e3) run(); }
  var JOB = { id:'dplan', lane:'live', prio:3, label:'Daily Plan: market state, side and a plan per coin (grade C, followed on paper)', what:'Every hour: reads the market state from BTC, ETH, SOL, BNB and XRP, picks long, short or stand aside for each, plans entries at liquidity, and follows every plan to its result (plan E16).', every:60*60e3,
    run: async function(){ var r = await run(); return String(r || 'Read.'); } };
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(!J.some(function(x){ return x.id === JOB.id; })) J.push(JOB); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var t2 = 0, iv2 = setInterval(function(){ if(el('dplanBody') || el('dplanAnaBody')){ clearInterval(iv2); render(); } else if(++t2 > 60) clearInterval(iv2); }, 1000);
  window.OMEGA_DPLAN = { run:run, render:render, onShow:onShow, state:function(){ return state; }, COINS:COINS, JOB:JOB, _:{ marketState:marketState, planFor:planFor, follow:follow, stats:stats, html:html } };
})();
</script>
