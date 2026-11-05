"""v6.5.83: the Breakout Desk. Two candidates from the 19–20 Oct edge hunt (done outside the app) go on paper: the 72-hour
breakout in US hours managed with the owner's 5-unit method, and the momentum burst with pyramiding. Each is played as a
live paper account (one market at a time, Binance rules, 1% risk), its signal and plan drawn on an hourly chart, with a
calculator for any account size. Not an edge: judged only on weeks after 20 Oct 2026 03:00 UTC. Research record gains
round 19 (the outside study). Nothing existing is changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
# 1. the module, right after the climax watch (it reads the climax watch's hourly store)
i = s.index('<script>/* ═══ CLIMAX REVERSAL'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('bdesk.js', encoding='utf-8').read().rstrip('\n') + s[j:]
# 2. navigation: under OMEGA Signals
rep('<li data-page="osig" onclick="navigate(\'osig\')"><span class="sb-icon">◎</span> OMEGA Signals <span class="sb-badge" id="sbBadge-osig"></span></li>',
    '<li data-page="osig" onclick="navigate(\'osig\')"><span class="sb-icon">◎</span> OMEGA Signals <span class="sb-badge" id="sbBadge-osig"></span></li>\n'
    '      <li data-page="bdesk" onclick="navigate(\'bdesk\')"><span class="sb-icon">⇡</span> Breakout Desk <span class="sb-badge" id="sbBadge-bdesk"></span></li>')
# 3. the page
page = ('<div id="page-bdesk" class="page">\n'
        '      <div class="creed-banner intel-banner">\n'
        '        <div class="creed-banner-glow"></div>\n'
        '        <div class="creed-banner-main">\n'
        '          <div class="creed-banner-kicker">Ω OMEGA · BREAKOUT DESK</div>\n'
        '          <h2 class="creed-banner-title">Breakout Desk <span>— two candidates on paper, your 5-unit plan on the chart</span></h2>\n'
        '          <div class="creed-banner-flow"><i>US-hours setup</i><b>→</b><i>Next open</i><b>→</b><i>5 units</i><b>→</b><i>Bank 3 at +1R</i><b>→</b><i>Add as it runs</i></div>\n'
        '        </div>\n'
        '      </div>\n'
        '      <div id="bdeskBody"><p class="hint">Loading…</p></div>\n'
        '    </div>\n'
        '    <div id="page-osig" class="page">')
rep('<div id="page-osig" class="page">', page)
rep("var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig',", "var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','bdesk',")
rep("drawSafe(p, function(){ if(p === 'osig' && window.OMEGA_SIGNALS) window.OMEGA_SIGNALS.render(); });",
    "drawSafe(p, function(){ if(p === 'osig' && window.OMEGA_SIGNALS) window.OMEGA_SIGNALS.render(); });\n      drawSafe(p, function(){ if((p === 'bdesk' || p === 'osig') && window.OMEGA_BDESK) window.OMEGA_BDESK.render(); });")
# 4. a line on OMEGA Signals, and the command palette
rep('<div id="climaxSigBody"></div>', '<div id="climaxSigBody"></div>\n      <div id="bdeskSigBody"></div>')
rep("['osig','OMEGA Signals'],", "['osig','OMEGA Signals'],['bdesk','Breakout Desk'],")
# 5. the research record: round 19
r19 = ("    { round:'19', tried:'Outside study, 19\\u201320 Oct (not pre-registered): 792 combinations of 22 entry families, 6 filters and 6 ways to manage a trade (scaling out and pyramiding included) on 334 hourly series, chosen on Jan 2024 \\u2013 Jun 2025 and judged on Jul 2025 \\u2013 Oct 2026; the best then played as a live account (one market at a time, Binance\\u2019s rules); a coin-flip test of the direction calls; and an autopsy of what caused each trade\\u2019s result', "
       "result:'No edge proven. Two candidates went on paper (Breakout Desk): the 72-hour breakout in US hours managed with 5 units (100 to 180 USDT at 1% risk over the unseen 16 months, worst fall 31%; beat 96% of coin-flip accounts) and the momentum burst with pyramiding (100 to 144; 91%). Each was the best of 10 pairs, so luck gives a result that good about 1 time in 3; counted by week, the sweep\\u2019s finalists were chance (t about 0.5). "
       "Autopsy: 85\\u201388% of each trade\\u2019s result came after entry (the market\\u2019s move about 30%, the coin\\u2019s own about 45\\u201350%); nothing measured before entry predicted it on unseen data, except forced selling (deeper and market-wide flushes rebounded more). Trade management changes how trading feels, not whether it earns: on shuffled prices every technique lost the cost of trading. CREED with the same techniques (CREED\u2019s own engine, 4,696 on-time setups on 20 coins): as taught \u22120.01R a trade in 2020\u201323 and \u22120.11R in 2023\u201326; the 5-unit method raised winners to 44\u201348% but lowered the average (\u22120.05R, \u22120.12R); pyramiding and a trailing stop were not positive in both periods. CREED is unchanged.' }")
rep("earns about nothing after fees.' } ];", "earns about nothing after fees.' },\n" + r19 + " ];")
rep('Research record, rounds 1\\u201318 \\u2014', 'Research record, rounds 1\\u201319 \\u2014')
# 6. version
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.82 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.82 ' + sep + ' build ' + old + ' UTC', 'v6.5.83 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.83 · build' in s and 'v6.5.82 · build' not in s and s.count('window.OMEGA_BDESK = ') == 1 and s.count("{ round:'19',") == 1 and s.count('id="page-bdesk"') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
