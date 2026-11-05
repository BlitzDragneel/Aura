"""v6.5.92: the Risk Guard (rules for every trade), the Growth Bot (plan E17: the app's signals under those rules, paper, from
100 USDT), a pre-trade check and journal for real trades, automatic research exports; all run by the Autopilot. Signals unchanged."""
import sys, re, json, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)
i = s.index('<script>/* ═══ DAILY PLAN (v6.5.91)'); j = s.index('</script>', i) + len('</script>'); s = s[:j] + '\n' + open('rguard.js', encoding='utf-8').read().rstrip('\n') + s[j:]
rep('<li data-page="mread" onclick="navigate(\'mread\')">', '<li data-page="rguard" onclick="navigate(\'rguard\')"><span class="sb-icon">⛨</span> Risk Guard <span class="sb-badge" id="sbBadge-rguard"></span></li>\n      <li data-page="mread" onclick="navigate(\'mread\')">')
page = ('<div id="page-rguard" class="page">\n      <div class="creed-banner intel-banner">\n        <div class="creed-banner-glow"></div>\n        <div class="creed-banner-main">\n'
        '          <div class="creed-banner-kicker">Ω OMEGA · RISK GUARD</div>\n          <h2 class="creed-banner-title">Risk Guard <span>— risk is what makes money; managing it decides whether it does</span></h2>\n'
        '          <div class="creed-banner-flow"><i>0.5% a trade</i><b>→</b><i>2 open at most</i><b>→</b><i>−2% a day stops</i><b>→</b><i>−5% a week stops</i><b>→</b><i>review at −20%</i></div>\n'
        '        </div>\n      </div>\n      <div id="rguardBody"><p class="hint">Loading…</p></div>\n    </div>\n    <div id="page-mread" class="page">')
rep('<div id="page-mread" class="page">', page)
rep("'bdesk','mprof','mread',", "'bdesk','mprof','mread','rguard',")
rep("drawSafe(p, function(){ if(p === 'mread' && window.OMEGA_MREAD) window.OMEGA_MREAD.onShow(); });", "drawSafe(p, function(){ if(p === 'mread' && window.OMEGA_MREAD) window.OMEGA_MREAD.onShow(); });\n      drawSafe(p, function(){ if(p === 'rguard' && window.OMEGA_RGUARD) window.OMEGA_RGUARD.onShow(); });")
rep("['mread','Market Read'],", "['mread','Market Read'],['rguard','Risk Guard'],")
k = s.index('var LESSONS = ['); e = s.index('\n  ];', k)
s = s[:e] + ("\n    ,{ t:'Risk is what makes money; managing it decides whether it does', why:'In the spirit of Sharran Srivatsaa\\u2019s teaching on risk: avoiding risk earns nothing, and unmanaged risk ends accounts. The difference is how it is sized, limited and learned from.', how:'The Risk Guard sizes every trade at 0.5% (1% after 30 clean trades), allows 2 open, stops the day at \\u22122% and the week at \\u22125%, and pauses for review at \\u221220%; the Growth Bot follows the same rules.' }") + s[e:]
i = s.index('var KN = '); j = s.index(';\n', i); KN = json.loads(s[i + 9:j])
if 'E17' not in {x.get('r') for x in KN['earlier']}: KN['earlier'].append({'r':'E17', 'name':'The Growth Bot (v6.5.92): the app\u2019s signals under the Risk Guard\u2019s rules, paper, from 100 USDT', 'v':'running from 22 Oct 2026; judged once after 26 weeks or 50 trades'})
s = s[:i + 9] + json.dumps(KN, ensure_ascii=False, separators=(',', ':')) + s[j:]
r31 = ("    { round:'31', tried:'Not a test: the Risk Guard and the Growth Bot (v6.5.92) \\u2014 rules for every trade (0.5% risk, 2 open, \\u22122% day and \\u22125% week stops, review at \\u221220%), a 100 USDT paper bot that takes the climax (A) and Daily Plan (C) signals under them (plan E17), a pre-trade check for real trades, and automatic research exports', "
       "result:'Running forward. It answers the owner\\u2019s question \\u2014 can these signals grow 100 USDT when risk is managed? \\u2014 with a record no one can tune after the fact. The signals themselves are unchanged.' }")
k2 = s.index("{ round:'30',"); e2 = s.index("' } ];", k2) + len("' }"); s = s[:e2] + ",\n" + r31 + s[e2:]
rep('Research record, rounds 1\\u201330 \\u2014', 'Research record, rounds 1\\u201331 \\u2014')
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.91 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.91 ' + sep + ' build ' + old + ' UTC', 'v6.5.92 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.92 · build' in s and s.count('window.OMEGA_RGUARD = ') == 1 and s.count('id="page-rguard"') == 1 and "{ round:'31'," in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
