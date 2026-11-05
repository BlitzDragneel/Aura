// v6.5.70 checks: the Edge Lab. The engine reproduces the research code; no look-ahead; conditions and exits; the explorer
// never proposes anything already tested; the protocol (screen, check, book, promotion, retirement); the wide store's merge.
const fs = require('fs'), path = require('path'), D = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-70.html'), 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const store = {}; global.window = {}; global.document = { getElementById: () => null }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; const realST = setTimeout; global.setTimeout = (f, ms) => ms === 0 ? realST(f, 0) : 0;
new Function(grab('EDGE LIBRARY'))(); const L = window.OMEGA_EDGELIB;
// 1. parity with the research code on the 25 studied coins
const recs = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/wide25.json'), 'utf8')), ref = Object.assign(JSON.parse(fs.readFileSync(path.join(D, 'fixtures/r12_stage1_ref.json'), 'utf8')), JSON.parse(fs.readFileSync(path.join(D, 'fixtures/r12_exact_ref.json'), 'utf8')));
const END = Date.UTC(2026, 9, 12)/864e5, S0 = Date.UTC(2020, 0, 1)/864e5, G = L.grid(recs, END); let bad = [];
for(const nm of L.BASES.map(b => b.name).concat(['harvest 10 pairs, hurdle 0.10%/week', 'harvest 15 pairs, hurdle 0.20%/week'])){ const m = nm.match(/^harvest (\d+) pairs, hurdle ([\d.]+)%/);
  const S = L.judge(G, L.run(G, m ? { kind:'harvest', h:{ k:+m[1], hurdle:+m[2]/100 } } : { base:nm }), S0, END), P = ref[nm];
  if(!(Math.abs(S.alpha - P.alpha) < 0.02 && Math.abs(S.z - P.z) < 0.02 && Math.abs(S.costs2x - P.costs2x) < 0.02 && S.ypos === P.ypos)) bad.push(nm); }
ok(bad.length === 0, 'all 40 rules reproduce the research code on the 25 studied coins (alpha, z, costs doubled, years); funding rules on exact sums, cross-coin ties by name' + (bad.length ? ': ' + bad.join(', ') : ''));
// 2. no look-ahead: changing prices and funding after a day never changes the weights up to that day
function clone(rs){ return JSON.parse(JSON.stringify(rs)); }
const cut = END - 400, rs2 = clone(recs); rs2.forEach(r => { for(let i=0; i<r.c.length; i++){ const d = r.k0 + i; if(d > cut && r.c[i] != null){ const f = 1 + 0.3*Math.sin(i); r.c[i] *= f; r.h[i] *= f*1.01; r.l[i] *= f*0.99; r.v[i] = (r.v[i] || 0)*2; r.tb[i] = (r.tb[i] || 0)*1.7; r.ff[i] = -r.ff[i]*3; } } });
const G2 = L.grid(rs2, END); bad = [];
const probe = L.BASES.map(b => ({ base:b.name })).concat(['mkt_up', 'fund_high', 'calm', 'breadth_up', 'align', 'cheap', 'old', 'liquid'].map(c => ({ base:'TSMOM 30d LS', cond:c }))).concat(['t5', 't20', 'atr3'].map(e => ({ base:'RSI(5) 10/90 revert LF', exit:e }))).concat([{ kind:'fundprice', mode:'LS' }, { kind:'agexs', mode:'LS' }, { base:'XS carry 7d (short high funding)', cond:'disp_high' }]);
for(const c of probe){ const a = L.run(G, c, { wantW:true }), b = L.run(G2, c, { wantW:true }); const t1 = cut - G.K0; let same = true; for(let j=0; j<a.W.length && same; j++) for(let t=0; t<=t1; t++) if(Math.abs(a.W[j][t] - b.W[j][t]) > 1e-15){ same = false; break; } if(!same) bad.push(c.base || c.kind); }
const H1 = L.harvest(G, { k:10, hurdle:0.001, exitNeg:-0.001 }), H2 = L.harvest(G2, { k:10, hurdle:0.001, exitNeg:-0.001 }); let hs = true; for(let t=0; t<=cut - G.K0; t++) if(Math.abs((H1.gross[t] - H1.cost[t]) - (H2.gross[t] - H2.cost[t])) > 1e-15) hs = false;
ok(bad.length === 0 && hs, 'no look-ahead: ' + probe.length + ' rules, conditions and exits (and a guarded harvest) give identical positions up to a day when everything after it is changed' + (bad.length ? ': ' + bad.join(', ') : ''));
// 3. conditions and exits
const X = L._, T = G.T, j0 = G.syms.indexOf('BTCUSDT'), sig = new Float64Array(T).fill(1), up = G.ctx.mkt_up;
const fc = X.applyCond(G, j0, sig, 'mkt_up'); ok(fc.every((v, t) => v === (up[t] ? 1 : 0)), 'a market condition passes the signal only while it holds');
const neg = new Float64Array(T).fill(-1), al = X.applyCond(G, j0, neg, 'align'); ok(al.every((v, t) => v === (G.ctx.mkt_down[t] ? -1 : 0)), 'trend-aligned: shorts only in a down market');
const one = new Float64Array(T).fill(0); for(let t=100; t<130; t++) one[t] = 1; for(let t=140; t<150; t++) one[t] = 1;
const e5 = X.applyExit(G, j0, one, 't5'); ok(e5[100] === 1 && e5[104] === 1 && e5[105] === 0 && e5[129] === 0 && e5[140] === 1 && e5[145] === 0, 'a 5-day time stop closes after 5 days and waits for a fresh signal');
// 4. the explorer never proposes anything already tested
new Function(grab('EDGE LAB').replace(/__KNOWLEDGE__/, '{}'))(); const KN = window.OMEGA_EDGELAB.KNOWLEDGE;
const c1 = L.candidates(KN.tested, {}, 1), c2 = L.candidates(KN.tested, {}, 2);
ok(KN && Object.keys(KN.tested).length === 630 && Object.keys(KN.combos).length === 105 && KN.lessons.length >= 8, 'built-in knowledge: 630 tested rule keys, 105 combinations, ' + KN.earlier.length + ' earlier studies, ' + KN.lessons.length + ' lessons');
ok(c1.length > 2800 && c2.length > c1.length && c2.every(c => !KN.tested[c.key]) && new Set(c2.map(c => c.key)).size === c2.length, 'explorer: ' + c1.length + ' untested candidates in tier 1, ' + c2.length + ' with tier 2; none in the knowledge; no duplicates');
ok(Object.keys(KN.tested).filter(k => !/\|none\|own$/.test(k) && L.BASES.some(b => k.startsWith(b.name + '|'))).every(k => !c2.some(c => c.key === k)), 'the regime-filtered combinations round 12 tested are skipped');
// 5. bars and forward judgement
const E = window.OMEGA_EDGELAB; ok(Math.abs(E.bar(1) - 1.6449) < 1e-3 && Math.abs(E.bar(140) - 3.3840) < 2e-3 && Math.abs(E.bar(100) - 3.2905) < 2e-3, 'Bonferroni bars: 1 → 1.645, 100 → 3.29, 140 → 3.38 (as research)');
ok(['BTCUSDT', 'ETHUSDT', 'SOLUSDT'].map(E.half).join() === ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'].map(E.half).join() && L.BASES.length === 38, 'halves are fixed by name; 38 base rules');
// 6. the protocol on synthetic coins: one planted edge (14-day momentum) among noise candidates
(async () => {
  let seed = 7; const rnd = () => { seed = (seed*1103515245 + 12345) % 2147483648; return seed/2147483648; }, gauss = () => Math.sqrt(-2*Math.log(rnd() + 1e-12))*Math.cos(2*Math.PI*rnd());
  const K0 = Date.UTC(2020, 0, 1)/864e5, NT = 2300, syn = [];
  for(let i=0; i<80; i++){ const c = [], h = [], l = [], v = [], tb = [], ff = [], fcn = [], r = []; let px = 100;
    for(let t=0; t<NT; t++){ let m = 0; for(let q=Math.max(0, t-14); q<t; q++) m += r[q]; const ri = 0.004*Math.sign(m) + 0.03*gauss(); r.push(ri); px *= 1 + ri; c.push(px); h.push(px*1.01); l.push(px*0.99); v.push(1000); tb.push(500); ff.push(0.0003); fcn.push(3); }
    syn.push({ sym:'C' + i + 'USDT', k0:K0, c, h, l, v, tb, ff, fc:fcn }); }
  const SG = L.grid(syn, K0 + NT), A = [], B = []; SG.syms.forEach((s, j) => (E.half(s) === 'A' ? A : B).push(j));
  const gc = { G:SG, GA:L.subgrid(SG, A), GB:L.subgrid(SG, B), lastDay:SG.K0 + SG.T - 1 };
  const meta = {}; window.OMEGA_WIDE = { getMeta:async k => meta[k], putMeta:async (k, v) => { meta[k] = JSON.parse(JSON.stringify(v)); }, version:() => 1, all:async () => [], status:async () => null };
  const list = [{ base:'TSMOM 14d LS', cond:'calm' }, { base:'TSMOM 14d LS', exit:'t20' }, { base:'RSI(2) 10/90 revert LF', exit:'t5' }, { base:'reversal 1d LS', cond:'mkt_up' }, { base:'Bollinger revert 20, 2.0 sd LF', cond:'old' }, { base:'OBV > its SMA 20 LS', cond:'fund_low' }, { base:'XS low vol 60d LS', cond:'calm' }];
  list.forEach(c => { c.key = c.base + '|' + (c.cond || 'none') + '|' + (c.exit || 'own'); c.tier = 1; });
  L.candidates = () => list; await E._.load(); const st = E.state(); st.tier = 2; st.phase = 'screen';
  while(st.phase !== 'done' && st.phase !== 'coins') await E._.explore(gc, 1e9, Date.now());
  const inBook = Object.keys(st.book).filter(k => !st.book[k].research);
  ok(st.surv.includes('TSMOM 14d LS|calm|own') && inBook.includes('TSMOM 14d LS|calm|own') && inBook.includes('TSMOM 14d LS|none|t20') && inBook.every(k => k.startsWith('TSMOM')), 'protocol on synthetic coins: the planted edge passes half A and half B and enters the shadow book; noise does not (survivors ' + st.surv.length + ', book ' + inBook.join(', ') + ')');
  ok(Math.abs(st.s2['TSMOM 14d LS|calm|own'][6] - E.bar(st.surv.length)) < 0.01, 'the check on half B used the bar over all ' + st.surv.length + ' survivors (z ≥ ' + E.bar(st.surv.length).toFixed(2) + ')');
  // forward judgement: inject forward weeks
  const k = 'TSMOM 14d LS|calm|own', start = st.book[k].start; st.fwd[k] = {}; for(let w=0; w<12; w++) st.fwd[k][start + 6 + 7*w] = [0.01 + 0.002*Math.sin(w), 0.0];
  let J = E._.judgeFwd(k); ok(J.code === 'EDGE' && J.S.n === 12, 'promotion: 12 strong forward weeks clear the bar over the book (' + Object.keys(st.book).length + ' entries, z ≥ ' + J.bar.toFixed(2) + ') → EDGE');
  st.fwd[k] = {}; for(let w=0; w<5; w++) st.fwd[k][start + 6 + 7*w] = [0.05, 0]; J = E._.judgeFwd(k); ok(J.code === 'SHADOW', 'under 8 forward weeks it stays in the shadow book, however good');
  st.fwd[k] = {}; for(let w=0; w<4; w++) st.fwd[k][start + 6 + 7*w] = [-0.05, 0]; st.stat[k] = {}; J = E._.judgeFwd(k); ok(J.code === 'RETIRED', 'a 15% forward fall retires it'); st.stat[k] = J; J = E._.judgeFwd(k); ok(J.code === 'RETIRED', 'and a retired rule stays retired');
  const P = E._.positions(SG, { base:'TSMOM 14d LS' }, 1000); ok(Object.keys(P.dir).length > 0 && Object.values(P.dir).every(v => Math.abs(v) < 1000/SG.syms.length*1.5 + 1e-9), 'positions for an edge: USDT per coin within 1/N × 1.5 of the account');
  // 7. the wide store's merge
  new Function(grab('WIDE DATA STORE').replace('__FINAL3__', '[]'))(); const M = window.OMEGA_WIDE._.merge, day = 864e5, k1 = [], now = Date.UTC(2026, 9, 18, 12);
  for(let d=0; d<10; d++){ const t = Date.UTC(2026, 9, 5 + d); k1.push([t, '1', '2', '0.5', String(1 + d), '100', t + day - 1, '0', 0, '40', '0', '0']); }
  const fund = []; for(let d=-2; d<10; d++) for(let q=0; q<3; q++) fund.push([Date.UTC(2026, 9, 5 + d, q*8), 0.0001*(q + 1)]);
  let R = M(null, 'XUSDT', k1, fund, now); ok(R.k0 === Date.UTC(2026, 9, 3)/day && R.c[2] === 1 && R.c[0] === null && Math.abs(R.ff[0] - 0.0006) < 1e-12 && R.fc[0] === 3 && R.tb[2] === 40, 'store: funding before the first bar extends the record back; day sums and counts; taker volume kept');
  const k2 = [[Date.UTC(2026, 9, 14), '1', '2', '0.5', '99', '100', 0, '0', 0, '40', '0', '0'], [Date.UTC(2026, 9, 15), '1', '2', '0.5', '11', '100', 0, '0', 0, '40', '0', '0']], f2 = [[Date.UTC(2026, 9, 15, 0), 0.0005], [Date.UTC(2026, 9, 14, 16), 0.0003]];
  R = M(R, 'XUSDT', k2, f2, now); const i14 = Date.UTC(2026, 9, 14)/day - R.k0; ok(R.c[i14] === 99 && R.c[i14 + 1] === 11 && Math.abs(R.ff[i14] - 0.0006) < 1e-12 && R.fc[i14] === 3 && R.fc[i14 + 1] === 1 && R.f1 === Date.UTC(2026, 9, 15, 0), 'store: an update overwrites the last days and re-adds a known payment once (no double count)');
  // 8. the store end to end on an IndexedDB stand-in: a coin not stored yet reads as nothing (the bug the v6.5.70 browser test found), then fills and updates
  global.indexedDB = require('/home/claude/fake_idb.js')(); const DAYm = 864e5, nowT = Date.UTC(2026, 9, 18, 12);
  global.fetch = async (url) => { const u = new URL(url), sym = u.searchParams.get('symbol'), st = +u.searchParams.get('startTime'), en = +u.searchParams.get('endTime'), out = [];
    if(/klines/.test(url)){ for(let t = Date.UTC(2026, 6, 1); t <= en && t < Date.UTC(2026, 9, 18); t += DAYm) if(t >= st) out.push([t, '1', '2', '0.5', '1.5', '10', t + DAYm - 1, '0', 1, '4', '0', '0']); }
    else { for(let t = Date.UTC(2026, 6, 1); t <= en && t < nowT; t += 8*3600e3) if(t >= st) out.push({ fundingTime:t, fundingRate:'0.00010000' }); }
    return { ok:true, status:200, json:async () => out.slice(0, 1000) }; };
  const WS = window.OMEGA_WIDE; ok((await WS.get('NOPEUSDT')) === undefined, 'store: a coin not stored yet reads as nothing (not the request object)');
  const saveDN = Date.now; Date.now = () => nowT; global.setTimeout = realST;   // real timers for the store's pacing
  const r1 = await WS.runNow(0); const recA = await WS.get('BTCUSDT'); Date.now = saveDN;
  const st2 = await WS.status(); ok(st2.stored === st2.coins && st2.coins === 150 && recA && recA.c.filter(x => x != null).length === 109 && Math.abs(recA.ff[0] - 0.0003) < 1e-12 && recA.fc[0] === 3, 'store: every listed coin downloaded and saved (here 25 studied + 125 untouched; BTC 109 daily bars, funding 3 a day) — ' + (r1.text || r1.error));
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
