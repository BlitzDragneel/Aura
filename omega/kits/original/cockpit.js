<script>/* ═══ MARKET COCKPIT (v6.5.93) — one clean chart per coin: candles, volume by who is aggressive, liquidity, the book, the plan ═══
   On the Analysis page, under Market now and Today's plan. For the eleven Market Read markets, 1-hour (3 days) or 15-minute
   (18 hours) candles from Binance's public USD-M data:
   - candles with US hours shaded (the busiest, most volatile session);
   - volume underneath, split into aggressive buying (green) and selling (red) from the taker-buy share of each candle;
   - Market Read's liquidity levels on the price axis (red above: buy stops; green below: sell stops), labels kept apart;
   - the order book's resting depth in its own column at the right (bids green, asks red), so it never covers the candles;
   - the Daily Plan's setup drawn ahead of the last candle as zones: entry line, stop zone (red), target zone (green);
   - a strip: price, 24-hour change, range against a typical day, funding, open-interest change, long/short, crowding and
     the share of aggressive buying over 24 hours; and one clean setup card.
   The Autopilot refreshes the selected coin hourly. It reads; it never changes a signal or a plan. */
(function(){
  'use strict';
  var H = 3600e3, FAPI = 'https://fapi.binance.com', CFG = 'omega_cockpit_cfg_v1', NBAR = 72;
  var state = { busy:false, msg:'', D:null, A:null, at:0 };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function cfg(){ try{ var c = JSON.parse(localStorage.getItem(CFG) || 'null'); if(c && c.sym) return c; }catch(e){} return { sym:'BTCUSDT', tf:'1h' }; }
  function setCfg(c){ try{ localStorage.setItem(CFG, JSON.stringify(c)); }catch(e){} }
  function markets(){ return (window.OMEGA_MREAD && window.OMEGA_MREAD.MARKETS) || ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']; }
  function fmtP(x){ if(x == null || !isFinite(x)) return '—'; var a = Math.abs(x); return a >= 1000 ? x.toLocaleString('en-US', { maximumFractionDigits:0 }) : a >= 10 ? x.toFixed(2) : a >= 1 ? x.toFixed(3) : x.toPrecision(4); }
  function pct(x, d){ return x == null || !isFinite(x) ? '—' : (x > 0 ? '+' : '') + (x*100).toFixed(d == null ? 2 : d) + '%'; }
  async function getJSON(url){ var r = await fetch(url); if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }
  // ── pure helpers ──
  function bars(kl){ return (kl || []).map(function(k){ var v = +k[5], tb = +k[9]; return { t:+k[0], o:+k[1], h:+k[2], l:+k[3], c:+k[4], v:v, buy:v > 0 && tb >= 0 ? Math.min(1, tb/v) : 0.5, qv:+k[7] || 0, qb:+k[10] || 0 }; }).filter(function(b){ return b.c > 0 && b.h >= b.l; }); }
  function spread(items, top, bottom, gap){ items.sort(function(a, b){ return a.y - b.y; }); var i;
    for(i = 0; i < items.length; i++){ items[i].ly = Math.max(items[i].y, i ? items[i-1].ly + gap : top); }
    for(i = items.length - 1; i >= 0; i--){ var lim = i < items.length - 1 ? items[i+1].ly - gap : bottom; if(items[i].ly > lim) items[i].ly = lim; }
    return items; }
  function depthBuckets(depth, lo, hi, n){ var bw = (hi - lo)/n, b = [], a = []; for(var i=0; i<n; i++){ b.push(0); a.push(0); }
    if(depth && depth.bids) depth.bids.forEach(function(x){ var p = +x[0], k = Math.floor((p - lo)/bw); if(k >= 0 && k < n) b[k] += p*(+x[1]); });
    if(depth && depth.asks) depth.asks.forEach(function(x){ var p = +x[0], k = Math.floor((p - lo)/bw); if(k >= 0 && k < n) a[k] += p*(+x[1]); });
    return { bids:b, asks:a, bw:bw, max:Math.max.apply(null, b.concat(a).concat([1])) }; }
  // ── the chart ──
  function chart(D, A, P){ var B = bars(D.kl).slice(-NBAR); if(B.length < 10) return '<p class="hint">Not enough candles.</p>';
    var W = 380, PT = 8, PB = 262, VT = 272, VB = 330, XL = 4, XR = 282, DL = 286, DR = 322, LX = 326;
    var lo = Math.min.apply(null, B.map(function(b){ return b.l; })), hi = Math.max.apply(null, B.map(function(b){ return b.h; }));
    var lv = (A && !A.err) ? A.above.slice(0, 4).concat(A.below.slice(0, 4)) : [], plan = P && P.side !== 'none' ? P : null, span = hi - lo;
    lv = lv.filter(function(p){ return p.price >= lo - 0.6*span && p.price <= hi + 0.6*span; });
    var ext = lv.map(function(p){ return p.price; }); if(plan) ext = ext.concat([plan.entry, plan.stop, plan.target]); ext.forEach(function(v){ if(v < lo) lo = v; if(v > hi) hi = v; });
    var pad = (hi - lo)*0.04; lo -= pad; hi += pad;
    var Y = function(v){ return PT + (hi - v)/(hi - lo)*(PB - PT); }, cw = (XR - XL)/B.length, X = function(i){ return XL + (i + 0.5)*cw; }, s = '';
    // US-hours shading and the time axis
    B.forEach(function(b, i){ var hU = new Date(b.t).getUTCHours(); if(hU >= 13 && hU < 21) s += '<rect x="' + (XL + i*cw).toFixed(1) + '" y="' + PT + '" width="' + cw.toFixed(2) + '" height="' + (VB - PT) + '" fill="var(--gold)" fill-opacity="0.045"/>'; });
    var step = D.tf === '15m' ? 16 : 24; B.forEach(function(b, i){ var d = new Date(b.t); if((D.tf === '15m' ? d.getUTCMinutes() === 0 && d.getUTCHours() % 4 === 0 : d.getUTCHours() === 0)) s += '<line x1="' + X(i).toFixed(1) + '" x2="' + X(i).toFixed(1) + '" y1="' + PT + '" y2="' + VB + '" stroke="var(--border)" stroke-width="0.6"/><text x="' + X(i).toFixed(1) + '" y="' + (VB + 11) + '" class="ck-ax" text-anchor="middle">' + (D.tf === '15m' ? d.toISOString().slice(11, 16) : d.toISOString().slice(5, 10)) + '</text>'; });
    // the plan zones, ahead of the last candle
    if(plan){ var x0 = XL + Math.max(0, B.length - 14)*cw, x1 = XR, ye = Y(plan.entry), ys = Y(plan.stop), yt = Y(plan.target);
      s += '<rect data-zone="stop" x="' + x0.toFixed(1) + '" y="' + Math.min(ye, ys).toFixed(1) + '" width="' + (x1 - x0).toFixed(1) + '" height="' + Math.abs(ys - ye).toFixed(1) + '" fill="var(--bear)" fill-opacity="0.16"/>' +
        '<rect data-zone="target" x="' + x0.toFixed(1) + '" y="' + Math.min(ye, yt).toFixed(1) + '" width="' + (x1 - x0).toFixed(1) + '" height="' + Math.abs(yt - ye).toFixed(1) + '" fill="var(--bull)" fill-opacity="0.13"/>' +
        '<line data-zone="entry" x1="' + XL + '" x2="' + x1 + '" y1="' + ye.toFixed(1) + '" y2="' + ye.toFixed(1) + '" stroke="var(--gold)" stroke-width="1.4" stroke-dasharray="5 3"/>'; }
    // liquidity levels
    lv.forEach(function(p){ var y = Y(p.price); s += '<line data-lv="' + p.kind + '" x1="' + XL + '" x2="' + XR + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" stroke="' + (p.side === 'above' ? 'var(--bear)' : 'var(--bull)') + '" stroke-opacity="0.55" stroke-width="0.9" stroke-dasharray="' + (p.kind === 'RND' ? '1 3' : '4 3') + '"/>'; });
    // candles
    B.forEach(function(b, i){ var up = b.c >= b.o, col = up ? 'var(--bull)' : 'var(--bear)', x = X(i), yo = Y(b.o), yc = Y(b.c);
      s += '<line x1="' + x.toFixed(1) + '" x2="' + x.toFixed(1) + '" y1="' + Y(b.h).toFixed(1) + '" y2="' + Y(b.l).toFixed(1) + '" stroke="' + col + '" stroke-width="0.9"/><rect data-c="1" x="' + (x - cw*0.36).toFixed(1) + '" y="' + Math.min(yo, yc).toFixed(1) + '" width="' + Math.max(1, cw*0.72).toFixed(1) + '" height="' + Math.max(0.8, Math.abs(yc - yo)).toFixed(1) + '" fill="' + col + '"/>'; });
    // volume: aggressive buying (green, bottom) and selling (red, top)
    var vmax = Math.max.apply(null, B.map(function(b){ return b.v; }).concat([1e-12]));
    B.forEach(function(b, i){ var hTot = (VB - VT)*b.v/vmax, hb = hTot*b.buy, x = XL + i*cw + cw*0.12, w = Math.max(0.8, cw*0.76);
      s += '<rect data-v="1" x="' + x.toFixed(1) + '" y="' + (VB - hb).toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + hb.toFixed(1) + '" fill="var(--bull)" fill-opacity="0.7"/><rect x="' + x.toFixed(1) + '" y="' + (VB - hTot).toFixed(1) + '" width="' + w.toFixed(1) + '" height="' + (hTot - hb).toFixed(1) + '" fill="var(--bear)" fill-opacity="0.7"/>'; });
    s += '<text x="' + XL + '" y="' + (VT - 2) + '" class="ck-ax">volume · green aggressive buying · red aggressive selling</text>';
    // the order book's depth in its own column
    if(D.depth){ var Q = depthBuckets(D.depth, lo, hi, 48), bh = (PB - PT)/48;
      for(var k = 0; k < 48; k++){ var yk = PB - (k + 1)*bh, lb = (DR - DL)*Q.bids[k]/Q.max, la = (DR - DL)*Q.asks[k]/Q.max;
        if(lb > 0.3) s += '<rect data-d="b" x="' + DL + '" y="' + yk.toFixed(1) + '" width="' + lb.toFixed(1) + '" height="' + Math.max(0.6, bh - 0.4).toFixed(1) + '" fill="var(--bull)" fill-opacity="0.55"/>';
        if(la > 0.3) s += '<rect data-d="a" x="' + DL + '" y="' + yk.toFixed(1) + '" width="' + la.toFixed(1) + '" height="' + Math.max(0.6, bh - 0.4).toFixed(1) + '" fill="var(--bear)" fill-opacity="0.55"/>'; }
      s += '<text x="' + ((DL + DR)/2) + '" y="' + (PT + 7) + '" class="ck-ax" text-anchor="middle">book</text>'; }
    // the price axis: the price, the levels and the plan, labels kept apart
    var last = B[B.length - 1].c, labs = [{ y:Y(last), t:fmtP(last), cls:'ck-now' }];
    lv.forEach(function(p){ labs.push({ y:Y(p.price), t:(p.kind === 'RND' ? '' : p.kind + ' ') + fmtP(p.price), cls:p.side === 'above' ? 'ck-up' : 'ck-dn' }); });
    if(plan){ labs.push({ y:Y(plan.entry), t:'entry ' + fmtP(plan.entry), cls:'ck-now' }); labs.push({ y:Y(plan.stop), t:'stop', cls:'ck-dn2' }); labs.push({ y:Y(plan.target), t:'target', cls:'ck-up2' }); }
    spread(labs, PT + 4, PB, 9.5).forEach(function(l){ s += '<text data-lab="1" x="' + LX + '" y="' + (l.ly + 3).toFixed(1) + '" class="ck-lab ' + l.cls + '">' + esc(l.t) + '</text>' + (Math.abs(l.ly - l.y) > 1 ? '<line x1="' + (LX - 3) + '" x2="' + XR + '" y1="' + l.ly.toFixed(1) + '" y2="' + l.y.toFixed(1) + '" stroke="var(--text-dim)" stroke-width="0.4"/>' : ''); });
    s += '<line x1="' + XL + '" x2="' + DR + '" y1="' + Y(last).toFixed(1) + '" y2="' + Y(last).toFixed(1) + '" stroke="var(--gold)" stroke-width="0.8"/>';
    return '<svg class="ck-svg" viewBox="0 0 ' + W + ' ' + (VB + 16) + '" role="img" aria-label="' + esc(D.sym) + ' chart with liquidity, depth, volume and plan">' + s + '</svg>'; }
  // ── the strip and the setup card ──
  function strip(D, A){ var B = bars(D.kl), last24 = B.slice(D.tf === '15m' ? -96 : -24), qv = last24.reduce(function(a, b){ return a + b.qv; }, 0), qb = last24.reduce(function(a, b){ return a + b.qb; }, 0), P = A && A.pos ? A.pos : {};
    var cells = [['Price', fmtP(A ? A.price : B[B.length-1].c)], ['24 h', pct(A && A.chg24)], ['Range / typical', A && A.range24 != null ? pct(A.range24, 1).replace('+', '') + ' / ' + pct(A.typDay, 1).replace('+', '') : '—'], ['Hourly range', A ? pct(A.atrPct).replace('+', '') : '—'],
      ['Funding', P.funding != null ? (P.funding*100).toFixed(4) + '%' : '—'], ['Open interest 24 h', pct(P.oiChg, 1)], ['Long/short', P.ls != null ? P.ls.toFixed(2) : '—'], ['Crowded', A ? A.crowd : '—'], ['Aggressive buying 24 h', qv > 0 ? (100*qb/qv).toFixed(1) + '%' : '—'],
      ['Book within 1%', A && A.book ? (A.book.imb1 > 0.15 ? 'bids heavier' : A.book.imb1 < -0.15 ? 'asks heavier' : 'balanced') : '—']];
    return '<div class="ck-strip">' + cells.map(function(c){ return '<div><span>' + esc(c[0]) + '</span><b>' + esc(c[1]) + '</b></div>'; }).join('') + '</div>'; }
  function setup(P, sym){ if(!P || P.side === 'none') return '<div class="ck-setup none"><b>No setup for ' + esc(sym.replace('USDT', '')) + '</b><p>' + esc((P && P.why) || 'The Daily Plan has not read this coin yet (it plans BTC, ETH, SOL, BNB and XRP).') + '</p></div>';
    return '<div class="ck-setup ' + P.side + '"><b>' + P.side.toUpperCase() + ' · ' + P.rr.toFixed(1) + ':1 · grade C (unproven, paper first)</b><table class="mr-tab"><tr><td>Entry</td><td>' + fmtP(P.entry) + ' <span class="hint">(' + esc(P.near) + ')</span></td></tr><tr><td>Stop</td><td>' + fmtP(P.stop) + '</td></tr><tr><td>Target</td><td>' + fmtP(P.target) + ' <span class="hint">(' + esc(P.far) + ')</span></td></tr></table><p>' + esc(P.why) + '. Size it on the Risk Guard page: 0.5% risk.</p></div>'; }
  // ── load, render ──
  async function load(){ var c = cfg(); if(state.busy) return; state.busy = true; state.msg = 'Reading ' + c.sym.replace('USDT', '') + '…'; render();
    try{ var D = { sym:c.sym, tf:c.tf }; var h1 = await getJSON(FAPI + '/fapi/v1/klines?symbol=' + c.sym + '&interval=1h&limit=500');
      D.kl = c.tf === '15m' ? await getJSON(FAPI + '/fapi/v1/klines?symbol=' + c.sym + '&interval=15m&limit=192') : h1;
      try{ D.depth = await getJSON(FAPI + '/fapi/v1/depth?symbol=' + c.sym + '&limit=500'); }catch(e){} try{ D.prem = await getJSON(FAPI + '/fapi/v1/premiumIndex?symbol=' + c.sym); }catch(e){}
      try{ D.oi = await getJSON(FAPI + '/futures/data/openInterestHist?symbol=' + c.sym + '&period=1h&limit=25'); }catch(e){} try{ D.ls = await getJSON(FAPI + '/futures/data/globalLongShortAccountRatio?symbol=' + c.sym + '&period=1h&limit=25'); }catch(e){}
      var MR = window.OMEGA_MREAD; state.A = MR && MR._ ? MR._.analyze(c.sym, { kl:h1, depth:D.depth, prem:D.prem, oi:D.oi, ls:D.ls }) : null; state.D = D; state.at = Date.now();
      state.msg = 'Read at ' + new Date().toISOString().slice(11, 16) + ' UTC.'; }
    catch(e){ state.msg = 'Could not read live data (' + (e.message || e) + ').'; }
    state.busy = false; render(); return state.msg; }
  function planOf(sym){ try{ var r = JSON.parse(localStorage.getItem('omega_dplan_v1') || 'null'); return r && r.plans ? r.plans[sym] : null; }catch(e){ return null; } }
  function html(){ var c = cfg(), h = '<div class="dp-card"><h3 class="dp-h">Market cockpit</h3><div class="mr-tabs">' + markets().map(function(s){ return '<button type="button" data-cks="' + s + '" class="' + (s === c.sym ? 'on' : '') + '">' + esc(s.replace('USDT', '')) + '</button>'; }).join('') + '</div>' +
      '<div class="mr-tabs">' + ['1h', '15m'].map(function(tf){ return '<button type="button" data-cktf="' + tf + '" class="' + (tf === c.tf ? 'on' : '') + '">' + (tf === '1h' ? '1 hour · 3 days' : '15 minutes · 18 hours') + '</button>'; }).join('') + '</div>';
    if(state.D && state.D.sym === c.sym && state.D.tf === c.tf){ var P = planOf(c.sym); h += strip(state.D, state.A) + chart(state.D, state.A, P) + '<p class="hint">Gold band: US hours. Dashed red: liquidity above (buy stops); dashed green: below (sell stops); labels on the right. Book column: resting bids and asks. Gold dashed: today’s planned entry, with its stop zone (red) and target zone (green).</p>' + setup(P, c.sym); }
    else h += '<p class="hint">' + (state.busy ? 'Reading…' : 'Not read yet.') + '</p>';
    h += '<p class="hint" style="margin:6px 0 0;">' + esc(state.msg) + ' <button class="btn-outline" type="button" data-ck="load"' + (state.busy ? ' disabled' : '') + '>Read again</button></p></div>'; return h; }
  function css(){ if(el('ckCss')) return; var st = document.createElement('style'); st.id = 'ckCss';
    st.textContent = '.ck-svg{width:100%;height:auto;display:block;background:var(--bg);border:1px solid var(--border);border-radius:10px;margin:6px 0;}.ck-ax{font-size:7px;fill:var(--text-dim);}.ck-lab{font-size:7.5px;font-weight:600;fill:var(--text-dim);}.ck-up{fill:var(--bear);}.ck-dn{fill:var(--bull);}.ck-now{fill:var(--gold);}.ck-up2{fill:var(--bull);}.ck-dn2{fill:var(--bear);}' +
      '.ck-strip{display:grid;grid-template-columns:repeat(2,1fr);gap:4px;margin:6px 0;}.ck-strip div{background:var(--panel2);border-radius:8px;padding:5px 7px;min-width:0;}.ck-strip span{display:block;font-size:10px;color:var(--text-dim);}.ck-strip b{font-size:13px;overflow-wrap:anywhere;}@media(min-width:700px){.ck-strip{grid-template-columns:repeat(5,1fr);}}' +
      '.ck-setup{border-radius:10px;padding:10px;margin:6px 0;border:1px solid var(--border);}.ck-setup.long{border-color:var(--bull);}.ck-setup.short{border-color:var(--bear);}.ck-setup p{font-size:12.5px;margin:6px 0 0;}' +
      '.mr-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 8px;}.mr-tabs button{border:1px solid var(--border);background:var(--panel);color:var(--text);border-radius:999px;padding:5px 10px;font-size:12.5px;cursor:pointer;}.mr-tabs button.on{border-color:var(--gold);color:var(--gold);}';
    document.head.appendChild(st); }
  function render(){ var host = el('cockpitBody'); if(!host) return; css(); host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-cks]'), function(b){ b.onclick = function(){ var c = cfg(); c.sym = b.getAttribute('data-cks'); setCfg(c); load(); }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-cktf]'), function(b){ b.onclick = function(){ var c = cfg(); c.tf = b.getAttribute('data-cktf'); setCfg(c); load(); }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-ck="load"]'), function(b){ b.onclick = function(){ load(); }; }); }
  function onShow(){ render(); var c = cfg(); if(!state.D || state.D.sym !== c.sym || state.D.tf !== c.tf || Date.now() - state.at > 15*60e3) load(); }
  var JOB = { id:'cockpit', lane:'live', prio:2, label:'Market cockpit: keeps the selected coin’s chart, levels and book fresh', what:'Every hour: re-reads the coin chosen in the cockpit (candles, volume, liquidity, order book, positioning) so the Analysis page is ready when opened.', every:60*60e3,
    run: async function(){ return String(await load() || 'Read.'); } };
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(!J.some(function(x){ return x.id === JOB.id; })) J.push(JOB); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  // the Analysis page is a core page, so it is watched directly: when it is on screen, the cockpit (and an unread Daily Plan) load
  var seen = false, lastDP = null; setInterval(function(){ var host = el('cockpitBody'), vis = !!(host && host.offsetParent !== null), DP = window.OMEGA_DPLAN;
    if(vis && !seen){ onShow(); if(DP && DP.state && !DP.state().S && !DP.state().busy) DP.onShow(); }
    if(vis && DP && DP.state && DP.state().at !== lastDP){ lastDP = DP.state().at; if(state.D) render(); }   // a new Daily Plan → redraw its zones and setup card
    seen = vis; }, 1500);
  window.OMEGA_COCKPIT = { render:render, onShow:onShow, load:load, state:function(){ return state; }, JOB:JOB, _:{ bars:bars, spread:spread, depthBuckets:depthBuckets, chart:chart, strip:strip, setup:setup } };
})();
</script>
