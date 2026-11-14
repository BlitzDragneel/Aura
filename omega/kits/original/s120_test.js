// v6.5.120: Signal Auditor. Page, menu entry, Home line, palette; paste -> /auditor/parse -> saved with the server's logged
// time; Score all -> /auditor/score -> per-signal result (fill, outcome, pips, R), summary per provider, verdict; delete only
// while "waiting for entry"; risk check via /auditor/risk; no token -> says how to connect. Screenshots: SHOTS=<dir>.
// usage: HARNESS=tools [SHOTS=dir] node s120_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
const SHOTS = process.env.SHOTS; if(SHOTS) fs.mkdirSync(SHOTS, { recursive:true });
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 700) : '')); } }
ok(/v6\.5\.1(2\d|[3-9]\d) · build/.test(html), 'build v6.5.120 or later');
ok(html.split('id="page-auditor"').length === 2 && /data-page="auditor"/.test(html) && /'auditor'\];/.test(html), 'one Signal Auditor page, a menu entry, known to the navigator');
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(o){ o = o || {}; const ctx = await b.newContext({ viewport:{ width:o.w || 412, height:o.h || 915 } });
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue();
      if(r.request().method() === 'OPTIONS') return r.fulfill({ status:204, headers:{ 'access-control-allow-origin':'*', 'access-control-allow-headers':'authorization,content-type,accept', 'access-control-allow-methods':'GET,POST' } });
      if(M.handle(r)) return; return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(p => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); if(p) Object.keys(p).forEach(k => localStorage.setItem(k, p[k])); }, o.prep || null);
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000); return { ctx, pg, errs }; }
  const shot = async (pg, n, full) => { if(SHOTS) await pg.screenshot({ path:path.join(SHOTS, n + '.png'), fullPage:!!full }); };
  const body = pg => pg.evaluate(() => document.getElementById('auditorBody').innerText);
  let { ctx, pg, errs } = await open({ prep:{ omega_live_token:M.TOKEN } });
  const home = await pg.evaluate(() => { const p = document.getElementById('page-command'); return { nav:Array.from(document.querySelectorAll('.omega-bottomnav button span')).map(s => s.textContent), line:document.getElementById('homeAuditor').innerText.replace(/\n/g, ' '),
    cards:p.querySelectorAll('details.cmd-card').length, menu:document.querySelectorAll('.sidebar-menu li[data-page="auditor"]').length }; });
  ok(JSON.stringify(home.nav) === JSON.stringify(['Home', 'Charts', 'Signals', 'CREED', 'Bots', 'Academy', 'More']) && home.menu === 1 && home.cards === 8 && /Signal Auditor · check a signal provider against real prices/.test(home.line), 'bottom bar and Home cards unchanged; reachable from Home (a line) and the menu (More)', home);
  await pg.click('#homeAuditor [data-sago]'); await pg.waitForTimeout(600);
  ok(await pg.evaluate(() => document.querySelector('.page.active').id === 'page-auditor'), 'the Home line opens the page');
  // log three signals
  const t0 = Date.now();
  async function log(text, prov){ await pg.fill('#saText', text); await pg.fill('#saProv', prov); await pg.click('[data-saadd]'); await pg.waitForTimeout(700); }
  await log('XAUUSD BUY NOW 4105 SL 4095 TP1 4110 TP2 4120', 'Gold Kings');
  let st = await pg.evaluate(() => ({ s:window.OMEGA_AUDITOR.state().signals, msg:document.getElementById('saMsg').innerText, stored:JSON.parse(localStorage.getItem('omega_auditor_v1')).signals.length }));
  const p1 = M.AUD.filter(a => a.path === '/auditor/parse')[0];
  ok(st.s.length === 1 && st.stored === 1 && st.s[0].symbol === 'XAUUSD' && st.s[0].side === 'buy' && st.s[0].stop === 4095 && st.s[0].logged_ms >= t0 - 1000 && st.s[0].id && p1 && p1.body.provider === 'Gold Kings' && /Logged XAUUSD buy at .* \(server time\)/.test(st.msg),
    'paste -> POST /auditor/parse -> saved on the device with the server’s logged time', { msg:st.msg, s:st.s[0] });
  await log('GOLD SELL NOW SL 4140 TP 4125', 'Gold Kings'); await log('XAUUSD BUY limit 4050 SL 4040 TP1 4070', 'Other Guy'); await log('hello team, big week ahead!', 'Other Guy');
  st = await pg.evaluate(() => ({ n:window.OMEGA_AUDITOR.state().signals.length, msg:document.getElementById('saMsg').innerText, del:document.querySelectorAll('[data-sadel]').length, tags:Array.from(document.querySelectorAll('.sa-sig .sa-st')).map(x => x.innerText.toLowerCase()) }));
  ok(st.n === 3 && /Not logged: could not read a symbol/.test(st.msg) && st.del === 0 && st.tags.every(x => x === 'not scored yet'), 'a message that is not a signal is refused with the reason; nothing can be deleted before scoring', st);
  await pg.click('[data-sascore]'); await pg.waitForTimeout(1200);
  let t = await body(pg); const sc = M.AUD.filter(a => a.path === '/auditor/score').pop();
  ok(sc && sc.body.signals.length === 3 && sc.body.signals.every(x => x.logged_ms && x.symbol && x.side), 'Score all -> POST /auditor/score with every logged signal and its logged time', sc && sc.body.signals.map(x => x.side));
  ok(/Too early: 2 closed signals with a stop\. About 30 are needed/.test(t) && /3 logged · 2 closed/i.test(t) && /−0\.28R|-0\.28R/.test(t) && /50%/.test(t), 'summary: the verdict line, logged/closed, average R and win rate', t.slice(0, 500));
  ok(/By provider/.test(t) && /Gold Kings/.test(t) && /Other Guy/.test(t), 'summary per provider', t.slice(300, 900));
  ok(/Filled .* at 4105\.2 · risk 100\.0 pips/.test(t) && /All at TP1: target 1 · \+47\.0 pips · \+0\.47R/.test(t) && /Ladder: targets · \+80\.0 pips · \+0\.80R/.test(t) && /All at TP1: stop · -103\.0 pips · -1\.03R/.test(t) && /Price has not reached the entry yet/.test(t) && !/NaN|undefined|\[object/.test(t),
    'per signal: fill, outcome, pips and R for both styles; the limit order is still waiting', t.slice(600, 1500));
  const d = await pg.evaluate(() => ({ btn:Array.from(document.querySelectorAll('[data-sadel]')).map(x => x.closest('.sa-sig').innerText.slice(0, 40)), closedId:window.OMEGA_AUDITOR.state().signals.find(x => x.side === 'sell').id }));
  ok(d.btn.length === 1 && /XAUUSD BUY/.test(d.btn[0]) && /Other Guy/.test(d.btn[0]), 'only the signal waiting for its entry has a Delete button', d.btn);
  await shot(pg, 'phone_auditor_scored', true);
  await pg.evaluate(id => window.OMEGA_AUDITOR.del(id), d.closedId); await pg.waitForTimeout(200);
  let n1 = await pg.evaluate(() => ({ n:window.OMEGA_AUDITOR.state().signals.length, msg:document.getElementById('saMsg').innerText }));
  ok(n1.n === 3 && /Only a signal still waiting for its entry can be deleted/.test(n1.msg), 'a closed (losing) signal cannot be deleted, even by code', n1);
  await pg.click('[data-sadel]'); await pg.waitForTimeout(300);
  n1 = await pg.evaluate(() => ({ n:window.OMEGA_AUDITOR.state().signals.length, stored:JSON.parse(localStorage.getItem('omega_auditor_v1')).signals.length }));
  ok(n1.n === 2 && n1.stored === 2, 'the waiting signal can be deleted', n1);
  // risk check
  await pg.fill('#saBal', '100'); await pg.fill('#saLots', '0.05'); await pg.click('[data-sarisk]'); await pg.waitForTimeout(700);
  t = await body(pg); const rk = M.AUD.filter(a => a.path === '/auditor/risk').pop();
  ok(rk && rk.body.balance === 100 && rk.body.positions[0].lots === 0.05 && rk.body.positions[0].symbol === 'XAUUSD' && /costs \$5\.00 \(\$0\.50 a pip\)/.test(t) && /A move of 20 \(200 pips\) against you equals the whole balance of \$100\.00/.test(t) && /typical day move is 40 \(200% of the balance\)/.test(t),
    'risk check: balance + lots -> /auditor/risk -> how far price can move before the balance is gone, with typical moves', t.slice(-500));
  await pg.reload(); await pg.waitForTimeout(3500); await pg.evaluate(() => navigate('auditor')); await pg.waitForTimeout(400);
  t = await body(pg); const hl = await pg.evaluate(() => document.getElementById('homeAuditor').innerText.replace(/\n/g, ' '));
  ok(/2 logged/i.test(t) && /Too early/.test(t) && /\+0\.47R/.test(t) && /2 signal\(s\) logged, 2 closed, average -0\.28R/.test(hl), 'the log, results and verdict survive a reload; Home shows the count', hl);
  const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  ok(!errs.length && !wide, 'phone: no page errors, nothing wider than the screen', { errs, wide });
  await ctx.close();
  ({ ctx, pg, errs } = await open({}));
  await pg.evaluate(() => navigate('auditor')); await pg.waitForTimeout(500); t = await body(pg);
  ok(/Connect the OMEGA Live API to log and score signals/.test(t) && await pg.evaluate(() => document.querySelector('[data-saadd]').disabled), 'no token: says how to connect; logging is disabled', t.slice(0, 200));
  ok(!errs.length, 'no page errors without a token', errs); await ctx.close();
  ({ ctx, pg, errs } = await open({ w:1280, h:900, prep:{ omega_live_token:M.TOKEN } }));
  await pg.evaluate(() => navigate('auditor')); await pg.waitForTimeout(500); await pg.fill('#saText', 'XAUUSD BUY NOW 4105 SL 4095 TP1 4110'); await pg.fill('#saProv', 'Gold Kings'); await pg.click('[data-saadd]'); await pg.waitForTimeout(700); await pg.click('[data-sascore]'); await pg.waitForTimeout(900);
  await shot(pg, 'computer_auditor', true);
  ok(!errs.length && !(await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)), 'computer: no page errors, no overflow', errs);
  await ctx.close(); await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
