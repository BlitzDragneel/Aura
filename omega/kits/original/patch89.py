"""v6.5.89: Market Read (the app's own read and liquidity map, level memory, Autopilot jobs), the Brain's knowledge gains
plans E1–E13 and new lessons, research record rounds 26–28, the gold download stops on a paid-plan answer. Nothing else changed."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
# 1. modules: gold download replaced; Market Read after the Research files card
i = s.index('<script>/* ═══ GOLD HOURLY HISTORY (v6.5.84, v6.5.85)'); j = s.index('</script>', i) + len('</script>')
s = s[:i] + open('goldh89.js', encoding='utf-8').read().rstrip('\n') + s[j:]
i = s.index('<script>/* ═══ RESEARCH FILES (v6.5.88)'); j = s.index('</script>', i) + len('</script>')
s = s[:j] + '\n' + open('mread.js', encoding='utf-8').read().rstrip('\n') + s[j:]
# 2. the page
rep('<li data-page="mprof" onclick="navigate(\'mprof\')"><span class="sb-icon">◈</span> Market Profiles <span class="sb-badge" id="sbBadge-mprof"></span></li>',
    '<li data-page="mread" onclick="navigate(\'mread\')"><span class="sb-icon">≋</span> Market Read <span class="sb-badge" id="sbBadge-mread"></span></li>\n      <li data-page="mprof" onclick="navigate(\'mprof\')"><span class="sb-icon">◈</span> Market Profiles <span class="sb-badge" id="sbBadge-mprof"></span></li>')
page = ('<div id="page-mread" class="page">\n      <div class="creed-banner intel-banner">\n        <div class="creed-banner-glow"></div>\n        <div class="creed-banner-main">\n'
        '          <div class="creed-banner-kicker">Ω OMEGA · MARKET READ</div>\n          <h2 class="creed-banner-title">Market Read <span>— where the liquidity lies, read by the app itself</span></h2>\n'
        '          <div class="creed-banner-flow"><i>Stops above</i><b>→</b><i>Stops below</i><b>→</b><i>Resting orders</i><b>→</b><i>Who is crowded</i><b>→</b><i>What the research supports</i></div>\n'
        '        </div>\n      </div>\n      <div id="mreadBody"><p class="hint">Loading…</p></div>\n    </div>\n    <div id="page-mprof" class="page">')
rep('<div id="page-mprof" class="page">', page)
rep("var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','bdesk','mprof',", "var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','bdesk','mprof','mread',")
rep("drawSafe(p, function(){ if(p === 'mprof' && window.OMEGA_MPROF) window.OMEGA_MPROF.onShow(); });",
    "drawSafe(p, function(){ if(p === 'mprof' && window.OMEGA_MPROF) window.OMEGA_MPROF.onShow(); });\n      drawSafe(p, function(){ if(p === 'mread' && window.OMEGA_MREAD) window.OMEGA_MREAD.onShow(); });")
rep("['mprof','Market Profiles'],", "['mprof','Market Profiles'],['mread','Market Read'],")
# 3. the Brain's built-in knowledge: plans E1–E13 and lessons
i = s.index('var KN = '); j = s.index(';\n', i); KN = json.loads(s[i + 9:j])
E = [("E1", "One-shot test on 2021\u20132023 (14 older perpetuals) of the 72-hour breakout + 5-unit method, the momentum burst + pyramid and the new management method", "all failed: 100 \u2192 49.1, 27.2, 71.4; A and B worse than coin-flip direction"),
     ("E2", "Gold hourly, Jul 2020 \u2013 Oct 2026: the 5-unit method and the new method on a 72-hour breakout in US hours", "both failed: 100 \u2192 47.4 and 74.3 while holding gold gained 128%"),
     ("E3", "Gold hourly: overnight drift, forced-selling rebound, weekend gap fade", "all failed; found: before costs gold made +103% outside US hours and \u221221% during them"),
     ("E4", "The gold session split on silver and older gold", "data changed: Twelve Data gold starts 24 Jan 2020 and silver needs a paid plan; silver to come from Binance\u2019s perpetual"),
     ("E5", "Six markets profiled (gold, DOGE, LINK, LTC, ADA, AVAX) and seven simple rules each, judged on 2024\u20132026", "no rule passed; common to all six before costs: gains outside US hours, drift down during them"),
     ("E6", "Forward record of the session split, six markets, from 21 Oct 2026", "running; judged once after 26 weeks"),
     ("E7", "Both directions: how each market falls and rises; four short-only rules", "no short-only rule passed; movement close to symmetric"),
     ("E8", "Market states (depressed, booming, correcting, consolidating) and one rule each", "no state predicted the next week; no rule passed (closest: capitulation bounce, t 2.05)"),
     ("E9", "The capitulation bounce unchanged on the 324 perpetuals", "failed (\u221253.5%): it bought LUNA in May 2022"),
     ("E10", "Market-level capitulation on BTC, ETH, SOL, BNB, XRP", "failed: +7.3%, t 0.28, negative before 2024"),
     ("E11", "Absorption on BTC and ETH (aggressive flow that does not move price)", "failed: right direction, smaller than fees (\u22120.057% a trade after costs)"),
     ("E12", "Stop-outs on BTC and ETH: noise or hunting?", "mostly noise (37\u201339% went the trade\u2019s way after the stop vs 44\u201345% on shuffled prices); obvious-level stops reversed 0.9 points more: real but tiny"),
     ("E13", "Market Watch questions: liquidation flushes, short squeezes, tape absorption, Coinbase vs Binance", "waiting for 5 days of near-complete recording")]
have = {e.get('r') for e in KN['earlier']}
for r, nm, v in E:
    if r not in have: KN['earlier'].append({'r':r, 'name':nm, 'v':v})
L = ["Picking the best of many combinations on past data fails on new data: every winner of the 792-combination sweep and the 23,328-account management search faded (E-studies, 20 Oct 2026).",
     "Count results by week, not by trade: trades in the same week share the market\u2019s move; a t of 3.0 by trade was 0.55 by week.",
     "Small accounts change results: Binance\u2019s 5 USDT minimum order silently raised risk and made one setup look twice as good as it was.",
     "Trade management (scaling out, break-even, pyramiding) changes how trading feels, not whether it earns: on shuffled prices every technique lost the cost of trading.",
     "Most stop-outs are noise: price went the trade\u2019s way after a stop-out less often than on random paths; obvious-level stops are swept and reversed only about 1 time in 100 more.",
     "Liquidations follow price; the information is in what happens after a cluster, which is what the Market Watch questions (plan E13) will test."]
for x in L:
    if x not in KN['lessons']: KN['lessons'].append(x)
s = s[:i + 9] + json.dumps(KN, ensure_ascii=False, separators=(',', ':')) + s[j:]
# 4. the Mind's lessons
k = s.index('var LESSONS = ['); e = s.index('\n  ];', k)
newL = ("\n    ,{ t:'Judge on weeks it has not seen', why:'Every rule chosen as the best on past data faded on later data or other coins in the 19\\u201321 Oct studies.', how:'Each test is written down and fingerprinted before its data, run once, and only then trusted on new weeks.' }"
        "\n    ,{ t:'A stop-out is usually just noise', why:'After a stop-out, price went the trade\\u2019s way less often than on random price paths; stops at obvious levels are swept only slightly more.', how:'Size from the hourly range, keep stops a little away from obvious highs and lows, and do not read a stop-out as being targeted.' }"
        "\n    ,{ t:'Liquidity sits at the obvious levels', why:'Stops gather beyond yesterday\\u2019s and last week\\u2019s highs and lows, equal highs and lows and round numbers.', how:'Market Read maps them, with the order book and crowding, and measures how often price reaches them.' }")
s = s[:e] + newL + s[e:]
# 5. research record rounds 26–28
R = [("26", "Plans E8\\u2013E10: market states (depressed, booming, correcting, consolidating) on the 20 majors with one rule each; the capitulation bounce on the 324 perpetuals (E9) and on BTC, ETH, SOL, BNB, XRP (E10)", "No state predicted the next week and no state rule passed (closest: the capitulation bounce, t 2.05). E9 failed (\\u221253.5%; it bought LUNA in May 2022); E10 failed (+7.3%, t 0.28). The daily capitulation bounce is closed."),
     ("27", "Plans E11\\u2013E12 on BTC and ETH: absorption (aggressive flow that does not move price) and stop-outs (noise or hunting?)", "E11 failed: the right direction but smaller than fees (\\u22120.057% a trade after costs). E12: after a stop-out, price went 1R the trade\\u2019s way in 37\\u201339% of cases against 44\\u201345% on shuffled prices (mostly noise); stops just beyond obvious highs and lows reversed 0.9 points more (95% interval 0.1\\u20131.7): real but tiny."),
     ("28", "Market Watch: two exports (47 and 442 minutes recorded); plan E13 written and checked on synthetic recordings; Market Read added (v6.5.89)", "Too little recording to test (E13 needs 5 days with 80%+ of minutes). One night explored: $4.3M liquidated on 25 coins while BTC moved 0.6%; liquidations follow price; the busiest 5% of minutes carry 70% of the dollars.")]
rows = ''.join(",\n    { round:'" + n + "', tried:'" + a + "', result:'" + b + "' }" for n, a, b in R)
k2 = s.index("{ round:'25',"); e2 = s.index("' } ];", k2) + len("' }")
s = s[:e2] + rows + s[e2:]
rep('Research record, rounds 1\\u201325 \\u2014', 'Research record, rounds 1\\u201328 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.88 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.88 ' + sep + ' build ' + old + ' UTC', 'v6.5.89 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.89 · build' in s and s.count('window.OMEGA_MREAD = ') == 1 and s.count("{ round:'28',") == 1 and s.count('id="page-mread"') == 1 and 'not available on the free Twelve Data plan' in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now, '| KN earlier', len(KN['earlier']), 'lessons', len(KN['lessons']))
