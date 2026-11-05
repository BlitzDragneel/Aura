"""v6.5.94: Events ahead under Market now (from the Market Clock's official calendar) with an event-risk warning, the same
warning in the pre-trade check, and the Monthly review on the Risk Guard page. The Growth Bot's rules are unchanged."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ RISK GUARD AND GROWTH BOT (v6.5.92)'); j = s.index('</script>', i) + len('</script>'); s = s[:i] + open('rguard94.js', encoding='utf-8').read().rstrip('\n') + s[j:]
i = s.index('<script>/* ═══ MARKET COCKPIT (v6.5.93)'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + open('review.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<div id="dplanAnaBody"></div>\n      <div id="cockpitBody"></div>', '<div id="dplanAnaBody"></div>\n      <div id="evAnaBody"></div>\n      <div id="cockpitBody"></div>')
rep('<div id="dplanBody"></div>', '<div id="dplanBody"></div>\n      <div id="evBody"></div>')
rep('<div id="rguardBody"><p class="hint">Loading…</p></div>', '<div id="rguardBody"><p class="hint">Loading…</p></div>\n      <div id="reviewBody"></div>')
r33 = ("    { round:'33', tried:'Not a test: Events ahead and the Monthly review (v6.5.94) \\u2014 the next US inflation and Fed releases from the Market Clock\\u2019s official calendar under Market now, a warning from 2 hours before to 1 hour after each, the same warning in the pre-trade check, and a month-by-month review of the Growth Bot, the Daily Plan and the owner\\u2019s trades', "
       "result:'Advice and record-keeping only: the Growth Bot\\u2019s rules stay as plan E17 fixed them, and the review is computed from the records, never edited.' }")
k2 = s.index("{ round:'32',"); e2 = s.index("' } ];", k2) + len("' }"); s = s[:e2] + ",\n" + r33 + s[e2:]
rep('Research record, rounds 1\\u201332 \\u2014', 'Research record, rounds 1\\u201333 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.93 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.93 ' + sep + ' build ' + old + ' UTC', 'v6.5.94 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.94 · build' in s and s.count('window.OMEGA_REVIEW = ') == 1 and s.count('id="reviewBody"') == 1 and s.count('id="evAnaBody"') == 1 and "{ round:'33'," in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
