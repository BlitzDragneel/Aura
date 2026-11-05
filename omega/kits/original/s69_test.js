// v6.5.69 checks: the round-12 winners in the app reproduce the research code day by day on the 25 coins; blends, positions,
// flags; desk and research record; the harvest's negative-funding warning.
const fs = require('fs'), path = require('path'), D = __dirname, R = '/home/claude/research/';
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-69.html'), 'utf8');
function mod(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); const store = {}; global.window = {}; global.document = { getElementById: () => null };
  global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0; new Function(m[1])(); }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/r12_data.json'), 'utf8')), py = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/r12_py_daily.json'), 'utf8'));
mod('ROUND 12 WINNERS'); const X = window.OMEGA_R12, END = Date.UTC(2026, 9, 12)/864e5;
const G = X.grid(data, END), P = X.parts(G);
const map = { S174:'DIP', S419:'FNEG', S285:'ST', S033:'SMA', S480:'H10', S484:'H15' };
for(const [sid, part] of Object.entries(map)){
  const ref = py[sid]; let n = 0, mx = 0, bad = 0, sumJ = 0, sumP = 0;
  for(const [k, v] of Object.entries(ref)){ const t = +k - G.K0; const j = P[part].ret[t]; n++; const d = Math.abs(j - v); if(d > mx) mx = d; if(d > 1e-9) bad++; sumJ += j; sumP += v; }
  const harvest = part[0] === 'H', sma = part === 'SMA';   // SMA 10/50: on exact ties of the two averages (ETC, 28 Feb 2023: equal to 4e-15) float rounding decides the sign, differently in pandas
  ok(n === 2476 && (harvest ? bad <= 30 : sma ? (bad <= 60 && Math.abs(sumJ - sumP)/n*365.25 < 5e-4) : mx < 1e-10), sid + ' ' + part + ': ' + n + ' days, largest difference ' + mx.toExponential(1) + ', days differing ' + bad + (harvest ? ' (harvest ties broken by exact sums here, by float noise in pandas)' : '') + '; a year ' + (100*sumJ/n*365.25).toFixed(2) + '% vs ' + (100*sumP/n*365.25).toFixed(2) + '%');
}
// the blends: weekly results as the research code would sum them
const res = X.compute(data, { now:Date.UTC(2026, 9, 12, 6), endDay:END });
for(const id of ['C028', 'C016']){ const spec = py._combos[id], parts = X.BLENDS[id].parts; ok(parts.length === spec.members.length && parts.every((p, i) => map[spec.members[i]] === p[0] && p[1] === spec.w[i]), id + ': parts and weights are exactly the frozen ones');
  let pyDaily = {}; spec.members.forEach((m, i) => { for(const [k, v] of Object.entries(py[m])) pyDaily[k] = (pyDaily[k] || 0) + spec.w[i]*v; });
  const pyAnn = Object.values(pyDaily).reduce((a, b) => a + b, 0)/Object.keys(pyDaily).length*365.25, wk = res.blends[id].weeks.filter(w => w[0] >= Date.UTC(2020, 0, 5)/864e5), jsAnn = wk.reduce((a, w) => a + w[1], 0)/wk.length*52;
  ok(Math.abs(jsAnn - pyAnn) < 0.003, id + ': ' + (100*jsAnn).toFixed(2) + '% a year in the app vs ' + (100*pyAnn).toFixed(2) + '% in the research code (' + wk.length + ' weeks)'); }
// positions and flags
const pos = X.positions(res, 'C028', 100); ok(pos.pairs && pos.pairs.hold.length <= 10 && Math.abs(pos.pairs.each - 5) < 1e-9 && Object.values(pos.dir).every(v => v > 0), 'C028 positions: ' + pos.pairs.hold.length + ' harvest pairs at 5.00 USDT each (half of 100 over 10), dip-buy legs long only (' + Object.keys(pos.dir).length + ' now)');
const pos2 = X.positions(res, 'C016', 100); ok(pos2.pairs && Math.abs(pos2.pairs.each - 100*0.5356612887226874/15) < 1e-9, 'C016 positions: harvest pairs at ' + pos2.pairs.each.toFixed(2) + ' USDT each');
const d2 = JSON.parse(JSON.stringify(data)), held = pos.pairs.hold[0], last = Math.max(...Object.values(d2).map(x => x.fund.length ? x.fund[x.fund.length - 1][0] : 0));
d2[held].fund.push([last - 3600e3, -0.004]); const fl = X.flags(X.compute(d2, { now:Date.UTC(2026, 9, 12, 6), endDay:END }), [held]);
ok(fl.negative.length === 1 && fl.negative[0][0] === held, 'a held coin paying −0.4% within 24 hours is flagged (' + held + ')');
ok(X.flags(res, pos.pairs.hold).negative.length === 0 && X.flags(res, pos.pairs.hold).stale.length === 0, 'no flag on the real fixture');
ok(X.verdict({ n:0 }, null).code === 'WAIT' && X.verdict({ n:30, mean:0.001, t:2.5, worstFall:-0.02 }).code === 'CONFIRMED' && X.verdict({ n:5, mean:0.001, worstFall:-0.12 }).code === 'RETIRE', 'forward judgement as fixed');
ok(!/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(JSON.stringify(X.report())), 'report carries no credential-like field');
// harvest warning
mod('FUNDING HARVEST'); const H = window.OMEGA_HARVEST, cd = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8')); const NOW = Date.UTC(2026, 9, 18, 1, 30);
const h0 = H.compute(cd, { now:NOW, rec:{}, k:10, keep:20 }); ok(Array.isArray(h0.current.negative) && h0.current.negative.length === 0, 'harvest: no negative-funding warning on the real fixture');
const cd2 = JSON.parse(JSON.stringify(cd)), hs = Object.keys(h0.current.hold)[0], lf = Math.max(...Object.values(cd2).map(x => (x.fund || []).length ? x.fund[x.fund.length - 1][0] : 0)); cd2[hs].fund.push([lf - 3600e3, -0.005]);
const h1 = H.compute(cd2, { now:NOW, rec:{}, k:10, keep:20 }); ok(h1.current.negative.length === 1 && h1.current.negative[0][0] === hs, 'harvest: a held coin paying −0.5% within 24 hours is warned about (' + hs + ')');
// desk and record
mod('POSITIONING DESK'); const PR = window.OMEGA_POSDESK.report(); ok(PR.round12 && PR.round12.winners.length === 2 && PR.round12.families.passed === 2, 'desk round 12: two winners');
const F = JSON.parse(fs.readFileSync(R + 'round12_final.json', 'utf8')); ok(F.passed.sort().join() === 'C016,C028' && Math.abs(F.results.C028.z - 3.31) < 1e-9 && Math.abs(F.results.C016.z - 3.90) < 1e-9 && X.BLENDS.C028.final.z === F.results.C028.z && X.BLENDS.C016.final.z === F.results.C016.z && X.BLENDS.C028.final.alpha === F.results.C028.alpha && X.BLENDS.C016.final.alpha === F.results.C016.alpha && X.BLENDS.C028.final.costs2x === F.results.C028.costs2x && X.BLENDS.C016.final.costs2x === F.results.C016.costs2x && X.BLENDS.C028.final.worst === F.results.C028.worst && X.BLENDS.C016.final.worst === F.results.C016.worst, 'final-test figures in the app match round12_final.json');
ok(/round:'12'/.test(html), 'research record carries round 12');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
