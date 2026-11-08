// v6.5.102: CREED reality check on the CREED desk; research rows for E29/E31, E30, E32; CREED's engine unchanged.
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const prev = process.env.PREV && fs.readFileSync(process.env.PREV, 'utf8');
if(prev){ const k = s => s.slice(s.indexOf('function analyseSeries('), s.indexOf('function analyseSeries(') + 60000); ok(k(prev) === k(html) && /function walkExit[\s\S]{0,2000}/.exec(prev)[0] === /function walkExit[\s\S]{0,2000}/.exec(html)[0], 'CREED’s engine (analyseSeries and the 60,000 characters after it, walkExit) is byte-identical to the previous build'); }
ok(/v6\.5\.(1\d\d) · build/.test(html) && html.split('CREED REALITY CHECK').length === 2, 'build v6.5.102 or later carries the CREED reality check once');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  for(const vp of [{ width:412, height:915, n:'phone' }, { width:1280, height:900, n:'computer' }]){
    const ctx = await b.newContext({ viewport:{ width:vp.width, height:vp.height } });
    await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('creed')); await pg.waitForTimeout(3000);
    const c = await pg.evaluate(() => { const e = document.getElementById('creedReality'), p = e && e.previousElementSibling; return { t:e ? e.innerText : '', after:p ? p.className : null, svg:!!(e && e.querySelector('svg')), bars:e ? e.querySelectorAll('svg rect').length : 0 }; });
    if(vp.n === 'phone'){ await pg.evaluate(() => document.getElementById('creedReality').scrollIntoView()); await pg.screenshot({ path:'/tmp/v102_creed.png' }); }
    await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(2500); const r = await pg.evaluate(() => (document.getElementById('rareSigBody') || {}).innerText || '');
    const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    ok(/CREED reality check/i.test(c.t) && c.after === 'creed-banner' && c.svg && c.bars === 8 && /49%/.test(c.t) && /−0\.118R on 20 majors/.test(c.t) && /−0\.100R/.test(c.t) && /Moving stops and targets cannot create an edge/.test(c.t) && !/NaN|undefined/.test(c.t),
      vp.n + ': the CREED desk opens with the reality check under its banner: the coin-flip chart (8 bars), the three measured results, what failed and why', { after:c.after, bars:c.bars, t:c.t.slice(0, 160) });
    if(html.indexOf('WHY SIGNALS ARE RARE') > -1) ok(/CREED, fixed and improved \(E29, E31\)/.test(r) && /Real liquidity \(E30\)/.test(r) && /Neural network \(E32\)/.test(r) && /12,480 rules/.test(r) && /Timing BTC and ETH from market-wide gauges/.test(r) && !/9,240/.test(r) && !wide && !errs.length, vp.n + ': research card lists E29/E31, E30 and E32; no overflow, no errors', { wide, errs });
    await ctx.close(); }
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
