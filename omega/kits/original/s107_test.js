// v6.5.107: backups leave out the alert webhook and the WhatsApp number; a restore never takes keys or a webhook from the file
// and keeps this browser's number; SRI on the chart library; a CSP that limits scripts, frames and plugins.
// usage: HARNESS=<kit>/tools node s107_test.js <build>   (LWC=<path to lightweight-charts 5.0.2 standalone> checks SRI with the real file)
const fs = require('fs'), path = require('path'); const FILE = process.argv[2], html = fs.readFileSync(FILE, 'utf8');
const hasPhone = require((process.env.HARNESS || path.join(__dirname, 'tools')) + '/nophone.js');
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const head = html.slice(0, html.indexOf('<style>'));
ok(/v6\.5\.(1\d\d) · build/.test(html) && !/v6\.5\.10[0-6] · build/.test(html), 'build v6.5.107 or later');
ok(/lightweight-charts@5\.0\.2\/dist\/lightweight-charts\.standalone\.production\.js" integrity="sha384-NWTHVp\/2n1SsvFhrMDcsRGYu71Cla1UgKADA6\+ErV2oklVI3DLjsnXK92nl4Cm\+J" crossorigin="anonymous"/.test(head), 'the chart library is pinned with Subresource Integrity');
const csp = (/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/.exec(head) || [])[1] || '';
ok(head.indexOf('Content-Security-Policy') < head.indexOf('<script') && /script-src 'self' 'unsafe-inline' https:\/\/unpkg\.com https:\/\/s3\.tradingview\.com;/.test(csp) && /object-src 'none'/.test(csp) && /base-uri 'none'/.test(csp) && !/unsafe-eval/.test(csp) && !/connect-src|default-src/.test(csp), 'CSP comes before any script: scripts from self/unpkg/TradingView only, no eval, no plugins, no <base>; data hosts left open', csp);
const HOOK = 'https://discord.com/api/webhooks/123456789012345678/AbCdEfGhIjKlMnOpQrStUvWxYz0123456789', NUM = '15550100123';
(async () => { const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  const lwc = process.env.LWC && fs.existsSync(process.env.LWC) ? fs.readFileSync(process.env.LWC, 'utf8') : null;
  await ctx.route('**/*', r => { const u = new URL(r.request().url()); if(u.protocol === 'file:') return r.continue();
    if(lwc && /unpkg\.com/.test(u.hostname)) return r.fulfill({ status:200, contentType:'application/javascript', headers:{ 'access-control-allow-origin':'*' }, body:lwc });
    return r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }); });
  const pg = await ctx.newPage(), errs = [], csperr = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  pg.on('console', m => { if(/Content Security Policy/i.test(m.text())) csperr.push(m.text().slice(0, 200)); });
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(4000);
  if(lwc) ok(await pg.evaluate(() => typeof LightweightCharts !== 'undefined'), 'with the real library file the integrity check passes and the charts library loads');
  await pg.evaluate(([HOOK, NUM]) => { localStorage.setItem('omega_alert_url', HOOK); localStorage.setItem('creed_alert_v1', JSON.stringify({ number:NUM, on:true }));
    localStorage.setItem('omega_note_test', 'see ' + HOOK + ' here'); localStorage.setItem('omega_claude_key', 'sk-ant-TESTKEY-0123456789abcdef'); }, [HOOK, NUM]);
  const bk = await pg.evaluate(() => window.OMEGA_BACKUP.build().then(b => JSON.stringify(b)));
  ok(!bk.includes('discord.com/api/webhooks') && !bk.includes('15550100123') && !hasPhone(bk) && !bk.includes('TESTKEY') && /"creed_alert_v1":"\{\\"on\\":true\}"/.test(bk) && /omega_alert_url/.test(JSON.stringify(JSON.parse(bk).excluded)),
    'backup: no webhook (as a store or inside one), no WhatsApp number, no key; the rest of the alert settings kept; exclusions named', { len:bk.length, ex:JSON.parse(bk).excluded });
  // a crafted backup from someone else
  const evil = JSON.stringify({ _omega:'full-backup', version:'3.8', data:{ omega_alert_url:'https://discord.com/api/webhooks/9/STRANGER', omega_claude_key:'sk-ant-STRANGER-000000000000', creed_alert_v1:JSON.stringify({ number:'15550199999', on:false }), omega_custom_feeds:'["https://evil.example/feed"]', omega_note_test:'restored' }, excluded:[], archive:[] });
  const res = await pg.evaluate(t => window.OMEGA_BACKUP.restore(t, { noConfirm:true, noReload:true }), evil);
  const after = await pg.evaluate(() => ({ url:localStorage.getItem('omega_alert_url'), key:localStorage.getItem('omega_claude_key'), alert:localStorage.getItem('creed_alert_v1'), note:localStorage.getItem('omega_note_test'), msg:(document.getElementById('backupStatus') || {}).textContent || '' }));
  ok(res.ok && after.url === HOOK && after.key === 'sk-ant-TESTKEY-0123456789abcdef' && JSON.parse(after.alert).number === NUM && JSON.parse(after.alert).on === false && after.note === 'restored' && res.feedsChanged === true && res.skipped.includes('omega_alert_url') && res.skipped.includes('omega_claude_key'),
    'restore: the file cannot set the webhook or a key, this browser keeps its WhatsApp number, other settings restore, changed feeds are flagged', { res, after });
  await pg.evaluate(() => navigate('analysis')); await pg.waitForTimeout(2000);
  ok(!errs.length && !csperr.length, 'no page errors and no CSP violations on load and on the Analysis page', { errs, csperr });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0); })();
