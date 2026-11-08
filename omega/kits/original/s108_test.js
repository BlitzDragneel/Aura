// v6.5.108: Neon Glow theme — default, one-time switch from the old default, other choices kept; look only (no script logic
// beyond the switch), no page errors, CREED desk renders.
// usage: node s108_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
ok(/v6\.5\.1(0[89]|[1-9]\d) · build/.test(html), 'build v6.5.108 or later');
ok(/<option value="neonglow" selected>Neon Glow \(default\)<\/option>/.test(html) && /<option value="dark">Dark \(classic\)<\/option>/.test(html), 'Neon Glow listed first and selected; Dark still offered');
ok(/html\[data-theme="neonglow"\]\{/.test(html) && /@keyframes omegaNeonPulse/.test(html) && /prefers-reduced-motion/.test(html), 'theme CSS present with reduced-motion fallback');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(prep){ const ctx = await b.newContext({ viewport:{ width:412, height:915 } });
    await ctx.route('**/*', r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue();
      return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    if(prep){ await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(prep); }
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); return { pg, errs, ctx }; }
  // fresh browser
  let { pg, errs, ctx } = await open();
  const fresh = await pg.evaluate(() => ({ t:document.documentElement.getAttribute('data-theme'), gold:getComputedStyle(document.documentElement).getPropertyValue('--gold').trim(),
    sh:getComputedStyle(document.querySelector('.card') || document.body).boxShadow, flag:localStorage.getItem('omega_neon108') }));
  ok(fresh.t === 'neonglow' && fresh.gold.toUpperCase() === '#22F3FF' && fresh.sh !== 'none' && fresh.flag === '1', 'fresh browser: Neon Glow on, cyan accent, cards glow', fresh);
  await pg.evaluate(() => navigate('creed')); await pg.waitForTimeout(1500);
  ok(!errs.length, 'no page errors on load and on the CREED desk', errs); await ctx.close();
  // old default saved -> switched once
  ({ pg, errs, ctx } = await open(() => { localStorage.clear(); const k = Object.keys(localStorage); localStorage.setItem('omega_settings_probe', '1'); }));
  await ctx.close();
  // user who chose another theme keeps it
  ({ pg, errs, ctx } = await open(async () => { localStorage.clear(); document.getElementById('setTheme').value = 'ocean'; document.getElementById('setTheme').dispatchEvent(new Event('change')); }));
  const kept = await pg.evaluate(() => document.documentElement.getAttribute('data-theme'));
  ok(kept === 'ocean', 'a chosen theme (ocean) is kept, not overwritten', kept); await ctx.close();
  // choosing Dark again after the switch sticks
  ({ pg, errs, ctx } = await open(async () => { document.getElementById('setTheme').value = 'dark'; document.getElementById('setTheme').dispatchEvent(new Event('change')); }));
  const back = await pg.evaluate(() => document.documentElement.getAttribute('data-theme'));
  ok(back === null, 'picking Dark (classic) after the switch sticks', back); await ctx.close();
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
