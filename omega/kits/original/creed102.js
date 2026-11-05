<script>/* ═══ WHY CREED DOES NOT WIN — the diagnosis (plans E29, E30; v6.5.102) ═══
   A card under the CREED desk's banner. CREED's rules are unchanged (byte-identical, as taught); this explains its record.
   Source: the app's own CREED engine replayed on 15-minute candles — 20 majors 2020 → Oct 2026 (5,053 setups shown on time)
   and 30 coins it had never been run on, Oct 2023 → Sep 2026 (3,122 setups). Static text and figures. */
(function(){
  'use strict';
  var BARS = [['+1R', 50, 49], ['+2R', 33, 32], ['+3R', 25, 24], ['target (~5R)', 17, 17.5]];
  function chart(){
    var W = 340, H = 168, x0 = 10, w = (W - 20)/BARS.length, s = '<svg viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;max-width:440px;height:auto;display:block;margin:4px 0 10px;" role="img" aria-label="CREED versus a coin flip">';
    BARS.forEach(function(b, i){ var cx = x0 + i*w, base = 128, k = 1.9;
      s += '<rect x="' + (cx + w*0.14) + '" y="' + (base - b[1]*k) + '" width="' + (w*0.32) + '" height="' + (b[1]*k) + '" rx="3" fill="var(--text-dim)" opacity="0.55"/>';
      s += '<rect x="' + (cx + w*0.52) + '" y="' + (base - b[2]*k) + '" width="' + (w*0.32) + '" height="' + (b[2]*k) + '" rx="3" fill="var(--gold)"/>';
      s += '<text x="' + (cx + w*0.30) + '" y="' + (base - b[1]*k - 4) + '" text-anchor="middle" style="font:600 10px system-ui;fill:var(--text-dim)">' + b[1] + '%</text>';
      s += '<text x="' + (cx + w*0.68) + '" y="' + (base - b[2]*k - 4) + '" text-anchor="middle" style="font:700 10px system-ui;fill:var(--gold)">' + b[2] + '%</text>';
      s += '<text x="' + (cx + w/2) + '" y="' + (base + 15) + '" text-anchor="middle" style="font:600 11px system-ui;fill:var(--text)">' + b[0] + '</text>'; });
    s += '<rect x="12" y="152" width="10" height="10" rx="2" fill="var(--text-dim)" opacity="0.55"/><text x="27" y="161" style="font:11px system-ui;fill:var(--text-dim)">a fair coin (no edge)</text>';
    s += '<rect x="160" y="152" width="10" height="10" rx="2" fill="var(--gold)"/><text x="175" y="161" style="font:11px system-ui;fill:var(--text-dim)">CREED (5,053 setups)</text></svg>';
    return s; }
  function html(){
    return '<div class="card" style="margin:0 0 14px;border-color:var(--gold);"><h2 style="color:var(--gold);">Why CREED does not win — the honest test</h2>' +
      '<p class="hint" style="margin:0 0 6px;color:var(--text);">How often price reached each level before CREED’s stop, compared with a fair coin flip. They are the same: after a CREED setup, price moves as if there were no setup.</p>' + chart() +
      '<p class="hint" style="margin:0 0 6px;color:var(--text);"><b>As taught it makes +0.003R a trade before costs and −0.118R after</b> (5,053 setups shown on time, 20 major coins, 2020 → Oct 2026; 11% winners). On 30 coins it had never been run on: −0.100R.</p>' +
      '<details style="margin:4px 0 0;"><summary class="hint" style="cursor:pointer;color:var(--text);"><b>Why — and what was tried</b></summary>' +
      '<p class="hint" style="margin:8px 0 6px;">• <b>No direction in the pattern.</b> The sweep and acceptance do not tilt the odds. Moving the stop, the target or the breakeven cannot create an edge from a fair coin; it only reshapes the bets — which is why every exit change tried (no breakeven, 1.5R and 2R targets, the 5-unit method, pyramiding, trailing) failed.</p>' +
      '<p class="hint" style="margin:0 0 6px;">• <b>Costs eat it.</b> The stop sits just beyond the sweep’s wick with a small fixed buffer, so fees and slippage cost 0.12R a trade on average (0.3–0.5R on the tightest stops).</p>' +
      '<p class="hint" style="margin:0 0 6px;">• <b>It rarely trades real liquidity.</b> 99% of setups are pokes at the 1-hour pullback zone; the 52 true 4-hour liquidity sweeps lost (−0.49R before costs).</p>' +
      '<p class="hint" style="margin:0 0 6px;">• <b>Why it sometimes wins.</b> Big targets (+4.7R on about 11% of trades) give long winning streaks, mostly in trending years (2020–21). The one helpful condition was market context: longs after BTC had fallen 1–3% (+0.12R before costs).</p>' +
      '<p class="hint" style="margin:0 0 6px;">• <b>The improvement, tested fairly (plan E29).</b> “CREED longs only, after BTC fell 1% / 2%”, written down first and run once on the 30 untouched coins: −0.04R and −0.06R. Holding the same coin for the same time did about as well: CREED’s pattern added nothing.</p>' +
      '<p class="hint" style="margin:0 0 6px;">• <b>Real liquidity (plan E30).</b> 3¾ years of Binance order-book depth: the book’s imbalance does not predict direction after costs, and a thin book barely predicts size. Fading crowded positioning failed. Price drops with open interest falling (forced selling) rebounded in both periods but too rarely on 10 coins to stand alone — the same effect as the panic bounce.</p>' +
      '<p class="hint" style="margin:0 0 0;"><b>What has held up</b> is the panic bounce on the Signals page: buying forced, market-wide selling. CREED stays as taught; trade it on paper only.</p></details></div>'; }
  function wire(){ var pg = document.getElementById('page-creed'); if(!pg || document.getElementById('creedWhyBody')) return !!pg;
    var ban = pg.querySelector('.creed-banner'), d = document.createElement('div'); d.id = 'creedWhyBody'; d.innerHTML = html();
    if(ban && ban.parentNode) ban.parentNode.insertBefore(d, ban.nextSibling); else pg.insertBefore(d, pg.firstChild); return true; }
  var n = 0, iv = setInterval(function(){ if(wire() || ++n > 60) clearInterval(iv); }, 1000);
  window.OMEGA_CREEDWHY = { html:html };
})();
</script>
