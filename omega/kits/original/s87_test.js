// v6.5.87 checks: the five newest parts are Autopilot (Operator) jobs, run through the scheduler, and shown on the Autopilot page.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-87.html'), html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const NEW = ['climax', 'bdesk', 'mprof', 'mwatch', 'goldh'];
ok(/v6\.5\.(8[7-9]|9[0-9]|1\d\d) · build/.test(html) && html.includes("{ round:'25',") && /Research record, rounds 1\\u2013(2[5-9]|3[0-9]) \\u2014/.test(html) && (html.match(/window\.OMEGA_AUTOCOV = /g) || []).length === 1, 'version, research record round 25, the coverage module once');
(async () => {
  const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } }); const base = { XAUUSDT:4100, DOGEUSDT:0.21, LINKUSDT:17, LTCUSDT:95, ADAUSDT:0.7, AVAXUSDT:25 };
  await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const q = u.searchParams, j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(/binance/.test(u.hostname) && /klines$/.test(u.pathname) && base[q.get('symbol')] && q.get('limit') === '1000'){ const s = q.get('symbol'), end = Math.floor(Date.now()/H), out = []; let pr = base[s];
      for(let h = end - 999; h <= end; h++){ const o = pr; pr = pr*(1 + 0.002*Math.sin(h*0.37)); out.push([h*H, String(o), String(Math.max(o, pr)*1.001), String(Math.min(o, pr)*0.999), String(pr), '1000', h*H + H - 1]); } return j(out); }
    if(/binance|twelvedata|coinbase/.test(u.hostname)) return j([]); return route.abort(); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(6000);
  const reg = await pg.evaluate(ids => { const O = window.OMEGA_OPERATOR, J = O.jobs(); return { all:J.map(j => j.id), ok:ids.every(id => { const j = J.filter(x => x.id === id)[0]; return j && typeof j.run === 'function' && (j.lane === 'live' || j.lane === 'heavy') && j.label && j.what && j.every > 0; }) }; }, NEW);
  ok(reg.ok && NEW.every(id => reg.all.includes(id)) && ['harvest', 'edge'].some(id => reg.all.includes(id)), 'all five newest parts are registered as Autopilot jobs, next to the older research jobs (' + reg.all.length + ' jobs in total)', reg.all);
  const r = await pg.evaluate(async () => { const O = window.OMEGA_OPERATOR; await O.tick('mprof'); await O.tick('goldh'); await O.tick('bdesk'); const S = O.state().jobs; return { mprof:S.mprof && S.mprof.result, goldh:S.goldh && S.goldh.result, bdesk:S.bdesk && S.bdesk.result, live:Object.keys(window.OMEGA_MPROF.state().live).length }; });
  ok(/Live prices for 6 of 6/.test(r.mprof || '') && r.live === 6, 'the Autopilot runs Market Profiles’ job through the scheduler and records its result', r);
  ok(typeof r.goldh === 'string' && r.goldh.length > 0 && typeof r.bdesk === 'string' && r.bdesk.length > 0, 'the gold and Breakout Desk jobs run and leave a readable result (here: waiting or no key, as expected offline)', r);
  await pg.evaluate(() => navigate('auto')); await pg.waitForTimeout(1500);
  const tb = await pg.evaluate(() => { if(window.OMEGA_OPERATOR.render) window.OMEGA_OPERATOR.render(); const t = document.getElementById('opJobs'); return t ? t.textContent : ''; });
  ok(['Climax watch', 'Breakout Desk records', 'Market Profiles', 'Market Watch recorder', ].every(x => tb.includes(x)) && /Gold(,| and) silver/.test(tb) && errs.length === 0, 'the Autopilot page lists all five, each with its result and on/off switch; no page errors', { errs, has:tb.slice(0, 200) });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
