"""v6.5.90: the app no longer sticks (the Autopilot stopped forcing Market Watch's full recording on), Market Profiles add
BTC, ETH, SOL, BNB, XRP (plan E14), the research download adds the five forex majors (plan E15), record round 29."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
def swap(head, file):
    global s
    i = s.index(head); j = s.index('</script>', i) + len('</script>'); s = s[:i] + open(file, encoding='utf-8').read().rstrip('\n') + s[j:]
swap('<script>/* ═══ AUTOPILOT COVERAGE (v6.5.87)', 'autocov90.js')
swap('<script>/* ═══ GOLD HOURLY HISTORY (v6.5.84, v6.5.85)', 'goldh90.js')
swap('<script>/* ═══ MARKET PROFILES (v6.5.85, v6.5.86)', 'mprof90.js')
i = s.index('var KN = '); j = s.index(';\n', i); KN = json.loads(s[i + 9:j])
for r, nm, v in [("E14", "The top 5 coins one by one (BTC, ETH, SOL, BNB, XRP): profiles, who trades them when, eleven rules", "no rule passed on any of the five; the US-hours drift seen in gold and altcoins does not hold for BTC, ETH or XRP"),
                 ("E15", "The five forex majors one by one (EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD)", "waiting for the hourly forex download (v6.5.90)")]:
    if r not in {e.get('r') for e in KN['earlier']}: KN['earlier'].append({'r':r, 'name':nm, 'v':v})
s = s[:i + 9] + json.dumps(KN, ensure_ascii=False, separators=(',', ':')) + s[j:]
r29 = ("    { round:'29', tried:'Plan E14: the top 5 coins one by one (BTC, ETH, SOL, BNB, XRP; hourly 2020\\u20132026) \\u2014 profiles, who trades them when, both directions, and eleven rules (seven two-sided, four short-only) chosen on 2020\\u20132023 and judged once on 2024\\u20132026; plan E15 (forex majors) written', "
       "result:'No rule passed on any of the five. US hours carry the most trading (36\\u201342%) and the biggest moves; aggressive buying is 49\\u201350% in every session; the US-hours drift down seen in gold and the altcoins does not hold for BTC, ETH or XRP. Also v6.5.90: the Autopilot no longer forces Market Watch\\u2019s full recording on, which made phones stick.' }")
k2 = s.index("{ round:'28',"); e2 = s.index("' } ];", k2) + len("' }"); s = s[:e2] + ",\n" + r29 + s[e2:]
rep('Research record, rounds 1\\u201328 \\u2014', 'Research record, rounds 1\\u201329 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.89 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.89 ' + sep + ' build ' + old + ' UTC', 'v6.5.90 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.90 · build' in s and "{ round:'29'," in s and "'EUR/USD', 'GBP/USD'" in s and "if(!c.on) return 'Off:" in s and "'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'XAUUSD'" in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
