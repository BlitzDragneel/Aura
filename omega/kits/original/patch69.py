"""v6.5.69: round 12 (600 known strategies, 100 combinations, own ideas; final test on 125 untouched coins). The two winners,
both the funding harvest plus RSI(5) dip-buying, become frozen paper strategies with daily positions as orders. The loader
passes daily highs and lows; the harvest card warns when a held coin's funding turns sharply negative. Desk card and
research record for round 12."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
def swap(start, new):
    global s
    assert s.count(start) == 1, start
    i = s.index(start); j = s.index('</script>', i) + len('</script>'); s = s[:i] + new.rstrip('\n') + s[j:]
# the loader: daily highs and lows beside the closes (new fields; nothing else reads them)
rep("var k0 = Math.round(d[0].time/86400), c = [];", "var k0 = Math.round(d[0].time/86400), c = [], hi = [], lo = [];")
rep("d.forEach(function(r){ var k = Math.round(r.time/86400) - k0; if(k >= 0) c[k] = +r.c; }); for(var i=0; i<c.length; i++) if(!(c[i] > 0)) c[i] = null;",
    "d.forEach(function(r){ var k = Math.round(r.time/86400) - k0; if(k >= 0){ c[k] = +r.c; hi[k] = +r.h; lo[k] = +r.l; } }); for(var i=0; i<c.length; i++){ if(!(c[i] > 0)) c[i] = null; if(!(hi[i] > 0)) hi[i] = null; if(!(lo[i] > 0)) lo[i] = null; }")
rep("out[s] = { k0:k0, c:c, fund:fund }; }", "out[s] = { k0:k0, c:c, h:hi, l:lo, fund:fund }; }   // v6.5.69: h, l for the round-12 Supertrend part")
swap('<script>/* ═══ FUNDING HARVEST (v6.5.59', open('harvest.js', encoding='utf-8').read())
i = s.index('<script>/* ═══ FUNDING HARVEST (v6.5.59'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('r12live.js', encoding='utf-8').read().rstrip('\n') + s[j:]
swap('<script>/* ═══ POSITIONING DESK (v6.5.58', open('posdesk.src.js', encoding='utf-8').read().replace('__STATIC__', open('desk_static.min.json').read().strip()))
m = re.search(r"\{ round:'11', tried:[^}]*\} \];", s); assert m
s = s[:m.end() - 3] + (",\n    { round:'12', tried:'600 known strategies (52 families: trend, moving averages, breakouts, RSI, Bollinger, MACD, oscillators, volume, volatility, calendar, funding, cross-sectional momentum, reversal, low volatility, size, carry, lead-lag, patterns), then 100 combinations and 5 own ideas; screened on the 25 coins, validated on 140, final test once on 125 untouched coins', "
  "result:'2 of the 100 finalists passed (bar z 3.29), both the funding harvest plus RSI(5) dip-buying: +4.0% and +4.1% a year over the market, worst falls under 4%. Carry on 1-day funding passed validation then lost (\\u221278% worst fall); trend stayed positive but unproven; everything else failed. The two winners run on paper.' } ];") + s[m.end():]
rep("the funding harvest passed untouched tests three times; nothing else did", "the funding harvest passed untouched tests three times; in round 12 it passed again only when paired with RSI(5) dip-buying")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.68 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.68 ' + sep + ' build ' + old + ' UTC', 'v6.5.69 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.69 · build' in s and 'v6.5.68 · build' not in s and s.count('ROUND 12 WINNERS (v6.5.69)') == 1 and "round:'12'" in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
