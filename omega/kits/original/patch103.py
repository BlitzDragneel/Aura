"""v6.5.103: research card row for E33 (forced deleveraging on 60 coins: FAIL). Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()
A = "    ['FAILED', 'var(--bear)', 'Neural network (E32)',"
assert s.count(A) == 1
s = s.replace(A, "    ['FAILED', 'var(--bear)', 'Forced deleveraging on 60 coins (E33)', 'E30’s best lead, frozen and run on 60 coins it had never seen (Oct 2023 → Sep 2026, 2,063 events): an hour down 5%+ with open interest down 1%+, bought and held 4 hours: −0.03% a trade (t −0.10). +0.39% in 2024, −0.74% in 2025, −0.47% in 2026. Forced selling did 0.26% better than ordinary 5% falls, but neither makes money: single events lost 28–36% in 4 hours. The panic bounce H1 held up where this did not because it waits for a limit 2σ lower and holds a day.'],\n" + A)
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.102 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.102 ' + sep + ' build ' + o + ' UTC', 'v6.5.103 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.103 · build' in s and 'v6.5.102 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
