// v6.5.121: Signal Lab card on the Desks page (public bot-state record; signals, reasons, scoreboard). usage: node s121_test.js <build>
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0; function ok(c, m, x){ if(c){ pass++; console.log('ok   ' + m); } else { fail++; console.log('FAIL ' + m + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
ok(/v6\.5\.1(2[1-9]|[3-9]\d) · build/.test(html), 'build v6.5.121 or later');
ok(html.split('id="sigLabBody"').length === 2 && /OMEGA_SIGLAB/.test(html), 'one Signal Lab container and module');
const REC = { signals:[
  { id:'a', symbol:'XAUUSD', setup:'S5', side:'sell', logged_ms:Date.now() - 7200000, ref_price:4051.6, stop:4059.7, targets:[4047.5,4043.5,4039.4,4035.4,4031.3], status:'closed', outcome:'TP2+BE', R_ladder:0.3, review:'Reached TP2 then came back to the entry.', state:{ trend:'down', vol:'high', session:'London' }, sent:true, grade_at_issue:'PAPER' },
  { id:'b', symbol:'BTCUSD', setup:'S4', side:'buy', logged_ms:Date.now() - 600000, ref_price:65505.2, stop:64471.2, targets:[66022,66539,67056,67573,68090], status:'open', state:{ trend:'up', vol:'normal', session:'New York' }, sent:true, grade_at_issue:'PAPER' } ],
  record:{ all:{ n:1, avg_R:0.3, win:1 }, open:1, by_setup_market:{ 'XAUUSD S5':{ n:1, avg_R:0.3, win:1, grade:'PAPER' } } }, record_by_context:{ 'S5 | with trend':{ n:3, avg_R:0.2, win:0.67 } } };
(async () => { const pw = require('playwright'), b = await pw.chromium.launch();
  for(const mode of ['ok', 'down']){
    const ctx = await b.newContext({ viewport:{ width:412, height:915 } });
    await ctx.route('**/*', r => { let u; try{ u = new URL(r.request().url()); }catch(e){ return r.abort(); } if(u.protocol === 'file:') return r.continue();
      if(u.hostname === 'raw.githubusercontent.com' && u.pathname.includes('siglab')) return mode === 'ok' ? r.fulfill({ status:200, contentType:'application/json', body:JSON.stringify(REC) }) : r.fulfill({ status:404, body:'' });
      return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.evaluate(() => { localStorage.setItem('omega_tutorial_v1', '{"done":1}'); });
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3000);
    await pg.evaluate(() => navigate('desks')); await pg.waitForTimeout(2500);
    const t = await pg.evaluate(() => document.getElementById('sigLabBody').innerText);
    if(mode === 'ok'){
      ok(/Signal Lab/.test(t) && /XAUUSD SELL · session drive/.test(t) && /TP2\+BE \+0\.3R/.test(t) && /Reached TP2/.test(t), 'closed signal with result and reason', t.slice(0, 300));
      ok(/BTCUSD BUY · fib pullback/.test(t) && /open/i.test(t) && /Market then: trend up/.test(t), 'open signal with its market state');
      ok(/Scoreboard/.test(t) && /What it has learned/.test(t), 'scoreboard and lessons');
      if(process.env.SHOTS) await pg.screenshot({ path:path.join(process.env.SHOTS, 'phone_siglab.png'), fullPage:true });
    } else ok(/could not be loaded/.test(t), 'says so when the record is unreachable');
    ok(errs.length === 0, 'no page errors (' + mode + ')', errs);
    await ctx.close(); }
  await b.close(); console.log(pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
