// v6.5.81 checks: round 18 (the outside report) on the harvest card, in the research record and in the knowledge.
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(process.argv[2] || path.join(__dirname, 'omega-v6_5-81.html'), 'utf8');
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
ok(/Checked \(round 18\):<\/b> all of that came from new listings that have <b>no Binance spot market<\/b>/.test(html) && /On the 81 new listings that do have spot, the harvest made \\u22122% to \\u22123% a year/.test(html) && !/question for the next round, not a rule/.test(html), 'harvest card: the new-listing question is answered');
ok(/\{ round:'18', tried:'Another assistant\\u2019s report: an order-flow rule/.test(html) && /FAILED on the 165 coins it never used \(\+5\.3%, t 0\.72/.test(html), 'research record: round 18 with the failed independent test');
ok(/"r":"18"/.test(html) && /"total_rules":2240/.test(html) && /earlier studies \(rounds 1–18, CREED,/.test(html), 'knowledge: round 18 (2,240 rules and studies)');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
