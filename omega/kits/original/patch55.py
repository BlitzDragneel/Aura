"""v6.5.55: the frozen funding-carry rule (carry-xs-7d) as a paper strategy; outside-research record brought up to date."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
# 1. module, after the older-history module
mod = open('carryxs.js', encoding='utf-8').read()
rep('</body>', mod + '\n</body>')
# 2. its card at the top of the OMEGA Strategy page
rep('    <div id="page-ostrat" class="page">\n      <div id="portfolioCard"></div>', '    <div id="page-ostrat" class="page">\n      <div id="carryxsCard"></div>\n      <div id="portfolioCard"></div>')
# 3. report field
rep("outsideResearch: safe(function(){ return window.OMEGA_OUTSIDE ? window.OMEGA_OUTSIDE.record() : null; }) || null,",
    "outsideResearch: safe(function(){ return window.OMEGA_OUTSIDE ? window.OMEGA_OUTSIDE.record() : null; }) || null, carryRule: safe(function(){ return window.OMEGA_CARRYXS ? window.OMEGA_CARRYXS.report() : null; }) || null,")
# 4. a research job (shares the research lane fairly) and a compressed store
rep("var RESEARCH_JOBS = ['lab','backtests','explore','portfolio','workshop',", "var RESEARCH_JOBS = ['lab','backtests','explore','portfolio','workshop','carryxs',")
rep("omega_xs_v1:1, omega_workshop_v1:1,", "omega_xs_v1:1, omega_workshop_v1:1, omega_carryxs_v1:1,")
# 5. outside-research record: the later rounds
rounds = """  REC.rounds = [
    { round:'2', tried:'120 variants: round 1 again, plus CREED\\u2019s sweep-and-reclaim rebuilt as a rule, low volatility, pairs against BTC, BTC and ETH only, intraday momentum, limit-order (maker) execution', result:'6 candidates and their blend; none passed on 2026 (bar z \\u2265 2.45). Fading a sweep of yesterday\\u2019s high or low lost about 36% a year in both 2024 and 2025, mostly to fees.' },
    { round:'3', tried:'8 variants: the opposite of the sweep (trade with the poke, or with a close beyond yesterday\\u2019s high or low)', result:'none qualified on 2024\\u201325.' },
    { round:'4', tried:'6 funding variants: carry across markets, crowding reversal, funding-filtered trend, market-wide crowding', result:'carry-xs-7d chosen on 2024\\u201325 and PASSED on 2026: +106% a year, z 2.88 against a bar of 2.58, +99% with costs doubled. Now a frozen paper strategy (the card at the top of this page).' },
    { round:'6', tried:'12 low-turnover variants judged against buy-and-hold (volatility timing, BTC against altcoins, volatility-scaled trend)', result:'none beat buy-and-hold in every year of 2024\\u201325.' },
    { round:'5', tried:'every frozen rule above on Jan 2019 \\u2013 Sep 2023, data never used', result:'waiting for the older-history file.' } ];
"""
rep("  function el(id){ return document.getElementById(id); }\n  function esc(s){ return String(s==null?'':s).replace(/[&<>\"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]; }); }\n  function fmt(v){ return v == null ? '\\u2014' : (v >= 0 ? '+' : '') + v.toFixed(1) + '% a year'; }",
    rounds + "  function el(id){ return document.getElementById(id); }\n  function esc(s){ return String(s==null?'':s).replace(/[&<>\"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]; }); }\n  function fmt(v){ return v == null ? '\\u2014' : (v >= 0 ? '+' : '') + v.toFixed(1) + '% a year'; }")
rep("<h2 style=\"color:var(--gold);\">Outside research, ' + esc(REC.date) + ' \\u2014 no edge survived</h2>'",
    "<h2 style=\"color:var(--gold);\">Outside research, ' + esc(REC.date) + ' \\u2014 one rule passed (funding carry) out of six rounds</h2><p class=\"hint\" style=\"margin-top:0;\"><b>Round 1</b> (below): no edge survived.</p>'")
rep("Deviations from the plan, disclosed: ' + REC.deviations.map(esc).join(' ') + '</p></div>'; }",
    "Deviations from the plan, disclosed: ' + REC.deviations.map(esc).join(' ') + '</p>' +\n      '<div style=\"overflow-x:auto;margin-top:8px;\"><table class=\"creed-events\"><thead><tr><th>Later round (plan written first)</th><th>Result</th></tr></thead><tbody>' + REC.rounds.map(function(r){ return '<tr><td><b>' + esc(r.round) + '</b> \\u00b7 ' + esc(r.tried) + '</td><td>' + esc(r.result) + '</td></tr>'; }).join('') + '</tbody></table></div></div>'; }")
# 6. version stamp
now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.54 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.54 ' + sep + ' build ' + old + ' UTC', 'v6.5.55 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.55' in s and ('v6.5.54 · build' not in s) and ('v6.5.54 \\u00b7 build' not in s)
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
