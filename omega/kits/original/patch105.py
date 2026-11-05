"""v6.5.105: research card rows for E35 (new-listing fade) and E36 (pairs mean reversion), both FAIL. Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()
A = "    ['FAILED', 'var(--bear)', 'Funding harvest, delta-neutral (E34)',"
assert s.count(A) == 1
s = s.replace(A, "    ['FAILED', 'var(--bear)', 'New-listing fade (E35)', 'Short newly listed perpetuals 3 days after launch for 30 days with a +50% stop (823 listings, costs scaled to each coin’s liquidity). The typical trade wins (median +13.5%) but squeezes take it back: before 2025 +2.6% a trade (t 1.10); 2025–26 +2.5% (t 1.02), 2026 negative, worst −76%, negative without the best 5% of trades.'],\n    ['FAILED', 'var(--bear)', 'Pairs mean reversion (E36)', 'Short the rich leg and buy the cheap leg of the 20 most correlated pairs among the 30 most-traded coins when they pull apart, until they reconverge. Best of 12 before 2025: +1.8% a year (t 0.50, luck reached 0.78); 2025–26 −2.1% a year. The pairs drift apart for real more often than they snap back.'],\n" + A)
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.104 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.104 ' + sep + ' build ' + o + ' UTC', 'v6.5.105 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.105 · build' in s and 'v6.5.104 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
