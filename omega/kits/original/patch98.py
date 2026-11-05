"""v6.5.98: the panic-bounce watch (plan E22's H1 and H3, grade B; survivorship test E25 passed), the same rules and code as
OMEGA Prime's watch, adapted to this build (localStorage key omega_panic_v1, the original's cards, Autopilot job 'panic').
It is shown under the climax reversal on the Signals, Edge Lab and Watch pages. Nothing else changed."""
import sys, re, datetime, os
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
mod = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'panic98.js'), encoding='utf-8').read().strip()
assert 'PANIC BOUNCE (v6.5.98)' not in s, 'already patched'
i = s.index('<script>/* ═══ CLIMAX REVERSAL (v6.5.78)'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + mod + s[j:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.97 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.97 ' + sep + ' build ' + o + ' UTC', 'v6.5.98 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.98 · build' in s and s.count('PANIC BOUNCE (v6.5.98)') == 1 and 'v6.5.97 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
