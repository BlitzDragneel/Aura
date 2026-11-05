"""v6.5.76: round 15's first family (the harvest's ranking window) in the record, the built-in knowledge and the harvest
card; the harvest's recent years on 140 coins and the fall in BTC's own funding shown where the harvest is shown."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
# 1. built-in knowledge
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
# 2. the research record: round 15
i = s.index("    { round:'CREED', tried:'Your CREED replays"); j = s.index('\n', i)
line = s[i:j]; assert line.endswith("' } ];"), line[-40:]
r15 = ("    { round:'15', tried:'The funding harvest on Binance ranked on 7, 14 or 60 days of funding instead of 30 (140 coins, 2020 \\u2013 Oct 2026); "
       "and the harvest on Bybit, on whichever venue pays more, and half on each (waiting for the Bybit download)', "
       "result:'No ranking window beat 30 days: 7 days \\u22124.1% a year against it, 14 days \\u22122.0%, 60 days +1.0% (z 1.62 against a bar of 2.39). "
       "On these 140 coins the 10-coin harvest made +47% in 2021 and +12% in 2024, but +0.7% in 2025 and \\u22121.8% in 2026 so far; BTC\\u2019s own funding fell from about 12% a year in 2024 to 5% in 2025 and 2% so far in 2026. "
       "The Bybit test runs once the download is in.' }")
s = s[:j - len(' ];')] + ',\n' + r15 + ' ];' + s[j:]
# 3. the harvest card: where it stands now
a = "'. Worth running for the boom years, not as a steady income.</p>';"
rep(a, "'. Worth running for the boom years, not as a steady income.</p>' +\n"
       "      '<p class=\"hint\" style=\"color:var(--amber);\"><b>Round 15 (19 Oct 2026):</b> on all 140 validation coins the 10-coin version made +47% in 2021 and +12% in 2024, but +0.7% in 2025 and \\u22121.8% in 2026 so far. BTC\\u2019s own funding fell from about 12% a year in 2024 to 5% in 2025 and 2% so far in 2026, so there is less to collect. "
       "Ranking on 7, 14 or 60 days instead of 30 did not help (7 and 14 days earned 2\\u20134% a year less; 60 days 1% more, z 1.62, below the bar of 2.39), so the rule stays as frozen. Whether Bybit pays more is tested on the Round 15 download.</p>';")
# 4. the Edge Lab's count of earlier studies now covers rounds 14, 15 and CREED (2,208 rules in all: 600 + 105 + about 1,500)
rep("earlier studies (rounds 1–11, the outside study and the other assistants’ tests: about 1,300 more configurations)",
    "earlier studies (rounds 1–15, CREED, the outside study and the other assistants’ tests: about 1,500 more configurations)")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.75 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.75 ' + sep + ' build ' + old + ' UTC', 'v6.5.76 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.76 · build' in s and 'v6.5.75 · build' not in s and s.count("{ round:'15',") == 1 and '"built":"2026-10-19"' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
