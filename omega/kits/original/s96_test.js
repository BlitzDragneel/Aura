// v6.5.96 checks: the data check, the bot against holding BTC, the fill stress, and the bot keeping each trade's size.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-96.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0; new Function(grab('DATA CHECK AND BASELINES'))(); const X = window.OMEGA_TRUTH._, NOW = Date.UTC(2026, 9, 25, 12);
const J = X.jobsCheck([{ id:'a', every:H }, { id:'b', every:H }, { id:'c', every:H }, { id:'d', every:H }, { id:'e', every:H }], { a:{ last:NOW - 30*60e3, result:'ok' }, b:{ last:NOW - 3*H, result:'ok' }, c:{ last:NOW - 10*60e3, result:'Problem: HTTP 418' }, e:{ enabled:false } }, NOW);
ok(J.map(j => j.status).join() === 'fresh,overdue,failing,never run,off', 'jobs: fresh, overdue (over twice the schedule), failing, never run, switched off', J.map(j => j.status));
const nowH = Math.floor(NOW/H), R = X.readsCheck({ BTCUSDT:{ lastH:nowH - 1, at:NOW - 60e3, pos:{ premium:0.0003 } }, ETHUSDT:{ lastH:nowH - 5, at:NOW - 60e3, pos:{ premium:0.0002 } }, SOLUSDT:{ lastH:nowH - 1, at:NOW - 60e3, pos:{ premium:0.012 } } }, NOW);
ok(R.find(r => r.sym === 'BTCUSDT').ok && /candle/.test(R.find(r => r.sym === 'ETHUSDT').issues[0]) && /spot index/.test(R.find(r => r.sym === 'SOLUSDT').issues[0]), 'markets: current candles and sane prices pass; a 4-hour-old candle and a 1.2% gap to the spot index are flagged', R);
const B = X.baseline({ eq:103 }, { t0:NOW - 864e5, btc0:100000, eq0:100 }, 105000), B2 = X.baseline({ eq:101 }, { t0:NOW, btc0:100000, eq0:100 }, 104000);
ok(Math.abs(B.bot - 0.03) < 1e-12 && Math.abs(B.btc - 0.05) < 1e-12 && !B.beats && Math.abs(B2.bot - 0.01) < 1e-12 && !B2.beats && X.baseline({ eq:110 }, { t0:NOW, btc0:100, eq0:100 }, 99).beats, 'baseline: the bot’s change is compared with holding BTC over the same time');
const mk = arr => ({ start0:100, closed:arr.map(([pnl, nt]) => ({ pnl, nt })) });
const sR = X.stress(mk([[1, 50], [1, 50]])), sS = X.stress(mk([[0.1, 50], [0.1, 50]])), sF = X.stress(mk([[0.04, 50], [0.04, 50]])), sL = X.stress(mk([[-1, 50]])), sOld = X.stress({ start0:100, closed:[{ pnl:1 }] });
ok(/robust/.test(sR.word) && Math.abs(sR.hard - (102 - 0.3)) < 1e-9 && /sensitive/.test(sS.word) && /fragile/.test(sF.word) && /losing/.test(sL.word) && sOld.n === 0 && sOld.skipped === 1, 'fill stress: robust, sensitive, fragile and losing are told apart; older trades without a size are skipped, not guessed', { sR, sS:sS.word, sF:sF.word });
new Function(grab('RISK GUARD AND GROWTH BOT'))(); const G = window.OMEGA_RGUARD._; let A = G.newAcct(100); A = G.step(A, [], NOW); A = G.step(A, [{ key:'d|BTC|1', src:'plan', sym:'BTCUSDT', side:'long', closed:false, stopPct:0.01 }], NOW + 1);
A = G.step(A, [{ key:'d|BTC|1', src:'plan', sym:'BTCUSDT', side:'long', closed:true, R:1 }], NOW + 2);
ok(A.closed.length === 1 && A.closed[0].nt === 50 && Math.abs(A.eq - 100.5) < 1e-9, 'the Growth Bot keeps each closed trade’s size (50 USDT here); its result is unchanged (+0.50)', A.closed[0]);
(async () => {
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(2500);
  const a = await pg.evaluate(() => (document.getElementById('truthBody') || {}).innerText || '');
  await pg.evaluate(() => navigate('rguard')); await pg.waitForTimeout(2500); const g = await pg.evaluate(() => (document.getElementById('truthRgBody') || {}).innerText || '');
  const t = await pg.evaluate(async () => { await window.OMEGA_OPERATOR.tick('truth'); return { res:(window.OMEGA_OPERATOR.state().jobs.truth || {}).result, wide:document.documentElement.scrollWidth > window.innerWidth }; });
  ok(/Data check/i.test(a) && /Autopilot jobs fresh/.test(a) && /Is the bot worth it/i.test(g) && /problem|live and consistent/.test(t.res || '') && !/\bNaN\b|\bundefined\b/.test(a + g) && !t.wide && errs.length === 0, 'in the browser: the Data check on Analysis, “Is the bot worth it?” on Risk Guard, the Autopilot job runs; no NaN, no overflow, no page errors', { a:a.slice(0, 160), g:g.slice(0, 100), t, errs });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
