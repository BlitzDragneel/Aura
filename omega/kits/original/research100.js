<script>/* ═══ WHY SIGNALS ARE RARE — the research record E22–E28 (v6.5.100) ═══
   A card on the Signals and Edge Lab pages that says plainly what has been tested on Binance's own archive (every USDT
   perpetual, delisted coins included, real costs and funding), what survived and why the rest failed. Static text: it changes
   only when a new test is run and written down. */
(function(){
  'use strict';
  var ROWS = [
    ['PASSED', 'var(--bull)', 'Panic bounce H1 and H3 (E22, E25)', 'Buy after a coin’s 24-hour fall lands in its own worst 10% (H1, with a limit order 2σ lower) or when a fifth of the market panics together (H3). With the 143 delisted coins put back: H1 +0.32% a trade (t 4.54), H3 +0.30% (t 4.08), positive in 2024, 2025 and 2026. Grade B: still unconfirmed by a forward record, and it lives on the big rebounds.'],
    ['FAILED', 'var(--bear)', 'H1 as a 100 USDT account (E26)', '5 or 10 USDT seats with a −10% stop, 2021 → Oct 2026: drawdowns of 56% and 59%, gains in only 4 of 6 years; 2021 made most of it and 2026 is negative. Keep it on paper.'],
    ['FAILED', 'var(--bear)', 'The daily-trading search (E28): 9,240 rules', 'Built on 2021–2023, checked on 2024 and against luck (the same search on shuffled signals). Nothing survived:'],
    ['', '', '· Small coins over big, funding carry', 'The two best of 8,660 tries: +0.15% a day on 2021–2023 as a daily portfolio. In 2024 all five versions went to about zero or below (drops of 27–45%). Both were 2021–22 effects, fading by 2023.'],
    ['', '', '· Next-day direction, 31 measures', 'Up to 15 settings per measure made money before costs and lost it after. Daily direction is close to random; costs win.'],
    ['', '', '· Daily dip-buying limit orders', 'Deep dips (2σ) held two days were positive every year but came on only 28% of days. Forced daily, it becomes market risk, and random coins with the same orders did as well.'],
    ['', '', '· Hour-of-day timing', 'The biggest average hourly moves are 0.03–0.09%; a round trip costs 0.12–0.20%.']
  ];
  function html(){
    var h = '<div class="card" style="margin-bottom:14px;"><h2>Why signals are rare — what has been tested</h2>' +
      '<p class="hint" style="margin:0 0 10px;color:var(--text);">OMEGA only raises a signal when a rule that passed a fair test fires. <b>No rule that trades every day has passed</b>: 9,240 were tried. The edges that hold up come in rare moments (panics), and forcing them to trade daily dilutes them to nothing. On most days the right move is to do nothing, and that is the app working, not broken.</p>' +
      ROWS.map(function(r){ var sub = !r[0];
        return '<div style="padding:8px 0;border-top:1px solid var(--border);' + (sub ? 'margin-left:14px;' : '') + '">' +
          (r[0] ? '<span style="display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;padding:2px 7px;border-radius:4px;margin-right:8px;color:' + r[1] + ';border:1px solid ' + r[1] + ';white-space:nowrap;">' + r[0] + '</span>' : '') +
          '<b>' + r[2].replace(/^· /, '') + '</b><div class="hint" style="margin-top:4px;color:var(--text);">' + r[3] + '</div></div>'; }).join('') +
      '<p class="hint" style="margin:8px 0 0;">Data: Binance’s archive, 903 USDT perpetuals incl. 163 delisted, real funding, costs 0.10% a side. Paper only. Next ideas not yet run: BTC/ETH timing from market-wide funding and breadth; H1/H3 on every perpetual, not only the 40 most-traded (more coins, more panics).</p></div>';
    return h; }
  var HOSTS = [['rareSigBody', 'panicSigBody'], ['rareBody', 'panicBody']];
  function css(){ if(document.getElementById('pbCss')) return; var st = document.createElement('style'); st.id = 'pbCss'; st.textContent = '.pb-tab{width:100%;border-collapse:collapse;font-size:13px;margin:6px 0;}.pb-tab th{text-align:left;color:var(--text-dim);font-weight:600;border-bottom:1px solid var(--border);padding:4px;}.pb-tab td{padding:4px;border-bottom:1px solid var(--border);vertical-align:top;white-space:normal;overflow-wrap:anywhere;}'; document.head.appendChild(st); }
  function wire(){ HOSTS.forEach(function(p){ var after = document.getElementById(p[1]); if(after && !document.getElementById(p[0])){ var d = document.createElement('div'); d.id = p[0]; d.innerHTML = html(); after.parentNode.insertBefore(d, after.nextSibling); } }); return HOSTS.every(function(p){ return document.getElementById(p[0]); }); }
  var n = 0, iv = setInterval(function(){ css(); if(wire() || ++n > 120) clearInterval(iv); }, 1000);
  window.OMEGA_RARE = { html:html, rows:ROWS };
})();
</script>
