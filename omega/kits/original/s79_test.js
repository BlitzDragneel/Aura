// v6.5.79 checks: the market clock (hour map from round 17, verified CPI/FOMC times with daylight saving, options
// expiry, CME weekend, funding), event tags on flight recordings, the climax card's anatomy note, record and knowledge.
const fs = require('fs'), path = require('path'), D0 = __dirname;
const html = fs.readFileSync(process.argv[2] || path.join(D0, 'omega-v6_5-79.html'), 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
global.window = {}; global.document = { getElementById:() => null }; global.setInterval = () => 0;
new Function(grab('MARKET CLOCK'))(); const C = window.OMEGA_MARKETCLOCK, D = C.DATA;
const R = JSON.parse(fs.readFileSync('/home/claude/research/round17.json', 'utf8'));
// 1. the hour map is round 17's, pooled over the 165 coins
const h14 = R.when.design.hour['14'], v14 = R.when.valid.hour['14'], pooled = (h14.big3*h14.n + v14.big3*v14.n)/(h14.n + v14.n);
ok(Math.abs(D.hours['14'][0] - pooled) < 0.01 && D.hours['14'][0] > 2*D.hours['4'][0], 'hour map = round 17 pooled over 165 coins (14:00 UTC: ' + D.hours['14'][0] + '% of hours with a 3σ move, against ' + D.hours['4'][0] + '% at 04:00)');
// 2. event times: 08:30 / 14:00 New York time with daylight saving
ok(D.cpi[0] === '2026-11-10T13:30Z' && D.cpi.includes('2027-07-14T12:30Z') && D.fomc[0] === '2026-10-28T18:00Z' && D.fomc.includes('2026-12-09T19:00Z') && D.cpi.length === 14 && D.fomc.length === 10,
  'CPI 08:30 ET and FOMC 14:00 ET converted with daylight saving (Nov 10 13:30 UTC, Jul 14 12:30 UTC; Oct 28 18:00, Dec 9 19:00)', [D.cpi.slice(0, 2), D.fomc.slice(0, 2)]);
ok(C._.lastFriday(2026, 9) === Date.UTC(2026, 9, 30, 8) && C._.lastFriday(2026, 11) === Date.UTC(2026, 11, 25, 8) && C._.usDST(Date.UTC(2026, 6, 1)) && !C._.usDST(Date.UTC(2026, 11, 1)), 'last-Friday expiry at 08:00 UTC; US daylight saving');
// 3. what is coming up, from a fixed moment (Mon 19 Oct 2026 12:00 UTC)
const now = Date.UTC(2026, 9, 19, 12), up = C.upcoming(now), kinds = up.map(e => e.kind);
ok(up[0].kind === 'funding' && up[0].t === Date.UTC(2026, 9, 19, 16) && up.some(e => e.kind === 'cme' && e.t === Date.UTC(2026, 9, 23, 21)) && up.some(e => e.kind === 'cme' && e.t === Date.UTC(2026, 9, 25, 22)) && up.some(e => e.kind === 'fomc' && e.t === Date.UTC(2026, 9, 28, 18)) && up.some(e => e.kind === 'expiry' && e.t === Date.UTC(2026, 9, 30, 8)) && up.every((e, i) => !i || e.t >= up[i-1].t),
  'coming up from 19 Oct 12:00 UTC: funding 16:00, CME close Fri 21:00 UTC (CDT), reopen Sun 22:00 UTC, FOMC 28 Oct 18:00, expiry 30 Oct 08:00', up.slice(0, 6).map(e => [e.kind, new Date(e.t).toISOString()]));
// 4. tags for flight recordings
const up2 = C.upcoming(Date.UTC(2026, 9, 27, 12)); ok(up2.some(e => e.kind === 'cme' && e.t === Date.UTC(2026, 9, 30, 21)) && up2.some(e => e.kind === 'cme' && e.t === Date.UTC(2026, 10, 1, 23)), 'the weekend the clocks change: CME closes Fri 30 Oct 21:00 UTC and reopens Sun 1 Nov 23:00 UTC');
ok(C.tags(Date.UTC(2026, 9, 28, 18, 20)).join() === 'FOMC statement hour' && C.tags(Date.UTC(2026, 10, 10, 13, 45)).join() === 'CPI release hour' && C.tags(Date.UTC(2026, 9, 30, 8, 5)).join() === 'monthly options expiry' && C.tags(Date.UTC(2026, 9, 23, 8, 5)).length === 0, 'flight-recording tags: FOMC hour, CPI hour, monthly expiry (not a weekly Friday)');
const W = grab('MARKET WATCH'); ok(/MC\.tags\(t\)/.test(W), 'Market Watch adds these tags to each flight recording');
// 5. climax card, record, knowledge
ok(/What it really catches \(round 17\)/.test(grab('CLIMAX REVERSAL')) && html.includes("{ round:'17',") && html.includes('"r":"17"') && /earlier studies \(rounds 1–(1[7-9]|[2-9]\d), CREED,/.test(html), 'climax card explains what it catches; research record and knowledge include round 17');
ok(!/c047445f|apikey=/i.test(grab('MARKET CLOCK')), 'no key in the clock');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
