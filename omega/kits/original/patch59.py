"""v6.5.59: the funding harvest (passed its untouched test on 51 fresh coins) as a frozen paper strategy; carry relabelled
'not an edge' after failing both untouched tests; the desk shows the fresh-coin results and a BTC/ETH panel."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
def swap(start, new):
    global s
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
swap('<script>/* ═══ FUNDING CARRY, WEEKLY (v6.5.55', open('carryxs.js', encoding='utf-8').read())
swap('<script>/* ═══ POSITIONING DESK (v6.5.58)', open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip()))
assert '__STATIC__' not in s
rep('</body>', open('harvest.js', encoding='utf-8').read() + '\n</body>')
rep('      <div id="carryxsCard"></div>\n', '      <div id="harvestCard"></div>\n      <div id="carryxsCard"></div>\n')
rep("'portfolio','workshop','carryxs',", "'portfolio','workshop','carryxs','harvest',")
rep("omega_carryxs_v1:1,", "omega_carryxs_v1:1, omega_harvest_v1:1,")
rep("carryRule: safe(function(){ return window.OMEGA_CARRYXS ? window.OMEGA_CARRYXS.report() : null; }) || null,",
    "carryRule: safe(function(){ return window.OMEGA_CARRYXS ? window.OMEGA_CARRYXS.report() : null; }) || null, harvestRule: safe(function(){ return window.OMEGA_HARVEST ? window.OMEGA_HARVEST.report() : null; }) || null,")
rep("no rule passed every test; funding carry came closest</h2>", "one rule passed an untouched test: the funding harvest</h2>")
m = re.search(r"\{ round:'5', tried:[^}]*\} \];", s); assert m
s = s[:m.end() - 3] + ",\n    { round:'7', tried:'on 51 coins never used (Jan 2020 \\u2013 Oct 2026): carry, carry over 8 coins, funding harvest, and 14-day trend (added after)', result:'the funding harvest PASSED: +12.0% a year, z 4.14 against 2.13, worst fall \\u22122.3% (now a frozen paper strategy). Carry (+50%, z 1.70, worst fall \\u221283%), carry over 8 (+33%, z 1.39) and trend (+39%, z 1.58, \\u221265%) failed.' } ];" + s[m.end():]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.58 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.58 ' + sep + ' build ' + old + ' UTC', 'v6.5.59 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.59 · build' in s and 'v6.5.58 · build' not in s and 'v6.5.58 \\u00b7 build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
