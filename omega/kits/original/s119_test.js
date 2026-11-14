// v6.5.119: Desks (Bitcoin, Gold, Silver). Page, menu entry, Home strip, palette; bottom bar unchanged; per desk: live price
// (+ spot for metals), what the bot says now, day/swing/hold states with reasons, WATCH without a direction, a call only from
// a tested rule (grade, entry, stop, target, size, evidence, paper record), the market read, forward record and notebook;
// no token -> prices and a way to connect; Autopilot job "desks". Screenshots: SHOTS=<dir> (optional).
// usage: HARNESS=tools [SHOTS=dir] node s119_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const M = require(path.resolve(process.env.HARNESS || path.join(__dirname, 'tools'), 'livemock.js'));
const SHOTS = process.env.SHOTS; if(SHOTS) fs.mkdirSync(SHOTS, { recursive:true });
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 700) : '')); } }
ok(/v6\.5\.1(19|[2-9]\d) · build/.test(html), 'build v6.5.119 or later');
ok(html.split('id="page-desks"').length === 2 && /data-page="desks"/.test(html) && /'desks'\];   \/\/ v6\.5\.119/.test(html), 'one Desks page, a menu entry, known to the navigator');
const CALL = { id:'btc_rule-202611141500', rule:'btc_trend_day', horizon:'day', asset:'BTC', symbol:'BTCUSDT', side:'long', entry_type:'market', entry:75830, stop:74314, target:78863, tf:'1h',
  signal_bar:new Date(Date.now() - 36e5).toISOString(), exit_by:new Date(Date.now() + 3 * 36e5).toISOString(), size:{ margin_usdt:5, leverage:1, notional_usdt:5 }, grade:'B', status_rule:'paper',
  evidence:'edges/results/E90_result.json', research_only:true, execution_allowed:false, state:'TRIGGERED', fill_time:null, fill_price:null };
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  async function open(o){ o = o || {}; const ctx = await b.newContext({ viewport:{ width:o.w || 412, height:o.h || 915 } });
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue(); if(M.handle(r)) return;
      const J = x => r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) }); const sym = u.searchParams.get('symbol') || '';
      if(/binance/.test(u.hostname) && /ticker\/24hr$/.test(u.pathname) && sym) return J({ symbol:sym, lastPrice:String(M.PERP_PX[sym] || 100), priceChangePercent:sym === 'XAGUSDT' ? '-1.10' : '0.40' });
      return J([]); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(p => { localStorage.clear(); localStorage.setItem('omega_tutorial_v1', '{"done":1}'); if(p) Object.keys(p).forEach(k => localStorage.setItem(k, p[k])); }, o.prep || null);
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000); return { ctx, pg, errs }; }
  const shot = async (pg, n, full) => { if(SHOTS) await pg.screenshot({ path:path.join(SHOTS, n + '.png'), fullPage:!!full }); };
  const deskText = pg => pg.evaluate(() => (document.getElementById('desksBody') || {}).innerText || '');
  // 1. phone, token set
  let { ctx, pg, errs } = await open({ prep:{ omega_live_token:M.TOKEN } });
  const home = await pg.evaluate(() => { const p = document.getElementById('page-command'); return { nav:Array.from(document.querySelectorAll('.omega-bottomnav button span')).map(s => s.textContent),
    tiles:Array.from(document.querySelectorAll('#homeDesks .dk-tile')).map(t => t.innerText.replace(/\n/g, ' ')), cards:p.querySelectorAll('details.cmd-card').length,
    first:Array.from(p.children).filter(e => e.offsetHeight > 0).slice(0, 3).map(e => e.id || e.className), jobs:window.OMEGA_OPERATOR.jobs().map(j => j.id),
    pal:(function(){ try{ return document.querySelectorAll('.sidebar-menu li[data-page="desks"]').length; }catch(e){ return 0; } })() }; });
  ok(JSON.stringify(home.nav) === JSON.stringify(['Home', 'Charts', 'Signals', 'CREED', 'Bots', 'Academy', 'More']) && home.pal === 1, 'bottom bar unchanged; Desks reachable from the menu (More)', home);
  ok(home.tiles.length === 3 && /Bitcoin desk/.test(home.tiles[0]) && /Gold desk/.test(home.tiles[1]) && /Silver desk/.test(home.tiles[2]) && home.cards === 8 && home.first[1] === 'cmdFive' && home.jobs.includes('desks'),
    'Home: a strip with the three desks (Home’s 8 cards and order unchanged); the Autopilot has the job "desks"', home);
  await pg.evaluate(async () => { await window.OMEGA_OPERATOR.jobs().find(j => j.id === 'desks').run(); }); await pg.waitForTimeout(500);
  const tiles = await pg.evaluate(() => Array.from(document.querySelectorAll('#homeDesks .dk-tile')).map(t => t.innerText.replace(/\n/g, ' ')));
  ok(/Gold desk 2,655\.10 WATCH · swing/.test(tiles[1]) && /Bitcoin desk 75,830\.0/.test(tiles[0]), 'Home tiles: live price and the notable state per desk', tiles);
  await pg.evaluate(() => document.getElementById('homeDesks').scrollIntoView({ block:'center' })); await pg.waitForTimeout(200); await shot(pg, 'phone_home_strip');
  await pg.click('#homeDesks .dk-tile[data-dkgo="XAU"]'); await pg.waitForTimeout(2500);
  let t = await deskText(pg);
  const g = await pg.evaluate(() => ({ act:document.querySelector('.page.active').id, tabs:Array.from(document.querySelectorAll('#desksBody [data-dk]')).map(x => x.innerText.replace(/\n/g, ' ')),
    st:Array.from(document.querySelectorAll('#desksBody .dk-h .dk-st')).map(x => x.innerText), folds:Array.from(document.querySelectorAll('#desksBody details.dk-fold > summary')).map(x => x.innerText.split('\n')[0]) }));
  ok(g.act === 'page-desks' && g.tabs.length === 3 && /Gold/.test(g.tabs[1]) && /WATCH/.test(g.tabs[1]), 'the Gold tile opens Desks on Gold; three tabs (Bitcoin, Gold, Silver)', g);
  ok(/2,655\.10/.test(t) && /\+0\.40%/.test(t) && /Spot XAU\/USD/i.test(t) && /2,650\.40/.test(t) && /Swissquote, live/.test(t), 'Gold: the 24/7 perpetual price and the spot quote', t.slice(0, 300));
  ok(/No trade\. Watching for a big move on swing — the direction is not known/.test(t) && /No rule for gold has passed a fair test yet/.test(t), 'what the bot says now: no trade, WATCH on swing without a direction, and why', t.slice(0, 600));
  ok(JSON.stringify(g.st) === JSON.stringify(['WAIT', 'WATCH', 'WAIT']) && !/WATCH · (long|short)/.test(t), 'day WAIT, swing WATCH, hold WAIT; a WATCH never shows a direction', g.st);
  ok(g.folds.join('|') === 'The market read|Forward record|What I know about gold', 'dropdowns: market read, forward record, the notebook', g.folds);
  await pg.evaluate(() => document.querySelectorAll('#desksBody details').forEach(d => d.open = true)); await pg.waitForTimeout(200);
  t = await deskText(pg);
  ok(/below its averages, falling/.test(t) && /Volatility is quiet/.test(t) && /30-day low/.test(t) && /30% chance of a big move either way/.test(t) && /never a direction/i.test(t) && /120 readings scored/.test(t) && /The research on Gold is still running/.test(t) && !/NaN|undefined|\[object/.test(t),
    'opened: trend per timeframe, volatility, the reason for WATCH, scouts as big-move risk only, the forward record and the notebook; no NaN/undefined', t.slice(0, 400));
  if(process.env.DBG) console.log(t);
  await shot(pg, 'phone_gold_desk_open', true);
  await pg.evaluate(() => document.querySelectorAll('#desksBody details').forEach(d => d.open = false));
  await pg.click('#desksBody [data-dk="XAG"]'); await pg.waitForTimeout(1500); await pg.evaluate(() => document.querySelectorAll('#desksBody details').forEach(d => d.open = true));
  t = await deskText(pg);
  ok(/Silver · perpetual XAGUSDT/i.test(t) && /31\.400/.test(t) && /−1\.10%|-1\.10%/.test(t) && /NO SKILL on validation/.test(t), 'Silver: its own price, and a scout without proven skill is labelled as such', t.slice(0, 300));
  await shot(pg, 'phone_silver_desk', true);
  // 2. a call from a tested rule (Bitcoin, day)
  M.DESKS.BTC = Object.assign(M.desk('BTC'), {}); const hz = M.DESKS.BTC.horizons;
  hz.day = Object.assign({}, hz.day, { state:'TRIGGERED', direction:'long', plain:'A tested rule fired: a call is out, waiting for its entry.', reasons:['rule btc_trend_day (grade B) called long at ' + CALL.signal_bar.slice(0, 16) + ' UTC'], call:CALL,
    rules:[{ id:'btc_trend_day', grade:'B', status:'paper', execution_allowed:false, research_only:true, evidence:CALL.evidence }] });
  M.DESKS.BTC.open_calls = [CALL];
  await pg.click('#desksBody [data-dk="BTC"]'); await pg.waitForTimeout(500); await pg.evaluate(() => window.OMEGA_DESKS.refresh(true)); await pg.waitForTimeout(800);
  t = await deskText(pg);
  ok(/A tested rule has called a trade: day trades — long \(rule btc_trend_day, grade B, waiting for its entry\)/.test(t) && /TRIGGERED · long/.test(t) && /Calls come only from rules that passed a fair test/.test(t),
    'Bitcoin: a call from a tested rule says so plainly, with its direction', t.slice(0, 500));
  ok(/Entry\s*75,830\.0/.test(t) && /Stop\s*74,314\.0/.test(t) && /Target\s*78,863\.0/.test(t) && /5 USDT margin × 1/.test(t) && /edges\/results\/E90_result\.json/.test(t) && /paper record \(research only\): not an order/.test(t) && /Grade B/i.test(t),
    'the call shows entry, stop, target, exit time, size from the rule, grade, evidence, and that it is a paper record', t.slice(0, 900));
  await shot(pg, 'phone_btc_call', true);
  // 3. a desk the bot has not written yet
  M.DESKS.XAG = { available:false, source:'cloud bots (GitHub bot-state)', note:'this desk has not written a record yet (the asset bots run every 15 minutes)' };
  await pg.click('#desksBody [data-dk="XAG"]'); await pg.waitForTimeout(400); await pg.evaluate(() => window.OMEGA_DESKS.refresh(true)); await pg.waitForTimeout(600);
  t = await deskText(pg);
  ok(/The silver bot has not written a desk yet/.test(t) && /31\.400/.test(t), 'no desk yet: says so, price still shown', t.slice(0, 300));
  delete M.DESKS.XAG; delete M.DESKS.BTC;
  const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  ok(!errs.length && !wide, 'phone: no page errors, nothing wider than the screen', { errs, wide });
  await ctx.close();
  // 4. no token: prices and a way to connect; the job only refreshes prices
  ({ ctx, pg, errs } = await open({}));
  await pg.evaluate(() => window.OMEGA_DESKS.open('XAU')); await pg.waitForTimeout(2000);
  const jr = await pg.evaluate(async () => window.OMEGA_OPERATOR.jobs().find(j => j.id === 'desks').run());
  t = await deskText(pg);
  ok(/Connect the OMEGA Live API to see the gold bot’s desk/.test(t) && /2,655\.10/.test(t) && /needs the Live API token/.test(t) && jr && jr.skip && /prices only/.test(jr.text), 'no token: live price, how to connect, the job refreshes prices only', { t:t.slice(0, 300), jr });
  await shot(pg, 'phone_no_token');
  ok(!errs.length, 'no page errors without a token', errs);
  await ctx.close();
  // 5. computer
  ({ ctx, pg, errs } = await open({ w:1280, h:900, prep:{ omega_live_token:M.TOKEN } }));
  await pg.evaluate(() => window.OMEGA_DESKS.open('XAU')); await pg.waitForTimeout(2500);
  const cols = await pg.evaluate(() => getComputedStyle(document.querySelector('#desksBody .dk-hz')).gridTemplateColumns.split(' ').length);
  ok(cols === 3, 'computer: day, swing and hold side by side', cols);
  await shot(pg, 'computer_gold_desk', true);
  await pg.evaluate(() => window.OMEGA_GS.openPerp('XAUUSDT')); await pg.waitForTimeout(3000); await shot(pg, 'computer_gold_chart_strip');
  await pg.evaluate(() => navigate('forex')); await pg.waitForTimeout(800); await pg.click('[data-fxg="metals"]'); await pg.waitForTimeout(1200); await shot(pg, 'computer_forex_metals');
  ok(!errs.length && !(await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)), 'computer: no page errors, no overflow', errs);
  await ctx.close(); await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
