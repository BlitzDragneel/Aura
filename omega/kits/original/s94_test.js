// v6.5.94 checks: Events ahead from the Market Clock's calendar, the event-risk window, the pre-trade warning (the bot's rules
// untouched), the Monthly review, and both cards in the browser.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-94.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
const mc = grab('MARKET CLOCK'), DATA = JSON.parse(mc.slice(mc.indexOf('var DATA = ') + 11, mc.indexOf(';\n', mc.indexOf('var DATA = '))));
window.OMEGA_MARKETCLOCK = { DATA }; new Function(grab('EVENTS AND MONTHLY REVIEW'))(); const V = window.OMEGA_REVIEW;
const T = s => Date.parse(s), N = V.nextEvents(T('2026-11-10T12:00Z')), r1 = V.eventRisk(T('2026-11-10T12:00Z')), r2 = V.eventRisk(T('2026-11-10T11:00Z')), r3 = V.eventRisk(T('2026-11-10T15:00Z')), r4 = V.eventRisk(T('2026-10-28T18:30Z'));
ok(N[0].kind === 'US inflation (CPI)' && N[0].at === T('2026-11-10T13:30Z') && r1.active && r1.mins === 90 && !r2.active && !r3.active && r4.active && /Fed/.test(r4.ev.kind) && /Do not open new trades/.test(V.riskText(r1)), 'events from the Market Clock’s calendar; the warning runs from 2 hours before to 1 hour after (CPI 10 Nov, Fed 28 Oct)', { first:N[0], r1, r2:r2.active, r3:r3.active });
const H = 3600e3, oct = T('2026-10-25T10:00Z'), nov = T('2026-11-05T10:00Z');
const rows = V._.review({ start0:100, closed:[{ at:oct, pnl:1 }, { at:oct + H, pnl:-0.5 }, { at:nov, pnl:2 }] }, { trades:[{ h:Math.floor(oct/H), R:2 }, { h:Math.floor(nov/H), R:-1 }] }, { closed:[{ at:nov, pnl:-3, breach:true }, { at:nov, pnl:1, breach:false }] });
const n = rows.find(r => r.month === '2026-11'), o = rows.find(r => r.month === '2026-10');
ok(rows[0].month === '2026-11' && o.bot.n === 2 && Math.abs(o.bot.pnl - 0.5) < 1e-9 && Math.abs(o.bot.eq - 100.5) < 1e-9 && Math.abs(n.bot.eq - 102.5) < 1e-9 && n.plan.R === -1 && n.mine.breaks === 1 && n.mine.breakPnl === -3 && /rule breaks cost \$3\.00/.test(V._.verdictLine(n)) && /kept every rule/.test(V._.verdictLine({ bot:{ n:0 }, plan:{ n:0 }, mine:{ n:1, breaks:0 } })), 'monthly review: per-month bot result and end equity, Daily Plan R, your trades with what rule breaks cost', rows);
const rg = grab('RISK GUARD AND GROWTH BOT'), stepSrc = rg.slice(rg.indexOf('function step('), rg.indexOf('function stats('));
global.window = Object.assign(global.window, { OMEGA_REVIEW:V }); new Function(rg)(); const X = window.OMEGA_RGUARD._, pc = X.preCheck(X.newAcct(100), 100, 98, 20, T('2026-11-10T12:30Z')), pc2 = X.preCheck(X.newAcct(100), 100, 98, 20, T('2026-11-12T12:30Z'));
ok(pc.ok && /Event risk: US inflation/.test(pc.msgs.join(' ')) && !/Event risk/.test(pc2.msgs.join(' ')) && !/OMEGA_REVIEW|eventRisk/.test(stepSrc), 'the pre-trade check warns inside the event window (and not outside it); the Growth Bot’s rules do not look at events (plan E17 unchanged)', pc.msgs);
(async () => {
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(1500);
  const a = await pg.evaluate(() => (document.getElementById('evAnaBody') || {}).innerText || '');
  await pg.evaluate(() => navigate('rguard')); await pg.waitForTimeout(1200); const rv = await pg.evaluate(() => ({ t:(document.getElementById('reviewBody') || {}).innerText || '', wide:document.documentElement.scrollWidth > window.innerWidth }));
  ok(/Events ahead/i.test(a) && /(US inflation|Fed decision)/.test(a) && /Tobago/.test(a) && /Monthly review/i.test(rv.t) && !/\bNaN\b|\bundefined\b/.test(a + rv.t) && !rv.wide && errs.length === 0, 'in the browser: Events ahead on the Analysis page (UTC and Tobago times) and the Monthly review on the Risk Guard page; no NaN, no overflow, no page errors', { errs, a:a.slice(0, 160), rv:rv.t.slice(0, 120) });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
