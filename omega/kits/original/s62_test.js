// v6.5.62 checks: the 10-coin funding harvest (round 8, R3) computed as the Python test code; desk round-8 table; wiring.
const fs = require('fs'), path = require('path'), D = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-62.html'), 'utf8');
function mod(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); const store = {}; global.window = {}; global.document = { getElementById: () => null };
  global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0; new Function(m[1])(); }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8')), py = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/harvest10_py_weeks.json'), 'utf8')), py5 = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/harvest_py_weeks.json'), 'utf8'));
mod('FUNDING HARVEST'); const H = window.OMEGA_HARVEST, NOW = Date.UTC(2026, 9, 18, 1, 30);
const r10 = H.compute(data, { now:NOW, rec:{}, k:10, keep:20 }), js = {}; r10.weeks.forEach(q => { js[new Date(q.end*864e5).toISOString().slice(0, 10)] = q; });
let n = 0, mx = 0, held = 0; py.forEach(([t, r, ne, w]) => { if(ne < 5 || !js[t]) return; n++; mx = Math.max(mx, Math.abs(js[t].r - r)); if(js[t].held !== w.length) held++; });
ok(n === 153 && mx < 1e-12 && held === 0, '10-coin harvest identical to the Python test code on ' + n + ' weeks (largest difference ' + mx.toExponential(1) + ')');
const r5 = H.compute(data, { now:NOW, rec:{} }), j5 = {}; r5.weeks.forEach(q => { j5[new Date(q.end*864e5).toISOString().slice(0, 10)] = q; });
let n5 = 0, d5 = []; py5.forEach(([t, r, ne]) => { if(ne < 5 || !j5[t]) return; n5++; if(Math.abs(j5[t].r - r) > 1e-12) d5.push(t); });
ok(n5 === 153 && d5.length <= 1, 'the 5-coin harvest is unchanged by the refactor (' + n5 + ' weeks; tie weeks differing: ' + d5.length + ')');
ok(r10.k === 10 && r10.current && Object.keys(r10.current.hold).length <= 10 && r10.before.worstFall > -0.01, '10-coin version: current week holds ' + Object.keys(r10.current.hold).length + ' pairs; worst fall before the freeze ' + (100*r10.before.worstFall).toFixed(2) + '%');
ok(H.RESEARCH.wide && Math.abs(H.RESEARCH.wide.fresh2.t - 3.38) < 1e-9 && H.RESEARCH.wide.fresh2.bar === 2.45, 'its final-test record (90 new coins: z 3.38 against 2.45) is in the module');
const rep = H.report(); ok(rep.wide && rep.wide.research && !/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(JSON.stringify(rep)), 'report carries the 10-coin version and no credential-like field');
mod('POSITIONING DESK'); const PR = window.OMEGA_POSDESK.report();
ok(PR.round8 && PR.round8.rows.length === 10 && PR.round8.rows.filter(r => /PASS/.test(r[3])).length === 1, 'desk: round-8 table with 10 strategies, exactly one final-test pass');
ok((html.includes("the funding harvest passed untouched tests twice; nothing else did") || (html.includes("the funding harvest passed untouched tests three times; nothing else did") || html.includes("the funding harvest passed untouched tests three times; in round 12 it passed again only when paired with RSI(5) dip-buying") || html.includes('what passed: the funding harvest (rounds 7, 8 and 10; with dip-buying in round 12) and the climax reversal (round 16)')   /* v6.5.82 rewrote the headline on purpose */)) && /round:'8'/.test(html), 'research record carries round 8');   // v6.5.67 changed "twice" to "three times" on purpose (round 10)
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
