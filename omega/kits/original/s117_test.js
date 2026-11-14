// v6.5.117: the Brain's betSize gives 0x to a negative-edge cell (never a positive floor); positive edges keep [0.25x, 2x].
// usage: node s117_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, m, x){ if(c){ pass++; console.log('ok   ' + m); } else { fail++; console.log('FAIL ' + m + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 300) : '')); } }
ok(/v6\.5\.1(1[7-9]|[2-9]\d) · build/.test(html), 'build v6.5.117 or later');
ok(!/kellyMult = fStar <= 0 \? 0\.25/.test(html) && /kellyMult = fStar <= 0 \? 0 :/.test(html), 'negative Kelly no longer floored at 0.25x');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext();
  await ctx.route('**/*', r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue();
    return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500);
  // build two journals: one losing, one winning (Brain pools read the journal store)
  const r = await pg.evaluate(() => {
    const B = window.OMEGA_BRAIN; const keys = Object.keys(localStorage).filter(k => /journal/i.test(k));
    function mk(n, wins){ const rows = []; for(let i = 0; i < n; i++) rows.push({ id:'t'+i, result: i < wins ? 'Win' : 'Loss', strategy:'smc', tf:'4h', simulated:false, ts: Date.now() - i*3600e3 }); return rows; }
    const out = {};
    // call with a crafted pool by temporarily wrapping the journal reader if exposed; otherwise use the public API on defaults
    const lose = B.betSize({ strategy:'smc', tfClass:'4h', rr:0.2, baseRiskPct:1 });  // payoff 0.2R: Kelly < 0 for any plausible win rate
    const win  = B.betSize({ strategy:'smc', tfClass:'4h', rr:50,  baseRiskPct:1 });  // payoff 50R: Kelly > 0 for any non-trivial win rate
    out.lose = lose; out.win = win; return out; });
  ok(r.lose.negativeEdge === true && r.lose.mult === 0 && /do not trade/.test(r.lose.why), 'negative-edge cell: size 0x and says not to trade it', r.lose);
  ok(r.win.negativeEdge === false && r.win.mult >= 0.25 && r.win.mult <= 2, 'positive-edge cell: size inside [0.25x, 2x]', r.win);
  ok(!errs.length, 'no page errors', errs);
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
