<script>/* ═══ PRIME PANIC-BOUNCE WATCH — E22 H1 and H3, Grade B (passed a fair test, not yet confirmed) ═══
   H1: a coin's 24-hour return falls into its own bottom 10% (thresholds from the previous 720 hours, set at 00:00 UTC);
       a buy limit 2σ below the close (σ = the 168 hourly returns before, at least 120); filled only if a candle in the next
       3 hours trades below it; sold at the close 24 hours after the fill hour; 0.12% round trip. Test: +0.36% a trade, t 4.34.
   H3: the 24-hour return in the bottom 5% while at least 20% of the watched coins are in their own bottom 10% in the same hour;
       bought at the close, sold 24 hours later; 0.20% round trip. Test: +0.22% a trade, t 3.63.
   Survivorship test (E25, with the 143 delisted coins): passed, H1 +0.32% (t 4.54), H3 +0.30% (t 4.08).
   As a 100 USDT account of 5 or 10 USDT seats with a −10% stop (E26, 2021 → Oct 2026): FAILED, drawdowns 56–59%, gains in
   4 of 6 years; 2021 made most of it, and since 2022 the trades average +0.1–0.4% (2026 negative).
   Open caveats: the result leans on the biggest rebounds (without the best 5% it loses), single trades have lost 90%, and
   breadth here is measured on the 40 watched coins (the test used every perpetual). Paper only; many small seats, never one big one. */
(function(){
  'use strict';
  var H = 3600e3, FAPI = 'https://fapi.binance.com', KEY = 'prime_panic_v1', NKEY = 'prime_panic_n';
  function NN(){ try{ return +window.PRIME_LS.getItem(NKEY) === 100 ? 100 : 40; }catch(e){ return 40; } }   // coins watched: 40 (default) or 100
  function setNN(n){ try{ window.PRIME_LS.setItem(NKEY, String(n === 100 ? 100 : 40)); }catch(e){} }
  var STABLE = { USDCUSDT:1, FDUSDUSDT:1, TUSDUSDT:1, BUSDUSDT:1, USDPUSDT:1, DAIUSDT:1, EURUSDT:1 };
  var H1 = { id:'H1', k:2, W:3, q:10, hold:24, cost:0.0012 }, H3 = { id:'H3', q:5, b:0.20, hold:24, cost:0.002 }, AGE = 720;
  var S = load(); S.busy = false;
  function load(){ try{ var v = JSON.parse(window.PRIME_LS.getItem(KEY) || 'null'); if(v && v.trades) return v; }catch(e){} return { trades:[], th:{}, lastH:null, scans:0, msg:'', breadth:null }; }
  function save(){ var c = Object.assign({}, S); delete c.busy; try{ window.PRIME_LS.setItem(KEY, JSON.stringify(c)); }catch(e){} }
  async function getJSON(u){ var r = await fetch(u); if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  // ── pure parts (tested against the research engine, trade for trade) ──
  function dense(rows){ if(!rows.length) return null; var h0 = rows[0].h, h1 = rows[rows.length - 1].h, n = h1 - h0 + 1, D = { h0:h0, n:n, c:new Array(n).fill(NaN), hi:new Array(n).fill(NaN), lo:new Array(n).fill(NaN) };
    rows.forEach(function(r){ var i = r.h - h0; if(i >= 0 && i < n){ D.c[i] = r.c; D.hi[i] = r.hi; D.lo[i] = r.lo; } }); return D; }
  function at(D, a, h){ var i = h - D.h0; return i >= 0 && i < D.n ? D[a][i] : NaN; }
  function r24(D, h){ var a = at(D, 'c', h), b = at(D, 'c', h - 24); return a > 0 && b > 0 ? Math.log(a/b) : NaN; }
  function pctl(sorted, q){ var p = (sorted.length - 1)*q/100, i = Math.floor(p), t = p - i, a = sorted[i], b = sorted[Math.min(i + 1, sorted.length - 1)], d = b - a; return t >= 0.5 ? b - d*(1 - t) : a + d*t; }   // numpy 'linear'
  function dayTh(D, day){ var d0 = day*24, w = []; for(var h = d0 - 720; h < d0; h++){ var x = r24(D, h); if(isFinite(x)) w.push(x); }
    if(w.length < 360) return null; w.sort(function(a, b){ return a - b; }); return { q10:pctl(w, 10), q5:pctl(w, 5) }; }
  function sigma(D, h){ var xs = []; for(var j = h - 168; j < h; j++){ var a = at(D, 'c', j), b = at(D, 'c', j - 1); if(a > 0 && b > 0) xs.push(Math.log(a/b)); }
    if(xs.length < 120) return NaN; var m = xs.reduce(function(s, x){ return s + x; }, 0)/xs.length; return Math.sqrt(xs.reduce(function(s, x){ return s + (x - m)*(x - m); }, 0)/(xs.length - 1)); }
  function blockUntil(t){ return t.fill != null ? t.fill + 24 : t.rule === 'H1' ? t.t + H1.W : t.t + 24; }
  // settle one trade with the data up to lastH: pending/missed/open/closed/void
  function settle(t, D, lastH){ if(t.status === 'closed' || t.status === 'missed' || t.status === 'void') return t;
    if(t.rule === 'H1' && t.fill == null){ for(var j = t.t + 1; j <= t.t + H1.W && j <= lastH; j++){ if(at(D, 'lo', j) < t.limit){ t.fill = j; t.entry = t.limit; break; } }
      if(t.fill == null){ t.status = lastH >= t.t + H1.W ? 'missed' : 'pending'; return t; } }
    var x = (t.rule === 'H1' ? t.fill : t.t) + 24;
    if(x > lastH){ t.status = 'open'; t.due = x; return t; }
    var c = at(D, 'c', x); if(!(c > 0)){ t.status = 'void'; return t; }
    t.exit = c; t.net = Math.round((c/t.entry - 1 - (t.rule === 'H1' ? H1.cost : H3.cost))*1e7)/1e7; t.status = 'closed'; return t; }
  // one coin, hours fromH..lastH: new signals in time order, each settled before the next is allowed (as the research run)
  function runCoin(sym, D, th, br, fromH, lastH, trades, firstH){ var made = [];
    ['H1', 'H3'].forEach(function(rule){ var mine = trades.filter(function(t){ return t.sym === sym && t.rule === rule; }), last = mine[mine.length - 1];
      if(last) settle(last, D, lastH); var nxt = last ? blockUntil(last) : -1;
      for(var h = fromH; h <= lastH; h++){ if(h < nxt || h - firstH < AGE) continue; var T = th[Math.floor(h/24)]; if(!T) continue; var x = r24(D, h); if(!isFinite(x)) continue;
        var c = at(D, 'c', h), t = null;
        if(rule === 'H1'){ if(!(x <= T.q10)) continue; var sg = sigma(D, h); if(!(sg > 0 && c > 0)) continue; t = { sym:sym, rule:'H1', t:h, close:c, limit:c*Math.exp(-H1.k*sg), r24:x }; }
        else { if(!(x <= T.q5) || !((br[h] || 0) >= H3.b) || !(c > 0)) continue; t = { sym:sym, rule:'H3', t:h, entry:c, r24:x, br:br[h] }; }
        settle(t, D, lastH); if(t.status === 'void'){ if(rule === 'H1') nxt = h + H1.W; continue; } /* as research: H1 blocks its window, H3 nothing */ made.push(t); nxt = blockUntil(t); } });
    return made; }
  function breadthAt(coins, h){ var n = 0, k = 0; coins.forEach(function(C){ var T = C.th[Math.floor(h/24)], x = r24(C.D, h); if(T && isFinite(x)){ n++; if(x <= T.q10) k++; } }); return n >= 5 ? k/n : null; }
  // ── the scan ──
  function rowsOf(kl){ return (kl || []).map(function(k){ return { h:Math.floor(+k[0]/H), hi:+k[2], lo:+k[3], c:+k[4], v:+k[5] }; }).filter(function(r){ return r.c > 0 && r.hi >= r.lo && r.v > 0; }); }   // a volume-0 candle is missing (halts, delistings)
  async function universe(){ var t = await getJSON(FAPI + '/fapi/v1/ticker/24hr'); return (t || []).filter(function(x){ return /USDT$/.test(x.symbol) && !STABLE[x.symbol] && +x.quoteVolume > 0; }).sort(function(a, b){ return +b.quoteVolume - +a.quoteVolume; }).slice(0, NN()).map(function(x){ return x.symbol; }); }
  function onboard(){ try{ var X = JSON.parse(window.PRIME_LS.getItem('prime_xinfo_v1') || 'null'); return (X && X.o) || {}; }catch(e){ return {}; } }
  async function scan(){ if(S.busy) return 'busy'; var nowH = Math.floor(Date.now()/H), lastClosed = nowH - 1, today = Math.floor(lastClosed/24);
    if(S.lastH != null && S.lastH >= lastClosed) return 'Up to date.';     // nothing new can settle before a new hour closes
    if(Date.now() % H < 150e3) return { skip:true, text:'waiting for the hour’s candles to settle', retryIn:160e3 - (Date.now() % H) + 5e3 };
    S.busy = true; S.msg = 'Scanning…'; render();
    try{ var syms = await universe(), ob = onboard(), coins = [], need = {}; syms.forEach(function(s){ need[s] = 1; }); S.trades.forEach(function(t){ if(t.status === 'pending' || t.status === 'open') need[t.sym] = 1; });
      var list = Object.keys(need), from = S.lastH == null ? lastClosed : Math.max(S.lastH + 1, lastClosed - 300);
      for(var i = 0; i < list.length; i++){ var sym = list[i], th = S.th[sym] || {};
        var full = false; for(var d = Math.floor(from/24); d <= today; d++) if(!th[d]) full = true;
        try{ var kl = await getJSON(FAPI + '/fapi/v1/klines?symbol=' + sym + '&interval=1h&limit=' + (full ? 1500 : (S.lastH != null && lastClosed - S.lastH <= 24 ? 200 : 499))); }catch(e){ continue; }
        var D = dense(rowsOf(kl).filter(function(r){ return r.h < nowH; })); if(!D) continue;
        if(full){ th = {}; for(d = Math.floor(from/24); d <= today; d++){ var T = dayTh(D, d); if(T) th[d] = T; } S.th[sym] = th;
          S.first = S.first || {}; S.first[sym] = kl.length < 1500 ? D.h0 : Math.min(S.first[sym] || Infinity, D.h0 - 1e5); }   // a short history means a young coin
        var firstH = ob[sym] ? Math.floor(ob[sym]/H) : (S.first && S.first[sym] != null ? S.first[sym] : D.h0);   // the 30-day age rule
        coins.push({ sym:sym, D:D, th:th, firstH:firstH, watched:syms.indexOf(sym) >= 0 }); await sleep(120); }
      var br = {}, W = coins.filter(function(C){ return C.watched; }); for(var h = from; h <= lastClosed; h++){ var b = breadthAt(W, h); if(b != null) br[h] = b; }
      var fired = 0; coins.forEach(function(C){
        S.trades.forEach(function(t){ if(t.sym === C.sym) settle(t, C.D, lastClosed); });
        if(C.watched){ var m = runCoin(C.sym, C.D, C.th, br, from, lastClosed, S.trades, C.firstH); m.forEach(function(t){ S.trades.push(t); if(t.status === 'pending' || t.status === 'open'){ fired++; notify(t); } }); } });
      Object.keys(S.th).forEach(function(s){ Object.keys(S.th[s]).forEach(function(d){ if(+d < today - 14) delete S.th[s][d]; }); });
      S.breadth = br[lastClosed] != null ? { h:lastClosed, v:br[lastClosed] } : S.breadth;
      S.trades = S.trades.slice(-800); S.lastH = lastClosed; S.scans++;
      S.msg = 'Scanned ' + syms.length + ' coins to ' + new Date((lastClosed + 1)*H).toISOString().slice(11, 16) + ' UTC: ' + fired + ' new signal' + (fired === 1 ? '' : 's') + '.'; }
    catch(e){ S.msg = 'Could not scan (' + (e.message || e) + ').'; S.busy = false; save(); render(); return { error:S.msg }; }
    S.busy = false; save(); render(); return S.msg; }
  function notify(t){ try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('OMEGA Prime · Grade B ' + t.rule + ': ' + t.sym.replace('USDT', ''), { body:t.rule === 'H1' ? 'Panic in its bottom 10%. Rule: buy limit at ' + t.limit.toPrecision(5) + ' for 3 hours, sell 24 hours after a fill. Paper first; a small seat.' : 'Market-wide panic. Rule: buy at the close, sell 24 hours later. Paper first; a small seat.' }); }catch(e){} }
  function stats(rule){ var c = S.trades.filter(function(t){ return t.status === 'closed' && (!rule || t.rule === rule); }), n = c.length, w = c.filter(function(t){ return t.net > 0; }).length, s = c.reduce(function(a, t){ return a + t.net; }, 0); return { n:n, wins:w, avg:n ? s/n : null }; }
  function live(){ return S.trades.filter(function(t){ return t.status === 'pending' || t.status === 'open'; }); }
  function fmt(x){ return x >= 10 ? x.toFixed(2) : x >= 1 ? x.toFixed(4) : x.toPrecision(4); }
  function hhmm(h){ return new Date(h*H).toISOString().slice(5, 16).replace('T', ' '); }
  function gauge(v){ var w = Math.max(0, Math.min(1, v || 0)), x = 8 + 304*w, bx = 8 + 304*H3.b;
    return '<svg viewBox="0 0 320 46" class="pgauge" role="img" aria-label="Share of coins in panic"><rect x="8" y="14" width="304" height="12" rx="6" fill="#e6e0d2"/><rect x="8" y="14" width="' + (x - 8).toFixed(1) + '" height="12" rx="6" fill="' + (w >= H3.b ? '#b3372f' : '#c27b2b') + '"/><line x1="' + bx.toFixed(1) + '" y1="8" x2="' + bx.toFixed(1) + '" y2="32" stroke="#1c2230" stroke-width="2"/><text x="' + bx.toFixed(1) + '" y="44" text-anchor="middle" style="font:600 10px system-ui;fill:#1c2230">H3 line 20%</text><text x="8" y="9" style="font:600 10px system-ui;fill:#8a8577">calm</text><text x="312" y="9" text-anchor="end" style="font:600 10px system-ui;fill:#8a8577">everything falling</text></svg>'; }
  function html(){ var L = live(), a = stats('H1'), b = stats('H3'), h = '<div class="dp-card"><h3 class="dp-h">Panic-bounce watch <span class="dp-grade" style="color:var(--gold)">Grade B · passed a fair test, not yet confirmed</span></h3>';
    h += '<p class="dp-p">Panic selling gets overdone. When a coin’s 24-hour fall lands in its own worst 10%, <b>H1</b> leaves a buy order 2σ lower for 3 hours and sells a day after it fills. When a fifth of the market panics together, <b>H3</b> buys the deepest falls at the close and sells a day later. Wins come from many small seats; one big seat can be ruined by a collapse.</p>';
    h += '<p class="hint" style="margin:8px 0 2px">Coins in their own worst-10% fall right now' + (S.breadth ? ' (' + Math.round(S.breadth.v*100) + '%, ' + hhmm(S.breadth.h + 1).slice(6) + ' UTC)' : '') + ':</p>' + gauge(S.breadth ? S.breadth.v : 0);
    h += L.length ? '<table class="mr-tab"><tr><th>Now</th><th>Signal (UTC)</th><th>Order / entry</th><th>Sells</th></tr>' + L.map(function(t){ return '<tr><td><b>' + t.sym.replace('USDT', '') + '</b> <span class="hint">' + t.rule + ' · ' + (t.r24*100).toFixed(1) + '% in 24 h</span></td><td>' + hhmm(t.t + 1) + '</td><td>' + (t.status === 'pending' ? 'buy limit ' + fmt(t.limit) + ' until ' + hhmm(t.t + 1 + H1.W).slice(6) : 'in at ' + fmt(t.entry)) + '</td><td>' + (t.status === 'pending' ? '24 h after a fill' : hhmm(t.due + 1)) + '</td></tr>'; }).join('') + '</table>' : '<p class="hint">No open panic-bounce order or trade.</p>';
    var one = function(s){ return s.n ? s.n + ' closed, ' + Math.round(100*s.wins/s.n) + '% winners, average ' + (s.avg >= 0 ? '+' : '') + (s.avg*100).toFixed(2) + '% after costs' : 'no closed trades yet'; };
    h += '<p class="dp-rec"><b>Forward record (this app):</b> H1 ' + one(a) + '. H3 ' + one(b) + '. It passed the survivorship test (delisted coins included). Run as a 100 USDT account of small seats it FAILED (E26: drawdowns of 56–59%, gains in 4 of 6 years), so it stays a paper record. Confirmation needs 50 closed trades each here.</p><p class="hint">' + (S.msg || 'Waits for the first scan.') + ' Breadth here counts the ' + NN() + ' watched coins; the test counted every perpetual.</p>' + '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;"><span class="hint" style="margin:0;">Watch:</span>' + [40, 100].map(function(n){ return '<button type="button" class="btn-outline" data-pbn="' + n + '" style="padding:4px 10px;' + (NN() === n ? 'font-weight:700;border-width:2px;' : 'opacity:.75;') + '">' + n + ' coins</button>'; }).join('') + '</div>' +
      '<p class="hint" style="margin:6px 0 0;">How often H1 filled in 2024–26 (the test’s own data): across the 100 most-traded coins on 82% of days, about 3 a day; across all ~900 perpetuals on 95% of days, about 15 a day (too many coins for a phone). 100 coins uses about 2 MB an hour while open.</p>' + '</div>';
    return h; }
  function render(){ var b = document.getElementById('panicBody'); if(b) b.innerHTML = html(); }
  if(typeof document !== 'undefined' && document.addEventListener) document.addEventListener('click', function(e){ var b = e.target && e.target.closest ? e.target.closest('[data-pbn]') : null; if(!b) return; setNN(+b.getAttribute('data-pbn')); render(); });
  var JOB = { id:'panic', lane:'live', prio:4, label:'Panic-bounce watch (grade B): H1 and H3 on the 40 or 100 most-traded coins, every hour', what:'Sets each coin’s worst-10% line once a day, checks every closed hour for a panic, and follows every order and trade to its result.', every:15*60e3, run:scan };
  window.OMEGA_OPERATOR.jobs().push(JOB);
  window.OMEGA_PANIC = { state:function(){ return S; }, scan:scan, render:render, live:live, H1:H1, H3:H3, NN:NN, setNN:setNN, _:{ rowsOf:rowsOf, dense:dense, dayTh:dayTh, sigma:sigma, settle:settle, runCoin:runCoin, breadthAt:breadthAt, r24:r24, pctl:pctl, stats:stats } };
})();
</script>
