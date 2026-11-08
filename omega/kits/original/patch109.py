"""v6.5.109: clean-up. Research now lives outside the app (repo `edges`, the GitHub paper bot and scouts, the Render Live API),
so the research machinery comes out and the app keeps what the owner uses: charts and mark-up, market intel, CREED (desk,
scanner, journal), OMEGA signals (climax A, panic bounce B, Daily Plan C), bots (Risk Guard / Growth Bot, Bots, Autopilot for
the kept jobs), the Positioning Desk, Futures (calculator, paper account, leverage warning), the journal, settings and backups.
CREED's engine (analyseSeries, walkExit, the whole CREED module) is byte-identical: no line of script 31 is touched.
 1. Pages removed (markup, menu entries, palette entries, page hooks): Research Lab, Edge Lab, Market Watch, Market Profiles,
    Breakout Desk, OMEGA Strategy, Strategy Scanner, Strategy Backtest, CREED Backtest (Simulation), How OMEGA thinks (Mind),
    Scoreboard.
 2. Research-only script modules removed with their CSS and their Autopilot jobs: the 1.06 MB embedded "starting knowledge"
    seed (99% research stores and 789 backtest rows; the owner's device applied it long ago, and backups cover a new device),
    Sim Labs 2 & 3 (orphaned since v4.3), Scoreboard, Edge Finder, OMEGA Strategy + cross-section, auto backtest, exploration,
    market board, portfolio lab, workshop, all research exports (history, older history, fresh coins x2, research files),
    the outside research record, funding carry weekly, funding harvest, round 12, BTC trend benchmark, wide data store, edge
    library, Edge Lab, "why signals are rare" research card, Breakout Desk, gold hourly download, Market Profiles, model across
    coins, Market Watch recorder.
 3. Autopilot jobs removed: history downloads (deep, topup), CREED replay, patterns, Research Lab, edge search, context and entry
    studies, forecasts, reflection, council, and every job of the removed modules (bdesk, mprof, mwatch, mwdays, goldh, autoexp,
    backtests, explore, portfolio, workshop, harvest, r12, btctrend, wide, edgelab).
 4. Kept although research-flavoured, because kept pages and CREED's bots call them (code only, no page of their own): the
    Research Lab engine and its signals module, Mind (broker costs), entry and context studies (CREED bot add-ons), history store.
 5. Navigation: menu regrouped for the kept app; phone bottom bar Home / Charts / Signals / CREED / Bots / Academy / More
    (Academy appears once its page exists, v6.5.110); the app always opens on Home.
 6. Signals page: climax (A), panic bounce (B) and the Daily Plan (C, now also shown here), plus a short Evidence note with a
    link to the progress board. The Research Lab's own signal lists leave the page.
 7. Data stored by removed pages is left in localStorage untouched (just no longer read).
usage: python3 patch109.py <v6.5.108 build> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:120])
    s = s.replace(a, b)


def rm_script(marker):
    """remove the whole <script>…</script> block whose content starts with marker"""
    global s
    i = s.find('<script>' + marker)
    assert i > -1 and s.count('<script>' + marker) == 1, marker[:80]
    j = s.index('</script>', i) + len('</script>')
    if s[j:j + 1] == '\n': j += 1
    s = s[:i] + s[j:]


def rm_div(open_tag):
    """remove a <div …> element (balanced) that starts with open_tag, plus its line indentation"""
    global s
    i = s.find(open_tag); assert i > -1 and s.count(open_tag) == 1, open_tag
    k, depth = i, 0
    for m in re.finditer(r'<div\b|</div>', s[i:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0: k = i + m.end(); break
    assert depth == 0, open_tag
    a = s.rfind('\n', 0, i) + 1
    if s[a:i].strip() == '': i = a
    if s[k:k + 1] == '\n': k += 1
    s = s[:i] + s[k:]


SIZE0 = len(s.encode('utf-8'))

# ── 1. pages ──
REMOVED = ['lab', 'edgelab', 'watch', 'mprof', 'bdesk', 'ostrat', 'ostratscan', 'ostratbt', 'simulation', 'mind', 'score']
for p in REMOVED:
    rm_div('<div id="page-' + p + '" class="page">')

# ── 2. research-only modules ──
SCRIPTS = [
    '\n// ================================================================\n// OMEGA v4.3 — SIM LABS 2 & 3',
    '/* ═══ SCOREBOARD + BRAIN PACKAGE — shared, neutral, read-only ═══',
    '/* ═══ EDGE FINDER — search honestly, confirm on data the search never',
    "/* ═══ OMEGA STRATEGY — a method of OMEGA's own, made only of what sur",
    '/* ═══ AUTO BACKTEST (v6.5.32)',
    '/* ═══ EXPLORATION + AVOID LIST (v6.5.35)',
    '/* ═══ MARKET BOARD (v6.5.38)',
    '/* ═══ PORTFOLIO LAB (v6.5.41)',
    'window.OMEGA_SEED_B64="',
    '/* ═══ STRATEGY WORKSHOP (v6.5.49)',
    '/* ═══ RESEARCH DATA EXPORT (v6.5.50)',
    '/* ═══ OUTSIDE RESEARCH RECORD (v6.5.52)',
    '/* ═══ OLDER HISTORY FOR RESEARCH (v6.5.54)',
    '/* ═══ FUNDING CARRY, WEEKLY (v6.5.55',
    '/* ═══ FRESH COINS FOR RESEARCH (v6.5.57)',
    '/* ═══ FUNDING HARVEST (v6.5.59',
    '/* ═══ ROUND 12 WINNERS (v6.5.69)',
    '/* ═══ BTC TREND BENCHMARK (v6.5.60)',
    '/* ═══ NEW COINS FOR RESEARCH (v6.5.61)',
    '/* ═══ WIDE DATA STORE (v6.5.70)',
    '/* ═══ EDGE LIBRARY (v6.5.70)',
    '/* ═══ EDGE LAB (v6.5.70)',
    '/* ═══ WHY SIGNALS ARE RARE',
    '/* ═══ BREAKOUT DESK (v6.5.83, v6.5.84)',
    '/* ═══ GOLD HOURLY HISTORY (v6.5.84, v6.5.85)',
    '/* ═══ MARKET PROFILES (v6.5.85, v6.5.86, v6.5.90)',
    '/* ═══ RESEARCH FILES (v6.5.88)',
    "/* ═══ MODEL ACROSS COINS (v6.5.73)",
    '/* ═══ MARKET WATCH (v6.5.77)',
]
for m in SCRIPTS: rm_script(m)
assert 'OMEGA_SEED_B64' not in s and 'window.OMEGA_EDGELAB =' not in s and 'window.OMEGA_WATCH =' not in s

# CSS used only by the removed OMEGA Strategy / backtest board
for sid in ['niCss', 'btCss']:
    m = re.search(r'<style id="' + sid + r'">.*?</style>\n?', s, re.S); assert m and s.count('<style id="' + sid + '">') == 1, sid
    s = s.replace(m.group(0), '')

# ── 3. Autopilot jobs ──
GONE = ['deep', 'creed', 'patterns', 'topup', 'lab', 'edge', 'context', 'entry', 'forecast', 'reflect', 'council']
rep("        var r = await K.convene(pick, {}); return pick+': '+((r && r.verdict && r.verdict.verdict) || 'done')+'.'; } }\n  ];\n",
    "        var r = await K.convene(pick, {}); return pick+': '+((r && r.verdict && r.verdict.verdict) || 'done')+'.'; } }\n  ];\n"
    "  // v6.5.109: research and download jobs retired (research now runs outside the app)\n"
    "  JOBS = JOBS.filter(function(j){ return " + repr(GONE).replace(' ', '') + ".indexOf(j.id) < 0; });\n")
# in-module jobs of kept modules: Market Watch days (Market Read), research exports (Risk Guard), autopilot coverage
m = re.search(r",\n    \{ id:'mwdays', lane:'live'.*?\} \}\];\n", s, re.S); assert m and s.count("{ id:'mwdays'") == 1
s = s.replace(m.group(0), "];\n", 1)
m = re.search(r",\n    \{ id:'autoexp', lane:'heavy'.*?\} \}\];\n", s, re.S); assert m and s.count("{ id:'autoexp'") == 1
s = s.replace(m.group(0), "];\n", 1)
m = re.search(r",\n    \{ id:'bdesk', lane:'live', prio:2.*?\n  \];\n", s, re.S); assert m and s.count("{ id:'bdesk'") == 1
s = s.replace(m.group(0), "\n  ];\n", 1)
assert "id:'mwatch'" not in s and "id:'goldh'" not in s and "id:'climax'" in s and "id:'mread'" in s and "id:'rguard'" in s

# ── 4. page hooks and links to removed pages ──
rep("  var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','bdesk','mprof','mread','rguard','auto','mind','futures','posdesk','edgelab','watch','ostrat','ostratscan','ostratbt'];",
    "  var EXTRA = ['command','brain','radar','intel','flow','osig','mread','rguard','auto','futures','posdesk','academy'];   // v6.5.109: research pages removed")
for line in ["      drawSafe(p, function(){ if(p === 'score' && window.OMEGA_SCORE) window.OMEGA_SCORE.render(); });\n",
             "      drawSafe(p, function(){ if((p === 'bdesk' || p === 'osig') && window.OMEGA_BDESK) window.OMEGA_BDESK.render(); });\n",
             "      drawSafe(p, function(){ if(p === 'mprof' && window.OMEGA_MPROF) window.OMEGA_MPROF.onShow(); });\n",
             "      drawSafe(p, function(){ var S = window.OMEGA_STRATEGY; if(!S) return; if(p === 'ostrat') S.renderMain(); else if(p === 'ostratscan') S.openScan(); else if(p === 'ostratbt') S.renderBt(); });\n",
             "      drawSafe(p, function(){ if(p === 'mind' && window.OMEGA_MIND) window.OMEGA_MIND.render(); });\n"]:
    rep(line, '')
m = re.search(r"      drawSafe\(p, function\(\)\{ if\(p === 'lab'\)\{[^\n]*\n", s); assert m; s = s.replace(m.group(0), '', 1)
rep("      drawSafe(p, function(){ if((p === 'mread' || p === 'analysis') && window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); });",
    "      drawSafe(p, function(){ if((p === 'mread' || p === 'analysis' || p === 'osig') && window.OMEGA_DPLAN) window.OMEGA_DPLAN.onShow(); });")
rep("  function navigate(p){\n    EXTRA.forEach(", "  function navigate(p){\n    if(p && !el('page-'+p)) p = 'command';   // v6.5.109: a link to a removed page lands on Home\n    EXTRA.forEach(")
# palette
m = re.search(r"    var pages = \[\['command','Command Center'\].*?\]\];\n", s, re.S); assert m
s = s.replace(m.group(0),
    "    var pages = [['command','Home'],['analysis','Charts (Analysis)'],['mread','Market Read (mark-up)'],['intel','Market Intelligence'],['flow','Live Market Data'],"
    "['osig','Signals'],['creed','CREED Desk'],['radar','CREED Scanner'],['journal','Journal'],['bot','Bots'],['rguard','Risk Guard & Growth Bot'],['auto','Autopilot'],"
    "['posdesk','Positioning Desk'],['futures','Futures'],['growth','Growth & Routine'],['brain','Brain'],['academy','Academy'],['settings','Settings']];\n", 1)
rep("    if(window.OMEGA_LAB){\n      list.push({ label:'Run research (OMEGA Research Lab)', hint:'Intelligence', run:function(){ navigate('lab'); window.OMEGA_LAB.runLab(); } });\n    }\n", '')
rep("    if(window.OMEGA_MIND) list.push({ label:'What does OMEGA know, not know and assume?', hint:'Intelligence', run:function(){ navigate('mind'); } });\n", '')
rep("    if(window.OMEGA_HISTORY){\n      list.push({ label:'Download market history', hint:'data', run:function(){ navigate('lab'); } });\n    }\n", '')
m = re.search(r"    if\(window.OMEGA_SCORE\)\{\n.*?\n    \}\n", s, re.S); assert m and 'navigate(\'score\')' in m.group(0); s = s.replace(m.group(0), '', 1)

# bottom bar: Home / Charts / Signals / CREED / Bots / Academy / More (a page that does not exist yet is left out)
rep("    var items = [['command','\\u2302','Home'],['creed','\\u2694','CREED'],['intel','\\u25c8','Intel'],['journal','\\u25a4','Journal'],['__more','\\u2630','More']];",
    "    var items = [['command','\\u2302','Home'],['analysis','\\u2197','Charts'],['osig','\\u25ce','Signals'],['creed','\\u2694','CREED'],['bot','\\u2699','Bots'],['academy','\\u2605','Academy'],['__more','\\u2630','More']]\n"
    "      .filter(function(x){ return x[0] === '__more' || el('page-'+x[0]); });   // v6.5.109")
rep(".omega-bottomnav{ display:grid; grid-template-columns:repeat(5,1fr);",
    ".omega-bottomnav{ display:grid; grid-template-columns:none; grid-auto-flow:column; grid-auto-columns:1fr;")

# always open on Home
rep("    if(saved && el('page-'+saved)) window.navigate(saved);\n  });", "    // v6.5.109: the app always opens on Home\n  });")
rep("    if(saved && EXTRA.indexOf(saved) < 0 && el('page-'+saved)){ var pc = el('page-command'); if(pc) pc.classList.remove('active'); markLi(saved); syncBottomNav(saved); }\n"
    "    else navigate((saved && EXTRA.indexOf(saved) > -1 && el('page-'+saved)) ? saved : 'command');",
    "    navigate('command');   // v6.5.109: always open on Home")

# sidebar menu
m = re.search(r'    <ul class="sidebar-menu">\n.*?    </ul>\n', s, re.S); assert m and s.count('<ul class="sidebar-menu">') == 1
def li(p, icon, name, badge=False, active=False):
    return ('      <li' + (' class="active"' if active else '') + ' data-page="' + p + '" onclick="navigate(\'' + p + '\')"><span class="sb-icon">' + icon + '</span> ' + name +
            (' <span class="sb-badge" id="sbBadge-' + p + '"></span>' if badge else '') + '</li>\n')
MENU = ('    <ul class="sidebar-menu">\n'
        '      <li class="sb-tier">Home</li>\n' + li('command', '⌂', 'Home', active=True) +
        '      <li class="sb-tier">Charts &amp; markets</li>\n' + li('analysis', '📊', 'Charts (Analysis)') + li('mread', '≋', 'Market Read (mark-up)', True) +
        li('intel', '◈', 'Market Intelligence', True) + li('flow', '≋', 'Live Market Data') +
        '      <li class="sb-tier">Signals</li>\n' + li('osig', '◎', 'Signals (OMEGA)', True) + li('creed', '⚔️', 'CREED Desk', True) + li('radar', '◎', 'CREED Scanner', True) +
        '      <li class="sb-tier">Bots &amp; risk</li>\n' + li('bot', '🤖', 'Bots', True) + li('rguard', '⛨', 'Risk Guard &amp; Growth Bot', True) + li('auto', '⚙', 'Autopilot', True) +
        '      <li class="sb-tier">Trading desk</li>\n' + li('posdesk', '⇅', 'Positioning Desk') + li('futures', '⚡', 'Futures') + li('journal', '📖', 'Journal') +
        li('growth', '🌱', 'Growth &amp; Routine') + li('brain', '✺', 'Brain') +
        '      <li class="sb-tier">Learn</li>\n' + li('academy', '★', 'Academy') +
        '      <li class="sb-tier">System</li>\n' + li('settings', '⚙️', 'Settings') +
        '    </ul>\n')
s = s.replace(m.group(0), MENU, 1)
# the Academy entry only shows once the page exists (v6.5.110)
rep("    buildBottomNav(); guardBotStarts();",
    "    buildBottomNav(); guardBotStarts();\n"
    "    try{ document.querySelectorAll('.sidebar-menu li[data-page]').forEach(function(li){ if(!el('page-'+li.getAttribute('data-page'))) li.style.display = 'none'; }); }catch(e){}   // v6.5.109")

# links on kept pages that pointed at removed pages
rep("""      <div class="card" style="margin-bottom:14px;">
        <h2 style="color:var(--gold);">Backtest on futures</h2>""", """      <div class="card" id="futBtGone" style="margin-bottom:14px;display:none;">
        <h2 style="color:var(--gold);">Backtest on futures</h2>""")
rep('          <button class="btn-outline" type="button" id="futRunLab">Run the Research Lab now</button>\n'
    '          <button class="btn-outline" type="button" id="futOpenBt">CREED Backtest in futures mode →</button>\n', '')
m = re.search(r'      <div class="card" id="futBtGone".*?\n      </div>\n', s, re.S); assert m; s = s.replace(m.group(0), '', 1)
rep("""<div id="opPill" class="op-pill" onclick="navigate('auto')"></div>""", """<div id="opPill" class="op-pill" onclick="navigate('auto')"></div>""")

# ── 6. Signals page ──
rep("""      <div id="climaxSigBody"></div>
      <div id="bdeskSigBody"></div>
""", """      <div id="climaxSigBody"></div>
      <div class="card" id="dplanSigWrap" style="margin-top:14px;"><h2 style="color:var(--gold);">Daily Plan — grade C (a plan, not a tested edge)</h2>
        <p class="hint" style="margin-top:0;">Grade C: a written plan per coin, followed on paper to its result. It has <b>not</b> passed a fair test — read it as structure for your own decision, not as a signal.</p>
        <div id="dplanSigBody"></div></div>
      <div class="card" id="osigEvidence" style="margin-top:14px;"><h2 style="color:var(--gold);">Evidence — what passed and what failed</h2>
        <p class="hint" style="margin:0;"><b>Passed fair tests:</b> the climax reversal (grade A) and the panic bounce H1/H3 (grade B, not yet confirmed forward; both fading lately).
        <b>Failed:</b> CREED measured at about a coin flip after costs (−0.10R to −0.12R a trade), the Breakout Desk setups, the funding harvest on 2025–26 (E34), and almost every other rule tested (12,480 rules in E28).
        The Daily Plan is grade C. Research, backtests and forward records now run outside the app — see the progress board:
        <a href="https://omega-board.onrender.com" target="_blank" rel="noopener">omega-board.onrender.com</a>.</p></div>
""")
m = re.search(r"      <p class=\"hint\"><b>Below: the phone Research Lab's own signals\.</b>.*?\n    </div>\n    <div id=\"page-posdesk\"", s, re.S); assert m
s = s.replace(m.group(0), "    </div>\n    <div id=\"page-posdesk\"", 1)
rep("  function render(){ ['dplanBody', 'dplanAnaBody'].forEach(function(id){",
    "  function render(){ ['dplanBody', 'dplanAnaBody', 'dplanSigBody'].forEach(function(id){")

# positioning desk: its "fresh coins" button opened the removed OMEGA Strategy page
m = re.search(r"    var g = el\('posdeskFresh'\); if\(g\) g.onclick = function\(\)\{[^\n]*\n", s); assert m
s = s.replace(m.group(0), "    var g = el('posdeskFresh'); if(g) g.style.display = 'none';   // v6.5.109: research exports left the app\n", 1)

# self-test: the checks of the removed Sim Labs 2 & 3 (labBacktest, labEdgeCheck, their resample) go; the carry monitor check stays
rep("      if(typeof window.labBacktest !== 'function') return FAIL('labBacktest not registered — sim lab buttons dead');\n      return 'analyzeTimeframe / scoreSetup / computeTradePlan / labBacktest all live';",
    "      return 'analyzeTimeframe / scoreSetup / computeTradePlan all live';   // v6.5.109: Sim Labs 2 & 3 removed")
rep("    t('edge lab wiring', function(){\n      if(typeof window.labEdgeCheck !== 'function') return FAIL('labEdgeCheck not registered — Edge Check buttons dead');\n      if(!window.OMEGA_CARRY) return FAIL('carry monitor module missing');\n      return 'labEdgeCheck + OMEGA_CARRY registered';",
    "    t('carry monitor', function(){\n      if(!window.OMEGA_CARRY) return FAIL('carry monitor module missing');\n      return 'OMEGA_CARRY registered';")
m = re.search(r"    /\* 17\. resample closed-bar integrity.*?\n    \}\);\n", s, re.S); assert m and '__omegaLabInternals' in m.group(0); s = s.replace(m.group(0), '', 1)

# ── version ──
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.108 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.108 ' + sep + ' build ' + o + ' UTC', 'v6.5.109 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.109 · build' in s and 'v6.5.108 · build' not in s
open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, now, 'size', SIZE0, '->', len(s.encode('utf-8')))
