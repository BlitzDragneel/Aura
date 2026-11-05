// v6.5.88 checks: the Research files card saves the wide store's daily history of the 25 studied coins in the research
// format (decoded the same way by the research loader), refuses credentials, and works in a browser.
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process'), D0 = __dirname, DAY = 86400e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-88.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 400) : '')); } }
function fake(sym, base, k0, n){ const r = { sym, k0, c:[], h:[], l:[], v:[], tb:[], ff:[], fc:[] }; let p = base; for(let i=0; i<n; i++){ if(i === 50){ ['c','h','l','v','tb'].forEach(k => r[k].push(null)); r.ff.push(0); r.fc.push(0); continue; } p *= 1 + 0.03*Math.sin(i*0.7); r.c.push(+p.toFixed(6)); r.h.push(+(p*1.02).toFixed(6)); r.l.push(+(p*0.97).toFixed(6)); r.v.push(1000 + i); r.tb.push(500 + i/2); r.ff.push(0.0003); r.fc.push(3); } return r; }
const K0 = Date.UTC(2020, 0, 1)/DAY, RECS = [fake('BTCUSDT', 7200, K0, 2480), fake('ETHUSDT', 130, K0, 2480), fake('SOLUSDT', 1.5, K0 + 220, 2260), fake('XRPUSDT', 0.19, K0, 2480)];
global.window = { OMEGA_WIDE:{ all: async () => RECS } }; global.document = { getElementById: () => null, createElement: () => ({}) }; const realST = global.setTimeout, realSI = global.setInterval; global.setInterval = () => 0; global.setTimeout = () => 0;
new Function(grab('RESEARCH FILES'))(); const X = window.OMEGA_RDL;
(async () => {
  ok(/v6\.5\.(8[8-9]|9[0-9]|1\d\d) · build/.test(html) && html.includes('<div id="rdlBody"></div>') && (html.match(/window\.OMEGA_RDL = /g) || []).length === 1 && X.COINS.length === 25 && X.COINS.slice(0, 5).join() === 'BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT', 'version, the card on the Breakout Desk, 25 coins with the five for plan E10 first');
  const out = await X.build();
  ok(out.format === 'omega-history' && out.tf === 1440 && out.markets.length === 4 && out.checks.BTCUSDT.days === 2479 && out.checks.SOLUSDT.from === '2020-08-08' && out.skipped.some(x => /BNBUSDT: not in the store/.test(x)), 'the file: daily, the stored coins with their date ranges, missing ones listed (BNB here), the empty day skipped', { checks:out.checks, skipped:out.skipped.slice(0, 3) });
  const m = out.markets[0];
  const py = cp.spawnSync('python3', ['-c', ['import json,sys,numpy as np', 'm=json.load(sys.stdin)', 's=10.0**-m["dp"]', 't=np.cumsum(np.asarray(m["t"],dtype=np.int64)); c=np.cumsum(np.asarray(m["c"],dtype=np.int64))*s',
    'o=c+np.asarray(m["o"],dtype=np.int64)*s; h=np.maximum(o,c)+np.asarray(m["h"],dtype=np.int64)*s; l=np.minimum(o,c)-np.asarray(m["l"],dtype=np.int64)*s',
    'print(json.dumps([int(t[0]//24),int(t[-1]//24),len(t),float(c[0]),float(c[-1]),float(h[10]),float(l[10]),bool(np.all(l<=c)),bool(np.all(h>=c))]))'].join('\n')], { input:JSON.stringify(m) });
  let v = null; try{ v = JSON.parse(String(py.stdout)); }catch(e){}
  const src = RECS[0], idx = src.c.map((x, i) => x != null ? i : -1).filter(i => i >= 0), tol = Math.pow(10, -m.dp);
  ok(v && v[0] === K0 && v[1] === K0 + 2479 && v[2] === 2479 && Math.abs(v[3] - src.c[0]) <= tol && Math.abs(v[4] - src.c[idx[idx.length - 1]]) <= tol && Math.abs(v[5] - src.h[10]) <= tol && Math.abs(v[6] - src.l[10]) <= tol && v[7] && v[8], 'the research loader decodes the same days and prices (closes, highs, lows)', v || String(py.stderr).slice(0, 200));
  window.__omegaLeak = () => true; let refused = false; try{ await X.save(); }catch(e){ refused = /refused/.test(e.message); } delete window.__omegaLeak; ok(refused, 'saving is refused if the file would carry a credential');
  global.setTimeout = realST; global.setInterval = realSI;
  const pw = require('playwright'), b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 }, acceptDownloads:true });
  await ctx.route('**/*', r => new URL(r.request().url()).protocol === 'file:' ? r.continue() : r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }));
  const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
  await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500);
  await pg.evaluate(recs => { window.OMEGA_WIDE.all = async () => recs; navigate('bdesk'); return window.OMEGA_RDL.status(); }, RECS); await pg.waitForTimeout(800);
  const txt = await pg.evaluate(() => (document.getElementById('rdlBody') || {}).innerText || '');
  ok(/Research files to send/i.test(txt) && /4 of 25 studied coins stored/.test(txt) && /Missing for plan E10: BNB/.test(txt), 'the card shows what is stored and which plan E10 coins are missing', txt.slice(0, 300));
  const [dl] = await Promise.all([pg.waitForEvent('download', { timeout:15000 }), pg.click('[data-rdl="save"]')]); const fp = '/tmp/rdl_test' + path.extname(dl.suggestedFilename()); await dl.saveAs(fp);
  let buf = fs.readFileSync(fp); if(/\.gz$/.test(dl.suggestedFilename())) buf = zlib.gunzipSync(buf); const F = JSON.parse(buf.toString());
  ok(/^omega-history-daily25-\d{4}-\d\d-\d\d\.json(\.gz)?$/.test(dl.suggestedFilename()) && F.markets.length === 4 && F.tf === 1440 && errs.length === 0, 'in the browser: Save writes ' + dl.suggestedFilename() + ' with the stored coins; no page errors', { name:dl.suggestedFilename(), n:F.markets.length, errs });
  await b.close(); console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
