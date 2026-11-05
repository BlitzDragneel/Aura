// v6.5.97 check: the data check counts a market that could not be read as a problem.
const fs = require('fs'), path = require('path');
const FILE = process.argv[2] || path.join(__dirname, 'omega-v6_5-97.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 300) : '')); } }
global.window = {}; global.document = { getElementById: () => null }; global.localStorage = { getItem:() => null, setItem(){} }; global.setInterval = () => 0; global.setTimeout = () => 0;
new Function(grab('DATA CHECK AND BASELINES'))(); const X = window.OMEGA_TRUTH._, now = Date.now(), nowH = Math.floor(now/3600e3);
const R = X.readsCheck({ BTCUSDT:{ err:'HTTP 500' }, ETHUSDT:{ lastH:nowH - 1, at:now - 60e3, pos:{ premium:0.0002 } } }, now);
ok(/v6\.5\.(9[7-9]|1\d\d) · build/.test(html) && R.length === 2 && !R.find(r => r.sym === 'BTCUSDT').ok && /could not be read \(HTTP 500\)/.test(R.find(r => r.sym === 'BTCUSDT').issues[0]) && R.find(r => r.sym === 'ETHUSDT').ok, 'a market that could not be read is now a problem; a healthy one still passes', R);
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
