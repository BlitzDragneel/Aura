// v6.5.100 check: "Why signals are rare" — the research record E22–E28 on the Signals and Edge Lab pages.
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
ok(/v6\.5\.(1\d\d) · build/.test(html) && html.split('WHY SIGNALS ARE RARE').length === 2, 'build v6.5.100 or later carries the research-record card once');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  for(const vp of [{ width:412, height:915, n:'phone' }, { width:1280, height:900, n:'computer' }]){
    const ctx = await b.newContext({ viewport:{ width:vp.width, height:vp.height } });
    await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); const got = {};
    for(const [p, id, after] of [['osig', 'rareSigBody', 'panicSigBody'], ['edgelab', 'rareBody', 'panicBody']]){ await pg.evaluate(p => navigate(p), p); await pg.waitForTimeout(2500);
      got[p] = await pg.evaluate(([id, after]) => { const e = document.getElementById(id); return { t:e ? e.innerText : '', after:e && e.previousElementSibling ? e.previousElementSibling.id : null }; }, [id, after]); }
    if(vp.n === 'phone'){ await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(800); await pg.evaluate(() => document.getElementById('rareSigBody').scrollIntoView()); await pg.screenshot({ path:'/tmp/v100_rare.png' }); }
    const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    ok(Object.values(got).every(x => /Why signals are rare/i.test(x.t) && /12,480/.test(x.t) && /Timing BTC and ETH/.test(x.t) && /No rule that trades every day has passed/i.test(x.t) && /t 4\.54/.test(x.t) && /56% and 59%/.test(x.t) && /Hour-of-day/i.test(x.t) && !/\bNaN\b|\bundefined\b/.test(x.t)) && got.osig.after === 'panicSigBody' && got.edgelab.after === 'panicBody' && !wide && !errs.length,
      vp.n + ': the card sits under the panic-bounce card on Signals and Edge Lab with E25, E26 and E28’s results and reasons; no overflow, no errors', { after:[got.osig.after, got.edgelab.after], wide, errs, t:got.osig.t.slice(0, 120) });
    await ctx.close(); }
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
