// v6.5.99 check: plan E26's result in the panic-bounce card, in the browser.
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
ok(/v6\.5\.(99|1\d\d) · build/.test(html) && !/Plan E26 tests exactly that/.test(html), 'build v6.5.99 or later; the old “E26 tests exactly that” line is gone');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(3000);
  const t = await pg.evaluate(() => (document.getElementById('panicSigBody') || {}).innerText || '');
  ok(/E26/.test(t) && /FAILED/.test(t) && /56% and 59%/.test(t) && /4 of 6 years/.test(t) && /Keep it on paper/.test(t) && errs.length === 0, 'Signals: the card reports E26 failed (56% and 59% drawdowns, 4 of 6 years) and says keep it on paper; no page errors', { t:t.slice(0, 300), errs });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
