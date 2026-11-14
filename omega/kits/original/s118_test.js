// v6.5.118: gold and silver first-class. Binance -> OKX -> Live API fallback for XAUUSDT/XAGUSDT in Binance's own shape;
// Charts strip (perpetual beside the spot quote, premium, "market closed"); Forex board metals open the 24/7 perpetual;
// the perpetuals in the CREED Scanner, Market Intelligence, Analysis catalog and CREED Desk lists; Autopilot job "metals".
// usage: HARNESS=tools node s118_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
ok(/v6\.5\.1(1[8-9]|[2-9]\d) · build/.test(html), 'build v6.5.118 or later');
ok(html.split('BINANCE, THEN OKX, THEN THE LIVE API (v6.5.118)').length === 2 && html.indexOf('BINANCE, THEN OKX') > html.indexOf('GOLD AND SILVER WITHOUT A KEY'), 'one fallback layer, installed right after the v6.5.40 metals rewrite');
const H = 3600e3;
function okxCandles(n, p){ const out = [], end = Math.floor(Date.now() / H) * H; for(let i = 0; i < n; i++){ const t = end - i * H, c = p * (1 + Math.sin(i) * 0.002); out.push([String(t), String(c), String(c * 1.001), String(c * 0.999), String(c), '100', '10', String(10 * c), i ? '1' : '0']); } return out; }
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(o){ o = o || {}; const ctx = await b.newContext({ viewport:{ width:o.w || 412, height:915 } }); const hits = { binance:0, okx:0 };
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue(); if(M.handle(r)) return;
      const J = (x, st) => r.fulfill({ status:st || 200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
      const sym = (u.searchParams.get('symbol') || u.searchParams.get('instId') || '');
      if(/okx\.com/.test(u.hostname)){ if(/XA[UG]-USDT-SWAP/.test(sym)) hits.okx++; if(o.okxDown) return r.abort();
        if(/market\/candles/.test(u.pathname) && /XAU/.test(sym)) return J({ code:'0', data:okxCandles(+u.searchParams.get('limit') || 100, 2655.1) });
        if(/market\/ticker$/.test(u.pathname) && /XA[UG]/.test(sym)) return J({ code:'0', data:[{ instId:sym, last:/XAU/.test(sym) ? '2655.1' : '31.4', open24h:/XAU/.test(sym) ? '2640' : '31', high24h:'2700', low24h:'2600', volCcy24h:'1234', ts:String(Date.now()) }] });
        return J({ code:'0', data:[] }); }
      if(/binance/.test(u.hostname)){ if(/XA[UG]USDT/.test(sym)) hits.binance++; if(o.binanceDown && /XA[UG]USDT/.test(sym)) return J({ msg:'Service unavailable from a restricted location' }, 451);
        if(/XA[UG]USDT/.test(sym) && /klines$/.test(u.pathname)){ const n = +u.searchParams.get('limit') || 100, out = [], end = Math.floor(Date.now() / H) * H; for(let i = n - 1; i >= 0; i--){ const t = end - i * H; out.push([t, '2650', '2652', '2648', '2651', '5', t + H - 1, '13255', 9, '2', '5300', '0']); } return J(out); }
        if(/XA[UG]USDT/.test(sym) && /ticker\/24hr$/.test(u.pathname)) return J({ symbol:sym, lastPrice:/XAU/.test(sym) ? '2651' : '31.3', priceChangePercent:'0.40' });
        if(/XA[UG]USDT/.test(sym) && /ticker\/price$/.test(u.pathname)) return J({ symbol:sym, price:'2651' }); }
      return J([]); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(p => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); if(p) Object.keys(p).forEach(k => localStorage.setItem(k, p[k])); }, o.prep || null);
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000); return { ctx, pg, errs, hits }; }
  const KL = 'https://data-api.binance.vision/api/v3/klines?symbol=XAUUSDT&interval=1h&limit=50';
  // 1. Binance answers: Binance is used, nothing else
  let { ctx, pg, errs, hits } = await open({ prep:{ omega_live_token:M.TOKEN } });
  let r = await pg.evaluate(async u => { const res = await fetch(u); const j = await res.json(); return { n:j.length, row:j[j.length - 1], st:window.OMEGA_GSDATA.state() }; }, KL);
  ok(r.n === 50 && r.row[4] === '2651' && r.st.binance >= 1 && r.st.okx === 0 && hits.okx === 0, 'Binance answers: gold candles come straight from Binance (no OKX, no Live API)', r);
  // lists
  const L = await pg.evaluate(() => { const ac = document.getElementById('creedAsset'); if(ac){ ac.value = 'crypto'; ac.dispatchEvent(new Event('change')); }
    return { radar:window.OMEGA_RADAR.universe().crypto, intel:window.OMEGA_INTEL.universe().crypto, cat:window.OMEGA_MARKETS.all('crypto'), creed:Array.from((document.getElementById('creedSymbol') || { options:[] }).options).map(o => o.value),
      jobs:window.OMEGA_OPERATOR.jobs().map(j => j.id), once:JSON.parse(localStorage.getItem('omega_metals_added_v118') || '{}') }; });
  ok(['radar', 'intel', 'cat', 'creed'].every(k => L[k].includes('XAUUSDT') && L[k].includes('XAGUSDT')), 'XAUUSDT and XAGUSDT are in the CREED Scanner, Market Intelligence, the Analysis catalog and the CREED Desk crypto list', { radar:L.radar.slice(-3), intel:L.intel.slice(-3), creed:L.creed.slice(0, 4) });
  ok(L.jobs.includes('metals') && L.jobs.includes('fxboard'), 'the Autopilot runs the job "metals" (one scheduler)', L.jobs);
  // Charts: open the perpetual; the strip shows perp, spot (closed or live) and the premium
  await pg.evaluate(() => window.OMEGA_GS.openPerp('XAUUSDT')); await pg.waitForTimeout(3000);
  let c = await pg.evaluate(() => ({ act:document.querySelector('.page.active').id, sym:document.getElementById('symbol').value, ac:document.getElementById('assetClass').value, strip:(document.getElementById('gsSpot') || {}).innerText || '', hid:document.getElementById('gsSpot').hidden }));
  ok(c.act === 'page-analysis' && c.sym === 'XAUUSDT' && c.ac === 'crypto' && !c.hid && /Gold · perpetual XAUUSDT/i.test(c.strip) && /2651\.00/.test(c.strip) && /\+0\.40% 24h/.test(c.strip) && /Spot XAU\/USD/i.test(c.strip) && /2650\.40/.test(c.strip) && /Swissquote live/.test(c.strip) && /\+0\.02%/.test(c.strip),
    'Charts: gold perpetual chart with the spot quote beside it (Swissquote via the Live API) and the perpetual premium', c);
  const job = await pg.evaluate(async () => { const j = window.OMEGA_OPERATOR.jobs().find(x => x.id === 'metals'); return { every:j.every(), res:await j.run() }; });
  ok(job.every === 60e3 && /Gold: perpetual 2651\.00, spot 2650\.40/.test(job.res), 'job "metals": every minute while a gold chart is open, refreshes both prices', job);
  // Forex board: metals tab note; gold opens the perpetual
  await pg.evaluate(() => navigate('forex')); await pg.waitForTimeout(1200); await pg.click('[data-fxg="metals"]'); await pg.waitForTimeout(1500);
  const fb = await pg.evaluate(() => ({ rows:document.querySelectorAll('#fxBoard .fx-row').length, note:(document.querySelector('#fxBoard .gs-note') || {}).innerText || '' }));
  ok(fb.rows === 4 && /trade around the clock/.test(fb.note) && /CME break/.test(fb.note) && /Gold 24\/7 chart/.test(fb.note), 'Forex board, Metals: 4 rows and a note with the 24/7 perpetual charts', fb);
  await pg.click('[data-fx="XAGUSD"]'); await pg.waitForTimeout(2500);
  c = await pg.evaluate(() => ({ act:document.querySelector('.page.active').id, sym:document.getElementById('symbol').value, strip:document.getElementById('gsSpot').innerText }));
  ok(c.act === 'page-analysis' && c.sym === 'XAGUSDT' && /Silver · perpetual XAGUSDT/i.test(c.strip) && /Spot XAG\/USD/i.test(c.strip), 'tapping silver on the board opens the silver perpetual chart, spot beside it', c);
  const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  ok(!errs.length && !wide, 'no page errors, nothing wider than the phone', { errs, wide });
  await ctx.close();
  // 2. Binance blocked (451): OKX answers in Binance's shape, keyless
  ({ ctx, pg, errs, hits } = await open({ binanceDown:true }));
  r = await pg.evaluate(async u => { const res = await fetch(u); const j = await res.json(); const t = await (await fetch('https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=XAUUSDT')).json();
    return { n:j.length, row:j[j.length - 1], src:res.headers.get('x-omega-source'), asc:j.every((x, i) => !i || x[0] > j[i - 1][0]), t, st:window.OMEGA_GSDATA.state() }; }, KL);
  ok(r.n === 50 && r.src === 'okx' && r.asc && r.row.length === 12 && +r.row[4] > 2600 && r.t.lastPrice === '2655.1' && Math.abs(+r.t.priceChangePercent - 0.568) < 0.01 && r.st.okx >= 2, 'Binance blocked: gold candles and the 24h ticker come from OKX, in Binance’s shape, oldest first', { n:r.n, src:r.src, t:r.t });
  await pg.evaluate(() => { const ac = document.getElementById('assetClass'); navigate('analysis'); }); await pg.evaluate(() => window.OMEGA_GS.openPerp('XAUUSDT')); await pg.waitForTimeout(2500);
  c = await pg.evaluate(() => document.getElementById('gsSpot').innerText);
  ok(/2655\.10/.test(c) && /OKX \(Binance did not answer\)/.test(c) && /needs the Live API token/.test(c), 'the strip says the price came from OKX and that spot needs the token', c);
  ok(!errs.length, 'no page errors (Binance blocked)', errs);
  await ctx.close();
  // 3. Binance and OKX both down, token set: the Live API answers
  ({ ctx, pg, errs, hits } = await open({ binanceDown:true, okxDown:true, prep:{ omega_live_token:M.TOKEN } }));
  M.calls.length = 0;
  await pg.waitForFunction(() => window.OMEGA_LAPI && window.OMEGA_LAPI.on(), null, { timeout:10000 });
  r = await pg.evaluate(async u => { const res = await fetch(u); const j = await res.json(); return { n:j.length, row:j[j.length - 1], src:res.headers.get('x-omega-source') }; }, KL);
  const lk = M.calls.filter(x => x.path === '/crypto/klines' && /symbol=XAUUSDT/.test(x.q));
  ok(r.n === 50 && r.src === 'omega-live-api' && Math.abs(+r.row[4] - 2655.1) < 0.01 && lk.length === 1 && lk[0].auth, 'Binance and OKX down: the Live API answers (/crypto/klines with the token), same shape', { n:r.n, src:r.src, calls:lk });
  // 4. everything down, no token: a clear error, not a crash
  await pg.evaluate(() => localStorage.removeItem('omega_live_token'));
  r = await pg.evaluate(async u => { try{ await fetch(u); return 'no error'; }catch(e){ return String(e.message); } }, KL);
  ok(/Binance, OKX and the Live API all failed/.test(r) && /no Live API token/.test(r), 'all sources down: one plain error naming what failed', r);
  ok(!errs.length, 'no page errors (all down)', errs);
  // 5. a stored list she edited gets the perpetuals once; removing them later is respected
  await ctx.close();
  ({ ctx, pg, errs } = await open({ prep:{ omega_radar_universe_v1:JSON.stringify({ crypto:['BTCUSDT', 'ETHUSDT'], forex:['EUR/USD'] }) } }));
  const u1 = await pg.evaluate(() => window.OMEGA_RADAR.universe().crypto.slice());
  await pg.evaluate(() => { localStorage.setItem('omega_radar_universe_v1', JSON.stringify({ crypto:['BTCUSDT'], forex:['EUR/USD'] })); }); await pg.reload(); await pg.waitForTimeout(3500);
  const u2 = await pg.evaluate(() => window.OMEGA_RADAR.universe().crypto.slice());
  ok(JSON.stringify(u1) === JSON.stringify(['BTCUSDT', 'ETHUSDT', 'XAUUSDT', 'XAGUSDT']) && JSON.stringify(u2) === JSON.stringify(['BTCUSDT']), 'an edited scanner list gets gold and silver once; a later removal is respected', { u1, u2 });
  await ctx.close(); await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
