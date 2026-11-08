// v6.5.78 checks: the climax reversal watch reproduces the research engine (round 16, family G, hold 12h) trade for
// trade on the 25 studied coins' densest 3,000 hours; its measurements match; no look-ahead; book limits; live use; the
// forward record; the card; the record and knowledge.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D0, 'omega-v6_5-78.html'), 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const store = {}; global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
/* v6.5.109: the edge library was removed; climax uses its own nwT */ if(html.indexOf('/* ═══ EDGE LIBRARY') > -1) new Function(grab('EDGE LIBRARY'))(); new Function(grab('CLIMAX REVERSAL'))(); const W = window.OMEGA_CLIMAX, X = W._;
const fx = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/climax25.json'), 'utf8'));
function data(f){ return { h0:f.h0, syms:f.syms, c:f.c, o:f.o, h:f.h, l:f.l, v:f.v, F:f.F, first:f.first }; }
function run(D, w0, w1){ const fired = {}; for(let t = w0; t < w1; t++){ const f = X.firesAt(D, t); if(f.length) fired[t] = f; } return X.book(D, fired); }
// 1. trade for trade, and the same measurements
const D = data(fx), T = run(D, fx.window[0], fx.window[1]), ref = fx.trades;
const same = T.length === ref.length && T.every((tr, k) => tr.t === ref[k][0] && tr.sym === ref[k][1] && Math.abs(tr.z - ref[k][2]) < 1e-9 && Math.abs(tr.ret - ref[k][3]) < 1e-12);
ok(same, 'the watch takes the same ' + ref.length + ' trades as the research engine on the 25 studied coins (hour, coin, depth of fall, return after funding)', { js:T.slice(0, 3).map(t => [t.t, t.sym, t.z, t.ret]), py:ref.slice(0, 3), n:[T.length, ref.length] });
ok(T.every((tr, k) => Math.abs(tr.vr - ref[k][4]) < 1e-9 && Math.abs(tr.loc - ref[k][5]) < 1e-12), 'volume against its 168-hour median and the close’s place in the hour’s range match research exactly');
ok(T.every(tr => Math.abs(tr.net - (tr.ret - 0.002)) < 1e-12) && W.RULE.slots === 20 && W.RULE.w === 0.05 && W.RULE.hold === 12 && W.RULE.k === 3 && W.RULE.vk === 3 && W.RULE.lk === 0.6, 'costs 0.10% a side; 20 slots of 5%; hold 12 hours; 3 sigma, 3x volume, top 40% of the hour (as PLAN16 addendum A)');
// 2. no look-ahead
const cut = fx.window[0] + 1500, D2 = data(JSON.parse(JSON.stringify(fx)));
for(let j=0; j<D2.syms.length; j++) for(let h = cut; h < D2.c[j].length; h++){ if(D2.c[j][h] != null){ D2.c[j][h] *= 1 + 0.2*Math.sin(h + j); D2.o[j][h] *= 1 - 0.1*Math.cos(h); D2.h[j][h] = Math.max(D2.c[j][h], D2.o[j][h])*1.05; D2.l[j][h] = Math.min(D2.c[j][h], D2.o[j][h])*0.9; D2.v[j][h] = (D2.v[j][h] || 1)*7; } }
const T2 = run(D2, fx.window[0], fx.window[1]), early = tr => tr.t < cut - 13;
ok(JSON.stringify(T.filter(early).map(t => [t.t, t.sym, t.ret])) === JSON.stringify(T2.filter(early).map(t => [t.t, t.sym, t.ret])) && T.filter(early).length > 10, 'no look-ahead: changing every price and volume after an hour leaves every earlier decision and its return unchanged');
// 3. book limits
let maxOpen = 0, dup = false; for(let h = fx.window[0]; h < fx.window[1] + 13; h++){ const op = T.filter(tr => tr.e <= h && h <= tr.x); maxOpen = Math.max(maxOpen, op.length); if(new Set(op.map(tr => tr.sym)).size !== op.length) dup = true; }
ok(maxOpen <= 20 && !dup, 'the book never holds more than 20 trades or one coin twice (most at once here: ' + maxOpen + ')');
// 4. live use
const tl = T[T.length - 1], D3 = data(JSON.parse(JSON.stringify(fx))); ['c', 'o', 'h', 'l', 'v'].forEach(f => { D3[f] = D3[f].map(a => a.slice(0, tl.e)); });
const t3 = X.book(D3, { [tl.t]: X.firesAt(D3, tl.t) }).find(tr => tr.sym === tl.sym);
ok(t3 && t3.entry === undefined && t3.status === undefined, 'a signal on the last closed hour waits for its entry (bought at the next open)');
const D4 = data(JSON.parse(JSON.stringify(fx))); ['c', 'o', 'h', 'l', 'v'].forEach(f => { D4[f] = D4[f].map(a => a.slice(0, tl.e + 5)); }); const t4 = X.book(D4, { [tl.t]: X.firesAt(D4, tl.t) }).find(tr => tr.sym === tl.sym);
ok(t4 && t4.status === 'open' && t4.entry > 0 && Math.abs(t4.markRet - (D4.c[D4.syms.indexOf(tl.sym)][tl.e + 4]/t4.entry - 1)) < 1e-12, 'an open trade is marked at the latest close');
// 5. forward record
ok(W.FREEZE_H === Date.UTC(2026, 9, 19, 12)/3600e3 && X.forward(D, T, fx.h0 + fx.c[0].length).trades === 0, 'only decisions from 19 Oct 2026 12:00 UTC count forward');
const Dsh = Object.assign({}, D, { h0: D.h0 + (W.FREEZE_H - (D.h0 + fx.window[0])) }), f2 = X.forward(Dsh, T, Dsh.h0 + fx.c[0].length + 24*7);
const P = X.hourlyPnl(Dsh, T.filter(tr => tr.t + Dsh.h0 >= W.FREEZE_H), 1, fx.c[0].length), sumP = Object.values(P).reduce((a, b) => a + b, 0), sumT = T.reduce((a, tr) => a + 0.05*tr.net, 0);
ok(f2.trades === T.length && Math.abs(sumP - sumT) < 1e-9 && f2.weeks > 10 && isFinite(f2.alpha), 'forward record: hourly P&L adds up to the trades; ' + f2.weeks + ' weeks judged against the market');
// 6. the card, the record, the knowledge
const card = X.html(); ok(W.STATUS() === 'EDGE' && /passed its final test on 324 untouched coins/.test(card) && /z 2\.35 against a bar of 2\.326/.test(card) && /passed the final bar only just/.test(card) && !/NaN|undefined/.test(card), 'the card states the rule, all three results, and that it passed only just');
if(html.indexOf('/* ═══ EDGE LAB (v6.5.70)') > -1) ok(html.includes("{ round:'16',") && /climax reversal/.test(html) && html.includes('"r":"16"') && /earlier studies \(rounds 1–1[6-9], CREED,/.test(html), 'research record and built-in knowledge include round 16');   // v6.5.109: the research record and Edge Lab left the app
if(html.indexOf('/* ═══ EDGE LAB (v6.5.70)') > -1) ok(/climaxWatchBody/.test(grab('CLIMAX REVERSAL')) && /edgelabBody/.test(grab('CLIMAX REVERSAL')), 'the watch is on the Edge Lab and on Market Watch');
else ok(/el\('climaxSigBody'\)/.test(grab('CLIMAX REVERSAL')) && !/edgelabBody/.test(grab('CLIMAX REVERSAL')), 'v6.5.109: the watch lives on the Signals page');
ok(!/c047445f|apikey=/i.test(grab('CLIMAX REVERSAL')), 'no key in the watch');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
