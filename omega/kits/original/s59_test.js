// v6.5.59 checks: the funding harvest (passed its untouched test) as the app computes it; carry relabelled; desk results.
const fs = require('fs'), path = require('path'), D = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-59.html'), 'utf8');
function mod(name, freeze){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name + ' not found'); let src = m[1]; if(freeze) src = src.replace('Date.UTC(2026, 9, 18)/DAY', freeze + '/DAY');
  const store = {}; global.window = global.window || {}; global.document = { getElementById: () => null }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0;
  new Function(src)(); return src; }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8')), py = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/harvest_py_weeks.json'), 'utf8'));
const DAY = 864e5, NOW = Date.UTC(2026, 9, 18, 1, 30);
mod('FUNDING HARVEST'); let H = window.OMEGA_HARVEST; const res = H.compute(data, { now:NOW, rec:{} });
const js = {}; res.weeks.forEach(q => { js[new Date(q.end*DAY).toISOString().slice(0, 10)] = q; });
let n = 0, diffs = []; py.forEach(([t, r, ne, w]) => { if(ne < 5 || !js[t]) return; n++; if(Math.abs(js[t].r - r) > 1e-12) diffs.push(t); });
// a difference is allowed only where the Python code broke an exact tie at the cut by set order
const P = H.prep(data), U = Object.keys(P).sort(), tieOnly = diffs.every(t => { const a = Date.parse(t + 'T00:00:00Z')/DAY - 7, C = H.choose(P, U, a, {}), v = Object.values(C.v).sort((x, y) => y - x); return v[4] === v[5]; });
ok(n === 153 && diffs.length <= 1 && tieOnly, 'identical to the Python test code on ' + n + ' weeks, except ' + diffs.length + ' week(s) with an exact tie at the 5th place (' + diffs.join(',') + ')');
ok(Math.abs(res.before.cum - 0.1922) < 0.001 && res.before.worstFall > -0.006 && res.before.n === 153, 'before the freeze on the stored history: ' + (100*res.before.cum).toFixed(1) + '% in all over ' + res.before.n + ' weeks, worst fall ' + (100*res.before.worstFall).toFixed(2) + '%');
ok(res.current && res.current.a === Date.UTC(2026, 9, 11)/DAY && Object.keys(res.current.hold).length === 5 && res.forward.n === 0, 'this week: decided 11 Oct, 5 pairs held; no forward week yet');
// hurdle and keep rules on synthetic coins
const syn = {}, k0 = 20000; for(let i=0;i<12;i++){ const s = 'C' + String(i).padStart(2, '0') + 'USDT', f = [], rate = (i < 5 ? 2e-4 : i < 7 ? 1e-4 : 2e-5) ; for(let d=k0; d<k0+60; d++) for(const h of [0, 8, 16]) f.push([d*DAY + h*3600e3, rate]); syn[s] = { k0, c:new Array(60).fill(10), fund:f }; }
const SP = H.prep(syn), SU = Object.keys(SP).sort(), a0 = k0 + 49;
const c1 = H.choose(SP, SU, a0, {}); ok(Object.keys(c1.hold).length === 5 && c1.hold.C00USDT && !c1.hold.C05USDT, 'holds the 5 coins paying the most above 0.1% a week');
const low = {}; Object.keys(syn).forEach(s => { low[s] = { k0, c:syn[s].c, fund:syn[s].fund.map(x => [x[0], 2e-5]) }; }); const c2 = H.choose(H.prep(low), SU, a0, {}); ok(Object.keys(c2.hold).length === 0, 'holds nothing when no coin pays above 0.1% a week (2e-5 every 8 h is about 0.04%)');
const held = { C07USDT:1 }; const c3 = H.choose(SP, SU, a0, held); ok(!c3.hold.C07USDT && Object.keys(c3.hold).length === 5, 'a held coin outside the top 5 gives way when 5 better coins clear the hurdle (keep only fills spare places)');
const mid = {}; Object.keys(syn).forEach((s, i) => { mid[s] = { k0, c:syn[s].c, fund:syn[s].fund.map(x => [x[0], i < 3 ? 2e-4 : i < 8 ? 9e-5 : 2e-5]) }; });
const c4 = H.choose(H.prep(mid), SU, a0, { C06USDT:1 }); ok(c4.hold.C06USDT && Object.keys(c4.hold).length === 4, 'a held coin ranked inside the top 10 with positive funding stays when fewer than 5 coins make the top 5 (tied coins share rank 6)');
// forward record with an earlier freeze (for this check only)
global.window = {}; mod('FUNDING HARVEST', 'Date.UTC(2026, 6, 5)'); const HF = window.OMEGA_HARVEST, rf = HF.compute(data, { now:NOW, rec:{} });
ok(rf.forwardAll.n === 14 && Object.keys(rf.newRec).length === 15, 'with a 5 Jul freeze: 14 forward weeks and 15 recorded holdings (' + rf.forwardAll.n + ', ' + Object.keys(rf.newRec).length + ')');
const V = H.verdict; ok(V({ n:0 }).code === 'WAIT' && V({ n:10, mean:0.001, t:3, worstFall:-0.01 }).code === 'COLLECT' && V({ n:30, mean:-0.0001, t:-1, worstFall:-0.01 }).code === 'RETIRE' && V({ n:30, mean:0.001, t:2.5, worstFall:-0.01 }).code === 'CONFIRMED' && V({ n:3, mean:-0.03, worstFall:-0.11 }).code === 'RETIRE' && V({ n:30, mean:0.001, t:1, worstFall:-0.01 }).code === 'HOLDING', 'judgement: wait, collect to 26 weeks, retire at <= 0 or a 10% fall, confirm at z >= 1.96');
ok(!/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(JSON.stringify(H.report())), 'harvest report has no credential-like field');
// carry: relabelled, fresh-coin result carried
global.window = {}; mod('FUNDING CARRY, WEEKLY'); const X = window.OMEGA_CARRYXS;
ok(X.RESEARCH.freshCoins && X.RESEARCH.freshCoins.passed === false && Math.abs(X.RESEARCH.freshCoins.t - 1.70) < 1e-9 && /not an edge/i.test(html.match(/FUNDING CARRY, WEEKLY[\s\S]*?<\/script>/)[0]) && !/the one rule that passed the research/.test(html), 'carry: fresh-coin fail recorded, labelled not an edge, no "passed" wording left');
// desk
global.window = {}; mod('POSITIONING DESK'); const PD = window.OMEGA_POSDESK, R = PD.report();
ok(R.freshTest && R.freshTest.rows.length === 4 && R.freshTest.rows.filter(r => r.passed).length === 1 && R.btcEth && R.btcEth.funding.BTC.every(y => y[1] > 0), 'desk: 4 fresh-coin results (1 pass), BTC/ETH funding positive every year');
ok(html.includes('<div id="harvestCard"></div>') && html.includes("'carryxs','harvest'") && html.includes('harvestRule: safe(function(){ return window.OMEGA_HARVEST') && html.includes('omega_harvest_v1:1') && html.includes("one rule passed an untouched test: the funding harvest"), 'harvest card, research job, report field, store and research record are wired');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
