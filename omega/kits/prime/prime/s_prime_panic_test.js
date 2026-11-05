// OMEGA Prime: the panic-bounce watch (E22 H1/H3, Grade B). Parity with the research engine, live behaviour, and the app.
const fs = require('fs'), path = require('path'), H = 3600e3;
const FILE = process.argv[2] || path.join(__dirname, 'omega-prime.html'), html = fs.readFileSync(FILE, 'utf8');
const PAR = JSON.parse(fs.readFileSync(path.join(__dirname, 'parity', 'parity.json'), 'utf8'));
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
const store = {}; global.window = { PRIME_LS:{ getItem:k => store[k] || null, setItem:(k, v) => { store[k] = v; } }, OMEGA_OPERATOR:{ jobs:() => ({ push(){} }) } }; global.document = { getElementById:() => null }; global.Notification = undefined;
new Function(grab('PRIME PANIC-BOUNCE WATCH'))(); const P = window.OMEGA_PANIC._;
// 1. parity: the same trades as the research engine (e22_lib.run), replayed with the app's own functions
const coins = Object.entries(PAR.markets).map(([sym, rows]) => { const D = P.dense(rows.map(r => ({ h:r[0], hi:r[1], lo:r[2], c:r[3] })));
  const th = {}; for(let d = Math.floor(D.h0/24); d <= Math.floor((D.h0 + D.n)/24); d++){ const T = P.dayTh(D, d); if(T) th[d] = T; } return { sym, D, th, first:D.h0 }; });
const lastH = Math.max(...coins.map(C => C.D.h0 + C.D.n - 1)), h0 = Math.min(...coins.map(C => C.D.h0));
const br = {}; for(let h = h0; h <= lastH; h++){ const b = P.breadthAt(coins, h); if(b != null) br[h] = b; }
const all = []; coins.forEach(C => { all.push(...P.runCoin(C.sym, C.D, C.th, br, h0, C.D.h0 + C.D.n - 1, [], C.first)); });
for(const rule of ['H1', 'H3']){
  const mine = all.filter(t => t.rule === rule && t.status === 'closed').map(t => [t.sym, t.t, +t.net.toFixed(6)]).sort();
  const ref = PAR.trades[rule].map(r => [r[0], r[1], +r[2].toFixed(6)]).sort();
  const diff = ref.filter((r, i) => !mine[i] || mine[i][0] !== r[0] || mine[i][1] !== r[1] || Math.abs(mine[i][2] - r[2]) > 2e-6);
  ok(mine.length === ref.length && diff.length === 0, rule + ': the app’s rule gives exactly the research engine’s ' + ref.length + ' trades (same coin, hour and result after costs)', { mine:mine.length, ref:ref.length, first:diff.slice(0, 3) });
}
ok(P.rowsOf([[3600e3, '1', '1.1', '0.9', '1', '5'], [7200e3, '1', '1', '1', '1', '0']]).length === 1, 'a volume-0 candle counts as missing (the archive’s flat candles after a delisting, trading halts)');
ok(Math.abs(P.pctl([1, 2, 3, 4, 10], 10) - 1.4) < 1e-12 && Math.abs(P.pctl([1, 2, 3, 4, 10], 95) - 8.8) < 1e-12, 'percentiles are interpolated as numpy does');
// 2. live behaviour on a hand-made coin
function coin(n, f){ const rows = []; for(let i = 0; i < n; i++){ const c = 100*(1 + 0.01*Math.sin(i*0.7)); rows.push({ h:24000 + i, hi:c*1.003, lo:c*0.997, c }); } f && f(rows); return P.dense(rows); }
const D = coin(900), th = {}; for(let d = 1000; d <= 1037; d++){ const T = P.dayTh(D, d); if(T) th[d] = T; }
const t = { sym:'X', rule:'H1', t:24850, close:100, limit:95 };
ok(P.settle(Object.assign({}, t), D, 24851).status === 'pending' && P.settle(Object.assign({}, t), D, 24853).status === 'missed', 'H1: an order is pending for 3 hours, then missed if price never trades below the limit');
const D2 = coin(900, rows => { rows[852].lo = 94; rows[876].c = 99; }), f = P.settle(Object.assign({}, t), D2, 24860);
const g = P.settle(Object.assign({}, t), D2, 24899);
ok(f.status === 'open' && f.fill === 24852 && f.entry === 95 && f.due === 24876 && g.status === 'closed' && Math.abs(g.net - (99/95 - 1 - 0.0012)) < 1e-6, 'H1: a fill at the limit, then the sale at the close 24 hours after the fill hour, net of 0.12%', { f, g });
const h3 = P.settle({ sym:'X', rule:'H3', t:24850, entry:100 }, D2, 24899);
ok(h3.status === 'closed' && Math.abs(h3.net - (D2.c[24874 - D2.h0]/100 - 1 - 0.002)) < 1e-6, 'H3: bought at the signal close, sold 24 hours later, net of 0.20%', h3);
const crash = coin(900, rows => { for(let i = 840; i < 900; i++){ rows[i].c *= i >= 848 ? 0.8 : 1; rows[i].lo = rows[i].c*0.97; rows[i].hi = rows[i].c*1.01; } });
const thc = {}; for(let d = 1000; d <= 1037; d++){ const T = P.dayTh(crash, d); if(T) thc[d] = T; }
const made = P.runCoin('X', crash, thc, {}, 24840, 24899, [], 24000);
const h1s = made.filter(x => x.rule === 'H1');
ok(h1s.length >= 1 && h1s[0].t <= 24848 && made.some(x => x.status === 'closed') && h1s.every((x, i) => i === 0 || x.t >= (h1s[i - 1].fill != null ? h1s[i - 1].fill + 24 : h1s[i - 1].t + 3)) && made.every(x => x.rule !== 'H3'), 'a falling coin fires H1 (by the crash at the latest), later signals wait their turn (3 hours unfilled, 24 hours after a fill), and H3 stays quiet without market-wide panic', made.map(x => [x.rule, x.t, x.status, x.fill]));
const young = P.runCoin('X', crash, thc, {}, 24840, 24899, [], 24300);
ok(young.length === 0, 'a coin listed under 30 days gives no signal');
// 3. in the app
(async () => {
  const pw = require('playwright'), b = await pw.chromium.launch(), nh = Math.floor(Date.now()/H);
  const route = async r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue(); const j = x => r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(!/binance/.test(u.hostname)) return j([]); const q = u.searchParams, sym = q.get('symbol'), iv = q.get('interval'), n = +(q.get('limit') || 100);
    if(/ticker\/24hr/.test(u.pathname)) return j(Array.from({ length:45 }, (_, i) => ({ symbol:'C' + i + 'USDT', quoteVolume:String(1e9 - i*1e6) })).concat([{ symbol:'USDCUSDT', quoteVolume:'9e9' }]));
    if(/exchangeInfo/.test(u.pathname)) return j({ symbols:[] });
    if(/\/klines$/.test(u.pathname)){ const step = iv === '15m' ? H/4 : iv === '1d' ? 24*H : H, end = iv === '1d' ? Math.floor(Date.now()/(24*H))*24*H : nh*H; const k = +(sym || 'C0').replace(/\D/g, '') || 0;
      return j(Array.from({ length:n }, (_, i) => { const tt = end - (n - i)*step, hh = Math.floor(tt/H); let c = 100*Math.exp(0.02*Math.sin(hh/9 + k) + 0.01*Math.sin(hh/2.3 + 2*k));
        if(iv === '1h' && hh >= nh - 6 && k < 15) c *= 0.82;                       // a market-wide panic in the last hours: 15 of 40 coins
        return [tt, String(c), String(c*1.004), String(c*0.996), String(c), '1000', 0, '100000', 0, '500', '50000']; })); }
    if(/\/depth$/.test(u.pathname)) return j({ bids:[['99.9', '10']], asks:[['100.1', '10']] });
    if(/premiumIndex/.test(u.pathname)) return j({ markPrice:'100', indexPrice:'100', lastFundingRate:'0.0001' }); return j([]); };
  for(const vp of [{ width:412, height:915, name:'phone' }, { width:1280, height:900, name:'desktop' }]){
    const ctx = await b.newContext({ viewport:{ width:vp.width, height:vp.height } }); await ctx.route('**/*', route);
    const SHIFT = (Date.now() % H) < 200e3 ? 300e3 : 0; if(SHIFT) await ctx.addInitScript(s => { const n0 = Date.now; Date.now = () => n0() + s; }, SHIFT);
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000);
    if(vp.name === 'phone'){
      let sc = null; for(let k = 0; k < 60; k++){ sc = await pg.evaluate(() => { const S = window.OMEGA_PANIC.state(); return { busy:S.busy, scans:S.scans, msg:S.msg, br:S.breadth, live:window.OMEGA_PANIC.live().map(t => [t.sym, t.rule, t.status]), honest:window.OMEGA_PANIC.live().every(t => { const T = (S.th[t.sym] || {})[Math.floor(t.t/24)]; return T && t.r24 <= (t.rule === 'H1' ? T.q10 : T.q5); }) }; }); if(!sc.busy && sc.scans >= 1) break; await pg.waitForTimeout(1500); }
      ok(sc.scans >= 1 && sc.br && sc.br.v >= 0.2 && Array.from({ length:15 }, (_, i) => 'C' + i + 'USDT').every(c => sc.live.some(x => x[0] === c)) && sc.honest, 'in the app: the hourly scan reads the planted market-wide panic (breadth ≥ 20%), flags every planted coin, and every coin it flags is really below its own panic line', { n:sc.live.length, honest:sc.honest, br:sc.br, msg:sc.msg });
      await pg.evaluate(() => navigate('today')); await pg.waitForTimeout(2000);
      const v = await pg.evaluate(() => (document.querySelector('.verdict') || {}).innerText || '');
      ok(/Grade B/.test(v) && /Panic bounce|Holding/.test(v) && /small seat/.test(v) && /not yet confirmed/.test(v) && /E26/.test(v), 'Today: with no Grade A climax, the verdict raises the Grade B panic bounce, labelled unconfirmed, with small seats', v);
      await pg.screenshot({ path:'/tmp/prime_panic_today.png', fullPage:false });
      await pg.evaluate(() => navigate('signals')); await pg.waitForTimeout(1500);
      const s = await pg.evaluate(() => ({ t:(document.getElementById('panicBody') || {}).innerText || '', g:!!document.querySelector('#panicBody svg.pgauge') }));
      ok(/Panic-bounce watch/.test(s.t) && /Grade B/.test(s.t) && s.g && /Forward record/.test(s.t), 'Signals: the panic-bounce watch with its breadth gauge, open orders and forward record', s.t.slice(0, 300));
      await pg.screenshot({ path:'/tmp/prime_panic_signals.png', fullPage:true });
      await pg.evaluate(() => navigate('evidence')); await pg.waitForTimeout(1500);
      const e = await pg.evaluate(() => document.getElementById('page-evidence').innerText);
      ok(/Panic bounce H1 \(E22, E25\) · Grade B/.test(e) && /t 4\.54/.test(e) && /Market-wide panic H3/.test(e) && /PASSED\s*Survivorship test/.test(e) && /FAILED\s*Many small seats \(E26\)/.test(e) && /drawdowns of 56% and 59%/.test(e) && /FAILED\s*The daily-trading search \(E28\): 12,480 rules/.test(e) && /Hour-of-day timing/.test(e) && /Timing BTC and ETH from market-wide gauges/.test(e) && /100 → 1,588/.test(e) && /Timing BTC and ETH from market-wide gauges/.test(e) && /100 → 1,588/.test(e) && /panic bounce H1 \d+ and H3 \d+ of 50/.test(e), 'Evidence: H1 and H3 as Grade B with E25’s result and caveats, the survivorship test passed, E26 failed with its numbers, and the forward counts', e.slice(0, 200));
      await pg.evaluate(() => navigate('signals')); await pg.waitForTimeout(1200); await pg.click('#panicBody [data-pbn="100"]'); await pg.waitForTimeout(400);
      const sw = await pg.evaluate(async () => { const P = window.OMEGA_PANIC, n = P.NN(); P.state().lastH = null; await P.scan(); return { n, msg:P.state().msg, txt:document.getElementById('panicBody').innerText }; });
      ok(sw.n === 100 && /Scanned 45 coins/.test(sw.msg) && /82% of days/.test(sw.txt) && /100 coins/.test(sw.txt), 'the 40/100 switch: tapping 100 makes the next scan cover every coin available (45 here), and the card explains how often H1 fills', sw);
      const jobs = await pg.evaluate(() => window.OMEGA_OPERATOR.list().map(j => j.id)), keys = await pg.evaluate(() => Object.keys(localStorage));
      ok(['climax', 'panic', 'mread', 'dplan', 'cockpit', 'rguard', 'truth'].every(j => jobs.includes(j)) && keys.every(k => k.startsWith('prime:')) && keys.includes('prime:prime_panic_v1'), 'the Autopilot runs the panic job, and its record is stored under “prime:”', { jobs, keys });
    } else { await pg.evaluate(() => navigate('signals')); await pg.waitForTimeout(2500); await pg.screenshot({ path:'/tmp/prime_panic_desktop.png', fullPage:false }); }
    const wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    ok(!wide && errs.length === 0, vp.name + ': no horizontal overflow and no page errors', { wide, errs });
    await ctx.close(); }
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
