"""v6.5.121: Signal Lab on the Desks page. CREED's engine is byte-identical.
 Under the three desks a "Signal Lab" card shows the cloud bots' event alerts and paper signals on 15 markets
 (bot-state/siglab/signals.json, a public record; no token needed): market state at the signal, entry / stop / TP1,
 the result and the written reason once closed, a scoreboard by setup and market, and which cells are muted because
 they lost on past data. Information only.
usage: python3 patch121.py <v6.5.120> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


rep('      <div id="desksBody"></div>\n', '      <div id="desksBody"></div>\n      <div id="sigLabBody"></div>\n')
rep("      drawSafe(p, function(){ if(p === 'desks' && window.OMEGA_DESKS) window.OMEGA_DESKS.onShow(); });\n",
    "      drawSafe(p, function(){ if(p === 'desks' && window.OMEGA_DESKS) window.OMEGA_DESKS.onShow(); });\n"
    "      drawSafe(p, function(){ if(p === 'desks' && window.OMEGA_SIGLAB) window.OMEGA_SIGLAB.onShow(); });\n")

JS = r'''<script>/* ═══ SIGNAL LAB (v6.5.121) ═══ reads the public record of the cloud Signal Lab; information only */
(function(){
  var RAW = 'https://raw.githubusercontent.com/BlitzDragneel/Aura/bot-state/siglab/signals.json';
  var NM = {S1:'trend pullback', S2:'breakout', S3:'stretch fade', S4:'fib pullback', S5:'session drive', S6:'daily bias', S7:'big move'};
  var last = 0;
  function esc(x){ return String(x == null ? '' : x).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function sg(v){ return (v >= 0 ? '+' : '') + v; }
  function draw(L){
    var box = document.getElementById('sigLabBody'); if(!box) return;
    if(!L){ box.innerHTML = '<div class="card"><h3>Signal Lab</h3><p class="sa-msg">The Signal Lab record could not be loaded right now. It is written by the cloud bots every 15 minutes.</p></div>'; return; }
    var rec = L.record || {}, all = rec.all || {}, T = rec.by_setup_market || {}, C = L.record_by_context || {};
    var rows = Object.keys(T).filter(function(k){ return T[k].n > 0; }).sort(function(a, b){ return (T[b].avg_R || 0) - (T[a].avg_R || 0); });
    var sigs = (L.signals || []).slice(-40).reverse();
    var h = '<div class="card"><h3>Signal Lab</h3><p class="sa-msg">Alerts fire when a breakout, big move, pullback or session drive happens on 15 markets. Every signal is scored in money and gets a written reason when it closes. PAPER = untested, do not trade. A setup earns PROMISING after 15 closed signals with a positive average and CONFIDENT after 30 clearly positive ones. Setups that lost on past data are sent without a trade plan.</p>'
      + '<div class="sa-stats"><div><b>' + (all.n || 0) + '</b><span>closed</span></div><div><b>' + (all.avg_R != null ? sg(all.avg_R) + 'R' : '—') + '</b><span>average</span></div><div><b>' + (all.win != null ? Math.round(all.win * 100) + '%' : '—') + '</b><span>won</span></div><div><b>' + (rec.open || 0) + '</b><span>open now</span></div></div>';
    if(rows.length) h += '<details><summary>Scoreboard by setup and market</summary>' + rows.map(function(k){ var v = T[k], q = k.split(' '); return '<div class="sa-sub">' + esc(NM[q[1]] || q[1]) + ' · ' + esc(q[0]) + ': ' + v.n + ' closed, ' + sg(v.avg_R) + 'R, ' + Math.round((v.win || 0) * 100) + '% won · <b>' + esc(v.grade) + '</b></div>'; }).join('') + '</details>';
    var ck = Object.keys(C).filter(function(k){ return C[k].n >= 3; });
    if(ck.length) h += '<details><summary>What it has learned (by market state)</summary>' + ck.map(function(k){ var q = k.split(' | '); return '<div class="sa-sub">' + esc(NM[q[0]] || q[0]) + ', ' + esc(q[1]) + ': ' + C[k].n + ' closed, ' + sg(C[k].avg_R) + 'R</div>'; }).join('') + '</details>';
    h += sigs.map(function(x){ var d = new Date(x.logged_ms), st = x.state || {}, cls = x.status === 'closed' ? 'closed' : 'running';
      return '<div class="sa-sig"><div class="sa-top"><b>' + esc(x.symbol) + ' ' + esc(String(x.side).toUpperCase()) + ' · ' + esc(NM[x.setup] || x.setup) + '</b><span class="sa-st ' + cls + '">' + esc(x.status) + '</span></div>'
        + '<div class="sa-sub">' + d.toLocaleString([], {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}) + ' · entry ~' + esc(x.ref_price) + ' · stop ' + esc(x.stop) + ' · TP1 ' + esc((x.targets || [])[0]) + ' · TP5 ' + esc((x.targets || [])[4])
        + (st.trend ? '<br>Market then: trend ' + esc(st.trend) + ', volatility ' + esc(st.vol) + ', ' + esc(st.session) + ' session' : '') + ' · ' + esc(x.grade_at_issue || 'PAPER') + (x.sent ? '' : ' · logged only') + '</div>'
        + (x.status === 'closed' ? '<div class="sa-res"><span class="' + (x.R_ladder > 0 ? 'sa-win' : (x.R_ladder < 0 ? 'sa-loss' : '')) + '">' + esc(x.outcome) + ' ' + sg(x.R_ladder) + 'R</span>' + (x.review ? ' — ' + esc(x.review) : '') + '</div>' : '') + '</div>'; }).join('')
      + (sigs.length ? '' : '<p class="sa-msg">No signals yet.</p>') + '</div>';
    box.innerHTML = h;
  }
  function load(){ last = Date.now();
    fetch(RAW + '?t=' + Math.floor(Date.now() / 60000)).then(function(r){ if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }).then(draw).catch(function(){ draw(null); }); }
  function onShow(){ if(Date.now() - last > 60000) load(); }
  window.OMEGA_SIGLAB = { onShow:onShow, draw:draw, load:load };
})();
</script>
'''
rep('</body>', JS + '</body>')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.120 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.120 ' + sep + ' build ' + o + ' UTC', 'v6.5.121 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.121 · build' in s and 'v6.5.120 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
