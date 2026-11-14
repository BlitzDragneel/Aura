// v6.5.112: all Forex through the OMEGA Live API and the bots feed. The server is mocked with route() (tools/livemock.js,
// same shapes and token rule as omega/live_api). Checks: token setting (never in backups, never restored), the Forex board
// (groups, prices, spread, market closed, tap -> Charts), the Twelve Data fallback (only without a key; Analysis, CREED desk,
// weekly bars built from daily), the bots feed (grades, paper marking, scouts, last updated) on Bots and Home, CREED's engine.
// usage: [PREV=<v6.5.111 build>] HARNESS=tools node s112_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
ok(/v6\.5\.1(1[2-9]|[2-9]\d) · build/.test(html), 'build v6.5.112 or later');
ok(/id="liveTokenInput"/.test(html) && /id="page-forex"/.test(html) && /data-page="forex"/.test(html) && /navigate\('forex'\)">Forex board/.test(html), 'token field, Forex page, menu entry and the Charts tab exist');
ok(/setInterval\(tickFeed, 120000\)/.test(html) || /id:'botsfeed'[\s\S]{0,400}120e3 : 15\*60e3/.test(html), 'bots feed refreshes every 2 minutes while visible (from v6.5.116 as the Autopilot job "botsfeed")');
const prev = process.env.PREV && fs.readFileSync(process.env.PREV, 'utf8');
if(prev){ const k = s => s.slice(s.indexOf('function analyseSeries('), s.indexOf('function analyseSeries(') + 60000);
  const mod = s => { const i = s.indexOf('// OMEGA v6.5 — CREED / ACCEPTANCE STRATEGY MODULE'); return s.slice(i, s.indexOf('</script>', i)).replace(/\n    if\(!key && window\.OMEGA_LAPI[^\n]*/, '').replace(/\n    crypto: \['BTCUSDT',[^\n]*/, ''); };   // v6.5.118: the Desk's crypto symbol list (gold/silver perpetuals) is a data line too
  ok(k(prev) === k(html) && mod(prev) === mod(html), 'CREED: engine byte-identical; the module differs only by the one data-source line (and from v6.5.118 its crypto symbol list)'); }
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(prep){ const ctx = await b.newContext({ viewport:{ width:412, height:915 } }); const tdCalls = [];
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue();
      if(M.handle(r)) return; if(u.hostname === 'api.twelvedata.com'){ tdCalls.push(u.search); return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify({ status:'error', code:429, message:'mock' }) }); }
      return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(p => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); if(p) Object.keys(p).forEach(k => localStorage.setItem(k, p[k])); }, prep || null);
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500); return { ctx, pg, errs, tdCalls }; }

  // 1. no token: the board explains, nothing is fetched with data endpoints
  let { ctx, pg, errs, tdCalls } = await open();
  M.calls.length = 0;
  await pg.evaluate(() => navigate('forex')); await pg.waitForTimeout(1200);
  const nt = await pg.evaluate(() => ({ t:document.getElementById('fxBoard').innerText, rows:document.querySelectorAll('#fxBoard .fx-row').length, feed:document.getElementById('homeBotsFeed').innerText }));
  ok(/Connect the OMEGA Live API/.test(nt.t) && nt.rows === 7 && !M.calls.some(c => /\/fx\/board|\/bots\/feed/.test(c.path)) && nt.feed === '', 'without a token: the board says how to connect, lists the 7 majors, calls no data endpoint, Home shows no feed card', { rows:nt.rows, calls:M.calls });
  // the token is saved from Settings and never leaves the device in a backup
  await pg.evaluate(() => { navigate('settings'); switchSettings('data'); }); await pg.fill('#liveTokenInput', M.TOKEN); await pg.click('#liveTokenSave');
  const saved = await pg.evaluate(() => ({ v:localStorage.getItem('omega_live_token'), shown:document.getElementById('liveTokenInput').value, m:document.getElementById('liveTokenMsg').textContent }));
  ok(saved.v === M.TOKEN && saved.shown.indexOf(M.TOKEN) < 0 && /Saved on this device/.test(saved.m), 'Settings saves the token on this device and does not show it back', saved);
  const bk = await pg.evaluate(() => window.OMEGA_BACKUP.build().then(b => JSON.stringify(b)));
  ok(bk.indexOf(M.TOKEN) < 0 && /omega_live_token/.test(JSON.parse(bk).excluded.join(',')), 'a backup leaves the token out (listed as excluded, value nowhere in the file)');
  const evil = JSON.stringify({ _omega:'full-backup', version:'3.8', exportedAt:new Date().toISOString(), data:{ omega_live_token:'stolen-token-xyz123', omega_academy_server:'https://example.org' }, excluded:[], archive:[] });
  await pg.evaluate(() => localStorage.setItem('omega_live_token', 'mine-0123456789'));
  const rs = await pg.evaluate(t => window.OMEGA_BACKUP.restore(t, { noConfirm:true, noReload:true }), evil);
  const after = await pg.evaluate(() => localStorage.getItem('omega_live_token'));
  ok(after === 'mine-0123456789' && (rs.skipped || []).indexOf('omega_live_token') > -1, 'a backup file cannot set the token (kept this device\u2019s, reported as not taken)', { after, rs });
  ok(!errs.length, 'no page errors (no token, settings, backup)', errs); await ctx.close();

  // 2. with the token
  ({ ctx, pg, errs, tdCalls } = await open({ omega_live_token:M.TOKEN }));
  await pg.evaluate(() => navigate('forex')); await pg.waitForTimeout(1500);
  const bd = await pg.evaluate(() => ({ t:document.getElementById('fxBoard').innerText, rows:Array.from(document.querySelectorAll('#fxBoard .fx-row')).map(r => r.innerText.replace(/\n/g, ' ')) }));
  ok(bd.rows.length === 7 && /EUR\/USD/.test(bd.rows[0]) && /1\.08420/.test(bd.rows[0]) && /spread 0\.9 pips/.test(bd.rows[0]) && /USD\/JPY .*151\.320/.test(bd.rows[2]) && /updated \d\d:\d\d/.test(bd.t), 'majors: 7 pairs with mid price, spread in pips, "updated" time', bd.rows.slice(0, 3));
  await pg.click('[data-fxg="exotics"]'); await pg.waitForTimeout(1200);
  const ex = await pg.evaluate(() => Array.from(document.querySelectorAll('#fxBoard .fx-row')).map(r => r.innerText.replace(/\n/g, ' ')));
  ok(ex.length === 18 && ex.some(r => /USD\/TTD.*Market closed/.test(r)) && ex.filter(r => /Market closed/.test(r)).length === 1, 'exotics: 18 pairs; the stale quote reads "Market closed"', ex.filter(r => /TTD/.test(r)));
  await pg.click('[data-fxg="metals"]'); await pg.waitForTimeout(1200);
  const mt = await pg.evaluate(() => Array.from(document.querySelectorAll('#fxBoard .fx-row')).map(r => r.innerText.replace(/\n/g, ' ')));
  ok(mt.length === 4 && /XAU\/USD.*Gold.*2650\.40.*spread \$0\.35/.test(mt[0]), 'metals: 4 rows, gold priced with a dollar spread', mt[0]);
  await pg.click('[data-fxg="majors"]'); await pg.waitForTimeout(800);
  M.calls.length = 0;
  await pg.click('[data-fx="GBPUSD"]'); await pg.waitForTimeout(9000);
  const an = await pg.evaluate(() => ({ act:document.querySelector('.page.active').id, sym:document.getElementById('symbol').value, ac:document.getElementById('assetClass').value, src:(document.getElementById('page-analysis').innerText.match(/OMEGA Live API · [^\n]{0,60}/) || [''])[0] }));
  const kl = M.calls.filter(c => c.path === '/fx/klines' && /symbol=GBPUSD/.test(c.q));
  ok(an.act === 'page-analysis' && an.sym === 'GBP/USD' && an.ac === 'forex' && kl.length >= 2 && kl.every(c => c.auth) && /OMEGA Live API/.test(an.src) && !tdCalls.length,
    'tapping GBP/USD opens Charts, and its analysis runs on Live API candles (with the token, no Twelve Data call)', { an, kl:kl.map(c => c.q), td:tdCalls.length });
  const wk = await pg.evaluate(() => window.OMEGA_LAPI.tdSeries('EUR/USD', '1week', 10));
  ok(wk.status === 'ok' && wk.values.length === 10 && wk.values.every(v => new Date(v.datetime.replace(' ', 'T') + 'Z').getUTCDay() === 1) && wk.values[0].datetime > wk.values[9].datetime, 'weekly bars are built from daily candles (Monday-start, newest first, Twelve Data shape)', wk.values.slice(0, 2));
  const cr = await pg.evaluate(async () => { const a = document.getElementById('creedAsset'), s = document.getElementById('creedSymbol'); if(a) a.value = 'forex'; if(s) s.value = 'EUR/USD';
    try{ const rows = await window.OMEGA_CREED.fetchTF('15m', 120); return { n:rows.length, c:rows[rows.length - 1].c }; }catch(e){ return { err:String(e.message || e) }; } });
  ok(cr.n === 120 && cr.c > 1 && cr.c < 1.2, 'CREED desk: EUR/USD 15m candles arrive through its own fetch with no Twelve Data key', cr);
  await pg.evaluate(() => navigate('bot')); await pg.waitForTimeout(1800);
  const fd = await pg.evaluate(() => document.getElementById('botsFeed').innerText);
  ok(/PAPER · FORECASTS/i.test(fd) && /Climax reversal\s*GRADE A/i.test(fd) && /Panic bounce H1\s*GRADE B/i.test(fd) && /C · WATCH LIST, PAPER ONLY/i.test(fd) && /SOL long/.test(fd) && /resting limit 242\.55/.test(fd) && /Last updated \d\d:\d\d/.test(fd),
    'Bots: the paper bot\u2019s positions and resting orders per rule with A/B/C grades, paper marking and last updated', fd.slice(0, 300));
  ok(/Waiting for a signal: .*Panic bounce H3.*\(B\)/.test(fd) && /Strongest up\s*DOGE\s*30\.1%/.test(fd) && /Strongest down\s*ETH\s*22\.2%/.test(fd) && /hit 25% vs base rate 16%/.test(fd), 'idle rules on one line; scouts: strongest up/down calls and forward hit rate vs base rate', fd.slice(-500));
  const ra = await pg.evaluate(() => document.querySelector('#botsFeed details').textContent);
  ok(/refused 2× \((TRUST, BICO|BICO, TRUST)\)/.test(ra) && /order BCH/.test(ra), 'recent actions: repeated refusals folded into one line', ra);
  await pg.evaluate(() => navigate('command')); await pg.waitForTimeout(1200);
  const hm = await pg.evaluate(() => document.getElementById('homeBotsFeed').innerText);
  ok(/24\/7 bots/.test(hm) && /PAPER/i.test(hm) && /2\s*open \(paper\)/.test(hm) && /DOGE/.test(hm), 'Home: compact bots card', hm);
  ok(!errs.length, 'no page errors with the token', errs); await ctx.close();

  // 3. with a Twelve Data key the old path is used, not the server
  ({ ctx, pg, errs, tdCalls } = await open({ omega_live_token:M.TOKEN, omega_td_key:'abcdefghijklmnop1234' }));
  M.calls.length = 0;
  await pg.evaluate(() => fetch('https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&outputsize=5&apikey=abcdefghijklmnop1234').then(r => r.json()));
  ok(tdCalls.filter(q => /outputsize=5&/.test(q)).length === 1 && !M.calls.some(c => c.path === '/fx/klines' && /limit=6\b|limit=5\b/.test(c.q)), 'with a Twelve Data key the request still goes to Twelve Data', { td:tdCalls.length, calls:M.calls });
  await ctx.close();
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
