// v6.5.92 checks: the Risk Guard's rules, the Growth Bot (reads signals, never changes them), the pre-trade check and journal,
// automatic exports, the page and the Autopilot jobs.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-92.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0; new Function(grab('RISK GUARD AND GROWTH BOT'))(); const X = window.OMEGA_RGUARD._, NOW = Date.UTC(2026, 9, 22, 12);
// 1. the rules
const a = X.newAcct(100); const L0 = X.limits(a, NOW);
const d = X.newAcct(100); d.eq = 97.9; d.closed.push({ pnl:-2.1, at:NOW - 3600e3 }); const Ld = X.limits(d, NOW);
const w = X.newAcct(100); w.eq = 94.8; w.closed.push({ pnl:-2.6, at:NOW - 3*864e5 }, { pnl:-2.6, at:NOW - 2*864e5 }); const Lw = X.limits(w, NOW);
const r = X.newAcct(100); r.peak = 125; const Lr = X.limits(r, NOW); const o = X.newAcct(100); o.open = [{}, {}]; const Lo = X.limits(o, NOW); const u = X.newAcct(100); u.nClean = 30;
ok(L0.risk === 0.005 && !L0.blocked && /daily stop/.test(Ld.blocked) && /weekly stop/.test(Lw.blocked) && /review/.test(Lr.blocked) && /two trades/.test(Lo.blocked) && X.limits(u, NOW).risk === 0.01, 'rules: 0.5% risk (1% after 30 clean trades); daily −2%, weekly −5%, review at −20% and 2 open each block new trades', { L0, d:Ld.blocked, w:Lw.blocked, r:Lr.blocked, o:Lo.blocked });
// 2. the bot reads signals and never changes them
const climax = { trades:[{ sym:'OLDUSDT', t:1, e:2, status:'closed', net:0.05 }] }; window.OMEGA_CLIMAX = { state:() => climax };
store.omega_dplan_v1 = JSON.stringify({ plans:{}, open:[], trades:[] });
let A = X.newAcct(100); A = X.step(A, X.sources(), NOW);                                  // primes: the old climax trade is not taken
climax.trades.push({ sym:'NEWUSDT', t:9, e:10, status:'open' }); store.omega_dplan_v1 = JSON.stringify({ plans:{}, open:[{ sym:'BTCUSDT', side:'long', entry:100, stop:99, h:500 }], trades:[] });
const snapC = JSON.stringify(climax), snapD = store.omega_dplan_v1; A = X.step(A, X.sources(), NOW + 60e3);
climax.trades.push({ sym:'THIRDUSDT', t:11, e:12, status:'open' }); A = X.step(A, X.sources(), NOW + 120e3);
const took = A.open.map(x => [x.src, x.sym, +x.notional.toFixed(2)]);
ok(A.open.length === 2 && took.some(x => x[0] === 'climax' && x[1] === 'NEWUSDT' && x[2] === 5) && took.some(x => x[0] === 'plan' && x[1] === 'BTCUSDT' && x[2] === 50) && A.skips.some(s => s.sym === 'THIRDUSDT' && /two trades/.test(s.why)) && !A.open.some(x => x.sym === 'OLDUSDT'), 'Growth Bot: forward only; a climax trade sized at risk ÷ 10% (5 USDT) and a Daily Plan trade at risk ÷ stop (50 USDT); a later third refused while 2 are open', { took, skips:A.skips });
climax.trades[1].status = 'closed'; climax.trades[1].net = 0.02; store.omega_dplan_v1 = JSON.stringify({ plans:{}, open:[], trades:[{ sym:'BTCUSDT', side:'long', h:500, R:2, out:'target' }] });
const snapC2 = JSON.stringify(climax), snapD2 = store.omega_dplan_v1; A = X.step(A, X.sources(), NOW + 2*3600e3); const S = X.stats(A);
ok(Math.abs(A.eq - 101.1) < 1e-9 && S.n === 2 && JSON.stringify(climax) === snapC2 && store.omega_dplan_v1 === snapD2 && snapC.length > 0 && snapD.length > 0, 'Growth Bot: books +0.10 (climax +2% on 5 USDT) and +1.00 (Daily Plan +2R on 0.50 risk) → 101.10; the signal records are left exactly as they were', { eq:A.eq, n:S.n });
// 3. my trades
const M = X.newAcct(100), big = X.preCheck(M, 100, 98, 100, NOW), fine = X.preCheck(M, 100, 98, 20, NOW), tiny = X.preCheck(M, 100, 98, 4, NOW);
let M2 = X.logTrade(X.newAcct(100), { sym:'BTC', side:'long', entry:100, stop:98, size:25 }); const id = M2.open[0].id; M2 = X.closeTrade(M2, id, 102);
ok(!big.ok && /Too big/.test(big.msgs.join(' ')) && Math.abs(big.maxSize - 25) < 1e-9 && fine.ok && /5 USDT minimum/.test(tiny.msgs.join(' ')) && Math.abs(M2.eq - 100.48) < 1e-9 && M2.breaks === 0 && M2.nClean === 1, 'pre-trade check: 2% risk refused with the right size (25 USDT); within the rule accepted; under 5 USDT warned; the journal books +0.48 after fees', { big:big.msgs, eq:M2.eq });
(async () => {
  // 4. automatic exports, each once
  let mw = 0, fx = 0; window.OMEGA_MREAD = { _:{ checkDays:() => ({ good:[20380, 20381, 20382] }) } }; window.OMEGA_WATCH = { exportData:async () => { mw++; } };
  window.OMEGA_GOLDH = { SYMS:['XAU/USD', 'EUR/USD'], state:() => ({ recs:{ 'XAU/USD':{ done:true }, 'EUR/USD':{ done:true } } }), save:async () => { fx++; } };
  const e1 = await X.autoExport(), e2 = await X.autoExport();
  ok(mw === 1 && fx === 1 && /saved 7 days/.test(e1) && /already saved/.test(e2), 'automatic exports: Market Watch after 3 new full days and the finished metals/forex file, each saved once', { e1, e2, mw, fx });
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('rguard')); await pg.waitForTimeout(1200);
  await pg.fill('#rgEntry', '100'); await pg.fill('#rgStop', '98'); await pg.fill('#rgSize', '100'); await pg.click('[data-rg="check"]'); await pg.waitForTimeout(300);
  const kept = await pg.evaluate(() => [document.getElementById('rgEntry').value, document.getElementById('rgStop').value, document.getElementById('rgSize').value].join('/'));
  const t = await pg.evaluate(async () => { await window.OMEGA_OPERATOR.tick('rguard'); const e = document.getElementById('page-rguard'); return { text:e.innerText, jobs:window.OMEGA_OPERATOR.jobs().map(j => j.id), res:(window.OMEGA_OPERATOR.state().jobs.rguard || {}).result, wide:document.documentElement.scrollWidth > window.innerWidth, curve:!!e.querySelector('svg.rg-curve') }; });
  const F = { bot:/Growth Bot/.test(t.text), before:/Before a real trade/i.test(t.text), big:/Too big/.test(t.text), exp:/Research exports/i.test(t.text), curve:t.curve, nan:/\bNaN\b|\bundefined\b/.test(t.text), wide:t.wide };
  ok(kept === '100/98/100' && /Growth Bot/.test(t.text) && /Before a real trade/i.test(t.text) && /Too big/.test(t.text) && /Research exports/i.test(t.text) && t.curve && t.jobs.includes('rguard') && t.jobs.includes('autoexp') && /Equity 100\.00 USDT/.test(t.res || '') && !/\bNaN\b|\bundefined\b/.test(t.text) && !t.wide && errs.length === 0, 'in the browser: the Risk Guard page (bot with its curve, pre-trade check refusing an oversized trade, exports); the Autopilot runs the bot; no NaN, no overflow, no page errors', { errs, res:t.res, F, kept });
  await pg.screenshot({ path:'/tmp/rguard92.png', fullPage:true }); await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
