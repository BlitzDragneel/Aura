"""v6.5.77: Market Watch, the recorder (round 16's data, PLAN16 draft): a new page that records every public footprint of
large buying and selling while the app is open, with flight recordings around sudden moves; and the liquidation feed
moved to Binance's new futures address (the old one ended 23 Apr 2026)."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)
# 1. the module
rep('</body>', open('watch.js', encoding='utf-8').read().rstrip('\n') + '\n</body>')
# 2. the page, its sidebar entry and the navigator's list
rep("""      <li data-page="edgelab" onclick="navigate('edgelab')"><span class="sb-icon">✦</span> Edge Lab</li>\n""",
    """      <li data-page="edgelab" onclick="navigate('edgelab')"><span class="sb-icon">✦</span> Edge Lab</li>\n      <li data-page="watch" onclick="navigate('watch')"><span class="sb-icon">◉</span> Market Watch</li>\n""")
page = """    <div id="page-watch" class="page">
      <div class="creed-banner intel-banner">
        <div class="creed-banner-glow"></div>
        <div class="creed-banner-main">
          <div class="creed-banner-kicker">Ω MARKET WATCH · RECORDING ONLY</div>
          <h2 class="creed-banner-title">Market Watch <span>— who is pushing the price, and how hard</span></h2>
          <div class="creed-banner-flow"><i>Aggressive orders</i><b>→</b><i>Large orders</i><b>→</b><i>Order book</i><b>→</b><i>Liquidations</i><b>→</b><i>Flight recordings</i></div>
        </div>
      </div>
      <div id="watchBody"><p class="hint">Loading…</p></div>
    </div>
"""
rep('    <div id="page-ostrat" class="page">\n', page + '    <div id="page-ostrat" class="page">\n')
rep("var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','auto','mind','futures','posdesk','edgelab','ostrat',",
    "var EXTRA = ['command','score','brain','radar','intel','flow','lab','osig','auto','mind','futures','posdesk','edgelab','watch','ostrat',")
rep("edgeLab: safe(function(){ return window.OMEGA_EDGELAB ? window.OMEGA_EDGELAB.report() : null; }) || null,",
    "edgeLab: safe(function(){ return window.OMEGA_EDGELAB ? window.OMEGA_EDGELAB.report() : null; }) || null, marketWatch: safe(function(){ return window.OMEGA_WATCH ? window.OMEGA_WATCH.report() : null; }) || null,")
# 3. the positioning collector's liquidation feed: Binance's routed address (liquidations are a /market stream since the
#    2026 split; the old /ws address ended 23 Apr 2026), and "live" only once data actually arrives
rep("""      ws = new WebSocket('wss://fstream.binance.com/ws/!forceOrder@arr'); wsState = 'connecting';
      ws.onopen = function(){ wsState = 'live'; render(); };""",
    """      ws = new WebSocket('wss://fstream.binance.com/market/ws/!forceOrder@arr'); wsState = 'connecting';   // v6.5.77: Binance moved liquidations to /market (the old /ws address ended 23 Apr 2026)
      ws.onopen = function(){ wsState = 'connected'; render(); };""")
rep("""      ws.onmessage = function(m){ try{ var d = JSON.parse(m.data), o = d && d.o; if(!o) return;""",
    """      ws.onmessage = function(m){ if(wsState !== 'live'){ wsState = 'live'; render(); } try{ var d = JSON.parse(m.data); d = d && d.data ? d.data : d; var o = d && d.o; if(!o) return;""")
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
old = re.search(r'v6\.5\.76 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.76 ' + sep + ' build ' + old + ' UTC', 'v6.5.77 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.77 · build' in s and 'v6.5.76 · build' not in s and s.count('window.OMEGA_WATCH = ') == 1 and "fstream.binance.com/ws/!forceOrder" not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, 'build', now)
