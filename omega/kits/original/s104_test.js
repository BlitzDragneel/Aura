// v6.5.104: E34 row in the research card.
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
ok(/v6\.5\.(1\d\d) · build/.test(html) && html.split('Funding harvest, delta-neutral (E34)').length === 2, 'build v6.5.104 or later carries the E34 row once');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(2500);
  const r = await pg.evaluate(() => (document.getElementById('rareSigBody') || {}).innerText || ''), wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  ok(/FAILED\s*Forced deleveraging on 60 coins \(E33\)/.test(r) && /−64\.6% in a month/.test(r) && /−17% a year/.test(r) && !wide && !errs.length, 'Signals: the research card lists E34 as failed with its numbers; no overflow, no errors', { wide, errs });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
