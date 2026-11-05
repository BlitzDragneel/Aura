<script>/* ═══ MARKET READ (v6.5.89) — the app's own read of a market, and where its liquidity lies ═══
   For BTC, ETH, SOL, BNB, XRP, gold, DOGE, LINK, LTC, ADA, AVAX (Binance USD-M perpetuals, keyless public data):
   1. Liquidity where stops gather: yesterday's and last week's highs and lows, today's so far, the 24- and 72-hour range,
      equal highs/lows (two or more hourly swing points within a small band) and round numbers. Above price: buy stops of
      shorts and breakout orders; below: sell stops of longs.
   2. Liquidity that rests in the order book: depth within 0.5%, 1% and 2% each side, and the biggest walls within 2%.
   3. Who is crowded: funding, open-interest change over 24 hours, the accounts' long/short ratio.
   4. A plain read that ends with what the research supports (plan E12: stops just beyond obvious highs/lows are swept and
      reversed only slightly more than elsewhere, about 1 stop-out in 100; trading breakouts and fakeouts lost after costs;
      the one rule that passed is the climax reversal). It describes; it does not predict.
   5. Level memory: every hour (Autopilot) the nearest pools of BTC and ETH (and any market read) are remembered and, after
      24 hours, checked: did price reach them? The page shows how often each kind of level was reached — the app's own,
      forward measurement. Also: Market Watch's finished days are checked, and a full recorded day prompts an export.
   OMEGA places no orders. */
(function(){
  'use strict';
  var H = 3600e3, FAPI = 'https://fapi.binance.com', CFG = 'omega_mread_cfg_v1', MEM = 'omega_mread_mem_v1', DAYS = 'omega_mwdays_v1';
  var MARKETS = ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','XAUUSDT','DOGEUSDT','LINKUSDT','LTCUSDT','ADAUSDT','AVAXUSDT'];
  var NAME = { BTCUSDT:'Bitcoin', ETHUSDT:'Ether', SOLUSDT:'Solana', BNBUSDT:'BNB', XRPUSDT:'XRP', XAUUSDT:'Gold', DOGEUSDT:'Dogecoin', LINKUSDT:'Chainlink', LTCUSDT:'Litecoin', ADAUSDT:'Cardano', AVAXUSDT:'Avalanche' };
  var WEIGHT = { PWH:3, PWL:3, PDH:2, PDL:2, EQH:1.5, EQL:1.5, H72:1.5, L72:1.5, H24:1, L24:1, TDH:1, TDL:1, RND:1 };
  var LABEL = { PWH:'last week’s high', PWL:'last week’s low', PDH:'yesterday’s high', PDL:'yesterday’s low', TDH:'today’s high', TDL:'today’s low', H72:'72-hour high', L72:'72-hour low', H24:'24-hour high', L24:'24-hour low', EQH:'equal highs', EQL:'equal lows', RND:'round number' };
  var state = { reads:{}, busy:false, msg:'', at:0 };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function load(k, dflt){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v == null ? dflt : v; }catch(e){ return dflt; } }
  function save(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function cfg(){ var c = load(CFG, null); return c && MARKETS.indexOf(c.sel) >= 0 ? c : { sel:'BTCUSDT' }; }
  function fmtP(x){ if(x == null || !isFinite(x)) return '—'; var a = Math.abs(x); return a >= 1000 ? x.toLocaleString('en-US', { maximumFractionDigits:0 }) : a >= 10 ? x.toFixed(2) : a >= 1 ? x.toFixed(3) : x.toPrecision(4); }
  function pct(x, d){ return x == null || !isFinite(x) ? '—' : (x > 0 ? '+' : '') + (x*100).toFixed(d == null ? 2 : d) + '%'; }
  function money(x){ if(!(x >= 0)) return '—'; return x >= 1e9 ? '$' + (x/1e9).toFixed(2) + 'B' : x >= 1e6 ? '$' + (x/1e6).toFixed(1) + 'M' : x >= 1e3 ? '$' + Math.round(x/1e3) + 'k' : '$' + Math.round(x); }
  async function getJSON(url){ var r = await fetch(url); if(!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }
  async function fetchAll(sym){ var out = { sym:sym, at:Date.now() };
    out.kl = await getJSON(FAPI + '/fapi/v1/klines?symbol=' + sym + '&interval=1h&limit=500');
    try{ out.depth = await getJSON(FAPI + '/fapi/v1/depth?symbol=' + sym + '&limit=500'); }catch(e){ out.depth = null; }
    try{ out.prem = await getJSON(FAPI + '/fapi/v1/premiumIndex?symbol=' + sym); }catch(e){ out.prem = null; }
    try{ out.oi = await getJSON(FAPI + '/futures/data/openInterestHist?symbol=' + sym + '&period=1h&limit=25'); }catch(e){ out.oi = null; }
    try{ out.ls = await getJSON(FAPI + '/futures/data/globalLongShortAccountRatio?symbol=' + sym + '&period=1h&limit=25'); }catch(e){ out.ls = null; }
    return out; }
  // ── the analysis (pure) ──
  function rowsOf(kl, nowH){ return (kl || []).map(function(k){ return { h:Math.floor(+k[0]/H), o:+k[1], hi:+k[2], lo:+k[3], c:+k[4], v:+k[5] }; }).filter(function(r){ return r.h < nowH && r.c > 0 && r.hi >= r.lo; }); }
  function roundStep(p){ var k = Math.pow(10, Math.floor(Math.log10(p)) - 1); return p/k >= 50 ? 5*k : k; }
  function analyze(sym, D, nowMs){ var nowH = Math.floor((nowMs || Date.now())/H), R = rowsOf(D.kl, nowH); if(R.length < 200) return { sym:sym, err:'not enough hourly bars' };
    var n = R.length, last = R[n-1], price = D.prem && +D.prem.markPrice > 0 ? +D.prem.markPrice : last.c, atr = null, ema = R[0].c, a2 = 2/201;
    for(var i=1; i<n; i++){ var pc = R[i-1].c, tr = Math.max(R[i].hi - R[i].lo, Math.abs(R[i].hi - pc), Math.abs(R[i].lo - pc)); atr = atr == null ? tr : atr + (tr - atr)/14; ema = ema + a2*(R[i].c - ema); }
    var A = { sym:sym, name:NAME[sym] || sym, price:price, atr:atr, atrPct:atr/price, ema200:ema, at:nowMs || Date.now(), lastH:last.h, pools:[], book:null, pos:null };
    var c24 = R[Math.max(0, n - 25)].c; A.chg24 = price/c24 - 1;
    function hl(from, to){ var hi = -Infinity, lo = Infinity, any = false; R.forEach(function(r){ if(r.h >= from && r.h < to){ any = true; if(r.hi > hi) hi = r.hi; if(r.lo < lo) lo = r.lo; } }); return any ? [hi, lo] : null; }
    var r24 = hl(nowH - 24, nowH), r72 = hl(nowH - 72, nowH); A.range24 = r24 ? (r24[0]/r24[1] - 1) : null;
    var dr = []; for(var dd = 1; dd <= 20; dd++){ var x = hl(Math.floor(nowH/24)*24 - dd*24, Math.floor(nowH/24)*24 - (dd - 1)*24); if(x) dr.push(x[0]/x[1] - 1); } dr.sort(function(a, b){ return a - b; }); A.typDay = dr.length ? dr[Math.floor(dr.length/2)] : null;
    var d0 = Math.floor(nowH/24)*24, wd = ((Math.floor(nowH/24) + 3) % 7), w0 = d0 - wd*24;
    var pd = hl(d0 - 24, d0), td = hl(d0, nowH), pw = hl(w0 - 168, w0);
    function add(kind, p){ if(!(p > 0)) return; var side = p >= price ? 'above' : 'below'; A.pools.push({ kind:kind, label:LABEL[kind], side:side, price:p, dist:p/price - 1, atrs:Math.abs(p - price)/atr, w:WEIGHT[kind] || 1 }); }
    if(pw){ add('PWH', pw[0]); add('PWL', pw[1]); } if(pd){ add('PDH', pd[0]); add('PDL', pd[1]); } if(td){ add('TDH', td[0]); add('TDL', td[1]); }
    if(r24){ add('H24', r24[0]); add('L24', r24[1]); } if(r72){ add('H72', r72[0]); add('L72', r72[1]); }
    // equal highs / lows: hourly swing points (3 bars each side) of the last 168 hours, two or more within a small band
    var tol = Math.max(0.0015*price, 0.25*atr), sh = [], sl = [];
    for(i = Math.max(3, n - 168); i < n - 3; i++){ var isH = true, isL = true; for(var k = i - 3; k <= i + 3; k++){ if(k === i) continue; if(R[k].hi >= R[i].hi) isH = false; if(R[k].lo <= R[i].lo) isL = false; } if(isH) sh.push(R[i].hi); if(isL) sl.push(R[i].lo); }
    function clusters(pts){ pts = pts.slice().sort(function(a, b){ return a - b; }); var out = [], cur = []; pts.forEach(function(p){ if(cur.length && p - cur[cur.length-1] > tol){ if(cur.length >= 2) out.push(cur); cur = []; } cur.push(p); }); if(cur.length >= 2) out.push(cur); return out.map(function(c){ return { p:c.reduce(function(a, b){ return a + b; }, 0)/c.length, n:c.length }; }); }
    clusters(sh).forEach(function(c){ if(c.p > price){ add('EQH', c.p); A.pools[A.pools.length-1].touches = c.n; A.pools[A.pools.length-1].w += 0.5*(c.n - 2); } });
    clusters(sl).forEach(function(c){ if(c.p < price){ add('EQL', c.p); A.pools[A.pools.length-1].touches = c.n; A.pools[A.pools.length-1].w += 0.5*(c.n - 2); } });
    var st = roundStep(price), up = Math.ceil(price/st)*st, dn = Math.floor(price/st)*st; if(up === price) up += st; if(dn === price) dn -= st; add('RND', up); add('RND', dn);
    A.pools = A.pools.filter(function(p){ return p.atrs <= 12 && Math.abs(p.dist) > 1e-6; });
    // merge pools closer than a quarter ATR (the stronger label wins; weights add up)
    A.pools.sort(function(a, b){ return a.price - b.price; }); var merged = [];
    A.pools.forEach(function(p){ var m = merged[merged.length-1]; if(m && m.side === p.side && Math.abs(p.price - m.price) < 0.25*atr){ if(p.w > m.w){ m.kind = p.kind; m.label = p.label; m.touches = p.touches; } m.w += p.w; m.also = (m.also || []).concat([p.label]); } else merged.push(Object.assign({}, p)); });
    A.pools = merged;
    A.above = A.pools.filter(function(p){ return p.side === 'above'; }).sort(function(a, b){ return a.price - b.price; });
    A.below = A.pools.filter(function(p){ return p.side === 'below'; }).sort(function(a, b){ return b.price - a.price; });
    // the order book
    if(D.depth && D.depth.bids && D.depth.asks){ var bids = D.depth.bids.map(function(x){ return [+x[0], +x[0]*+x[1]]; }), asks = D.depth.asks.map(function(x){ return [+x[0], +x[0]*+x[1]]; }), B = {};
      [0.005, 0.01, 0.02].forEach(function(w){ var b = 0, a = 0; bids.forEach(function(x){ if(x[0] >= price*(1 - w)) b += x[1]; }); asks.forEach(function(x){ if(x[0] <= price*(1 + w)) a += x[1]; }); B['b' + w] = b; B['a' + w] = a; });
      B.imb1 = (B['b0.01'] + B['a0.01']) > 0 ? (B['b0.01'] - B['a0.01'])/(B['b0.01'] + B['a0.01']) : null;
      function walls(list, dir){ var bw = Math.max(0.0005*price, 1e-12), buckets = {}; list.forEach(function(x){ if(Math.abs(x[0]/price - 1) > 0.02) return; var k = Math.floor(x[0]/bw); buckets[k] = (buckets[k] || 0) + x[1]; });
        var arr = Object.keys(buckets).map(function(k){ return { price:(+k + 0.5)*bw, usd:buckets[k] }; }), med = arr.map(function(x){ return x.usd; }).sort(function(a, b){ return a - b; })[Math.floor(arr.length/2)] || 0;
        return arr.filter(function(x){ return x.usd >= 3*med && x.usd > 0; }).sort(function(a, b){ return b.usd - a.usd; }).slice(0, 3).map(function(x){ x.dist = x.price/price - 1; x.x = med > 0 ? x.usd/med : null; return x; }); }
      B.bidWalls = walls(bids); B.askWalls = walls(asks); A.book = B; }
    // positioning
    var P = {}; if(D.prem){ P.funding = +D.prem.lastFundingRate; P.premium = +D.prem.indexPrice > 0 ? +D.prem.markPrice/+D.prem.indexPrice - 1 : null; }
    if(Array.isArray(D.oi) && D.oi.length >= 2){ var o0 = +D.oi[0].sumOpenInterest, o1 = +D.oi[D.oi.length-1].sumOpenInterest; P.oiChg = o0 > 0 ? o1/o0 - 1 : null; P.oiUsd = +D.oi[D.oi.length-1].sumOpenInterestValue; }
    if(Array.isArray(D.ls) && D.ls.length){ P.ls = +D.ls[D.ls.length-1].longShortRatio; P.ls0 = +D.ls[0].longShortRatio; }
    A.pos = P;
    var crowdL = (P.funding >= 0.0002) || (P.ls >= 2 && P.oiChg >= 0.03), crowdS = (P.funding != null && P.funding <= -0.0001) || (P.ls != null && P.ls <= 0.8);
    A.crowd = crowdL ? 'longs' : crowdS ? 'shorts' : 'balanced';
    // the read
    var na = A.above[0], nb = A.below[0], L = [];
    L.push(A.name + ' is at ' + fmtP(price) + ', ' + (price > ema ? 'above' : 'below') + ' its 200-hour average (' + pct(price/ema - 1, 1) + '). Last 24 hours ' + pct(A.chg24) + '; its range ' + pct(A.range24, 1).replace('+', '') + ' against a typical day of ' + pct(A.typDay, 1).replace('+', '') + (A.range24 != null && A.typDay ? (A.range24 < 0.6*A.typDay ? ' — unusually quiet, the kind of day that often ends in a move.' : A.range24 > 1.6*A.typDay ? ' — an unusually wide day.' : '.') : '.'));
    if(na) L.push('Nearest liquidity above: ' + na.label + (na.touches ? ' (' + na.touches + ' touches)' : '') + ' at ' + fmtP(na.price) + ' (' + pct(na.dist) + ', ' + na.atrs.toFixed(1) + ' hourly ranges). Short sellers’ stops and breakout buy orders tend to rest just beyond it.');
    if(nb) L.push('Nearest liquidity below: ' + nb.label + (nb.touches ? ' (' + nb.touches + ' touches)' : '') + ' at ' + fmtP(nb.price) + ' (' + pct(nb.dist) + ', ' + nb.atrs.toFixed(1) + ' hourly ranges). Long holders’ stops tend to rest just below it.');
    if(na && nb) L.push('The ' + (na.atrs < nb.atrs ? 'upside' : 'downside') + ' pool is closer' + (Math.abs(na.atrs - nb.atrs) < 0.5 ? ' (only just)' : '') + '. The weightiest pools within reach: above ' + strongest(A.above) + '; below ' + strongest(A.below) + '.');
    if(A.book){ var B2 = A.book; L.push('Order book within 1%: bids ' + money(B2['b0.01']) + ' against asks ' + money(B2['a0.01']) + (B2.imb1 != null ? ' (' + (B2.imb1 > 0.15 ? 'buyers resting heavier' : B2.imb1 < -0.15 ? 'sellers resting heavier' : 'balanced') + ')' : '') + '. ' + (B2.bidWalls[0] ? 'Biggest bid wall ' + money(B2.bidWalls[0].usd) + ' at ' + fmtP(B2.bidWalls[0].price) + ' (' + pct(B2.bidWalls[0].dist) + '). ' : '') + (B2.askWalls[0] ? 'Biggest ask wall ' + money(B2.askWalls[0].usd) + ' at ' + fmtP(B2.askWalls[0].price) + ' (' + pct(B2.askWalls[0].dist) + '). ' : '') + 'Walls can be pulled before price reaches them.'); }
    if(P.funding != null || P.oiChg != null || P.ls != null) L.push('Positioning: funding ' + (P.funding != null ? (P.funding*100).toFixed(4) + '% per period' : '—') + (P.oiChg != null ? ', open interest ' + pct(P.oiChg, 1) + ' in 24 hours' : '') + (P.ls != null ? ', accounts long/short ' + P.ls.toFixed(2) : '') + '. ' + (A.crowd === 'longs' ? 'Longs look crowded: if price falls into the pool below, forced selling of leveraged longs could add to the move.' : A.crowd === 'shorts' ? 'Shorts look crowded: if price rises into the pool above, forced buying could add to the move.' : 'Neither side looks crowded.'));
    L.push('What the research supports: stops just beyond obvious highs and lows are swept and then reversed only slightly more than elsewhere (about 1 stop-out in 100, plan E12); trading breakouts and fakeouts lost money after costs; the one rule that passed a fair test is buying a forced-selling flush that closes strong (the climax watch). This read describes where liquidity sits; it does not say which way price will go.');
    A.read = L; return A; }
  function strongest(list){ var x = list.filter(function(p){ return p.atrs <= 6; }).sort(function(a, b){ return b.w - a.w; })[0]; return x ? x.label + ' at ' + fmtP(x.price) + ' (' + pct(x.dist) + ')' : 'none within 6 ranges'; }
  // ── level memory: did price reach the pools within 24 hours? ──
  function remember(A){ if(!A || A.err) return; var M = load(MEM, { recs:[], stats:{} }), h = A.lastH;
    if(M.recs.some(function(r){ return r.s === A.sym && r.h === h; })) return;
    var keep = [A.above[0], A.above[1], A.below[0], A.below[1]].filter(Boolean).map(function(p){ return { k:p.kind, s:p.side, p:p.price, a:Math.round(p.atrs*10)/10 }; });
    M.recs.push({ s:A.sym, h:h, pools:keep }); M.recs = M.recs.filter(function(r){ return r.h >= h - 24*45; }).slice(-3000); save(MEM, M); }
  function resolve(sym, kl, nowMs){ var M = load(MEM, { recs:[], stats:{} }), nowH = Math.floor((nowMs || Date.now())/H), R = rowsOf(kl, nowH), by = {}; R.forEach(function(r){ by[r.h] = r; }); var changed = false;
    M.recs.forEach(function(rec){ if(rec.s !== sym || rec.done || rec.h + 25 > nowH) return; var hi = -Infinity, lo = Infinity, seen = 0;
      for(var h = rec.h + 1; h <= rec.h + 24; h++){ var r = by[h]; if(!r) continue; seen++; if(r.hi > hi) hi = r.hi; if(r.lo < lo) lo = r.lo; }
      if(seen < 20) return; rec.done = true; changed = true;
      rec.pools.forEach(function(p){ var hit = p.s === 'above' ? hi >= p.p : lo <= p.p, band = p.a <= 1 ? 'near' : p.a <= 3 ? 'mid' : 'far', key = p.k + '|' + band, S = M.stats[key] || (M.stats[key] = [0, 0]); S[0]++; if(hit) S[1]++; }); });
    if(changed) save(MEM, M); return M; }
  // ── Market Watch: each finished UTC day's recording ──
  function checkDays(nowMs){ var W = window.OMEGA_WATCH, out = load(DAYS, { days:{}, told:{} }); if(!W || !W._ || !W._.get) return out; var nowM = Math.floor((nowMs || Date.now())/60e3), d1 = Math.floor(nowM/1440);
    for(var d = d1 - 2; d < d1; d++){ if(out.days[d] != null) continue; var n = 0; try{ for(var m = d*1440; m < (d + 1)*1440; m++){ var v = W._.get('BTCUSDT', m, 'sC'); if(!(v > 0)) v = W._.get('BTCUSDT', m, 'pC'); if(v > 0) n++; } }catch(e){ return out; } out.days[d] = Math.round(n/1440*1000)/1000; }
    var good = Object.keys(out.days).filter(function(d){ return out.days[d] >= 0.8; }).map(Number).sort(); save(DAYS, out); out.good = good; return out; }
  async function read(sym, quiet){ var D = await fetchAll(sym), A = analyze(sym, D); state.reads[sym] = A; if(!A.err){ remember(A); resolve(sym, D.kl); } if(!quiet) render(); return A; }
  async function refresh(){ if(state.busy) return; state.busy = true; state.msg = 'Reading the market…'; render(); var c = cfg();
    try{ await read(c.sel, true); state.msg = 'Read at ' + new Date().toISOString().slice(11, 16) + ' UTC from Binance’s public data.'; }catch(e){ state.msg = 'Could not read live data (' + (e.message || e) + '). Offline?'; }
    state.busy = false; state.at = Date.now(); render(); }
  // ── the page ──
  function ladder(A){ var W = 360, Hh = 300, top = 12, bot = 12, lv = A.above.slice(0, 5).concat(A.below.slice(0, 5)), walls = A.book ? A.book.bidWalls.concat(A.book.askWalls) : [];
    var ps = lv.map(function(p){ return p.price; }).concat(walls.map(function(w){ return w.price; })).concat([A.price]), hi = Math.max.apply(null, ps), lo = Math.min.apply(null, ps), pad = (hi - lo)*0.08 || A.price*0.002; hi += pad; lo -= pad;
    var Y = function(v){ return top + (hi - v)/(hi - lo)*(Hh - top - bot); }, s = '', maxW = Math.max.apply(null, walls.map(function(w){ return w.usd; }).concat([1]));
    s += '<rect x="0" y="' + top + '" width="' + W + '" height="' + (Y(A.price) - top).toFixed(1) + '" fill="var(--bear)" fill-opacity="0.05"/><rect x="0" y="' + Y(A.price).toFixed(1) + '" width="' + W + '" height="' + (Hh - bot - Y(A.price)).toFixed(1) + '" fill="var(--bull)" fill-opacity="0.05"/>';
    walls.forEach(function(w){ var y = Y(w.price), len = 90*w.usd/maxW, isBid = w.price < A.price; s += '<rect data-wall="1" x="' + (W - 4 - len).toFixed(1) + '" y="' + (y - 3).toFixed(1) + '" width="' + len.toFixed(1) + '" height="6" rx="2" fill="' + (isBid ? 'var(--bull)' : 'var(--bear)') + '" fill-opacity="0.55"><title>' + (isBid ? 'Bid' : 'Ask') + ' wall ' + money(w.usd) + ' at ' + fmtP(w.price) + '</title></rect>'; });
    var used = [];
    lv.forEach(function(p){ var y = Y(p.price), col = p.side === 'above' ? 'var(--bear)' : 'var(--bull)', sw = 0.8 + Math.min(p.w, 5)*0.5; s += '<line data-pool="' + p.kind + '" x1="8" x2="' + (W - 100) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" stroke="' + col + '" stroke-width="' + sw.toFixed(1) + '" stroke-dasharray="' + (p.kind === 'RND' ? '2 3' : '6 3') + '"/>';
      var ty = y - 3; used.forEach(function(u){ if(Math.abs(u - ty) < 10) ty = u + (p.side === 'above' ? -10 : 10); }); used.push(ty);
      s += '<text x="10" y="' + ty.toFixed(1) + '" class="mr-lv" fill="' + col + '">' + esc(p.label) + (p.touches ? ' ×' + p.touches : '') + ' ' + esc(fmtP(p.price)) + ' (' + esc(pct(p.dist, 1)) + ')</text>'; });
    var yp = Y(A.price); s += '<line x1="0" x2="' + W + '" y1="' + yp.toFixed(1) + '" y2="' + yp.toFixed(1) + '" stroke="var(--gold)" stroke-width="2"/><text x="' + (W - 104) + '" y="' + (yp - 4).toFixed(1) + '" class="mr-now">now ' + esc(fmtP(A.price)) + '</text>';
    return '<svg class="mr-ladder" viewBox="0 0 ' + W + ' ' + Hh + '" role="img" aria-label="Where liquidity lies around the price">' + s + '<text x="' + (W - 4) + '" y="10" text-anchor="end" class="mr-ax">book walls →</text></svg>'; }
  function memTable(){ var M = load(MEM, { recs:[], stats:{} }), keys = Object.keys(M.stats); if(!keys.length) return '<p class="hint">Nothing measured yet: the first checks come 24 hours after the first reads. The Autopilot reads BTC and ETH every hour while the app is open.</p>';
    var kinds = {}; keys.forEach(function(k){ var p = k.split('|'), S = M.stats[k], r = kinds[p[0]] || (kinds[p[0]] = { near:[0, 0], mid:[0, 0], far:[0, 0] }); r[p[1]][0] += S[0]; r[p[1]][1] += S[1]; });
    var cell = function(x){ return x[0] ? Math.round(100*x[1]/x[0]) + '% <span class="hint">(' + x[0] + ')</span>' : '—'; };
    return '<table class="mr-tab"><tr><th>Kind of level</th><th>Within 1 range</th><th>1–3 ranges</th><th>Over 3</th></tr>' + Object.keys(kinds).sort().map(function(k){ var r = kinds[k]; return '<tr><td>' + esc(LABEL[k] || k) + '</td><td>' + cell(r.near) + '</td><td>' + cell(r.mid) + '</td><td>' + cell(r.far) + '</td></tr>'; }).join('') + '</table><p class="hint">Share of remembered levels that price reached within 24 hours (count in brackets), measured by the app since it started reading.</p>'; }
  function css(){ if(el('mreadCss')) return; var st = document.createElement('style'); st.id = 'mreadCss';
    st.textContent = '.mr-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px;}.mr-tabs button{border:1px solid var(--border);background:var(--panel);color:var(--text);border-radius:999px;padding:6px 11px;font-size:13px;cursor:pointer;}.mr-tabs button.on{border-color:var(--gold);color:var(--gold);background:rgba(201,162,75,.12);}' +
      '.mr-card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:12px;}.mr-read{margin:0;padding-left:18px;font-size:13px;line-height:1.55;}.mr-read li{margin:5px 0;}.mr-sec{border-top:1px solid var(--border);padding:10px 0 4px;margin-top:8px;}.mr-sec h4{margin:0 0 6px;font-size:14px;color:var(--gold);}' +
      '.mr-ladder{width:100%;height:auto;display:block;background:var(--bg);border:1px solid var(--border);border-radius:8px;}.mr-lv{font-size:8.5px;font-weight:600;paint-order:stroke;stroke:var(--bg);stroke-width:2.5px;}.mr-now{font-size:9px;font-weight:700;fill:var(--gold);}.mr-ax{font-size:8px;fill:var(--text-dim);}' +
      '.mr-tab{width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed;margin:6px 0;}.mr-tab th{text-align:left;color:var(--text-dim);font-weight:600;border-bottom:1px solid var(--border);padding:4px;}.mr-tab td{padding:4px;border-bottom:1px solid var(--border);white-space:normal;overflow-wrap:anywhere;}' +
      '.mr-start{border:1px solid var(--gold);border-radius:12px;padding:12px 14px;margin:0 0 12px;background:linear-gradient(135deg,rgba(201,162,75,.10),rgba(155,140,255,.05));}.mr-start h3{margin:0 0 6px;color:var(--gold);font-size:15px;}.mr-start p{font-size:13px;line-height:1.5;margin:4px 0;}';
    document.head.appendChild(st); }
  function html(){ var c = cfg(), A = state.reads[c.sel], h = '';
    h += '<div class="mr-start"><h3>Start here</h3><p>Pick a market. OMEGA reads it from Binance’s public data and shows <b>where liquidity lies</b>: the obvious levels where stops gather, the orders resting in the book, and which side is crowded. Then it says what the research does and does not support.</p><p>It also learns: every hour it remembers the nearest levels and, a day later, checks whether price reached them.</p></div>';
    h += '<div class="mr-tabs">' + MARKETS.map(function(s){ return '<button type="button" data-mrsel="' + s + '" class="' + (s === c.sel ? 'on' : '') + '">' + esc((NAME[s] || s).replace('Bitcoin', 'BTC').replace('Ether', 'ETH')) + '</button>'; }).join('') + '</div>';
    h += '<div class="mr-card">';
    if(!A) h += '<p class="hint">Not read yet. <button class="btn-outline" type="button" data-mr="refresh">Read ' + esc(NAME[c.sel]) + ' now</button></p>';
    else if(A.err) h += '<p class="hint">Could not read ' + esc(NAME[c.sel]) + ': ' + esc(A.err) + '.</p>';
    else { h += '<h3 style="margin:0 0 8px;">' + esc(A.name) + ' — the read</h3><ul class="mr-read">' + A.read.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
      h += '<div class="mr-sec"><h4>Where liquidity lies</h4>' + ladder(A) + '<p class="hint">Red above: buy stops and breakout orders (fuel for squeezes). Green below: sell stops of longs (fuel for flushes). Thicker lines carry more weight (last week’s and yesterday’s extremes, repeated touches). Bars on the right: the biggest resting orders in the book.</p>';
      h += '<table class="mr-tab"><tr><th>Above</th><th>Price</th><th>Away</th></tr>' + A.above.slice(0, 5).map(function(p){ return '<tr><td>' + esc(p.label) + (p.touches ? ' ×' + p.touches : '') + (p.also ? ' <span class="hint">(+' + esc(p.also.join(', ')) + ')</span>' : '') + '</td><td>' + esc(fmtP(p.price)) + '</td><td>' + esc(pct(p.dist)) + ' · ' + p.atrs.toFixed(1) + ' r</td></tr>'; }).join('') + '</table>';
      h += '<table class="mr-tab"><tr><th>Below</th><th>Price</th><th>Away</th></tr>' + A.below.slice(0, 5).map(function(p){ return '<tr><td>' + esc(p.label) + (p.touches ? ' ×' + p.touches : '') + (p.also ? ' <span class="hint">(+' + esc(p.also.join(', ')) + ')</span>' : '') + '</td><td>' + esc(fmtP(p.price)) + '</td><td>' + esc(pct(p.dist)) + ' · ' + p.atrs.toFixed(1) + ' r</td></tr>'; }).join('') + '</table><p class="hint">r = hourly ranges (ATR) away.</p></div>';
      if(A.book){ var B = A.book; h += '<div class="mr-sec"><h4>Resting orders (order book)</h4><table class="mr-tab"><tr><th>Within</th><th>Bids</th><th>Asks</th></tr>' + [0.005, 0.01, 0.02].map(function(w){ return '<tr><td>' + (w*100) + '%</td><td>' + money(B['b' + w]) + '</td><td>' + money(B['a' + w]) + '</td></tr>'; }).join('') + '</table></div>'; } }
    h += '<div class="mr-sec"><h4>What the app has learned (level memory)</h4>' + memTable() + '</div>';
    var D = checkDays(); var good = (D.good || []).map(function(d){ return new Date(d*864e5).toISOString().slice(5, 10); });
    h += '<div class="mr-sec"><h4>Market Watch recording (for plan E13)</h4><p class="hint">' + (window.OMEGA_WATCH ? 'Full days recorded (80%+ of minutes): ' + (good.length ? good.join(', ') : 'none yet') + '. Plan E13 needs 5. After a full day, export 3 days from Market Watch and send it.' : 'Market Watch is not loaded.') + '</p></div></div>';
    h += '<p class="hint" style="margin:8px 0 0;">' + esc(state.msg || '') + ' <button class="btn-outline" type="button" data-mr="refresh"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Reading…' : 'Read again') + '</button></p>';
    return h; }
  function render(){ var host = el('mreadBody'); if(!host) return; css(); host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-mrsel]'), function(b){ b.onclick = function(){ save(CFG, { sel:b.getAttribute('data-mrsel') }); render(); if(!state.reads[b.getAttribute('data-mrsel')]) refresh(); }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-mr="refresh"]'), function(b){ b.onclick = function(){ refresh(); }; }); }
  function onShow(){ render(); var c = cfg(); if(!state.reads[c.sel] || Date.now() - state.at > 15*60e3) refresh(); }
  // ── Autopilot jobs ──
  var JOBS = [
    { id:'mread', lane:'live', prio:2, label:'Market Read: BTC and ETH liquidity, and level memory', what:'Every hour: reads BTC and ETH (levels, order book, positioning), remembers the nearest liquidity and checks, a day later, whether price reached it.', every:60*60e3,
      run: async function(){ var out = []; for(var i=0; i<2; i++){ var s = ['BTCUSDT', 'ETHUSDT'][i]; try{ var A = await read(s, true); out.push(s.replace('USDT', '') + (A.err ? ' failed' : ' read')); }catch(e){ out.push(s.replace('USDT', '') + ' offline'); } } render(); return out.join(', ') + '.'; } },
    { id:'mwdays', lane:'live', prio:1, label:'Market Watch: full recorded days (plan E13)', what:'Checks each finished day of Market Watch recording; after a full day (80%+ of minutes) it reminds you to export 3 days and send them.', every:30*60e3,
      run: async function(){ var D = checkDays(), good = D.good || [], told = D.told || {}, fresh = good.filter(function(d){ return !told[d]; });
        if(fresh.length){ fresh.forEach(function(d){ told[d] = 1; }); D.told = told; save(DAYS, D);
          try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('OMEGA: a full day of Market Watch recorded', { body:'Export 3 days from Market Watch and send it for plan E13 (' + good.length + ' of 5 full days so far).' }); }catch(e){} }
        return good.length + ' full day' + (good.length === 1 ? '' : 's') + ' recorded' + (fresh.length ? ' (new: ' + fresh.map(function(d){ return new Date(d*864e5).toISOString().slice(5, 10); }).join(', ') + ' — export 3 days)' : '') + '.'; } }];
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); JOBS.forEach(function(j){ if(!J.some(function(x){ return x.id === j.id; })) J.push(j); }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  window.OMEGA_MREAD = { render:render, onShow:onShow, refresh:refresh, read:read, state:function(){ return state; }, MARKETS:MARKETS, JOBS:JOBS, _:{ analyze:analyze, rowsOf:rowsOf, remember:remember, resolve:resolve, checkDays:checkDays, roundStep:roundStep, html:html } };
})();
</script>
