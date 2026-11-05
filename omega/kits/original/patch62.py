"""v6.5.62: round 8 (ten strategies, three stages): the 10-coin funding harvest passed and runs on paper beside the 5-coin one;
the desk shows the round-8 table and the lesson; research record updated."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
def swap(start, new):
    global s
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
swap('<script>/* ═══ FUNDING HARVEST (v6.5.59)', open('harvest.js', encoding='utf-8').read())
swap('<script>/* ═══ POSITIONING DESK (v6.5.58', open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip()))
assert '__STATIC__' not in s
rep("one rule passed an untouched test: the funding harvest</h2>", "the funding harvest passed untouched tests twice; nothing else did</h2>")
m = re.search(r"\{ round:'7', tried:[^}]*\} \];", s); assert m
s = s[:m.end() - 3] + ",\n    { round:'8', tried:'ten new strategies (3 structural, 4 crowding, 2 trend, 1 settlement-timing) in three stages: 25 coins, 51 coins, then 90 coins never used', result:'only the 10-coin funding harvest passed all three (+8.8% a year on the 90 new coins, z 3.38 against 2.45, worst fall \\u22124.4%); the crowding rules reversed there (\\u221220% to \\u221236% a year) and trend made about nothing. Another assistant\\u2019s BTC/ETH trend pair also failed there (about 0% a year).' } ];" + s[m.end():]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.61 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.61 ' + sep + ' build ' + old + ' UTC', 'v6.5.62 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.62 · build' in s and 'v6.5.61 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
