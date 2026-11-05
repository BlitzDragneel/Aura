// v6.5.98 checks: the panic-bounce watch (E22 H1/H3, grade B). Parity with the research engine, live behaviour, the app.
const fs = require('fs'), path = require('path'), H = 3600e3;
const FILE = process.argv[2] || path.join(__dirname, 'omega-v6_5-98.html'), html = fs.readFileSync(FILE, 'utf8');
const PAR = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'panic_parity.json'), 'utf8'));
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = { localStorage:{ getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } } }; global.document = { getElementById:() => null, createElement:() => ({}), head:{ appendChild(){} } };
global.setInterval = () => 0; global.setTimeout = () => 0; global.Notification = undefined;
new Function(grab('PANIC BOUNCE \\(v6\\.5\\.98'))(); const P = window.OMEGA_PANIC._;
ok(/v6\.5\.(9[89]|1\d\d) · build/.test(html) && html.split('PANIC BOUNCE (v6.5.98').length === 2, 'build v6.5.98 carries the panic-bounce watch once');
const coins = Object.entries(PAR.markets).map(([sym, rows]) => { const D = P.dense(rows.map(r => ({ h:r[0], hi:r[1], lo:r[2], c:r[3] })));
  const th = {}; for(let d = Math.floor(D.h0/24); d <= Math.floor((D.h0 + D.n)/24); d++){ const T = P.dayTh(D, d); if(T) th[d] = T; } return { sym, D, th, first:D.h0 }; });
const lastH = Math.max(...coins.map(C => C.D.h0 + C.D.n - 1)), h0 = Math.min(...coins.map(C => C.D.h0)), br = {};
for(let h = h0; h <= lastH; h++){ const b = P.breadthAt(coins, h); if(b != null) br[h] = b; }
const all = []; coins.forEach(C => all.push(...P.runCoin(C.sym, C.D, C.th, br, h0, C.D.h0 + C.D.n - 1, [], C.first)));
for(const rule of ['H1', 'H3']){ const mine = all.filter(t => t.rule === rule && t.status === 'closed').map(t => [t.sym, t.t, +t.net.toFixed(6)]).sort(), ref = PAR.trades[rule].map(r => [r[0], r[1], +r[2].toFixed(6)]).sort();
  const diff = ref.filter((r, i) => !mine[i] || mine[i][0] !== r[0] || mine[i][1] !== r[1] || Math.abs(mine[i][2] - r[2]) > 2e-6);
  ok(mine.length === ref.length && !diff.length, rule + ': exactly the research engine’s ' + ref.length + ' trades (coin, hour, result after costs)', { mine:mine.length, ref:ref.length, diff:diff.slice(0, 3) }); }
ok(P.rowsOf([[3600e3, '1', '1.1', '0.9', '1', '5'], [7200e3, '1', '1', '1', '1', '0']]).length === 1, 'a volume-0 candle counts as missing (halts; the flat candles Binance keeps writing after a delisting)');
function coin(n, f){ const rows = []; for(let i = 0; i < n; i++){ const c = 100*(1 + 0.01*Math.sin(i*0.7)); rows.push({ h:24000 + i, hi:c*1.003, lo:c*0.997, c }); } f && f(rows); return P.dense(rows); }
const t0 = { sym:'X', rule:'H1', t:24850, close:100, limit:95 }, D = coin(900), D2 = coin(900, r => { r[852].lo = 94; r[876].c = 99; });
const f = P.settle(Object.assign({}, t0), D2, 24860), g = P.settle(Object.assign({}, t0), D2, 24899);
ok(P.settle(Object.assign({}, t0), D, 24851).status === 'pending' && P.settle(Object.assign({}, t0), D, 24853).status === 'missed' && f.status === 'open' && f.fill === 24852 && g.status === 'closed' && Math.abs(g.net - (99/95 - 1 - 0.0012)) < 1e-6, 'H1: pending for 3 hours, missed without a trade below the limit; a fill, then the sale 24 hours after the fill hour, net of 0.12%');
(async () => {
  global.setTimeout = realST; global.setInterval = realSI; const pw = require('playwright'), b = await pw.chromium.launch(), nh = Math.floor(Date.now()/H);
  const route = async r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue(); const j = x => r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(!/fapi\.binance/.test(u.hostname)) return j([]); const q = u.searchParams, sym = q.get('symbol'), iv = q.get('interval'), n = +(q.get('limit') || 100);
    if(/ticker\/24hr/.test(u.pathname)) return j(Array.from({ length:45 }, (_, i) => ({ symbol:'C' + i + 'USDT', quoteVolume:String(1e9 - i*1e6) })));
    if(/exchangeInfo/.test(u.pathname)) return j({ symbols:[] });
    if(/\/klines$/.test(u.pathname) && iv === '1h'){ const end = nh*H, k = +(sym || 'C0').replace(/\D/g, '') || 0;
      return j(Array.from({ length:Math.min(n, 1500) }, (_, i) => { const tt = end - (Math.min(n, 1500) - i)*H, hh = Math.floor(tt/H); let c = 100*Math.exp(0.02*Math.sin(hh/9 + k) + 0.01*Math.sin(hh/2.3 + 2*k));
        if(hh >= nh - 6 && k < 15 && /^C\d+USDT$/.test(sym || '')) c *= 0.82; return [tt, String(c), String(c*1.004), String(c*0.996), String(c), '1000', 0, '100000', 0, '500', '50000']; })); }
    return j([]); };
  const ctx = await b.newContext({ viewport:{ width:412, height:915 } }); await ctx.route('**/*', route);
  const SHIFT = (Date.now() % H) < 200e3 ? 300e3 : 0; if(SHIFT) await ctx.addInitScript(s => { const n0 = Date.now; Date.now = () => n0() + s; }, SHIFT);
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000);
  const reg = await pg.evaluate(() => (window.OMEGA_OPERATOR.list ? window.OMEGA_OPERATOR.list() : window.OMEGA_OPERATOR.jobs()).map(j => j.id));
  await pg.evaluate(async () => { await window.OMEGA_OPERATOR.tick('panic'); });
  let sc; for(let k = 0; k < 60; k++){ sc = await pg.evaluate(() => { const S = window.OMEGA_PANIC.state(); return { busy:S.busy, scans:S.scans, msg:S.msg, br:S.breadth, live:window.OMEGA_PANIC.live().map(t => [t.sym, t.rule, t.status]), honest:window.OMEGA_PANIC.live().every(t => { const T = (S.th[t.sym] || {})[Math.floor(t.t/24)]; return T && t.r24 <= (t.rule === 'H1' ? T.q10 : T.q5); }), res:(window.OMEGA_OPERATOR.state().jobs.panic || {}).result }; }); if(!sc.busy && sc.scans >= 1) break; await pg.waitForTimeout(1500); }
  ok(reg.includes('panic') && reg.includes('climax') && sc.scans >= 1 && sc.br && sc.br.v >= 0.2 && Array.from({ length:15 }, (_, i) => 'C' + i + 'USDT').every(c => sc.live.some(x => x[0] === c)) && sc.honest, 'in the app: the Autopilot job “panic” scans, reads the planted market-wide panic, flags every planted coin, and every coin it flags is really below its own panic line', { n:sc.live.length, honest:sc.honest, br:sc.br });
  const pages = {}; for(const [p, id] of [['osig', 'panicSigBody'], ['edgelab', 'panicBody'], ['watch', 'panicWatchBody']]){ await pg.evaluate(p => navigate(p), p); await pg.waitForTimeout(2500);
    pages[p] = await pg.evaluate(id => { const e = document.getElementById(id), prev = e && e.previousElementSibling; return { t:e ? e.innerText : null, g:!!(e && e.querySelector('svg.pgauge')), after:prev ? prev.id : null }; }, id); }
  await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(800); await pg.evaluate(() => { const e = document.getElementById('panicSigBody'); if(e) e.scrollIntoView(); }); await pg.screenshot({ path:'/tmp/v98_osig.png' });
  ok(Object.values(pages).every(x => x.t && /Panic bounce/i.test(x.t) && /GRADE B/i.test(x.t) && /E25/.test(x.t) && /t 4\.54/.test(x.t) && x.g && !/\bNaN\b|\bundefined\b/.test(x.t)) && pages.osig.after === 'climaxSigBody', 'Signals, Edge Lab and Watch: the card under the climax reversal, grade B with E22 and E25’s evidence, the gauge, no NaN or undefined', Object.fromEntries(Object.entries(pages).map(([k, v]) => [k, { after:v.after, g:v.g, t:(v.t || '').slice(0, 80) }])));
  const keys = await pg.evaluate(() => Object.keys(localStorage)), wide = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  ok(keys.includes('omega_panic_v1') && !keys.some(k => /^prime[:_]/.test(k)) && !wide && errs.length === 0, 'its record is stored as omega_panic_v1 (nothing of Prime’s); no horizontal overflow and no page errors', { wide, errs, keys:keys.filter(k => /panic/.test(k)) });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
