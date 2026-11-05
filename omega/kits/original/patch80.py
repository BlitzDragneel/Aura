"""v6.5.80: round 15's Bybit test. Choosing the better-paying venue passed validation and failed its final test on 324
untouched coins; the harvest stays on Binance. The harvest card, the research record and the knowledge say so, with
where funding income came from in 2025-26 (coins listed since April 2025; described, not tested)."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
rep("Whether Bybit pays more is tested on the Round 15 download.</p>",
    "<b>Bybit (tested 19 Oct 2026):</b> shorting each coin on whichever of Binance or Bybit paid more passed on 140 coins (+5.3% a year more, t 7.4), then <b>failed</b> on 324 untouched coins (+0.7%, t 1.25 against a bar of 2.13). On those coins Bybit paid more on only 12% of days. Bybit alone and half on each did worse. The harvest stays on Binance. "
    "<b>Where funding was paid in 2025\\u201326</b> (described, not tested): on the untouched coins the plain harvest made +12% in 2025 and +27% in 2026, almost all from coins listed since April 2025 (older coins: +5% and \\u22122%). Many of those new coins may have no Binance spot market to hold, which the harvest needs, so this is a question for the next round, not a rule.</p>")
rep("The Bybit test runs once the download is in.' }",
    "Bybit, tested on 19 Oct 2026: shorting on whichever venue paid more passed on 140 coins (+5.3% a year, t 7.4) and FAILED on 324 untouched coins (+0.7%, t 1.25 against 2.13). The harvest stays on Binance.' }")
rep("and the harvest on Bybit, on whichever venue pays more, and half on each (waiting for the Bybit download)'", "and the harvest on Bybit, on whichever venue pays more, and half on each'")
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.79 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.79 ' + sep + ' build ' + old + ' UTC', 'v6.5.80 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.80 · build' in s and 'v6.5.79 · build' not in s and 'Bybit (tested 19 Oct 2026)' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
