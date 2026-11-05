// OMEGA Prime: trade tickets on Today (exact orders for tested rules, exit reminders, taken/skipped, scoreboards).
const fs = require('fs'), path = require('path'); const FILE = process.argv[2] || path.join(__dirname, 'omega-prime.html');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), H = 3600e3;
  for(const vp of [{ width:412, height:915, n:'phone' }, { width:1280, height:900, n:'computer' }]){
    const ctx = await b.newContext({ viewport:{ width:vp.width, height:vp.height } });
    await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
    await ctx.addInitScript(() => { const H = 3600e3, nh = Math.floor(Date.now()/H);
      localStorage.setItem('prime:prime_panic_v1', JSON.stringify({ lastH:nh - 1, scans:1, msg:'', th:{}, breadth:{ h:nh - 1, v:0.12 }, trades:[
        { sym:'AAAUSDT', rule:'H1', t:nh - 2, close:1.4, limit:1.2345, r24:-0.153, status:'pending' },
        { sym:'BBBUSDT', rule:'H3', t:nh - 30, entry:2.5, r24:-0.2, br:0.25, status:'open', due:nh - 3 },
        { sym:'DDDUSDT', rule:'H1', t:nh - 100, entry:10, fill:nh - 99, exit:10.3, net:0.0288, status:'closed' } ] }));
      localStorage.setItem('prime:prime_climax_v1', JSON.stringify({ lastH:nh - 1, scans:1, msg:'', trades:[
        { sym:'CCCUSDT', t:nh - 1, e:nh, z:-3.4, vr:4.1, loc:0.7, status:'open' },
        { sym:'EEEUSDT', t:nh - 200, e:nh - 199, z:-3.1, vr:3.5, loc:0.6, entry:5, exit:5.2, net:0.038, status:'closed' } ] })); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000); await pg.evaluate(() => navigate('today')); await pg.waitForTimeout(1500);
    await pg.evaluate(() => window.OMEGA_TICKETS.render()); await pg.waitForTimeout(300);
    const t = await pg.evaluate(() => { const e = document.getElementById('ticketsBody'), v = document.querySelector('#todayBody .verdict'); return { t:e ? e.innerText : '', slips:e ? e.querySelectorAll('.tk-slip').length : 0, afterVerdict:!!(v && e && (v.compareDocumentPosition(e) & 4)) }; });
    ok(t.slips === 3 && t.afterVerdict && /Your orders/.test(t.t), vp.n + ': Today shows “Your orders” under the verdict, with 3 tickets (H1 limit, H3 exit, climax entry)', t);
    ok(/SELL NOW/.test(t.t) && t.t.indexOf('SELL NOW') < t.t.indexOf('PLACE THIS ORDER') && /Market Sell now/.test(t.t), vp.n + ': an exit that is due comes first, as SELL NOW, market sell', t.t.slice(0, 300));
    ok(/Limit Buy at 1\.2345/.test(t.t) && /5 USDT/.test(t.t) && /Cancel if unfilled/.test(t.t) && /USDT-M Futures · AAAUSDT · 1×/.test(t.t) && /sell at market 24 hours after the fill/.test(t.t), vp.n + ': the H1 ticket gives the exact limit price, 5 USDT, where, when to cancel and how it ends', t.t.slice(0, 600));
    ok(/Market Buy now/.test(t.t) && /CCC · Climax \(grade A\)/.test(t.t) && /\+0\.32% a trade/.test(t.t) && /77–93%/.test(t.t), vp.n + ': the climax ticket says buy at market now; every ticket carries its measured odds and tail risk');
    ok(/Every ticket \(paper\): 2 closed, 100% winners/.test(t.t) && /The ones you placed: no closed trades yet/.test(t.t), vp.n + ': the scoreboard counts the rules’ closed paper trades (climax and panic), and yours separately', t.t.slice(-300));
    if(vp.n === 'phone'){
      await pg.evaluate(() => { [...document.querySelectorAll('#ticketsBody .tk-btn')].find(b => b.textContent === 'I placed it').click(); }); await pg.waitForTimeout(300);
      const st = await pg.evaluate(() => JSON.parse(localStorage.getItem('prime:prime_tickets_v1')));
      ok(Object.values(st.taken).filter(v => v === 'taken').length === 1, 'tapping “I placed it” is stored (under prime:)', st.taken);
      await pg.evaluate(() => { const s = document.getElementById('tkSeat'); s.value = '10'; s.onchange(); }); await pg.waitForTimeout(300);
      const t2 = await pg.evaluate(() => document.getElementById('ticketsBody').innerText);
      ok(/10 USDT/.test(t2) && !/Size\s*5 USDT/.test(t2), 'changing the ticket size to 10 USDT updates every order', t2.slice(0, 300));
      await pg.evaluate(() => document.getElementById('ticketsBody').scrollIntoView()); await pg.screenshot({ path:'/tmp/prime_tickets.png' }); }
    const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    ok(!wide && !errs.length, vp.n + ': no horizontal overflow and no page errors', { wide, errs });
    await ctx.close(); }
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
