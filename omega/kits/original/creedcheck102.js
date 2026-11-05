<script>/* ═══ CREED REALITY CHECK (v6.5.102) — what CREED's setups have actually done, measured three times ═══
   CREED's own method, levels, gates and exits are unchanged (byte-identical). This card only reports, at the top of the CREED
   desk, what its on-time setups did when the app's own CREED engine was replayed on history (research E29, E31, Oct 2026):
   20 majors 2020–2026 (5,053 setups), 30 untouched coins (3,122) and 30 more untouched coins (2,802), 0.06% a side. */
(function(){
  'use strict';
  var HIT = [['+1R', 50, 49], ['+2R', 33, 32], ['+3R', 25, 24], ['target ~5R', 17, 17.5]];
  function chart(){ var W = 340, rowH = 34, h = 26 + HIT.length*rowH, x0 = 92, sc = (W - x0 - 40)/60, o = '';
    o += '<svg viewBox="0 0 ' + W + ' ' + h + '" style="width:100%;max-width:440px;height:auto;display:block;margin:6px 0 4px;" role="img" aria-label="CREED hit rates against a fair coin">';
    o += '<text x="' + x0 + '" y="12" style="font:600 10px system-ui;fill:var(--text-dim)">reached before the stop (%)</text>';
    HIT.forEach(function(r, i){ var y = 22 + i*rowH;
      o += '<text x="0" y="' + (y + 13) + '" style="font:600 11px system-ui;fill:var(--text)">' + r[0] + '</text>';
      o += '<rect x="' + x0 + '" y="' + y + '" width="' + (r[1]*sc).toFixed(1) + '" height="11" rx="3" fill="var(--border)"/><text x="' + (x0 + r[1]*sc + 4).toFixed(1) + '" y="' + (y + 9) + '" style="font:10px system-ui;fill:var(--text-dim)">coin flip ' + r[1] + '%</text>';
      o += '<rect x="' + x0 + '" y="' + (y + 13) + '" width="' + (r[2]*sc).toFixed(1) + '" height="11" rx="3" fill="var(--gold)"/><text x="' + (x0 + r[2]*sc + 4).toFixed(1) + '" y="' + (y + 22) + '" style="font:600 10px system-ui;fill:var(--gold)">CREED ' + r[2] + '%</text>'; });
    return o + '</svg>'; }
  function html(){
    return '<div class="card" id="creedReality" style="margin:0 0 14px;border-color:var(--gold);"><h2 style="color:var(--gold);">CREED reality check — read this before a setup</h2>' +
      '<p style="margin:0 0 8px;"><span class="es-chip">MEASURED: NO EDGE AFTER COSTS</span></p>' +
      '<p class="hint" style="margin:0 0 6px;color:var(--text);">After a CREED setup, price behaves like a fair coin: it reaches +1R before the stop about as often as a coin flip would, and the same at 2R, 3R and the target.</p>' + chart() +
      '<p class="hint" style="margin:6px 0 8px;color:var(--text);"><b>Result per trade after costs (0.06% a side):</b> −0.118R on 20 majors (2020–2026, 5,053 setups), −0.100R on 30 coins it had never seen, −0.118R on 30 more. Before costs it is about zero; its tight stops make costs about 0.12R a trade.</p>' +
      '<p class="hint" style="margin:0 0 8px;"><b>Why it sometimes wins:</b> its 3–7R targets pay big on about 1 trade in 10, so winning streaks happen, mostly in strong trends (2020–21). <b>Why it loses:</b> the sweep and acceptance carry no information about direction, so the many −1R stops and the costs outweigh the rare targets.</p>' +
      '<p class="hint" style="margin:0 0 8px;"><b>Tried, all failed:</b> no breakeven, breakeven at 2R, 1.5R and 2R targets, longs only, shorts only, the 5-unit method, pyramiding, trailing, only against BTC’s last 24 hours, only during market panics, a stop buffer scaled to volatility. Moving stops and targets cannot create an edge from a coin flip.</p>' +
      '<p class="hint" style="margin:0;color:var(--text);"><b>What that means for you:</b> treat a CREED “Ready” as a picture of the chart, not as odds in your favour. If you trade it, size it as a bet you expect to lose slowly. The rules that passed fair tests are the panic bounce (H1/H3) and the climax reversal, on the Signals page.</p></div>'; }
  function wire(){ var pg = document.getElementById('page-creed'); if(!pg || document.getElementById('creedReality')) return !!pg;
    var ban = pg.querySelector('.creed-banner'), d = document.createElement('div'); d.innerHTML = html();
    if(ban && ban.parentNode) ban.parentNode.insertBefore(d.firstChild, ban.nextSibling); else pg.insertBefore(d.firstChild, pg.firstChild); return true; }
  var n = 0, iv = setInterval(function(){ if(wire() || ++n > 120) clearInterval(iv); }, 1000);
  window.OMEGA_CREEDCHECK = { html:html, hit:HIT };
})();
</script>
