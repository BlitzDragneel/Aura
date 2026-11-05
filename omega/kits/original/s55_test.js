// v6.5.55 checks: the frozen funding-carry rule (carry-xs-7d) as the app computes it.
const fs = require('fs'), path = require('path'), D = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-55.html'), 'utf8');
const m = html.match(/<script>(\/\* ═══ FUNDING CARRY, WEEKLY[\s\S]*?)<\/script>/); if(!m) throw new Error('module not found in build');
function load(freezeOverride){ let src = m[1]; if(freezeOverride) src = src.replace('Date.UTC(2026, 9, 18)/DAY', freezeOverride + '/DAY');
  const store = {}; global.window = {}; global.document = { getElementById: () => null };
  global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0;
  new Function(src)(); return window.OMEGA_CARRYXS; }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8'));
const py = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_py_weeks.json'), 'utf8'));
const DAY = 864e5, NOW = Date.UTC(2026, 9, 18, 1, 30);
// 1. identical to the research implementation, week by week
let X = load(), res = X.compute(data, { now:NOW, rec:{} });
const js = {}; res.weeks.forEach(q => { js[new Date(q.end*DAY).toISOString().slice(0, 10)] = q; });
let n = 0, maxd = 0, sizes = 0; py.forEach(([t, r, nS, nL]) => { if(t < '2023-12-31' || !js[t]) return; n++; maxd = Math.max(maxd, Math.abs(js[t].r - r)); if(js[t].nS !== nS || js[t].nL !== nL) sizes++; });
ok(n >= 146 && maxd < 1e-12 && sizes === 0, 'matches the Python research code on ' + n + ' weeks (largest difference ' + maxd.toExponential(1) + ', basket-size mismatches ' + sizes + ')');
ok(Math.abs(res.before.y26.ann - 1.170) < 0.005 && res.before.y26.n === 41 && Math.abs(res.before.y2425.ann - 0.616) < 0.005, '2026 to the freeze: ' + (100*res.before.y26.ann).toFixed(1) + '% a year over ' + res.before.y26.n + ' weeks; 2024-25: ' + (100*res.before.y2425.ann).toFixed(1) + '%');
ok(res.current && res.current.a === Date.UTC(2026, 9, 11)/DAY && Object.keys(res.current.w).length === 10 && res.forward.n === 0, 'this week\'s basket is the one decided at the close of Sun 11 Oct (10 positions); no forward week yet');
// 2. live edge: data to the close of Sun 11 Oct, funding to its 16:00 -> the 11 Oct basket is current, the week to 11 Oct complete
function cut(lastDay, fundTo, only){ const o = {}; Object.keys(data).forEach(s => { const x = data[s], k = lastDay - x.k0 + 1; o[s] = { k0:x.k0, c:x.c.slice(0, Math.max(0, k)), fund:x.fund.filter(f => f[0] <= ((only && only !== s) ? lastDay*DAY + 16*3600e3 : fundTo)) }; }); return o; }
const d11 = Date.UTC(2026, 9, 11)/DAY;
let r2 = X.compute(cut(d11, d11*DAY + 16*3600e3), { now:Date.UTC(2026, 9, 12, 1, 0), rec:{} });
ok(r2.current && r2.current.a === d11 && new Date(r2.weeks[r2.weeks.length - 1].end*DAY).toISOString().slice(0, 10) === '2026-10-11', 'at 01:00 Monday with Sunday stored: new basket from Sun 11 Oct, last finished week ends 11 Oct');
// 3. one market's funding missing Sunday 16:00 -> no new basket is decided with a market left out
let r3 = X.compute(cut(d11, d11*DAY + 8*3600e3, 'SOLUSDT'), { now:Date.UTC(2026, 9, 12, 1, 0), rec:{} });
ok(r3.current && r3.current.a < d11, 'a market without its Sunday funding holds the new basket back (current stays the 4 Oct basket)');
// 4. forward record: freeze moved back to 5 Jul 2026 for this check only; recorded baskets are kept as first decided
let XF = load('Date.UTC(2026, 6, 5)'), rf = XF.compute(data, { now:NOW, rec:{} });
ok(rf.forward.n === 14 && Object.keys(rf.newRec).length === 15, 'with a 5 Jul freeze: 14 forward weeks finished and 15 baskets recorded (' + rf.forward.n + ', ' + Object.keys(rf.newRec).length + ')');
const rec = JSON.parse(JSON.stringify(rf.newRec)), a0 = Object.keys(rec).sort()[0]; rec[a0].w = { BTCUSDT:0.2, ETHUSDT:-0.2 };
let rg = XF.compute(data, { now:NOW, rec });
ok(rg.recMismatch === 1 && Object.keys(rg.newRec).length === 0 && Math.abs(rg.weeks.find(q => q.a === +a0).r - rf.weeks.find(q => q.a === +a0).r) > 1e-6, 'a recorded basket is used as recorded and the difference from a recount is reported');
// 5. ties share their average rank; under 15 rankable markets holds nothing
const syn = {}, k0 = 20000; for(let i=0;i<16;i++){ const s = 'M' + i + 'USDT', f = [], v = i < 2 ? 3e-4 - i*1e-5 : (i < 8 ? 1e-4 : -i*1e-5); for(let d=k0; d<k0+20; d++) for(const h of [0, 8, 16]) f.push([d*DAY + h*3600e3, v]); syn[s] = { k0, c:new Array(20).fill(100), fund:f }; }
const U = Object.keys(syn), Pz = X.prep(syn), a = k0 + 10, B = X.basketAt(Pz, U, a), nS = Object.values(B.w).filter(x => x < 0).length, nL = Object.values(B.w).filter(x => x > 0).length;
ok(B.n === 16 && nS === 2 && nL === 5, 'six markets tied at ranks 3-8 share rank 5.5 and are left out: 2 shorts, 5 longs');
const B2 = X.basketAt(Pz, U.slice(0, 14), a); ok(B2.n === 14 && Object.keys(B2.w).length === 0, 'with 14 rankable markets the rule holds nothing');
// 6. the forward judgement
const V = X.verdict; ok(V({ n:0 }).code === 'WAIT' && V({ n:10, mean:0.01, t:3, worstFall:-0.05 }).code === 'COLLECT' && V({ n:30, mean:-0.001, t:-1, worstFall:-0.1 }).code === 'RETIRE' && V({ n:30, mean:0.01, t:2.1, worstFall:-0.1 }).code === 'CONFIRMED' && V({ n:30, mean:0.01, t:1.2, worstFall:-0.1 }).code === 'HOLDING' && V({ n:60, mean:0.01, t:1.2, worstFall:-0.1 }).code === 'UNPROVEN' && V({ n:5, mean:-0.05, t:-2, worstFall:-0.26 }).code === 'RETIRE' && V({ n:40, mean:0.01, t:3 }, { at:'2027-01-01T00:00:00Z', why:'x' }).code === 'RETIRED',
  'judgement: wait, collect to 26 weeks, retire at <= 0 or a 25% fall, confirm at z >= 1.96, holding/unproven otherwise, retired stays retired');
// 7. the report carries no credential-like field; the build wires the card, the job and the report
const rep = JSON.stringify(X.report()); ok(!/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(rep), 'report has no credential-like field');
ok(html.includes('<div id="carryxsCard"></div>') && html.includes("'portfolio','workshop','carryxs'") && html.includes('carryRule: safe(function(){ return window.OMEGA_CARRYXS') && html.includes('omega_carryxs_v1:1'), 'card, research job, report field and compressed store are wired');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
