"""v6.5.61: download 90 new coins (none in any earlier test, Jan 2021 to now) for the final test of the round-8 strategies."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read(); assert s.count('</body>') == 1
s = s.replace('</body>', open('fresh2export.js', encoding='utf-8').read() + '\n</body>')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.60 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.60 ' + sep + ' build ' + old + ' UTC', 'v6.5.61 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.61 · build' in s and 'v6.5.60 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
