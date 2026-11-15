"""Prime upgrade: a Desks page (Bitcoin, Gold, Silver bots) with the big-move WATCH and the alerts log.
Usage: python3 patch_prime_desks.py <omega-prime.html>   (idempotent)"""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
if "page-desks" in s:
    print("already patched"); sys.exit(0)

sec = ('<section class="page" id="page-desks"><h2 class="pg">Desks</h2><p class="pg-sub">One bot each for Bitcoin, gold and silver. '
       'They read the market every 15 minutes. A trade is called only by a rule that passed its test; WATCH means a big move is likely, direction unknown.</p>'
       '<div id="desksBody"><div class="card"><p class="dp-p">Loading the desks…</p></div></div></section>\n  ')
a = s.index('<section class="page" id="page-evidence">')
s = s[:a] + sec + s[a:]

old = "['risk', 'Risk', 'M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z'],"
assert s.count(old) == 1
s = s.replace(old, "['desks', 'Desks', 'M4 20V10M10 20V4M16 20v-7M22 20H2'], " + old)

js = r"""
<script>
/* Prime Desks: reads the asset bots' public records (bot-state branch) and live prices. Information only. */
(function(){
  var RAW = 'https://raw.githubusercontent.com/BlitzDragneel/Aura/bot-state/', FAPI = 'https://fapi.binance.com';
  var A = [['BTC', 'Bitcoin', 'BTCUSDT'], ['XAU', 'Gold', 'XAUUSDT'], ['XAG', 'Silver', 'XAGUSDT']];
  function esc(x){ return String(x == null ? '' : x).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function num(x, d){ return (typeof x === 'number' && isFinite(x)) ? x.toLocaleString('en-US', {minimumFractionDigits:d, maximumFractionDigits:d}) : '—'; }
  async function j(u){ var r = await fetch(u + (u.indexOf('?') < 0 ? '?t=' : '&t=') + Math.floor(Date.now() / 60000)); if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }
  var COL = {WAIT:'#8a93b8', WATCH:'#e0a100', SETUP:'#2a7de1', TRIGGERED:'#2a7de1', CONFIRMED:'#1a9f5a', INVALIDATED:'#c0392b', EXPIRED:'#8a93b8'};
  function chip(st){ return '<span style="display:inline-block;padding:2px 9px;border-radius:999px;font-weight:700;font-size:12px;color:#fff;background:' + (COL[st] || '#8a93b8') + '">' + esc(st) + '</span>'; }
  function card(a, S, px){
    var h = '<div class="card"><h3 class="dp-h">' + a[1] + ' <span style="font-weight:400;opacity:.7">' + (px != null ? num(px, a[0] === 'XAG' ? 3 : 2) : '') + '</span></h3>';
    if(!S){ return h + '<p class="dp-p">The ' + a[1] + ' bot has not written a record yet. It runs every 15 minutes; check back shortly.</p></div>'; }
    var r = S.read || {}, v = r.volatility || {}, sc = (r.scouts || {}).day || {}, t = r.trend || {};
    var age = Math.round((Date.now() - new Date(S.asof).getTime()) / 60000);
    h += '<p class="dp-p">Trend: 15m <b>' + esc((t['15m'] || {}).state) + '</b> · 1h <b>' + esc((t['1h'] || {}).state) + '</b> · 4h <b>' + esc((t['4h'] || {}).state) + '</b> · day <b>' + esc((t['1d'] || {}).state) + '</b><br>'
      + 'Volatility: <b>' + esc(v.regime) + '</b> · typical day range ' + esc(v.day_range_pct_median) + '%'
      + (typeof sc.p_big_move === 'number' ? ' · chance of a big move in 4 h: <b>' + Math.round(sc.p_big_move * 100) + '%</b>' : '') + '</p>';
    ['day', 'swing', 'hold'].forEach(function(k){ var H = (S.horizons || {})[k]; if(!H) return;
      h += '<details style="margin:6px 0"><summary style="cursor:pointer">' + ({day:'Day trades', swing:'Swing (days)', hold:'Holding'})[k] + ' ' + chip(H.state) + (H.direction ? ' <b>' + esc(H.direction) + '</b>' : '') + '</summary><p class="dp-p">' + esc(H.plain) + '</p><ul class="dp-p">' + (H.reasons || []).map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></details>'; });
    var oc = S.open_calls || [];
    h += oc.length ? '<p class="dp-p"><b>Open calls:</b></p><ul class="dp-p">' + oc.map(function(c){ return '<li>' + esc(c.rule) + ' (grade ' + esc(c.grade) + ', ' + esc(c.status) + '): ' + esc(String(c.side || '').toUpperCase()) + ' entry ' + esc(c.entry) + ' stop ' + esc(c.stop) + ' target ' + esc(c.target) + '</li>'; }).join('') + '</ul>'
                   : '<p class="dp-p" style="opacity:.75">No open call. The bot stays quiet until a tested rule fires.</p>';
    h += '<p class="dp-p" style="opacity:.6;font-size:12px">Bot record ' + (age < 120 ? age + ' min' : Math.round(age / 60) + ' h') + ' old · source ' + esc(S.data_source) + (age > 90 ? ' · <b>stale</b>: the cloud scheduler skipped runs' : '') + '</p></div>';
    return h;
  }
  async function load(){
    var box = document.getElementById('desksBody'); if(!box) return;
    var px = {}; try{ (await j(FAPI + '/fapi/v1/ticker/price')).forEach(function(x){ px[x.symbol] = +x.price; }); }catch(e){}
    var out = '<div class="grid2">';
    for(var i = 0; i < A.length; i++){ var S = null; try{ S = await j(RAW + 'assets/' + A[i][0] + '.json'); }catch(e){} out += card(A[i], S, px[A[i][2]] != null ? px[A[i][2]] : (S && S.read ? S.read.price : null)); }
    out += '</div>';
    try{ var r = await fetch(RAW + 'alerts/outbox.md?t=' + Math.floor(Date.now() / 60000)); if(r.ok){ var tx = await r.text(); var parts = tx.split('\n## ').slice(-4).reverse();
      out += '<div class="card"><h3 class="dp-h">Latest alerts sent</h3>' + parts.map(function(p){ return '<pre style="white-space:pre-wrap;font:inherit;margin:8px 0;padding:8px;border-radius:8px;background:rgba(127,127,127,.08)">' + esc(p.trim()) + '</pre>'; }).join('') + '</div>'; } }catch(e){}
    out += '<div class="card"><h3 class="dp-h">How to read this</h3><p class="dp-p"><b>WAIT</b>: nothing to do. <b>WATCH</b>: a big move is likely in the next hours; in tests the 4-hour range roughly doubled in WATCH windows, but the direction could not be predicted. <b>SETUP / TRIGGERED / CONFIRMED</b>: a rule that passed its test is calling a trade (paper first). Evidence for every rule is on the Evidence page.</p></div>';
    box.innerHTML = out;
  }
  window.addEventListener('load', function(){ load(); setInterval(function(){ var s = document.getElementById('page-desks'); if(s && s.classList.contains('on')) load(); }, 120000); });
})();
</script>
"""
a = s.rindex("</body>")
s = s[:a] + js + "\n" + s[a:]
open(p, "w", encoding="utf-8").write(s)
print("patched", len(s))
# bottom bar: six tabs
s2 = open(p, encoding="utf-8").read()
s2 = s2.replace(".bar{position:fixed;left:0;right:0;bottom:0;z-index:30;background:var(--paper);border-top:1px solid var(--border);display:grid;grid-template-columns:repeat(5,1fr)", ".bar{position:fixed;left:0;right:0;bottom:0;z-index:30;background:var(--paper);border-top:1px solid var(--border);display:grid;grid-template-columns:repeat(6,1fr)")
open(p, "w", encoding="utf-8").write(s2)
