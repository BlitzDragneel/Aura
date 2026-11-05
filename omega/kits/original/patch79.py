"""v6.5.79: round 17, what moves the market. A market clock on Market Watch (when moves happen, the CPI/FOMC/expiry/CME
calendar ahead with what research found about each), flight recordings tagged with scheduled events, the climax card
explains what it really catches, and the research record and knowledge gain round 17."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
def swap(marker, path):
    global s
    i = s.index('<script>/* ═══ ' + marker); j = s.index('</script>', i) + len('</script>')
    s = s[:i] + open(path, encoding='utf-8').read().rstrip('\n') + s[j:]
# 1. updated modules
swap('MARKET WATCH', 'watch.js'); swap('CLIMAX REVERSAL', 'climax.js')
# 2. the market clock, after Market Watch
clock = open('clock.js', encoding='utf-8').read().replace('__CLOCK__', open('clock_data.json', encoding='utf-8').read().strip())
i = s.index('<script>/* ═══ MARKET WATCH'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + clock.rstrip('\n') + s[j:]
# 3. knowledge and the research record
k0 = s.index('var KN = '); k1 = s.index('\n', k0); assert s[k0:k1].endswith(';')
s = s[:k0] + 'var KN = ' + open('knowledge.min.json', encoding='utf-8').read().strip() + ';' + s[k1:]
i = s.index("    { round:'16', tried:"); j = s.index('\n', i); line = s[i:j]; assert line.endswith("' } ];"), line[-30:]
r17 = ("    { round:'17', tried:'What moves the market, described on 165 coins (hourly, 2020 \\u2013 Oct 2026): how much of a move is the market, whether buying and selling predict the next hours, the busiest hours, the US CPI and FOMC hours, options expiry, the CME weekend, what follows big moves, and why the climax rule works', "
       "result:'About 60% of a coin\\u2019s hourly move is the whole market and about 6% its own aggressive flow. Moves cluster at 13\\u201316 UTC and 00 UTC. CPI and FOMC hours move 1.3\\u00d7 and 1.9\\u00d7 a normal hour. No options-expiry effect and no CME gap fill. "
       "After sudden market-wide falls the market rebounded +0.8% in a day, which is what the climax rule rides. Description only; three hypotheses are left for forward testing.' }")
s = s[:j - len(' ];')] + ',\n' + r17 + ' ];' + s[j:]
rep("earlier studies (rounds 1–16, CREED,", "earlier studies (rounds 1–17, CREED,")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.78 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.78 ' + sep + ' build ' + old + ' UTC', 'v6.5.79 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.79 · build' in s and 'v6.5.78 · build' not in s and s.count('window.OMEGA_MARKETCLOCK = ') == 1 and '__CLOCK__' not in s and s.count("{ round:'17',") == 1 and 'What it really catches (round 17)' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
