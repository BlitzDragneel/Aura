"""v6.5.86: Market Profiles gain 'Both directions' (plan E7: how each market falls and rises, squeezes and crashes, the long
and short side of every tested rule, four short-only rules — none passed). Research record round 24. Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ MARKET PROFILES (v6.5.85)'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('mprof86.js', encoding='utf-8').read().rstrip('\n') + s[j:]
r24 = ("    { round:'24', tried:'Plan E7: both directions on the six markets \\u2014 rising vs falling hours, tails, swings, squeezes and crashes, volatility after drops vs rises; the long and short side of plan E5\\u2019s two-sided rules; four short-only rules (blow-off, failed breakout, downtrend US hours, breakdown in a downtrend), chosen on 2020\\u20132023 and judged once on 2024\\u20132026', "
       "result:'No short-only rule passed on any market, and the short sides held up no better than the long sides. Movement is close to symmetric (about half the hours up; average up hour equals average down hour); DOGE\\u2019s sharpest hours are spikes up, LTC\\u2019s and gold\\u2019s are drops; big hours in both directions mostly come in US hours. Shown on each Market Profile.' }")
rep("The profiles are on the new Market Profiles page.' } ];", "The profiles are on the new Market Profiles page.' },\n" + r24 + " ];")
rep('Research record, rounds 1\\u201323 \\u2014', 'Research record, rounds 1\\u201324 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.85 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.85 ' + sep + ' build ' + old + ' UTC', 'v6.5.86 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.86 · build' in s and 'v6.5.85 · build' not in s and s.count('window.OMEGA_MPROF = ') == 1 and s.count("{ round:'24',") == 1 and 'DATA2:DATA2' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
