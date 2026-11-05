"""v6.5.102 (also: the E28 count corrected to 12,480 with round 5's row): CREED reality check at the top of the CREED desk (CREED's method unchanged) + research card rows for E29, E31
(CREED), E30 (real liquidity) and E32 (neural network). Nothing else changed."""
import sys, re, datetime, os
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read(); here = os.path.dirname(os.path.abspath(__file__))
mod = open(os.path.join(here, 'creedcheck102.js'), encoding='utf-8').read().strip()
assert 'CREED REALITY CHECK' not in s
i = s.index('<script>/* ═══ WHY SIGNALS ARE RARE'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + mod + s[j:]
R0 = "E13 needs 5 days with the live streams working (the backup has no liquidations).']\n  ];"
assert s.count(R0) == 1
s = s.replace(R0, """E13 needs 5 days with the live streams working (the backup has no liquidations).'],
    ['FAILED', 'var(--bear)', 'CREED, fixed and improved (E29, E31)', 'After a CREED setup price behaves like a fair coin (+1R before the stop 49%, random 50%). As taught: −0.118R, −0.100R and −0.118R a trade on three separate coin sets (about 11,000 setups). Longs only after BTC fell, longs only in market panics, and a volatility-scaled stop buffer all failed on coins CREED had never seen. CREED stays as taught; its desk now shows this.'],
    ['FAILED', 'var(--bear)', 'Real liquidity (E30)', 'Order-book depth (13,690 coin-days, 2023–2026): the heavier or thinner side does not predict direction (best of 18: −0.14% a trade in 2025–26), and a thin book barely predicts size. Forced deleveraging (price −5% in an hour with open interest −1%, long 4 h): +0.75% a trade before 2024 and +0.83% in 2024, but only 72 events on 10 coins (t 0.99): same direction as the panic bounce, too rare to prove here. Fading crowded positioning failed.'],
    ['FAILED', 'var(--bear)', 'Neural network (E32)', 'Six networks learned next-day moves of the 100 most-traded coins from 33 measures (2021–23), the best chosen on 2024 (t 1.02): 2025–26 −0.10% a day, drawdown 68%. It had learned to short coins whose funding shorts must pay.']
  ];""")
for x, y in [("'The daily-trading search (E28): 9,240 rules'", "'The daily-trading search (E28): 12,480 rules'"), ("<b>No rule that trades every day has passed</b>: 9,240 were tried.", "<b>No rule that trades every day has passed</b>: 12,480 were tried.")]:
    assert s.count(x) == 1, x; s = s.replace(x, y)
H0 = "    ['', '', '· Hour-of-day timing',"
assert s.count(H0) == 1
s = s.replace(H0, "    ['', '', '· Timing BTC and ETH from market-wide gauges', 'Funding, breadth, dispersion, momentum and volatility (15 gauges, 3,240 rules, round 5): the same gauges shifted in time (luck) did as well (best real t 2.55 against luck 2.53); rules in the market most days had drawdowns of 46–82%.'],\n" + H0)
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.101 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.101 ' + sep + ' build ' + o + ' UTC', 'v6.5.102 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.102 · build' in s and 'v6.5.101 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
