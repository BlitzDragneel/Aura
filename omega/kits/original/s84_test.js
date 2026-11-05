// v6.5.84 checks: setups A and B marked FAILED (plan E1) with no alerts, the 180.5 correction, the gold/silver hourly
// download (paging, limits, resume, checks, encoding the research loader reads, no key in the file), and the page in a browser.
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process'), D0 = __dirname, H = 3600e3;
const FILE = process.argv[2] || path.join(D0, 'omega-v6_5-84.html'), html = fs.readFileSync(FILE, 'utf8');
function grab(name){ const m = html.match(new RegExp('<script>(\\/\\* ═══ ' + name + '[\\s\\S]*?)<\\/script>')); if(!m) throw new Error(name); return m[1]; }
let pass = 0, fail = 0; function ok(c, msg, x){ if(c){ pass++; console.log('ok   ' + msg); } else { fail++; console.log('FAIL ' + msg + (x !== undefined ? ' — ' + JSON.stringify(x).slice(0, 500) : '')); } }
const realST = global.setTimeout, realSI = global.setInterval, store = {};
global.window = {}; global.document = { getElementById: () => null, createElement: () => ({}) }; global.localStorage = { getItem:k => store[k] || null, setItem:(k, v) => { store[k] = String(v); } };
global.setInterval = () => 0; global.setTimeout = f => { if(typeof f === 'function') f(); return 0; };
global.indexedDB = require((process.env.HARNESS || path.join(D0, 'tools')) + '/fake_idb.js')();
new Function(grab('EDGE LIBRARY'))(); new Function(grab('BREAKOUT DESK'))(); new Function(grab('GOLD HOURLY HISTORY'))();
const B = window.OMEGA_BDESK, X = B._, G = window.OMEGA_GOLDH, Q = G._;
(async () => {
  // 1. the desk: failed, corrected, no alerts
  ok(/v6\.5\.(8[4-9]|9[0-9]|1\d\d) · build/.test(html) && html.includes("{ round:'20',") && /Research record, rounds 1\\u2013[23][0-9] \\u2014/.test(html) && /Plan E1 on 2021\\u20132023: A 100 to 49\.1, B 27\.2, the new method 71\.4: all FAILED/.test(html), 'version, research record round 20 and its E1 result');
  ok(B.SETUPS.A.failed && B.SETUPS.A.failed.end === 49.1 && B.SETUPS.B.failed && B.SETUPS.B.failed.end === 27.2 && X.verdict(X.newAcct('A')).status === 'FAILED' && X.verdict(X.newAcct('B')).status === 'FAILED', 'setups A and B carry the E1 result and judge as FAILED');
  const src = grab('BREAKOUT DESK'); ok(/P\.t >= nowH - 2 && !SETUPS\[k2\]\.failed\)/.test(src) && /A\[k\]\.pend && !SETUPS\[k\]\.failed/.test(src), 'no alert and no menu badge for a failed setup');
  const st = B.state(); st.recs = []; st.accts = { A:X.newAcct('A'), B:X.newAcct('B') }; const page = X.html();
  ok(/FAILED a clean test/.test(page) && /100 → <b>49\.1<\/b>/.test(page) && /100 → <b>27\.2<\/b>/.test(page) && /Do not trade it/.test(page) && /238 of 623 trades above 1% risk; at a true 1% it was about 108/.test(page) && !/NaN|undefined|Infinity/.test(page), 'the page says both failed, with numbers, and corrects the 180.5', page.slice(0, 300));
  // 2. gold: parsing, checks, encoding
  ok(Q.hourOf('2026-10-20 03:00:00') === Date.UTC(2026, 9, 20, 3)/H && Q.hourOf('2026-10-20T03:00:00Z') === Date.UTC(2026, 9, 20, 3)/H && isNaN(Q.hourOf('bad')), 'Twelve Data datetimes read as UTC hours');
  const rows = {}; let p = 1950.123; for(let h = 480000, k = 0; k < 3000; k++, h += (k % 120 === 0 ? 49 : 1)){ const o = p, c = p*(1 + 0.002*Math.sin(k)); rows[h] = [o, Math.max(o, c) + 0.5, Math.min(o, c) - 0.5, c]; p = c; }
  rows[400000] = [0, 1, 1, 1]; rows[400001] = [10, 9, 11, 10.5];                   // a bad candle (dropped) and a high below its close (corrected)
  const g = Q.guard(rows); ok(g.dropped === 1 && g.fixed === 1 && g.t.length === 3001 && g.t.every((t, i) => !i || t > g.t[i-1]) && g.h.every((x, i) => x >= Math.max(g.o[i], g.c[i]) && g.l[i] <= Math.min(g.o[i], g.c[i])), 'checks: one per hour in order, impossible candles dropped, highs and lows made consistent');
  const m = Q.encode('XAU/USD', g), d = Q.decode(m), tol = Math.pow(10, -m.dp);
  ok(m.sym === 'XAUUSD' && m.dp === 3 && d.t.length === g.t.length && d.t.every((t, i) => t === g.t[i]) && ['o', 'h', 'l', 'c'].every(f => d[f].every((x, i) => Math.abs(x - g[f][i]) <= tol)), 'encoding round-trips every hour and price to 0.001');
  const py = cp.spawnSync('python3', ['-c', [
    'import json,sys,numpy as np', 'm=json.load(sys.stdin)', 's=10.0**-m["dp"]', 't=np.cumsum(np.asarray(m["t"],dtype=np.int64)); c=np.cumsum(np.asarray(m["c"],dtype=np.int64))*s',
    'o=c+np.asarray(m["o"],dtype=np.int64)*s; h=np.maximum(o,c)+np.asarray(m["h"],dtype=np.int64)*s; l=np.minimum(o,c)-np.asarray(m["l"],dtype=np.int64)*s',
    'print(json.dumps([int(t[0]),int(t[-1]),len(t),float(c[-1]),float(h[100]),float(l[100]),bool(np.all(l<=np.minimum(o,c)+1e-9))]))'].join('\n')], { input:JSON.stringify(m) });
  let pyv = null; try{ pyv = JSON.parse(String(py.stdout)); }catch(e){}
  ok(pyv && pyv[0] === g.t[0] && pyv[1] === g.t[g.t.length - 1] && pyv[2] === g.t.length && Math.abs(pyv[3] - g.c[g.c.length - 1]) <= tol && Math.abs(pyv[4] - g.h[100]) <= tol && Math.abs(pyv[5] - g.l[100]) <= tol && pyv[6], 'the research loader’s decoding (edge/load.py) reads the same hours and prices', pyv || String(py.stderr).slice(0, 200));
  // 3. paging, limits, resume
  store.omega_td_key = 'TESTKEY1234567890abcd'; Q.setWait({ gap:0, retry:0, limit:0 }); const T0 = Date.UTC(2026, 9, 20, 0)/H, calls = []; let mode = 'normal', limitOnce = true;
  const fmt = h => new Date(h*H).toISOString().slice(0, 19).replace('T', ' ');
  global.fetch = async url => { const u = new URL(url), sym = u.searchParams.get('symbol'), end = u.searchParams.get('end_date'); calls.push({ sym, end, key:u.searchParams.get('apikey') });
    const J = x => ({ json:async () => x });
    if(limitOnce && calls.length === 2){ limitOnce = false; return J({ status:'error', code:429, message:'You have run out of API credits for the current minute.' }); }
    if(mode === 'daily' && calls.length === 4) return J({ status:'error', code:429, message:'You have run out of API credits for the day.' });
    const top = end ? Date.parse(end.replace(' ', 'T') + 'Z')/H : T0, oldest = sym === 'XAU/USD' ? T0 - 12000 : T0 - 3000, vals = [];
    for(let h = top; h > oldest && vals.length < 5000; h--){ const v = 2000 + Math.sin(h); vals.push({ datetime:fmt(h), open:String(v), high:String(v + 1), low:String(v - 1), close:String(v + 0.2) }); }
    if(!vals.length) return J({ status:'error', code:400, message:'No data is available on the specified dates.' });
    return J({ status:'ok', values:vals }); };
  mode = 'daily'; let r1 = await G.run();
  const s1 = G.state(), x1 = s1.recs['XAU/USD'] || {}, n1 = x1.rows ? Object.keys(x1.rows).length : 0;
  ok(/allowance is used up/.test(r1) && n1 === 10000 && !x1.done, 'a minute limit is waited out and retried; a daily limit stops cleanly with progress kept (' + n1 + ' hours)', { r1, n1 });
  mode = 'normal'; const before = calls.length; const r2 = await G.run(), x2 = G.state().recs['XAU/USD'], y2 = G.state().recs['XAG/USD'];
  const resumedAt = calls[before].end, expect = fmt(T0 - 9999 - 1);
  ok(/Done/.test(r2) && resumedAt === expect && Object.keys(x2.rows).length === 12000 && x2.done && Object.keys(y2.rows).length === 3000 && y2.done, 'pressing again resumes from the oldest stored hour and completes both metals (12,000 and 3,000 hours)', { r2, resumedAt, expect });
  ok(calls.every(c => c.key === 'TESTKEY1234567890abcd') && calls.every((c, i) => !c.end || !i || true), 'requests carry the key set in OMEGA');
  // 4. the file: research format, checks, never the key
  const out = await Q.build(), txt = JSON.stringify(out);
  ok(out.format === 'omega-history' && out.tf === 60 && out.markets.length >= 2 && out.checks.XAUUSD.hours === 12000 && out.checks.XAUUSD.complete && out.markets.every(mm => mm.v.every(v => v === 0)) && !txt.includes('TESTKEY1234567890abcd') && !/apikey/i.test(txt), 'the file: both metals in the research format, with its checks, and no key');
  window.__omegaLeak = () => true; let refused = false; try{ await G.save(); }catch(e){ refused = /refused/.test(String(e.message)); } delete window.__omegaLeak;
  ok(refused, 'saving is refused if the file would carry a credential');
  // 5. in a browser: the desk with the gold card; a mocked Twelve Data; the saved file
  global.setTimeout = realST; global.setInterval = realSI; let pw = null; try{ pw = require('playwright'); }catch(e){}
  if(!pw){ ok(false, 'playwright not found (set NODE_PATH)'); }
  else { const b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 }, acceptDownloads:true }); let tdCalls = 0, sawKey = true;
    await ctx.addInitScript(() => { try{ localStorage.setItem('omega_td_key', 'BROWSERKEY99887766'); }catch(e){} });
    await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue();
      const j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
      if(/twelvedata/.test(u.hostname) && /time_series/.test(u.pathname) && u.searchParams.get('interval') === '1h'){ if(u.searchParams.get('outputsize') === '5000') tdCalls++; if(u.searchParams.get('apikey') !== 'BROWSERKEY99887766') sawKey = false;
        const sym = u.searchParams.get('symbol'), end = u.searchParams.get('end_date'), top = end ? Date.parse(end.replace(' ', 'T') + 'Z')/H : Date.UTC(2026, 9, 20)/H, oldest = Date.UTC(2026, 9, 20)/H - (sym === 'XAU/USD' ? 6200 : 3000), vals = [];
        for(let h = top; h > oldest && vals.length < 5000; h--){ const v = (sym === 'XAU/USD' ? 2500 : 30) + Math.sin(h); vals.push({ datetime:new Date(h*H).toISOString().slice(0, 19).replace('T', ' '), open:String(v), high:String(v + 0.5), low:String(v - 0.5), close:String(v + 0.1) }); }
        return j(vals.length ? { status:'ok', values:vals } : { status:'error', code:400, message:'No data' }); }
      if(/binance/.test(u.hostname)) return j([]);
      return route.abort(); });
    const pg = await ctx.newPage(), errs = []; pg.on('pageerror', e => errs.push(String(e).slice(0, 200)));
    await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(3500);
    await pg.evaluate(() => { navigate('bdesk'); if(window.OMEGA_TD) window.OMEGA_TD.acquire = () => Promise.resolve(); window.OMEGA_GOLDH._.setWait({ gap:0, retry:0, limit:0 }); }); await pg.waitForTimeout(2500);
    const btn = await pg.$('[data-goldh="run"]'); ok(!!btn && !(await btn.isDisabled()), 'the gold card is on the Breakout Desk with Download enabled when a key is set');
    await btn.click(); await pg.waitForFunction(() => !window.OMEGA_GOLDH.state().busy && /Done|Stopped/.test(window.OMEGA_GOLDH.state().msg), null, { timeout:60000 });
    const msg = await pg.evaluate(() => window.OMEGA_GOLDH.state().msg);
    const [dl] = await Promise.all([pg.waitForEvent('download', { timeout:20000 }), pg.click('[data-goldh="save"]')]); const fp = '/tmp/gold_dl_test' + path.extname(dl.suggestedFilename()); await dl.saveAs(fp);
    let buf = fs.readFileSync(fp); if(/\.gz$/.test(dl.suggestedFilename())) buf = zlib.gunzipSync(buf); const F = JSON.parse(buf.toString());
    ok(/Done/.test(msg) && tdCalls >= 3 && sawKey && /^omega-history-(gold1h|metals-fx1h)-\d{4}-\d\d-\d\d\.json(\.gz)?$/.test(dl.suggestedFilename()) && F.markets.length >= 2 && F.checks.XAUUSD.hours === 6200 && F.checks.XAGUSD.hours === 3000 && !buf.toString().includes('BROWSERKEY99887766'), 'in the browser: 3 requests, both metals complete, a ' + dl.suggestedFilename() + ' with 6,200 and 3,000 hours and no key', { msg, tdCalls, name:dl.suggestedFilename(), checks:F.checks });
    const r = await pg.evaluate(() => { const e = document.getElementById('page-bdesk'); return { text:e.innerText, pills:Array.from(e.querySelectorAll('.bd-pill')).map(x => x.textContent), wide:document.documentElement.scrollWidth > window.innerWidth }; });
    ok(r.pills.filter(t => t === 'FAILED').length === 2 && /FAILED a clean test/.test(r.text) && /plan E[24]/i.test(r.text) && !/\bNaN\b|\bundefined\b/.test(r.text) && !r.wide && errs.length === 0, 'the page shows both setups FAILED, the gold card, no NaN, no overflow, no page errors', { pills:r.pills, errs, wide:r.wide });
    await pg.screenshot({ path:'/tmp/bdesk84.png', fullPage:true }); await b.close(); }
  console.log('\n' + pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
})();
