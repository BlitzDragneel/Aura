// v6.5.73 checks: round 14's model across coins, frozen. It reproduces the research code's predictions exactly on the
// app's own daily data; it never looks ahead; it trades long/short fifths at the Sunday close; it sits in the shadow book.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D0, 'omega-v6_5-73.html'), 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const store = {}; global.window = {}; global.document = { getElementById: () => null }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; const realST = setTimeout; global.setTimeout = (f, ms) => ms === 0 ? realST(f, 0) : 0;
new Function(grab('EDGE LIBRARY'))(); new Function(grab('MODEL ACROSS COINS'))(); const L = window.OMEGA_EDGELIB, M = window.OMEGA_XSMODEL, DAY = 864e5;
const recs = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/wide25.json'), 'utf8')), ref = JSON.parse(fs.readFileSync(path.join(D0, 'fixtures/xsmodel_ref.json'), 'utf8'));
ok(M.MODEL.feats.length === 28 && M.MODEL.trees.length === 124 && M.MODEL.feats.join() === ref.names.join(), 'the frozen model: 28 features in the research order, 124 trees (the research fit, early stopping as tested)');
const G = L.grid(recs, null), t0 = Date.now(), S = M.scores(G, null), ms = Date.now() - t0;
let n = 0, bad = 0; for(const d of Object.keys(ref.pred)){ const t = +d - G.K0; for(const s of Object.keys(ref.pred[d])){ n++; if(!(Math.abs(S[G.syms.indexOf(s)][t] - ref.pred[d][s]) < 1e-9)) bad++; } }
ok(n === 1500 && bad === 0, 'its predictions match the research code exactly on the app’s own data: ' + n + ' coin-Sundays, 25 coins, the last 60 Sundays (' + ms + ' ms for every Sunday since 2019)', { n, bad });
// no look-ahead
const cut = G.K0 + G.T - 200, r2 = JSON.parse(JSON.stringify(recs)); r2.forEach(r => { for(let i=0; i<r.c.length; i++){ if(r.k0 + i > cut && r.c[i] != null){ r.c[i] *= 1 + 0.3*Math.sin(i); r.v[i] = (r.v[i] || 0)*3; r.tb[i] = (r.tb[i] || 0)*0.5; r.ff[i] = 0.001; } } });
const G2 = L.grid(r2, null), S2 = M.scores(G2, null); let same = true, cnt = 0; for(let j=0; j<G.syms.length; j++) for(let t=0; t <= cut - G.K0; t++){ const a = S[j][t], b = S2[j][t]; if(a === a || b === b){ cnt++; if(!(a === b)) same = false; } }
ok(same && cnt > 5000, 'no look-ahead: changing prices, volume and funding after a day leaves every earlier prediction identical (' + cnt + ' checked)');
// trading: long the top fifth, short the bottom fifth at each Sunday close, only from the day it was frozen
const from = Date.UTC(2026, 9, 11)/DAY, R = L.run(G, { kind:'model', from, key:'model across coins (round 14)' }, { wantW:true });
let okW = true, sundays = 0; for(let t=0; t<G.T; t++){ const day = t + G.K0, sw = R.W.reduce((a, w) => a + w[t], 0), pos = R.W.reduce((a, w) => a + Math.max(0, w[t]), 0), neg = R.W.reduce((a, w) => a + Math.min(0, w[t]), 0);
  if(day < from && R.W.some(w => w[t] !== 0)) okW = false; if(day >= from && new Date(day*DAY).getUTCDay() === 0){ sundays++; if(!(Math.abs(pos - 0.5) < 1e-12 && Math.abs(neg + 0.5) < 1e-12 && Math.abs(sw) < 1e-12)) okW = false; } }
const tS = from + 7 - G.K0, el = G.syms.map((s, j) => j).filter(j => G.E[j][tS] && S[j][tS] === S[j][tS]).sort((a, b) => S[a][tS] - S[b][tS] || a - b), k = Math.round(el.length*0.2);
ok(okW && sundays >= 1 && el.slice(-k).every(j => R.W[j][tS] > 0) && el.slice(0, k).every(j => R.W[j][tS] < 0), 'it holds nothing before it was frozen, then long the top fifth and short the bottom fifth by prediction (half the account each side)');
const R70 = L.run(G, { kind:'model', from:from - 70, key:'x' }), last = G.K0 + G.T - 1, costDays = Array.from(R70.cost).filter(c => c > 0).length;
ok(R70.gross.length === G.T && costDays >= 9 && costDays <= 11 && Array.from(R70.gross).slice(-60).some(g => g !== 0), 'its daily returns carry trading costs on each weekly rebalance (' + costDays + ' in 10 weeks) and funding, like every other book entry (data end ' + new Date(last*DAY).toISOString().slice(0, 10) + ')');
// in the shadow book
window.OMEGA_WIDE = { getMeta: async () => null, putMeta: async () => {} };
new Function(grab('EDGE LAB'))(); (async () => { const st = await window.OMEGA_EDGELAB._.load(); const E = st.book['research: model across coins (round 14)'];
  ok(E && E.research && E.start === Date.UTC(2026, 9, 18)/DAY && E.cand.kind === 'model' && Object.keys(st.book).filter(k => /^research: /.test(k)).length === 4, 'the shadow book holds it as a research entry from 18 Oct 2026, beside the harvest and the two round-12 blends');
  ok(/below the strict bar of 3\.29; judged only on new weeks/.test(html), 'its origin says why it is not an edge yet');
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
