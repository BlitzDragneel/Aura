// v6.5.90 checks: no forced Market Watch recording; the top 5 coins on Market Profiles; forex in the research download; record 29.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-90.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const store = {}; global.document = { getElementById: () => null, createElement: () => ({}), visibilityState:'visible' }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
(async () => {
  let started = 0, live = false; let saved = null; global.window = { OMEGA_WATCH:{ cfg:() => (saved || { on:false, mode:'full' }), setCfg:c => { saved = Object.assign({}, c); }, running:() => live, start:async () => { started++; live = true; } }, OMEGA_OPERATOR:{ jobs:() => [] } };
  new Function(grab('AUTOPILOT COVERAGE'))(); const job = window.OMEGA_AUTOCOV.JOBS.find(j => j.id === 'mwatch'); const r1 = await job.run();
  window.OMEGA_WATCH.cfg = () => ({ on:true, mode:'light' }); const r2 = await job.run();
  ok((/^Off/.test(r1) && started === 1 && /Started recording/.test(r2)) || (/Started recording \(light mode/.test(r1) && saved && saved.on && saved.mode === 'light' && started === 1), 'Market Watch: started only when switched on (v6.5.90), or by the Autopilot in light mode (v6.5.91)', { r1, r2, started, saved });
  global.window = {}; new Function(grab('MARKET PROFILES'))(); const M = window.OMEGA_MPROF, X = M._;
  const top = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'], E14 = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/E14_dossiers.json'), 'utf8'));
  const bad = top.filter(s => { const h = X.profile(s) + X.bothDir(s); return /NaN|undefined|Infinity/.test(h) || !/Who trades it, and when/.test(h) || !/Plan E14/.test(h) || !/FAILED/.test(h) || (h.match(/data-hour="/g) || []).length !== 24; });
  ok(M.ORDER.slice(0, 5).join() === top.join() && !bad.length && top.every(s => M.DATA[s].volume_share_pct.US === E14[s].volume_share_pct.US && M.DATA[s].strategy.passed === false), 'the top 5 coins head Market Profiles with plan E14’s figures, a who-trades-it table, both directions and FAILED verdicts, no NaN', bad);
  ok(/var SYMS = \['XAU\/USD', 'XAG\/USD', 'EUR\/USD', 'GBP\/USD', 'USD\/JPY', 'AUD\/USD', 'USD\/CAD'\]/.test(grab('GOLD HOURLY HISTORY')) && /plans E4, E15/.test(grab('GOLD HOURLY HISTORY')) && /forex hourly download \(plans E4, E15\)/.test(grab('AUTOPILOT COVERAGE')), 'the research download fetches the five forex majors for plan E15, also through the Autopilot');
  const KN = JSON.parse(html.slice(html.indexOf('var KN = ') + 9, html.indexOf(';\n', html.indexOf('var KN = '))));
  ok(/v6\.5\.(9[0-9]|1\d\d) · build/.test(html) && html.includes("{ round:'29',") && /Research record, rounds 1\\u2013(2[9]|3[0-9])/.test(html) && KN.earlier.some(e => e.r === 'E14') && KN.earlier.some(e => e.r === 'E15'), 'version, research record round 29, the Brain knows E14 and E15');
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
