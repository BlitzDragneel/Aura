// v6.5.67 checks: round 10/11 results in the harvest card, desk and research record match the result files; the
// stopped-funding flag; the harvest rule itself unchanged (identical to the Python test code).
const fs = require('fs'), path = require('path'), D = __dirname, R = '/home/claude/research/';
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-67.html'), 'utf8');
function mod(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); const store = {}; global.window = {}; global.document = { getElementById: () => null };
  global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0; new Function(m[1])(); }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8')), py = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/harvest10_py_weeks.json'), 'utf8')), py5 = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/harvest_py_weeks.json'), 'utf8'));
const PB = JSON.parse(fs.readFileSync(R + 'partB_fresh.json', 'utf8'))['141 together'], DL = JSON.parse(fs.readFileSync(R + 'diagB4_delist.json', 'utf8'))['closed when a market stops'], PC = JSON.parse(fs.readFileSync(R + 'partC.json', 'utf8')), F = JSON.parse(fs.readFileSync(R + 'round11.json', 'utf8'));
mod('FUNDING HARVEST'); const H = window.OMEGA_HARVEST, NOW = Date.UTC(2026, 9, 18, 1, 30);
const r10 = H.compute(data, { now:NOW, rec:{}, k:10, keep:20 }), js = {}; r10.weeks.forEach(q => { js[new Date(q.end*864e5).toISOString().slice(0, 10)] = q; });
let n = 0, mx = 0; py.forEach(([t, r, ne]) => { if(ne < 5 || !js[t]) return; n++; mx = Math.max(mx, Math.abs(js[t].r - r)); });
ok(n === 153 && mx < 1e-12, 'rule unchanged: 10-coin harvest identical to the Python test code on ' + n + ' weeks');
const r5 = H.compute(data, { now:NOW, rec:{} }), j5 = {}; r5.weeks.forEach(q => { j5[new Date(q.end*864e5).toISOString().slice(0, 10)] = q; });
let n5 = 0, d5 = 0; py5.forEach(([t, r, ne]) => { if(ne < 5 || !j5[t]) return; n5++; if(Math.abs(j5[t].r - r) > 1e-12) d5++; });
ok(n5 === 153 && d5 <= 1, 'rule unchanged: 5-coin harvest (' + n5 + ' weeks; documented tie weeks differing: ' + d5 + ')');
ok(Array.isArray(r10.current.stale) && r10.current.stale.length === 0, 'no false flag on the real fixture (all coins paying)');
const T3 = H.RESEARCH.wide.third;
ok(T3.annPct === +PB.ann && T3.t === PB.t && T3.costs2xPct === +PB.costs2x && T3.worstFallPct === PB.worst && T3.plainAnnPct === +PB.plain_harvest_ann && PB.passed, 'third test figures match partB_fresh.json (' + T3.annPct + '%, z ' + T3.t + ')');
ok(T3.years.every(y => PB.years[y[0].slice(0, 4)] === y[1]), 'third test years match partB_fresh.json');
ok(T3.closedOnStop.annPct === +DL.ann && T3.closedOnStop.t === DL.t && T3.closedOnStop.worstFallPct === DL.worst, 'closed-on-delisting figures match diagB4_delist.json');
// stopped-funding flag
const DAY = 864e5, now = Date.UTC(2026, 9, 21, 12), syn = {};
['AAAUSDT','BBBUSDT','CCCUSDT','DDDUSDT','EEEUSDT','FFFUSDT'].forEach((c, i) => { const k0 = Math.floor(Date.UTC(2026, 5, 1)/DAY), m = Math.floor(now/DAY) - k0 + 1, fund = [], stop = c === 'AAAUSDT' ? Date.UTC(2026, 9, 20) : now;
  for(let t = Date.UTC(2026, 5, 1); t <= Math.min(stop, now - 3600e3); t += 8*3600e3) fund.push([t, 0.0003*(6 - i)]); syn[c] = { k0, c:Array(m).fill(100), fund }; });
const S5 = H.compute(syn, { now, rec:{} }), S10 = H.compute(syn, { now, rec:{}, k:10, keep:20 });
ok(S5.current.stale.length === 1 && S5.current.stale[0][0] === 'AAAUSDT' && S10.current.stale.length === 1, 'a held coin whose funding stopped 1.5 days ago is flagged (5- and 10-coin)');
const syn2 = JSON.parse(JSON.stringify(syn)); syn2.AAAUSDT.fund = syn.BBBUSDT.fund.map(q => [q[0], 0.0004]); const S6 = H.compute(syn2, { now, rec:{} });
ok(S6.current.stale.length === 0, 'no flag when every coin is paying');
const rep = H.report(); ok(rep.staleNow && rep.research.basis.h10.withBasis === 11.94 && !/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(JSON.stringify(rep)), 'report carries the basis, the stale list and no credential-like field');
ok((html.includes('the one idea that passed untouched tests, three times') || html.includes('passed untouched tests in rounds 7, 8 and 10')   /* v6.5.82 retitled on purpose */) && !html.includes('untouched tests, twice'), 'card title counts the untouched passes');
mod('POSITIONING DESK'); const PR = window.OMEGA_POSDESK.report();
ok(PR.round10 && PR.round10.rows.length === 8 && PR.round10.rows.filter(r => /PASS/.test(r[3])).length === 1 && /z 4\.28/.test(PR.round10.rows[4][2]), 'desk round 10: 8 rows, exactly one pass (B4, z 4.28)');
const c1 = PC['C1 fade the crowd']; ok(!c1.passed && PR.round10.rows[5][2].includes('z ' + c1.test.t.toFixed(2)) && PR.round10.rows[5][1].includes('z ' + c1.design.t.toFixed(2)), 'desk C1 figures match partC.json (design z ' + c1.design.t + ', test z ' + c1.test.t + ', failed)');
ok(!PC['C2 follow the big traders'].passed && !PC['C3 leverage flush'].design_passed, 'C2 failed and C3 out, as in partC.json');
const fx = ['F1 carry', 'F2 trend 3 months', 'F3 trend blend', 'F4 carry + trend'];
ok(PR.round11 && PR.round11.rows.length === 4 && fx.every((k, i) => !F[k].passed && PR.round11.rows[i][2].replace('−', '-') === F[k].all.t.toFixed(2)), 'desk round 11: four forex rules, z values match round11.json, all failed');
ok(/round:'10'/.test(html) && /round:'11'/.test(html) && (html.includes('the funding harvest passed untouched tests three times; nothing else did') || html.includes('in round 12 it passed again only when paired with RSI(5) dip-buying') || html.includes('what passed: the funding harvest (rounds 7, 8 and 10; with dip-buying in round 12) and the climax reversal (round 16)'))   /* v6.5.69 extended the headline on purpose */, 'research record carries rounds 10 and 11');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
