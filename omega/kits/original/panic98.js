<script>/* ═══ PANIC BOUNCE (v6.5.98) — plan E22's two passes, H1 and H3, grade B: passed fair tests, not yet confirmed (paper) ═══
   H1: a coin's 24-hour return falls into its own bottom 10% (thresholds from the previous 720 hours, set at 00:00 UTC);
       a buy limit 2σ below the close (σ = the 168 hourly returns before, at least 120); filled only if a candle in the next
       3 hours trades below it; sold at the close 24 hours after the fill hour; 0.12% round trip.
   H3: the 24-hour return in the bottom 5% while at least 20% of the watched coins are in their own bottom 10% in the same
       hour; bought at the close, sold 24 hours later; 0.20% round trip.
   Evidence: E22 on 324 perpetuals, 2024 → Oct 2026: H1 +0.36% a trade after costs (t 4.34), H3 +0.22% (t 3.63).
   E25, the survivorship test, with the 143 delisted perpetuals put back (883 coins, Binance's own archive): H1 +0.32%
   (t 4.54), H3 +0.30% (t 4.08), both positive in 2024, 2025 and 2026 (H1's 2025 only +0.03%).
   Caveats: it lives on the big rebounds (without the best 5% of trades each loses about 0.7% a trade) and single trades have
   lost 77–93%: many small seats, never one big one. Breadth here counts the 40 watched coins (the test used every perpetual).
   A volume-0 candle counts as missing (trading halts; Binance keeps writing flat ones after a delisting).
   Same rules and code as OMEGA Prime's watch (trade-for-trade parity with the research engine). Its own record is stored
   under omega_panic_v1. Paper only: OMEGA places no orders; it runs while the app is open. */
(function(){
  'use strict';
  var H = 3600e3, FAPI = 'https://fapi.binance.com', KEY = 'omega_panic_v1', XKEY = 'omega_panic_xinfo_v1', NKEY = 'omega_panic_n';
  function NN(){ try{ return +localStorage.getItem(NKEY) === 100 ? 100 : 40; }catch(e){ return 40; } }   // coins watched: 40 (default) or 100
  function setNN(n){ try{ localStorage.setItem(NKEY, String(n === 100 ? 100 : 40)); }catch(e){} }
  var LS = window.localStorage;
  var STABLE = { USDCUSDT:1, FDUSDUSDT:1, TUSDUSDT:1, BUSDUSDT:1, USDPUSDT:1, DAIUSDT:1, EURUSDT:1 };
  var H1 = { id:'H1', k:2, W:3, q:10, hold:24, cost:0.0012 }, H3 = { id:'H3', q:5, b:0.20, hold:24, cost:0.002 }, AGE = 720;
  var S = load(); S.busy = false;
  function load(){ try{ var v = JSON.parse(LS.getItem(KEY) || 'null'); if(v && v.trades) return v; }catch(e){} return { trades:[], th:{}, lastH:null, scans:0, msg:'', breadth:null }; }
  function save(){ var c = Object.assign({}, S); delete c.busy; try{ LS.setItem(KEY, JSON.stringify(c)); }catch(e){} }
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
  async function onboard(){ var X = null; try{ X = JSON.parse(LS.getItem(XKEY) || 'null'); }catch(e){} if(X && Date.now() - X.at < 24*H) return X.o;
    try{ var info = await getJSON(FAPI + '/fapi/v1/exchangeInfo'), o = {}; (info.symbols || []).forEach(function(s){ if(s.onboardDate) o[s.symbol] = +s.onboardDate; }); LS.setItem(XKEY, JSON.stringify({ at:Date.now(), o:o })); return o; }catch(e){ return (X && X.o) || {}; } }
  async function scan(){ if(S.busy) return 'busy'; var nowH = Math.floor(Date.now()/H), lastClosed = nowH - 1, today = Math.floor(lastClosed/24);
    if(S.lastH != null && S.lastH >= lastClosed) return 'Up to date.';     // nothing new can settle before a new hour closes
    if(Date.now() % H < 150e3) return { skip:true, text:'waiting for the hour’s candles to settle', retryIn:160e3 - (Date.now() % H) + 5e3 };
    S.busy = true; S.msg = 'Scanning…'; render();
    try{ var syms = await universe(), ob = await onboard(), coins = [], need = {}; syms.forEach(function(s){ need[s] = 1; }); S.trades.forEach(function(t){ if(t.status === 'pending' || t.status === 'open') need[t.sym] = 1; });
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
    return '<svg viewBox="0 0 320 46" class="pgauge" role="img" aria-label="Share of coins in panic"><rect x="8" y="14" width="304" height="12" rx="6" fill="var(--border)"/><rect x="8" y="14" width="' + (x - 8).toFixed(1) + '" height="12" rx="6" fill="' + (w >= H3.b ? '#b3372f' : '#c27b2b') + '"/><line x1="' + bx.toFixed(1) + '" y1="8" x2="' + bx.toFixed(1) + '" y2="32" stroke="var(--text)" stroke-width="2"/><text x="' + bx.toFixed(1) + '" y="44" text-anchor="middle" style="font:600 10px system-ui;fill:var(--text)">H3 line 20%</text><text x="8" y="9" style="font:600 10px system-ui;fill:var(--text-dim)">calm</text><text x="312" y="9" text-anchor="end" style="font:600 10px system-ui;fill:var(--text-dim)">everything falling</text></svg>'; }
  function html(){ var L = live(), a = stats('H1'), b = stats('H3');
    var h = '<div class="card" style="margin-bottom:14px;border-color:var(--gold);"><h2 style="color:var(--gold);">Panic bounce — plan E22’s two passes, H1 and H3 (paper)</h2>' +
      '<p style="margin:0 0 8px;"><span class="es-chip">GRADE B — passed two fair tests, not yet confirmed forward</span></p>' +
      '<p class="hint" style="margin:0 0 8px;color:var(--text);"><b>The rules.</b> Panic selling gets overdone. <b>H1:</b> when a coin’s 24-hour fall lands in its own worst 10%, leave a buy order 2σ below the close for 3 hours; if it fills, sell 24 hours later. <b>H3:</b> when a fifth of the market panics in the same hour, buy the deepest falls (worst 5%) at the close and sell 24 hours later.</p>' +
      '<p class="hint" style="margin:0 0 8px;"><b>Evidence.</b> E22, 324 perpetuals, 2024 → Oct 2026: H1 +0.36% a trade after costs (t 4.34), H3 +0.22% (t 3.63). <b>E25, the survivorship test, with the 143 delisted coins put back (883 coins): H1 +0.32% (t 4.54), H3 +0.30% (t 4.08)</b>, both positive in 2024, 2025 and 2026; H1’s 2025 was only +0.03%.</p>' +
      '<p class="hint" style="margin:0 0 8px;"><b>Read it honestly.</b> It lives on the big rebounds: without the best 5% of trades each loses about 0.7% a trade, and single trades have lost 77–93%. So: many small seats (5–10 USDT each on a 100 USDT account), never one big one. Plan E26 tests exactly that.</p>' +
      '<p class="hint" style="margin:8px 0 2px;">Coins in their own worst-10% fall now' + (S.breadth ? ' (' + Math.round(S.breadth.v*100) + '%, hour to ' + hhmm(S.breadth.h + 1).slice(6) + ' UTC)' : '') + ':</p>' + gauge(S.breadth ? S.breadth.v : 0);
    h += L.length ? '<div style="overflow-x:auto;"><table class="pb-tab"><tr><th>Now</th><th>Signal (UTC)</th><th>Order / entry</th><th>Sells</th></tr>' + L.map(function(t){ return '<tr><td><b>' + t.sym.replace('USDT', '') + '</b> <span class="hint">' + t.rule + ' · ' + (t.r24*100).toFixed(1) + '% in 24 h</span></td><td>' + hhmm(t.t + 1) + '</td><td>' + (t.status === 'pending' ? 'buy limit ' + fmt(t.limit) + ' until ' + hhmm(t.t + 1 + H1.W).slice(6) : 'in at ' + fmt(t.entry)) + '</td><td>' + (t.status === 'pending' ? '24 h after a fill' : hhmm(t.due + 1)) + '</td></tr>'; }).join('') + '</table></div>' : '<p class="hint">No open panic-bounce order or trade.</p>';
    var one = function(s){ return s.n ? s.n + ' closed, ' + Math.round(100*s.wins/s.n) + '% winners, average ' + (s.avg >= 0 ? '+' : '') + (s.avg*100).toFixed(2) + '% after costs' : 'no closed trades yet'; };
    h += '<p class="hint" style="margin:8px 0 0;color:var(--text);"><b>Forward record (this app):</b> H1 ' + one(a) + '. H3 ' + one(b) + '. Confirmation needs 50 closed trades each.</p><p class="hint" style="margin:6px 0 0;">' + esc(S.msg || 'Waits for the first scan (the Autopilot runs it hourly).') + ' Watches the ' + NN() + ' most-traded coins; breadth here counts those (the tests counted every perpetual). Paper only.</p>' + '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;"><span class="hint" style="margin:0;">Watch:</span>' + [40, 100].map(function(n){ return '<button type="button" class="btn-outline" data-pbn="' + n + '" style="padding:4px 10px;' + (NN() === n ? 'font-weight:700;border-width:2px;' : 'opacity:.75;') + '">' + n + ' coins</button>'; }).join('') + '</div>' +
      '<p class="hint" style="margin:6px 0 0;">How often H1 filled in 2024–26 (the test’s own data): across the 100 most-traded coins on 82% of days, about 3 a day; across all ~900 perpetuals on 95% of days, about 15 a day (too many coins for a phone). 100 coins uses about 2 MB an hour while open.</p>' + '</div>';
    return h; }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function css(){ if(document.getElementById('pbCss')) return; var st = document.createElement('style'); st.id = 'pbCss';
    st.textContent = '.pgauge{width:100%;max-width:420px;height:auto;display:block;margin:2px 0 10px;}.pb-tab{width:100%;border-collapse:collapse;font-size:13px;margin:6px 0;}.pb-tab th{text-align:left;color:var(--text-dim);font-weight:600;border-bottom:1px solid var(--border);padding:4px;}.pb-tab td{padding:4px;border-bottom:1px solid var(--border);white-space:normal;overflow-wrap:anywhere;}';
    document.head.appendChild(st); }
  var HOSTS = [['panicSigBody', 'climaxSigBody'], ['panicBody', 'climaxBody'], ['panicWatchBody', 'climaxWatchBody']];
  function wire(){ HOSTS.forEach(function(p){ var after = document.getElementById(p[1]); if(after && !document.getElementById(p[0])){ var d = document.createElement('div'); d.id = p[0]; after.parentNode.insertBefore(d, after.nextSibling); } });
    return HOSTS.every(function(p){ return document.getElementById(p[0]); }); }
  function render(){ wire(); css(); HOSTS.forEach(function(p){ var b = document.getElementById(p[0]); if(b) b.innerHTML = html(); }); }
  if(typeof document !== 'undefined' && document.addEventListener) document.addEventListener('click', function(e){ var b = e.target && e.target.closest ? e.target.closest('[data-pbn]') : null; if(!b) return; setNN(+b.getAttribute('data-pbn')); render(); });
  var JOB = { id:'panic', lane:'live', prio:3, label:'Panic-bounce watch (grade B, plans E22/E25): H1 and H3 on the 40 or 100 most-traded coins', what:'Sets each coin’s worst-10% line once a day, checks every closed hour for a panic, and follows every order and trade to its result.', every:15*60e3, run:scan };
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(!J.some(function(x){ return x.id === JOB.id; })) J.push(JOB); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var t2 = 0, iv2 = setInterval(function(){ if(wire()){ clearInterval(iv2); render(); } else if(++t2 > 90){ clearInterval(iv2); render(); } }, 1000);
  window.OMEGA_PANIC = { state:function(){ return S; }, scan:scan, render:render, live:live, H1:H1, H3:H3, NN:NN, setNN:setNN, _:{ rowsOf:rowsOf, dense:dense, dayTh:dayTh, sigma:sigma, settle:settle, runCoin:runCoin, breadthAt:breadthAt, r24:r24, pctl:pctl, stats:stats } };
})();
</script>
