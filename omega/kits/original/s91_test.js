// v6.5.91 checks: the Daily Plan — market state, side, plans at liquidity, the forward record — on Market Read and Analysis.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-91.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0; new Function(grab('DAILY PLAN'))(); const X = window.OMEGA_DPLAN._;
const NOW = Date.UTC(2026, 9, 22, 2), nowD = Math.floor(NOW/864e5);
function daily(fn){ const o = {}; ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT'].forEach((s, j) => { o[s] = Array.from({ length:600 }, (_, i) => { const d = nowD - 600 + i; return [d*864e5, '0', '0', '0', String(fn(i, j)), '0']; }); }); return o; }
const boom = X.marketState(daily((i, j) => 100*(1 + j*0.1)*Math.exp(i < 570 ? 0.0005*i : 0.0005*570 + 0.012*(i - 570))), NOW);
const dep = X.marketState(daily((i, j) => 100*(1 + j*0.1)*Math.exp(i < 570 ? 0.3 - 0.0002*i : 0.3 - 0.0002*570 - 0.009*(i - 570))), NOW);
ok(boom.state === 'BOOMING' && boom.uptrend && dep.state === 'DEPRESSED' && !dep.uptrend && dep.falling, 'market state: a strong rise reads BOOMING (uptrend), a slide reads DEPRESSED (downtrend, falling this week)', { boom:boom.state, dep:dep.state });
const A = { price:100, ema200:98, atr:1, below:[{ price:98.5, atrs:1.5, label:'yesterday’s low' }], above:[{ price:103, atrs:3, label:'last week’s high' }] };
const L = X.planFor(A, boom), S = X.planFor(Object.assign({}, A, { ema200:102, above:[{ price:101.5, atrs:1.5, label:'24-hour high' }], below:[{ price:97, atrs:3, label:'yesterday’s low' }] }), dep);
const none = X.planFor(Object.assign({}, A, { ema200:102 }), boom), thin = X.planFor(Object.assign({}, A, { above:[{ price:99.2, atrs:0.8, label:'x' }] }), boom);
ok(L.side === 'long' && L.entry === 98.5 && Math.abs(L.stop - 98) < 1e-9 && L.target === 103 && Math.abs(L.rr - 9) < 1e-9 && L.grade === 'C', 'booming → LONG at the liquidity below (entry 98.5, stop half a range lower, target the pool above, 9:1)', L);
ok(S.side === 'short' && S.entry === 101.5 && Math.abs(S.stop - 102) < 1e-9 && S.target === 97, 'depressed → SHORT at the liquidity above', S);
ok(none.side === 'none' && /below its 200-hour/.test(none.why) && thin.side === 'none' && /under 1.5:1/.test(thin.why), 'stand aside when the coin disagrees with the market, or when reward-to-risk is under 1.5:1', { none:none.why, thin:thin.why });
// forward record: a long plan touched, then the target is reached; a short plan touched, then stopped
const h0 = Math.floor(NOW/H) - 10; let rec = { plans:{ BTCUSDT:Object.assign({}, L, { h:h0 }), ETHUSDT:Object.assign({}, S, { h:h0 }) }, open:[], trades:[] };
const rowsB = [{ h:h0 + 1, o:100, hi:100.2, lo:98.4, c:99 }, { h:h0 + 2, o:99, hi:103.5, lo:98.9, c:103 }], rowsE = [{ h:h0 + 1, o:100, hi:101.6, lo:99.8, c:101 }, { h:h0 + 2, o:101, hi:102.4, lo:100.5, c:102.2 }];
rec = X.follow(rec, 'BTCUSDT', rowsB, h0 + 5); rec = X.follow(rec, 'ETHUSDT', rowsE, h0 + 5); const tb = rec.trades.find(t => t.sym === 'BTCUSDT'), te = rec.trades.find(t => t.sym === 'ETHUSDT'), st = X.stats(rec);
ok(tb && tb.out === 'target' && Math.abs(tb.R - (9 - 0.0012*98.5/0.5)) < 1e-3 && te && te.out === 'stop' && te.R < -1 && st.n === 2, 'forward record: the long reaches its target (+9R less costs), the short is stopped (−1R less costs)', { tb, te, st });
(async () => {
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(/binance/.test(u.hostname)){ const q = u.searchParams, nh = Math.floor(Date.now()/H), nd = Math.floor(Date.now()/864e5);
      if(/\/klines$/.test(u.pathname) && q.get('interval') === '1d') return j(Array.from({ length:600 }, (_, i) => { const c = 100*Math.exp(0.0006*i), o = c*0.999; return [(nd - 600 + i)*864e5, String(o), String(c*1.01), String(o*0.99), String(c), '1000']; }));
      if(/\/klines$/.test(u.pathname) && q.get('limit') === '500') return j(Array.from({ length:500 }, (_, i) => { const p = 100 + 2*Math.sin(i/7) + 0.01*i; return [(nh - 500 + i)*H, String(p), String(p + 0.4), String(p - 0.4), String(p + 0.1), '1000']; }));
      if(/\/depth$/.test(u.pathname)) return j({ bids:[['99', '10']], asks:[['101', '10']] }); if(/premiumIndex$/.test(u.pathname)) return j({ markPrice:'105', indexPrice:'105', lastFundingRate:'0.0001' }); return j([]); }
    return j([]); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000); await pg.evaluate(() => navigate('mread')); await pg.waitForTimeout(6000);
  const r = await pg.evaluate(() => ({ t:(document.getElementById('dplanBody') || {}).innerText || '', jobs:window.OMEGA_OPERATOR.jobs().map(j => j.id), wide:document.documentElement.scrollWidth > window.innerWidth }));
  await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(1500); const a = await pg.evaluate(() => (document.getElementById('dplanAnaBody') || {}).innerText || '');
  ok(/Market now/i.test(r.t) && !/Unknown/.test(r.t) && !/no data/.test(r.t) && /Today’s plan/i.test(r.t) && ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'].every(c => r.t.includes(c)) && /Grade C/i.test(r.t) && /Forward record/.test(r.t) && /Market now/i.test(a) && !/\bNaN\b|\bundefined\b/.test(r.t + a) && !r.wide && errs.length === 0 && r.jobs.includes('dplan'), 'in the browser: Market now and Today’s plan for the five coins on Market Read and the Analysis page, graded C, with the forward record; the Autopilot job exists; no NaN, no overflow, no page errors', { errs, jobs:r.jobs.includes('dplan'), head:r.t.slice(0, 160) });
  await pg.screenshot({ path:'/tmp/dplan91.png', fullPage:false }); await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
