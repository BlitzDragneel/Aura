"""v6.5.113: "Heaven" theme and the About OMEGA page. Look and documentation only: no rule, engine, data or research logic
changed; CREED's engine is byte-identical.
 1. New default theme `heaven`: soft white and pearl surfaces over a faint cool-blue/lavender wash, deep slate text
    (#1A2332 on white 15.8:1; secondary #586274 6.2:1), one refined accent (deep soft gold #8A6A1E, 5.1:1 on white),
    calm green/red for direction (#0B7D55 5.2:1, #B42F45 6.1:1), generous spacing, rounded cards with soft shadows,
    sentence-case headings in Inter / the system UI stack (no new font or CDN). Decorative glows, the banner "flow" pills
    and neon text shadows are switched off in this theme. Charts (lightweight-charts) get light backgrounds and grids.
    The theme is applied before first paint (a tiny inline script reads the saved setting), so there is no dark flash.
 2. Settings > Display > Theme lists Heaven first (default); Neon Glow and Dark (classic) stay selectable, with every
    other theme. One-time switch (flag omega_heaven113): a browser on neonglow or dark moves to Heaven once; any other
    chosen theme is kept, and she can pick Neon Glow or Dark again at any time. The accent setting does not apply here.
 3. About OMEGA page (menu "More" > About OMEGA, and a button at the top of Settings): everything in dropdowns, closed by
    default: what OMEGA is; every page; every signal and its grade with the measured evidence (handover section 3 and
    edges/RESULTS.md only); the bots; data sources; the Live API and token; the Academy; risk and leverage (measured
    liquidation results); privacy and backups; the progress board.
usage: python3 patch113.py <v6.5.112> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


H = 'html[data-theme="heaven"]'
CSS = """
/* ═══ v6.5.113 — HEAVEN theme (default; look only) ═══ */
html[data-theme="heaven"]{ color-scheme:light; --bg:#F6F8FC; --panel:#FFFFFF; --panel2:#F3F5FA; --border:#E3E7EF;
  --text:#1A2332; --text-dim:#586274; --bull:#0B7D55; --bear:#B42F45; --gold:#8A6A1E !important; --amber:#A15C0B; --violet:#5149B8;
  --halo:#D9C089; --sky:#E8F0FB; --lav:#F1EEFA; --hv-shadow:0 1px 2px rgba(26,35,50,.04), 0 6px 22px rgba(26,35,50,.055); --hv-radius:16px; }
html[data-theme="heaven"], html[data-theme="heaven"] body{ font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,system-ui,sans-serif; }
html[data-theme="heaven"] body{ background:
  radial-gradient(900px 420px at 10% -6%, rgba(205,220,246,.55), transparent 62%),
  radial-gradient(800px 420px at 100% 0%, rgba(232,224,248,.50), transparent 60%),
  linear-gradient(180deg, #F7F9FD 0%, #FAFAFC 55%, #FBFAF6 100%) fixed; color:var(--text); }
html[data-theme="heaven"] *{ text-shadow:none !important; }
html[data-theme="heaven"] ::selection{ background:#EADFBF; }
html[data-theme="heaven"] h1, html[data-theme="heaven"] h2, html[data-theme="heaven"] h3, html[data-theme="heaven"] h4{ color:var(--text); letter-spacing:-.01em; }
/* header, menu, bottom bar */
html[data-theme="heaven"] .mobile-header{ background:rgba(255,255,255,.86); -webkit-backdrop-filter:saturate(1.4) blur(14px); backdrop-filter:saturate(1.4) blur(14px); border-bottom:1px solid rgba(227,231,239,.9); }
html[data-theme="heaven"] .mh-brand{ font-family:'Inter',system-ui,sans-serif; letter-spacing:.14em; font-weight:700; color:var(--text); font-size:14px; }
html[data-theme="heaven"] .mh-brand small{ letter-spacing:0; font-weight:500; color:#8A93A3; font-size:10.5px; }
html[data-theme="heaven"] .mh-glyph, html[data-theme="heaven"] .sidebar-brand .glyph{ color:var(--gold); animation:none; }
html[data-theme="heaven"] .hamburger{ background:#fff; border-color:var(--border); color:var(--text); box-shadow:0 1px 2px rgba(26,35,50,.05); border-radius:12px; }
html[data-theme="heaven"] .sidebar{ background:rgba(255,255,255,.97); border-right:1px solid var(--border); box-shadow:8px 0 30px rgba(26,35,50,.06); }
html[data-theme="heaven"] .sidebar-scrim{ background:rgba(26,35,50,.22); -webkit-backdrop-filter:blur(2px); backdrop-filter:blur(2px); }
html[data-theme="heaven"] .sidebar-brand .sb-titles h1{ font-family:'Inter',system-ui,sans-serif; letter-spacing:.16em; }
html[data-theme="heaven"] .sb-banner{ background:linear-gradient(135deg,#FBF7EC,#F6F8FC); border-color:#EEE3C8; }
html[data-theme="heaven"] .sidebar-menu li{ color:#465063; }
html[data-theme="heaven"] .sidebar-menu li:hover{ background:var(--panel2); transform:none; }
html[data-theme="heaven"] .sidebar-menu li.active{ background:#F6F1E4; color:var(--text); border-color:transparent; font-weight:600; }
html[data-theme="heaven"] .sidebar-menu li.sb-tier{ color:#8A93A3; letter-spacing:.12em; }
html[data-theme="heaven"] .omega-bottomnav{ background:rgba(255,255,255,.92); -webkit-backdrop-filter:saturate(1.4) blur(16px); backdrop-filter:saturate(1.4) blur(16px); border-top:1px solid var(--border); box-shadow:0 -4px 20px rgba(26,35,50,.04); }
html[data-theme="heaven"] .omega-bottomnav button{ color:#7B8495; }
html[data-theme="heaven"] .omega-bottomnav button.active{ color:var(--gold); }
html[data-theme="heaven"] .omega-bottomnav button.active i{ transform:translateY(-1px); }
html[data-theme="heaven"] .ost-line, html[data-theme="heaven"] .ost-sheet{ background:rgba(255,255,255,.96); }
html[data-theme="heaven"] .ost-sheet{ box-shadow:0 -10px 30px rgba(26,35,50,.10); border-top-color:var(--border); }
/* surfaces */
html[data-theme="heaven"] .card, html[data-theme="heaven"] .ad-card, html[data-theme="heaven"] .dp-card, html[data-theme="heaven"] .om-card,
html[data-theme="heaven"] .chart-panel, html[data-theme="heaven"] .analysis-controls-bar, html[data-theme="heaven"] .wl-room, html[data-theme="heaven"] .fl-room,
html[data-theme="heaven"] .creed-watch, html[data-theme="heaven"] .creed-verdict, html[data-theme="heaven"] .creed-stage, html[data-theme="heaven"] .brief-q,
html[data-theme="heaven"] .cmd-product, html[data-theme="heaven"] .an-deep, html[data-theme="heaven"] .om-about, html[data-theme="heaven"] .ab-sec{
  background:var(--panel); border:1px solid var(--border); border-radius:var(--hv-radius); box-shadow:var(--hv-shadow); }
html[data-theme="heaven"] .creed-verdict, html[data-theme="heaven"] .creed-stage{ border-left-width:3px; }
html[data-theme="heaven"] .fl-room{ background:var(--panel); }
html[data-theme="heaven"] .card:hover{ box-shadow:var(--hv-shadow); }
html[data-theme="heaven"] .card h2, html[data-theme="heaven"] .chart-panel h2{ font-family:'Inter',system-ui,sans-serif; font-size:15px; font-weight:650; letter-spacing:-.005em; text-transform:none; color:var(--text); }
html[data-theme="heaven"] .card h2[style*="gold"]{ color:var(--text) !important; }
html[data-theme="heaven"] .dp-h, html[data-theme="heaven"] .cmd-card-head h3{ color:var(--text); text-transform:none; letter-spacing:-.005em; font-size:15px; font-weight:650; }
html[data-theme="heaven"] .page-title{ font-family:'Inter',system-ui,sans-serif; letter-spacing:-.015em; font-weight:700; }
html[data-theme="heaven"] .hint, html[data-theme="heaven"] .page-sub{ color:var(--text-dim); }
html[data-theme="heaven"] .ck-time, html[data-theme="heaven"] .bn-stat b, html[data-theme="heaven"] .watch-tab .wt-sym, html[data-theme="heaven"] .creed-ohlc b,
html[data-theme="heaven"] .cmd-product b, html[data-theme="heaven"] .fl-room-head h2, html[data-theme="heaven"] .fl-top b, html[data-theme="heaven"] .wl-room h2,
html[data-theme="heaven"] .rz-head b, html[data-theme="heaven"] .op-room h2, html[data-theme="heaven"] .brief-q h3, html[data-theme="heaven"] .creed-banner-title,
html[data-theme="heaven"] .creed-ptab.active{ color:var(--text); }
html[data-theme="heaven"] .brief-list li.bad{ color:var(--amber); }
html[data-theme="heaven"] .creed-ptab.active{ background:#F6F1E4; border-color:#E8DCBC; }
/* hero banners: calm, no glow, no decorative pills */
html[data-theme="heaven"] .creed-banner{ background:linear-gradient(135deg,#FFFFFF 0%,#F7F9FD 55%,#FAF6EC 100%); border:1px solid #ECE6D6; box-shadow:var(--hv-shadow); border-radius:20px; padding:20px 20px 18px; animation:none; }
html[data-theme="heaven"] .creed-banner-glow, html[data-theme="heaven"] .creed-banner-flow{ display:none; }
html[data-theme="heaven"] .creed-banner-kicker{ font-family:'Inter',system-ui,sans-serif; font-size:10.5px; font-weight:600; letter-spacing:.18em; color:var(--gold); }
html[data-theme="heaven"] .creed-banner-title{ font-family:'Inter',system-ui,sans-serif; font-size:24px; font-weight:700; letter-spacing:-.02em; margin:6px 0 2px; line-height:1.25; }
html[data-theme="heaven"] .creed-banner-title span{ display:block; margin-top:4px; font-size:13.5px; font-weight:400; letter-spacing:0; color:var(--text-dim); line-height:1.5; }
html[data-theme="heaven"] .omega-clock .ck-time{ font-weight:600; }
/* controls */
html[data-theme="heaven"] .btn, html[data-theme="heaven"] .btn-primary, html[data-theme="heaven"] .ad-btn.primary, html[data-theme="heaven"] .btn.primary{
  background:#1E2A3B; color:#fff; border:1px solid #1E2A3B; box-shadow:0 1px 2px rgba(26,35,50,.12); border-radius:10px; font-weight:600; filter:none; }
html[data-theme="heaven"] .btn:hover, html[data-theme="heaven"] .btn-primary:hover, html[data-theme="heaven"] .ad-btn.primary:hover{ background:#2A3850; box-shadow:0 2px 10px rgba(26,35,50,.16); filter:none; }
html[data-theme="heaven"] #page-creed .btn-primary, html[data-theme="heaven"] #page-bot .btn-primary{ background:#1E2A3B; color:#fff; border-color:#1E2A3B; box-shadow:0 1px 2px rgba(26,35,50,.12); }
html[data-theme="heaven"] .btn-outline, html[data-theme="heaven"] .ad-btn{ background:#fff; border:1px solid #D8DEE8; color:var(--text); border-radius:10px; }
html[data-theme="heaven"] .btn-outline:hover, html[data-theme="heaven"] .ad-btn:hover, html[data-theme="heaven"] .an-seg button:hover{ border-color:var(--halo); box-shadow:0 0 0 3px rgba(217,192,137,.18); }
html[data-theme="heaven"] .btn-ghost{ background:transparent; border:1px solid #E6DCC0; color:var(--gold); border-radius:10px; }
html[data-theme="heaven"] .btn-ghost:hover{ background:#FBF7EC; }
html[data-theme="heaven"] .set-tab{ background:#fff; border-radius:999px; }
html[data-theme="heaven"] .set-tab.active{ background:#1E2A3B; border-color:#1E2A3B; color:#fff; }
html[data-theme="heaven"] input, html[data-theme="heaven"] select, html[data-theme="heaven"] textarea{ background:#fff; color:var(--text); border:1px solid #D8DEE8; border-radius:10px; }
html[data-theme="heaven"] input:focus, html[data-theme="heaven"] select:focus, html[data-theme="heaven"] textarea:focus{ outline:none; border-color:#C9AE6E; box-shadow:0 0 0 3px rgba(217,192,137,.25); }
html[data-theme="heaven"] th{ color:#6B7486; background:#F7F8FB; font-weight:600; }
html[data-theme="heaven"] td, html[data-theme="heaven"] th{ border-color:#EDF0F5; }
/* notices */
html[data-theme="heaven"] .notice-banner, html[data-theme="heaven"] .bot-notice, html[data-theme="heaven"] .orch-conflicts{ background:#FFF8EC; border-color:#F0D9A8; color:#7A4F0A; }
html[data-theme="heaven"] .paper-banner{ background:linear-gradient(160deg,#FFFBF2,#FFFFFF); border:1px solid #EEDFBD; }
html[data-theme="heaven"] .paper-banner-badge{ font-family:'Inter',system-ui,sans-serif; font-size:12px; letter-spacing:.14em; border-color:#E6D3A6; }
html[data-theme="heaven"] .cmdk-box{ border-color:var(--border); box-shadow:0 24px 60px rgba(26,35,50,.18); }
html[data-theme="heaven"] .dot, html[data-theme="heaven"] .fl-state i{ background:#C5CCD8; }
html[data-theme="heaven"] .fl-card{ border-left-color:#C5CCD8; background:var(--panel2); }
/* charts */
html[data-theme="heaven"] #creedChartTV, html[data-theme="heaven"] #creedChartSVG{ background:#fff; box-shadow:var(--hv-shadow); }
html[data-theme="heaven"] #creedTvContainer{ box-shadow:var(--hv-shadow); }
html[data-theme="heaven"] .omega-cux button{ background:rgba(255,255,255,.92) !important; color:var(--gold) !important; border-color:#E3D6B4 !important; }
html[data-theme="heaven"] [data-omega-fs="1"]{ background:#fff !important; }
/* first-load mark */
html[data-theme="heaven"] #omegaIntro{ background:radial-gradient(circle at 50% 42%, rgba(217,192,137,.20) 0%, transparent 55%), radial-gradient(ellipse at 50% 45%, #FFFFFF 0%, #EEF2F9 78%); }
html[data-theme="heaven"] #omegaIntro::before{ background-image:linear-gradient(rgba(138,106,30,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(138,106,30,.06) 1px, transparent 1px); }
html[data-theme="heaven"] #omegaIntro::after{ background:radial-gradient(ellipse at 50% 45%, transparent 35%, #F2F5FA 82%); }
html[data-theme="heaven"] .oi-name .oi-l{ color:var(--text); }
html[data-theme="heaven"] .oi-glyph{ text-shadow:none; }
html[data-theme="heaven"] .oi-rings span{ border-color:rgba(138,106,30,.28); }
html[data-theme="heaven"] ::-webkit-scrollbar{ width:10px; height:10px; } html[data-theme="heaven"] ::-webkit-scrollbar-thumb{ background:#D5DBE5; border-radius:10px; border:2px solid transparent; background-clip:padding-box; }
@media (max-width:719px){ html[data-theme="heaven"] .creed-banner-title{ font-size:21px; } }
"""
m = re.search(r'@media \(prefers-reduced-motion: reduce\)\{ html\[data-theme="neonglow"\] \.mh-glyph\{ animation:none; \} \}\n', s)
assert m and s.count(m.group(0)) == 1
rep(m.group(0), m.group(0) + CSS)

# 1b. no dark flash: apply the saved theme before first paint (same rule as the one-time switch below)
rep('<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
    '<script>/* v6.5.113: theme before first paint */try{var _o=JSON.parse(localStorage.getItem(\'omega_settings_v3\')||\'{}\'),_t=_o&&_o.setTheme;'
    'if(!_t||(!localStorage.getItem(\'omega_heaven113\')&&(_t===\'neonglow\'||_t===\'dark\')))_t=\'heaven\';if(_t!==\'dark\')document.documentElement.setAttribute(\'data-theme\',_t);}catch(e){}</script>\n')

# 2. theme option + one-time switch
rep('            <option value="neonglow" selected>Neon Glow (default)</option>\n            <option value="dark">Dark (classic)</option>\n',
    '            <option value="heaven" selected>Heaven (default)</option>\n            <option value="neonglow">Neon Glow</option>\n            <option value="dark">Dark (classic)</option>\n')
rep("      localStorage.setItem('omega_neon108','1'); applyTheme(); } }catch(e){}\n",
    "      localStorage.setItem('omega_neon108','1'); applyTheme(); } }catch(e){}\n"
    "    try{ if(!localStorage.getItem('omega_heaven113')){ var th2=document.getElementById('setTheme');   // v6.5.113: one-time move to Heaven\n"
    "      if(th2 && (th2.value==='neonglow' || th2.value==='dark')){ th2.value='heaven'; saveSettings(); }\n"
    "      localStorage.setItem('omega_heaven113','1'); applyTheme(); } }catch(e){}\n")
rep("    if(t === 'dark'){ document.documentElement.removeAttribute('data-theme'); }\n    else { document.documentElement.setAttribute('data-theme', t); }\n",
    "    if(t === 'dark'){ document.documentElement.removeAttribute('data-theme'); }\n    else { document.documentElement.setAttribute('data-theme', t); }\n"
    "    try{ var mt = document.querySelector('meta[name=\"theme-color\"]'); if(mt) mt.setAttribute('content', t === 'heaven' ? '#F6F8FC' : '#0A0D12'); if(window.OMEGA_HEAVEN) window.OMEGA_HEAVEN.charts(); }catch(e){}   // v6.5.113\n")

# 3. About OMEGA page
def sec(title, body):
    return '        <details class="ab-sec"><summary>' + title + '</summary><div class="ab-body">\n' + body.strip('\n') + '\n        </div></details>\n'

PAGES = [
    ('Home', 'The start of every session: what is happening, what is actionable, what needs you, the bots at a glance, and the trades OMEGA sees now. A strong bias with no permission is a reason to wait.'),
    ('Charts (Analysis)', 'One market in depth: candles, structure, liquidity, a trade plan and its reasoning (the classic SMC engine, not a tested OMEGA idea), the Daily Plan, events ahead, the market cockpit and a scan of every market.'),
    ('Forex board', 'Every major, minor and exotic pair and the metals, live from Swissquote through the Live API: price, spread and whether the market is open. Tap a pair to chart it.'),
    ('Market Read (mark-up)', 'What is going on now, which side to trade, today&rsquo;s plan, and where liquidity sits (stops above and below, resting orders, who is crowded).'),
    ('Market Intelligence', 'OMEGA&rsquo;s own engine reading many markets on several timeframes, with its own conclusions; also the market clock (sessions, CPI/FOMC calendar).'),
    ('Live Market Data', 'Beyond candles: order books, other venues, options volatility and crowd positioning, checked later against what price did.'),
    ('Signals', 'Only what has been tested: the climax reversal (A), the panic bounce (B), the Daily Plan (C) and the evidence note.'),
    ('CREED Desk', 'The CREED method run exactly as taught (4H battlefield, 1H pullback, 15M sweep, acceptance) on three markets, with its reality check first.'),
    ('CREED Scanner', 'The CREED method across many markets, with a timeframe ladder for context. CREED alone decides whether a setup exists.'),
    ('Bots', 'Every in-app paper bot at a glance, plus the 24/7 cloud bots and scouts from the Live API.'),
    ('Risk Guard &amp; Growth Bot', 'The risk rules every trade must pass, the Growth Bot that follows them on paper, and the review of how the rules held.'),
    ('Autopilot', 'The jobs that read markets, keep signals current and run the paper bots while the app is open.'),
    ('Positioning Desk', 'Who is crowded, who pays whom (funding), and how hard it can fall.'),
    ('Futures', 'Perpetual futures maths with your margin and leverage: fees, funding, liquidation distance, and a paper account.'),
    ('Journal', 'Every closed trade from every part of OMEGA, with review notes on why each may have worked or failed.'),
    ('Growth &amp; Routine', 'Your real edge in dollars, how fast it can compound at a sustainable pace, and a daily routine.'),
    ('Brain', 'What OMEGA knows, how sure it should be, its prediction scorecard and evidence ledger.'),
    ('Academy', 'The course: markets, chart reading, risk first, and how to test an idea before trusting it; with quizzes and progress.'),
    ('Settings', 'Trading thresholds, display and theme, data sources and keys, the Live API token, backups.'),
]
ABOUT = '''    <div id="page-about" class="page">
      <header class="om-head ab-hero"><p class="ab-kicker">About</p><h2>OMEGA, explained</h2>
        <p>Everything OMEGA does, where its data comes from, and what the evidence says. Open any section.</p></header>
      <div class="ab-list">
''' + sec('What OMEGA is', '''
          <p>OMEGA is a trading companion that runs in your browser. It reads crypto, forex and metals markets, shows them clearly, tests ideas with fair rules before trusting them, and runs <b>paper</b> bots so a rule can prove itself on live prices first.</p>
          <p><b>It places no real orders.</b> Nothing in this app is connected to a broker. Your data stays on this device unless you download a backup.</p>
          <p>Its standing rules: never invent data; plan a test before looking at the data and count every try; paper first; no secrets in files or backups.</p>
''') + sec('Every page and what it is for', '<dl class="ab-dl">\n' + '\n'.join('          <dt>' + a + '</dt><dd>' + b + '</dd>' for a, b in PAGES) + '\n          </dl>') + sec('Signals, grades and the evidence behind them', '''
          <p>Every test was planned and fingerprinted before its data and run once; results are after trading costs.</p>
          <h4><span class="om-tag ga">Grade A</span> Climax reversal</h4>
          <p>A 3&sigma; hourly drop on 3&times; normal volume that closes in the top 40% of its range: buy the next open, hold 12 hours. It passed on 324 untouched coins. Over all perpetuals in 2025&ndash;26 it still averaged +109 bp a trade, but not significantly (t 0.78), so its forward record decides.</p>
          <h4><span class="om-tag gb">Grade B</span> Panic bounce (H1 and H3)</h4>
          <p>Buying coins that fell far below their own normal range. Plan E22: H1 +0.36% a trade (t 4.34), H3 +0.22% (t 3.63). E25, with 143 delisted coins included (883 coins): H1 +0.32% (t 4.54), H3 +0.30% (t 4.08).</p>
          <p class="ab-warn">It lives on the big rebounds: without the best 5% of trades each version loses about 0.7% a trade, and single trades lost 77&ndash;93%. Run as a 100 USDT account (E26) it had drawdowns of 56% and 59%. In 2025&ndash;26 its edge was +18 bp a trade (t 0.59): positive, not significant.</p>
          <h4><span class="om-tag gc">Grade C</span> Watch list and the Daily Plan</h4>
          <p>Ideas that failed their final test but stay on paper to be watched: the panic bounce on 5- and 15-minute bars (E37 +31.8 bp, t 1.05; E38 +2.8 bp, t 0.10), the market-wide 15-minute panic (E40 +24.7 bp, t 0.74) and the UpScout top-2% longs (E81). Without their best 5% of trades E37 and E40 lose (&minus;32.7 and &minus;44.1 bp). They are never real trades. The <b>Daily Plan</b> is grade C too: a written plan per coin, followed on paper, not a tested edge.</p>
          <h4>CREED: measured as a coin flip</h4>
          <p>After a CREED setup, price behaves like a fair coin: it reached +1R before the stop 49% of the time against 50% for chance. Per trade after costs: &minus;0.118R, &minus;0.100R and &minus;0.118R on three coin sets (about 11,000 setups). Longs-only, BTC-context, panic-gated and volatility-buffer versions all failed on untouched coins (E29, E31). In 100,000 simulated accounts, CREED at 1% risk lost half the account within a year in 76% of them. Treat a CREED &ldquo;Ready&rdquo; as structure, not a promise.</p>
          <h4>What failed</h4>
          <p>Daily-trading rules (12,480 tried, E28), order-book depth and crowd positioning (E30), a neural network (E32), funding harvest (E34: +8.8% a year in 2021&ndash;24, &minus;17% a year in 2025&ndash;26), forex majors hour by hour (E15), trend, momentum and funding rules (E50&ndash;E55), new data sources (E63&ndash;E70) and exit tweaks (E80: the original exits were best). The lesson: size is predictable, direction is not; panic selling gets overdone.</p>
''') + sec('The bots', '''
          <p><b>In-app bots</b> (Bots page): the OMEGA bot, CREED bots 1 and 2, the Confluence bot and the Portfolio bot, and the Growth Bot on the Risk Guard page. All trade on paper against real prices and run only while the app is open.</p>
          <p><b>24/7 cloud bots</b>: a paper bot runs every hour on GitHub and trades only the approved rules (A, B, and the C watch list on paper). Its positions, resting orders and recent actions are published on the bot-state branch. The <b>laptop Station</b> runs the same bot and scouts when the laptop is on; the Live API reads the Station when it runs next to it, otherwise the cloud record.</p>
          <p><b>Scouts</b>: UpScout and DownScout forecast a big move in the next 24 hours from hourly candles (E81), the fast scouts the next 4 hours from 15-minute candles (E82). They see big moves coming but failed as trading rules, so they are scored forward against the base rate and feed no bot.</p>
          <p>Everything the bots show is <b>paper or forecast information</b>, never an order.</p>
''') + sec('Data sources', '''
          <dl class="ab-dl">
          <dt>Binance and OKX</dt><dd>Crypto candles, prices, order books, funding and open interest (Bybit and Kraken as fallbacks). Gold and silver also trade as Binance perpetuals (XAUUSDT, XAGUSDT), so they work without a key.</dd>
          <dt>Swissquote</dt><dd>Live forex and metals bid/ask, through the OMEGA Live API.</dd>
          <dt>Yahoo</dt><dd>Forex candles through the Live API when no Twelve Data key is set (1 hour back 2 years, 15 minutes back 60 days, 5 minutes back 5 days). Metal candles are futures (GC, SI, PL, PA): a proxy, not spot.</dd>
          <dt>Deribit</dt><dd>BTC and ETH implied volatility (DVOL).</dd>
          <dt>Twelve Data</dt><dd>Forex and metals candles with your own free key (8 requests a minute, 800 a day). With a key in this browser it is always used first.</dd>
          </dl>
''') + sec('The Live API and your token', '''
          <p>The OMEGA Live API is a small read-only server (default <code>https://omega-live-api.onrender.com</code>) that gathers forex quotes and candles, crypto data and the bots feed. It never places orders and holds no exchange keys.</p>
          <p>Its address and your <b>token</b> live in Settings &rsaquo; Data &amp; Keys. The token is kept on this device only, like an API key: it is never written into a backup and a backup file can never set it. Health, the pair list and the Academy are public; prices, candles and the bots feed need the token. A server that has slept takes about a minute to wake.</p>
''') + sec('The Academy', '''
          <p>A course on markets, chart reading, risk first and testing an idea before trusting it, with quizzes and progress kept on this device. Modules 1 and 2 and the first lesson of every module are free and also built into the app for offline reading; the rest unlocks with a license key. The tutorial can be reopened from the Academy or Settings.</p>
''') + sec('Risk and leverage', '''
          <p>The Risk Guard rules: 0.5% of the account a trade, at most 2 open, stop trading after &minus;2% in a day or &minus;5% in a week.</p>
          <p class="ab-warn"><b>Measured leverage</b> on the short-timeframe panic trades (E37, E38, E40; 5% margin a trade): at 1&times; no liquidations (drawdown 10&ndash;15%); <b>2&times; already liquidates</b>; at 20&times; 29&ndash;31% of trades hit the liquidation distance and the account goes to about 1 USDT; <b>40&times; liquidates about 60% of trades</b>. The worst move inside one bar was &minus;83% (October 2025).</p>
          <p>No strategy tested turned 100 into 1,000,000 in 5 simulated years. Trading carries a high risk of losing money; leverage can lose the whole deposit quickly.</p>
''') + sec('Privacy and backups', '''
          <p>Everything (journal, settings, progress) is stored in this browser. Nothing leaves it except the requests for market data, the Live API and the Academy, and what you set up yourself (alerts, the Claude council with your own key).</p>
          <p>A backup file leaves out every API key and token, the alert webhook and your WhatsApp number; restoring a file can never set them. Re-enter keys after restoring on a new device. The app only runs scripts from itself and its chart library (Content-Security-Policy).</p>
''') + sec('The progress board', '''
          <p>Research ideas, tests, verdicts and the live bots&rsquo; records are published on the progress board: <a href="https://omega-board.onrender.com" target="_blank" rel="noopener">omega-board.onrender.com</a>.</p>
''') + '''      </div>
      <p class="om-meta ab-ver" id="aboutVersion"></p>
    </div>
'''
rep('    <div id="page-academy" class="page">', ABOUT + '    <div id="page-academy" class="page">')
rep('''      <li data-page="settings" onclick="navigate('settings')"><span class="sb-icon">⚙️</span> Settings</li>\n''',
    '''      <li data-page="settings" onclick="navigate('settings')"><span class="sb-icon">⚙️</span> Settings</li>\n      <li data-page="about" onclick="navigate('about')"><span class="sb-icon">ⓘ</span> About OMEGA</li>\n''')
rep("'posdesk','academy','forex'];", "'posdesk','academy','forex','about'];")
rep("['forex','Forex board'],", "['forex','Forex board'],['about','About OMEGA'],")
rep('''          <h2 class="page-title">⚙️ Settings</h2>
          <p class="page-sub">Configure trading thresholds, AI behaviour, display and data sources.</p>
''', '''          <h2 class="page-title">⚙️ Settings</h2>
          <p class="page-sub">Configure trading thresholds, AI behaviour, display and data sources.</p>
          <p style="margin:10px 0 0;"><button class="btn-ghost" type="button" id="setAboutBtn" onclick="navigate('about')">About OMEGA — how everything works</button></p>
''')

ABCSS = r'''<style id="aboutCss">/* v6.5.113: About OMEGA (theme variables only) */
.ab-hero{margin:4px 0 16px}.ab-kicker{margin:0 0 2px!important;font-size:11px!important;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--gold)!important}
.ab-list{display:flex;flex-direction:column;gap:10px}
.ab-sec{background:var(--panel);border:1px solid var(--border);border-radius:16px;overflow:hidden}
.ab-sec>summary{cursor:pointer;list-style:none;padding:15px 18px;font-weight:600;font-size:15px;color:var(--text);display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:48px;box-sizing:border-box}
.ab-sec>summary::-webkit-details-marker{display:none}
.ab-sec>summary::after{content:'';flex:none;width:8px;height:8px;border-right:1.6px solid var(--text-dim);border-bottom:1.6px solid var(--text-dim);transform:rotate(45deg);transition:transform .2s;margin-right:4px}
.ab-sec[open]>summary::after{transform:rotate(-135deg)}.ab-sec[open]>summary{border-bottom:1px solid var(--border)}
.ab-body{padding:14px 18px 16px;font-size:14px;line-height:1.65;color:var(--text)}.ab-body p{margin:0 0 10px;color:var(--text-dim)}.ab-body p b{color:var(--text)}
.ab-body h4{margin:16px 0 6px;font-size:14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}.ab-body h4:first-of-type{margin-top:4px}
.ab-body code{font-size:12.5px;background:var(--panel2);padding:1px 6px;border-radius:6px;overflow-wrap:anywhere}
.ab-dl{margin:0;display:grid;grid-template-columns:minmax(120px,170px) 1fr;gap:8px 16px}.ab-dl dt{font-weight:600;color:var(--text);font-size:13.5px}.ab-dl dd{margin:0;color:var(--text-dim);font-size:13.5px}
@media (max-width:560px){.ab-dl{grid-template-columns:1fr;gap:2px}.ab-dl dd{margin-bottom:10px}}
.ab-warn{border-left:3px solid var(--amber);padding-left:10px}.ab-ver{text-align:center;margin:18px 0 8px}
</style>
'''
HJS = r'''<script>/* ═══ HEAVEN helpers (v6.5.113): light charts in the Heaven theme; the About page's version line ═══ */
(function(){
  'use strict';
  function heaven(){ return document.documentElement.getAttribute('data-theme') === 'heaven'; }
  var LIGHT = { layout:{ background:{ type:'solid', color:'#FFFFFF' }, textColor:'#586274' }, grid:{ vertLines:{ color:'#EEF1F6' }, horzLines:{ color:'#EEF1F6' } },
    rightPriceScale:{ borderColor:'#E3E7EF' }, leftPriceScale:{ borderColor:'#E3E7EF' }, timeScale:{ borderColor:'#E3E7EF' }, crosshair:{ vertLine:{ color:'#B9C1CF' }, horzLine:{ color:'#B9C1CF' } } };
  var DARK = { layout:{ background:{ type:'solid', color:'#0A0D12' }, textColor:'#8995A8' }, grid:{ vertLines:{ color:'#171C24' }, horzLines:{ color:'#171C24' } },
    rightPriceScale:{ borderColor:'#212834' }, leftPriceScale:{ borderColor:'#212834' }, timeScale:{ borderColor:'#212834' } };
  var made = [];
  function paint(c){ try{ c.applyOptions(heaven() ? LIGHT : DARK); }catch(e){} }
  var LW = window.LightweightCharts;
  if(LW && typeof LW.createChart === 'function' && !LW.createChart.__heaven){
    var orig = LW.createChart; var wrapped = function(){ var c = orig.apply(this, arguments); try{ made.push(c); if(heaven()) paint(c); }catch(e){} return c; };
    wrapped.__heaven = true; try{ LW.createChart = wrapped; }catch(e){ try{ window.LightweightCharts = Object.assign({}, LW, { createChart:wrapped }); }catch(x){} } }
  function charts(){ var all = made.slice(); try{ (window.OMEGA_CHARTUX ? window.OMEGA_CHARTUX.charts() : []).forEach(function(x){ if(x && x.chart && all.indexOf(x.chart) < 0) all.push(x.chart); }); }catch(e){}
    all.forEach(paint); }
  function version(){ var v = document.getElementById('aboutVersion'), b = document.querySelector('.mh-brand small'); if(v && b) v.textContent = 'OMEGA ' + b.textContent + ' · information only, never an order'; }
  function boot(){ version(); if(heaven()) setTimeout(charts, 50); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else setTimeout(boot, 0);
  window.addEventListener('load', function(){ if(heaven()) setTimeout(charts, 300); });
  window.OMEGA_HEAVEN = { charts:charts, on:heaven };
})();
</script>
'''
rep('</body>', ABCSS + HJS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.112 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.112 ' + sep + ' build ' + o + ' UTC', 'v6.5.113 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.113 · build' in s and 'v6.5.112 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now, 'size', len(s.encode('utf-8')))
