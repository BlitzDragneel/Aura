"""v6.5.72: the capitulation watch (round 14's candidate rule, live on the research coins' perpetuals, recorded forward)."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
i = s.index('<script>/* ═══ EDGE LAB'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('capwatch.js', encoding='utf-8').read().rstrip('\n') + s[j:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.71 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.71 ' + sep + ' build ' + old + ' UTC', 'v6.5.72 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.72 · build' in s and 'v6.5.71 · build' not in s and s.count('window.OMEGA_CAPWATCH = ') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
