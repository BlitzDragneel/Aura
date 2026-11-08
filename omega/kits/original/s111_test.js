// v6.5.111: Brain page without the research registry/export; the Brain engine still answers the bots and Signals.
// usage: node s111_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, m, x){ if(c){ pass++; console.log('ok   ' + m); } else { fail++; console.log('FAIL ' + m + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 300) : '')); } }
ok(/v6\.5\.1(1[1-9]|[2-9]\d) · build/.test(html), 'build v6.5.111 or later');
ok(!/Hypothesis registry/.test(html) && !/id="rpExport"/.test(html), 'registry and research-package export are gone from the page');
ok(/Prediction scorecard/.test(html) && /Reason about a market/.test(html) && /omega-board\.onrender\.com/.test(html), 'kept sections and the board pointer are present');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue();
    return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500);
  const api = await pg.evaluate(() => { const B = window.OMEGA_BRAIN || {};
    let ev = null, bs = null, rec = null;
    try { ev = B.evaluate({ source:'signals', sysKey:'signals-page', simulated:true, symbol:'BTCUSDT', direction:'long', score:70 }); } catch(e){ ev = 'ERR ' + e; }
    try { bs = B.betSize({ strategy:'smc', tfClass:'4h', rr:2, baseRiskPct:1 }); } catch(e){ bs = 'ERR ' + e; }
    try { rec = B.recommend(); } catch(e){ rec = 'ERR ' + e; }
    return { fns:['evaluate','betSize','recommend','feedObservation','observationsFor'].map(k => typeof B[k]), ev:typeof ev, bs:typeof bs, rec:typeof rec, err:[ev,bs,rec].filter(x => typeof x === 'string') }; });
  ok(api.fns.every(t => t === 'function') && !api.err.length && api.ev === 'object', 'Brain engine answers evaluate / betSize / recommend as before', api);
  await pg.evaluate(() => navigate('brain')); await pg.waitForTimeout(1500);
  await pg.evaluate(() => navigate('signals')); await pg.waitForTimeout(1500);
  await pg.evaluate(() => navigate('bot')); await pg.waitForTimeout(1500);
  ok(!errs.length, 'no page errors on Home, Brain, Signals and Bots', errs);
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
