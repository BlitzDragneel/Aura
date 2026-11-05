// v6.5.72 checks: the capitulation watch reproduces the research engine (round 14, family 1) trade for trade on the
// 25 studied coins' last 3,000 hours; no look-ahead; weeks and the forward judgement.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D0, 'omega-v6_5-72.html'), 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const store = {}; global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
new Function(grab('EDGE LIBRARY'))(); new Function(grab('CAPITULATION WATCH'))(); const W = window.OMEGA_CAPWATCH, X = W._;
const fx = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/capwatch25.json'), 'utf8'));
function data(f){ return { h0:f.h0, syms:f.syms, c:f.c, o:f.o, pr:f.pr, F:f.F, first:f.first }; }
function run(D, w0, w1){ const fired = {}; for(let t = w0; t < w1; t++){ const f = X.firesAt(D, t); if(f.length) fired[t] = f; } return X.book(D, fired); }
// 1. trade for trade
const D = data(fx), T = run(D, fx.window[0], fx.window[1]);
const ref = fx.trades, same = T.length === ref.length && T.every((tr, k) => tr.t === ref[k][0] && tr.sym === ref[k][1] && Math.abs(tr.z - ref[k][2]) < 1e-9 && Math.abs(tr.ret - ref[k][3]) < 1e-12);
ok(same, 'the watch takes the same ' + ref.length + ' trades as the research engine on the 25 studied coins (hour, coin, depth of fall, return after funding)', { js:T.slice(0, 3).map(t => [t.t, t.sym, t.z, t.ret]), py:ref.slice(0, 3) });
ok(T.every(tr => Math.abs(tr.net - (tr.ret - 0.002)) < 1e-12) && W.RULE.slots === 20 && W.RULE.w === 0.05 && W.RULE.hold === 12 && W.RULE.k === 5 && W.RULE.q === 0.05, 'costs 0.10% a side; 20 slots of 5%; hold 12 hours; 5 sigma; 5th percentile (as PLAN14)');
// 2. no look-ahead: change every price and premium after an hour; decisions up to 13 hours before it do not change
const cut = fx.window[0] + 1800, D2 = data(JSON.parse(JSON.stringify(fx)));
for(let j=0; j<D2.syms.length; j++) for(let h = cut; h < D2.c[j].length; h++){ if(D2.c[j][h] != null){ D2.c[j][h] *= 1 + 0.2*Math.sin(h + j); D2.o[j][h] *= 1 - 0.1*Math.cos(h); } if(D2.pr[j][h] != null) D2.pr[j][h] = -0.01*Math.abs(Math.sin(h*j)); }
const T2 = run(D2, fx.window[0], fx.window[1]), early = tr => tr.t < cut - 13;
ok(JSON.stringify(T.filter(early).map(t => [t.t, t.sym, t.ret])) === JSON.stringify(T2.filter(early).map(t => [t.t, t.sym, t.ret])) && T.filter(early).length > 10, 'no look-ahead: changing everything after an hour leaves every earlier decision and its return unchanged');
// 3. slots and holding: never more than 20 open, never the same coin twice at once
let maxOpen = 0, dup = false; for(let h = fx.window[0]; h < fx.window[1] + 13; h++){ const op = T.filter(tr => tr.e <= h && h <= tr.x); maxOpen = Math.max(maxOpen, op.length); if(new Set(op.map(tr => tr.sym)).size !== op.length) dup = true; }
ok(maxOpen <= 20 && !dup, 'the book never holds more than 20 trades or one coin twice (most at once here: ' + maxOpen + ')');
// 4. live use: the entry bar not closed yet means an open trade without a price; the last close marks it
const D3 = data(JSON.parse(JSON.stringify(fx))), tl = T[T.length - 1], cutE = tl.e; D3.c = D3.c.map(c => c.slice(0, cutE)); D3.o = D3.o.map(c => c.slice(0, cutE));
const T3 = X.book(D3, { [tl.t]: X.firesAt(D3, tl.t) }); const t3 = T3.find(tr => tr.sym === tl.sym);
ok(t3 && t3.entry === undefined && t3.status === undefined && t3.ret === undefined, 'a signal on the last closed hour is taken with its entry still to come (bought at the next open)');
const D4 = data(JSON.parse(JSON.stringify(fx))); D4.c = D4.c.map(c => c.slice(0, tl.e + 5)); D4.o = D4.o.map(c => c.slice(0, tl.e + 5)); const t4 = X.book(D4, { [tl.t]: X.firesAt(D4, tl.t) }).find(tr => tr.sym === tl.sym);
ok(t4 && t4.status === 'open' && t4.entry > 0 && Math.abs(t4.markRet - (D4.c[D4.syms.indexOf(tl.sym)][tl.e + 4]/t4.entry - 1)) < 1e-12, 'an open trade is marked at the latest close');
// 5. weeks end on Sunday (UTC), and the forward record counts only decisions after the freeze
const sun = Date.UTC(2026, 9, 18, 12)/3600e3, mon = Date.UTC(2026, 9, 19, 1)/3600e3; ok(X.weekOf(sun) === Math.floor(sun/24) && X.weekOf(mon) === Math.floor(sun/24) + 7, 'weeks run Monday to Sunday (UTC)');
const fwd = X.forward(D, T, fx.h0 + fx.c[0].length); ok(fwd.trades === 0 && W.FREEZE_H === Date.UTC(2026, 9, 19)/3600e3, 'decisions before 19 Oct 2026 do not count in the forward record');
const Dsh = Object.assign({}, D, { h0: D.h0 + (W.FREEZE_H - (D.h0 + fx.window[0])) });   // pretend the window began at the freeze
const f2 = X.forward(Dsh, T, Dsh.h0 + fx.c[0].length + 24*7);
const P = X.hourlyPnl(Dsh, T.filter(tr => tr.t + Dsh.h0 >= W.FREEZE_H), 1, fx.c[0].length), sumP = Object.values(P).reduce((a, b) => a + b, 0), sumT = T.reduce((a, tr) => a + 0.05*tr.net, 0);
ok(f2.trades === T.length && Math.abs(sumP - sumT) < 1e-9 && f2.weeks > 10 && isFinite(f2.alpha) && isFinite(f2.z), 'forward record: hourly P&L adds up to the trades (5% each, after costs and funding); ' + f2.weeks + ' weeks judged against the market (alpha ' + (100*f2.alpha).toFixed(1) + '%/yr, z ' + (f2.z || 0).toFixed(2) + ')', { sumP, sumT, f2 });
ok(W.STATUS() === 'FAILED' && W.EVIDENCE.final && W.EVIDENCE.final.z === -0.27 && W.EVIDENCE.final.coins === 324 && /omega_capwatch_cfg_v2/.test(html), 'after its final test it is shown as FAILED (324 untouched coins, z \u22120.27), with the watch off by default');
store['omega_capwatch_cfg_v2'] = undefined; ok(JSON.parse(localStorage.getItem('omega_capwatch_cfg_v2') || 'null') === null && /if\(STATUS !== 'FAILED'\) newT\.filter/.test(html), 'a failed rule sends no alerts');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
