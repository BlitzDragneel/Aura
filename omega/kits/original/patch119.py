"""v6.5.119: Desks: Bitcoin, Gold and Silver, each read by its own bot (edges/assetbots). CREED's engine is byte-identical.
 A new page "Desks" (menu under Charts & markets, a strip on Home, the command palette; the bottom bar is unchanged) with
 three desks. Each shows, in plain words:
  - the price: the 24/7 perpetual (Binance -> OKX -> Live API, v6.5.118) and, for gold and silver, the spot quote;
  - what the bot says now: one sentence from its three horizons;
  - day / swing / hold: the state (WAIT, WATCH, SETUP, TRIGGERED, CONFIRMED, INVALIDATED, EXPIRED) with the reasons in a
    dropdown; a call only when a tested rule made one (rule, grade, side, entry, stop, target, exit time, size, evidence,
    paper record or execution allowed); WATCH never carries a direction;
  - dropdowns: the market read (trend per timeframe, volatility regime, session, ranges, funding, scouts with their labels),
    the forward record (readings and calls scored after the fact) and the notebook ("What I know about gold").
 Data: GET /assets/{BTC|XAU|XAG} on the OMEGA Live API (the Station folder or the bot-state branch). Without the token the
 page still shows live prices and says how to connect. Autopilot job "desks": every 2 minutes while Desks or Home is open,
 every 15 minutes otherwise; the last desks are kept for offline reading.
usage: python3 patch119.py <v6.5.118> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


# page, menu, navigation, palette, Home strip
PAGE = '''    <div id="page-desks" class="page">
      <header class="om-head"><h2>Desks</h2><p>Bitcoin, gold and silver, each read by its own bot every 15 minutes. A bot calls a trade only when a rule that passed a fair test fires; otherwise it waits, or watches when a big move looks likely without knowing its direction.</p></header>
      <div id="desksBody"></div>
      <details class="om-about"><summary>About this page</summary><div class="om-about-body">
        <p><b>Who reads the markets.</b> Three bots run 24/7 in the cloud (or on the laptop Station): one for Bitcoin, one for gold, one for silver. Every 15 minutes each reads its market on closed candles &mdash; the 24/7 Binance perpetual (BTCUSDT, XAUUSDT, XAGUSDT) and, for the metals, the spot quote &mdash; and writes down what it sees before anyone knows what happens next.</p>
        <p><b>States.</b> WAIT: nothing qualifies. WATCH: a big move looks likely, direction unknown &mdash; watch only. SETUP: a tested rule&rsquo;s conditions are forming. TRIGGERED: a tested rule fired and a call is out. CONFIRMED: the call&rsquo;s entry filled. INVALIDATED: its stop was hit. EXPIRED: it ended otherwise (target, time, never filled).</p>
        <p><b>Calls.</b> Only rules in OMEGA&rsquo;s approved list for that asset and horizon (day, swing, hold) with status paper or higher can give a direction. Paper calls are records for the forward test, not orders; OMEGA places no orders from this page.</p>
        <p><b>Learning.</b> Every reading and call is scored after its horizon passes (the forward record), the gold and silver scouts are retrained monthly, and each bot keeps a notebook built from the research findings and its own record. Its scouts say how likely a big move is, never which way; a scout without proven skill is shown but not used.</p>
      </div></details>
    </div>
'''
rep('    <div id="page-about" class="page">\n', PAGE + '    <div id="page-about" class="page">\n')
rep('''      <li data-page="forex" onclick="navigate('forex')"><span class="sb-icon">¤</span> Forex board</li>\n''',
    '''      <li data-page="forex" onclick="navigate('forex')"><span class="sb-icon">¤</span> Forex board</li>\n      <li data-page="desks" onclick="navigate('desks')"><span class="sb-icon">◆</span> Desks: Bitcoin, Gold, Silver</li>\n''')
rep("  var EXTRA = ['command','brain','radar','intel','flow','osig','mread','rguard','auto','futures','posdesk','academy','forex','about'];",
    "  var EXTRA = ['command','brain','radar','intel','flow','osig','mread','rguard','auto','futures','posdesk','academy','forex','about','desks'];   // v6.5.119: Desks")
rep("      drawSafe(p, function(){ if(p === 'auto' && window.OMEGA_AUTOPILOT) window.OMEGA_AUTOPILOT.render(); });\n",
    "      drawSafe(p, function(){ if(p === 'auto' && window.OMEGA_AUTOPILOT) window.OMEGA_AUTOPILOT.render(); });\n"
    "      drawSafe(p, function(){ if(p === 'desks' && window.OMEGA_DESKS) window.OMEGA_DESKS.onShow(); });\n")
rep("    var pages = [['command','Home'],['analysis','Charts (Analysis)'],['forex','Forex board'],",
    "    var pages = [['command','Home'],['analysis','Charts (Analysis)'],['forex','Forex board'],['desks','Desks (Bitcoin, Gold, Silver)'],")
rep('      <div id="selfRunHome" class="sr-host"></div>\n', '      <div id="selfRunHome" class="sr-host"></div>\n      <div id="homeDesks" class="dk-home"></div>\n')

CSS = r'''<style id="desksCss">/* v6.5.119: Desks (theme variables only) */
.dk-price{display:flex;flex-wrap:wrap;align-items:flex-end;gap:10px 22px}.dk-price .dk-big{font-size:28px;font-weight:700;color:var(--text);letter-spacing:-.01em;line-height:1.1}
.dk-k{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim);display:block;margin-bottom:2px}.dk-sub{font-size:12px;color:var(--text-dim)}
.dk-up{color:var(--bull)}.dk-dn{color:var(--bear)}.dk-warn{color:var(--amber);font-weight:600}
.dk-say{font-size:15px;color:var(--text);line-height:1.5;margin:0}.dk-say small{display:block;font-size:12.5px;color:var(--text-dim);margin-top:6px}
.dk-hz{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:0 0 14px}@media(max-width:760px){.dk-hz{grid-template-columns:1fr}}
.dk-h{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:12px 14px;min-width:0}.dk-h h4{margin:0 0 6px;font-size:13px;color:var(--text);display:flex;justify-content:space-between;align-items:center;gap:8px}
.dk-h h4 small{font-weight:400;color:var(--text-dim);font-size:11px}.dk-h p{margin:6px 0 0;font-size:12.5px;color:var(--text-dim);line-height:1.5}
.dk-st{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.07em;padding:3px 9px;border-radius:999px;border:1px solid var(--border);color:var(--text-dim);background:var(--panel2)}
.dk-st.WATCH{color:var(--amber);border-color:var(--amber)}.dk-st.SETUP{color:var(--gold);border-color:var(--gold)}.dk-st.TRIGGERED,.dk-st.CONFIRMED{color:var(--bull);border-color:var(--bull)}.dk-st.INVALIDATED{color:var(--bear);border-color:var(--bear)}
.dk-h details{margin-top:8px}.dk-h summary{cursor:pointer;font-size:12px;color:var(--text);font-weight:600}.dk-h ul{margin:6px 0 0;padding-left:18px;font-size:12px;color:var(--text-dim);line-height:1.5}
.dk-call{margin-top:8px;border-top:1px solid var(--border);padding-top:8px;font-size:12.5px;color:var(--text)}.dk-call dl{display:grid;grid-template-columns:auto 1fr;gap:3px 10px;margin:6px 0 0}.dk-call dt{color:var(--text-dim)}.dk-call dd{margin:0;min-width:0;overflow-wrap:anywhere}
.dk-fold{background:var(--panel);border:1px solid var(--border);border-radius:14px;margin:0 0 10px}.dk-fold>summary{cursor:pointer;padding:12px 14px;font-size:14px;font-weight:600;color:var(--text);list-style:none;display:flex;justify-content:space-between;gap:8px}
.dk-fold>summary::-webkit-details-marker{display:none}.dk-fold>summary span{font-weight:400;font-size:12px;color:var(--text-dim)}.dk-fold>div{padding:0 14px 12px;font-size:13px;color:var(--text-dim);line-height:1.55}
.dk-fold table{width:100%;border-collapse:collapse;font-size:12.5px}.dk-fold td,.dk-fold th{text-align:left;padding:5px 6px;border-top:1px solid var(--border);color:var(--text)}.dk-fold th{color:var(--text-dim);font-weight:600}
.dk-fold h5{margin:10px 0 4px;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--text-dim)}.dk-fold ul{margin:0;padding-left:18px}
.dk-acts{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 14px}.dk-note{font-size:12px;color:var(--text-dim);line-height:1.5;margin:0 0 14px}
.dk-home{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0 0 14px}.dk-home:empty{display:none}
.dk-tile{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:10px 12px;text-align:left;font:inherit;color:var(--text);cursor:pointer;min-width:0}
.dk-tile b{display:block;font-size:13px}.dk-tile em{display:block;font-style:normal;font-size:15px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dk-tile small{display:block;font-size:11px;color:var(--text-dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
</style>
'''
JS = r'''<script>/* ═══ DESKS: BITCOIN, GOLD, SILVER (v6.5.119) ═══
   Each desk shows its bot's market read, day/swing/hold states, any call (only from tested rules), the forward record and
   the notebook, from GET /assets/{BTC|XAU|XAG} on the OMEGA Live API. Prices are live in the browser. Information only. */
(function(){
  'use strict';
  var KEY = 'omega_desks_v1', A = ['BTC', 'XAU', 'XAG'];
  var META = { BTC:{ name:'Bitcoin', perp:'BTCUSDT', spot:null, d:1 }, XAU:{ name:'Gold', perp:'XAUUSDT', spot:'XAU/USD', d:2 }, XAG:{ name:'Silver', perp:'XAGUSDT', spot:'XAG/USD', d:3 } };
  var HZ = [['day', 'Day trades', 'minutes to hours'], ['swing', 'Swing', '1–20 days'], ['hold', 'Holding', 'weeks to months']];
  var S = (function(){ try{ return JSON.parse(localStorage.getItem(KEY) || 'null') || {}; }catch(e){ return {}; } })(); S.desks = S.desks || {}; S.cur = A.indexOf(S.cur) > -1 ? S.cur : 'XAU';
  var LIVE = {}, busy = false, err = null;
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify({ cur:S.cur, desks:S.desks })); }catch(e){} }
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function L(){ return window.OMEGA_LAPI; }
  function active(p){ var e = el('page-' + p); return !!(e && e.classList.contains('active')); }
  function num(x, d){ x = +x; return isFinite(x) && x !== 0 ? x.toLocaleString('en-US', { minimumFractionDigits:d, maximumFractionDigits:d }) : '—'; }
  function pct(x, d){ x = +x; return isFinite(x) ? (x > 0 ? '+' : '') + x.toFixed(d == null ? 2 : d) + '%' : '—'; }
  function ago(t){ var d = typeof t === 'number' ? t : Date.parse(t); if(!isFinite(d)) return '—'; var m = Math.round((Date.now() - d) / 6e4); return m < 1 ? 'just now' : m < 90 ? m + ' min ago' : m < 48 * 60 ? Math.round(m / 60) + ' h ago' : Math.round(m / 1440) + ' days ago'; }
  function when(t){ var d = new Date(t); return isFinite(d) ? d.toLocaleString([], { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }) : '—'; }
  // ── data ──
  async function loadDesk(a, force){ var LA = L(); if(!LA || !LA.on()) return null; var c = S.desks[a];
    if(!force && c && Date.now() - c.at < 60e3) return c.j;
    var j = await LA.get('/assets/' + a, 45000); S.desks[a] = { at:Date.now(), j:j }; save(); return j; }
  async function loadPrice(a){ var M = META[a];
    try{ var r = await fetch('https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=' + M.perp), j = await r.json(); if(+j.lastPrice > 0) LIVE[a] = { price:+j.lastPrice, chg:+j.priceChangePercent, src:(r.headers && r.headers.get('x-omega-source')) || 'binance', at:Date.now() }; }catch(e){}
    if(M.spot && L() && L().on()){ try{ var q = await L().get('/fx/quote?symbol=' + M.spot.replace('/', ''), 30000); (LIVE[a] = LIVE[a] || {}).spot = { price:+q.price, stale:!!q.stale, bid:q.bid, ask:q.ask }; }catch(e){} } }
  async function refresh(force, which){ if(busy) return 'busy'; busy = true; err = null; var list = which ? [which] : A, got = 0;
    try{ for(var i = 0; i < list.length; i++){ try{ if(await loadDesk(list[i], force)) got++; }catch(e){ err = String(e && e.message || e).slice(0, 160); } await loadPrice(list[i]); } }
    finally{ busy = false; } draw(); return got; }
  // ── words ──
  function stateOf(j, k){ return ((j && j.horizons) || {})[k] || null; }
  function sayNow(j){ if(!j || !j.horizons) return null; var hs = HZ.map(function(h){ return [h, stateOf(j, h[0])]; }).filter(function(x){ return x[1]; });
    var calls = hs.filter(function(x){ return /TRIGGERED|CONFIRMED/.test(x[1].state); }), watch = hs.filter(function(x){ return x[1].state === 'WATCH'; }), setups = hs.filter(function(x){ return x[1].state === 'SETUP'; });
    if(calls.length) return 'A tested rule has called a trade: ' + calls.map(function(x){ var c = x[1].call || {}; return x[0][1].toLowerCase() + ' — ' + (c.side || '?') + ' (rule ' + (c.rule || '?') + ', grade ' + (c.grade || '?') + ', ' + (x[1].state === 'CONFIRMED' ? 'entry filled' : 'waiting for its entry') + ')'; }).join('; ') + '.';
    if(setups.length) return 'No trade yet. A tested rule’s conditions are forming on ' + setups.map(function(x){ return x[0][1].toLowerCase(); }).join(' and ') + '.';
    if(watch.length) return 'No trade. Watching for a big move on ' + watch.map(function(x){ return x[0][1].toLowerCase(); }).join(' and ') + ' — the direction is not known, so there is nothing to act on.';
    return 'No trade. Nothing qualifies right now, so the bot waits.'; }
  function hasRules(j){ return HZ.some(function(h){ var x = stateOf(j, h[0]); return x && x.rules && x.rules.length; }); }
  function callBlock(c, d){ if(!c) return ''; var open = /TRIGGERED|CONFIRMED/.test(c.state);
    return '<div class="dk-call"><b>' + (open ? 'Call' : 'Last call') + ': ' + esc(c.side) + '</b> · rule ' + esc(c.rule) + ' · <span class="om-tag">Grade ' + esc(c.grade || '?') + '</span>' +
      '<dl><dt>Entry</dt><dd>' + num(c.fill_price || c.entry, d) + (c.fill_price ? ' (filled ' + esc(when(c.fill_time)) + ')' : c.entry_type === 'limit' ? ' (limit, not filled yet)' : ' (next candle’s open)') + '</dd>' +
      '<dt>Stop</dt><dd>' + num(c.stop, d) + '</dd><dt>Target</dt><dd>' + (c.target ? num(c.target, d) : 'none (time exit)') + '</dd><dt>Exit by</dt><dd>' + esc(when(c.exit_by)) + '</dd>' +
      '<dt>Size</dt><dd>' + (c.size ? num(c.size.margin_usdt, 0) + ' USDT margin × ' + num(c.size.leverage, 0) + ' (the rule’s tested maximum)' : '—') + '</dd>' +
      (c.outcome ? '<dt>Outcome</dt><dd>' + esc(c.outcome) + (c.net_pct != null ? ' · ' + pct(c.net_pct) + ' after costs' : '') + '</dd>' : '') +
      '<dt>Evidence</dt><dd>' + esc(c.evidence || '—') + '</dd><dt>Status</dt><dd>' + (c.execution_allowed ? 'testnet/live rule: the trading bot may execute it' : 'paper record (research only): not an order') + '</dd></dl></div>'; }
  function hzTile(j, h, d){ var x = stateOf(j, h[0]); if(!x) return '<div class="dk-h"><h4>' + h[1] + ' <small>' + h[2] + '</small></h4><span class="dk-st">—</span><p>No reading yet.</p></div>';
    var rs = (x.reasons || []).filter(Boolean), dir = /TRIGGERED|CONFIRMED/.test(x.state) && x.direction ? ' · ' + esc(x.direction) : '';
    return '<div class="dk-h"><h4>' + h[1] + ' <small>' + h[2] + '</small></h4><span class="dk-st ' + esc(x.state) + '">' + esc(x.state) + dir + '</span><p>' + esc(x.plain || '') + '</p>' +
      '<p class="dk-sub">Since ' + esc(ago(x.since)) + (x.rules && x.rules.length ? ' · tested rules: ' + x.rules.map(function(r){ return esc(r.id) + ' (' + esc(r.grade) + ', ' + esc(r.status) + ')'; }).join(', ') : ' · no tested rule yet') + '</p>' +
      (rs.length ? '<details><summary>Why</summary><ul>' + rs.map(function(r){ return '<li>' + esc(r) + '</li>'; }).join('') + '</ul></details>' : '') + callBlock(x.call, d) + '</div>'; }
  function readFold(j, d){ var r = (j && j.read) || {}, v = r.volatility || {}, t = r.trend || {}, rg = r.ranges || {}, sc = r.scouts || {};
    var TW = { up:'above its averages, rising', down:'below its averages, falling', flat:'mixed / sideways' };
    var trend = '<table><tr><th>Candles</th><th>Where price sits</th></tr>' + ['15m', '1h', '4h', '1d'].map(function(k){ var x = t[k]; return '<tr><td>' + k + '</td><td>' + (x ? esc(TW[x.state] || x.state) : '—') + '</td></tr>'; }).join('') + '</table>';
    var vol = '<p>Volatility is <b>' + esc(v.regime || 'unknown') + '</b>' + (v.atr1h_pct != null ? ' (a typical hour moves ' + esc(v.atr1h_pct) + '% — ' + esc(v.atr1h_pctile) + 'th percentile of the last 3 weeks)' : '') + (v.rv20d_ann_pct != null ? '; daily volatility ' + esc(v.rv20d_ann_pct) + '% a year (' + esc(v.rv20d_pctile) + 'th percentile), regime ' + esc(v.regime_daily) : '') + '.' + (v.day_range_pct_median != null ? ' A typical day ranges ' + esc(v.day_range_pct_median) + '%.' : '') + '</p>';
    var ses = r.session ? '<p>Session: <b>' + esc(r.session.name) + '</b>' + (r.session.note ? ' — ' + esc(r.session.note) : '') + '.</p>' : '';
    var rng = '<table><tr><th>Range</th><th>High</th><th>Low</th><th>Where</th></tr>' + ['24h', '7d', '30d'].map(function(k){ var x = rg[k]; return x ? '<tr><td>' + k + '</td><td>' + num(x.high, d) + ' <span class="dk-sub">(' + pct(x.to_high_pct, 1) + ')</span></td><td>' + num(x.low, d) + ' <span class="dk-sub">(−' + (+x.to_low_pct).toFixed(1) + '%)</span></td><td>' + (x.position != null ? Math.round(x.position * 100) + '%' : '—') + '</td></tr>' : ''; }).join('') + '</table>';
    var fund = r.funding && r.funding.rate != null ? '<p>Funding: ' + (r.funding.rate * 100).toFixed(4) + '% per 8 h (' + (r.funding.rate >= 0 ? 'longs pay shorts' : 'shorts pay longs') + ').</p>' : '';
    var scouts = sc.missing ? '<p>Scouts: ' + esc(sc.missing) + '.</p>' : ['day', 'swing'].map(function(k){ var x = sc[k]; return x ? '<p>Scout, next ' + esc(x.horizon) + ': <b>' + Math.round(x.p_big_move * 100) + '%</b> chance of a big move either way' + (x.flag ? ' — <span class="dk-warn">flagged</span>' : '') + '. <span class="dk-sub">' + esc(x.label || '') + '</span></p>' : ''; }).join('');
    return '<details class="dk-fold"><summary>The market read <span>trend, volatility, session, ranges, scouts</span></summary><div><p class="dk-sub">' + esc(r.note || '') + '</p><h5>Trend</h5>' + trend + '<h5>Volatility</h5>' + vol + ses + '<h5>Ranges</h5><p class="dk-sub">Where = how far up the range the price sits (0% at the low, 100% at the high).</p>' + rng + fund + '<h5>Scouts (big-move risk, never a direction)</h5>' + (scouts || '<p>No scout reading.</p>') + '</div></details>'; }
  function fwdFold(j){ var f = (j && j.forward) || {}, rc = (j && j.recent_calls) || [];
    var rows = HZ.map(function(h){ var x = f[h[0]] || {}; return '<li><b>' + h[1] + ':</b> ' + esc(x.text || 'no record yet') + '</li>'; }).join('') + '<li><b>Calls:</b> ' + esc((f.calls || {}).text || 'none yet') + '</li>';
    var past = rc.length ? '<h5>Recent calls</h5><ul>' + rc.slice(0, 8).map(function(c){ return '<li>' + esc(when(c.signal_bar)) + ' · ' + esc(c.horizon) + ' · ' + esc(c.side) + ' (' + esc(c.rule) + ') → ' + esc(c.outcome || c.state) + (c.net_pct != null ? ' ' + pct(c.net_pct) : '') + '</li>'; }).join('') + '</ul>' : '';
    return '<details class="dk-fold"><summary>Forward record <span>scored after the fact</span></summary><div><p>Every reading and call is written down before its outcome and scored once its horizon has passed.</p><ul>' + rows + '</ul>' + past + '</div></details>'; }
  function nbFold(j, name){ var nb = (j && j.notebook) || []; if(!nb.length) return '';
    return '<details class="dk-fold"><summary>What I know about ' + esc(name.toLowerCase()) + ' <span>the bot’s notebook</span></summary><div>' + nb.map(function(sx){ return '<h5>' + esc(sx.title) + '</h5><ul>' + (sx.lines || []).map(function(l){ return '<li>' + esc(l) + '</li>'; }).join('') + '</ul>'; }).join('') + '</div></details>'; }
  function priceCard(a, j){ var M = META[a], lv = LIVE[a] || {}, r = (j && j.read) || {}, p = lv.price || r.price, chg = lv.price ? lv.chg : r.change_24h_pct, sp = lv.spot || r.spot;
    var src = lv.price ? (lv.src === 'okx' ? 'OKX (Binance did not answer)' : lv.src === 'omega-live-api' ? 'OMEGA Live API' : 'Binance') + ', live' : r.price ? 'the bot’s last reading' : '';
    return '<div class="om-card"><div class="dk-price"><div><span class="dk-k">' + M.name + ' · perpetual ' + M.perp + ' · 24/7</span><span class="dk-big">' + num(p, M.d) + '</span><span class="dk-sub"> ' + (isFinite(+chg) && chg != null ? '<span class="' + (+chg >= 0 ? 'dk-up' : 'dk-dn') + '">' + pct(chg) + '</span> 24h · ' : '') + esc(src) + '</span></div>' +
      (M.spot ? '<div><span class="dk-k">Spot ' + M.spot + '</span><b style="font-size:18px;color:var(--text)">' + (sp && sp.price ? num(sp.price, M.d) : '—') + '</b><span class="dk-sub"> ' + (sp && sp.price ? (sp.stale ? '<span class="dk-warn">market closed</span> (weekend or CME break)' : 'Swissquote, live') : (L() && L().on() ? 'no quote yet' : 'needs the Live API token')) + '</span></div>' : '') + '</div></div>'; }
  function deskHtml(a){ var M = META[a], c = S.desks[a], j = c && c.j, LA = L(), on = !!(LA && LA.on());
    var out = priceCard(a, j);
    if(!on) out += '<div class="om-card om-empty"><b style="color:var(--text)">Connect the OMEGA Live API to see the ' + M.name.toLowerCase() + ' bot’s desk.</b><br>Add the token in Settings &rsaquo; Data &amp; Keys. Prices above still update.<br><button class="btn-outline" type="button" data-dkset="1">Open Settings</button></div>';
    else if(!j && busy) out += '<div class="om-card"><p class="dk-say">Loading the ' + M.name.toLowerCase() + ' desk…</p></div>';
    else if(!j) out += '<div class="om-card"><p class="dk-say">The ' + M.name.toLowerCase() + ' desk could not be loaded' + (err ? ': ' + esc(err) : '') + '.</p></div>';
    else if(!j.available) out += '<div class="om-card"><p class="dk-say">The ' + M.name.toLowerCase() + ' bot has not written a desk yet.<small>' + esc(j.note || 'The asset bots run every 15 minutes once their job is switched on.') + '</small></p></div>';
    else { var stale = j.age_minutes > 60;
      out += '<div class="om-card"><span class="dk-k">What the bot says now</span><p class="dk-say">' + esc(sayNow(j)) + '<small>' + (hasRules(j) ? 'Calls come only from rules that passed a fair test.' : 'No rule for ' + M.name.toLowerCase() + ' has passed a fair test yet, so this bot calls no trades: it waits, or watches when a big move looks likely.') +
        ' Read ' + esc(ago(j.asof)) + ' from the ' + esc(j.source || 'bots') + (stale ? ' · <span class="dk-warn">this reading is old: the bots may be paused</span>' : '') + '.</small></p></div>';
      out += '<div class="dk-hz">' + HZ.map(function(h){ return hzTile(j, h, M.d); }).join('') + '</div>';
      out += readFold(j, M.d) + fwdFold(j) + nbFold(j, M.name); }
    out += '<div class="dk-acts"><button class="btn-outline" type="button" data-gsperp="' + M.perp + '">Open the 24/7 chart</button><button class="btn-ghost" type="button" data-dkref="1">' + (busy ? 'Updating…' : 'Refresh') + '</button></div>';
    out += '<p class="dk-note">Information only. A call is a paper record from a tested rule, not an order; OMEGA places no orders from this page. WAIT and WATCH mean there is no tested reason to trade.</p>';
    return out; }
  function draw(){ var host = el('desksBody'); if(host){ host.innerHTML = '<div class="om-tabs" role="tablist">' + A.map(function(a){ var j = S.desks[a] && S.desks[a].j, w = j && j.horizons ? HZ.map(function(h){ return (j.horizons[h[0]] || {}).state; }).filter(function(x){ return x && x !== 'WAIT'; })[0] : null;
        return '<button type="button" role="tab" data-dk="' + a + '" class="' + (a === S.cur ? 'on' : '') + '" aria-selected="' + (a === S.cur) + '">' + META[a].name + (w ? '<em>' + esc(w) + '</em>' : '') + '</button>'; }).join('') + '</div>' + deskHtml(S.cur); }
    home(); }
  function home(){ var h = el('homeDesks'); if(!h) return;
    h.innerHTML = A.map(function(a){ var M = META[a], j = S.desks[a] && S.desks[a].j, lv = LIVE[a] || {}, p = lv.price || (j && j.read && j.read.price);
      var st = j && j.horizons ? HZ.map(function(x){ var s0 = (j.horizons[x[0]] || {}).state; return s0 && s0 !== 'WAIT' ? s0 + ' · ' + x[1].toLowerCase() : null; }).filter(Boolean)[0] || 'WAIT on every horizon' : (L() && L().on() ? 'desk not loaded' : 'open the desk');
      return '<button type="button" class="dk-tile" data-dkgo="' + a + '"><b>' + M.name + ' desk</b><em>' + num(p, M.d) + '</em><small>' + esc(st) + '</small></button>'; }).join(''); }
  function open(a){ if(a && META[a]){ S.cur = a; save(); } window.navigate('desks'); }
  document.addEventListener('click', function(e){ var t = e.target && e.target.closest ? e.target.closest('[data-dk],[data-dkref],[data-dkset],[data-dkgo]') : null; if(!t) return;
    if(t.hasAttribute('data-dk')){ S.cur = t.getAttribute('data-dk'); save(); draw(); refresh(false, S.cur); }
    else if(t.hasAttribute('data-dkref')) refresh(true);
    else if(t.hasAttribute('data-dkgo')) open(t.getAttribute('data-dkgo'));
    else { window.navigate('settings'); try{ window.switchSettings && window.switchSettings('data'); }catch(x){} } });
  function onShow(){ draw(); refresh(false); }
  // ── the Autopilot job ──
  var JOB = { id:'desks', lane:'live', prio:3, label:'Bitcoin, gold & silver desks', what:'The three asset bots’ desks from the Live API (/assets) and live prices: every 2 minutes while Desks or Home is open, every 15 minutes otherwise. Information only, never an order.',
    every:function(){ return (active('desks') || active('command')) && !document.hidden ? 120e3 : 15*60e3; },
    run:async function(){ var LA = L(); if(!LA || !LA.on()){ for(var i = 0; i < A.length; i++) await loadPrice(A[i]); draw(); return { skip:true, text:'no Live API token: prices only', retryIn:30*60e3 }; }
      var n = await refresh(true); if(!n && err) return { error:err };
      return A.map(function(a){ var j = S.desks[a] && S.desks[a].j; return META[a].name + ' ' + (j && j.horizons ? HZ.map(function(h){ return (j.horizons[h[0]] || {}).state || '?'; }).join('/') : 'no desk'); }).join('; ') + '.'; } };
  function register(){ var Op = window.OMEGA_OPERATOR; if(!Op || !Op.jobs) return false; var J = Op.jobs(); if(!J.some(function(x){ return x.id === JOB.id; })) J.push(JOB); return true; }
  var prevAfter = window.__omegaAfterNav;
  window.__omegaAfterNav = function(p){ try{ if(typeof prevAfter === 'function') prevAfter(p); }catch(e){} if(p === 'command') setTimeout(function(){ home(); }, 30); };
  function boot(){ register(); home(); if(active('desks')) onShow(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(boot, 0); }); else setTimeout(boot, 0);
  window.OMEGA_DESKS = { open:open, onShow:onShow, refresh:refresh, draw:draw, state:function(){ return { cur:S.cur, desks:S.desks, live:LIVE, err:err }; }, sayNow:sayNow, job:JOB };
})();
</script>
'''
rep('</body>', CSS + JS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.118 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.118 ' + sep + ' build ' + o + ' UTC', 'v6.5.119 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.119 · build' in s and 'v6.5.118 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
