// v6.5.86 checks: Market Profiles 'Both directions' (plan E7 figures, rendering, short-only verdicts), research record round 24.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-86.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
const store = {}; global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}), visibilityState:'visible' }; global.localStorage = { getItem:k => (k in store ? store[k] : null), setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = () => 0;
new Function(grab('MARKET PROFILES'))(); const M = window.OMEGA_MPROF, X = M._, E7 = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/E7_anatomy.json'), 'utf8'));
ok(/v6\.5\.(8[6-9]|9[0-9]|1\d\d) · build/.test(html) && html.includes("{ round:'24',") && /Research record, rounds 1\\u2013(2[4-9]|3[0-9]) \\u2014/.test(html), 'version and research record round 24');
const same = ['XAUUSD','DOGEUSDT','LINKUSDT','LTCUSDT','ADAUSDT','AVAXUSDT'].every(s => { const a = M.DATA2[s], b = E7[s]; return a && a.up_hours_pct === b.up_hours_pct && JSON.stringify(a.down_legs) === JSON.stringify(b.down_legs) && JSON.stringify(a.up_legs) === JSON.stringify(b.up_legs) && JSON.stringify(a.worst_hour) === JSON.stringify(b.worst_hour) && a.shorts.pick === b.shorts.pick && a.shorts.passed === b.shorts.passed && JSON.stringify(a.e5_direction_split) === JSON.stringify(b.e5_direction_split); });
ok(same && M.ORDER.every(s => M.DATA2[s].shorts.passed === false) && M.DATA2.DOGEUSDT.best_24h[0] === 960.6 && M.DATA2.LINKUSDT.worst_hour[1].startsWith('2021-05-19 12'), 'every both-direction figure equals plan E7’s results file; no short-only rule passed');
let bad = []; for(const s of M.ORDER){ const h = X.bothDir(s); if(/NaN|undefined|Infinity/.test(h) || !/how it falls and how it rises/.test(h) || (h.match(/<tr/g) || []).length < 20 || !/FAILED/.test(h) || !/Squeeze risk/.test(h)) bad.push(s); }
ok(!bad.length, 'all six profiles show both directions: tables, long vs short side, short-only verdicts, squeeze guidance, no NaN', bad);
ok(/spikes up/.test(X.bothDir('DOGEUSDT')) && /mostly <b>drops<\/b>/.test(X.bothDir('LTCUSDT')) && /overnight swap/.test(X.bothDir('XAUUSD')), 'per-market wording follows the data (DOGE spikes up, LTC drops, gold swap note)');
store.omega_mprof_cfg_v1 = JSON.stringify({ sel:'AVAXUSDT', acct:100, risk:1 }); const page = X.html();
ok(/buying or shorting/.test(page) && /data-sec="both"/.test(page) && !/NaN|undefined|Infinity/.test(page), 'the start panel and the selected profile include both directions');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
