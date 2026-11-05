// OMEGA Prime checks: the climax rule, the Today verdict, every page, the Autopilot, storage kept apart, phone and desktop.
const fs = require('fs'), path = require('path'), H = 3600e3;
const FILE = process.argv[2] || path.join(__dirname, 'omega-prime.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
// 1. the rule, in Node
const store = {}; global.window = { PRIME_LS:{ getItem:k => store[k] || null, setItem:(k, v) => { store[k] = v; } }, OMEGA_OPERATOR:{ jobs:() => ({ push(){} }) } }; global.document = { getElementById:() => null }; global.Notification = undefined;
new Function(grab('PRIME CLIMAX WATCH'))(); const C = window.OMEGA_CLIMAX._;
function series(last){ const rows = []; let p = 100; for(let i = 0; i < 200; i++){ const r = 0.004*Math.sin(i*1.7) + 0.002*Math.cos(i*0.9); const o = p; p = p*Math.exp(r); rows.push({ h:1000 + i, o, hi:Math.max(o, p)*1.001, lo:Math.min(o, p)*0.999, c:p, v:1000 + 50*Math.sin(i) }); } if(last) rows[199] = Object.assign(rows[199], last(rows[198].c)); return rows; }
const fire = series(pc => ({ o:pc, hi:pc*1.001, lo:pc*0.93, c:pc*0.975, v:6000 })), weakClose = series(pc => ({ o:pc, hi:pc*1.001, lo:pc*0.93, c:pc*0.935, v:6000 })), lowVol = series(pc => ({ o:pc, hi:pc*1.001, lo:pc*0.93, c:pc*0.975, v:1500 })), young = series(pc => ({ o:pc, hi:pc*1.001, lo:pc*0.93, c:pc*0.975, v:6000 }));
const a = C.check(fire, 199, 0), b = C.check(weakClose, 199, 0), c = C.check(lowVol, 199, 0), d = C.check(young, 199, (1199 - 100)*H);
ok(a.fires && a.z <= -3 && a.vr >= 3 && a.loc >= 0.6 && !b.fires && !c.fires && d === null, 'climax rule: fires on a 3σ flush with 3× volume that closes in the top 40%; not on a weak close, low volume, or a coin under 30 days old', { a, b:b.loc, c:c.vr });
const tr = C.settle({ sym:'X', t:1199, e:1200, status:'open' }, Array.from({ length:12 }, (_, i) => ({ h:1200 + i, o:i === 0 ? 100 : 101, hi:103, lo:99, c:i === 11 ? 102 : 101 })));
ok(tr.status === 'closed' && tr.entry === 100 && tr.exit === 102 && Math.abs(tr.net - 0.018) < 1e-9, 'a climax trade buys the next open and closes 12 hours later, after 0.10% a side (+1.8%)', tr);
(async () => {
  const pw = require('playwright'), b = await pw.chromium.launch(); const nh = Math.floor(Date.now()/H);
  const route = async r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue(); const j = x => r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(!/binance/.test(u.hostname)) return j([]); const q = u.searchParams, sym = q.get('symbol'), iv = q.get('interval'), n = +(q.get('limit') || 100);
    if(/ticker\/24hr/.test(u.pathname)) return j(Array.from({ length:45 }, (_, i) => ({ symbol:i === 0 ? 'PLANTUSDT' : 'C' + i + 'USDT', quoteVolume:String(1e9 - i*1e6) })).concat([{ symbol:'USDCUSDT', quoteVolume:'9e9' }]));
    if(/exchangeInfo/.test(u.pathname)) return j({ symbols:[{ symbol:'PLANTUSDT', onboardDate:Date.now() - 400*24*H }] });
    if(/\/klines$/.test(u.pathname)){ const step = iv === '15m' ? H/4 : iv === '1d' ? 24*H : H, end = iv === '1d' ? Math.floor(Date.now()/(24*H))*24*H : nh*H;
      return j(Array.from({ length:n }, (_, i) => { let o = 100 + 3*Math.sin(i/8) + 0.004*i, c = o + 0.2, hi = o + 0.6, lo = o - 0.6, v = 1000 + 30*Math.sin(i);
        if(sym === 'PLANTUSDT' && iv === '1h' && n === 200){ const p0 = 100*Math.exp(0.003*Math.sin(i*1.7)); o = p0; c = p0*1.0005; hi = p0*1.002; lo = p0*0.998; v = 1000; if(i === n - 1){ o = 100; hi = 100.1; lo = 93; c = 97.5; v = 6000; } }
        return [end - (n - i)*step, String(o), String(Math.max(hi, o, c)), String(Math.min(lo, o, c)), String(c), String(v), 0, String(v*o), 0, String(v*0.5), String(v*o*0.5)]; })); }
    if(/\/depth$/.test(u.pathname)) return j({ bids:Array.from({ length:40 }, (_, i) => [String(100 - i*0.1), String(i === 15 ? 300 : 10)]), asks:Array.from({ length:40 }, (_, i) => [String(100.3 + i*0.1), '10']) });
    if(/premiumIndex/.test(u.pathname)) return j({ markPrice:'100.2', indexPrice:'100.18', lastFundingRate:'0.0001' }); return j([]); };
  for(const vp of [{ width:412, height:915, name:'phone' }, { width:1280, height:900, name:'desktop' }]){
    const ctx = await b.newContext({ viewport:{ width:vp.width, height:vp.height } }); await ctx.route('**/*', route);
    const SHIFT = (Date.now() % H) < 200e3 ? 300e3 : 0; if(SHIFT) await ctx.addInitScript(s => { const n0 = Date.now; Date.now = () => n0() + s; }, SHIFT); const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(5000);
    if(vp.name === 'phone'){
      let sc = null; for(let k = 0; k < 40; k++){ sc = await pg.evaluate(() => { const S = window.OMEGA_CLIMAX.state(); return { busy:S.busy, scans:S.scans, r:S.msg, trades:S.trades }; }); if(!sc.busy && sc.scans >= 1) break; await pg.waitForTimeout(1500); }
      ok(sc.trades.some(t => t.sym === 'PLANTUSDT' && t.status === 'open') && sc.trades.length === 1 && /1 new signal/.test(typeof sc.r === 'string' ? sc.r : JSON.stringify(sc.r)), 'in the app: the scan of the 40 most-traded coins finds the planted climax (and nothing else; stablecoins skipped)', sc);
      await pg.evaluate(() => navigate('today')); await pg.waitForTimeout(2500);
      const t = await pg.evaluate(() => ({ v:(document.querySelector('.verdict') || {}).innerText || '', dial:!!document.querySelector('svg.dial'), coins:document.querySelectorAll('.coin').length, ev:(document.getElementById('evBody') || {}).innerText || '' }));
      ok(/Grade A signal/i.test(t.v) && /Climax buy: PLANT/.test(t.v) && t.dial && t.coins === 5 && /Events ahead/i.test(t.ev), 'Today: the verdict raises the Grade A climax signal first, with the market dial, the five coins and the events ahead', t);
      await pg.screenshot({ path:'/tmp/prime_today_phone.png', fullPage:true });
      const pages = {}; for(const p of ['chart', 'signals', 'risk', 'evidence']){ await pg.evaluate(p => navigate(p), p); await pg.waitForTimeout(p === 'chart' ? 5000 : 2000); pages[p] = await pg.evaluate(p => { const e = document.getElementById('page-' + p); return { text:e.innerText.slice(0, 20000), svg:e.querySelectorAll('svg').length, candles:e.querySelectorAll('[data-c]').length }; }, p); if(p === 'chart') await pg.screenshot({ path:'/tmp/prime_chart_phone.png', fullPage:true }); }
      const jobs = await pg.evaluate(() => window.OMEGA_OPERATOR.list().map(j => j.id));
      ok(pages.chart.candles >= 70 && /Climax watch/.test(pages.signals.text) && /PLANT/.test(pages.signals.text) && /Today’s plan/i.test(pages.signals.text) && /Growth Bot/.test(pages.risk.text) && /Is the bot worth it/i.test(pages.risk.text) && /What is known/.test(pages.evidence.text) && /Autopilot/.test(pages.evidence.text) && !/Research exports|Market Watch recording/.test(pages.risk.text + pages.chart.text), 'every page: the chart with its candles, Signals (climax and Daily Plan), Risk (bot, baseline), Evidence (ledger, Autopilot); no research-only sections', Object.fromEntries(Object.entries(pages).map(([k, v]) => [k, v.text.slice(0, 60)])));
      ok(['climax', 'mread', 'dplan', 'cockpit', 'rguard', 'truth'].every(j => jobs.includes(j)) && !jobs.includes('mwdays') && !jobs.includes('autoexp'), 'the Autopilot carries Prime’s jobs and refuses the research ones', jobs);
      const keys = await pg.evaluate(() => Object.keys(localStorage));
      const fr = await pg.evaluate(() => window.OMEGA_TRUTH._.readsCheck({ BTCUSDT:{ err:'HTTP 500' } }, Date.now()));
      ok(fr.length === 1 && !fr[0].ok && /could not be read/.test(fr[0].issues[0]), 'the data check counts a market that could not be read as a problem (it used to skip it)', fr);
      ok(keys.length > 0 && keys.every(k => k.startsWith('prime:')), 'every piece of data is stored under “prime:”, apart from the original build’s (' + keys.length + ' keys)', keys);
    } else { await pg.evaluate(() => navigate('today')); await pg.waitForTimeout(3000); await pg.screenshot({ path:'/tmp/prime_today_desktop.png', fullPage:false }); }
    const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    ok(!wide && errs.length === 0, vp.name + ': no horizontal overflow and no page errors', { wide, errs });
    await ctx.close(); }
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
