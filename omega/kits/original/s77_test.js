// v6.5.77 checks: Market Watch, the recorder. Minute aggregation of trades, large orders, book, premium, liquidations
// and Coinbase; the second-by-second buffer; flight recordings (trigger, no false trigger on a throttled tab, outcome);
// light mode; the liquidity map; the export round trip (decoded by research/watch16.py); the streams and their
// addresses (Binance's 2026 futures split); the page; the positioning collector's liquidation address.
const fs = require('fs'), path = require('path'), cp = require('child_process'), D0 = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D0, 'omega-v6_5-77.html'), 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
const ls = {}; let NOW = Date.UTC(2026, 9, 17, 8, 2, 0);   // a Saturday, 08:02 UTC
const RealDate = Date; global.Date = class extends RealDate { constructor(...a){ super(...(a.length ? a : [NOW])); } static now(){ return NOW; } };
global.window = {}; global.document = { getElementById:() => null, hidden:false }; global.localStorage = { getItem:k => ls[k] || null, setItem:(k, v) => { ls[k] = String(v); } };
global.setInterval = () => 0; global.clearInterval = () => {}; global.setTimeout = () => 0; global.clearTimeout = () => {};
const opened = []; global.WebSocket = class { constructor(u){ this.url = u; this.sent = []; opened.push(this); } send(x){ this.sent.push(x); } close(){ if(this.onclose) this.onclose({ code:1000 }); } };
global.btoa = s => Buffer.from(s, 'binary').toString('base64');
// in-memory store with the same interface as the IndexedDB one (string keys, ordered ranges)
const mem = { min:new Map(), pos:new Map(), book:new Map(), events:new Map() }, KP = { min:'k', pos:'sym', book:'k', events:'id' };
const memStore = { putMany:(n, rs) => { rs.forEach(r => mem[n].set(r[KP[n]], r)); return Promise.resolve(); }, get:(n, k) => Promise.resolve(mem[n].get(k)),
  range:(n, lo, hi) => Promise.resolve([...mem[n].keys()].filter(k => k >= lo && k <= hi).sort().map(k => mem[n].get(k))), keys:n => Promise.resolve([...mem[n].keys()]),
  del:(n, ks) => { ks.forEach(k => mem[n].delete(k)); return Promise.resolve(); }, all:n => Promise.resolve([...mem[n].values()]) };
new Function(grab('MARKET WATCH'))(); const W = window.OMEGA_WATCH, X = W._;
X.setStore(memStore); X.setWant(['BTCUSDT', 'ETHUSDT', 'SOLUSDT']); X.setRunning(true); X.setSkew(0);
const F = W.FIELDS, MF = W.MFIELDS, B = W.BFIELDS, M = 60e3;
const sp = (d, stream) => X.onSpot({ stream:stream || (d.s.toLowerCase() + '@aggTrade'), data:d }), fu = d => X.onFut({ stream:'x', data:d });
const trade = (s, p, q, T, sell, mk) => (mk === 'p' ? fu : sp)({ e:'aggTrade', s, p:String(p), q:String(q), T, m:sell });
(async () => {
  // 1. spot trades in one minute: totals, close/high/low, one taker order split over two trades, the large-order rule
  const m0 = Math.floor(NOW/M) + 1, T0 = m0*M + 1000; X.thr.BTCUSDT = { s:50000, p:80000 }; NOW = T0 + 5500;
  trade('BTCUSDT', 60000, 0.5, T0, false);            // 30,000 buy } one taker order of 60,000 (same time, same side)
  trade('BTCUSDT', 60010, 0.49983, T0, false);         // 29,995 buy }
  trade('BTCUSDT', 60020, 0.6664, T0 + 500, false);    // 39,997 buy: below 50,000, not large
  trade('BTCUSDT', 59990, 1, T0 + 900, true);          // 59,990 sell: large
  trade('BTCUSDT', 59980, 0.1, T0 + 5000, true);       // 5,998 sell
  X.flushOrders(m0*M + 60e3);
  const g = f => X.get('BTCUSDT', m0, f);
  ok(Math.abs(g('sBuy') - (30000 + 29994.8983 + 39996.928)) < 2 && Math.abs(g('sSell') - (59990 + 5998)) < 1 && g('sN') === 5 && g('sC') === 59980 && g('sH') === 60020 && g('sL') === 59980,
    'spot trades add up per minute: aggressive buying and selling in USDT, trade count, last, high and low', F.map((f, i) => [f, g(f)]).slice(0, 11));
  ok(g('sWN') === 2 && Math.abs(g('sWBuy') - 59994.9) < 2 && Math.abs(g('sWSell') - 59990) < 1 && Math.abs(g('sMaxB') - 59994.9) < 2 && Math.abs(g('sMaxS') - 59990) < 1,
    'one taker order filled at two prices counts as one order; large orders = at least the coin’s threshold (2 here: a 60K buy and a 60K sell)', [g('sWN'), g('sWBuy'), g('sWSell'), g('sMaxB')]);
  // 2. the perpetual: trades, mark price, premium (averaged over the minute), funding
  trade('BTCUSDT', 60030, 2, T0 + 100, true, 'p'); trade('BTCUSDT', 60040, 1, T0 + 200, false, 'p');
  fu({ e:'markPriceUpdate', E:T0 + 1000, s:'BTCUSDT', p:'60060', i:'60000', r:'0.0001' }); fu({ e:'markPriceUpdate', E:T0 + 2000, s:'BTCUSDT', p:'60030', i:'60000', r:'0.0001' });
  ok(Math.abs(g('pSell') - 120060) < 1 && Math.abs(g('pBuy') - 60040) < 1 && g('pC') === 60040 && Math.abs(g('prem') - 0.00075) < 1e-7 && g('mark') === 60030 && g('idx') === 60000 && Math.abs(g('fr') - 0.0001) < 1e-9,
    'perpetual: aggressive flows, last trade, mark and index, premium averaged over the minute (0.075%), funding rate', [g('pSell'), g('pBuy'), g('prem'), g('fr')]);
  // 3. the visible book: bids against asks, spread (stream name gives the coin)
  NOW = T0 + 3000; sp({ lastUpdateId:1, bids:[['59990', '3'], ['59980', '1']], asks:[['60000', '1'], ['60010', '1']] }, 'btcusdt@depth20');
  const bq = 59990*3 + 59980, aq = 60000 + 60010;
  ok(Math.abs(g('sImb') - (bq - aq)/(bq + aq)) < 1e-6 && Math.abs(g('sBidQ') - bq) < 1 && Math.abs(g('sSprd') - 10/59995*1e4) < 1e-3, 'order book: top-20 bids against asks (imbalance), sizes in USDT, spread in basis points');
  // 4. liquidations: a SELL force order closes a long; every coin counts for the market, watched coins also on their own row
  fu({ e:'forceOrder', E:T0 + 4000, o:{ s:'BTCUSDT', S:'SELL', q:'2', p:'59000', ap:'59500', z:'2', T:T0 + 4000 } });
  fu({ e:'forceOrder', E:T0 + 4100, o:{ s:'PEPEUSDT', S:'BUY', q:'1000000', p:'0.00001', ap:'0.00001', z:'1000000', T:T0 + 4100 } });
  const mk = f => X.get('_MKT', m0, f);
  ok(g('liqL') === 119000 && Number.isNaN(g('liqS')) && mk('liqL') === 119000 && Math.abs(mk('liqS') - 10) < 1e-6 && mk('liqN') === 2, 'liquidations: longs closed on BTC on its own row; the market row counts every coin (PEPE short liquidated)');
  // 5. Coinbase (US spot buyers)
  X.onCB({ type:'ticker', product_id:'BTC-USD', price:'60100.5', time:new Date(T0 + 4500).toISOString() }); X.onCB({ type:'ticker', product_id:'USDT-USD', price:'1.0001', time:new Date(T0 + 4500).toISOString() });
  ok(mk('cbBTC') === Math.fround(60100.5) && mk('cbUSDT') === Math.fround(1.0001) && mk('bnBTC') === 59980, 'Coinbase BTC-USD and USDT-USD are kept beside Binance BTC, for the Coinbase premium');
  // 6. the second-by-second buffer: flows per second, prices carried forward
  NOW = T0 + 6000; X.setSkew(0); X.second(); const r1 = X.rings.BTCUSDT; const row = i => Array.from(r1.a.slice(((r1.n - 1 - i) % 1800)*B.length, ((r1.n - 1 - i) % 1800 + 1)*B.length));
  const a1 = row(0); ok(r1.n === 1 && a1[0] === Math.floor((T0 + 5000)/1000) && a1[1] === 59980 && a1[4] === 60040 && a1[7] === 119000 && Math.abs(a1[10] - 0.0005) < 1e-9, 'a row per second: price, flows since the last row, liquidations, book and premium', a1);
  NOW += 1000; X.second(); const a2 = row(0); ok(a2[1] === 59980 && a2[2] === 0 && a2[3] === 0 && a2[7] === 0, 'flows reset each second; prices carry forward');
  // 7. flight recording: build 7 hours of 1-minute closes on SOL (a quiet coin), then a sudden fall
  X.setWant(['BTCUSDT', 'ETHUSDT', 'SOLUSDT']); let p = 150, t = NOW - 7*3600e3; const rnd = (() => { let z = 7; return () => (z = (z*48271) % 2147483647)/2147483647; })();
  for(let k=0; k<420; k++){ p *= 1 + (rnd() - 0.5)*0.002; trade('SOLUSDT', p.toFixed(4), 1, t + k*M + 30e3, rnd() < 0.5); }   // old timestamps: ignored by the clock
  const sg = X.sigma('SOLUSDT'); ok(sg > 0.0003 && sg < 0.0009, 'a coin’s 1-minute standard deviation comes from its recorded minutes (' + (sg*100).toFixed(3) + '%)');
  // throttled tab: rows 30 s apart, with a big move between them, must not trigger
  for(let k=0; k<70; k++){ NOW += 30e3; trade('SOLUSDT', p.toFixed(4), 0.1, NOW - 500, false); X.second(); }
  trade('SOLUSDT', (p*0.97).toFixed(4), 0.1, NOW + 500, true); NOW += 30e3; X.second();
  ok(!X.open.SOLUSDT, 'no recording when the row 60 s back is not really 60 s back (a phone throttling a background page)');
  p *= 0.97; for(let k=0; k<90; k++){ NOW += 1000; trade('SOLUSDT', p.toFixed(4), 0.2, NOW - 400, k % 2 === 0); X.second(); }
  for(let k=0; k<5; k++){ NOW += 1000; p *= 0.996; trade('SOLUSDT', p.toFixed(4), 50, NOW - 300, true, 'p'); trade('SOLUSDT', p.toFixed(4), 5, NOW - 300, true); X.second(); }
  for(let k=0; k<55; k++){ NOW += 1000; trade('SOLUSDT', p.toFixed(4), 0.2, NOW - 300, false); X.second(); if(X.open.SOLUSDT) break; }
  const ev = X.open.SOLUSDT; X.setSkew(0); ok(ev && ev.kind === 'move' && ev.x < 0 && Math.abs(ev.z) >= 4 && ev.pre.length > 60 && ev.ctx && ev.ctx.session.length, 'a sudden fall (' + (ev ? (100*(Math.exp(ev.x) - 1)).toFixed(2) + '%, ' + Math.abs(ev.z).toFixed(1) + 'σ' : '') + ') opens a flight recording with the minutes before and what was going on', ev && { x:ev.x, z:ev.z, ctx:ev.ctx });
  const off = ev.post.length, pre0 = ev.pre[ev.pre.length - 1], pTrig = pre0[1] > 0 ? pre0[1] : pre0[4]; const priceAt = j => j < 299 ? pTrig : j < 899 ? pTrig*1.01 : j < 2000 ? pTrig*1.02 : j < 3500 ? pTrig*0.98 : pTrig*1.005;
  for(let k=0; k<4000 && X.open.SOLUSDT; k++){ NOW += 1000; trade('SOLUSDT', priceAt(off + k), 0.1, NOW - 300, false); X.setSkew(0); X.second(); }
  await new Promise(r => setImmediate(r));
  const done = mem.events.get(ev.id);
  ok(!X.open.SOLUSDT && done && done.done && Math.abs(done.after.r5 - 0.01) < 2e-4 && Math.abs(done.after.r15 - 0.02) < 2e-4 && Math.abs(done.after.r60 - 0.005) < 2e-4 && Math.abs(done.after.maxDn + 0.02) < 2e-4,
    'the recording closes after an hour with what happened next: +1% at 5 min, +2% at 15 min, +0.5% at 60 min, low −2%', done && done.after);
  const back = X.rowsOf(done.post, done.nPost, done.t/1000); ok(done.post instanceof Float32Array && done.nPost === 3600 && back[0][0] === done.t/1000 + 1 && Math.abs(back[3599][1] - pTrig*1.005) < 1e-3*pTrig, 'it is stored compactly (Float32, seconds from the trigger) and reads back exactly');
  // 8. light mode: 1-minute candles with taker-buy totals; flows per second from the change in the running totals
  const mL = m0 + 2000, tL = mL*M; sp({ e:'kline', E:tL + 2000, s:'ETHUSDT', k:{ t:tL, s:'ETHUSDT', o:'3000', c:'3001', h:'3002', l:'2999', q:'100000', Q:'60000', n:40, x:false } }, 'ethusdt@kline_1m');
  NOW = tL + 3000; X.setSkew(0); X.second(); sp({ e:'kline', E:tL + 4000, s:'ETHUSDT', k:{ t:tL, s:'ETHUSDT', o:'3000', c:'3003', h:'3004', l:'2999', q:'130000', Q:'70000', n:55, x:false } }, 'ethusdt@kline_1m');
  NOW = tL + 5000; X.setSkew(0); X.second(); const re = X.rings.ETHUSDT, rr = Array.from(re.a.slice(((re.n - 1) % 1800)*B.length, ((re.n - 1) % 1800 + 1)*B.length));
  ok(X.get('ETHUSDT', mL, 'sBuy') === 70000 && X.get('ETHUSDT', mL, 'sSell') === 60000 && X.get('ETHUSDT', mL, 'sN') === 55 && rr[2] === 10000 && rr[3] === 20000 && Number.isNaN(X.get('ETHUSDT', mL, 'sWN')), 'light mode: minute buying/selling from the candle’s taker totals; per-second flows from their change; no large-order detail');
  // 9. the liquidity map
  const snap = X.bookSnap({ bids:[['99.9', '100'], ['99.4', '50'], ['98.5', '1000'], ['96', '10']], asks:[['100.1', '100'], ['100.8', '300'], ['104', '5']] }, 123), K = W.KFIELDS, sv = k => snap[K.indexOf(k)];
  ok(sv('mid') === 100 && Math.abs(sv('b05') - 9990) < 1e-6 && Math.abs(sv('b1') - (9990 + 4970)) < 1e-6 && Math.abs(sv('b2') - (9990 + 4970 + 98500)) < 1e-6 && Math.abs(sv('b5') - (9990 + 4970 + 98500 + 960)) < 1e-6 && Math.abs(sv('a1') - (10010 + 30240)) < 1e-6 &&
     Math.abs(sv('bw1d') - 0.015) < 1e-9 && Math.abs(sv('bw1q') - 98500) < 1e-6 && Math.abs(sv('aw1d') - 0.008) < 1e-9 && Math.abs(sv('bSpan') - 0.04) < 1e-9, 'liquidity map: USDT within 0.5/1/2/5% of the mid each side, the largest walls (distance, size), how far the book reaches');
  // 10. timing tags and the plain read
  ok(JSON.stringify(X.session(Date.UTC(2026, 9, 17, 8, 2))) === JSON.stringify(['Europe hours', 'funding settlement', 'weekend']) && X.session(Date.UTC(2026, 9, 19, 14, 30)).join() === 'Europe + US hours', 'time tags: session, funding settlement, daily close, weekend');
  const w = X.win('BTCUSDT', m0, 1), txt = X.read('BTCUSDT', w, -0.02);
  ok(/aggressive net: spot/.test(txt) && /large orders/.test(txt) && /liquidated: longs/.test(txt) && /open interest −2\.0% in the hour \(positions closing\)/.test(txt) && /bids \d+% heavier than asks/.test(txt) && !/NaN|undefined/.test(txt), 'the plain read states facts only: ' + txt);
  // 11. export round trip: the research decoder reads every field back
  await X.persist(); const out = await W.build(3); const tmp = path.join(require('os').tmpdir(), 'omega-watch-test.json'); fs.writeFileSync(tmp, JSON.stringify(out));
  let py = ''; try{ py = cp.execFileSync('python3', ['-I', path.join('/home/claude/research', 'watch16.py'), tmp, '--check'], { encoding:'utf8' }); }catch(e){ py = String(e.stdout || e.message); }
  const want = { sBuy:g('sBuy'), sWN:g('sWN'), prem:g('prem'), liqL:g('liqL'), cbBTC:mk('cbBTC'), events:out.events.length };
  ok(/CHECK/.test(py) && py.includes('BTCUSDT ' + m0 + ' sBuy ' + want.sBuy.toFixed(3)) && py.includes('sWN 2.000') && /\nMKT [^\n]*cbBTC 60100\.500/.test(py) && py.includes('events ' + out.events.length) && out.events.length === 1 && py.includes('SOL post 3600 r60 0.0050'),
    'export → research decoder (watch16.py): minute rows, market row and flight recordings read back exactly', py.slice(0, 600));
  // 12. the streams and their addresses
  opened.length = 0; ls.omega_watch_cfg_v1 = JSON.stringify({ on:true, mode:'full', coins:['BTCUSDT', 'SOLUSDT'], awake:false, bookEvery:0, k:4, liqBurst:10e6 }); X.setRunning(false);
  global.fetch = () => Promise.reject(new Error('offline in test'));
  await W.start(); const us = opened.map(o => o.url), spU = us.find(u => u.startsWith('wss://stream.binance.com')), fuU = us.find(u => u.startsWith('wss://fstream')), cb = opened.find(o => /coinbase/.test(o.url));
  ok(/streams=btcusdt@aggTrade\/btcusdt@depth20\/solusdt@aggTrade\/solusdt@depth20$/.test(spU) && fuU.startsWith('wss://fstream.binance.com/market/stream?streams=') && /btcusdt@aggTrade\/btcusdt@markPrice@1s\/.*!forceOrder@arr$/.test(fuU),
    'streams: spot trades + book; futures trades, mark price and all liquidations on Binance’s /market address (not the old /ws, ended Apr 2026)', us);
  cb.onopen(); ok(JSON.parse(cb.sent[0]).channels[0] === 'ticker' && JSON.parse(cb.sent[0]).product_ids.join() === 'BTC-USD,ETH-USD,USDT-USD', 'Coinbase: subscribes to BTC, ETH and USDT tickers on connect');
  const S = X.socks.futures; S.ws.onopen(); NOW += 61e3; X.watchdog(); ok(S.state === 'silent', 'connected but no data for a minute shows "connected but no data" (a changed address would show here)');
  S.ws.onmessage({ data:JSON.stringify({ stream:'!forceOrder@arr', data:{ e:'forceOrder', o:{ s:'BTCUSDT', S:'BUY', q:'1', p:'60000', ap:'60000', z:'1', T:NOW } } }) }); ok(S.state === 'live' && S.n === 1, 'the first message makes it live');
  await W.stop(); ok(!W.running() && opened.every(o => !o.onclose || true), 'stop closes the feeds');
  ls.omega_watch_cfg_v1 = JSON.stringify({ on:true, mode:'light', coins:['BTCUSDT'], awake:false, bookEvery:0, k:4, liqBurst:10e6 }); opened.length = 0; await W.start(); await W.stop();
  ok(opened.some(o => /btcusdt@kline_1m\/btcusdt@depth20$/.test(o.url)) && opened.some(o => /btcusdt@kline_1m\/btcusdt@markPrice@1s\/!forceOrder@arr$/.test(o.url)), 'light mode asks for 1-minute candles instead of every trade');
  // 13. the page, the navigator, the research report; the positioning collector's liquidation address
  ok(html.includes('data-page="watch"') && html.includes('<div id="page-watch" class="page">') && html.includes("'posdesk','edgelab','watch','ostrat'") && html.includes('marketWatch: safe(function(){ return window.OMEGA_WATCH'), 'Market Watch page: sidebar, page, navigator list, research report');
  ok(html.includes("new WebSocket('wss://fstream.binance.com/market/ws/!forceOrder@arr')") && !html.includes('fstream.binance.com/ws/!forceOrder') && /onmessage = function\(m\)\{ if\(wsState !== 'live'\)/.test(html), 'the positioning collector’s liquidation feed uses the new address and says "live" only once data arrives');
  ok(!/c047445f|apikey=/i.test(grab('MARKET WATCH')), 'no key in the recorder');
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})().catch(e => { console.log('CRASH', e && e.stack); process.exit(1); });
