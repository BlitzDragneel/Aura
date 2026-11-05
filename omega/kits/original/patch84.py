"""v6.5.84: plan E1's result and the next clean test. The Breakout Desk marks setups A and B as FAILED (a one-shot test fixed
in advance on 2021–2023: A 100 → 49.1, B 27.2, worse than most coin-flip accounts); they stay on paper as a record with no
alerts. Setup A's 180.5 is corrected (it came from Binance's 5 USDT minimum rounding trades above 1% risk; ×1.08 at a true 1%).
New: a gold and silver hourly history download (Twelve Data, resumable, checked, research format) for plan E2.
Research record gains round 20."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
# 1. the desk module, replaced whole; the gold download right after it
i = s.index('<script>/* ═══ BREAKOUT DESK (v6.5.83)'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('bdesk84.js', encoding='utf-8').read().rstrip('\n') + '\n' + open('goldh.js', encoding='utf-8').read().rstrip('\n') + s[j:]
# 2. the page: the gold card under the desk; the banner says what the setups are now
rep('<div id="bdeskBody"><p class="hint">Loading…</p></div>', '<div id="bdeskBody"><p class="hint">Loading…</p></div>\n      <div id="goldhBody"></div>')
rep('<span>— two candidates on paper, your 5-unit plan on the chart</span>', '<span>— both setups FAILED a clean test (record only); next test: gold hourly</span>')
# 3. research record: round 20
r20 = ("    { round:'20', tried:'Outside study, 20 Oct: trade management searched as 7 parts (entry, stop, adding, profit in parts, exit, time limit, protection), all 1,944 combinations on 12 entries (23,328 one-market accounts at a true 1% risk); a new method built from the parts that helped in the first half; then plan E1, written and fingerprinted first, ran the three candidates once on 2021\\u20132023', "
       "result:'Picking the best combination on the first half failed (the top 10 went from 500\\u2013640 to 43\\u201386 on the unseen half). Helped in both halves: a limit retest entry and a 3 ATR stop; adding on strength hurt. Correction: setup A\\u2019s 180.5 came from Binance\\u2019s 5 USDT minimum rounding 238 of 623 trades above 1% risk (\\u00d71.08 at a true 1%). "
       "The new method made 100 to 125 on the unseen half (worst fall 18%; beat 97% of coin-flip accounts). Plan E1 on 2021\\u20132023: A 100 to 49.1, B 27.2, the new method 71.4: all FAILED. A and B are marked failed on the Breakout Desk. Next: plan E2 on gold hourly (download added).' }")
rep("CREED is unchanged.' } ];", "CREED is unchanged.' },\n" + r20 + " ];")
rep('Research record, rounds 1\\u201319 \\u2014', 'Research record, rounds 1\\u201320 \\u2014')
# 4. version
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.83 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.83 ' + sep + ' build ' + old + ' UTC', 'v6.5.84 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.84 · build' in s and 'v6.5.83 · build' not in s and s.count('window.OMEGA_GOLDH = ') == 1 and s.count('window.OMEGA_BDESK = ') == 1 and s.count("{ round:'20',") == 1 and s.count('id="goldhBody"') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
