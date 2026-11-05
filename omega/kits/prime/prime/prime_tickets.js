<script>/* ═══ PRIME TRADE TICKETS — exact orders for the tested rules only, exit reminders, and two scoreboards ═══
   For every live signal of a rule that passed a fair test (climax reversal, grade A; panic bounce H1/H3, grade B) Prime writes
   the order to place on Binance USDT-M futures: side, type, price, size in USDT for this account, how long the order stays,
   and when to sell. A notification says when an exit is due. "I placed it" marks a ticket as taken: Prime then keeps the
   rule's paper record and the record of the tickets you took. CREED and the Daily Plan never get tickets: they have no edge
   after costs. Prime places no orders itself. */
(function(){
  'use strict';
  var H = 3600e3, KEY = 'prime_tickets_v1';
  var ODDS = { H1:'Measured with delisted coins (E25): +0.32% a trade after costs, about 53% winners; single trades have lost 77–93%, so one small seat per signal.',
               H3:'Measured with delisted coins (E25): +0.30% a trade after costs, about 52% winners; same tail risk as H1.',
               climax:'Passed on 324 untouched coins (round 16): about +1.6% a trade before costs; rare.' };
  var S = load();
  function load(){ try{ var v = JSON.parse(window.PRIME_LS.getItem(KEY) || 'null'); if(v && v.cfg) return v; }catch(e){} return { cfg:{ equity:100, seat:5 }, taken:{}, warned:{} }; }
  function save(){ try{ window.PRIME_LS.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  function utc(h){ return new Date(h*H).toISOString().slice(5, 16).replace('T', ' ') + ' UTC'; }
  function fmt(x){ return !(x > 0) ? '—' : x >= 1000 ? x.toFixed(1) : x >= 10 ? x.toFixed(3) : x >= 1 ? x.toFixed(4) : x.toPrecision(4); }
  function left(ms){ if(ms <= 0) return 'now'; var m = Math.round(ms/60e3); return m >= 60 ? Math.floor(m/60) + ' h ' + (m % 60) + ' min' : m + ' min'; }
  function id(t, rule){ return rule + '|' + t.sym + '|' + t.t; }
  function tickets(){ var out = [], now = Date.now();
    var P = window.OMEGA_PANIC ? window.OMEGA_PANIC.state().trades : [];
    P.forEach(function(t){ if(t.status !== 'pending' && t.status !== 'open') return; var k = id(t, t.rule);
      if(t.status === 'pending') out.push({ k:k, rule:t.rule, sym:t.sym, step:'place', side:'Buy', type:'Limit', price:t.limit, until:t.t + 4, then:'If it fills, sell at market 24 hours after the fill (Prime will say when).', why:'Down ' + (Math.abs(t.r24)*100).toFixed(1) + '% in 24 hours, in its own worst 10%.' });
      else { var due = (t.due + 1)*H; out.push({ k:k, rule:t.rule, sym:t.sym, step:now >= due ? 'sell' : 'hold', side:'Sell', type:'Market', entry:t.entry, dueMs:due, why:t.rule === 'H3' ? 'Bought in a market-wide panic.' : 'Bought after its own panic.' }); } });
    var C = window.OMEGA_CLIMAX ? window.OMEGA_CLIMAX.state().trades : [], hold = window.OMEGA_CLIMAX ? window.OMEGA_CLIMAX.RULE.hold : 12;
    C.forEach(function(t){ if(t.status !== 'open') return; var k = id(t, 'climax'), nowH = Math.floor(now/H), exitMs = (t.e + hold)*H;
      out.push({ k:k, rule:'climax', sym:t.sym, step:nowH === t.e ? 'place' : (now >= exitMs ? 'sell' : 'hold'), side:nowH === t.e ? 'Buy' : 'Sell', type:'Market', until:t.e + 1, dueMs:exitMs, entry:t.entry, why:'A ' + Math.abs(t.z).toFixed(1) + 'σ hourly flush on ' + t.vr.toFixed(1) + '× volume that closed strong.' }); });
    return out.sort(function(a, b){ var o = { sell:0, place:1, hold:2 }; return o[a.step] - o[b.step]; }); }
  function seat(){ return Math.max(5, +S.cfg.seat || 5); }
  function slip(t){ var tk = S.taken[t.k], qty = t.price ? seat()/t.price : null, name = t.sym.replace('USDT', '');
    var head = t.step === 'sell' ? '<b style="color:var(--bad,#b3372f)">SELL NOW</b>' : t.step === 'place' ? '<b>PLACE THIS ORDER</b>' : '<b>HOLDING</b>';
    var body = '';
    if(t.step === 'place' && t.type === 'Limit') body = '<tr><td>Where</td><td>Binance · USDT-M Futures · ' + t.sym + ' · 1× (isolated)</td></tr><tr><td>Order</td><td><b>Limit Buy at ' + fmt(t.price) + '</b></td></tr><tr><td>Size</td><td><b>' + seat() + ' USDT</b> (≈ ' + (qty >= 1 ? qty.toFixed(2) : qty.toPrecision(3)) + ' ' + name + ')</td></tr><tr><td>Cancel if unfilled</td><td>' + utc(t.until) + '</td></tr><tr><td>Then</td><td>' + t.then + '</td></tr>';
    else if(t.step === 'place') body = '<tr><td>Where</td><td>Binance · USDT-M Futures · ' + t.sym + ' · 1× (isolated)</td></tr><tr><td>Order</td><td><b>Market Buy now</b>, before ' + utc(t.until) + '</td></tr><tr><td>Size</td><td><b>' + seat() + ' USDT</b></td></tr><tr><td>Sell</td><td>at market at ' + utc(t.dueMs/H) + '</td></tr>';
    else body = '<tr><td>Position</td><td>' + name + (t.entry ? ' bought at ' + fmt(t.entry) : '') + '</td></tr><tr><td>Sell</td><td><b>Market Sell ' + (t.step === 'sell' ? 'now' : 'at ' + utc(t.dueMs/H) + ' (in ' + left(t.dueMs - Date.now()) + ')') + '</b>, the whole position</td></tr>';
    var taken = tk ? '<span class="tk-tag">' + (tk === 'skip' ? 'skipped' : 'you placed it') + '</span> <button class="tk-btn" data-k="' + t.k + '" data-v="">undo</button>' :
      '<button class="tk-btn" data-k="' + t.k + '" data-v="taken">I placed it</button> <button class="tk-btn ghost" data-k="' + t.k + '" data-v="skip">Skip</button>';
    return '<div class="tk-slip"><div class="tk-top">' + head + '<span>' + name + ' · ' + (t.rule === 'climax' ? 'Climax (grade A)' : 'Panic bounce ' + t.rule + ' (grade B)') + '</span></div><table class="tk-tab">' + body + '</table>' +
      '<p class="hint" style="margin:6px 0 4px">' + t.why + ' ' + ODDS[t.rule] + '</p><div>' + taken + '</div></div>'; }
  function board(){ var P = window.OMEGA_PANIC ? window.OMEGA_PANIC.state().trades : [], C = window.OMEGA_CLIMAX ? window.OMEGA_CLIMAX.state().trades : [];
    var all = P.filter(function(t){ return t.status === 'closed'; }).map(function(t){ return { k:id(t, t.rule), net:t.net }; })
      .concat(C.filter(function(t){ return t.status === 'closed' && t.net != null; }).map(function(t){ return { k:id(t, 'climax'), net:t.net }; }));
    var mine = all.filter(function(x){ return S.taken[x.k] === 'taken'; });
    function line(a, who){ if(!a.length) return who + ': no closed trades yet.'; var s = a.reduce(function(q, x){ return q + x.net; }, 0), w = a.filter(function(x){ return x.net > 0; }).length;
      return who + ': ' + a.length + ' closed, ' + Math.round(100*w/a.length) + '% winners, ' + (s >= 0 ? '+' : '') + (s*seat()).toFixed(2) + ' USDT at ' + seat() + ' USDT a trade (average ' + (s/a.length*100 >= 0 ? '+' : '') + (s/a.length*100).toFixed(2) + '%).'; }
    return '<p class="hint" style="margin:8px 0 0"><b>Scoreboard.</b> ' + line(all, 'Every ticket (paper)') + ' ' + line(mine, 'The ones you placed') + '</p>'; }
  function css(){ if(document.getElementById('tkCss')) return; var st = document.createElement('style'); st.id = 'tkCss';
    st.textContent = '.tk-slip{border:1.5px dashed var(--ink,#1c2230);border-radius:8px;padding:10px 12px;margin:10px 0;background:var(--paper,#fffdf7);}.tk-top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;font-size:13px;letter-spacing:.04em;margin-bottom:6px;}.tk-tab{width:100%;border-collapse:collapse;font-size:14px;}.tk-tab td{padding:3px 4px;border-top:1px solid rgba(0,0,0,.08);vertical-align:top;}.tk-tab td:first-child{color:#6b6556;width:34%;}.tk-tab b{font-variant-numeric:tabular-nums;}.tk-btn{font:inherit;font-size:13px;padding:6px 12px;border-radius:6px;border:1px solid var(--ink,#1c2230);background:var(--ink,#1c2230);color:#fff;margin-right:6px;cursor:pointer;}.tk-btn.ghost{background:transparent;color:var(--ink,#1c2230);}.tk-tag{font-size:12px;padding:2px 8px;border-radius:10px;background:#e6e0d2;margin-right:6px;}.tk-cfg input{width:72px;font:inherit;padding:3px 6px;margin:0 6px 0 4px;}';
    document.head.appendChild(st); }
  function html(){ var T = tickets();
    var h = '<div class="dp-card" id="ticketCard"><h3 class="dp-h">Your orders</h3>';
    h += T.length ? T.map(slip).join('') : '<p class="dp-p"><b>No order to place.</b> None of the tested rules is live right now, so there is nothing to do. Prime will notify you when a ticket appears.</p>';
    h += '<p class="hint tk-cfg" style="margin:6px 0 0">Account <input type="number" min="5" step="1" id="tkEq" value="' + (+S.cfg.equity || 100) + '">USDT · a ticket uses <input type="number" min="5" step="1" id="tkSeat" value="' + seat() + '">USDT (Binance’s minimum is 5). Tickets cover only rules that passed fair tests; CREED and the Daily Plan get none.</p>';
    return h + board() + '</div>'; }
  function render(){ var b = document.getElementById('ticketsBody'); if(!b) return; css(); b.innerHTML = html();
    b.querySelectorAll('.tk-btn').forEach(function(x){ x.onclick = function(){ var k = x.getAttribute('data-k'), v = x.getAttribute('data-v'); if(v) S.taken[k] = v; else delete S.taken[k]; save(); render(); }; });
    var e = document.getElementById('tkEq'), s = document.getElementById('tkSeat');
    if(e) e.onchange = function(){ S.cfg.equity = Math.max(5, +e.value || 100); save(); render(); };
    if(s) s.onchange = function(){ S.cfg.seat = Math.max(5, +s.value || 5); save(); render(); }; }
  function remind(){ tickets().forEach(function(t){ if(t.step !== 'sell' || S.taken[t.k] !== 'taken' || S.warned[t.k]) return; S.warned[t.k] = 1; save();
    try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('OMEGA Prime · sell ' + t.sym.replace('USDT', '') + ' now', { body:'The rule’s holding time is over: market sell the whole position.' }); }catch(e){} }); }
  setInterval(function(){ remind(); var pg = document.getElementById('page-today'); if(pg && pg.offsetParent !== null) render(); }, 20e3);
  setTimeout(function(){ render(); remind(); }, 1500);
  window.OMEGA_TICKETS = { render:render, tickets:tickets, state:function(){ return S; } };
})();
</script>
