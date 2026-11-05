// v6.5.106: E34 shown wherever the funding harvest was still called a pass; stale "next ideas" and "risk-free" wording fixed;
// one pinned Brain correction; CREED's engine unchanged (PREV=<older build>).
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const prev = process.env.PREV && fs.readFileSync(process.env.PREV, 'utf8');
if(prev){ const k = s => s.slice(s.indexOf('function analyseSeries('), s.indexOf('function analyseSeries(') + 60000); ok(k(prev) === k(html) && /function walkExit[\s\S]{0,2000}/.exec(prev)[0] === /function walkExit[\s\S]{0,2000}/.exec(html)[0], 'CREED’s engine (analyseSeries + 60,000 characters, walkExit) is byte-identical to the previous build'); }
ok(/v6\.5\.(1\d\d) · build/.test(html) && !/v6\.5\.10[0-5] · build/.test(html), 'build v6.5.106 or later');
ok(!html.includes('the rule that passed its untouched test') && !html.includes("WAIT:['Paper · passed its untouched test") && !html.includes('being paid for supplying leverage is.'), 'no text left that calls the funding harvest a current pass');
ok(!/(now|remainder) risk-free/.test(html.replace(/\/\/[^\n]*/g, '')), 'no user-facing claim that a breakeven stop makes a trade risk-free (code comments excluded)');
ok(!html.includes('Next ideas not yet run: BTC/ETH timing') && html.includes('on-chain flows and options data'), 'research card footer lists only ideas not yet tested');
ok(html.split('E34 CORRECTION NOTE').length === 2 && html.split('id="harvestE34"').length === 2 && html.split('id="r12E34"').length === 2, 'each new piece appears once');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4500); await pg.evaluate(() => navigate('ostrat')); await pg.waitForTimeout(3000);
  const t = await pg.evaluate(() => ({ h:(document.getElementById('harvestCard') || {}).innerText || '', r:(document.getElementById('r12Card') || {}).innerText || '', page:(document.getElementById('page-ostrat') || {}).innerText || '' }));
  ok(/FAILED on 2025–26 \(E34\)/i.test(t.h) && /−17% a year/.test(t.h) && /do not trade it/.test(t.h) && !/NaN|undefined/.test(t.h), 'Strategy: the harvest card heads with E34’s failure', t.h.slice(0, 300));
  ok(/its harvest half failed E34/.test(t.r) && /Half of each winner is the funding harvest/.test(t.r), 'Strategy: the Round 12 card says its harvest half failed E34', t.r.slice(0, 300));
  const jobs = await pg.evaluate(() => { const O = window.OMEGA_OPERATOR; return O && O.jobs ? O.jobs().map(j => j.id + '|' + j.label) : []; });
  const hj = jobs.filter(j => /^harvest\|/.test(j)), ids = jobs.map(j => j.split('|')[0]);
  ok(hj.length === 1 && /failed E34/.test(hj[0]) && ids.length === new Set(ids).size, 'Autopilot: one harvest job, labelled as failed E34; no duplicate job ids', jobs);
  const obs = await pg.evaluate(() => (window.OMEGA_BRAIN.observationsFor('omega', '1w') || []).filter(o => /^Correction \(E34/.test(o.text)).length);
  await pg.reload(); await pg.waitForTimeout(4500);
  const obs2 = await pg.evaluate(() => (window.OMEGA_BRAIN.observationsFor('omega', '1w') || []).filter(o => /^Correction \(E34/.test(o.text)).length);
  ok(obs === 1 && obs2 === 1, 'Brain: one pinned E34 correction, not repeated on reload', { obs, obs2 });
  const css = await pg.evaluate(() => ({ pb:document.querySelectorAll('#pbCss').length, rare:document.querySelectorAll('#rareCss').length, g:Array.from(document.styleSheets).some(x => { try{ return Array.from(x.cssRules).some(r => /\.pgauge/.test(r.selectorText || '')); }catch(e){ return false; } }) }));
  ok(css.pb === 1 && css.rare === 1 && css.g, 'styles: the panic card and the research card each keep their own <style>; the gauge rules are present', css);
  await pg.evaluate(() => navigate('futures')); await pg.waitForTimeout(1500);
  const fz = await pg.evaluate(() => { const e = document.getElementById('futLevTruth'); return e ? { t:e.innerText, page:e.closest('#page-futures') ? 1 : 0, n:document.querySelectorAll('#futLevTruth').length } : null; });
  ok(fz && fz.page && fz.n === 1 && /76% of 100,000/.test(fz.t) && /56–59%/.test(fz.t) && /1× isolated/.test(fz.t), 'Futures: one leverage evidence card on the Futures page', fz);
  await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(2500); const r = await pg.evaluate(() => (document.getElementById('rareSigBody') || {}).innerText || '');
  ok(/on-chain flows and options data/.test(r) && !/Next ideas not yet run/.test(r) && !errs.length, 'Signals: the research card footer is current; no page errors', { errs });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
