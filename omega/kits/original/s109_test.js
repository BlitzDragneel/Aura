// v6.5.109: clean-up. Research pages, modules, jobs and the 1.06 MB seed are gone; the kept app works, opens on Home, has the
// new menu and bottom bar, and the Signals page carries climax (A), panic bounce (B), the Daily Plan (C) and the Evidence note.
// usage: [PREV=<v6.5.108 build>] node s109_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const REMOVED = ['lab', 'edgelab', 'watch', 'mprof', 'bdesk', 'ostrat', 'ostratscan', 'ostratbt', 'simulation', 'mind', 'score'];
const KEPT = ['command', 'radar', 'flow', 'intel', 'rguard', 'mread', 'osig', 'posdesk', 'futures', 'auto', 'brain', 'analysis', 'journal', 'growth', 'bot', 'creed', 'settings'];
const GONE_JOBS = ['deep', 'creed', 'patterns', 'topup', 'lab', 'edge', 'context', 'entry', 'forecast', 'reflect', 'council', 'backtests', 'explore', 'portfolio', 'workshop',
  'harvest', 'r12', 'btctrend', 'wide', 'edgelab', 'bdesk', 'mprof', 'mwatch', 'mwdays', 'goldh', 'autoexp'];
const KEPT_JOBS = ['intel', 'scanner', 'positioning', 'live', 'journal', 'reason', 'desk', 'analysis', 'bots', 'health', 'panic', 'climax', 'mread', 'dplan', 'rguard', 'cockpit', 'truth'];
ok(/v6\.5\.1(09|[1-9]\d) · build/.test(html), 'build v6.5.109 or later');
ok(Buffer.byteLength(html) < 2.8e6, 'the app lost real weight: under 2.8 MB (v6.5.108 was 4.57 MB)', Buffer.byteLength(html));
ok(!/OMEGA_SEED_B64|window\.OMEGA_EDGELAB =|window\.OMEGA_WATCH =|window\.OMEGA_MPROF =|window\.OMEGA_BDESK =|window\.OMEGA_STRATEGY =|window\.OMEGA_XSMODEL =|window\.OMEGA_SCORE =/.test(html), 'seed and research modules removed from the file');
ok(REMOVED.every(p => html.indexOf('id="page-' + p + '"') < 0 && html.indexOf('data-page="' + p + '"') < 0), 'no markup or menu entry for a removed page');
const prev = process.env.PREV && fs.readFileSync(process.env.PREV, 'utf8');
if(prev){ const k = s => s.slice(s.indexOf('function analyseSeries('), s.indexOf('function analyseSeries(') + 60000);
  const mod = s => { const i = s.indexOf('// OMEGA v6.5 — CREED / ACCEPTANCE STRATEGY MODULE'); return s.slice(i, s.indexOf('</script>', i)); };
  ok(k(prev) === k(html) && mod(prev) === mod(html), 'CREED’s engine and its whole module are byte-identical to the previous build'); }
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  const ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(() => { localStorage.setItem('omega_active_page', 'creed'); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); });
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(6000);
  const home = await pg.evaluate(() => ({ act:Array.from(document.querySelectorAll('.page.active')).map(e => e.id), nav:Array.from(document.querySelectorAll('.omega-bottomnav button span')).map(s => s.textContent),
    menu:Array.from(document.querySelectorAll('.sidebar-menu li[data-page]')).filter(li => li.style.display !== 'none').map(li => li.getAttribute('data-page')),
    jobs:(window.OMEGA_OPERATOR && window.OMEGA_OPERATOR.jobs ? window.OMEGA_OPERATOR.jobs().map(j => j.id) : []),
    st:window.OMEGA_SELFTEST ? window.OMEGA_SELFTEST.run().filter(x => x.status === 'fail').map(x => x.name) : ['no self-test'] }));
  ok(home.act.length === 1 && home.act[0] === 'page-command', 'opens on Home even when the last page was CREED', home.act);
  const wantNav = ['Home', 'Charts', 'Signals', 'CREED', 'Bots'].concat(html.indexOf('id="page-academy"') > -1 ? ['Academy'] : []).concat(['More']);
  ok(JSON.stringify(home.nav) === JSON.stringify(wantNav), 'bottom bar: ' + wantNav.join(' / '), home.nav);
  ok(KEPT.every(p => home.menu.indexOf(p) > -1) && home.menu.every(p => REMOVED.indexOf(p) < 0), 'menu lists every kept page and no removed one', home.menu);
  ok(GONE_JOBS.every(j => home.jobs.indexOf(j) < 0) && KEPT_JOBS.every(j => home.jobs.indexOf(j) > -1), 'Autopilot: research jobs gone, kept jobs present', home.jobs);
  ok(!home.st.length, 'self-test has no failures', home.st);
  await pg.evaluate(() => navigate('lab')); await pg.waitForTimeout(400);
  ok(await pg.evaluate(() => document.getElementById('page-command').classList.contains('active')), 'a link to a removed page lands on Home');
  await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(3000);
  const sig = await pg.evaluate(() => ({ t:document.getElementById('page-osig').innerText, a:Array.from(document.querySelectorAll('#osigEvidence a')).map(a => a.href),
    hosts:['climaxSigBody', 'panicSigBody', 'dplanSigBody'].map(id => !!document.getElementById(id)), lab:!!document.getElementById('osigActive') }));
  ok(sig.hosts.every(Boolean) && /grade C/.test(sig.t) && /Evidence — what passed and what failed/i.test(sig.t) && sig.a.some(h => /^https:\/\/omega-board\.onrender\.com/.test(h)) && !sig.lab,
    'Signals: climax, panic bounce, Daily Plan (grade C) and the Evidence note with the board link; the Lab lists are gone', { hosts:sig.hosts, a:sig.a });
  for(const p of KEPT){ await pg.evaluate(x => navigate(x), p); await pg.waitForTimeout(700); }
  const fut = await pg.evaluate(() => ({ lev:!!document.getElementById('futLevTruth'), lab:!!document.getElementById('futRunLab'), acct:!!document.getElementById('perpAccount') }));
  ok(fut.lev && fut.acct && !fut.lab, 'Futures keeps the leverage warning and paper account, without research buttons', fut);
  ok(!errs.length, 'no page errors on load and on every kept page', errs);
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
