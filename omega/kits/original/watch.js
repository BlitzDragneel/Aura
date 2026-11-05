<script>/* ═══ MARKET WATCH (v6.5.77) — the recorder: every public footprint of large buying and selling, minute by minute,
   and a second-by-second flight recording around every sudden move (research/PLAN16_DRAFT.md) ═══
   Records, while the app is open, for each watched coin (default: the 25 studied coins):
   - spot and perpetual aggressive buying and selling (every trade: who crossed the spread), the largest single orders
     and "large orders" (one taker order of at least 0.02% of the coin's 24-hour volume, and at least 10,000 USDT);
   - the visible spot order book (top 20 levels each second: bids against asks, spread);
   - the perpetual's mark price, index price, premium and funding rate (every second);
   - liquidations on every Binance perpetual (Binance's live sample: at most one per coin per second);
   - Coinbase BTC-USD, ETH-USD and USDT-USD (US spot buyers' price);
   - every 15 minutes, 5-minute open interest, long/short account and position ratios and taker buy/sell ratio from
     Binance (this history reaches 30 days back, so gaps while the app was closed are filled);
   - every 15 minutes (setting), a liquidity map from a 500-level spot order book: bids and asks within 0.5/1/2/5% and
     the three largest walls each side.
   Sudden moves (a 60-second move of 4+ of the coin's own 1-minute standard deviations, or 10M USDT of liquidations
   across the market in 60 seconds) open a flight recording: the 30 minutes before and 60 minutes after, second by
   second. All of it is description, not a signal: nothing here trades or votes until round 16 tests it.
   Binance moved its futures streams in 2026 (trades, mark price and liquidations on /market; the old /ws and /stream
   addresses ended 23 Apr 2026). Minutes with no data stay empty (never filled in). Runs only while the app is open. */
(function(){
  'use strict';
  var SAPI = 'https://api.binance.com', FAPI = 'https://fapi.binance.com';
  var URL_SPOT = 'wss://stream.binance.com:9443/stream?streams=', URL_FMKT = 'wss://fstream.binance.com/market/stream?streams=', URL_CB = 'wss://ws-feed.exchange.coinbase.com';
  var COINS0 = ['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','TRXUSDT','AVAXUSDT','LINKUSDT','DOTUSDT','BCHUSDT','LTCUSDT','NEARUSDT','UNIUSDT','ATOMUSDT','XLMUSDT','ETCUSDT','FILUSDT','ICPUSDT','APTUSDT','ARBUSDT','OPUSDT','INJUSDT','SUIUSDT'];
  // per coin, per minute (Float32, NaN = no data)
  var F = ['sC','sH','sL','sBuy','sSell','sN','sWBuy','sWSell','sWN','sMaxB','sMaxS','sImb','sBidQ','sAskQ','sSprd','pC','pBuy','pSell','pN','pWBuy','pWSell','pWN','pMaxB','pMaxS','prem','mark','idx','fr','liqL','liqS','liqN'];
  // the market, per minute: liquidations on every perpetual, Coinbase prices, Binance BTC/ETH spot
  var MF = ['liqL','liqS','liqN','cbBTC','cbETH','cbUSDT','bnBTC','bnETH'];
  // a flight recording's row, one per second
  var B = ['t','sP','sBuy','sSell','pP','pBuy','pSell','liqL','liqS','sImb','prem'];
  // a liquidity map snapshot (quote USDT within each distance of the mid; walls: distance % and size)
  var BK = ['t','mid','b05','b1','b2','b5','a05','a1','a2','a5','bSpan','aSpan','bw1d','bw1q','bw2d','bw2q','bw3d','bw3q','aw1d','aw1q','aw2d','aw2q','aw3d','aw3q'];
  var NF = F.length, NMF = MF.length, NB = B.length, IX = {}, MX = {}; F.forEach(function(k, i){ IX[k] = i; }); MF.forEach(function(k, i){ MX[k] = i; });
  var MKT = '_MKT', M = 60e3, H = 3600e3, BUF = 1800, POST = 3600, PAD = 7, KEEP_H = 24*14, MEM_H = 26, EV_MAX = 150, POS_DAYS = 45;
  var CFG_KEY = 'omega_watch_cfg_v1', DBN = 'omega_watch';
  function defCfg(){ return { on:false, mode:'full', coins:COINS0.slice(), awake:true, bookEvery:15, k:4, liqBurst:10e6 }; }
  function cfg(){ try{ var v = JSON.parse(localStorage.getItem(CFG_KEY) || 'null'); if(v && typeof v === 'object'){ var d = defCfg(); for(var k in d) if(!(k in v)) v[k] = d[k]; return v; } }catch(e){} return defCfg(); }
  function setCfg(v){ try{ localStorage.setItem(CFG_KEY, JSON.stringify(v)); }catch(e){} }
  function el(id){ return typeof document !== 'undefined' && document.getElementById ? document.getElementById(id) : null; }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function pad(h){ var s = String(h); while(s.length < PAD) s = '0' + s; return s; }
  function nan(x){ return x !== x; }

  // ── storage (IndexedDB; replaceable in tests) ──
  var STORES = { min:'k', pos:'sym', book:'k', events:'id' };
  function idbStore(){
    var dbp = null;
    function db(){ if(dbp) return dbp; dbp = new Promise(function(res, rej){ var r = indexedDB.open(DBN, 1);
      r.onupgradeneeded = function(){ var d = r.result; Object.keys(STORES).forEach(function(n){ if(!d.objectStoreNames.contains(n)) d.createObjectStore(n, { keyPath:STORES[n] }); }); };
      r.onsuccess = function(){ res(r.result); }; r.onerror = function(){ dbp = null; rej(r.error); }; }); return dbp; }
    function tx(name, mode, fn){ return db().then(function(d){ return new Promise(function(res, rej){ var t = d.transaction(name, mode), s = t.objectStore(name), out = fn(s); t.oncomplete = function(){ res(out ? out.result : undefined); };   /* out is the request (null for writes); a missing key gives undefined */ t.onerror = t.onabort = function(){ rej(t.error); }; }); }); }
    return {
      putMany:function(name, recs){ if(!recs.length) return Promise.resolve(); return tx(name, 'readwrite', function(s){ recs.forEach(function(r){ s.put(r); }); return null; }); },
      get:function(name, key){ return tx(name, 'readonly', function(s){ return s.get(key); }); },
      range:function(name, lo, hi){ return tx(name, 'readonly', function(s){ return s.getAll(IDBKeyRange.bound(lo, hi)); }); },
      keys:function(name){ return tx(name, 'readonly', function(s){ return s.getAllKeys(); }); },
      del:function(name, keys){ if(!keys.length) return Promise.resolve(); return tx(name, 'readwrite', function(s){ keys.forEach(function(k){ s.delete(k); }); return null; }); },
      all:function(name){ return tx(name, 'readonly', function(s){ return s.getAll(); }); }
    }; }
  var store = (typeof indexedDB !== 'undefined') ? idbStore() : null;

  // ── minute blocks in memory (the last 26 hours), written to storage every minute ──
  var blocks = {}, dirty = {}, av = {};
  function bkey(sym, h){ return sym + '|' + pad(h); }
  function blk(sym, h){ var k = bkey(sym, h), b = blocks[k]; if(!b){ var a = new Float32Array(60*(sym === MKT ? NMF : NF)); a.fill(NaN); b = blocks[k] = { k:k, sym:sym, h:h, a:a }; } dirty[k] = 1; return b.a; }
  function slot(sym, t, f){ var m = Math.floor(t/M), h = Math.floor(m/60), a = blk(sym, h), mk = sym === MKT; return { a:a, i:(m - h*60)*(mk ? NMF : NF) + (mk ? MX[f] : IX[f]) }; }
  function add(sym, t, f, v){ var s = slot(sym, t, f); s.a[s.i] = (nan(s.a[s.i]) ? 0 : s.a[s.i]) + v; }
  function put(sym, t, f, v){ var s = slot(sym, t, f); s.a[s.i] = v; }
  function hi(sym, t, f, v){ var s = slot(sym, t, f); if(nan(s.a[s.i]) || v > s.a[s.i]) s.a[s.i] = v; }
  function lo(sym, t, f, v){ var s = slot(sym, t, f); if(nan(s.a[s.i]) || v < s.a[s.i]) s.a[s.i] = v; }
  function avg(sym, t, f, v){ var m = Math.floor(t/M), k = sym + '\u0001' + f, x = av[k]; if(!x || x.m !== m) x = av[k] = { m:m, s:0, n:0 }; x.s += v; x.n++; put(sym, t, f, x.s/x.n); }
  function get(sym, m, f){ var mk = sym === MKT, fi = mk ? MX[f] : IX[f]; if(fi === undefined) return NaN; var h = Math.floor(m/60), b = blocks[bkey(sym, h)]; if(!b) return NaN; return b.a[(m - h*60)*(mk ? NMF : NF) + fi]; }

  // ── clock: exchange time, from trade timestamps (the phone's clock may be off) ──
  var skew = null;
  function clock(T){ if(!(T > 0)) return; var d = Date.now() - T; if(skew == null){ skew = d; return; } if(Math.abs(d - skew) > 300e3) return; skew += (d - skew)*0.05; }   // a stray old timestamp is ignored
  function now(){ return Date.now() - (skew || 0); }

  // ── second-by-second rows (the flight recorder's buffer: the last 30 minutes per coin) ──
  var secs = {}, rings = {}, open = {}, lastEv = {}, lastSec = 0, liqWin = [];
  function sacc(sym){ return secs[sym] || (secs[sym] = { sP:NaN, sBuy:0, sSell:0, pP:NaN, pBuy:0, pSell:0, liqL:0, liqS:0, sImb:NaN, prem:NaN }); }
  function ring(sym){ var r = rings[sym]; if(!r){ r = rings[sym] = { a:new Float64Array(BUF*NB), n:0 }; r.a.fill(NaN); } return r; }
  function pushSecond(sym, s){ var x = secs[sym]; if(!x) return null; var r = ring(sym), o = (r.n % BUF)*NB, row = [s, x.sP, x.sBuy, x.sSell, x.pP, x.pBuy, x.pSell, x.liqL, x.liqS, x.sImb, x.prem];
    for(var i=0; i<NB; i++) r.a[o + i] = row[i]; r.n++; x.sBuy = x.sSell = x.pBuy = x.pSell = x.liqL = x.liqS = 0;   // prices, book and premium carry forward
    var ev = open[sym]; if(ev){ ev.post.push(row); if(ev.post.length >= POST) finishEvent(ev); } return row; }
  function rowAt(r, j){ var o = (j % BUF)*NB, row = []; for(var i=0; i<NB; i++) row.push(r.a[o + i]); return row; }
  function lastRows(sym, k){ var r = rings[sym]; if(!r || !r.n) return []; var n = Math.min(k, r.n, BUF), out = []; for(var j = r.n - n; j < r.n; j++) out.push(rowAt(r, j)); return out; }
  function px(row){ return row[1] > 0 ? row[1] : (row[4] > 0 ? row[4] : NaN); }

  // ── large orders: consecutive trades of one taker order (same time, same side) are one order ──
  var pend = {}, thr = {};
  function threshold(sym, mk){ var t = thr[sym]; var v = t ? t[mk] : null; return v > 0 ? v : 1e5; }
  function order(sym, mk, T, sell, q){ var k = mk + sym, p = pend[k]; if(p && p.T === T && p.sell === sell){ p.q += q; return; } if(p) closeOrder(sym, mk, p); pend[k] = { T:T, sell:sell, q:q }; }
  function closeOrder(sym, mk, p){ hi(sym, p.T, mk + (p.sell ? 'MaxS' : 'MaxB'), p.q); if(p.q >= threshold(sym, mk)){ add(sym, p.T, mk + (p.sell ? 'WSell' : 'WBuy'), p.q); add(sym, p.T, mk + 'WN', 1); } }
  function flushOrders(beforeT){ for(var k in pend){ var p = pend[k]; if(p.T < beforeT){ closeOrder(k.slice(1), k[0], p); delete pend[k]; } } }

  // ── message handlers ──
  var want = {}, kl = {};
  function onTrade(mk, d){ var sym = d.s, p = +d.p, q = +d.q, T = +d.T, sell = !!d.m; if(!want[sym] || !(p > 0) || !(q > 0) || !(T > 0)) return; var Q = p*q;
    clock(T); add(sym, T, mk + (sell ? 'Sell' : 'Buy'), Q); add(sym, T, mk + 'N', 1); put(sym, T, mk + 'C', p);
    var x = sacc(sym);
    if(mk === 's'){ hi(sym, T, 'sH', p); lo(sym, T, 'sL', p); x.sP = p; if(sell) x.sSell += Q; else x.sBuy += Q; if(sym === 'BTCUSDT'){ put(MKT, T, 'bnBTC', p); sacc(MKT).sP = p; } if(sym === 'ETHUSDT') put(MKT, T, 'bnETH', p); }
    else { x.pP = p; if(sell) x.pSell += Q; else x.pBuy += Q; if(sym === 'BTCUSDT') sacc(MKT).pP = p; }
    order(sym, mk, T, sell, Q); }
  function onKline(mk, d){ var k = d.k; if(!k) return; var sym = k.s || d.s; if(!want[sym]) return; var t = +k.t, q = +k.q, Qb = +k.Q, c = +k.c; if(!(t > 0) || !(c > 0)) return;
    clock(+d.E); put(sym, t, mk + 'C', c); put(sym, t, mk + 'Buy', Qb); put(sym, t, mk + 'Sell', q - Qb); put(sym, t, mk + 'N', +k.n);
    if(mk === 's'){ put(sym, t, 'sH', +k.h); put(sym, t, 'sL', +k.l); if(sym === 'BTCUSDT'){ put(MKT, t, 'bnBTC', c); sacc(MKT).sP = c; } if(sym === 'ETHUSDT') put(MKT, t, 'bnETH', c); }
    var key = mk + sym, pr = kl[key], dB = Qb, dS = q - Qb; if(pr && pr.t === t){ dB = Qb - pr.Q; dS = (q - Qb) - (pr.q - pr.Q); } kl[key] = { t:t, Q:Qb, q:q };
    var x = sacc(sym); if(mk === 's'){ x.sP = c; x.sBuy += Math.max(0, dB); x.sSell += Math.max(0, dS); } else { x.pP = c; x.pBuy += Math.max(0, dB); x.pSell += Math.max(0, dS); if(sym === 'BTCUSDT') sacc(MKT).pP = c; } }
  function onDepth(sym, d){ if(!want[sym]) return; var b = d.bids || d.b, a = d.asks || d.a; if(!b || !a || !b.length || !a.length) return; var bq = 0, aq = 0, i;
    for(i=0; i<b.length; i++) bq += b[i][0]*b[i][1]; for(i=0; i<a.length; i++) aq += a[i][0]*a[i][1];
    var bb = +b[0][0], ba = +a[0][0]; if(!(bq + aq > 0) || !(bb > 0) || !(ba > 0)) return; var t = now(), imb = (bq - aq)/(bq + aq);
    avg(sym, t, 'sImb', imb); avg(sym, t, 'sBidQ', bq); avg(sym, t, 'sAskQ', aq); avg(sym, t, 'sSprd', (ba - bb)/((ba + bb)/2)*1e4); sacc(sym).sImb = imb; }
  function onMark(d){ var sym = d.s; if(!want[sym]) return; var t = +d.E || now(), mp = +d.p, ix = +d.i, r = +d.r; if(!(mp > 0)) return;
    put(sym, t, 'mark', mp); if(isFinite(r) && d.r !== '' && d.r != null) put(sym, t, 'fr', r);
    var x = sacc(sym); if(ix > 0){ put(sym, t, 'idx', ix); var pr = mp/ix - 1; avg(sym, t, 'prem', pr); x.prem = pr; } if(nan(x.pP)) x.pP = mp; }
  function onLiq(o){ if(!o) return; var sym = o.s, q = (+o.ap || +o.p)*(+o.z || +o.q), T = +o.T || now(), L = o.S === 'SELL'; if(!sym || !(q > 0)) return;   // a SELL force order closes a long
    add(MKT, T, L ? 'liqL' : 'liqS', q); add(MKT, T, 'liqN', 1); var y = sacc(MKT); if(L) y.liqL += q; else y.liqS += q; liqWin.push([T, q]);
    if(want[sym]){ add(sym, T, L ? 'liqL' : 'liqS', q); add(sym, T, 'liqN', 1); var x = sacc(sym); if(L) x.liqL += q; else x.liqS += q; } }
  function onSpot(m){ var d = m && m.data; if(!d) return; if(d.e === 'aggTrade') onTrade('s', d); else if(d.e === 'kline') onKline('s', d); else if(d.bids && m.stream) onDepth(m.stream.split('@')[0].toUpperCase(), d); }
  function onFut(m){ var d = m && (m.data || m); if(!d) return; if(d.e === 'aggTrade') onTrade('p', d); else if(d.e === 'markPriceUpdate') onMark(d); else if(d.e === 'forceOrder') onLiq(d.o); else if(d.e === 'kline') onKline('p', d); }
  function onCB(d){ if(!d || d.type !== 'ticker') return; var p = +d.price, t = Date.parse(d.time) || Date.now(); var f = d.product_id === 'BTC-USD' ? 'cbBTC' : d.product_id === 'ETH-USD' ? 'cbETH' : d.product_id === 'USDT-USD' ? 'cbUSDT' : null; if(f && p > 0) put(MKT, t, f, p); }

  // ── connections ──
  var socks = {}, running = false, tickIv = null, minIv = null, st = { msgs:0, bytes:0, since:null, events:[], pos:{}, book:{}, err:null, rate:{ at:Date.now(), msgs:0, bytes:0, mps:0, kbps:0 }, dayBytes:0, day:null };
  function sock(name, url, onmsg, onopen){ var S = socks[name] || (socks[name] = { name:name, state:'off', n:0, bytes:0, last:0, tries:0, err:null, ws:null, timer:null, bad:0 }); S.url = url; S.onmsg = onmsg; S.onopen = onopen; connect(S); return S; }
  function connect(S){ if(S.ws || !running) return; if(typeof WebSocket === 'undefined'){ S.state = 'unsupported'; return; }
    var ws; try{ ws = new WebSocket(S.url); }catch(e){ S.state = 'error'; S.err = String(e && e.message || e); retry(S); return; }
    S.ws = ws; S.state = 'connecting'; S.opened = 0;
    ws.onopen = function(){ S.state = 'open'; S.opened = Date.now(); if(S.onopen) try{ S.onopen(ws); }catch(e){} };
    ws.onmessage = function(ev){ var txt = typeof ev.data === 'string' ? ev.data : ''; S.n++; S.bytes += txt.length; S.last = Date.now(); if(S.state !== 'live'){ S.state = 'live'; S.tries = 0; S.err = null; } st.msgs++; st.bytes += txt.length; st.dayBytes += txt.length;
      var m; try{ m = JSON.parse(txt); }catch(e){ S.bad++; return; } try{ S.onmsg(m); }catch(e){ S.bad++; S.lastErr = String(e && e.message || e); } };
    ws.onerror = function(){ S.err = 'connection error'; };
    ws.onclose = function(ev){ S.ws = null; S.code = ev && ev.code; S.state = running ? 'retrying' : 'off'; retry(S); }; }
  function retry(S){ if(!running) return; clearTimeout(S.timer); var wait = [2, 5, 15, 30, 60][Math.min(S.tries++, 4)]*1000; S.timer = setTimeout(function(){ S.timer = null; connect(S); }, wait); }
  function closeAll(){ Object.keys(socks).forEach(function(k){ var S = socks[k]; clearTimeout(S.timer); if(S.ws){ try{ S.ws.onclose = null; S.ws.close(); }catch(e){} S.ws = null; } S.state = 'off'; }); }
  function watchdog(){ var t = Date.now(); Object.keys(socks).forEach(function(k){ var S = socks[k]; if(!S.ws) return; var quiet = t - (S.last || S.opened || t);
      if(S.state === 'open' && S.opened && t - S.opened > 60e3) S.state = 'silent';                         // connected but nothing arrives: the address may have changed
      if(S.state === 'live' && quiet > 120e3 && k !== 'coinbase'){ try{ S.ws.close(); }catch(e){} } }); }
  function streams(c){ var sp = [], fm = []; c.coins.forEach(function(s0){ var s = s0.toLowerCase();
      if(c.mode === 'light'){ sp.push(s + '@kline_1m'); fm.push(s + '@kline_1m'); } else { sp.push(s + '@aggTrade'); fm.push(s + '@aggTrade'); }
      sp.push(s + '@depth20'); fm.push(s + '@markPrice@1s'); }); fm.push('!forceOrder@arr'); return { spot:sp, fut:fm }; }
  function start(){ if(running) return; var c = cfg(); running = true; want = {}; c.coins.forEach(function(s){ want[s] = 1; }); st.since = Date.now(); st.mode = c.mode;
    var S = streams(c);
    sock('spot', URL_SPOT + S.spot.join('/'), onSpot);
    sock('futures', URL_FMKT + S.fut.join('/'), onFut);
    sock('coinbase', URL_CB, onCB, function(ws){ ws.send(JSON.stringify({ type:'subscribe', product_ids:['BTC-USD', 'ETH-USD', 'USDT-USD'], channels:['ticker'] })); });
    tickIv = setInterval(second, 1000); minIv = setInterval(minuteJobs, 60e3); wake(); jobs(); render(); }
  function stop(){ Object.keys(open).forEach(function(k){ var ev = open[k]; ev.interrupted = true; finishEvent(ev); }); running = false; closeAll(); clearInterval(tickIv); clearInterval(minIv); tickIv = minIv = null; release(); return persist().then(function(){ render(); }); }

  // ── every second: close orders, write a row per coin, look for sudden moves ──
  function second(){ var s = Math.floor(now()/1000) - 1; if(s <= lastSec) return; flushOrders((s - 1)*1000);
    for(var sym in secs) pushSecond(sym, s); lastSec = s; checkEvents(s);
    var t = Date.now(), dt = (t - st.rate.at)/1000; if(dt >= 5){ st.rate.mps = (st.msgs - st.rate.msgs)/dt; st.rate.kbps = (st.bytes - st.rate.bytes)/dt/1024; st.rate.at = t; st.rate.msgs = st.msgs; st.rate.bytes = st.bytes; watchdog(); maybeRender(); }
    var dy = new Date(t).toISOString().slice(0, 10); if(dy !== st.day){ st.day = dy; st.dayBytes = 0; } }
  var sigC = {};
  function sigma(sym){ var m1 = Math.floor(now()/M), c = sigC[sym]; if(c && c.m === m1) return c.v; var prev = NaN, s = 0, s2 = 0, n = 0;
    for(var m = m1 - 1440; m < m1; m++){ var p = get(sym, m, 'sC'); if(!(p > 0)) p = get(sym, m, 'pC'); if(p > 0 && prev > 0){ var x = Math.log(p/prev); s += x; s2 += x*x; n++; } prev = p > 0 ? p : NaN; }
    var v = n >= 360 ? Math.sqrt(Math.max(0, (s2 - s*s/n)/(n - 1))) : null; sigC[sym] = { m:m1, v:v || null }; return v || null; }
  function checkEvents(s){ var c = cfg();
    for(var sym in rings){ if(sym === MKT || open[sym] || (lastEv[sym] && s - lastEv[sym] < 1800)) continue; var r = rings[sym]; if(r.n < 61) continue;
      var a = rowAt(r, r.n - 1), b = rowAt(r, r.n - 61); if(Math.abs((a[0] - b[0]) - 60) > 5) continue;   // the row 60 s back must really be 60 s back (not a throttled tab)
      var p1 = px(a), p0 = px(b); if(!(p1 > 0 && p0 > 0)) continue; var sg = sigma(sym); if(!sg) continue; var x = Math.log(p1/p0); if(Math.abs(x) >= c.k*sg) openEvent(sym, 'move', s, x, sg); }
    var from = s*1000 - 60e3, L = 0; liqWin = liqWin.filter(function(z){ return z[0] >= from; }); for(var i=0; i<liqWin.length; i++) L += liqWin[i][1];
    if(L >= c.liqBurst && !open[MKT] && !(lastEv[MKT] && s - lastEv[MKT] < 1800)) openEvent(MKT, 'liq', s, L, null); }

  // ── flight recordings ──
  function openEvent(sym, kind, s, x, sg){ var ev = { id:sym + '-' + s, sym:sym, kind:kind, t:s*1000, x:x, sigma:sg, z:sg ? x/sg : null, pre:lastRows(sym, BUF), post:[], done:false, ctx:context(sym, s) };
    open[sym] = ev; lastEv[sym] = s; st.events.unshift(brief(ev)); if(st.events.length > EV_MAX) st.events.length = EV_MAX; saveEvent(ev); maybeRender(true); return ev; }
  function outcome(ev){ var p0 = NaN; for(var i = ev.pre.length - 1; i >= 0 && !(p0 > 0); i--) p0 = px(ev.pre[i]); var o = { n:ev.post.length };
    if(!(p0 > 0)) return o; var up = 0, dn = 0; ev.post.forEach(function(r){ var p = px(r); if(p > 0){ var x = p/p0 - 1; if(x > up) up = x; if(x < dn) dn = x; } });
    function at(k){ for(var j = Math.min(k, ev.post.length) - 1; j >= Math.max(0, k - 30); j--){ var p = px(ev.post[j]); if(p > 0) return p/p0 - 1; } return null; }
    o.p0 = p0; o.r5 = ev.post.length >= 300 ? at(300) : null; o.r15 = ev.post.length >= 900 ? at(900) : null; o.r60 = ev.post.length >= 3600 ? at(3600) : null; o.maxUp = up; o.maxDn = dn; return o; }
  function finishEvent(ev){ ev.done = true; ev.after = outcome(ev); delete open[ev.sym]; var b = st.events.filter(function(e){ return e.id === ev.id; })[0]; if(b) Object.assign(b, brief(ev)); saveEvent(ev); maybeRender(true); }
  function brief(ev){ return { id:ev.id, sym:ev.sym, kind:ev.kind, t:ev.t, x:ev.x, z:ev.z, ctx:ev.ctx, after:ev.after || outcome(ev), done:ev.done, nPost:ev.post.length, interrupted:!!ev.interrupted }; }
  function f32rows(rows, s0){ var a = new Float32Array(rows.length*NB); rows.forEach(function(r, j){ for(var i=0; i<NB; i++) a[j*NB + i] = i === 0 ? r[0] - s0 : r[i]; }); return a; }
  function rowsOf(a, n, s0){ var out = []; for(var j=0; j<n; j++){ var r = []; for(var i=0; i<NB; i++) r.push(i === 0 ? a[j*NB] + s0 : a[j*NB + i]); out.push(r); } return out; }
  function saveEvent(ev){ if(!store) return Promise.resolve(); var s0 = ev.t/1000, b = brief(ev);
    b.nPre = ev.pre.length; b.pre = f32rows(ev.pre, s0); b.post = f32rows(ev.post, s0); b.sigma = ev.sigma;
    return store.putMany('events', [b]).then(pruneEvents).catch(function(e){ st.err = 'saving a recording: ' + (e && e.message || e); }); }
  function pruneEvents(){ return store.keys('events').then(function(ks){ if(ks.length <= EV_MAX) return; ks.sort(function(a, b){ return +a.split('-').pop() - +b.split('-').pop(); }); return store.del('events', ks.slice(0, ks.length - EV_MAX)); }); }

  // ── what was going on at a moment (facts only) ──
  function win(sym, m1, n){ var o = { sNet:0, pNet:0, wNet:0, wN:0, liqL:0, liqS:0, imb:0, imbN:0, p0:NaN, p1:NaN, prem:NaN, mins:0, sTot:0, pTot:0 };
    for(var m = m1 - n + 1; m <= m1; m++){ var c = get(sym, m, 'sC'); if(!(c > 0)) c = get(sym, m, 'pC'); if(c > 0){ if(!(o.p0 > 0)) o.p0 = c; o.p1 = c; o.mins++; }
      function g(f){ var v = get(sym, m, f); return nan(v) ? 0 : v; }
      o.sNet += g('sBuy') - g('sSell'); o.pNet += g('pBuy') - g('pSell'); o.sTot += g('sBuy') + g('sSell'); o.pTot += g('pBuy') + g('pSell');
      o.wNet += (g('sWBuy') + g('pWBuy')) - (g('sWSell') + g('pWSell')); o.wN += g('sWN') + g('pWN'); o.liqL += g('liqL'); o.liqS += g('liqS');
      var im = get(sym, m, 'sImb'); if(!nan(im)){ o.imb += im; o.imbN++; } var pr = get(sym, m, 'prem'); if(!nan(pr)) o.prem = pr; }
    o.chg = o.p0 > 0 && o.p1 > 0 ? o.p1/o.p0 - 1 : null; o.imb = o.imbN ? o.imb/o.imbN : null; return o; }
  function oiChange(sym, hours, at){ var P = posMem[sym]; if(!P || !P.oi || P.oi.length < 2) return null; var arr = P.oi, t1 = at || Infinity, i = arr.length - 1; while(i >= 0 && arr[i][0] > t1) i--; if(i < 1) return null;
    var tgt = arr[i][0] - hours*H, j = i; while(j > 0 && arr[j][0] > tgt) j--; if(!(arr[j][2] > 0) || arr[i][0] - arr[j][0] < hours*H*0.8) return null; return arr[i][2]/arr[j][2] - 1; }
  function session(t){ var d = new Date(t), h = d.getUTCHours() + d.getUTCMinutes()/60, w = d.getUTCDay(), tags = [];
    tags.push(h < 7 ? 'Asia hours' : h < 13 ? 'Europe hours' : h < 16 ? 'Europe + US hours' : h < 21 ? 'US hours' : 'late US hours');
    var mm = d.getUTCHours()*60 + d.getUTCMinutes(); [0, 480, 960].forEach(function(f){ var dd = Math.min(Math.abs(mm - f), 1440 - Math.abs(mm - f)); if(dd <= 10) tags.push('funding settlement'); });
    if(mm <= 10 || mm >= 1430) tags.push('daily close'); if(w === 0 || w === 6) tags.push('weekend');
    try{ var MC = typeof window !== 'undefined' && window.OMEGA_MARKETCLOCK; if(MC && MC.tags) tags = tags.concat(MC.tags(t)); }catch(e){} return tags; }   /* v6.5.79: CPI, FOMC, options expiry */
  function context(sym, s){ var t = s*1000, m1 = Math.floor(t/M), c = { session:session(t) };
    if(sym !== MKT){ var w = win(sym, m1, 15); c.sNet = w.sNet; c.pNet = w.pNet; c.wNet = w.wNet; c.wN = w.wN; c.liqL = w.liqL; c.liqS = w.liqS; c.imb = w.imb; c.prem = w.prem; c.oi1h = oiChange(sym, 1, t); }
    var b = rings.BTCUSDT; if(b && b.n > 61 && sym !== 'BTCUSDT'){ var a = rowAt(b, b.n - 1), z = rowAt(b, b.n - 61); if(px(a) > 0 && px(z) > 0) c.btc60 = px(a)/px(z) - 1; }
    var mw = win(MKT, m1, 15); c.mktLiqL = mw.liqL; c.mktLiqS = mw.liqS; return c; }
  function heavier(imb){ var a = Math.abs(imb); return a >= 1 ? null : 2*a/(1 - a); }   // (bigger side / smaller side) - 1
  function money(v){ var a = Math.abs(v), s = v < 0 ? '−$' : '$'; return a >= 1e9 ? s + (a/1e9).toFixed(2) + 'B' : a >= 1e6 ? s + (a/1e6).toFixed(1) + 'M' : a >= 1e3 ? s + Math.round(a/1e3) + 'K' : s + Math.round(a); }
  function pc(x, d){ return x == null || !isFinite(x) ? '—' : (x >= 0 ? '+' : '−') + Math.abs(100*x).toFixed(d == null ? 1 : d) + '%'; }
  function read(sym, w, oi){ var out = [], name = sym.replace(/USDT$/, '');
    if(w.chg != null) out.push(name + ' ' + pc(w.chg, 2) + ' in 15 min');
    if(w.sTot + w.pTot > 0){ var lead = Math.abs(w.pNet) > 2*Math.abs(w.sNet) ? 'futures led' : Math.abs(w.sNet) > 2*Math.abs(w.pNet) ? 'spot led' : 'spot and futures together';
      out.push('aggressive net: spot ' + money(w.sNet) + ', futures ' + money(w.pNet) + ' (' + lead + ')'); }
    if(w.wN > 0) out.push(Math.round(w.wN) + ' large order' + (w.wN >= 2 ? 's' : '') + ', net ' + money(w.wNet));
    if(w.liqL + w.liqS > 0) out.push('liquidated: longs ' + money(w.liqL) + ', shorts ' + money(w.liqS) + ' (sampled)');
    if(oi != null) out.push('open interest ' + pc(oi, 1) + ' in the hour' + (oi < -0.01 ? ' (positions closing)' : oi > 0.01 ? ' (new positions)' : ''));
    if(w.imb != null && heavier(w.imb) != null) out.push('visible book: ' + (w.imb >= 0 ? 'bids' : 'asks') + ' ' + Math.round(100*heavier(w.imb)) + '% heavier than ' + (w.imb >= 0 ? 'asks' : 'bids'));
    if(isFinite(w.prem)) out.push('perpetual premium ' + pc(w.prem, 3));
    return out.join('; ') + '.'; }

  // ── slower jobs: thresholds, positioning history, liquidity map ──
  var posMem = {}, jobBusy = false, lastJobs = { thr:0, pos:0, book:0, prune:0 };
  function getJSON(url){ var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null, to = ctl ? setTimeout(function(){ ctl.abort(); }, 20e3) : 0;
    return fetch(url, ctl ? { signal:ctl.signal } : undefined).then(function(r){ clearTimeout(to); return r.json().then(function(j){ if(!r.ok) throw new Error((j && j.msg) || ('HTTP ' + r.status)); return j; }); }); }
  async function refreshThr(){ var c = cfg();
    try{ var sp = await getJSON(SAPI + '/api/v3/ticker/24hr?type=MINI&symbols=' + encodeURIComponent(JSON.stringify(c.coins))); (sp || []).forEach(function(x){ var t = thr[x.symbol] || (thr[x.symbol] = {}); t.s = Math.max(1e4, 2e-4*(+x.quoteVolume || 0)); }); }catch(e){ st.err = 'spot 24-hour volumes: ' + (e.message || e); }
    try{ var fu = await getJSON(FAPI + '/fapi/v1/ticker/24hr'); (fu || []).forEach(function(x){ if(!want[x.symbol]) return; var t = thr[x.symbol] || (thr[x.symbol] = {}); t.p = Math.max(1e4, 2e-4*(+x.quoteVolume || 0)); }); }catch(e){ st.err = 'futures 24-hour volumes: ' + (e.message || e); } }
  var POS_EP = [['oi', '/futures/data/openInterestHist', function(x){ return [+x.timestamp, +x.sumOpenInterest, +x.sumOpenInterestValue]; }],
                ['gls', '/futures/data/globalLongShortAccountRatio', function(x){ return [+x.timestamp, +x.longShortRatio]; }],
                ['tps', '/futures/data/topLongShortPositionRatio', function(x){ return [+x.timestamp, +x.longShortRatio]; }],
                ['tbs', '/futures/data/takerlongshortRatio', function(x){ return [+x.timestamp, +x.buySellRatio, +x.buyVol, +x.sellVol]; }]];
  async function loadPos(sym){ if(posMem[sym]) return posMem[sym]; var r = null; try{ r = store ? await store.get('pos', sym) : null; }catch(e){} posMem[sym] = r || { sym:sym, oi:[], gls:[], tps:[], tbs:[] }; return posMem[sym]; }
  async function collectPos(sym){ var P = await loadPos(sym), added = 0, floor = Date.now() - 29.5*864e5;
    for(var e=0; e<POS_EP.length; e++){ var key = POS_EP[e][0], arr = P[key] || (P[key] = []), last = arr.length ? arr[arr.length - 1][0] : 0, from = Math.max(last + 1, floor);
      for(var page=0; page<20 && running; page++){ var d = await getJSON(FAPI + POS_EP[e][1] + '?symbol=' + sym + '&period=5m&limit=500&startTime=' + from); if(!Array.isArray(d) || !d.length) break;
        d.forEach(function(x){ var row = POS_EP[e][2](x); if(row[0] > (arr.length ? arr[arr.length - 1][0] : 0) && row.every(function(v){ return isFinite(v); })){ arr.push(row); added++; } });
        from = arr.length ? arr[arr.length - 1][0] + 1 : from; if(d.length < 500) break; await sleep(400); }
      var cut = Date.now() - POS_DAYS*864e5; while(arr.length && arr[0][0] < cut) arr.shift(); await sleep(400); }
    if(store) await store.putMany('pos', [P]); return added; }
  function bookSnap(d, t){ var b = (d.bids || []).map(function(x){ return [+x[0], +x[1]]; }), a = (d.asks || []).map(function(x){ return [+x[0], +x[1]]; }); if(!b.length || !a.length) return null;
    var mid = (b[0][0] + a[0][0])/2, out = { t:t, mid:mid }, D = [0.005, 0.01, 0.02, 0.05], nm = ['05', '1', '2', '5'];
    function side(L, sgn, pre){ D.forEach(function(dd, k){ var q = 0; L.forEach(function(x){ if(sgn*(x[0] - mid)/mid <= dd) q += x[0]*x[1]; }); out[pre + nm[k]] = q; });
      out[pre + 'Span'] = Math.abs(L[L.length - 1][0] - mid)/mid;
      var w = L.map(function(x){ return [Math.abs(x[0] - mid)/mid, x[0]*x[1]]; }).sort(function(p, q){ return q[1] - p[1]; }).slice(0, 3);
      for(var i=0; i<3; i++){ out[pre + 'w' + (i + 1) + 'd'] = w[i] ? w[i][0] : NaN; out[pre + 'w' + (i + 1) + 'q'] = w[i] ? w[i][1] : NaN; } }
    side(b, -1, 'b'); side(a, 1, 'a'); return BK.map(function(k){ return out[k]; }); }
  async function collectBook(sym){ var d = await getJSON(SAPI + '/api/v3/depth?symbol=' + sym + '&limit=500'); var t = Date.now(), row = bookSnap(d, t); if(!row) return 0;
    var k = sym + '|' + pad(Math.floor(t/864e5)), rec = null; try{ rec = store ? await store.get('book', k) : null; }catch(e){} rec = rec || { k:k, sym:sym, day:Math.floor(t/864e5), snaps:[] }; rec.snaps.push(row); bookMem[sym] = row;
    if(store) await store.putMany('book', [rec]); return 1; }
  var bookMem = {};
  async function jobs(){ if(jobBusy || !running) return; jobBusy = true; var c = cfg(), t = Date.now();
    try{
      if(t - lastJobs.thr > H){ lastJobs.thr = t; await refreshThr(); }
      if(t - lastJobs.pos > 15*M){ lastJobs.pos = t; var ok = 0, bad = 0, err = null; for(var i=0; i<c.coins.length && running; i++){ try{ await collectPos(c.coins[i]); ok++; }catch(e){ bad++; err = err || (e.message || String(e)); } } st.pos = { at:Date.now(), ok:ok, bad:bad, err:err }; }
      if(c.bookEvery > 0 && t - lastJobs.book > c.bookEvery*M){ lastJobs.book = t; var ok2 = 0, bad2 = 0, err2 = null; for(var j=0; j<c.coins.length && running; j++){ try{ ok2 += await collectBook(c.coins[j]); }catch(e){ bad2++; err2 = err2 || (e.message || String(e)); } await sleep(300); } st.book = { at:Date.now(), ok:ok2, bad:bad2, err:err2 }; }
    } finally { jobBusy = false; } maybeRender(); }

  // ── every minute: save minute blocks and open recordings; drop old data ──
  function persist(){ if(!store) return Promise.resolve(); var recs = Object.keys(dirty).map(function(k){ return blocks[k]; }).filter(Boolean); dirty = {};
    return store.putMany('min', recs).catch(function(e){ st.err = 'saving minutes: ' + (e && e.message || e); }); }
  function minuteJobs(){ var nh = Math.floor(now()/H); persist().then(function(){ Object.keys(blocks).forEach(function(k){ if(blocks[k].h < nh - MEM_H && !dirty[k]) delete blocks[k]; }); });
    Object.keys(open).forEach(function(s){ saveEvent(open[s]); }); jobs();
    if(Date.now() - lastJobs.prune > H && store){ lastJobs.prune = Date.now(); store.keys('min').then(function(ks){ var cut = nh - KEEP_H; return store.del('min', ks.filter(function(k){ return +k.split('|')[1] < cut; })); }).catch(function(){}); } }
  function boot(){ if(!store) return Promise.resolve(); var nh = Math.floor(Date.now()/H), c = cfg(), syms = c.coins.concat([MKT]);
    return Promise.all(syms.map(function(s){ return store.range('min', bkey(s, nh - MEM_H), bkey(s, nh + 1)).then(function(rs){ rs.forEach(function(r){ if(!blocks[r.k]) blocks[r.k] = { k:r.k, sym:r.sym, h:r.h, a:r.a instanceof Float32Array ? r.a : new Float32Array(r.a) }; }); }); }))
      .then(function(){ return store.all('events'); }).then(function(evs){ evs.sort(function(a, b){ return b.t - a.t; }); st.events = evs.slice(0, EV_MAX).map(function(e){ if(!e.done){ e.interrupted = true; } return { id:e.id, sym:e.sym, kind:e.kind, t:e.t, x:e.x, z:e.z, ctx:e.ctx, after:e.after || null, done:e.done, nPost:e.nPost, interrupted:!!e.interrupted }; }); })
      .then(function(){ return Promise.all(c.coins.map(function(s){ return loadPos(s); })); }).catch(function(e){ st.err = 'loading: ' + (e && e.message || e); }); }

  // ── screen awake while recording (phones pause pages in the background) ──
  var lock = null;
  function wake(){ var c = cfg(); if(!running || !c.awake || lock || typeof navigator === 'undefined' || !navigator.wakeLock || (typeof document !== 'undefined' && document.hidden)) return;
    navigator.wakeLock.request('screen').then(function(l){ lock = l; st.awake = true; l.addEventListener('release', function(){ lock = null; st.awake = false; }); }).catch(function(e){ st.awake = false; st.wakeErr = e && e.message || String(e); }); }
  function release(){ if(lock){ try{ lock.release(); }catch(e){} lock = null; } }
  if(typeof document !== 'undefined' && document.addEventListener) document.addEventListener('visibilitychange', function(){ if(document.hidden){ st.hiddenAt = Date.now(); persist(); return; } if(running){ wake(); Object.keys(socks).forEach(function(k){ if(!socks[k].ws) connect(socks[k]); }); } });

  // ── export for research (format omega-watch v1; prices and flows only, no keys) ──
  function b64(u8){ var s = '', CH = 0x8000; for(var i=0; i<u8.length; i += CH) s += String.fromCharCode.apply(null, u8.subarray(i, i + CH)); return btoa(s); }
  function f32b64(a){ var f = a instanceof Float32Array ? a : new Float32Array(a); return b64(new Uint8Array(f.buffer, f.byteOffset, f.byteLength)); }
  async function build(days){ await persist(); var c = cfg(), nh = Math.floor(Date.now()/H), h0 = nh - days*24, out = { format:'omega-watch', v:1, made:new Date().toISOString(), fromH:h0, toH:nh, fields:F, mfields:MF, bfields:B, kfields:BK, mode:c.mode, coins:{}, market:[], pos:{}, book:{}, events:[],
      notes:'Minute rows per coin: Float32 little-endian, 60 x fields per hour (NaN = no data). Liquidations are Binance’s live sample (at most one per coin per second). Large order = one taker order >= max(10,000, 0.02% of 24h quote volume) USDT. Event rows: t in seconds from the trigger.' };
    for(var i=0; i<c.coins.length; i++){ var s = c.coins[i], rs = await store.range('min', bkey(s, h0), bkey(s, nh)); out.coins[s] = rs.map(function(r){ return [r.h, f32b64(r.a)]; });
      var P = await loadPos(s); out.pos[s] = { oi:P.oi.filter(function(x){ return x[0] >= h0*H; }), gls:P.gls.filter(function(x){ return x[0] >= h0*H; }), tps:P.tps.filter(function(x){ return x[0] >= h0*H; }), tbs:P.tbs.filter(function(x){ return x[0] >= h0*H; }) };
      var bk = await store.range('book', s + '|' + pad(Math.floor(h0/24)), s + '|' + pad(Math.floor(nh/24))); out.book[s] = [].concat.apply([], bk.map(function(r){ return r.snaps; })).filter(function(x){ return x[0] >= h0*H; }); }
    out.market = (await store.range('min', bkey(MKT, h0), bkey(MKT, nh))).map(function(r){ return [r.h, f32b64(r.a)]; });
    var evs = await store.all('events'); out.events = evs.filter(function(e){ return e.t >= h0*H; }).map(function(e){ return { id:e.id, sym:e.sym, kind:e.kind, t:e.t, x:e.x, z:e.z, sigma:e.sigma, ctx:e.ctx, after:e.after, done:e.done, nPre:e.nPre, nPost:e.nPost, pre:f32b64(e.pre), post:f32b64(e.post) }; });
    return out; }
  var kept = [];
  async function exportData(days){ var out = await build(days), txt = JSON.stringify(out);
    if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
    var name = 'omega-watch-' + new Date(out.fromH*H).toISOString().slice(0, 10) + '-to-' + new Date(out.toH*H).toISOString().slice(0, 10), blob;
    if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    var mb = Math.round(blob.size/1048576*10)/10; kept = kept.filter(function(k){ return k.name !== name; }); kept.push({ name:name, url:url, mb:mb }); return { name:name, mb:mb }; }

  // ── the page ──
  var lastRender = 0, ui = { busy:null, msg:'' };
  function maybeRender(force){ var p = el('page-watch'); if(!p) return; if(!force && !p.classList.contains('active')) return; if(!force && Date.now() - lastRender < 4500) return; render(); }
  function coverage(sym){ var m1 = Math.floor(now()/M), n = 0; for(var m = m1 - 1440; m < m1; m++){ var v = get(sym, m, 'sC'); if(!(v > 0)) v = get(sym, m, 'pC'); if(v > 0) n++; } return n/1440; }
  var STATE = { off:['off', 'dim'], connecting:['connecting', 'warn'], open:['connected, waiting for data', 'warn'], live:['live', 'bull'], retrying:['reconnecting', 'warn'], error:['blocked', 'bear'], silent:['connected but no data', 'bear'], unsupported:['not supported here', 'bear'] };
  function pill(name, S){ var s = STATE[S ? S.state : 'off'] || [S.state, 'warn']; return '<span class="bt-lab ' + s[1] + '" style="margin:0 6px 6px 0;display:inline-block;">' + esc(name) + ': ' + esc(s[0]) + (S && S.n ? ' · ' + S.n.toLocaleString() + ' msgs' : '') + '</span>'; }
  function tm(t){ var d = new Date(t); return d.toISOString().slice(5, 16).replace('T', ' ') + ' UTC (' + d.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' }) + ' your time)'; }
  function render(){ var host = el('watchBody'); if(!host) return; lastRender = Date.now(); var c = cfg(), h = '';
    h += '<div class="card" style="margin-bottom:14px;"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;"><div><h2 style="color:var(--gold);margin-bottom:4px;">Market recorder — every public footprint of big buying and selling</h2>' +
      '<span class="bt-lab ' + (running ? 'bull' : 'warn') + '">' + (running ? 'Recording since ' + esc(new Date(st.since).toLocaleTimeString()) : (c.on ? 'Paused' : 'Off')) + '</span></div>' +
      '<button class="btn-outline" type="button" id="watchToggle">' + (running ? 'Stop recording' : 'Start recording') + '</button></div>' +
      '<p class="hint" style="margin-top:8px;">For each watched coin it records who is buying and who is selling, minute by minute, on spot and on the perpetual. That means every aggressive order, every large single order, the visible order book, the perpetual’s premium and funding, and liquidations. It also records US buyers’ price on Coinbase, and open interest and long/short ratios every 5 minutes. A sudden move opens a <b>flight recording</b>: the 30 minutes before and the hour after, second by second. <b>This is description, not a signal.</b> Round 16 tests what it finds before anything trades on it.</p>';
    if(running || Object.keys(socks).length){ h += '<div style="margin:6px 0;">' + pill('Spot trades + book', socks.spot) + pill('Futures trades, premium, liquidations', socks.futures) + pill('Coinbase', socks.coinbase) + '</div>';
      h += '<p class="hint" style="margin-top:0;">' + st.rate.mps.toFixed(0) + ' messages a second, ' + st.rate.kbps.toFixed(0) + ' KB/s (' + (st.dayBytes/1048576).toFixed(0) + ' MB today). Positioning history: ' + (st.pos.at ? st.pos.ok + ' coins updated ' + esc(new Date(st.pos.at).toLocaleTimeString()) + (st.pos.bad ? ', ' + st.pos.bad + ' failed (' + esc(st.pos.err) + ')' : '') : 'first fill running (about 12 minutes)') +
        '. Liquidity map: ' + (c.bookEvery > 0 ? (st.book.at ? st.book.ok + ' coins at ' + esc(new Date(st.book.at).toLocaleTimeString()) + (st.book.bad ? ', ' + st.book.bad + ' failed' : '') : 'first map soon') : 'off') +
        (st.awake ? '. Screen kept on.' : st.wakeErr ? '. Could not keep the screen on (' + esc(st.wakeErr) + ').' : '.') + (st.err ? ' <span style="color:var(--amber);">Last problem: ' + esc(st.err) + '.</span>' : '') + '</p>'; }
    var cov = coverage(c.coins[0] || 'BTCUSDT');
    h += '<p class="hint">Recorded ' + (cov*24 >= 1 ? (cov*24).toFixed(1) + ' hours' : Math.round(cov*1440) + ' minute' + (Math.round(cov*1440) === 1 ? '' : 's')) + ' of the last 24 hours ('  + esc((c.coins[0] || '').replace(/USDT$/, '')) + '). <b>It records only while OMEGA is open and on screen.</b> Phones pause pages in the background, and those minutes stay empty. They are never filled in. For 24/7, leave it open on a computer that doesn’t sleep. Open interest and long/short history fill back 30 days by themselves. Full mode can use a few GB a day on busy days, so Wi-Fi is best. Light mode uses far less, but has no large-order detail.</p>';
    h += '<details style="margin:6px 0 4px;"><summary class="hint" style="cursor:pointer;"><b>Settings</b> (' + c.coins.length + ' coins, ' + (c.mode === 'light' ? 'light' : 'full') + ' mode)</summary><div class="hint" style="margin-top:6px;line-height:2;">' +
      'Mode <select id="watchMode"><option value="full"' + (c.mode !== 'light' ? ' selected' : '') + '>Full: every trade</option><option value="light"' + (c.mode === 'light' ? ' selected' : '') + '>Light: 1-minute totals</option></select> · ' +
      'Liquidity map <select id="watchBook">' + [[0, 'off'], [5, 'every 5 min'], [15, 'every 15 min'], [60, 'every hour']].map(function(o){ return '<option value="' + o[0] + '"' + (+c.bookEvery === o[0] ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') + '</select> · ' +
      '<label><input type="checkbox" id="watchAwake"' + (c.awake ? ' checked' : '') + '> keep the screen on while recording</label><br>' +
      'Coins (up to 60, comma separated): <input id="watchCoins" style="width:100%;" value="' + esc(c.coins.join(', ')) + '"> <button class="btn-outline" type="button" id="watchSave">Save settings</button>' +
      (running ? ' <span class="dim">(saved settings apply when recording restarts)</span>' : '') + '</div></details>';
    h += '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:6px;"><span class="hint">Export for research:</span>' + [1, 3, 7].map(function(d){ return '<button class="btn-outline" type="button" data-watchexp="' + d + '"' + (ui.busy ? ' disabled' : '') + '>' + d + ' day' + (d > 1 ? 's' : '') + '</button>'; }).join('') + '<span class="hint" id="watchExpMsg">' + esc(ui.msg) + '</span></div>' +
      (kept.length ? '<p class="hint">Not in your Downloads? Tap to save again: ' + kept.map(function(x){ return '<a href="' + x.url + '" download="' + esc(x.name) + '">' + esc(x.name) + '</a> (' + x.mb + ' MB)'; }).join(' · ') + '</p>' : '') + '</div>';
    // what's moving now
    var m1 = Math.floor(now()/M) - 1, rows = c.coins.map(function(s){ return { s:s, w:win(s, m1, 15), oi:oiChange(s, 1) }; }).filter(function(r){ return r.w.mins > 0; });
    rows.sort(function(a, b){ return Math.abs(b.w.chg || 0) - Math.abs(a.w.chg || 0); });
    var mw = win(MKT, m1, 15), mw60 = win(MKT, m1, 60), cbB = NaN, bnB = NaN, cbU = NaN; for(var m = m1; m > m1 - 10; m--){ if(nan(cbB)) cbB = get(MKT, m, 'cbBTC'); if(nan(bnB)) bnB = get(MKT, m, 'bnBTC'); if(nan(cbU)) cbU = get(MKT, m, 'cbUSDT'); }
    var cbPrem = cbB > 0 && bnB > 0 ? cbB/(bnB*(cbU > 0 ? cbU : 1)) - 1 : null;
    h += '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">What’s moving it now (last 15 minutes)</h2>';
    if(!rows.length) h += '<p class="hint" style="margin-top:0;">Nothing recorded in the last 15 minutes. ' + (running ? 'Waiting for the first minutes.' : 'Start recording to see it.') + '</p>';
    else { h += '<p class="hint" style="margin-top:0;">Market: liquidations ' + money(mw.liqL) + ' of longs and ' + money(mw.liqS) + ' of shorts in 15 minutes (' + money(mw60.liqL + mw60.liqS) + ' in the hour, sampled). Coinbase BTC premium ' + (cbPrem == null ? '—' : pc(cbPrem, 3)) + ' (US buyers paying more when positive).</p>';
      h += rows.slice(0, 3).map(function(r){ return '<p class="hint" style="margin:4px 0;">▸ ' + esc(read(r.s, r.w, r.oi)) + '</p>'; }).join('');
      h += '<div style="overflow-x:auto;"><table class="creed-events"><thead><tr><th>Coin</th><th>15 min</th><th>Spot net</th><th>Futures net</th><th>Large orders</th><th>Liquidated L / S</th><th>Book</th><th>Premium</th><th>OI 1h</th></tr></thead><tbody>' +
        rows.map(function(r){ var w = r.w; return '<tr><td>' + esc(r.s.replace(/USDT$/, '')) + '</td><td class="mono">' + pc(w.chg, 2) + '</td><td class="mono">' + money(w.sNet) + '</td><td class="mono">' + money(w.pNet) + '</td><td class="mono">' + (w.wN ? Math.round(w.wN) + ' · ' + money(w.wNet) : '—') + '</td><td class="mono">' + (w.liqL + w.liqS ? money(w.liqL) + ' / ' + money(w.liqS) : '—') + '</td><td class="mono">' + (w.imb == null || heavier(w.imb) == null ? '—' : (w.imb >= 0 ? 'bids +' : 'asks +') + Math.round(100*heavier(w.imb)) + '%') + '</td><td class="mono">' + pc(w.prem, 3) + '</td><td class="mono">' + pc(r.oi, 1) + '</td></tr>'; }).join('') + '</tbody></table></div>'; }
    h += '<p class="hint">Net = aggressive buying minus aggressive selling, in USDT. A large order is one taker order of at least 0.02% of the coin’s daily volume. Book = how much heavier the visible top 20 levels are on one side.</p></div>';
    // flight recordings
    h += '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">Flight recordings (' + st.events.length + ')</h2>';
    if(!st.events.length) h += '<p class="hint" style="margin-top:0;">None yet. A recording opens when a coin moves 4+ of its own 1-minute standard deviations in 60 seconds, or when 10M USDT is liquidated across the market in 60 seconds. A coin needs 6 hours of recorded minutes before its moves can be measured.</p>';
    else h += st.events.slice(0, 30).map(function(e){ var c0 = e.ctx || {}, a = e.after || {}, nm = e.sym === MKT ? 'Market' : e.sym.replace(/USDT$/, '');
      var head = e.kind === 'liq' ? 'Liquidation burst: ' + money(e.x) + ' in 60 s' : nm + ' ' + pc(Math.exp(e.x) - 1, 2) + ' in 60 s (' + (e.z == null ? '' : Math.abs(e.z).toFixed(1) + 'σ') + ')';
      var lead = [], nx = [];
      if(c0.sNet != null && e.sym !== MKT) lead.push('15 min before: spot ' + money(c0.sNet) + ', futures ' + money(c0.pNet) + (c0.wN ? ', ' + Math.round(c0.wN) + ' large orders net ' + money(c0.wNet) : '') + (c0.liqL + c0.liqS ? ', liquidated L ' + money(c0.liqL) + ' / S ' + money(c0.liqS) : '') + (c0.oi1h != null ? ', OI 1h ' + pc(c0.oi1h, 1) : ''));
      if(c0.btc60 != null) lead.push('BTC in the same minute ' + pc(c0.btc60, 2) + (Math.abs(c0.btc60) < 0.002 ? ' (this coin alone)' : ' (market-wide)'));
      if(a.r5 != null) nx.push('5 min ' + pc(a.r5, 2)); if(a.r15 != null) nx.push('15 min ' + pc(a.r15, 2)); if(a.r60 != null) nx.push('60 min ' + pc(a.r60, 2)); if(a.maxUp != null && a.n) nx.push('range ' + pc(a.maxDn, 1) + ' to ' + pc(a.maxUp, 1));
      return '<p class="hint" style="margin:6px 0;border-top:1px solid var(--border);padding-top:6px;"><b>' + esc(head) + '</b> · ' + esc(tm(e.t)) + ' · ' + esc((c0.session || []).join(', ')) + '<br>' + esc(lead.join('; ')) + (lead.length ? '<br>' : '') +
        (nx.length ? 'Then: ' + esc(nx.join(', ')) : (e.interrupted ? 'Interrupted (the app was closed during the hour after).' : 'Recording the hour after…')) + '</p>'; }).join('');
    h += '</div>';
    h += '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">What it cannot see</h2><ul class="hint" style="margin:0;padding-left:18px;line-height:1.6;">' +
      '<li>Order books before today. Binance publishes no free history of them, so this record starts now.</li><li>Hidden orders. Icebergs show only as selling that hits a level without moving it.</li>' +
      '<li>Every liquidation. Binance’s live feed sends at most one per coin per second, so big cascades are undercounted.</li><li>Other exchanges (apart from Coinbase’s BTC and ETH price), over-the-counter deals and on-chain transfers.</li>' +
      '<li>Why a move happened. It shows who pushed and how hard. News is not in it.</li></ul></div>';
    host.innerHTML = h; wireUI(); }
  function wireUI(){ var b = el('watchToggle'); if(b) b.onclick = function(){ var c = cfg(); if(running){ c.on = false; setCfg(c); stop(); } else { c.on = true; setCfg(c); boot().then(start); } };
    var sv = el('watchSave'); if(sv) sv.onclick = function(){ var c = cfg(), list = String((el('watchCoins') || {}).value || '').toUpperCase().split(/[\s,]+/).filter(function(s){ return /^[A-Z0-9]{2,20}USDT$/.test(s); });
      var seen = {}; list = list.filter(function(s){ if(seen[s]) return false; seen[s] = 1; return true; }).slice(0, 60); if(list.length) c.coins = list;
      c.mode = (el('watchMode') || {}).value === 'light' ? 'light' : 'full'; c.bookEvery = +((el('watchBook') || {}).value || 0); c.awake = !!(el('watchAwake') || {}).checked; setCfg(c);
      if(running){ stop().then(function(){ return boot(); }).then(start); } else render(); };
    Array.prototype.forEach.call(document.querySelectorAll('[data-watchexp]'), function(x){ x.onclick = function(){ var d = +x.getAttribute('data-watchexp'); ui.busy = true; ui.msg = 'Building the file…'; render();
      exportData(d).then(function(r){ ui.msg = 'Saved ' + r.name + ' (' + r.mb + ' MB).'; }).catch(function(e){ ui.msg = 'Could not export: ' + (e && e.message || e); }).then(function(){ ui.busy = null; render(); }); }; }); }
  function report(){ var c = cfg(); return { on:running, mode:c.mode, coins:c.coins.length, since:st.since ? new Date(st.since).toISOString() : null, coverage24h:Math.round(coverage(c.coins[0] || 'BTCUSDT')*1000)/1000, recordings:st.events.length,
      feeds:{ spot:socks.spot ? socks.spot.state : 'off', futures:socks.futures ? socks.futures.state : 'off', coinbase:socks.coinbase ? socks.coinbase.state : 'off' } }; }
  window.OMEGA_WATCH = { start:function(){ return boot().then(start); }, stop:stop, cfg:cfg, setCfg:setCfg, report:report, render:render, exportData:exportData, build:build, running:function(){ return running; }, FIELDS:F, MFIELDS:MF, BFIELDS:B, KFIELDS:BK, COINS:COINS0, URLS:{ spot:URL_SPOT, futures:URL_FMKT, coinbase:URL_CB },
    _:{ watchdog:watchdog, onSpot:onSpot, onFut:onFut, onCB:onCB, second:second, get:get, win:win, read:read, sigma:sigma, open:open, rings:rings, blocks:blocks, st:st, socks:socks, threshold:threshold, thr:thr, bookSnap:bookSnap, session:session, outcome:outcome, rowsOf:rowsOf, f32rows:f32rows, flushOrders:flushOrders, minuteJobs:minuteJobs, persist:persist, posMem:posMem, oiChange:oiChange,
      setStore:function(s){ store = s; }, setWant:function(list){ want = {}; list.forEach(function(s){ want[s] = 1; }); }, setRunning:function(v){ running = v; }, setSkew:function(v){ skew = v; }, reset:function(){ [blocks, dirty, av, secs, rings, open, lastEv, pend, kl, sigC, posMem].forEach(function(o){ Object.keys(o).forEach(function(k){ delete o[k]; }); }); lastSec = 0; liqWin = []; st.events = []; }, collectPos:collectPos, collectBook:collectBook, jobs:jobs, lastJobs:lastJobs } };
  // start on load if it was left on; the page wires itself when it exists
  var tries = 0, iv = setInterval(function(){ if(el('watchBody')){ clearInterval(iv); render(); boot().then(function(){ if(cfg().on && !running) start(); else render(); }); } else if(++tries > 60) clearInterval(iv); }, 1000);   /* shows what is stored even when off */
})();
</script>
