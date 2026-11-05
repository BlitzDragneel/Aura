"""v6.5.96: the data check (every Autopilot job fresh or late, current candles, futures price against the spot index), the
Growth Bot against holding BTC, and the bot under worse fills. The bot now keeps each closed trade's size (rules unchanged)."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
rep("A.closed.push({ key:o.key, src:o.src, sym:o.sym, side:o.side, pnl:Math.round(pnl*1e4)/1e4, R:Math.round(pnl/o.risk*1000)/1000, at:nowMs });",
    "A.closed.push({ key:o.key, src:o.src, sym:o.sym, side:o.side, pnl:Math.round(pnl*1e4)/1e4, R:Math.round(pnl/o.risk*1000)/1000, nt:Math.round(o.notional*100)/100, at:nowMs });   // v6.5.96: size kept for the fill stress test")
i = s.index('<script>/* ═══ MARKET COCKPIT (v6.5.93)'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + open('truth.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<div id="page-analysis" class="page">\n      <div id="dplanAnaBody"></div>', '<div id="page-analysis" class="page">\n      <div id="truthBody"></div>\n      <div id="dplanAnaBody"></div>')
rep('<div id="rguardBody"><p class="hint">Loading…</p></div>', '<div id="rguardBody"><p class="hint">Loading…</p></div>\n      <div id="truthRgBody"></div>')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.95 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.95 ' + sep + ' build ' + old + ' UTC', 'v6.5.96 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.96 · build' in s and s.count('window.OMEGA_TRUTH = ') == 1 and 'nt:Math.round(o.notional*100)/100' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
