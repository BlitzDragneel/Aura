"""v6.5.112: all Forex on OMEGA, and the 24/7 bots feeding OMEGA. Data come from the OMEGA Live API (the lead's server,
omega/live_api). CREED's ENGINE is byte-identical; only its data source gets a one-line fallback (see 3).
 1. Settings > Data & Keys: "Live API token" next to the server address (the Academy's, default
    https://omega-live-api.onrender.com). Stored only on this device as omega_live_token: the backup code already leaves out
    and never restores any store ending in _token (patch107's isSecretKey), and the token's value is also cut out of every
    other store in a backup. "Test connection" calls /health and one data endpoint.
 2. window.OMEGA_LAPI: one client for the server (Authorization: Bearer <token>), plus a fetch-level fallback: when the
    browser has NO Twelve Data key and a token is set, a Twelve Data candle request (api.twelvedata.com/time_series) is
    answered from {server}/fx/klines and handed back in Twelve Data's own format (newest first, datetime UTC). Intervals the
    server lacks (30min, 2h, 12h, 1week, 1month...) are built from smaller candles. With a key, nothing changes.
 3. The places that refused to fetch without a key now also accept the Live API: Charts/Analysis (fetchCandles; no
    Twelve Data throttle or daily budget for server calls), the CREED desk (one line in its fetchTD: key = the Live API
    marker; the method, analyseSeries and walkExit are untouched), the CREED Scanner, Market Intelligence. Gold without a
    key keeps its PAXG proxy, as before. Key hints say when the Live API covers forex.
 4. Forex page (Charts tab "Forex board", menu and More): every pair the server lists, grouped Majors / Minors / Exotics /
    Metals: mid price, bid/ask, spread (pips; metals in dollars) and "Market closed" when Swissquote's quote is stale.
    Refreshes every 20 s while open. Tapping a pair opens it on Charts and runs the analysis. Metals candles from Yahoo are
    futures (GC/SI/PL/PA): the source is shown with the chart.
 5. Bots feed (Bots page, compact card on Home) from {server}/bots/feed: the paper bot's open positions and resting orders
    per rule with its grade (A climax, B panic bounce, C watch list = paper only), recent actions, and the scouts' strongest
    up/down calls with their forward hit rate against the base rate. Marked PAPER / FORECAST. Refreshes every 2 minutes
    while visible, with "last updated".
usage: python3 patch112.py <v6.5.111> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


# ── 1. Settings: token next to the server address ──
rep('        <h2 style="color:var(--gold);">Academy server and tutorial</h2>\n',
    '        <h2 style="color:var(--gold);">OMEGA Live API, Academy and tutorial</h2>\n')
rep('''        <p class="hint" id="acadServerMsg" style="margin-bottom:0;">Lessons, unlocking and premium lessons come from this address. Free lessons are also built into the app for offline reading.</p>
''', '''        <p class="hint" id="acadServerMsg" style="margin-bottom:0;">Lessons, unlocking and premium lessons come from this address. Free lessons are also built into the app for offline reading.</p>
        <div class="settings-grid" style="margin-top:12px;"><div class="field"><label>Live API token (forex prices and candles, the bots feed)</label>
          <input type="password" id="liveTokenInput" autocomplete="off" spellcheck="false" placeholder="Paste the token for this server" /></div></div>
        <div class="journal-actions" style="margin-top:8px;"><button class="btn-ghost" type="button" id="liveTokenSave">Save token</button>
          <button class="btn-ghost" type="button" id="liveTokenTest">Test connection</button><button class="btn-ghost" type="button" id="liveTokenClear">Remove token</button></div>
        <p class="hint" id="liveTokenMsg" style="margin-bottom:0;">Kept on this device only, like an API key: never written into a backup and never taken from one.</p>
''')

# ── 3a. Charts / Analysis ──
rep("    if(!apikey) throw new Error('Enter a Twelve Data API key to analyze ' + (assetClass==='metals'?'gold/silver':'forex') + ' pairs. Get a free key at twelvedata.com.');\n"
    "    const candles = await fetchTwelveData(symbol, interval, apikey, 300);\n"
    "    return { candles: candles, source: 'Twelve Data' };\n",
    "    const LK = window.OMEGA_LAPI ? window.OMEGA_LAPI.KEY : null;\n"
    "    if(!apikey && window.OMEGA_LAPI && window.OMEGA_LAPI.on()) apikey = LK;   // v6.5.112: no Twelve Data key -> OMEGA Live API\n"
    "    if(!apikey) throw new Error('Enter a Twelve Data API key, or the OMEGA Live API token (Settings > Data & Keys), to analyze ' + (assetClass==='metals'?'gold/silver':'forex') + ' pairs.');\n"
    "    const candles = await fetchTwelveData(symbol, interval, apikey, 300);\n"
    "    return { candles: candles, source: apikey === LK ? 'OMEGA Live API \\u00b7 ' + window.OMEGA_LAPI.sourceOf(symbol) : 'Twelve Data' };\n")
rep("    if(window.OMEGA_TD && typeof window.OMEGA_TD.acquire === 'function') await window.OMEGA_TD.acquire('analysis');\n    await tdThrottle();\n",
    "    const viaLive = !!(window.OMEGA_LAPI && apikey === window.OMEGA_LAPI.KEY);   // v6.5.112: the server has its own limits\n"
    "    if(!viaLive && window.OMEGA_TD && typeof window.OMEGA_TD.acquire === 'function') await window.OMEGA_TD.acquire('analysis');\n"
    "    if(!viaLive) await tdThrottle();\n")
rep("    if(!key){ hint.innerHTML = '⚠ No Twelve Data key — forex &amp; silver need one.",
    "    if(!key && window.OMEGA_LAPI && window.OMEGA_LAPI.on()){ hint.textContent = '✓ No Twelve Data key: forex and metals candles come from your OMEGA Live API (gold keeps its PAXG proxy).'; hint.style.color='var(--text-dim)'; return; }\n"
    "    if(!key){ hint.innerHTML = '⚠ No Twelve Data key — forex &amp; silver need one (or the OMEGA Live API token in Settings).")

# ── 3b. CREED desk: data source only (one line; the method is untouched) ──
rep("    var key = keyNow();\n    if(!key) throw new Error('No Twelve Data key.",
    "    var key = keyNow();\n    if(!key && window.OMEGA_LAPI && window.OMEGA_LAPI.on()) key = window.OMEGA_LAPI.KEY;   // v6.5.112: data source only\n    if(!key) throw new Error('No Twelve Data key.")

# ── 3c. CREED Scanner ──
rep("""  async function fetchTD(sym, L){
    var b = budget();
    var cap = Math.floor((cfg.tdDailyLimit||800) * RADAR_SHARE);
    if(b.used >= cap) throw new Error('Radar has used its share of today\\u2019s Twelve Data allowance ('+b.used+'/'+cap+'); resumes after 00:00 UTC');
    var wait = Math.max(0, TD_GAP - (Date.now()-tdLast)); if(wait) await sleep(wait);
    await acquire('radar');
    tdLast = Date.now(); spend(1);
    var url = 'https://api.twelvedata.com/time_series?symbol='+encodeURIComponent(sym)+'&interval='+L.td+'&outputsize='+L.limit+'&apikey='+encodeURIComponent(tdKey());
""", """  async function fetchTD(sym, L){
    var LV = !tdKey() && window.OMEGA_LAPI && window.OMEGA_LAPI.on();   // v6.5.112: OMEGA Live API, no Twelve Data budget
    if(!LV){
    var b = budget();
    var cap = Math.floor((cfg.tdDailyLimit||800) * RADAR_SHARE);
    if(b.used >= cap) throw new Error('Radar has used its share of today\\u2019s Twelve Data allowance ('+b.used+'/'+cap+'); resumes after 00:00 UTC');
    var wait = Math.max(0, TD_GAP - (Date.now()-tdLast)); if(wait) await sleep(wait);
    await acquire('radar');
    tdLast = Date.now(); spend(1);
    }
    var url = 'https://api.twelvedata.com/time_series?symbol='+encodeURIComponent(sym)+'&interval='+L.td+'&outputsize='+L.limit+'&apikey='+encodeURIComponent(tdKey() || (LV ? window.OMEGA_LAPI.KEY : ''));
""")
rep("    if(!d || !Array.isArray(d.values)){ var bb=budget(); bb.errors++; lsSet(BUD_KEY, bb); throw",
    "    if(!d || !Array.isArray(d.values)){ if(!LV){ var bb=budget(); bb.errors++; lsSet(BUD_KEY, bb); } throw")
rep("    else if(!tdKey()) throw new Error('NO_KEY');\n    else { src='Twelve Data'; rows = await fetchTD(sym, L); }\n",
    "    else if(!tdKey() && !(window.OMEGA_LAPI && window.OMEGA_LAPI.on())) throw new Error('NO_KEY');\n"
    "    else { src = tdKey() ? 'Twelve Data' : 'OMEGA Live API'; rows = await fetchTD(sym, L); }\n")

# ── 3d. Market Intelligence ──
rep("""      if(!tdKey()) throw new Error('NO_KEY');
      var b=budget(); if(b.used >= cap()) throw new Error('BUDGET');
      if(window.OMEGA_TD) await window.OMEGA_TD.acquire('intel');
      b=budget(); b.used++; lsSet(BUD_KEY,b);
      var j = await (await fetch('https://api.twelvedata.com/time_series?symbol='+encodeURIComponent(sym)+'&interval='+T.td+'&outputsize='+T.n+'&timezone=UTC&apikey='+encodeURIComponent(tdKey()))).json();
""", """      var LV = !tdKey() && window.OMEGA_LAPI && window.OMEGA_LAPI.on();   // v6.5.112: OMEGA Live API, no Twelve Data budget
      if(!tdKey() && !LV) throw new Error('NO_KEY');
      if(!LV){ var b=budget(); if(b.used >= cap()) throw new Error('BUDGET');
      if(window.OMEGA_TD) await window.OMEGA_TD.acquire('intel');
      b=budget(); b.used++; lsSet(BUD_KEY,b); }
      var j = await (await fetch('https://api.twelvedata.com/time_series?symbol='+encodeURIComponent(sym)+'&interval='+T.td+'&outputsize='+T.n+'&timezone=UTC&apikey='+encodeURIComponent(tdKey() || (LV ? window.OMEGA_LAPI.KEY : '')))).json();
""")

# ── 3e. honest hints elsewhere ──
rep("    if(I && !hasKey) dont.push(",
    "    if(!hasKey && window.OMEGA_LAPI && window.OMEGA_LAPI.on()) hasKey = true;   // v6.5.112: the Live API reads forex\n    if(I && !hasKey) dont.push(")
rep("    var key = safe(function(){ return localStorage.getItem('omega_td_key'); }); if(!key) out.push(",
    "    var key = safe(function(){ return localStorage.getItem('omega_td_key') || (window.OMEGA_LAPI && window.OMEGA_LAPI.on() ? 'live' : ''); }); if(!key) out.push(")

# ── 4. Forex page, menu, Charts tab, navigator ──
FXPAGE = '''    <div id="page-forex" class="page">
      <nav class="om-subnav" aria-label="Charts"><button type="button" onclick="navigate('analysis')">Charts</button><button type="button" class="on" aria-current="page">Forex board</button></nav>
      <header class="om-head"><h2>Forex</h2><p>Every major, minor and exotic pair, and the metals: live price, spread and whether the market is open. Tap a pair to chart it.</p></header>
      <div id="fxBoard"></div>
      <details class="om-about"><summary>About this page</summary><div class="om-about-body">
        <p><b>Prices</b> are Swissquote&rsquo;s live bid and ask, read by your OMEGA Live API every few seconds. <b>Spread</b> is ask minus bid, in pips (0.0001; 0.01 for yen and forint pairs); for metals it is in dollars. When a quote is more than ten minutes old the market is closed (weekends, holidays) or the feed paused, and the row says so.</p>
        <p><b>Candles</b> for the chart come from Twelve Data when this browser has a key; without one they come from the Live API (Twelve Data on the server if it has a key, otherwise Yahoo: 1 hour back 2 years, 15 minutes back 60 days, 5 minutes back 5 days). Metal candles from Yahoo are <b>futures</b> (gold GC, silver SI, platinum PL, palladium PA): a close proxy, not spot. The chart says which source it used.</p>
        <p>The board needs the Live API token (Settings &rsaquo; Data &amp; Keys). Information only: OMEGA places no orders, and forex majors failed every hour-by-hour test OMEGA ran (E15).</p>
      </div></details>
    </div>
'''
rep('    <div id="page-academy" class="page">', FXPAGE + '    <div id="page-academy" class="page">')
rep('    <div id="page-analysis" class="page">\n',
    '    <div id="page-analysis" class="page">\n      <nav class="om-subnav" aria-label="Charts"><button type="button" class="on" aria-current="page">Charts</button><button type="button" onclick="navigate(\'forex\')">Forex board</button></nav>\n')
rep('''      <li data-page="analysis" onclick="navigate('analysis')"><span class="sb-icon">📊</span> Charts (Analysis)</li>\n''',
    '''      <li data-page="analysis" onclick="navigate('analysis')"><span class="sb-icon">📊</span> Charts (Analysis)</li>\n      <li data-page="forex" onclick="navigate('forex')"><span class="sb-icon">¤</span> Forex board</li>\n''')
rep("  var EXTRA = ['command','brain','radar','intel','flow','osig','mread','rguard','auto','futures','posdesk','academy'];",
    "  var EXTRA = ['command','brain','radar','intel','flow','osig','mread','rguard','auto','futures','posdesk','academy','forex'];")
rep("    var pages = [['command','Home'],['analysis','Charts (Analysis)'],",
    "    var pages = [['command','Home'],['analysis','Charts (Analysis)'],['forex','Forex board'],")

# ── 5. bots feed hosts ──
rep('    <div id="page-bot" class="page">\n      <div id="botsHub"></div>\n',
    '    <div id="page-bot" class="page">\n      <div id="botsFeed" class="om-feed"></div>\n      <div id="botsHub"></div>\n')
rep('      <div id="cmdFive" class="cmd-five"></div>\n',
    '      <div id="cmdFive" class="cmd-five"></div>\n      <div id="homeBotsFeed" class="om-feed om-feed-sm"></div>\n')

CSS = r'''<style id="omLiveCss">/* v6.5.112: Forex board, bots feed, Live API (theme variables only) */
.om-subnav{display:inline-flex;gap:2px;padding:3px;margin:0 0 14px;border:1px solid var(--border);border-radius:999px;background:var(--panel2)}
.om-subnav button{border:0;background:none;color:var(--text-dim);font:inherit;font-size:13px;font-weight:600;padding:7px 16px;border-radius:999px;cursor:pointer;min-height:36px}
.om-subnav button.on{background:var(--panel);color:var(--text);box-shadow:0 1px 3px rgba(0,0,0,.12)}
.om-head{margin:2px 0 14px}.om-head h2{margin:0 0 4px;font-size:22px;letter-spacing:-.01em;color:var(--text);text-transform:none}.om-head p{margin:0;color:var(--text-dim);font-size:13.5px;line-height:1.5;max-width:640px}
.om-card{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:16px;margin:0 0 14px}
.om-card h3{margin:0;font-size:15px;color:var(--text);text-transform:none;letter-spacing:0}
.om-ch{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.om-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px}.om-tabs button{border:1px solid var(--border);background:var(--panel);color:var(--text-dim);font:inherit;font-size:13px;font-weight:600;padding:7px 14px;border-radius:999px;cursor:pointer;min-height:36px}
.om-tabs button.on{border-color:var(--gold);color:var(--text);background:var(--panel2)}.om-tabs button em{font-style:normal;opacity:.6;margin-left:4px;font-weight:500}
.om-tag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:999px;border:1px solid var(--border);color:var(--text-dim);white-space:nowrap}
.om-tag.paper{color:var(--amber);border-color:var(--amber)}.om-tag.ga{color:var(--bull);border-color:var(--bull)}.om-tag.gb{color:var(--gold);border-color:var(--gold)}.om-tag.gc{color:var(--text-dim)}
.om-tag.live{color:var(--bull);border-color:transparent;background:color-mix(in srgb,var(--bull) 12%,transparent)}.om-tag.closed{color:var(--text-dim);background:var(--panel2);border-color:transparent}
.om-meta{font-size:12px;color:var(--text-dim)}.om-empty{padding:18px;text-align:center;color:var(--text-dim);font-size:13.5px;line-height:1.5}.om-empty .btn-outline{margin-top:10px}
.fx-list{display:flex;flex-direction:column;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--panel)}
.fx-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;width:100%;text-align:left;background:none;border:0;border-top:1px solid var(--border);padding:12px 14px;color:var(--text);font:inherit;cursor:pointer;min-height:56px}
.fx-row:first-child{border-top:0}.fx-row:hover{background:var(--panel2)}.fx-row b{font-size:15px;font-weight:650;letter-spacing:.01em}.fx-row small{display:block;color:var(--text-dim);font-size:11.5px;margin-top:2px}
.fx-px{text-align:right;font-variant-numeric:tabular-nums}.fx-px b{font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:600}
.fx-nm{display:flex;gap:10px;align-items:center;min-width:0}.fx-dot{flex:none;width:8px;height:8px;border-radius:50%;background:var(--border)}.fx-dot.on{background:var(--bull);box-shadow:0 0 0 3px color-mix(in srgb,var(--bull) 18%,transparent)}.fx-dot.off{background:var(--text-dim);opacity:.5}
.fx-closed{color:var(--amber);font-weight:600}
.fx-row.stale .fx-px b{color:var(--text-dim)}
.om-feed:empty{display:none}.om-grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.bf-rule{border:1px solid var(--border);border-radius:12px;padding:10px 12px;background:var(--panel2)}.bf-rule h4{margin:0 0 6px;font-size:13.5px;display:flex;gap:6px;align-items:center;flex-wrap:wrap;color:var(--text)}
.bf-li{display:flex;justify-content:space-between;gap:8px;font-size:12.5px;padding:5px 0;border-top:1px dashed var(--border)}.bf-li:first-of-type{border-top:0}.bf-li span{color:var(--text-dim)}
.bf-act{font-size:12.5px;padding:6px 0;border-top:1px solid var(--border);display:flex;gap:8px}.bf-act time{color:var(--text-dim);white-space:nowrap;font-variant-numeric:tabular-nums}
.bf-call{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;border-top:1px dashed var(--border)}.bf-call:first-of-type{border-top:0}
.bf-score{font-size:12px;color:var(--text-dim);margin-top:8px;line-height:1.5}
.om-feed-sm .om-card{padding:14px}.bf-mini{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:8px 0}.bf-mini div{background:var(--panel2);border-radius:10px;padding:8px 10px}.bf-mini b{display:block;font-size:18px;color:var(--text)}.bf-mini span{font-size:11px;color:var(--text-dim)}
.om-about{margin:14px 0;border:1px solid var(--border);border-radius:14px;background:var(--panel)}.om-about>summary{cursor:pointer;list-style:none;padding:13px 16px;font-weight:600;font-size:13.5px;color:var(--text);display:flex;justify-content:space-between;align-items:center}
.om-about>summary::-webkit-details-marker{display:none}.om-about>summary::after{content:'';width:7px;height:7px;border-right:1.6px solid var(--text-dim);border-bottom:1.6px solid var(--text-dim);transform:rotate(45deg);transition:transform .2s;margin-left:12px;flex:none}
.om-about[open]>summary::after{transform:rotate(-135deg)}.om-about-body{padding:0 16px 14px;color:var(--text-dim);font-size:13px;line-height:1.6}.om-about-body p{margin:0 0 10px}.om-about-body b{color:var(--text)}
</style>
'''

JS = r'''<script>/* ═══ OMEGA LIVE API CLIENT, FOREX BOARD, BOTS FEED (v6.5.112) ═══
   Server: Settings > Data & Keys (shared with the Academy). Token: localStorage omega_live_token (a *_token store: never in a
   backup, never restored from one). Twelve Data fallback: with NO Twelve Data key in this browser and a token set, a
   time_series request is answered from {server}/fx/klines in Twelve Data's own shape, so every page that reads forex works
   unchanged. Read-only: nothing here places an order. */
(function(){
  'use strict';
  var SKEY = 'omega_academy_server', TOK = 'omega_live_token', DEF = 'https://omega-live-api.onrender.com', KEY = 'omega-live-api';
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function okServer(u){ return /^https:\/\/[a-z0-9.-]+(:\d+)?(\/[^\s"'<>]*)?$/i.test(u) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/[^\s"'<>]*)?$/i.test(u); }
  function server(){ var u = ''; try{ u = localStorage.getItem(SKEY) || ''; }catch(e){} u = String(u).trim().replace(/\/+$/, ''); return okServer(u) ? u : DEF; }
  function token(){ try{ return String(localStorage.getItem(TOK) || '').trim(); }catch(e){ return ''; } }
  function on(){ return !!token(); }
  var f0 = window.fetch;   // the fetch underneath this module (data guard and metals rewrite included)
  function fetchT(url, opt, ms){ var c = typeof AbortController !== 'undefined' ? new AbortController() : null; opt = opt || {}; if(c) opt.signal = c.signal;
    var t = setTimeout(function(){ try{ c && c.abort(); }catch(e){} }, ms || 30000);
    return f0.call(window, url, opt).finally(function(){ clearTimeout(t); }); }
  function clean(m){ return String(m || '').replace(/symbol/gi, 'pair').replace(/api key/gi, 'token').replace(/not found/gi, 'missing').replace(/limit/gi, 'cap').slice(0, 160); }
  async function get(path, ms){
    var h = { 'Accept':'application/json' }, t = token(); if(t) h.Authorization = 'Bearer ' + t;
    var r; try{ r = await fetchT(server() + path, { headers:h }, ms || 30000); }
    catch(e){ throw new Error(e && e.name === 'AbortError' ? 'the server did not answer in time (a sleeping server takes about a minute to wake)' : 'the server could not be reached'); }
    var j = null; try{ j = await r.json(); }catch(e){}
    if(r.status === 401) throw new Error('the Live API token is missing or wrong (Settings > Data & Keys)');
    if(!r.ok) throw new Error((j && (j.detail || j.message)) ? clean(typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)) : 'HTTP ' + r.status);
    return j; }

  // ── Twelve Data shape from the server's candles ──
  var lastSrc = {}, kc = {};
  function plain(sym){ return String(sym || '').toUpperCase().replace(/[^A-Z0-9]/g, ''); }
  function tdPlan(iv){ iv = String(iv || '').toLowerCase(); var m;
    if((m = /^(\d+)min$/.exec(iv))){ var n = +m[1]; if(n === 1 || n === 5 || n === 15) return { tf:n + 'm', k:1 }; if(n % 15 === 0) return { tf:'15m', k:n/15 }; if(n % 5 === 0) return { tf:'5m', k:n/5 }; return { tf:'1m', k:n }; }
    if((m = /^(\d+)h$/.exec(iv))){ var h = +m[1]; if(h === 1) return { tf:'1h', k:1 }; if(h % 4 === 0) return { tf:'4h', k:h/4 }; return { tf:'1h', k:h }; }
    if((m = /^(\d+)day$/.exec(iv))) return { tf:'1d', k:+m[1] };
    if(/week$/.test(iv)) return { tf:'1d', k:'W' }; if(/month$/.test(iv)) return { tf:'1d', k:'M' };
    return null; }
  var STEP = { '1m':6e4, '5m':3e5, '15m':9e5, '1h':36e5, '4h':144e5, '1d':864e5 };
  function bucket(t, p){ if(p.k === 'W'){ var d = new Date(t), day = (d.getUTCDay() + 6) % 7; return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - day); }
    if(p.k === 'M'){ var e = new Date(t); return Date.UTC(e.getUTCFullYear(), e.getUTCMonth(), 1); }
    var w = STEP[p.tf] * p.k; return Math.floor(t / w) * w; }
  function agg(rows, p){ if(p.k === 1) return rows; var out = [], cur = null;
    rows.forEach(function(r){ var b = bucket(r.t, p); if(!cur || cur.t !== b){ cur = { t:b, o:r.o, h:r.h, l:r.l, c:r.c, v:r.v || 0 }; out.push(cur); } else { cur.h = Math.max(cur.h, r.h); cur.l = Math.min(cur.l, r.l); cur.c = r.c; cur.v += r.v || 0; } });
    return out; }
  function dt(t){ return new Date(t).toISOString().slice(0, 19).replace('T', ' '); }
  async function tdSeries(sym, iv, size, from, to){
    var p = tdPlan(iv), S = plain(sym); if(!p) return { status:'error', code:400, message:'Live API: interval ' + clean(iv) + ' is not offered' };
    var mult = p.k === 'W' ? 7 : p.k === 'M' ? 31 : p.k, lim = Math.max(1, Math.min(5000, Math.ceil((+size || 300) * mult) + mult));
    var ck = S + '|' + p.tf + '|' + lim, hit = kc[ck], j;
    try{ if(hit && Date.now() - hit.t < 30000) j = hit.j; else { j = await get('/fx/klines?symbol=' + encodeURIComponent(S) + '&tf=' + p.tf + '&limit=' + lim, 45000); kc[ck] = { t:Date.now(), j:j }; } }
    catch(e){ return { status:'error', code:0, message:'Live API: ' + clean(e && e.message || e) }; }
    var rows = (j && Array.isArray(j.candles) ? j.candles : []).filter(function(c){ return c && c.o > 0 && c.h > 0 && c.l > 0 && c.c > 0 && isFinite(c.t); })
      .map(function(c){ return { t:+c.t, o:+c.o, h:+c.h, l:+c.l, c:+c.c, v:+c.v || 0 }; }).sort(function(a, b){ return a.t - b.t; });
    rows = agg(rows, p);
    if(from) rows = rows.filter(function(r){ return r.t >= from; }); if(to) rows = rows.filter(function(r){ return r.t <= to; });
    rows = rows.slice(-(+size || 300));
    lastSrc[S] = String((j && j.source) || 'server');
    if(!rows.length) return { status:'error', code:0, message:'Live API: no candles for ' + clean(sym) + ' at ' + clean(iv) + ' (the free source keeps 5 days of 1-5 minute bars, 60 days of 15-minute bars)' };
    return { meta:{ symbol:sym, interval:iv, type:'Physical Currency', source:'OMEGA Live API: ' + lastSrc[S] }, status:'ok',
      values:rows.slice().reverse().map(function(r){ return { datetime:dt(r.t), open:String(r.o), high:String(r.h), low:String(r.l), close:String(r.c), volume:String(r.v || 0) }; }) }; }
  function sourceOf(sym){ var s = (lastSrc[plain(sym)] || 'server').replace(/^yahoo/i, 'Yahoo').replace(/^twelvedata/i, 'Twelve Data'); return /futures proxy/i.test(s) ? s.replace(/\(futures proxy ([^)]+)\)/i, '\u2014 futures $1 as a proxy, not spot') : s; }

  // ── the fallback, at fetch level: only when this browser has no Twelve Data key of its own ──
  if(f0 && !f0.__omegaLive){
    var fl = function(input, init){ var u = typeof input === 'string' ? input : (input && input.url) || '';
      if(/^https:\/\/api\.twelvedata\.com\/time_series\?/.test(u)){
        try{ var url = new URL(u), k = url.searchParams.get('apikey') || '';
          if((k === KEY || !k) && on()){
            var sd = url.searchParams.get('start_date'), ed = url.searchParams.get('end_date');
            return tdSeries(url.searchParams.get('symbol'), url.searchParams.get('interval'), +url.searchParams.get('outputsize') || 30,
                sd ? Date.parse(sd.replace(' ', 'T') + 'Z') : 0, ed ? Date.parse(ed.replace(' ', 'T') + 'Z') : 0)
              .then(function(js){ return new Response(JSON.stringify(js), { status:200, headers:{ 'content-type':'application/json' } }); }); }
        }catch(e){}
      }
      return f0.apply(this, arguments); };
    fl.__omegaLive = true; fl.__guard = !!f0.__guard; fl.__metals = !!f0.__metals; window.fetch = fl;
  }

  // ── the pair list (the server's /fx/list; this copy is used until it answers) ──
  var LIST = { majors:['EURUSD','GBPUSD','USDJPY','USDCHF','AUDUSD','USDCAD','NZDUSD'],
    minors:['EURGBP','EURJPY','EURCHF','EURAUD','EURCAD','EURNZD','GBPJPY','GBPCHF','GBPAUD','GBPCAD','GBPNZD','AUDJPY','AUDCHF','AUDCAD','AUDNZD','CADJPY','CADCHF','CHFJPY','NZDJPY','NZDCHF','NZDCAD'],
    exotics:['USDMXN','USDZAR','USDTRY','USDSGD','USDHKD','USDNOK','USDSEK','USDDKK','USDPLN','USDHUF','USDCZK','USDCNH','USDTHB','EURTRY','EURNOK','EURSEK','EURPLN','USDTTD'],
    metals:['XAUUSD','XAGUSD','XPTUSD','XPDUSD'] };
  var GROUPS = [['majors','Majors'],['minors','Minors'],['exotics','Exotics'],['metals','Metals']];
  var CUR = { EUR:'Euro', USD:'US dollar', GBP:'Pound', JPY:'Yen', CHF:'Swiss franc', AUD:'Australian dollar', CAD:'Canadian dollar', NZD:'NZ dollar', MXN:'Mexican peso', ZAR:'Rand', TRY:'Lira',
    SGD:'Singapore dollar', HKD:'HK dollar', NOK:'Norwegian krone', SEK:'Swedish krona', DKK:'Danish krone', PLN:'Zloty', HUF:'Forint', CZK:'Koruna', CNH:'Yuan (offshore)', THB:'Baht', TTD:'TT dollar',
    XAU:'Gold', XAG:'Silver', XPT:'Platinum', XPD:'Palladium' };
  function nice(s){ return s.slice(0, 3) + '/' + s.slice(3); }
  function names(s){ var a = s.slice(0, 3), b = s.slice(3); return /^X(AU|AG|PT|PD)$/.test(a) ? CUR[a] + ' in US dollars' : (CUR[a] || a) + ' / ' + (CUR[b] || b); }
  function pip(s){ return /JPY$|HUF$/.test(s) ? 0.01 : 0.0001; }
  function dec(s, p){ if(/^X(AU|PT|PD)/.test(s)) return 2; if(/^XAG/.test(s)) return 3; return p >= 100 ? 3 : p >= 10 ? 4 : 5; }
  var FX = { group:'majors', data:{}, at:{}, err:'', busy:false, timer:null, listAt:0 };
  try{ var g0 = localStorage.getItem('omega_fx_group'); if(LIST[g0]) FX.group = g0; }catch(e){}
  async function loadList(){ if(Date.now() - FX.listAt < 6 * 36e5) return; FX.listAt = Date.now();
    try{ var j = await get('/fx/list', 20000); ['majors','minors','exotics','metals'].forEach(function(k){ if(j && Array.isArray(j[k]) && j[k].length) LIST[k] = j[k].map(plain).filter(Boolean); }); }catch(e){} }
  async function loadBoard(force){ if(FX.busy || !on()) { renderFx(); return; } var g = FX.group;
    if(!force && FX.at[g] && Date.now() - FX.at[g] < 15000){ renderFx(); return; }
    FX.busy = true; renderFx();
    try{ loadList(); var j = await get('/fx/board?group=' + g, 40000); var m = {}; (j && j.quotes || []).forEach(function(q){ if(q && q.symbol) m[plain(q.symbol)] = q; });
      FX.data[g] = m; FX.at[g] = Date.now(); FX.err = ''; }
    catch(e){ FX.err = String(e && e.message || e); }
    FX.busy = false; renderFx(); }
  function hhmm(t){ if(!t) return '\u2014'; var d = new Date(t); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2) + ':' + ('0' + d.getSeconds()).slice(-2); }
  function renderFx(){ var host = el('fxBoard'); if(!host) return; var g = FX.group, rows = LIST[g] || [], d = FX.data[g] || {};
    var tabs = '<div class="om-tabs" role="tablist">' + GROUPS.map(function(x){ return '<button type="button" role="tab" data-fxg="' + x[0] + '" class="' + (x[0] === g ? 'on' : '') + '" aria-selected="' + (x[0] === g) + '">' + x[1] + '<em>' + (LIST[x[0]] || []).length + '</em></button>'; }).join('') + '</div>';
    var status;
    if(!on()) status = '<div class="om-card om-empty"><b style="color:var(--text)">Connect the OMEGA Live API to see live prices.</b><br>Add the token in Settings &rsaquo; Data &amp; Keys. The pairs below still open on Charts.<br><button class="btn-outline" type="button" data-fxset="1">Open Settings</button></div>';
    else status = '<p class="om-meta" id="fxStatus" style="margin:0 0 8px;">' + (FX.busy ? 'Updating\u2026 ' : '') + (FX.at[g] ? 'Swissquote live quotes \u00b7 updated ' + hhmm(FX.at[g]) : (FX.busy ? '' : 'Not loaded yet.')) + (FX.err ? ' <span style="color:var(--bear)">\u00b7 ' + esc(FX.err) + '</span>' : '') + '</p>';
    var list = '<div class="fx-list">' + rows.map(function(s){ var q = d[s], p = q && +q.price, st = q && q.stale, sp = q && q.bid != null && q.ask != null ? (+q.ask - +q.bid) : null, metal = /^X(AU|AG|PT|PD)/.test(s);
        var spT = sp == null ? '' : metal ? 'spread $' + sp.toFixed(s === 'XAGUSD' ? 3 : 2) : 'spread ' + (sp / pip(s)).toFixed(1) + ' pips';
        var dot = '<i class="fx-dot' + (!q ? '' : st ? ' off' : ' on') + '" title="' + (!q ? 'no quote' : st ? 'market closed' : 'live') + '"></i>';
        return '<button type="button" class="fx-row' + (st ? ' stale' : '') + '" data-fx="' + s + '"><div class="fx-nm">' + dot + '<div><b>' + nice(s) + '</b><small>' + esc(names(s)) + '</small></div></div>' +
          '<div class="fx-px"><b>' + (p > 0 ? p.toFixed(dec(s, p)) : '\u2014') + '</b><small>' + (st ? '<span class="fx-closed">Market closed</span>' : q && q.bid != null ? esc(spT) : (on() ? '' : 'tap to chart')) + '</small></div></button>'; }).join('') + '</div>';
    host.innerHTML = tabs + status + list;
    Array.prototype.forEach.call(host.querySelectorAll('[data-fxg]'), function(b){ b.onclick = function(){ FX.group = b.getAttribute('data-fxg'); try{ localStorage.setItem('omega_fx_group', FX.group); }catch(e){} renderFx(); loadBoard(false); }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-fx]'), function(b){ b.onclick = function(){ openOnCharts(b.getAttribute('data-fx')); }; });
    var st = host.querySelector('[data-fxset]'); if(st) st.onclick = openSettings; }
  function openSettings(){ window.navigate('settings'); try{ window.switchSettings && window.switchSettings('data'); }catch(e){} setTimeout(function(){ var i = el('liveTokenInput'); if(i){ i.scrollIntoView({ block:'center' }); try{ i.focus(); }catch(e){} } }, 120); }
  function openOnCharts(s){ var sym = nice(plain(s)), metal = /^X(AU|AG|PT|PD)/.test(sym); window.navigate('analysis');
    var sel = el('symbol'); if(!sel) return;
    if(!Array.prototype.some.call(sel.options, function(o){ return o.value === sym; })){ var grp = Array.prototype.filter.call(sel.querySelectorAll('optgroup'), function(o){ return metal ? /gold|silver/i.test(o.label) : /forex/i.test(o.label); })[0] || sel;
      var o = document.createElement('option'); o.value = sym; o.textContent = sym; grp.appendChild(o); }
    sel.value = sym; try{ sel.dispatchEvent(new Event('change')); }catch(e){}
    var ac = el('assetClass'); if(ac){ var want = metal ? 'metals' : 'forex'; if(ac.value !== want){ ac.value = want; try{ ac.dispatchEvent(new Event('change')); }catch(e){} sel.value = sym; try{ sel.dispatchEvent(new Event('change')); }catch(e){} } }
    setTimeout(function(){ var d = el('anDeep') || sel; try{ d.scrollIntoView({ block:'start' }); }catch(e){} }, 60);
    var hasKey = false; try{ hasKey = !!localStorage.getItem('omega_td_key') || !!((el('apikey') || {}).value); }catch(e){}
    if((hasKey || on() || sym === 'XAU/USD') && typeof window.runAnalysis === 'function') setTimeout(function(){ try{ window.runAnalysis(); }catch(e){} }, 150); }

  // ── bots feed ──
  var RULES = { climax_a:['Climax reversal','A'], panic_h1:['Panic bounce H1','B'], panic_h3:['Panic bounce H3, market-wide','B'], panic5m_watch:['Panic bounce 5m','C'],
    panic15m_watch:['Panic bounce 15m','C'], breadth15m_watch:['Market-wide panic 15m','C'], upscout_watch:['UpScout top-2% longs','C'] };
  function rule(id){ var r = RULES[id]; if(r) return { name:r[0], g:r[1] }; return { name:String(id || '?').replace(/_/g, ' '), g:/watch/.test(id) ? 'C' : '?' }; }
  function gradeTag(g){ return '<span class="om-tag g' + String(g).toLowerCase() + '">' + (g === 'C' ? 'C \u00b7 watch list, paper only' : g === 'A' ? 'Grade A' : g === 'B' ? 'Grade B' : 'ungraded') + '</span>'; }
  var BF = { j:null, at:0, err:'', busy:false };
  function coin(s){ return String(s || '').replace(/USDT$/, ''); }
  function num(x, d){ x = +x; if(!isFinite(x)) return '\u2014'; var a = Math.abs(x); return x.toFixed(d != null ? d : a >= 1000 ? 1 : a >= 10 ? 2 : a >= 1 ? 3 : a >= 0.01 ? 5 : 7); }
  function pct(x){ x = +x; return isFinite(x) ? Math.round(x * 1000) / 10 + '%' : '\u2014'; }
  function when(t){ var d = new Date(t); if(!isFinite(d)) return '\u2014'; var s = Math.round((Date.now() - d) / 6e4), f = s < 0, a = Math.abs(s);
    var x = a < 1 ? 'now' : a < 90 ? a + ' min' : a < 2880 ? Math.round(a / 60) + ' h' : Math.round(a / 1440) + ' d'; return a < 1 ? x : f ? 'in ' + x : x + ' ago'; }
  function hm(t){ var d = new Date(t); return isFinite(d) ? ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2) : '\u2014'; }
  async function loadFeed(force){ if(BF.busy || !on()){ renderFeeds(); return; } if(!force && BF.at && Date.now() - BF.at < 110000){ renderFeeds(); return; }
    BF.busy = true; renderFeeds();
    try{ BF.j = await get('/bots/feed', 40000); BF.at = Date.now(); BF.err = ''; }catch(e){ BF.err = String(e && e.message || e); }
    BF.busy = false; renderFeeds(); }
  function byRule(pb){ var m = {}; function add(kind, x){ var k = x.strategy || '?'; (m[k] = m[k] || { open:[], rest:[] })[kind].push(x); }
    (pb.open_positions || pb.open || []).forEach(function(x){ add('open', x); }); (pb.resting_orders || pb.resting || []).forEach(function(x){ add('rest', x); });
    Object.keys(pb.approved || {}).forEach(function(k){ m[k] = m[k] || { open:[], rest:[] }; }); return m; }
  function actions(pb){ var L = (pb.recent_log || pb.recent_actions || []).slice(-40).reverse(), out = [];
    L.forEach(function(a){ var prev = out[out.length - 1], why = (a.reasons && a.reasons.join('; ')) || a.why || a.reason || a.exit_reason || '';
      if(prev && a.event === 'refused' && prev.ev === 'refused' && prev.why === why){ prev.n++; prev.syms.push(coin(a.sym)); return; }
      out.push({ t:a.t || a.time, ev:a.event || a.kind || '?', r:a.rule || a.strategy, sym:coin(a.sym), why:why, n:1, syms:[coin(a.sym)], px:a.price || a.entry || a.exit }); });
    return out.slice(0, 8); }
  function scoutBlock(name, sc){ if(!sc) return '<div class="bf-rule"><h4>' + esc(name) + '</h4><p class="om-meta" style="margin:0">No forecasts yet.</p></div>';
    var L = (sc.latest || []).map(function(r){ return { s:coin(r.sym), u:+r.p_up_move, d:+r.p_down_move }; });
    var up = L.slice().sort(function(a, b){ return b.u - a.u; }).slice(0, 3), dn = L.slice().sort(function(a, b){ return b.d - a.d; }).slice(0, 3);
    var uf = sc.up_flags || {}, df = sc.down_flags || {};
    return '<div class="bf-rule"><h4>' + esc(name) + ' <span class="om-tag">forecast</span></h4><p class="om-meta" style="margin:0 0 6px">Latest reading ' + esc(when(sc.latest_time)) + '</p>' +
      '<div class="om-meta" style="margin-top:4px">Strongest up</div>' + up.map(function(x){ return '<div class="bf-call"><span>' + esc(x.s) + '</span><b style="color:var(--bull)">' + pct(x.u) + '</b></div>'; }).join('') +
      '<div class="om-meta" style="margin-top:6px">Strongest down</div>' + dn.map(function(x){ return '<div class="bf-call"><span>' + esc(x.s) + '</span><b style="color:var(--bear)">' + pct(x.d) + '</b></div>'; }).join('') +
      '<p class="bf-score">Forward record: ' + (sc.scored || 0) + ' of ' + (sc.predictions || 0) + ' forecasts scored. Up calls ' + (uf.flagged || 0) + ', hit ' + (uf.hit_rate == null ? '\u2014' : pct(uf.hit_rate)) +
      ' vs base rate ' + (sc.base_rate_up == null ? '\u2014' : pct(sc.base_rate_up)) + '. Down calls ' + (df.flagged || 0) + ', hit ' + (df.hit_rate == null ? '\u2014' : pct(df.hit_rate)) + '.</p></div>'; }
  function feedHead(small){ return '<div class="om-ch"><h3>' + (small ? '24/7 bots' : 'The 24/7 bots, live') + '</h3><span class="om-tag paper">Paper \u00b7 forecasts</span></div>'; }
  function feedStatus(){ var j = BF.j; return '<p class="om-meta" style="margin:0 0 10px;">' + (BF.busy ? 'Updating\u2026 ' : '') + (BF.at ? 'Last updated ' + hm(BF.at) + (j && j.source ? ' \u00b7 from the ' + esc(j.source) : '') : (BF.busy ? '' : 'Not loaded yet.')) + (BF.err ? ' <span style="color:var(--bear)">\u00b7 ' + esc(BF.err) + '</span>' : '') + '</p>'; }
  function renderFeeds(){ var big = el('botsFeed'), small = el('homeBotsFeed');
    if(big){ if(!on()) big.innerHTML = '<div class="om-card">' + feedHead(false) + '<p class="om-meta" style="margin:0">The paper bot and the scouts run 24/7 in the cloud (and on the laptop Station). Add the Live API token in Settings &rsaquo; Data &amp; Keys to see their positions, orders and forecasts here.</p><div class="journal-actions" style="margin-top:10px"><button class="btn-outline" type="button" data-bfset="1">Open Settings</button></div></div>';
      else { var j = BF.j || {}, pb = j.paper_bot || {}, R = byRule(pb), ids = Object.keys(R).sort(function(a, b){ return (rule(a).g + a).localeCompare(rule(b).g + b); });
        var idle = ids.filter(function(id){ return !R[id].open.length && !R[id].rest.length; }); ids = ids.filter(function(id){ return idle.indexOf(id) < 0; });
        var rules = ids.map(function(id){ var r = rule(id), x = R[id];
          return '<div class="bf-rule"><h4>' + esc(r.name) + ' ' + gradeTag(r.g) + '</h4>' +
            (x.open.length ? x.open.map(function(p){ return '<div class="bf-li"><b>' + esc(coin(p.sym)) + ' ' + esc(p.side || '') + '</b><span>open at ' + num(p.entry) + ' \u00b7 stop ' + num(p.stop_price) + (p.exit_due ? ' \u00b7 exits ' + esc(when(p.exit_due)) : '') + '</span></div>'; }).join('') : '') +
            (x.rest.length ? x.rest.map(function(o){ return '<div class="bf-li"><b>' + esc(coin(o.sym)) + ' ' + esc(o.side || '') + '</b><span>resting ' + esc(o.kind || 'order') + ' ' + num(o.price) + ' \u00b7 until ' + esc(hm(o.expires_at)) + '</span></div>'; }).join('') : '') +
            (!x.open.length && !x.rest.length ? '<p class="om-meta" style="margin:0">Nothing open or resting.</p>' : '') + '</div>'; }).join('');
        var acts = actions(pb).map(function(a){ return '<div class="bf-act"><time>' + esc(hm(a.t)) + '</time><span><b>' + esc(a.ev) + '</b> ' + esc(a.n > 1 ? a.n + '\u00d7 (' + a.syms.slice(0, 4).join(', ') + (a.n > 4 ? '\u2026' : '') + ')' : a.sym) + (a.r ? ' \u00b7 ' + esc(rule(a.r).name) : '') + (a.why ? ' \u2014 <span class="om-meta">' + esc(String(a.why).slice(0, 90)) + '</span>' : '') + '</span></div>'; }).join('');
        big.innerHTML = '<div class="om-card">' + feedHead(false) + feedStatus() +
          (BF.j ? '<div class="om-meta" style="margin:0 0 8px">Paper bot: ' + (pb.open_positions || []).length + ' open, ' + (pb.resting_orders || []).length + ' resting, ' + (+pb.closed_trades || 0) + ' closed' + (pb.today_pnl_paper != null ? ' \u00b7 today ' + num(pb.today_pnl_paper, 2) + ' USDT (paper)' : '') + (pb.kill_switch ? ' \u00b7 <b style="color:var(--bear)">kill switch on</b>' : '') + '</div>' +
            '<div class="om-grid2">' + (rules || '<p class="om-meta" style="margin:0">No open positions or resting orders right now.</p>') + '</div>' +
            (idle.length ? '<p class="om-meta" style="margin:10px 0 0">Waiting for a signal: ' + idle.map(function(id){ var r = rule(id); return esc(r.name) + ' <b>(' + r.g + ')</b>'; }).join(', ') + '.</p>' : '') +
            '<details class="om-about" style="margin:12px 0 0"><summary>Recent actions</summary><div class="om-about-body">' + (acts || 'None yet.') + '</div></details>' +
            '<h3 style="margin:16px 0 8px">Scouts</h3><div class="om-grid2">' + scoutBlock('Hourly scouts (24 h ahead)', j.scouts_hourly) + scoutBlock('Fast scouts (4 h ahead)', j.scouts_fast) + '</div>' +
            '<p class="om-meta" style="margin:10px 0 0">' + esc(j.note || 'Paper records and forecasts; information only, never an order.') + ' Grade C rules are a watch list: they failed their final test and trade on paper only. The scouts failed as trading rules (E81, E82) and are scored forward.</p>' : '') + '</div>'; } }
    if(small){ if(!on()) small.innerHTML = ''; else { var jj = BF.j || {}, p2 = jj.paper_bot || {}, sh = jj.scouts_hourly, top = sh && (sh.latest || []).slice().sort(function(a, b){ return +b.p_up_move - +a.p_up_move; })[0];
        small.innerHTML = '<div class="om-card">' + feedHead(true) + feedStatus() + (BF.j ? '<div class="bf-mini"><div><b>' + (p2.open_positions || []).length + '</b><span>open (paper)</span></div><div><b>' + (p2.resting_orders || []).length + '</b><span>resting orders</span></div><div><b>' + (top ? esc(coin(top.sym)) : '\u2014') + '</b><span>' + (top ? 'strongest up call ' + pct(top.p_up_move) : 'no forecast') + '</span></div></div>' : '') +
          '<div class="journal-actions"><button class="btn-ghost" type="button" onclick="navigate(\'bot\')">Open Bots</button></div></div>'; } }
    Array.prototype.forEach.call(document.querySelectorAll('[data-bfset]'), function(b){ b.onclick = openSettings; }); }

  // ── settings ──
  function wireSettings(){ var inp = el('liveTokenInput'), sv = el('liveTokenSave'), ts = el('liveTokenTest'), cl = el('liveTokenClear'), msg = el('liveTokenMsg'); if(!inp) return;
    inp.value = token() ? '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022' : ''; inp.setAttribute('data-masked', token() ? '1' : '');
    inp.addEventListener('focus', function(){ if(inp.getAttribute('data-masked')){ inp.value = ''; inp.setAttribute('data-masked', ''); } });
    function say(t, bad){ if(msg){ msg.textContent = t; msg.style.color = bad ? 'var(--bear)' : ''; } }
    if(sv) sv.onclick = function(){ var v = String(inp.value || '').trim(); if(inp.getAttribute('data-masked')){ say('The saved token is unchanged.'); return; }
      if(!v){ say('Paste the token first.', true); return; } if(v.length < 8 || /\s/.test(v)){ say('That does not look like a token (no spaces, at least 8 characters).', true); return; }
      try{ localStorage.setItem(TOK, v); }catch(e){} inp.value = '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022'; inp.setAttribute('data-masked', '1'); say('Saved on this device. Forex and the bots feed now use ' + server() + '.'); FX.at = {}; BF.at = 0; kc = {}; };
    if(cl) cl.onclick = function(){ try{ localStorage.removeItem(TOK); }catch(e){} inp.value = ''; inp.setAttribute('data-masked', ''); say('Token removed from this device.'); renderFx(); renderFeeds(); };
    if(ts) ts.onclick = async function(){ say('Testing ' + server() + '\u2026 (a sleeping server takes about a minute to wake)');
      try{ var h = await get('/health', 70000); var extra = '';
        if(on()){ try{ var q = await get('/fx/quote?symbol=EURUSD', 30000); extra = ' Token accepted: EUR/USD ' + (+q.price).toFixed(5) + (q.stale ? ' (market closed)' : '') + '.'; }catch(e){ extra = ' ' + e.message.charAt(0).toUpperCase() + e.message.slice(1) + '.'; } }
        else extra = ' No token saved yet: forex and the bots feed need one.';
        say('Server answers (version ' + esc(h && h.version || '?') + (h && h.twelvedata_key ? ', Twelve Data on the server' : ', candles from Yahoo') + ').' + extra, /missing|wrong|could not/.test(extra)); }
      catch(e){ say('No answer: ' + (e && e.message || e), true); } }; }

  // ── when the pages show ──
  function active(p){ var e = el('page-' + p); return !!(e && e.classList.contains('active')); }
  var prevAfter = window.__omegaAfterNav;
  window.__omegaAfterNav = function(p){ try{ if(typeof prevAfter === 'function') prevAfter(p); }catch(e){}
    if(p === 'forex') setTimeout(function(){ renderFx(); loadBoard(false); }, 20);
    if(p === 'bot' || p === 'command') setTimeout(function(){ renderFeeds(); loadFeed(false); }, 40); };
  function tick(){ if(document.hidden) return; if(active('forex')) loadBoard(true); }
  function tickFeed(){ if(document.hidden) return; if(active('bot') || active('command')) loadFeed(true); }
  function boot(){ wireSettings(); renderFx(); renderFeeds(); if(active('forex')) loadBoard(false); if(active('bot') || active('command')) loadFeed(false);
    setInterval(tick, 20000); setInterval(tickFeed, 120000);
    document.addEventListener('visibilitychange', function(){ if(!document.hidden){ if(active('forex')) loadBoard(false); if(active('bot') || active('command')) loadFeed(false); } }); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else setTimeout(boot, 0);
  window.OMEGA_LAPI = { KEY:KEY, on:on, server:server, token:function(){ return !!token(); }, get:get, tdSeries:tdSeries, tdPlan:tdPlan, sourceOf:sourceOf,
    fx:{ list:function(){ return LIST; }, state:function(){ return FX; }, load:loadBoard, render:renderFx, open:openOnCharts },
    feed:{ state:function(){ return BF; }, load:loadFeed, render:renderFeeds, actions:actions, rule:rule } };
})();
</script>
'''
rep('</body>', CSS + JS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.111 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.111 ' + sep + ' build ' + o + ' UTC', 'v6.5.112 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.112 · build' in s and 'v6.5.111 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now, 'size', len(s.encode('utf-8')))
