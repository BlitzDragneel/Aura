"""v6.5.104: research card row for E34 (delta-neutral funding harvest: FAIL). Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()
A = "    ['FAILED', 'var(--bear)', 'Forced deleveraging on 60 coins (E33)',"
assert s.count(A) == 1
s = s.replace(A, "    ['FAILED', 'var(--bear)', 'Funding harvest, delta-neutral (E34)', 'Spot long + perpetual short, collecting funding (no bet on direction), costs 0.5% a round trip. Best of 36 on 2021–24: +8.8% a year on capital, worst month −0.2%. 2025–26: −17% a year. Most months nothing paid enough; when something did it earned 1–3% a month; then one coin’s funding flipped in a crash (DEXE, June 2026: −20.8% in a day, −64.6% in a month) and erased it all. The “small amount every day” bot with a rare blow-up. The Bridge shows live funding as information only.'],\n" + A)
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.103 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.103 ' + sep + ' build ' + o + ' UTC', 'v6.5.104 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.104 · build' in s and 'v6.5.103 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
