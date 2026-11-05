"""v6.5.56: the 2019–2023 (round 5) result for the funding-carry rule; honest risk wording; forward fall limit 60%."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ FUNDING CARRY, WEEKLY (v6.5.55)'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('carryxs.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep("one rule passed (funding carry) out of six rounds</h2>", "no rule passed every test; funding carry came closest</h2>")
rep("    { round:'5', tried:'every frozen rule above on Jan 2019 \\u2013 Sep 2023, data never used', result:'waiting for the older-history file.' } ];",
    "    { round:'5', tried:'every frozen rule above (14) on Jan 2019 \\u2013 Sep 2023, data never used, the same 25 coins', result:'none passed (bar z \\u2265 2.69). Funding carry came closest: +98% a year, z 2.27, but it fell 48% (Oct 2020 \\u2013 Jan 2021). Next best: volatility-managed trend, +24% a year, z 1.88.' } ];")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.55 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.55 ' + sep + ' build ' + old + ' UTC', 'v6.5.56 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.56 · build' in s and 'v6.5.55 · build' not in s and 'v6.5.55 \\u00b7 build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
