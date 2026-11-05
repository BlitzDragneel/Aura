"""v6.5.85: Market Profiles (plan E5: six markets studied one by one; plan E6: forward record of the session split), the
gold card moved on to plan E4, research record rounds 21–23. Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
i = s.index('<script>/* ═══ GOLD HOURLY HISTORY (v6.5.84)'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('goldh85.js', encoding='utf-8').read().rstrip('\n') + '\n' + open('mprof.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<li data-page="bdesk" onclick="navigate(\'bdesk\')"><span class="sb-icon">⇡</span> Breakout Desk <span class="sb-badge" id="sbBadge-bdesk"></span></li>',
    '<li data-page="bdesk" onclick="navigate(\'bdesk\')"><span class="sb-icon">⇡</span> Breakout Desk <span class="sb-badge" id="sbBadge-bdesk"></span></li>\n'
    '      <li data-page="mprof" onclick="navigate(\'mprof\')"><span class="sb-icon">◈</span> Market Profiles <span class="sb-badge" id="sbBadge-mprof"></span></li>')
page = ('<div id="page-mprof" class="page">\n'
        '      <div class="creed-banner intel-banner">\n'
        '        <div class="creed-banner-glow"></div>\n'
        '        <div class="creed-banner-main">\n'
        '          <div class="creed-banner-kicker">Ω OMEGA · MARKET PROFILES</div>\n'
        '          <h2 class="creed-banner-title">Market Profiles <span>— gold and five coins, studied one by one</span></h2>\n'
        '          <div class="creed-banner-flow"><i>When it moves</i><b>→</b><i>How it behaves</i><b>→</b><i>What drives it</i><b>→</b><i>How to size it</i><b>→</b><i>What was tested</i></div>\n'
        '        </div>\n'
        '      </div>\n'
        '      <div id="mprofBody"><p class="hint">Loading…</p></div>\n'
        '    </div>\n'
        '    <div id="page-bdesk" class="page">')
rep('<div id="page-bdesk" class="page">', page)
rep("var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','bdesk',", "var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','bdesk','mprof',")
rep("drawSafe(p, function(){ if((p === 'bdesk' || p === 'osig') && window.OMEGA_BDESK) window.OMEGA_BDESK.render(); });",
    "drawSafe(p, function(){ if((p === 'bdesk' || p === 'osig') && window.OMEGA_BDESK) window.OMEGA_BDESK.render(); });\n      drawSafe(p, function(){ if(p === 'mprof' && window.OMEGA_MPROF) window.OMEGA_MPROF.onShow(); });")
rep("['bdesk','Breakout Desk'],", "['bdesk','Breakout Desk'],['mprof','Market Profiles'],")
R = [("21", "Plan E2 (written and fingerprinted before any gold hourly data existed): the 5-unit method and the new method on a 72-hour breakout in US hours, gold hourly Jul 2020 \\u2013 Oct 2026 (Twelve Data, downloaded by OMEGA), a true 1% risk, 0.05% a side",
             "Both FAILED: 100 to 47.4 (0 of 7 years positive) and 100 to 74.3 (2 of 7), beating 88% and 89.5% of coin-flip accounts (97.5% needed), while holding gold gained 128%."),
     ("22", "Plan E3 on the same gold file: overnight drift (holding only outside US hours), a forced-selling rebound, and a weekend gap fade, at 0.02% a side",
             "All FAILED (overnight +34% after costs, t 1.08; only 4 rebound cases; gap fade about 0). Found: before costs gold made +103% outside US hours and \\u221221% during them. Plan E4 checks this once on silver and on gold before July 2020."),
     ("23", "Plan E5: six markets profiled one by one (gold, DOGE, LINK, LTC, ADA, AVAX; hourly 2020\\u20132026) and seven simple rules each, chosen on 2020\\u20132023 and judged once on 2024\\u20132026",
             "No rule passed on any market. Common to all six (before costs, on data already used): gains outside US hours and a drift down during them. Recorded forward from 21 Oct 2026 (plan E6, judged once after 26 weeks). The profiles are on the new Market Profiles page.")]
rows = ''.join(",\n    { round:'" + n + "', tried:'" + a + "', result:'" + b + "' }" for n, a, b in R)
rep("Next: plan E2 on gold hourly (download added).' } ];", "Next: plan E2 on gold hourly (download added).' }" + rows + " ];")
rep('Research record, rounds 1\\u201320 \\u2014', 'Research record, rounds 1\\u201323 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.84 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.84 ' + sep + ' build ' + old + ' UTC', 'v6.5.85 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.85 · build' in s and 'v6.5.84 · build' not in s and s.count('window.OMEGA_MPROF = ') == 1 and s.count('window.OMEGA_GOLDH = ') == 1 and s.count("{ round:'23',") == 1 and s.count('id="page-mprof"') == 1
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
