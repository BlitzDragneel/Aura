"""v6.5.63: round 9 (a different strategy per coin, picked walk-forward on 166 coins) on the desk and in the research record. Not an edge."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def swap(start, new):
    global s
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
swap('<script>/* ═══ POSITIONING DESK (v6.5.58', open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip()))
m = re.search(r"\{ round:'8', tried:[^}]*\} \];", s); assert m
s = s[:m.end() - 3] + ",\n    { round:'9', tried:'a different strategy for each coin: every quarter, each of 166 coins got the best of nine strategies on its last two years, then traded the next quarter unseen', result:'not an edge: +4.4% a year better than not picking, z 1.63 against 1.96. A coin\\u2019s best strategy of one year beat its typical strategy the next year in only 40% of 705 coin-years. The picker mostly picks the coin harvest (123 of 166 coins).' } ];" + s[m.end():]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.62 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.62 ' + sep + ' build ' + old + ' UTC', 'v6.5.63 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.63 · build' in s and 'v6.5.62 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
