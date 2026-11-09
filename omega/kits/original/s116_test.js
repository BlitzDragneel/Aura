// v6.5.116: one self-running Autopilot. The job runner is the only scheduler (OMEGA_AUTOPILOT has no timer of its own and
// runs as job "paper"); retired research jobs are gone from the runner and its state while their stored data stays; new jobs
// (fxboard, botsfeed, scouts, academy, connections) run; first launch switches it on, a reload keeps the choice; heavy jobs
// wait on battery; the status card shows jobs, last/next run, problems with a fix, the setup check and the honest note.
// usage: HARNESS=tools node s116_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
ok(/v6\.5\.1(1[6-9]|[2-9]\d) · build/.test(html), 'build v6.5.116 or later');
ok(/function start\(\)\{ if\(timer \|\| window\.OMEGA_OPERATOR\) return;/.test(html) && !/setInterval\(tick, 20000\); setInterval\(tickFeed, 120000\)/.test(html) && !/try\{ reflect\(\); \}catch\(e\)\{\} \}, 3600e3\)/.test(html), 'no second scheduler: the Autopilot core, the Forex board, the bots feed and the reflection have no timers of their own');
const RETIRED = ['deep', 'creed', 'patterns', 'topup', 'lab', 'edge', 'context', 'entry', 'council'];
const NEED = ['intel', 'scanner', 'positioning', 'live', 'journal', 'reason', 'desk', 'analysis', 'bots', 'health', 'panic', 'climax', 'mread', 'dplan', 'rguard', 'cockpit', 'truth', 'forecast', 'reflect', 'paper', 'fxboard', 'botsfeed', 'scouts', 'academy', 'connections'];
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(prep, init){ const ctx = await b.newContext({ viewport:{ width:412, height:915 } }); if(init) await ctx.addInitScript(init);
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue(); if(M.handle(r)) return;
      if(/okx\.com/.test(u.hostname)) return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'{"code":"0","data":[{"ts":"1"}]}' });
      if(/binance/.test(u.hostname) && /ping/.test(u.pathname) && global.BINANCE_DOWN) return r.abort();
      return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(p => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); if(p) Object.keys(p).forEach(k => localStorage.setItem(k, p[k])); }, prep || null);
    await pg.goto('file://' + path.resolve(FILE)); return { ctx, pg, errs }; }
  // 1. first launch, with the token and old research state from an earlier version
  global.BINANCE_DOWN = true;
  let { ctx, pg, errs } = await open({ omega_live_token:M.TOKEN, omega_operator_v1:JSON.stringify({ jobs:{ lab:{ last:1, result:'old' }, deep:{ last:1 }, intel:{ last:0 } }, choose:true }), omega_lab_results_v1:'{"keep":1}' });
  await pg.waitForTimeout(25000);
  const r = await pg.evaluate(() => { const O = window.OMEGA_OPERATOR, st = O.state(); return { on:O.on(), ids:O.jobs().map(j => j.id), st:Object.keys(st.jobs), res:Object.fromEntries(Object.entries(st.jobs).map(([k, v]) => [k, String(v.result || '')])),
    lab:localStorage.getItem('omega_lab_results_v1'), flag:!!localStorage.getItem('omega_selfrun116'), conn:window.OMEGA_SELFRUN.state().conn, cj:JSON.stringify(window.OMEGA_SELFRUN.state().conn || {}), card:document.getElementById('selfRunHome').innerText }; });
  ok(r.on && r.flag, 'first launch: the Autopilot switched itself on (once)', { on:r.on });
  ok(NEED.every(id => r.ids.includes(id)) && RETIRED.every(id => !r.ids.includes(id)), 'one runner: kept jobs, forecast and reflect for the Brain, the paper core, and the new Live API jobs; retired research jobs gone', r.ids);
  ok(!r.st.includes('lab') && !r.st.includes('deep') && r.lab === '{"keep":1}', 'retired jobs leave the runner’s state; the stored research results stay untouched', r.st);
  ok(/Quotes for 7 majors/.test(r.res.fxboard) && /Paper bot: 2 open/.test(r.res.botsfeed) && r.conn && r.conn.server && r.conn.tokenOk && !r.conn.binance && r.conn.okx && r.conn.forex === 'liveapi',
    'new jobs ran: Forex quotes, bots feed, connections check (Live API up, token accepted, Binance down -> OKX, forex via the Live API)', { fx:r.res.fxboard, bf:r.res.botsfeed, c:r.cj });
  ok(/OMEGA is running itself/.test(r.card) && /\d+ of \d+\s*jobs on/.test(r.card) && /switched to OKX automatically/.test(r.card) && /works only while it is open/.test(r.card) && /laptop Station and the cloud bots/.test(r.card),
    'Home card: running itself, jobs on, last/next run, the OKX fallback said plainly, the honest note about 24/7', r.card.slice(0, 500));
  ok(/Setup check/i.test(r.card) && /Server reachable\s*✓ done/.test(r.card) && /Live API token\s*✓ done/.test(r.card) && /Installed as an app\s*Install/.test(r.card), 'setup check: server and token done by themselves; install offered', r.card);
  await pg.evaluate(() => navigate('auto')); await pg.waitForTimeout(800);
  ok(await pg.evaluate(() => /OMEGA is running itself/.test(document.getElementById('selfRunAuto').innerText)), 'the same card leads the Autopilot page');
  // a reload keeps it running; switching off is respected
  await pg.reload(); await pg.waitForTimeout(3000);
  ok(await pg.evaluate(() => window.OMEGA_OPERATOR.on()), 'after a reload (or a crash) the Autopilot is back on by itself');
  await pg.evaluate(() => { navigate('command'); window.OMEGA_SELFRUN.act('off'); }); await pg.reload(); await pg.waitForTimeout(3000);
  const off = await pg.evaluate(() => ({ on:window.OMEGA_OPERATOR.on(), card:document.getElementById('selfRunHome').innerText }));
  ok(!off.on && /OMEGA is paused/.test(off.card) && /The Autopilot is off/.test(off.card), 'switched off stays off across a reload, and the card offers the one-tap fix', off.card.slice(0, 200));
  ok(!errs.length, 'no page errors', errs); await ctx.close();
  // 2. no token, on battery: the problems say what to do; heavy jobs wait
  global.BINANCE_DOWN = false;
  ({ ctx, pg, errs } = await open(null, () => { navigator.getBattery = () => Promise.resolve({ charging:false, level:0.4 }); }));
  await pg.waitForTimeout(9000);
  const n = await pg.evaluate(() => ({ heavy:window.OMEGA_SELFRUN.heavyOk(), why:window.OMEGA_SELFRUN.heavyWhy(), card:document.getElementById('selfRunHome').innerText, fx:(window.OMEGA_OPERATOR.state().jobs.fxboard || {}).result || '' }));
  ok(!n.heavy && /battery/.test(n.why) && /Heavy jobs .* wait: on battery/.test(n.card), 'on battery: heavy jobs wait, and the card says so', n);
  ok(/No Live API token/.test(n.card) && /Open Settings/.test(n.card) && (!n.fx || /Waiting: no Live API token/.test(n.fx)), 'no token: the card says what is missing with "Open Settings"; the Forex job waits instead of failing', n.card.slice(0, 300));
  await pg.click('#selfRunHome [data-srf="settings"]'); await pg.waitForTimeout(400);
  ok(await pg.evaluate(() => document.getElementById('page-settings').classList.contains('active') && document.getElementById('setData').classList.contains('active')), 'the fix opens Settings > Data & Keys');
  ok(!errs.length, 'no page errors (no token)', errs); await ctx.close();
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
