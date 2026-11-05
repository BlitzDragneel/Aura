"""v6.5.91: the Daily Plan (market state, side per coin, plans at liquidity, followed on paper: plan E16) on Market Read and the
Analysis page; the Autopilot runs Market Watch again in light mode; record round 30. Nothing else changed."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ AUTOPILOT COVERAGE (v6.5.87, v6.5.90)'); j = s.index('</script>', i) + len('</script>'); s = s[:i] + open('autocov91.js', encoding='utf-8').read().rstrip('\n') + s[j:]
i = s.index('<script>/* ═══ MARKET READ (v6.5.89)'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + open('dplan.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<div id="mreadBody"><p class="hint">Loading…</p></div>', '<div id="dplanBody"></div>\n      <div id="mreadBody"><p class="hint">Loading…</p></div>')
rep('<div id="page-analysis" class="page">', '<div id="page-analysis" class="page">\n      <div id="dplanAnaBody"></div>')
rep('<span>— where the liquidity lies, read by the app itself</span>', '<span>— what is going on now, which side to trade, today’s plan, and where liquidity lies</span>')
rep("drawSafe(p, function(){ if(p === 'mread' && window.OMEGA_MREAD) window.OMEGA_MREAD.onShow(); });",
    "drawSafe(p, function(){ if(p === 'mread' && window.OMEGA_MREAD) window.OMEGA_MREAD.onShow(); });\n      drawSafe(p, function(){ if((p === 'mread' || p === 'analysis') && window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); });")
i = s.index('var KN = '); j = s.index(';\n', i); KN = json.loads(s[i + 9:j])
if 'E16' not in {e.get('r') for e in KN['earlier']}: KN['earlier'].append({'r':'E16', 'name':'Forward record of the Daily Plan (v6.5.91): side from the market state, entries at liquidity, grade C', 'v':'running from 22 Oct 2026; judged once after 50 paper trades or 26 weeks'})
s = s[:i + 9] + json.dumps(KN, ensure_ascii=False, separators=(',', ':')) + s[j:]
r30 = ("    { round:'30', tried:'Not a test: the Daily Plan (v6.5.91) \\u2014 market state from the top 5 coins, long, short or stand aside per coin, entries at liquidity with stop and target, followed on paper (plan E16, judged once after 50 trades or 26 weeks)', "
       "result:'Grade C, unproven: the trend and sweep rules it resembles failed fair tests; it exists so the owner can trade daily with a written plan while its forward record shows whether it works. The two things that passed fair tests remain the climax reversal and the funding harvest.' }")
k2 = s.index("{ round:'29',"); e2 = s.index("' } ];", k2) + len("' }"); s = s[:e2] + ",\n" + r30 + s[e2:]
rep('Research record, rounds 1\\u201329 \\u2014', 'Research record, rounds 1\\u201330 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.90 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.90 ' + sep + ' build ' + old + ' UTC', 'v6.5.91 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.91 · build' in s and s.count('window.OMEGA_DPLAN = ') == 1 and "c.mode = 'light'" in s and "{ round:'30'," in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
