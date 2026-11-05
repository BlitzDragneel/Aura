"""v6.5.78: round 16's result. The climax reversal (a fall of 3+ hourly standard deviations on 3x+ volume that closes in
the top 40% of the hour; buy, hold 12 hours) passed screen, validation and its final test on 324 untouched coins: it
goes on paper, watched hourly on every Binance coin perpetual (top of the Edge Lab and on Market Watch). Research record
and built-in knowledge gain round 16."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
# 1. the watch, right after the capitulation watch
i = s.index('<script>/* ═══ CAPITULATION WATCH'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('climax.js', encoding='utf-8').read().rstrip('\n') + s[j:]
# 2. built-in knowledge
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
# 3. the research record: round 16
i = s.index("    { round:'15', tried:"); j = s.index('\n', i); line = s[i:j]; assert line.endswith("' } ];"), line[-30:]
r16 = ("    { round:'16', tried:'The footprints of big buying and selling on hourly perpetual bars: absorption, exhaustion after a dip, flow divergence at a low, a leverage flush completing, stop runs reclaimed, "
       "spot-led and leverage-led breakouts and the climax wick; 18 rules, each against the same setup without the footprint; screened on 25 coins, validated on 140, final test once on 324 untouched coins', "
       "result:'1 rule PASSED all three: the climax reversal (a fall of 3+ hourly standard deviations on 3\\u00d7+ volume that closes in the top 40% of the hour; buy at the next open, hold 12 hours). "
       "Final test: +5.3% a year over the market, z 2.35 against a bar of 2.33, +4.6% with costs doubled, 440 trades averaging +1.8% before costs. Now on paper (Edge Lab). "
       "The rest failed the screen or did not beat the plain setup.' }")
s = s[:j - len(' ];')] + ',\n' + r16 + ' ];' + s[j:]
rep("earlier studies (rounds 1–15, CREED,", "earlier studies (rounds 1–16, CREED,")
rep("result:'1 rule passed validation: buying a coin after a fall of 5+ of its own hourly standard deviations",
    "result:'(Round 16 later found the first rule to pass all three stages: the climax reversal, below.) 1 rule passed validation: buying a coin after a fall of 5+ of its own hourly standard deviations")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.77 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.77 ' + sep + ' build ' + old + ' UTC', 'v6.5.78 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.78 · build' in s and 'v6.5.77 · build' not in s and s.count('window.OMEGA_CLIMAX = ') == 1 and s.count("{ round:'16',") == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
