// v6.5.60 checks: the BTC trend benchmark runs exactly the other assistant's rule (plus funding), judged forward.
const fs = require('fs'), path = require('path'), D = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-60.html'), 'utf8');
function mod(freeze){ const m = html.match(/<script>(\/\* ═══ BTC TREND BENCHMARK[\s\S]*?)<\/script>/); if(!m) throw new Error('module not found'); let src = m[1]; if(freeze) src = src.replace('Date.UTC(2026, 9, 18)/DAY', freeze + '/DAY');
  const store = {}; global.window = {}; global.document = { getElementById: () => null }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0;
  new Function(src)(); return window.OMEGA_BTCTREND; }
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8')), py = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/btctrend_py.json'), 'utf8'));
const B = mod(), x = data.BTCUSDT, res = B.compute(x, Date.UTC(2026, 9, 18, 9, 0), true);
let mp = 0, mh = 0; res.hist.forEach(q => { const i = q[0] - x.k0; mp = Math.max(mp, Math.abs(q[1] - py.pnl[i])); mh = Math.max(mh, Math.abs(q[2] - py.pos[i])); });
ok(res.hist.length === py.pnl.length && mp < 1e-12 && mh < 1e-12, 'day by day identical to the Python test code (' + res.hist.length + ' days; largest differences ' + mp.toExponential(1) + ' and ' + mh.toExponential(1) + ')');
const N = res.now; ok(N.day === Date.UTC(2026, 9, 17)/864e5 && N.held < 0 && Math.abs(N.held + 0.8037) < 1e-3 && Math.abs(N.want + 0.7121) < 1e-3 && Math.abs(N.momentum + 0.0385) < 1e-3 && Math.abs(N.vol - 0.2528) < 1e-3,
  'after the close of 17 Oct: short 0.80x held (the rule wants 0.71x; the change is under 0.15), 14-day change -3.85%, volatility 25.3%');
ok(Math.abs(res.before.cum - 0.8131) < 1e-3 && Math.abs(res.before.worstFall + 0.2170) < 1e-3 && res.forward.days === 0, 'before the freeze on stored history: +81.3% in all, worst fall -21.7%; no forward day yet');
const BF = mod('Date.UTC(2026, 6, 5)'), rf = BF.compute(x, Date.UTC(2026, 9, 18, 9, 0));
ok(rf.forward.days === Date.UTC(2026, 9, 17)/864e5 - Date.UTC(2026, 6, 5)/864e5, 'with a 5 Jul freeze: every day after it is forward (' + rf.forward.days + ' days)');
// threshold: a steady trend with slowly changing volatility trades rarely
const syn = { k0:20000, c:[], fund:[[20000*864e5, 1e-4]] }; let p = 100; for(let i=0;i<200;i++){ p *= 1 + 0.004 + 0.02*Math.sin(i*1.7); syn.c.push(p); }
const rs = B.compute(syn, (20000 + 200)*864e5, true); let changes = 0; for(let i=1;i<rs.hist.length;i++) if(rs.hist[i][2] !== rs.hist[i-1][2]) changes++;
ok(rs.hist[rs.hist.length - 1][2] > 0 && changes < 20, 'a rising market is held long, re-sized only when the size moves more than 0.15 (' + changes + ' changes in 200 days)');
const V = B.verdict; ok(V({ days:0 }).code === 'WAIT' && V({ days:50, weeks:8, worstFall:-0.1, weekMean:0.01, t:3 }).code === 'COLLECT' && V({ days:200, weeks:30, worstFall:-0.1, weekMean:-0.001, t:-1 }).code === 'RETIRE' && V({ days:200, weeks:30, worstFall:-0.1, weekMean:0.01, t:2.2 }).code === 'CONFIRMED' && V({ days:20, weeks:3, worstFall:-0.36, weekMean:-0.05 }).code === 'RETIRE',
  'judgement: wait, collect to 26 weeks, retire at <= 0 or a 35% fall, confirm at z >= 1.96');
ok(B.RESEARCH.fresh.passed === false && Math.abs(B.RESEARCH.fresh.t - 1.60) < 1e-9 && /not proven/i.test(html.match(/BTC TREND BENCHMARK[\s\S]*?<\/script>/)[0]), 'labelled not proven, with its failed untouched test (z 1.60 against 2.33)');
ok(!/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(JSON.stringify(B.report())), 'report has no credential-like field');
ok(html.includes('<div id="btctrendCard"></div>') && html.includes("'harvest','btctrend'") && html.includes('btcTrend: safe(function(){ return window.OMEGA_BTCTREND') && html.includes('omega_btctrend_v1:1') && html.includes('BTC trend benchmark</b> (14-day direction'), 'card, job, report field, store and desk link are wired');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
