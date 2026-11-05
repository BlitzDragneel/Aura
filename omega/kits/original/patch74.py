"""v6.5.74: round 14's final tests. The capitulation rule FAILED on 324 untouched coins: the watch shows it, is off by
default and only records. CREED's variants and exits, and the outside Asian-session dip, go into the record and the
built-in knowledge."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
i = s.index('<script>/* ═══ CAPITULATION WATCH'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('capwatch.js', encoding='utf-8').read().rstrip('\n') + s[j:]
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
rep("result:'1 rule passed validation: buying a coin after a fall of 5+ of its own hourly standard deviations while its perpetual trades at an unusual discount, held 12 hours (+19% a year over the market on 140 coins, z 3.04). Its final test needs untouched hourly data (the download below). The model across coins made +37.8% a year over the market on 125 untouched coins (z 2.89) but missed the strict bar of 3.29, so it is judged on new weeks. Everything else failed.' }",
    "result:'1 rule passed validation: buying a coin after a fall of 5+ of its own hourly standard deviations while its perpetual trades at an unusual discount, held 12 hours (+19% a year over the market on 140 coins, z 3.04). It FAILED its final test on 324 untouched coins (\\u22121.5% a year, z \\u22120.27; 2025 \\u221227%). The model across coins made +37.8% a year over the market on 125 untouched coins (z 2.89) but missed the strict bar of 3.29, so it is judged on new weeks. Another assistant\\u2019s Asian-session dip failed (z 0.56 week by week). No new edge.' }")
rep("result:'Setups shown on time made +0.015R a trade before costs and \\u22120.085R after (2,497 setups): no edge. The +0.47R headline came from setups shown hours later but priced at the earlier close. Three take-profit tiers (+0.001R) and breakeven off (+0.057R) change nothing.' }",
    "result:'Setups shown on time made +0.015R a trade before costs and \\u22120.085R after (2,497 setups): no edge. The +0.47R headline came from setups shown hours later but priced at the earlier close. Re-run with CREED\\u2019s own code on 15-minute data (3,268 on-time setups): every entry version (longs only, capitulation sweeps, perpetual at a discount, shorts only) and every exit (no breakeven \\u22120.091R with 18% wins, breakeven at 2R, targets at 2R or 1.5R) lost after costs.' }")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.73 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.73 ' + sep + ' build ' + old + ' UTC', 'v6.5.74 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.74 · build' in s and 'v6.5.73 · build' not in s and "var STATUS = 'FAILED';" in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
