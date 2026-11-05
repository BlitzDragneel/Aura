// v6.5.93 checks: the Market Cockpit — labels kept apart, depth, volume split, the chart's parts, the page and the Autopilot.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-93.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0; new Function(grab('MARKET COCKPIT'))(); const X = window.OMEGA_COCKPIT._;
const sp = X.spread([{ y:50 }, { y:51 }, { y:52 }, { y:200 }, { y:259 }, { y:260 }], 12, 262, 9.5), ly = sp.map(l => l.ly);
ok(ly.every((v, i) => i === 0 || v - ly[i-1] >= 9.5 - 1e-9) && Math.min(...ly) >= 12 && Math.max(...ly) <= 262, 'price labels are kept at least 9.5 apart and inside the chart', ly);
const dq = X.depthBuckets({ bids:[['99', '2'], ['98.5', '1']], asks:[['101', '3']] }, 95, 105, 10);
ok(Math.abs(dq.bids[3] - 98.5) < 1e-9 && Math.abs(dq.bids[4] - 198) < 1e-9 && Math.abs(dq.asks[6] - 303) < 1e-9 && dq.max === 303, 'the book column sums resting bids and asks by price band');
const NOW = Date.UTC(2026, 9, 22, 10), kl = Array.from({ length:500 }, (_, i) => { const p = 100 + 3*Math.sin(i/8); return [NOW - (500 - i)*H, String(p), String(p + 0.6), String(p - 0.6), String(p + 0.2), '1000', 0, String(1000*p), 0, String(i % 2 ? 700 : 300), String(i % 2 ? 700*p : 300*p)]; });
const B = X.bars(kl); ok(B.length === 500 && B[1].buy === 0.7 && B[0].buy === 0.3, 'volume is split by the taker-buy share of each candle');
const A = { err:null, price:100.2, chg24:0.01, range24:0.03, typDay:0.04, atrPct:0.006, pos:{ funding:0.0001, oiChg:0.02, ls:1.3 }, crowd:'balanced', book:{ imb1:0.2 }, above:[{ kind:'PDH', side:'above', price:103.2 }, { kind:'RND', side:'above', price:105 }], below:[{ kind:'PDL', side:'below', price:97.1 }, { kind:'EQL', side:'below', price:96.9 }] };
const P = { side:'long', entry:97.1, stop:96.6, target:103.2, rr:12.2, why:'Market in an uptrend', near:'yesterday’s low', far:'yesterday’s high' };
const svg = X.chart({ sym:'BTCUSDT', tf:'1h', kl, depth:{ bids:[['99', '50'], ['98', '30']], asks:[['101', '40']] } }, A, P), svg0 = X.chart({ sym:'BTCUSDT', tf:'1h', kl }, A, { side:'none' });
const cnt = re => (svg.match(re) || []).length;
ok(cnt(/data-c="1"/g) === 72 && cnt(/data-v="1"/g) === 72 && cnt(/data-lv="/g) === 4 && cnt(/data-zone="(stop|target|entry)"/g) === 3 && cnt(/data-d="[ab]"/g) >= 2 && !/NaN|undefined|Infinity/.test(svg) && !/data-zone/.test(svg0), 'the chart: 72 candles and volume bars, 4 liquidity levels, the plan’s entry/stop/target zones (none without a plan), the book column, no NaN');
(async () => {
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(/binance/.test(u.hostname)){ const q = u.searchParams, nh = Math.floor(Date.now()/H), iv = q.get('interval'), step = iv === '15m' ? H/4 : iv === '1d' ? 24*H : H, n = +(q.get('limit') || 100);
      if(/\/klines$/.test(u.pathname)) return j(Array.from({ length:n }, (_, i) => { const p = 100 + 3*Math.sin(i/8) + 0.004*i; return [nh*H - (n - i)*step, String(p), String(p + 0.6), String(p - 0.6), String(p + 0.2), '1000', 0, String(1000*p), 0, String(i % 2 ? 650 : 350), String((i % 2 ? 650 : 350)*p)]; }));
      if(/\/depth$/.test(u.pathname)) return j({ bids:Array.from({ length:50 }, (_, i) => [String(101 - i*0.1), String(i === 20 ? 400 : 10)]), asks:Array.from({ length:50 }, (_, i) => [String(101.2 + i*0.1), '10']) });
      if(/premiumIndex$/.test(u.pathname)) return j({ markPrice:'101.1', indexPrice:'101.1', lastFundingRate:'0.0001' }); return j([]); }
    return j([]); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(5000);
  const r = await pg.evaluate(() => { const e = document.getElementById('cockpitBody'), labs = Array.from(e.querySelectorAll('[data-lab]')).map(t => +t.getAttribute('y')).sort((a, b) => a - b);
    return { text:e.innerText, candles:e.querySelectorAll('[data-c]').length, vol:e.querySelectorAll('[data-v]').length, depth:e.querySelectorAll('[data-d]').length, lv:e.querySelectorAll('[data-lv]').length, minGap:labs.length > 1 ? Math.min(...labs.slice(1).map((y, i) => y - labs[i])) : 99, wide:document.documentElement.scrollWidth > window.innerWidth, jobs:window.OMEGA_OPERATOR.jobs().map(j => j.id) }; });
  await pg.waitForTimeout(4000); const zp = await pg.evaluate(() => { const r = JSON.parse(localStorage.getItem('omega_dplan_v1') || 'null'), P = r && r.plans ? r.plans.BTCUSDT : null; return { side:P ? P.side : null, zones:document.querySelectorAll('#cockpitBody [data-zone]').length, card:(document.querySelector('#cockpitBody .ck-setup') || {}).innerText || '' }; });
  ok(zp.side && (zp.side === 'none' ? /No setup/.test(zp.card) && zp.zones === 0 : zp.zones === 3 && new RegExp(zp.side.toUpperCase()).test(zp.card)), 'the cockpit follows the Daily Plan: its zones and setup card match the plan for the coin (here: ' + zp.side + ')', zp);
  await pg.screenshot({ path:'/tmp/cockpit93.png', fullPage:true });
  await pg.click('[data-cktf="15m"]'); await pg.waitForTimeout(3000); const r2 = await pg.evaluate(() => ({ on:(document.querySelector('[data-cktf="15m"]') || {}).className, candles:document.querySelectorAll('#cockpitBody [data-c]').length, ax:document.querySelector('#cockpitBody .ck-ax') ? 1 : 0 }));
  const t = await pg.evaluate(async () => { await window.OMEGA_OPERATOR.tick('cockpit'); return (window.OMEGA_OPERATOR.state().jobs.cockpit || {}).result; });
  ok(/Market cockpit/i.test(r.text) && /Aggressive buying 24 h/.test(r.text) && r.candles === 72 && r.vol === 72 && r.depth >= 2 && r.lv >= 2 && r.minGap >= 9 && /on/.test(r2.on) && r2.candles === 72 && /Read at/.test(t || '') && r.jobs.includes('cockpit') && !/\bNaN\b|\bundefined\b/.test(r.text) && !r.wide && errs.length === 0, 'in the browser: the cockpit on the Analysis page (strip, 72 candles, volume, book, levels, labels apart), the 15-minute view, the Autopilot refresh; no NaN, no overflow, no page errors', { errs, r:Object.assign({}, r, { text:r.text.slice(0, 80) }), r2, t });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
