// v6.5.85 checks: Market Profiles (plan E5 figures, six markets, clock, sizing, forward record of plan E6), the gold card on plan E4.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-85.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}), visibilityState:'visible' }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
new Function(grab('MARKET PROFILES'))(); const M = window.OMEGA_MPROF, X = M._;
const E5 = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/E5_dossiers.json'), 'utf8'));
(async () => {
  ok(/v6\.5\.(8[5-9]|9[0-9]|1\d\d) · build/.test(html) && html.includes('id="page-mprof"') && html.includes('data-page="mprof"') && /var EXTRA = \[[^\]]*'mprof'/.test(html) && html.includes("['mprof','Market Profiles']") && html.includes("window.OMEGA_MPROF.onShow()") && ["{ round:'21',", "{ round:'22',", "{ round:'23',"].every(r => html.includes(r)) && /Research record, rounds 1\\u2013(2[3-9]|3[0-9]) \\u2014/.test(html), 'version, page, menu, navigation, palette, research record rounds 21–23');
  ok(M.ORDER.length >= 6 && ['XAUUSD','DOGEUSDT','LINKUSDT','LTCUSDT','ADAUSDT','AVAXUSDT'].every(s => M.ORDER.includes(s)) && M.ORDER.every(s => M.DATA[s] && M.DATA[s].hour_move_bps.length === 24 && Object.keys(M.DATA[s].sessions).length === 4 && M.TEXT[s] && M.TEXT[s].drivers.length >= 3), 'six markets, each with 24 hours, 4 sessions, drivers and guidance');
  const same = ['XAUUSD','DOGEUSDT','LINKUSDT','LTCUSDT','ADAUSDT','AVAXUSDT'].every(s => JSON.stringify(M.DATA[s].hour_drift_bps) === JSON.stringify(E5[s].hour_drift_bps) && M.DATA[s].sessions.US.perYear === E5[s].sessions.US.perYear && M.DATA[s].strategy.passed === E5[s].strategy.passed && M.DATA[s].strategy.pick === E5[s].strategy.pick);
  ok(same && M.DATA.AVAXUSDT.sessions.US.perYear === -62.4 && M.DATA.XAUUSD.sessions.Late.yearsUp === 7 && M.ORDER.every(s => M.DATA[s].strategy.passed === false), 'every figure equals plan E5’s results file; no market passed');
  // each profile renders cleanly, with its clock
  let bad = []; for(const s of M.ORDER){ store.omega_mprof_cfg_v1 = JSON.stringify({ sel:s, acct:100, risk:1 }); const h = X.profile(s); if(/NaN|undefined|Infinity/.test(h) || (h.match(/data-hour="/g) || []).length !== 24 || !/FAILED/.test(h) || !/What moves it/.test(h)) bad.push(s); }
  ok(!bad.length, 'all six profiles render with a 24-hour clock, the tested-rule table marked FAILED, drivers, and no NaN', bad);
  store.omega_mprof_cfg_v1 = JSON.stringify({ sel:'XAUUSD', acct:100, risk:1 }); const g = X.profile('XAUUSD'), stop = 2*M.DATA.XAUUSD.atr_h_pct_recent, pos = 1/(stop/100);
  ok(g.includes(pos.toFixed(2) + ' USDT') && g.includes(stop.toFixed(2) + '%'), 'sizing: 1% of 100 USDT with a 2-range stop (' + stop.toFixed(2) + '%) → ' + pos.toFixed(2) + ' USDT');
  store.omega_mprof_cfg_v1 = JSON.stringify({ sel:'XAUUSD', acct:10, risk:0.1 }); ok(/Below Binance’s 5 USDT minimum order/.test(X.profile('XAUUSD')), 'a position below the 5 USDT minimum is flagged with the risk the minimum would force');
  // plan E6 record: synthetic hours, outside US +0.0005 each, US hours −0.001 each
  const now = Date.UTC(2026, 9, 25, 5, 30), realNow = Date.now; Date.now = () => now; let p = 100, kl = [];
  for(let h = Date.UTC(2026, 9, 15)/H; h < Math.floor(now/H) + 1; h++){ const hh = h % 24, r = (hh >= 13 && hh <= 20) ? -0.001 : 0.0005; const o = p; p = p*Math.exp(r); kl.push([h*H, String(o), String(Math.max(o, p)*1.0005), String(Math.min(o, p)*0.9995), String(p)]); }
  const dg = X.digest('DOGEUSDT', kl); Date.now = realNow; const days = JSON.parse(store.omega_mprof_e6_v1).days.DOGEUSDT, ks = Object.keys(days).map(Number).sort();
  const d21 = Date.UTC(2026, 9, 21)/864e5, okDays = JSON.stringify(ks) === JSON.stringify([d21, d21 + 1, d21 + 2, d21 + 3]), okSums = ks.every(k => Math.abs(days[k][0] - 16*0.0005) < 1e-9 && Math.abs(days[k][1] + 8*0.001) < 1e-9 && days[k][2] === 16 && days[k][3] === 8);
  ok(okDays && okSums && dg && isFinite(dg.price) && isFinite(dg.atrPct) && isFinite(dg.chg24), 'plan E6 record: whole UTC days from 21 Oct only (not the day in progress), outside and US-hours sums exact', { ks, first:days[ks[0]] });
  const e = X.e6('DOGEUSDT'); ok(e.days === 4 && e.weeks <= 1 && /of 26 weeks/.test(X.profile('DOGEUSDT')), 'the record says how many of 26 weeks it has; nothing judged early');
  ok(/plans? E4/.test(grab('GOLD HOURLY HISTORY')) && /continues gold back from where it stopped, then fetches silver|fetches the five forex majors for plan E15/.test(grab('GOLD HOURLY HISTORY')), 'the gold card now serves plan E4 (older gold, then silver)');
  // browser
  global.setTimeout = realST; global.setInterval = realSI; let pw = null; try{ pw = require('playwright'); }catch(e){}
  if(!pw){ ok(false, 'playwright not found'); }
  else { const b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } }); const base = { XAUUSDT:4100, DOGEUSDT:0.21, LINKUSDT:17, LTCUSDT:95, ADAUSDT:0.7, AVAXUSDT:25 }; let calls = 0;
    await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const q = u.searchParams, j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
      if(/binance/.test(u.hostname) && /klines$/.test(u.pathname) && base[q.get('symbol')] && q.get('limit') === '1000'){ calls++; const s = q.get('symbol'), end = Math.floor(Date.now()/H), out = []; let pr = base[s];
        for(let h = end - 999; h <= end; h++){ const o = pr; pr = pr*(1 + 0.002*Math.sin(h*0.37)); out.push([h*H, String(o), String(Math.max(o, pr)*1.001), String(Math.min(o, pr)*0.999), String(pr), '1000', h*H + H - 1]); } return j(out); }
      if(/binance|twelvedata/.test(u.hostname)) return j([]); return route.abort(); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('mprof')); await pg.waitForTimeout(3000);
    const r1 = await pg.evaluate(() => ({ live:Object.keys(window.OMEGA_MPROF.state().live).length, text:document.getElementById('page-mprof').innerText, bars:document.querySelectorAll('#page-mprof svg.mp-clock rect[data-hour]').length }));
    await pg.click('[data-mpsel="AVAXUSDT"]'); await pg.waitForTimeout(400);
    const r2 = await pg.evaluate(() => ({ text:document.getElementById('page-mprof').innerText, wide:document.documentElement.scrollWidth > window.innerWidth }));
    ok(calls === 6 && r1.live === 6 && r1.bars === 24 && /Start here/.test(r1.text) && /Gold \(XAU\/USD\)/.test(r1.text) && /Avalanche \(AVAX\)/.test(r2.text) && /FAILED/.test(r2.text), 'in the browser: live prices for all six, the clock, switching markets', { calls, live:r1.live, bars:r1.bars });
    ok(!/\bNaN\b|\bundefined\b|\bInfinity\b/.test(r1.text + r2.text) && !r2.wide && errs.length === 0, 'no NaN, no sideways overflow, no page errors', { errs, wide:r2.wide });
    await pg.screenshot({ path:'/tmp/mprof85.png', fullPage:true }); await b.close(); }
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
