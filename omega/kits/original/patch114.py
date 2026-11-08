"""v6.5.114: declutter without losing information. Layout and presentation only; every number, card and control is still
in the app. CREED's engine is byte-identical.
 1. Home: the verdict ("What is happening?" and the five questions) right under a calm hero, then the key numbers (Market
    pulse), the bots, and the trades OMEGA sees now. The eight detail cards (CREED's three markets and open positions open;
    Scanner, Intelligence, Classic analysis, Today, Lifecycle, What OMEGA learned closed) are dropdowns. The three
    "products" explainer cards move into "About this page".
 2. Charts: today's plan, the cockpit chart and events first; "Every market, one engine" (the scan of every market) is a
    dropdown; the in-depth chart follows; the data check moves to the end; "About this page" explains the page.
 3. Signals and CREED: the long evidence text inside the climax, panic-bounce and Daily Plan cards and the CREED reality
    check is clamped to its first screen with "Show the full evidence" (tap to open, tap again to close). The text stays
    in the page. CREED's intro paragraph moves into "About this page".
 4. Bots: the duplicate page header goes (its text is in "About this page"); one paper-trading notice stays; the OMEGA bot
    and Portfolio bot detail cards are one dropdown.
 5. Hero banners: the leading dash of each subtitle is hidden in the Heaven theme (the subtitle sits on its own line).
    Heaven polish: opaque status line and bottom bar, a little air under the header, a quiet disabled button.
usage: python3 patch114.py <v6.5.113> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


def about(body):
    return ('      <details class="om-about"><summary>About this page</summary><div class="om-about-body">\n' + body.strip('\n') +
            '\n      </div></details>\n')


# 5. hero subtitle dashes
s, n = re.subn(r'(<h2 class="creed-banner-title">[^<]*<span>)— ', r'\1<i class="hv-dash">— </i>', s)
assert n >= 10, n

# ── 1. Home ──
rep('    <div id="page-command" class="page active">\n      <div id="pulseCard"></div>\n',
    '    <div id="page-command" class="page active">\n')
rep('      <div id="cmdFive" class="cmd-five"></div>\n',
    '      <div id="cmdFive" class="cmd-five"></div>\n      <div id="pulseCard"></div>\n')
i = s.index('      <div class="cmd-products">'); j = s.index('      <div id="opPill"', i)
products = s[i:j]; s = s[:i] + s[j:]
g0 = s.index('      <div class="cmd-grid">'); g1 = s.index('    <div id="page-radar"', g0)
grid = s[g0:g1]
OPEN = ('CREED — three markets', 'Open positions')
def fold(m):
    cls, head = m.group(1), m.group(2)
    t = re.search(r'<h3>(.*?)</h3>', head).group(1)
    return '<details class="card cmd-card' + cls + ' hv-fold"' + (' open' if t in OPEN else '') + '>\n          <summary class="cmd-card-head">' + head + '</summary>'
grid2, n = re.subn(r'<section class="card cmd-card([^"]*)">\s*<div class="cmd-card-head">(<h3>.*?</h3>(?:\s*<div class="cmd-actions">.*?</div>)?)</div>', fold, grid, flags=re.S)
assert n == 8, n
grid2 = grid2.replace('</section>', '</details>'); assert grid2.count('</details>') == 8
grid2 = grid2.rstrip('\n') + '\n'
end = grid2.rindex('    </div>')   # the page's own closing tag
grid2 = grid2[:end] + about(products.replace('<div class="cmd-products">', '<p>Home answers five questions from what the app actually holds. The cards below each open with a tap; nothing is hidden for good.</p>\n      <div class="cmd-products">')) + grid2[end:]
s = s[:g0] + grid2 + s[g1:]

# ── 2. Charts ──
rep('      <div id="truthBody"></div>\n      <div id="dplanAnaBody"></div>\n      <div id="evAnaBody"></div>\n      <div id="cockpitBody"></div>\n      <section class="wl-room">\n',
    '      <div id="dplanAnaBody"></div>\n      <div id="cockpitBody"></div>\n      <div id="evAnaBody"></div>\n'
    '      <details class="wl-room hv-fold"><summary class="hv-sum">Every market, one engine <span>scan, setups and scores</span></summary>\n')
w0 = s.index('<details class="wl-room hv-fold">'); w1 = s.index('</section>', w0)
s = s[:w0] + s[w0:w1] + '</details>' + s[w1 + len('</section>'):]
p0 = s.index('    <div id="page-analysis" class="page">'); p1 = s.index('    <div id="page-journal"', p0)
pe = s.rindex('    </div>', p0, p1)
s = s[:pe] + '      <div id="truthBody"></div>\n' + about('''
        <p><b>Today&rsquo;s plan</b> (grade C) is a written plan per coin, followed on paper: not a tested edge. The <b>cockpit</b> shows the market with its levels, volume and order book. <b>Events ahead</b> warns before CPI, the Fed and other scheduled news.</p>
        <p><b>Every market, one engine</b> scores structure on 5-minute, 15-minute and 1-hour candles for every market; a score of 60 or more with at least 2:1 reward to risk meets the bar. It is the classic analysis engine, not a tested OMEGA idea.</p>
        <p><b>One market in depth</b> charts the market you pick (or tap on the Forex board) with structure, liquidity and a trade plan. Forex and metals candles come from Twelve Data with your key, otherwise from the OMEGA Live API; the source is shown with the result.</p>
        <p><b>Data check</b> (at the end) confirms the feeds are live and prices are sane.</p>
''') + s[pe:]

# ── 3. Signals and CREED: clamp the long evidence text (kept in the page) ──
rep('''      <div class="page-header">
        <div>
          <h2 class="page-title" style="display:none;">⚔️ CREED — Acceptance</h2>
          <p class="page-sub">One strategy, run as taught: 4H battlefield → 1H pullback zone → 15M sweep → acceptance. Market, symbol and key below are CREED&rsquo;s own — separate from the Analysis page.</p>
        </div>
      </div>
''', '''      <div class="page-header" style="display:none;">
        <div>
          <h2 class="page-title" style="display:none;">⚔️ CREED — Acceptance</h2>
        </div>
      </div>
''' + about('''
        <p>One strategy, run as taught: 4H battlefield &rarr; 1H pullback zone &rarr; 15M sweep &rarr; acceptance. Market, symbol and key below are CREED&rsquo;s own, separate from the Charts page. Without a Twelve Data key, forex comes from the OMEGA Live API and gold from its PAXG proxy.</p>
        <p>Read the reality check first: measured on about 11,000 setups, CREED behaves like a coin flip after costs. Use its verdict as structure, not as a promise.</p
'''.replace('</p\n', '</p>\n')))
o0 = s.index('    <div id="page-osig" class="page">'); o1 = s.index('    <div id="page-posdesk"', o0); oe = s.rindex('    </div>', o0, o1)
s = s[:oe] + about('''
        <p>Signals shows only rules that were tested fairly. <b>Grade A</b>: the climax reversal, passed on 324 untouched coins. <b>Grade B</b>: the panic bounce, passed with delisted coins included but lives on a few big rebounds. <b>Grade C</b>: the Daily Plan, a plan followed on paper, not a tested edge.</p>
        <p>Each card opens on its rule and current state; tap &ldquo;Show the full evidence&rdquo; for the research behind it. Everything here is paper: OMEGA places no orders. The full story is in About OMEGA.</p>
''') + s[oe:]

# ── 4. Bots ──
rep('''      <div id="omegaBotCard"></div>
      <div id="portfolioBot"></div>
      <div class="page-header">
        <div>
          <h2 class="page-title">🤖 Trading Bots <span class="hint" style="font-weight:400; font-size:12px;">— paper trading</span></h2>
          <p class="page-sub">Autonomous paper-trading agents. Pick a bot type below — each uses the same signal engine but a different trading style.</p>
        </div>
      </div>
''', '''      <details class="hv-fold hv-box"><summary class="hv-sum">OMEGA bot and Portfolio bot <span>controls, equity and trades</span></summary>
      <div id="omegaBotCard"></div>
      <div id="portfolioBot"></div>
      </details>
''')
b0 = s.index('    <div id="page-bot" class="page">'); b1 = s.index('    <div id="page-creed"', b0); be = s.rindex('    </div>', b0, b1)
s = s[:be] + about('''
        <p><b>The 24/7 bots</b> (top) run in the cloud and on the laptop Station: a paper bot trading only the approved rules, and the scouts&rsquo; forecasts, read from the OMEGA Live API every 2 minutes while this page is open.</p>
        <p><b>Your in-app bots</b> are autonomous paper-trading agents: each uses the same signal engine with a different trading style, and runs only while the app is open. Starting one asks you to confirm.</p>
        <p>Grades: A climax reversal, B panic bounce, C watch list (failed its final test; paper only). Nothing on this page places a real order.</p>
''') + s[be:]

CSS = r'''<style id="tidyCss">/* v6.5.114: folds, clamps and Heaven polish (theme variables only) */
details.hv-fold>summary{list-style:none;cursor:pointer}details.hv-fold>summary::-webkit-details-marker{display:none}
details.cmd-card.hv-fold>summary.cmd-card-head{margin-bottom:0}details.cmd-card.hv-fold[open]>summary.cmd-card-head{margin-bottom:10px}
details.hv-fold>summary h3::after,.hv-sum::after{content:'';display:inline-block;width:7px;height:7px;border-right:1.6px solid var(--text-dim);border-bottom:1.6px solid var(--text-dim);transform:rotate(45deg) translateY(-3px);margin-left:10px;transition:transform .2s}
details.hv-fold[open]>summary h3::after,details.hv-fold[open]>.hv-sum::after{transform:rotate(-135deg) translateY(-1px)}
.hv-sum{display:flex;align-items:center;flex-wrap:wrap;gap:4px 10px;font-weight:650;font-size:15px;color:var(--text);padding:2px 0;min-height:40px}.hv-sum span{font-weight:400;font-size:12.5px;color:var(--text-dim);order:2;flex-basis:100%}.hv-sum::after{order:1;margin-left:auto}
details.wl-room.hv-fold:not([open]){padding-bottom:12px}details.wl-room.hv-fold[open]>.hv-sum{margin-bottom:12px}
.hv-box{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:10px 16px;margin:0 0 14px}.hv-box[open]{padding-bottom:16px}
.hv-clamp:not(.hv-self)>:first-child,.hv-self{position:relative}.hv-clamp:not(.hv-self):not(.hv-open)>:first-child,.hv-self:not(.hv-open){max-height:430px;overflow:hidden;box-sizing:border-box}
.hv-clamp:not(.hv-self):not(.hv-open)>:first-child::after,.hv-self:not(.hv-open)::after{content:'Show the full evidence';position:absolute;left:0;right:0;bottom:0;height:86px;display:flex;align-items:flex-end;justify-content:center;padding-bottom:14px;box-sizing:border-box;background:linear-gradient(to bottom,transparent,var(--panel) 62%);font-weight:600;font-size:13px;color:var(--gold);cursor:pointer;z-index:2}
.hv-clamp:not(.hv-self).hv-open>:first-child::after,.hv-self.hv-open::after{content:'Show less';display:block;text-align:center;padding:10px 0 2px;font-weight:600;font-size:13px;color:var(--gold);cursor:pointer}
html[data-theme="heaven"] .hv-dash{display:none}
html[data-theme="heaven"] .ost-line,html[data-theme="heaven"] .ost-sheet{background:#FFFFFF}
html[data-theme="heaven"] .omega-bottomnav{background:rgba(255,255,255,.98)}
html[data-theme="heaven"] .page.active>:first-child{margin-top:12px}
html[data-theme="heaven"] .ac-buy[disabled]{background:#EEF1F6;border-color:#E3E7EF;color:#586274;opacity:1;filter:none}
html[data-theme="heaven"] .cmd-card.hv-fold:not([open]){padding-top:12px;padding-bottom:12px}
</style>
'''
JS = r'''<script>/* ═══ TIDY (v6.5.114): long evidence clamped to its first screen, the text kept in the page ═══ */
(function(){
  'use strict';
  var IDS = ['climaxSigBody', 'panicSigBody', 'dplanSigBody', 'creedReality'];
  function clamp(id){ var h = document.getElementById(id); if(!h || h.__hvClamp) return; h.__hvClamp = true; h.classList.add('hv-clamp'); if(h.classList.contains('card')) h.classList.add('hv-self');
    h.addEventListener('click', function(e){ var r = h.getBoundingClientRect(), t = e.target;
      if(t && t.closest && t.closest('a,button,input,select,textarea,summary,label')) return;
      if(!h.classList.contains('hv-open') ? e.clientY > r.bottom - 90 : e.clientY > r.bottom - 36){ h.classList.toggle('hv-open'); if(!h.classList.contains('hv-open')) try{ h.scrollIntoView({ block:'start' }); }catch(x){} } }); }
  function boot(){ IDS.forEach(clamp); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else setTimeout(boot, 0);
  window.OMEGA_TIDY = { clamp:clamp, IDS:IDS };
})();
</script>
'''
rep('</body>', CSS + JS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.113 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.113 ' + sep + ' build ' + o + ' UTC', 'v6.5.114 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.114 · build' in s and 'v6.5.113 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now, 'size', len(s.encode('utf-8')))
