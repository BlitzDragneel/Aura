// v6.5.58 checks: the Positioning Desk reads the market the way the research did.
const fs = require('fs'), path = require('path'), D = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D, 'omega-v6_5-58.html'), 'utf8');
const m = html.match(/<script>(\/\* ═══ POSITIONING DESK[\s\S]*?)<\/script>/); if(!m) throw new Error('desk module not found');
const store = {}; global.window = {}; global.document = { getElementById: () => null };
global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } }; global.setTimeout = () => 0; global.setInterval = () => 0;
new Function(m[1])(); const P = window.OMEGA_POSDESK;
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
const data = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/carry_data.json'), 'utf8')), exp = JSON.parse(fs.readFileSync(path.join(D, 'fixtures/posdesk_expected.json'), 'utf8'));
const L = P.analyse(data, exp.now);
let bad = []; Object.keys(exp.rows).forEach(s => { const e = exp.rows[s], r = L.rows[s]; if(!r || Math.abs(r.f7 - e.f7) > 1e-9 || Math.abs(r.m7 - e.m7) > 1e-9 || r.cell !== e.cell) bad.push(s); });
ok(L.ranked.length === 25 && bad.length === 0, '7-day funding, 7-day move and the map cell match the research code for all 25 coins' + (bad.length ? ' (differ: ' + bad.join(',') + ')' : ''));
const S = JSON.parse(fs.readFileSync(path.join(D, 'desk_static.min.json'), 'utf8'));
ok(JSON.stringify(P.STATIC) === JSON.stringify(S), 'the history tables in the build are exactly the research output (desk_static.json)');
ok(P.STATIC.cells['high/low'].yearsSame === 7 && P.STATIC.riskDial[2].worst === -58.8 && P.STATIC.carryYears['2023'] === 9, 'key history numbers: crowded-weak 7 of 7 years, worst fall at 2x -58.8%, carry 2023 +9%');
const mf = L.mktFunding, dec = L.mktDecile, expDec = 1 + S.mktFundingDeciles.filter(q => mf > q).length; ok(dec === expDec && dec >= 1 && dec <= 10, 'market funding ' + mf.toFixed(2) + '% a year sits in decile ' + dec);
// ties share an average rank, as pandas rank(pct=True)
const tie = {}; ['A','B','C','D','E','F'].forEach((k, i) => { tie[k + 'USDT'] = { k0:20000, c:new Array(40).fill(100).map((v, j) => j === 39 ? (i < 3 ? 110 : 90 + i) : 100), fund:[[20039*864e5 - 3600e3, i < 2 ? 1e-4 : 5e-5]] }; });
const T = P.analyse(tie, 20039*864e5 + 3600e3); ok(T.rows.AUSDT.F === 'high' && T.rows.BUSDT.F === 'high' && T.rows.CUSDT.F === 'mid' && T.rows.AUSDT.M === T.rows.BUSDT.M, 'tied coins share their average rank (two top funders both crowded; equal moves get the same kind)');
const stale = {}; Object.keys(data).slice(0, 3).forEach(s => { stale[s] = { k0:data[s].k0, c:data[s].c, fund:data[s].fund.filter(f => f[0] < exp.now - 3*864e5) }; });
ok(P.analyse(stale, exp.now).ranked.length === 0, 'coins whose funding is more than two days old are left off the map');
ok(html.includes('data-page="posdesk"') && html.includes('<div id="page-posdesk" class="page">') && (html.includes("'futures','posdesk','ostrat'") || html.includes("'futures','posdesk','edgelab','ostrat'") || html.includes("'futures','posdesk','edgelab','watch','ostrat'"))   /* v6.5.70 added the Edge Lab page and v6.5.77 Market Watch, on purpose */ && html.includes('positioning: safe(function(){ return window.OMEGA_POSDESK'), 'sidebar entry, page, navigator and report field are wired');
ok(P.PLAN7.rules.length === 3 && /2\.13/.test(P.PLAN7.bar), 'the fresh-coin test plan in the app is PLAN7 (3 rules, bar z >= 2.13)');
ok(!/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(JSON.stringify(P.report())), 'the desk report has no credential-like field');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
