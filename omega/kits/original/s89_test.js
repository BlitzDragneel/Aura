// v6.5.89 checks: Market Read (levels, equal highs, book walls, crowding, the read, level memory, recorded days, page, jobs),
// the Brain's knowledge (E1–E13, lessons), research record 26–28, and the gold download stopping on a paid-plan answer.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-89.html'), html = fs.readFileSync(FILE, 'utf8');
const R109 = html.indexOf('window.OMEGA_GOLDH =') < 0;   // v6.5.109: research (Edge Lab knowledge, gold download, Market Watch days) left the app
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
new Function(grab('MARKET READ'))(); const M = window.OMEGA_MREAD, X = M._;
// a synthetic market: 500 hours, a planted pair of equal highs at 102.0, a wall in the book, crowded longs
const NOW = Date.UTC(2026, 9, 21, 12, 30), nowH = Math.floor(NOW/H), kl = [];
for(let k = 0; k < 500; k++){ const h = nowH - 500 + k, base = 100 + 0.8*Math.sin(k/9); let hi = base + 0.3, lo = base - 0.3; if(k === 430 || k === 455){ hi = 102.0; } kl.push([h*H, String(base), String(hi), String(lo), String(base + 0.05), '1000']); }
const price = +kl[499][4], depth = { bids:[], asks:[] }; for(let i = 1; i <= 200; i++){ depth.bids.push([String(price*(1 - i*0.0001)), i === 50 ? '5000' : '10']); depth.asks.push([String(price*(1 + i*0.0001)), '10']); }
const D = { kl, depth, prem:{ markPrice:String(price), indexPrice:String(price*0.9998), lastFundingRate:'0.00025' }, oi:Array.from({ length:25 }, (_, i) => ({ sumOpenInterest:String(1000*(1 + 0.05*i/24)), sumOpenInterestValue:'1e6' })), ls:Array.from({ length:25 }, () => ({ longShortRatio:'2.4' })) };
const A = X.analyze('BTCUSDT', D, NOW);
const d0 = Math.floor(nowH/24)*24; let pdh = -1e9, pdl = 1e9; kl.forEach(k => { const h = Math.floor(+k[0]/H); if(h >= d0 - 24 && h < d0){ pdh = Math.max(pdh, +k[2]); pdl = Math.min(pdl, +k[3]); } });
const all = A.above.concat(A.below), find = kind => all.find(p => p.kind === kind || (p.also || []).length && p.kind === kind);
ok(!A.err && all.some(p => Math.abs(p.price - pdh) < 1e-9 || (p.also || []).includes('yesterday’s high')) && all.some(p => Math.abs(p.price - pdl) < 1e-9 || (p.also || []).includes('yesterday’s low')), 'yesterday’s high and low are found exactly', { pdh, pdl, kinds:all.map(p => [p.kind, +p.price.toFixed(3)]) });
const eq = A.above.find(p => Math.abs(p.price - 102.0) < 0.05 && (p.kind === 'EQH' || (p.also || []).includes('equal highs')));
ok(eq && Math.abs(eq.price - 102.0) < 0.05 && (eq.touches >= 2 || (eq.also || []).includes('equal highs')), 'the planted equal highs (two touches at 102.0) are found above price', eq);
ok(all.some(p => p.kind === 'RND'), 'round numbers are among the levels');
ok(A.book && A.book.bidWalls.length && Math.abs(A.book.bidWalls[0].price/price - (1 - 50*0.0001)) < 0.001 && A.book.imb1 > 0.15, 'the planted bid wall is found, and the book reads buyer-heavy', A.book && A.book.bidWalls[0]);
ok(A.crowd === 'longs' && A.read.length >= 5 && !A.read.join(' ').match(/NaN|undefined|Infinity/) && /plan E12/.test(A.read[A.read.length - 1]) && /does not say which way/.test(A.read[A.read.length - 1]), 'crowded longs read correctly; the read is complete, honest about what research supports, and has no gaps', A.read.slice(-2));
// level memory: remember now, then a day later price reaches the nearest level above
X.remember(A); const target = A.above[0].price, later = kl.slice(25).concat(Array.from({ length:25 }, (_, i) => { const h = nowH + i; return [h*H, String(price), String(i === 5 ? target*1.001 : price*1.001), String(price*0.999), String(price), '1000']; }));
const Mm = X.resolve('BTCUSDT', later, NOW + 26*H), key = Object.keys(Mm.stats).find(k => k.startsWith(A.above[0].kind + '|'));
ok(key && Mm.stats[key][1] >= 1 && Mm.recs.some(r => r.done), 'level memory: a level price reached within 24 hours is scored as reached', Mm.stats);
// recorded days: a full day of Market Watch minutes is counted
const dayFull = Math.floor(NOW/864e5) - 1; window.OMEGA_WATCH = { _:{ get:(s, m, f) => (Math.floor(m/1440) === dayFull ? 100 : NaN) } };
const DD = X.checkDays(NOW); ok(DD.good && DD.good.includes(dayFull) && DD.days[dayFull] === 1, 'a full recorded Market Watch day is counted toward plan E13');
// Brain knowledge, lessons, record
if(!R109){ const KN = JSON.parse(html.slice(html.indexOf('var KN = ') + 9, html.indexOf(';\n', html.indexOf('var KN = '))));
ok(['E1','E2','E3','E5','E8','E9','E10','E11','E12','E13'].every(r => KN.earlier.some(e => e.r === r)) && KN.lessons.some(x => /Count results by week/.test(x)) && /t:'A stop-out is usually just noise'/.test(html) && ["{ round:'26',", "{ round:'27',", "{ round:'28',"].every(r => html.includes(r)) && /Research record, rounds 1\\u2013(2[89]|3[0-9])/.test(html), 'the Brain knows plans E1–E13 and the new lessons; research record rounds 26–28'); }
(async () => {
  if(!R109){
  // gold download: a paid-plan answer for silver is final
  global.indexedDB = require((process.env.HARNESS || path.join(D0, 'tools')) + '/fake_idb.js')(); store.omega_td_key = 'KEY1234567890abcdef';
  new Function(grab('GOLD HOURLY HISTORY'))(); const G = window.OMEGA_GOLDH; G._.setWait({ gap:0, retry:0, limit:0 }); let calls = 0;
  global.fetch = async url => { calls++; const sym = new URL(url).searchParams.get('symbol'), J = x => ({ json:async () => x });
    if(sym === 'XAG/USD') return J({ status:'error', code:403, message:'This symbol is available starting with the Grow or Venture plan.' });
    return J({ status:'ok', values:Array.from({ length:1200 }, (_, i) => { const h = Math.floor(Date.UTC(2026, 9, 20)/H) - i, v = 4000 + Math.sin(i); return { datetime:new Date(h*H).toISOString().slice(0, 19).replace('T', ' '), open:String(v), high:String(v + 1), low:String(v - 1), close:String(v) }; }) }); };
  const r1 = await G.run(), xag = G.state().recs['XAG/USD'], c1 = calls; const r2 = await G.run(); 
  ok(/Done/.test(r1) && xag && xag.done && /free Twelve Data plan/.test(xag.unavailable) && calls === c1, 'silver’s paid-plan answer is final: marked unavailable, gold completes, and no further requests are made', { r1, xag:xag && xag.unavailable, calls, c1 }); }
  // browser: the page with a fake Binance, the Autopilot jobs
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(/binance/.test(u.hostname)){ const nh = Math.floor(Date.now()/H);
      if(/\/klines$/.test(u.pathname) && u.searchParams.get('limit') === '500') return j(D.kl.map((k, i) => [(nh - 500 + i)*H, k[1], k[2], k[3], k[4], k[5]]));
      if(/\/depth$/.test(u.pathname)) return j(D.depth); if(/premiumIndex$/.test(u.pathname)) return j(D.prem);
      if(/openInterestHist$/.test(u.pathname)) return j(D.oi); if(/globalLongShortAccountRatio$/.test(u.pathname)) return j(D.ls); return j([]); }
    if(/twelvedata|coinbase/.test(u.hostname)) return j([]); return route.abort(); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000); await pg.evaluate(() => navigate('mread')); await pg.waitForTimeout(3000);
  const r = await pg.evaluate(() => { const e = document.getElementById('page-mread'); return { text:e.innerText, pools:e.querySelectorAll('svg.mr-ladder [data-pool]').length, walls:e.querySelectorAll('svg.mr-ladder [data-wall]').length, wide:document.documentElement.scrollWidth > window.innerWidth, jobs:window.OMEGA_OPERATOR.jobs().map(j => j.id) }; });
  ok(/the read/i.test(r.text) && /Nearest liquidity above/.test(r.text) && r.pools >= 4 && r.walls >= 1 && !/\bNaN\b|\bundefined\b/.test(r.text) && !r.wide && errs.length === 0, 'in the browser: the read, the liquidity ladder (' + r.pools + ' levels, ' + r.walls + ' walls), no NaN, no overflow, no page errors', { errs, wide:r.wide });
  const t = await pg.evaluate(async () => { await window.OMEGA_OPERATOR.tick('mread'); await window.OMEGA_OPERATOR.tick('mwdays'); const S = window.OMEGA_OPERATOR.state().jobs; return { mread:S.mread && S.mread.result, mwdays:S.mwdays && S.mwdays.result }; });
  ok(r.jobs.includes('mread') && (R109 ? !r.jobs.includes('mwdays') : r.jobs.includes('mwdays') && /full day/.test(t.mwdays || '')) && /BTC read, ETH read/.test(t.mread || ''), 'the Autopilot runs Market Read (BTC and ETH) and the recorded-days check', t);
  await pg.screenshot({ path:'/tmp/mread89.png', fullPage:true }); await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
