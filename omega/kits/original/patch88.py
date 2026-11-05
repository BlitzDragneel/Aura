"""v6.5.88: a Research files card on the Breakout Desk saves the daily history of the 25 studied coins from the wide data
store (for plan E10), and can fetch the coins the store lacks. Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ AUTOPILOT COVERAGE (v6.5.87)'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('rdl.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<div id="goldhBody"></div>', '<div id="goldhBody"></div>\n      <div id="rdlBody"></div>')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.87 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.87 ' + sep + ' build ' + old + ' UTC', 'v6.5.88 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.88 · build' in s and 'v6.5.87 · build' not in s and s.count('window.OMEGA_RDL = ') == 1 and s.count('id="rdlBody"') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
