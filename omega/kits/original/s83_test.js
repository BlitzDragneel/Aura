// v6.5.83 checks: the Breakout Desk reproduces the research live-account simulator (edge/live.py) trade for trade on 40
// perpetuals (Jul–Sep 2025), hour by hour as the app runs it; no look-ahead; the plan's arithmetic; the judging rules;
// the page in a browser with a fake exchange whose coin breaks out in US hours.
const fs = require('fs'), path = require('path'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-83.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 600) : '')); } }
const store = {}; global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } };
const realST = global.setTimeout, realSI = global.setInterval; global.setInterval = () => 0; global.setTimeout = f => { if(typeof f === 'function') f(); return 0; };
new Function(grab('EDGE LIBRARY'))(); new Function(grab('BREAKOUT DESK'))(); const W = window.OMEGA_BDESK, X = W._;
const fx = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/bdesk40.json'), 'utf8'));
const recs = () => fx.coins.map(c => ({ sym:c.sym, h0:c.h0, first:c.first, o:c.o.slice(), h:c.h.slice(), l:c.l.slice(), c:c.c.slice(), qv:c.qv.slice(), fund:c.fund.slice() }));
function same(L, ref){ if(L.length !== ref.trades.length) return { n:[L.length, ref.trades.length] }; for(let k=0; k<L.length; k++){ const a = L[k], b = ref.trades[k]; if(a.sym !== b.sym || a.hr !== b.hr || a.out !== b.out || Math.abs(a.R - b.R) > 1e-9 || Math.abs(a.eq - b.eq) > 1e-7) return { k, js:a, py:b }; } return null; }
(async () => {
  // 1. trade for trade against the research simulator
  for(const k of ['A', 'B']){ const R = X.replay(recs(), k, fx.ev0, fx.ev1, 100, 0.01), bad = same(R.trades, fx.ref[k]);
    ok(!bad && Math.abs(R.end - fx.ref[k].end) < 1e-7, 'setup ' + k + ': the same ' + fx.ref[k].trades.length + ' paper trades as the research simulator (coin, hour, exit, R, balance); 100 → ' + R.end.toFixed(2) + ' USDT', bad); }
  // 2. hour by hour, as the app runs it: each check sees bars up to its hour only; funding comes from the exchange
  const all = recs(), by = {}; all.forEach(r => by[r.sym] = r); let calls = 0;
  global.fetch = async url => { calls++; const u = new URL(url), r = by[u.searchParams.get('symbol')], a = +u.searchParams.get('startTime'), b = +u.searchParams.get('endTime'), out = [];
    for(let i=0; i<r.c.length; i++){ const t = (r.h0 + i)*H; if(t >= a && t <= b && r.fund[i] !== 0) out.push({ fundingTime:t, fundingRate:String(r.fund[i]) }); } return { ok:true, status:200, json:async () => out }; };
  const realNow = Date.now; let seed = 5; const rnd = () => (seed = (seed*16807) % 2147483647)/2147483647;
  for(const k of ['A', 'B']){ const A = X.newAcct(k); A.free = fx.ev0; A.lastH = fx.ev0 - 1; let t = fx.ev0, end = fx.ev1 + 200;
    while(t < end){ let last = Math.min(t + 1 + Math.floor(rnd()*30), end); if(t < fx.ev1 - 1 && last > fx.ev1 - 1) last = fx.ev1 - 1; Date.now = () => (last + 1)*H + 300e3;
      const view = all.map(r => { const n = Math.max(0, Math.min(r.c.length, last - r.h0 + 1)); return { sym:r.sym, h0:r.h0, first:r.first, o:r.o.slice(0, n), h:r.h.slice(0, n), l:r.l.slice(0, n), c:r.c.slice(0, n), qv:r.qv.slice(0, n) }; }), vb = {}; view.forEach(r => vb[r.sym] = r);
      await X.stepAcct(A, view, vb, last); t = last; if(t >= fx.ev1 - 1) A.free = 1e12; }
    Date.now = realNow; const bad = same(A.log, fx.ref[k]);
    ok(!bad && Math.abs(A.eq - fx.ref[k].end) < 1e-7, 'setup ' + k + ': hour by hour with random gaps between checks (1–30 hours) and funding from the exchange, the same trades and balance', bad); }
  ok(calls > 50, 'funding for each open trade is read from Binance (' + calls + ' requests)');
  // 3. no look-ahead
  const cut = fx.ev0 + 1200, R2 = recs(); R2.forEach((r, j) => { for(let i = cut - r.h0; i < r.c.length; i++){ if(i < 0) continue; r.c[i] *= 1 + 0.15*Math.sin(i + j); r.o[i] *= 1 - 0.1*Math.cos(i); r.h[i] = Math.max(r.c[i], r.o[i])*1.04; r.l[i] = Math.min(r.c[i], r.o[i])*0.95; r.qv[i] *= 6; } });
  const a1 = X.replay(recs(), 'A', fx.ev0, fx.ev1).trades.filter(t => t.out < cut), a2 = X.replay(R2, 'A', fx.ev0, fx.ev1).trades.filter(t => t.out < cut);
  ok(a1.length > 20 && JSON.stringify(a1) === JSON.stringify(a2), 'no look-ahead: changing every bar from an hour on leaves every trade that closed before it unchanged (' + a1.length + ' trades)');
  // 4. the plan's arithmetic
  const P = X.plan('A', 1, 0.01, 1, 100, 1), P10 = X.plan('A', 1, 0.01, 1, 10, 1), PB = X.plan('B', 2, 0.02, -1, 100, 1);
  ok(Math.abs(P.unitN - 10) < 1e-9 && P.units.length === 5 && Math.abs(P.total - 50) < 1e-9 && Math.abs(P.riskEff - 1) < 1e-9 && Math.abs(P.stop - 0.98) < 1e-12 && Math.abs(P.r1 - 1.02) < 1e-12 && Math.abs(P.r3 - 1.06) < 1e-12 && !P.units[0].bumped,
    'setup A on 100 USDT at 1%: 5 units of 10 USDT, stop 2 ATR below, +1R/+2R/+3R above, 1% at risk');
  ok(P10.units.every(u => u.bumped && u.n === 5) && Math.abs(P10.riskEff - 5) < 1e-9, 'on 10 USDT the 5 USDT minimum makes the same plan 5% at risk, and the plan says so');
  ok(PB.units.length === 1 && Math.abs(PB.stop - 2.04) < 1e-12 && Math.abs(PB.r1 - 1.96) < 1e-12 && Math.abs(PB.riskEff - 1) < 1e-9, 'setup B short: 1 unit, stop above, adds below');
  // 5. judging
  const savedFail = W.SETUPS.A.failed; delete W.SETUPS.A.failed;   // v6.5.84 marks A failed; the judging rules underneath are tested on their own
  const A0 = X.newAcct('A'); ok(X.verdict(A0).status === 'TOO EARLY' && W.FREEZE_H === Date.UTC(2026, 9, 20, 3)/H, 'nothing is judged before 26 new weeks; the record starts 20 Oct 2026 03:00 UTC');
  const A1 = X.newAcct('A'); A1.weeks[X.weekOf(W.FREEZE_H)] = 100; A1.peak = 100; A1.eq = 50; A1.log = []; A1.retired = null;
  const fakeMark = (A, v) => { A.weeks[X.weekOf(W.FREEZE_H + 200)] = v; A.peak = Math.max(A.peak, v); if(1 - v/A.peak >= W.SETUPS[A.key].retire) A.retired = { why:'fell' }; }; fakeMark(A1, 50);
  ok(X.verdict(A1).status === 'RETIRED' && W.SETUPS.A.retire === 0.46 && W.SETUPS.B.retire === 0.56, 'retired on a fall of 1.5× the worst research fall (46% for A, 56% for B)');
  if(savedFail) W.SETUPS.A.failed = savedFail;
  // 6. the card with a live signal: no gaps in the numbers, the plan's levels drawn
  const st = W.state(), r0 = recs()[0]; st.recs = [r0]; const tSig = r0.h0 + 1500;
  st.accts = { A:Object.assign(X.newAcct('A'), { pend:{ t:tSig, c:[{ sym:r0.sym, t:tSig, d:1, pr:3 }] } }), B:X.newAcct('B') }; const page = X.html();
  ok(/SIGNAL — LONG/.test(page) && ['entry', 'stop', 'r1', 'r2', 'r3', 'box'].every(k => page.includes('data-level="' + k + '"')) && /close 3 units; stop to entry; add 1/.test(page) && !/NaN|undefined|Infinity/.test(page), 'a signal shows the chart with entry, stop, +1R/+2R/+3R and the 72-hour line, and the 5-unit order table');
  ok(/Candidates, not an edge|FAILED a clean test/.test(page) && /about 1 time in 3/.test(page) && /beat 96% of 100/.test(page) && /half the starts went to zero/.test(page), 'the page says plainly it is not an edge, and why');
  ok(html.includes('id="page-bdesk"') && html.includes("data-page=\"bdesk\"") && /var EXTRA = \[[^\]]*'bdesk'/.test(html) && html.includes('<div id="bdeskSigBody"></div>') && html.includes("['bdesk','Breakout Desk']") && html.includes("{ round:'19',") && !/c047445f|apikey=/i.test(grab('BREAKOUT DESK')), 'page, menu entry, navigation, OMEGA Signals line, command palette, research record round 19; no key in the module');
  // 7. in a browser: the clock at 20 Oct 2026 23:30 UTC; a coin breaks out on the 17:00 UTC hour
  global.setTimeout = realST; global.setInterval = realSI; let pw = null; try{ pw = require('playwright'); }catch(e){}
  if(!pw){ ok(false, 'playwright not found (set NODE_PATH)'); }
  else { const FAKE = Date.UTC(2026, 9, 20, 23, 30), SIG = Date.UTC(2026, 9, 20, 17)/H;
    const price = (sym, h) => { let p = (sym === 'BTCUSDT' ? 60000 : sym === 'ETHUSDT' ? 3000 : 2)*Math.exp(0.002*Math.sin(h*0.7) + 0.0015*Math.sin(h*1.3)); if(sym === 'BRKUSDT' && h >= SIG) p *= 1.03*(1 + 0.0012*(h - SIG)); return p; };
    const kl = (sym, startTime, limit) => { const end = Math.floor(FAKE/H) - 1, n = Math.min(limit || 500, 1000), t0 = startTime ? Math.max(Math.floor(+startTime/H), end - 3000) : end - n + 1, out = [];
      for(let h = t0; h <= end && out.length < n; h++){ const o = price(sym, h - 1), c = price(sym, h), v = sym === 'BRKUSDT' ? (h === SIG ? 1000000 : 200000) : 300000; out.push([h*H, o.toFixed(6), (Math.max(o, c)*1.0008).toFixed(6), (Math.min(o, c)*0.9992).toFixed(6), c.toFixed(6), String(v), h*H + H - 1, String(v*c), 100, String(v*0.5), String(v*0.5*c), '0']); } return out; };
    const b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
    await ctx.addInitScript(f => { const D = Date, off = f - D.now(); class FD extends D { constructor(...a){ if(a.length) super(...a); else super(D.now() + off); } static now(){ return D.now() + off; } } window.Date = FD; }, FAKE);
    await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const q = u.searchParams, j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
      if(!/binance/.test(u.hostname)) return route.abort();
      if(/exchangeInfo$/.test(u.pathname)) return j({ symbols:['BTCUSDT', 'ETHUSDT', 'BRKUSDT', 'CALMUSDT'].map(s => ({ symbol:s, contractType:'PERPETUAL', quoteAsset:'USDT', baseAsset:s.replace('USDT', ''), status:'TRADING', underlyingType:'COIN', onboardDate:Date.UTC(2024, 0, 1) })) });
      if(/klines$/.test(u.pathname) && q.get('interval') === '1h') return j(kl(q.get('symbol'), q.get('startTime'), +q.get('limit')));
      if(/fundingRate$/.test(u.pathname)) return j([]);
      return j([]); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000);
    await pg.evaluate(() => navigate('bdesk')); await pg.waitForTimeout(1500);
    await pg.evaluate(() => window.OMEGA_BDESK.check(true)); await pg.waitForTimeout(1500);
    const r = await pg.evaluate(() => { const e = document.getElementById('page-bdesk'), S = window.OMEGA_BDESK.state(), A = S.accts || {};
      return { text:e.innerText, active:e.classList.contains('active'), levels:Array.from(e.querySelectorAll('svg.bd-chart line[data-level]')).map(x => x.getAttribute('data-level')), candles:e.querySelectorAll('svg.bd-chart rect').length,
        a:A.A && A.A.pos ? { sym:A.A.pos.sym, eH:A.A.pos.eH, units:A.A.pos.lots.length, e:A.A.pos.e } : null, b:A.B && A.B.pos ? { sym:A.B.pos.sym, eH:A.B.pos.eH } : null, msg:S.msg, wide:document.documentElement.scrollWidth > window.innerWidth }; });
    ok(r.active && r.a && r.a.sym === 'BRKUSDT' && r.a.eH === SIG + 1 && r.a.units >= 2 && r.b && r.b.sym === 'BRKUSDT' && r.b.eH === SIG + 1, 'in the browser: both paper accounts enter BRKUSDT at the 18:00 UTC open after its 17:00 breakout on 5× volume', r);
    ok(/IN A TRADE — LONG BRKUSDT/.test(r.text) && ['entry', 'stop', 'r1', 'r2', 'r3', 'now'].every(k => r.levels.includes(k)) && r.candles > 50 && !/\bNaN\b|\bundefined\b|\bInfinity\b/.test(r.text) && !r.wide && errs.length === 0, 'the page shows the open trade, candles with its levels and the live stop; no NaN, no sideways overflow, no page errors', { levels:r.levels, errs, wide:r.wide, msg:r.msg });
    await pg.evaluate(() => navigate('osig')); await pg.waitForTimeout(800);
    const sig = await pg.evaluate(() => (document.getElementById('bdeskSigBody') || {}).innerText || '');
    ok(/Breakout Desk/.test(sig) && /in BRKUSDT/.test(sig), 'OMEGA Signals carries a line for the desk', sig.slice(0, 200));
    await pg.screenshot({ path:'/tmp/bdesk_page.png', fullPage:false }); await pg.evaluate(() => navigate('bdesk')); await pg.waitForTimeout(600); await pg.screenshot({ path:'/tmp/bdesk_page.png', fullPage:true });
    await b.close(); }
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
