"""v6.5.100: 'Why signals are rare' — the research record E22–E28 as a card on the Signals and Edge Lab pages (under the
panic-bounce card). Nothing else changed."""
import sys, re, datetime, os
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
mod = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'research100.js'), encoding='utf-8').read().strip()
assert 'WHY SIGNALS ARE RARE' not in s
i = s.index('<script>/* ═══ PANIC BOUNCE (v6.5.98'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + mod + s[j:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.99 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.99 ' + sep + ' build ' + o + ' UTC', 'v6.5.100 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.100 · build' in s and 'v6.5.99 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
