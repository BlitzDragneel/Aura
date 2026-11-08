// v6.5.95 checks: the scanner folds unread markets into one compact card; cards with data are unchanged.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-95.html'), html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
ok(/v6\.5\.(9[5-9]|1\d\d) · build/.test(html) && /function card\(sym\)\{\n    var r = results\[sym\];/.test(html), 'version; the card for a market with data is the same function as before');
(async () => {
  const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(2500);
  const r = await pg.evaluate(() => { const g = document.getElementById('wlGrid'); const fd = g && g.closest('details'); if(fd) fd.open = true;   // v6.5.114: the scan is a dropdown
    return { cards:g ? g.querySelectorAll('.wl-card').length : -1, unread:g ? g.querySelectorAll('.wl-unread').length : -1, names:g && g.querySelector('.wl-unread') ? g.querySelector('.wl-unread').querySelectorAll('p span').length : 0, text:g ? g.innerText.slice(0, 80) : '', h:g ? g.getBoundingClientRect().height : 0, wide:document.documentElement.scrollWidth > window.innerWidth }; });
  ok(r.cards === 1 && r.unread === 1 && r.names >= 50 && /not read yet|waiting their turn/.test(r.text) && r.h < 900 && !r.wide && errs.length === 0, 'unread markets fold into one compact card of ' + r.names + ' names (' + Math.round(r.h) + ' px tall instead of a long list); no overflow, no page errors', r);
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
