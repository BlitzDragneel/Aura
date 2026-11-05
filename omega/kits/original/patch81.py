"""v6.5.81: round 18, checking another assistant's report. Its order-flow rule failed on the 165 coins it never used, and
the 2026 harvest income on new listings came only from coins with no Binance spot market: the harvest card, the research
record and the knowledge say so."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
rep("almost all from coins listed since April 2025 (older coins: +5% and \\u22122%). Many of those new coins may have no Binance spot market to hold, which the harvest needs, so this is a question for the next round, not a rule.</p>",
    "almost all from coins listed since April 2025 (older coins: +5% and \\u22122%). <b>Checked (round 18):</b> all of that came from new listings that have <b>no Binance spot market</b>, so they cannot be hedged on Binance. On the 81 new listings that do have spot, the harvest made \\u22122% to \\u22123% a year. New coins also charge shorts heavily in their first weeks. Nothing to add here.</p>")
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
i = s.index("    { round:'17', tried:"); j = s.index('\n', i); line = s[i:j]; assert line.endswith("' } ];"), line[-30:]
r18 = ("    { round:'18', tried:'Another assistant\\u2019s report: an order-flow rule (rank coins by their 7-day share of aggressive buying; long the top fifth, short the bottom fifth, weekly), found on the final-test coins; and its study of new listings', "
       "result:'The order-flow rule made +47% a year where it was found and FAILED on the 165 coins it never used (+5.3%, t 0.72; negative with costs doubled). Its new-listing findings hold: shorts pay funding in a coin\\u2019s first weeks, and the harvest on new listings with a Binance spot market earns about nothing after fees.' }")
s = s[:j - len(' ];')] + ',\n' + r18 + ' ];' + s[j:]
rep("earlier studies (rounds 1–17, CREED,", "earlier studies (rounds 1–18, CREED,")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.80 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.80 ' + sep + ' build ' + old + ' UTC', 'v6.5.81 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.81 · build' in s and 'v6.5.80 · build' not in s and s.count("{ round:'18',") == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
