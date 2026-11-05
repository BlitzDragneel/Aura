// v6.5.101: Market Watch when the live streams deliver nothing (as in the 19–26 Oct export: 0 minute rows).
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
ok(/v6\.5\.(1\d\d) · build/.test(html) && /v6\.5\.101: a 7-day export/.test(html), 'build v6.5.101 or later, the recorder says what changed and why');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  let mult = 1;
  await ctx.route('**/*', r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue(); const j = x => r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(/\/klines$/.test(u.pathname) && u.searchParams.get('interval') === '1m'){ const n = +u.searchParams.get('limit'), now = Date.now(), m0 = Math.floor(now/60e3)*60e3, fut = /fapi/.test(u.hostname);
      return j(Array.from({ length:n }, (_, i) => { const t = m0 - (n - i)*60e3, c = (fut ? 101 : 100)*mult + i*0.01; return [t, String(c), String(c + 1), String(c - 1), String(c), '10', t + 59999, '1000', 42, '4', '400', '0']; })); }
    if(/coinbase/.test(u.hostname) && /candles/.test(u.pathname)){ const m0 = Math.floor(Date.now()/60e3)*60; return j(Array.from({ length:5 }, (_, i) => [m0 - (i + 1)*60, 99, 101, 100, 100.5*mult, 1])); }
    return j([]); });
  await ctx.addInitScript(() => { window.__ws = []; window.WebSocket = class { constructor(u){ this.url = u; window.__ws.push(u); setTimeout(() => { this.onclose && this.onclose({ code:1006 }); }, 30); } close(){} send(){} }; });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500);
  await pg.evaluate(async () => { const W = window.OMEGA_WATCH; W.setCfg(Object.assign(W.cfg(), { on:true, coins:['BTCUSDT', 'ETHUSDT', 'SOLUSDT'] })); await W.start(); });
  const n1 = await pg.evaluate(async () => { window.__st0 = Date.now(); window.OMEGA_WATCH._.st.since = Date.now() - 4*60e3; return await window.OMEGA_WATCH._.restFill(); });
  const v = await pg.evaluate(() => { const G = window.OMEGA_WATCH._.get, m = Math.floor(Date.now()/60e3) - 1;
    return { sC:G('BTCUSDT', m, 'sC'), pC:G('BTCUSDT', m, 'pC'), sBuy:G('BTCUSDT', m, 'sBuy'), sSell:G('BTCUSDT', m, 'sSell'), sN:G('BTCUSDT', m, 'sN'), sH:G('BTCUSDT', m, 'sH'), bnBTC:G('__MKT__', m, 'bnBTC'), REST:window.OMEGA_WATCH._.REST }; });
  ok(n1 > 0 && v.sC > 100 && v.sC < 101 && v.pC > 101 && v.pC < 102 && v.sBuy === 400 && v.sSell === 600 && v.sN === 42 && Math.abs(v.sH - v.sC - 1) < 1e-4 && v.REST.s.on && v.REST.p.on && v.REST.c.on,
     'streams dead: empty minutes are filled from the 1-minute candles with the exchange’s exact close, taker buy/sell volume, trade count and high', { n1, v });
  mult = 3; const n2 = await pg.evaluate(async () => await window.OMEGA_WATCH._.restFill()); const v2 = await pg.evaluate(() => window.OMEGA_WATCH._.get('BTCUSDT', Math.floor(Date.now()/60e3) - 1, 'sC'));
  ok(Math.abs(v2 - v.sC) < 1e-6, 'a minute already recorded is never overwritten (the second backup run brought different prices; the stored one stays)', { before:v.sC, after:v2, n2 });
  let urls = [];
  for(let k = 0; k < 40; k++){ urls = await pg.evaluate(() => window.__ws.filter(u => /binance\.(com|vision)(:\d+)?\/stream/.test(u) && !/fstream/.test(u)).map(u => u.split('?')[0])); if(urls.some(u => /data-stream\.binance\.vision/.test(u))) break; await pg.waitForTimeout(1000); }
  ok(urls.some(u => /:9443/.test(u)) && urls.some(u => /stream\.binance\.com:443/.test(u)) && urls.some(u => /data-stream\.binance\.vision/.test(u)), 'the spot stream rotates through its three addresses when it never comes alive', [...new Set(urls)]);
  const ex = await pg.evaluate(async () => { window.OMEGA_WATCH._.minuteJobs(); await new Promise(r => setTimeout(r, 1500)); const o = await window.OMEGA_WATCH.build(1); return { rows:(o.coins.BTCUSDT || []).length, diag:o.diag }; });
  ok(ex.rows >= 1 && ex.diag && ex.diag.feeds.spot && ex.diag.feeds.spot.everLive === false && ex.diag.feeds.spot.rotations >= 1 && ex.diag.backup.s.min > 0 && Object.values(ex.diag.daily).some(d => d.spot && d.spot.dead >= 1 && d.futures && d.futures.dead >= 1 && d.bh && (d.bh['BTCUSDT|s'] || []).length >= 1 && (d.bh['BTCUSDT|p'] || []).length >= 1),
     'the export now holds minute rows and a diag section: each feed’s state and address, rotations, backup counts, the daily live/dead log with the hours the backup filled', { rows:ex.rows, feeds:ex.diag && ex.diag.feeds, backup:ex.diag && ex.diag.backup.s });
  await pg.evaluate(() => navigate('watch')); await pg.waitForTimeout(2500); await pg.evaluate(() => window.OMEGA_WATCH.render()); await pg.waitForTimeout(500);
  const t = await pg.evaluate(() => (document.getElementById('watchBody') || {}).innerText || '');
  await pg.evaluate(() => { const e = [...document.querySelectorAll('#watchBody p')].find(p => /Backup on/.test(p.innerText)); if(e) e.scrollIntoView(); }); await pg.screenshot({ path:'/tmp/v101_watch.png' });
  ok(/Backup on/.test(t) && /Liquidations, large orders and flight recordings need the live stream/.test(t) && errs.length === 0, 'the card says the backup is on and what it cannot capture; no page errors', { t:t.slice(0, 300), errs });
  await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(2500); const rc = await pg.evaluate(() => (document.getElementById('rareSigBody') || {}).innerText || '');
  ok(/FAILED\s*Forex majors hour by hour \(E15\)/.test(rc) && /best t 1\.39/.test(rc) && /WAITING\s*Market Watch questions \(E13\)/.test(rc) && /delivered nothing on that device/.test(rc), 'the research card on Signals lists E15 as failed and E13 as waiting, with the reason', rc.slice(-500));
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
