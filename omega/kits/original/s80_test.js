// v6.5.80 checks: round 15's Bybit result is on the harvest card, in the research record and in the knowledge.
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(process.argv[2] || path.join(__dirname, 'omega-v6_5-80.html'), 'utf8');
let pass = 0, fail = 0; function ok(c, msg){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg); } }
ok(/Bybit \(tested 19 Oct 2026\):<\/b> shorting each coin on whichever of Binance or Bybit paid more passed on 140 coins \(\+5\.3% a year more, t 7\.4\), then <b>failed<\/b> on 324 untouched coins \(\+0\.7%, t 1\.25 against a bar of 2\.13\)/.test(html), 'harvest card: venue test passed validation and failed its final, with the numbers');
ok(/coins listed since April 2025/.test(html) && /described, not tested/.test(html) && /no Binance spot market/.test(html), 'harvest card: where funding was paid in 2025-26, labelled as description, with the spot answer');
ok(/FAILED on 324 untouched coins \(\+0\.7%, t 1\.25 against 2\.13\)\. The harvest stays on Binance\.' \}/.test(html) && !/waiting for the Bybit download|The Bybit test runs once the download is in/.test(html), 'research record: round 15 complete');
ok(/"r":"15","name":"Funding harvest on Bybit/.test(html) && /"total_rules":22(39|40)/.test(html), 'knowledge: the venue test and its result');
console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
