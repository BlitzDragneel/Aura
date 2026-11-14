"""v6.5.118: gold and silver are first-class markets wherever Bitcoin is. CREED's engine is byte-identical.
 1. Data: the Binance USDT-M perpetuals XAUUSDT and XAGUSDT (24/7) stay read directly from Binance in the browser (the
    v6.5.40 rewrite). New: when Binance does not answer (blocked region, HTTP 451/403, outage), a gold/silver request falls
    back to OKX's XAU/XAG-USDT-SWAP straight from the browser, then to the OMEGA Live API (/crypto/klines, /crypto/ticker:
    Binance -> OKX -> Gate on the server). Same Binance-shaped answer, so every page that reads Binance works unchanged.
 2. Charts: Gold and silver perpetuals are a group of the Crypto market list; a strip above the controls shows, for any
    gold or silver chart, the perpetual's price beside the spot quote XAUUSD/XAGUSD (Swissquote through the Live API;
    "market closed" at weekends and in the CME break) and the perpetual's premium to spot.
 3. Market lists (data-source layer only): CREED Scanner and Market Intelligence defaults include XAUUSDT/XAGUSDT, and
    stored lists get them once (removing them later is respected); the Analysis scan catalog; the CREED Desk's crypto
    symbol list (one list line in the CREED module, like v6.5.112's data line: the method is untouched).
 4. Forex board, Metals tab: gold and silver open the 24/7 perpetual chart (spot quote shown beside it); a note explains
    spot pauses vs the perpetual; platinum/palladium open their spot charts as before.
 5. One scheduler: the Autopilot job "metals" refreshes the strip (every minute while a gold/silver chart is open, else
    15 minutes).
usage: python3 patch118.py <v6.5.117> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


# 1. data: fallback wrapper right after the v6.5.40 metals rewrite (so everything loaded later goes through it)
FALLBACK = r'''<script>/* ═══ GOLD AND SILVER: BINANCE, THEN OKX, THEN THE LIVE API (v6.5.118) ═══
   Requests for XAUUSDT / XAGUSDT candles and tickers go to Binance first (direct, keyless, as since v6.5.40). If Binance does
   not answer (blocked region, 451/403, outage), the same request is answered from OKX's XAU/XAG-USDT-SWAP (direct from the
   browser, keyless), then from the OMEGA Live API (needs the token). The answer keeps Binance's shape, so nothing else changes.
   Read-only: nothing here places an order. */
(function(){
  'use strict';
  var PERP = { XAUUSDT:{ name:'Gold', spot:'XAUUSD', okx:'XAU-USDT-SWAP' }, XAGUSDT:{ name:'Silver', spot:'XAGUSD', okx:'XAG-USDT-SWAP' } };
  var f0 = window.fetch, ST = { binance:0, okx:0, live:0, failed:0, last:null, lastSym:null };
  var OKX_BAR = { '1m':'1m', '3m':'3m', '5m':'5m', '15m':'15m', '30m':'30m', '1h':'1H', '2h':'2H', '4h':'4H', '6h':'6Hutc', '12h':'12Hutc', '1d':'1Dutc', '1w':'1Wutc', '1M':'1Mutc' };
  var LIVE_TF = { '1m':1, '5m':1, '15m':1, '1h':1, '4h':1, '1d':1 }, STEP = { '1m':6e4, '3m':18e4, '5m':3e5, '15m':9e5, '30m':18e5, '1h':36e5, '2h':72e5, '4h':144e5, '6h':216e5, '12h':432e5, '1d':864e5, '1w':6048e5, '1M':2592e6 };
  function parse(u){ try{ var url = new URL(u, location.href); if(!/^(data-api\.binance\.vision|api[0-9]?\.binance\.com|fapi\.binance\.com)$/.test(url.hostname)) return null;
      var sym = (url.searchParams.get('symbol') || '').toUpperCase(); if(!PERP[sym]) return null;
      var m = url.pathname.match(/\/(klines|ticker\/price|ticker\/24hr)$/); if(!m) return null;
      return { sym:sym, kind:m[1], iv:url.searchParams.get('interval') || '1h', limit:Math.max(1, Math.min(1000, +url.searchParams.get('limit') || 500)) }; }catch(e){ return null; } }
  function bnRow(t, o, h, l, c, v, qv, iv){ return [t, String(o), String(h), String(l), String(c), String(v), t + (STEP[iv] || 36e5) - 1, String(qv), 0, '0', '0', '0']; }
  function okxGet(path){ return f0.call(window, 'https://www.okx.com' + path).then(function(r){ if(!r.ok) throw new Error('OKX HTTP ' + r.status); return r.json(); })
    .then(function(j){ if(!j || j.code !== '0' || !Array.isArray(j.data)) throw new Error('OKX: ' + (j && j.msg || 'bad answer')); return j.data; }); }
  async function viaOkx(q){ var P = PERP[q.sym];
    if(q.kind === 'klines'){ var bar = OKX_BAR[q.iv]; if(!bar) throw new Error('OKX has no ' + q.iv + ' candles');
      var d = await okxGet('/api/v5/market/candles?instId=' + P.okx + '&bar=' + bar + '&limit=' + Math.min(300, q.limit));
      return d.slice().reverse().map(function(k){ return bnRow(+k[0], k[1], k[2], k[3], k[4], k[6], k[7], q.iv); }); }
    var t = (await okxGet('/api/v5/market/ticker?instId=' + P.okx))[0]; if(!t) throw new Error('OKX: no ticker');
    if(q.kind === 'ticker/price') return { symbol:q.sym, price:String(t.last) };
    var o = +t.open24h, l = +t.last; return { symbol:q.sym, lastPrice:String(l), openPrice:String(o), highPrice:String(t.high24h), lowPrice:String(t.low24h),
      priceChange:String(l - o), priceChangePercent:String(o > 0 ? Math.round((l / o - 1) * 1e5) / 1e3 : 0), volume:String(t.volCcy24h), quoteVolume:String((+t.volCcy24h || 0) * l), closeTime:+t.ts }; }
  async function viaLive(q){ var LA = window.OMEGA_LAPI; if(!LA || !LA.on()) throw new Error('no Live API token');
    if(q.kind === 'klines'){ if(!LIVE_TF[q.iv]) throw new Error('the Live API has no ' + q.iv + ' candles');
      var j = await LA.get('/crypto/klines?symbol=' + q.sym + '&tf=' + q.iv + '&limit=' + q.limit, 45000);
      return (j && j.candles || []).map(function(c){ return bnRow(c.t, c.o, c.h, c.l, c.c, c.v || 0, c.qv || 0, q.iv); }); }
    var k = await LA.get('/crypto/klines?symbol=' + q.sym + '&tf=1h&limit=25', 45000), cs = (k && k.candles) || []; if(!cs.length) throw new Error('Live API: no candles');
    var last = cs[cs.length - 1].c; if(q.kind === 'ticker/price') return { symbol:q.sym, price:String(last) };
    var op = cs[0].o, hi = Math.max.apply(null, cs.map(function(c){ return c.h; })), lo = Math.min.apply(null, cs.map(function(c){ return c.l; })), vol = cs.reduce(function(a, c){ return a + (+c.v || 0); }, 0);
    return { symbol:q.sym, lastPrice:String(last), openPrice:String(op), highPrice:String(hi), lowPrice:String(lo), priceChange:String(last - op), priceChangePercent:String(Math.round((last / op - 1) * 1e5) / 1e3), volume:String(vol), quoteVolume:String(vol * last) }; }
  function answer(body, src){ return new Response(JSON.stringify(body), { status:200, headers:{ 'content-type':'application/json', 'x-omega-source':src } }); }
  function fb(input, init){ var u = typeof input === 'string' ? input : (input && input.url), q = u ? parse(u) : null;
    if(!q) return f0.call(this, input, init);
    var self = this;
    return f0.call(self, input, init).then(function(r){ if(r && r.ok){ ST.binance++; ST.last = 'binance'; ST.lastSym = q.sym; return r; } throw new Error('Binance HTTP ' + (r && r.status)); })
      .catch(function(e1){ return viaOkx(q).then(function(b){ if(q.kind === 'klines' && !b.length) throw new Error('OKX: empty'); ST.okx++; ST.last = 'okx'; ST.lastSym = q.sym; return answer(b, 'okx'); })
        .catch(function(e2){ return viaLive(q).then(function(b){ if(q.kind === 'klines' && !b.length) throw new Error('Live API: empty'); ST.live++; ST.last = 'live'; ST.lastSym = q.sym; return answer(b, 'omega-live-api'); })
          .catch(function(e3){ ST.failed++; ST.err = [e1, e2, e3].map(function(e){ return String(e && e.message || e).slice(0, 80); }).join(' | '); throw new Error('Gold/silver data: Binance, OKX and the Live API all failed (' + ST.err + ')'); }); }); }); }
  if(f0 && !f0.__gsfb){ fb.__gsfb = true; fb.__metals = !!f0.__metals; fb.__guard = !!f0.__guard; window.fetch = fb; }
  window.OMEGA_GSDATA = { PERP:PERP, parse:parse, state:function(){ return ST; }, viaOkx:viaOkx, viaLive:viaLive };
})();
</script>
'''
rep("  window.OMEGA_METALS = { symbols:function(){ return Object.keys(TRADFI); }, rewrite:rewrite, isMetalPerp:function(s){ return !!TRADFI[String(s || '').toUpperCase()]; } };\n})();\n</script>\n",
    "  window.OMEGA_METALS = { symbols:function(){ return Object.keys(TRADFI); }, rewrite:rewrite, isMetalPerp:function(s){ return !!TRADFI[String(s || '').toUpperCase()]; } };\n})();\n</script>\n" + FALLBACK)

# 3. market lists (data-source layer)
rep("      { group:'Newer large caps', list:['APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','INJUSDT','AAVEUSDT','HBARUSDT','TONUSDT','RENDERUSDT','POLUSDT'] } ],",
    "      { group:'Newer large caps', list:['APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','INJUSDT','AAVEUSDT','HBARUSDT','TONUSDT','RENDERUSDT','POLUSDT'] },\n"
    "      { group:'Gold & silver (Binance perpetuals, no key)', list:['XAUUSDT','XAGUSDT'] } ],   // v6.5.118: 24/7, first-class")
RADAR_DEF = "  var DEFAULT_UNIVERSE = { crypto:['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','TRXUSDT','DOTUSDT','BCHUSDT','NEARUSDT','ATOMUSDT','UNIUSDT','APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','FILUSDT','ICPUSDT','ETCUSDT','XLMUSDT','INJUSDT'],\n    forex:['EUR/USD','GBP/USD','USD/JPY','USD/CHF','AUD/USD','USD/CAD','NZD/USD','EUR/GBP','EUR/JPY','GBP/JPY','XAU/USD','XAG/USD'] };"
rep(RADAR_DEF, RADAR_DEF.replace("'XLMUSDT','INJUSDT']", "'XLMUSDT','INJUSDT','XAUUSDT','XAGUSDT']"))
INTEL_DEF = "    crypto:['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','TRXUSDT','DOTUSDT','BCHUSDT','NEARUSDT','ATOMUSDT','UNIUSDT','APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','FILUSDT','ICPUSDT','ETCUSDT','XLMUSDT','INJUSDT'],\n    forex:['EUR/USD','GBP/USD','USD/JPY','USD/CHF','AUD/USD','USD/CAD','NZD/USD','EUR/GBP','EUR/JPY','GBP/JPY','AUD/JPY','EUR/AUD','GBP/CHF','CAD/JPY','XAU/USD','XAG/USD']"
rep(INTEL_DEF, INTEL_DEF.replace("'XLMUSDT','INJUSDT']", "'XLMUSDT','INJUSDT','XAUUSDT','XAGUSDT']"))
rep("  var FALLBACK_CAT = { crypto:[{ group:'Crypto', list:['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','AVAXUSDT','LINKUSDT','LTCUSDT'] }],",
    "  var FALLBACK_CAT = { crypto:[{ group:'Crypto', list:['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','AVAXUSDT','LINKUSDT','LTCUSDT'] }, { group:'Gold & silver (24/7 perpetuals)', list:['XAUUSDT','XAGUSDT'] }],")
# the CREED Desk's crypto list: one data line inside the CREED module (the method is untouched; s109 excludes this line)
rep("    crypto: ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','TRXUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','DOTUSDT','BCHUSDT','NEARUSDT','ATOMUSDT','UNIUSDT','ETCUSDT','XLMUSDT','FILUSDT','ICPUSDT','APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','INJUSDT','AAVEUSDT','HBARUSDT','TONUSDT','RENDERUSDT','POLUSDT'],\n",
    "    crypto: ['BTCUSDT','XAUUSDT','XAGUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','TRXUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','DOTUSDT','BCHUSDT','NEARUSDT','ATOMUSDT','UNIUSDT','ETCUSDT','XLMUSDT','FILUSDT','ICPUSDT','APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','INJUSDT','AAVEUSDT','HBARUSDT','TONUSDT','RENDERUSDT','POLUSDT'],   // v6.5.118: gold & silver perpetuals (data list only)\n")

# 2 + 4. Charts strip host; Forex board metals note and perp links
rep('      <div class="analysis-controls-bar">\n', '      <div id="gsSpot" class="gs-spot" hidden></div>\n      <div class="analysis-controls-bar">\n')
rep("    host.innerHTML = tabs + status + list;\n    Array.prototype.forEach.call(host.querySelectorAll('[data-fxg]')",
    "    host.innerHTML = tabs + status + (g === 'metals' && window.OMEGA_GS ? window.OMEGA_GS.boardNote() : '') + list;   // v6.5.118: the 24/7 perpetuals\n    Array.prototype.forEach.call(host.querySelectorAll('[data-fxg]')")
rep("  function openOnCharts(s){ var sym = nice(plain(s)), metal = /^X(AU|AG|PT|PD)/.test(sym); window.navigate('analysis');",
    "  function openOnCharts(s){ if(window.OMEGA_GS && window.OMEGA_GS.perpFor(s)) return window.OMEGA_GS.openPerp(window.OMEGA_GS.perpFor(s));   // v6.5.118: gold/silver -> the 24/7 perpetual, spot shown beside it\n"
    "    var sym = nice(plain(s)), metal = /^X(AU|AG|PT|PD)/.test(sym); window.navigate('analysis');")

CSS = r'''<style id="gsCss">/* v6.5.118: gold & silver (theme variables only) */
.gs-spot{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:10px 14px;margin:0 0 12px;font-size:13px;color:var(--text)}
.gs-spot[hidden]{display:none}.gs-spot b{font-size:15px}.gs-spot .gs-k{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim)}
.gs-spot .gs-cell{display:flex;flex-direction:column;min-width:0}.gs-spot .gs-sub{font-size:11.5px;color:var(--text-dim)}.gs-spot .gs-closed{color:var(--amber);font-weight:600}
.gs-spot .gs-acts{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}.gs-spot .btn-ghost,.gs-spot .btn-outline{padding:5px 10px;font-size:12px}
.gs-note{background:var(--panel2);border:1px solid var(--border);border-radius:12px;padding:10px 12px;margin:0 0 10px;font-size:12.5px;color:var(--text-dim);line-height:1.5}
.gs-note b{color:var(--text)}.gs-note .gs-btns{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.gs-note .btn-outline{padding:5px 10px;font-size:12px}
</style>
'''
JS = r'''<script>/* ═══ GOLD AND SILVER, FIRST-CLASS (v6.5.118) ═══
   Charts: the spot quote beside any gold/silver chart; Forex board: the metals open the 24/7 perpetual; the CREED Scanner and
   Market Intelligence lists get the perpetuals once; the Autopilot job "metals" keeps the strip fresh. Information only. */
(function(){
  'use strict';
  var PERP = { XAUUSDT:{ name:'Gold', spot:'XAUUSD', sym:'XAU/USD' }, XAGUSDT:{ name:'Silver', spot:'XAGUSD', sym:'XAG/USD' } };
  var ONCE = 'omega_metals_added_v118', S = { spot:{}, perp:{}, at:0, err:null };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function L(){ return window.OMEGA_LAPI; }
  function plain(x){ return String(x || '').toUpperCase().replace(/[^A-Z0-9]/g, ''); }
  function perpFor(x){ var p = plain(x); if(PERP[p]) return p; if(p === 'XAUUSD') return 'XAUUSDT'; if(p === 'XAGUSD') return 'XAGUSDT'; return null; }
  function fmt(x, sym){ x = +x; if(!(x > 0)) return '—'; return x.toFixed(/XAG/.test(sym) ? 3 : 2); }
  function active(p){ var e = el('page-' + p); return !!(e && e.classList.contains('active')); }
  function chartSym(){ var e = el('symbol'); return e ? e.value : ''; }
  // ── open the 24/7 perpetual on Charts ──
  function openPerp(p){ p = perpFor(p) || 'XAUUSDT'; window.navigate('analysis');
    var ac = el('assetClass'), sel = el('symbol'); if(!sel) return;
    if(ac && ac.value !== 'crypto'){ ac.value = 'crypto'; try{ ac.dispatchEvent(new Event('change')); }catch(e){} }
    if(!Array.prototype.some.call(sel.options, function(o){ return o.value === p; })){ var o = document.createElement('option'); o.value = p; o.textContent = p; sel.appendChild(o); }
    sel.value = p; try{ sel.dispatchEvent(new Event('change')); }catch(e){}
    setTimeout(function(){ var d = el('anDeep') || sel; try{ d.scrollIntoView({ block:'start' }); }catch(e){} }, 60);
    refresh(); if(typeof window.runAnalysis === 'function') setTimeout(function(){ try{ window.runAnalysis(); }catch(e){} }, 150); }
  // ── prices: perpetual through the fetch chain (Binance -> OKX -> Live API), spot through the Live API ──
  async function perpPrice(p){ var r = await fetch('https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=' + p), j = await r.json();
    return { price:+j.lastPrice, chg:+j.priceChangePercent, src:r.headers && r.headers.get('x-omega-source') || 'binance', at:Date.now() }; }
  async function spotQuote(p){ var LA = L(); if(!LA || !LA.on()) return { none:'needs the Live API token (Settings > Data & Keys)' };
    var q = await LA.get('/fx/quote?symbol=' + PERP[p].spot, 30000); return { price:+q.price, bid:q.bid, ask:q.ask, stale:!!q.stale, age:q.age_s, src:q.source || 'swissquote', at:Date.now() }; }
  async function load(p){ var out = {}; try{ S.perp[p] = await perpPrice(p); }catch(e){ S.perp[p] = { err:String(e && e.message || e).slice(0, 140) }; }
    try{ S.spot[p] = await spotQuote(p); }catch(e){ S.spot[p] = { err:String(e && e.message || e).slice(0, 140) }; } S.at = Date.now(); return out; }
  function srcName(s){ return s === 'okx' ? 'OKX (Binance did not answer)' : s === 'omega-live-api' ? 'OMEGA Live API (Binance and OKX did not answer)' : 'Binance'; }
  function strip(){ var host = el('gsSpot'); if(!host) return; var p = perpFor(chartSym()); if(!p){ host.hidden = true; return; } host.hidden = false;
    var pp = S.perp[p] || {}, sp = S.spot[p] || {}, P = PERP[p];
    var prem = pp.price > 0 && sp.price > 0 && !sp.stale ? (pp.price / sp.price - 1) * 100 : null;
    host.innerHTML = '<div class="gs-cell"><span class="gs-k">' + P.name + ' · perpetual ' + p + '</span><b>' + fmt(pp.price, p) + '</b><span class="gs-sub">' + (pp.err ? esc(pp.err) : pp.price ? (isFinite(pp.chg) ? (pp.chg >= 0 ? '+' : '') + pp.chg.toFixed(2) + '% 24h · ' : '') + '24/7 · ' + esc(srcName(pp.src)) : 'loading…') + '</span></div>' +
      '<div class="gs-cell"><span class="gs-k">Spot ' + P.sym + '</span><b>' + (sp.price ? fmt(sp.price, p) : '—') + '</b><span class="gs-sub">' + (sp.none ? esc(sp.none) : sp.err ? esc(sp.err) : sp.stale ? '<span class="gs-closed">Market closed</span> (weekend or CME break) · last quote' : sp.price ? 'Swissquote live' + (sp.bid != null && sp.ask != null ? ' · spread $' + (+sp.ask - +sp.bid).toFixed(/XAG/.test(p) ? 3 : 2) : '') : 'loading…') + '</span></div>' +
      '<div class="gs-cell"><span class="gs-k">Perp vs spot</span><b>' + (prem == null ? '—' : (prem >= 0 ? '+' : '') + prem.toFixed(2) + '%') + '</b><span class="gs-sub">' + (prem == null ? (sp.stale ? 'not compared while spot is closed' : 'needs both prices') : 'premium of the perpetual') + '</span></div>' +
      '<div class="gs-acts">' + (perpFor(chartSym()) !== plain(chartSym()) ? '<button class="btn-outline" type="button" data-gsperp="' + p + '">24/7 perpetual chart</button>' : '') + (el('page-desks') ? '<button class="btn-ghost" type="button" data-gsdesk="' + (p === 'XAUUSDT' ? 'XAU' : 'XAG') + '">' + P.name + ' desk</button>' : '') + '</div>'; }
  async function refresh(){ var p = perpFor(chartSym()); strip(); if(!p) return 'No gold/silver chart open.'; await load(p); strip(); var pp = S.perp[p] || {}, sp = S.spot[p] || {};
    if(pp.err && (sp.err || sp.none)) return { error:pp.err };
    return PERP[p].name + ': perpetual ' + (pp.price ? fmt(pp.price, p) : 'n/a') + ', spot ' + (sp.price ? fmt(sp.price, p) + (sp.stale ? ' (closed)' : '') : 'n/a') + '.'; }
  function boardNote(){ return '<div class="gs-note"><b>Gold and silver also trade around the clock</b> as Binance perpetuals (XAUUSDT, XAGUSDT). The spot quotes below pause at weekends and in the daily CME break (21:00–22:00 UTC); the perpetuals keep trading, though thinly then. Tapping gold or silver opens the 24/7 perpetual chart with the spot quote beside it.' +
      '<div class="gs-btns"><button class="btn-outline" type="button" data-gsperp="XAUUSDT">Gold 24/7 chart</button><button class="btn-outline" type="button" data-gsperp="XAGUSDT">Silver 24/7 chart</button>' + (el('page-desks') ? '<button class="btn-ghost" type="button" data-gsdesks="1">Bitcoin, gold &amp; silver desks</button>' : '') + '</div></div>'; }
  document.addEventListener('click', function(e){ var t = e.target && e.target.closest ? e.target.closest('[data-gsperp],[data-gsdesk],[data-gsdesks]') : null; if(!t) return;
    if(t.hasAttribute('data-gsperp')) openPerp(t.getAttribute('data-gsperp'));
    else if(window.OMEGA_DESKS) window.OMEGA_DESKS.open(t.getAttribute('data-gsdesk') || null); });
  // ── stored market lists: add the perpetuals once (a later removal is respected) ──
  function addOnce(){ var done = null; try{ done = JSON.parse(localStorage.getItem(ONCE) || 'null'); }catch(e){} done = done || {};
    [['radar', 'omega_radar_universe_v1'], ['intel', 'omega_intel_universe_v1']].forEach(function(x){ if(done[x[0]]) return;
      try{ var u = JSON.parse(localStorage.getItem(x[1]) || 'null'); if(u && Array.isArray(u.crypto)){ Object.keys(PERP).forEach(function(p){ if(u.crypto.indexOf(p) < 0 && u.crypto.length < 30) u.crypto.push(p); }); localStorage.setItem(x[1], JSON.stringify(u));
        var M = x[0] === 'radar' ? window.OMEGA_RADAR : window.OMEGA_INTEL, live = M && M.universe && M.universe(); if(live && Array.isArray(live.crypto)) Object.keys(PERP).forEach(function(p){ if(live.crypto.indexOf(p) < 0 && live.crypto.length < 30) live.crypto.push(p); }); }
        done[x[0]] = Date.now(); }catch(e){} });
    try{ localStorage.setItem(ONCE, JSON.stringify(done)); }catch(e){} }
  // ── the Autopilot job ──
  var JOB = { id:'metals', lane:'live', prio:2, label:'Gold & silver prices', what:'The 24/7 gold/silver perpetual price beside the spot quote on Charts: every minute while a gold or silver chart is open, every 15 minutes otherwise. Binance, else OKX, else the Live API.',
    every:function(){ return active('analysis') && perpFor(chartSym()) && !document.hidden ? 60e3 : 15*60e3; }, run:refresh };
  function register(){ var Op = window.OMEGA_OPERATOR; if(!Op || !Op.jobs) return false; var J = Op.jobs(); if(!J.some(function(x){ return x.id === JOB.id; })) J.push(JOB); return true; }
  var prevAfter = window.__omegaAfterNav;
  window.__omegaAfterNav = function(p){ try{ if(typeof prevAfter === 'function') prevAfter(p); }catch(e){} if(p === 'analysis') setTimeout(refresh, 60); };
  function boot(){ register(); addOnce(); var sel = el('symbol'); if(sel) sel.addEventListener('change', function(){ refresh(); }); strip(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(boot, 0); }); else setTimeout(boot, 0);
  window.OMEGA_GS = { PERP:PERP, perpFor:perpFor, openPerp:openPerp, refresh:refresh, strip:strip, boardNote:boardNote, state:function(){ return S; }, job:JOB, addOnce:addOnce };
})();
</script>
'''
rep('</body>', CSS + JS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.117 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.117 ' + sep + ' build ' + o + ' UTC', 'v6.5.118 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.118 · build' in s and 'v6.5.117 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
