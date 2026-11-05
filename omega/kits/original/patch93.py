"""v6.5.93: the Market Cockpit on the Analysis page (candles with US hours, volume by aggressive side, liquidity levels on the
price axis, the order book's depth column, the Daily Plan's zones, a strip of the key figures, one setup card); Autopilot job."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ RISK GUARD AND GROWTH BOT (v6.5.92)'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + open('cockpit.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<div id="page-analysis" class="page">\n      <div id="dplanAnaBody"></div>', '<div id="page-analysis" class="page">\n      <div id="dplanAnaBody"></div>\n      <div id="cockpitBody"></div>')
rep("drawSafe(p, function(){ if((p === 'mread' || p === 'analysis') && window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); });", "drawSafe(p, function(){ if((p === 'mread' || p === 'analysis') && window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); });\n      drawSafe(p, function(){ if(p === 'analysis' && window.OMEGA_COCKPIT) window.OMEGA_COCKPIT.onShow(); });")
r32 = ("    { round:'32', tried:'Not a test: the Market Cockpit on the Analysis page (v6.5.93) \\u2014 one clean chart per coin with US hours, volume split by aggressive buying and selling, liquidity levels on the price axis, the order book in its own column, the Daily Plan\\u2019s entry, stop and target zones, and a strip of the key figures', "
       "result:'A view, not a signal: it reads Market Read\\u2019s levels and the Daily Plan without changing them, and the Autopilot keeps it fresh hourly.' }")
k2 = s.index("{ round:'31',"); e2 = s.index("' } ];", k2) + len("' }"); s = s[:e2] + ",\n" + r32 + s[e2:]
rep('Research record, rounds 1\\u201331 \\u2014', 'Research record, rounds 1\\u201332 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.92 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.92 ' + sep + ' build ' + old + ' UTC', 'v6.5.93 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.93 · build' in s and s.count('window.OMEGA_COCKPIT = ') == 1 and s.count('id="cockpitBody"') == 1 and "{ round:'32'," in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
