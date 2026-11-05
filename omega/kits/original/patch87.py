"""v6.5.87: the Autopilot runs everything. Registers the climax watch, Breakout Desk, Market Profiles' record, Market Watch's
recorder and the gold/silver download as Operator jobs (as the older research modules already do). Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ MARKET PROFILES (v6.5.85'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('autocov.js', encoding='utf-8').read().rstrip('\n') + s[j:]
r25 = ("    { round:'25', tried:'Not a research round: a check of what the Autopilot actually runs (v6.5.87)', "
       "result:'The Operator ran 20 built-in jobs plus 7 registered by the research modules, but not the five newest parts (climax watch, Market Watch, Breakout Desk, gold download, Market Profiles\\u2019 record), which ran on their own timers. All five now register as Operator jobs, so one switch runs everything.' }")
rep("Shown on each Market Profile.' } ];", "Shown on each Market Profile.' },\n" + r25 + " ];")
rep('Research record, rounds 1\\u201324 \\u2014', 'Research record, rounds 1\\u201325 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.86 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.86 ' + sep + ' build ' + old + ' UTC', 'v6.5.87 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.87 · build' in s and 'v6.5.86 · build' not in s and s.count('window.OMEGA_AUTOCOV = ') == 1 and s.count("{ round:'25',") == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
