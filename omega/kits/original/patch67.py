"""v6.5.67: round 10 (the perpetuals' own data) and round 11 (forex) results. The funding harvest passed a third untouched
test with the basis counted; nothing else passed. Harvest card: measured basis, recent thin years, delisting rule and a
flag for a held coin whose funding stops. Desk: round 10 and 11 cards. Research record: rounds 10 and 11."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def swap(start, new):
    global s
    assert s.count(start) == 1, start
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
swap('<script>/* ═══ FUNDING HARVEST (v6.5.59', open('harvest.js', encoding='utf-8').read())
swap('<script>/* ═══ POSITIONING DESK (v6.5.58', open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip()))
m = re.search(r"\{ round:'9', tried:[^}]*\} \];", s); assert m
s = s[:m.end() - 3] + (",\n    { round:'10', tried:'the perpetuals\\u2019 own data (premium index, futures buyers, BTC/ETH open interest and long/short ratios) and the basis, designed on the 25 coins, tested once on 140 other coins (and BTC/ETH 2025\\u201326)', "
  "result:'the 10-coin funding harvest passed a third untouched test with the perpetual\\u2019s own price counted (+11.9% a year, z 4.28); its premium filter adds nothing reliable. The basis costs about 0.05% a year on the 25 coins. Every direction rule from futures data failed (fade the crowd: +7.5% a year on 2025\\u201326 but z 1.03 against 2.13). Lessons: the harvest\\u2019s income has thinned since 2025, and a pair must be closed when its perpetual is delisted.' },"
  "\n    { round:'11', tried:'forex: carry, 3-month trend, a trend blend and carry with trend on nine currency pairs and gold, daily, 2009\\u20132026, with central-bank rates', "
  "result:'all four failed (carry +2.1% a year, z 1.41, worst fall \\u221220%; trend about \\u22121% a year). Missing forex data was not the reason for the lack of success.' } ];") + s[m.end():]
rep("the funding harvest passed untouched tests twice; nothing else did", "the funding harvest passed untouched tests three times; nothing else did")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.66 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.66 ' + sep + ' build ' + old + ' UTC', 'v6.5.67 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.67 · build' in s and 'v6.5.66 · build' not in s and "round:'11'" in s and 'untouched tests, twice' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
