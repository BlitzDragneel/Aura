// UX audit harness: screenshots + performance for OMEGA Prime and the original OMEGA.
// Usage: node ux_shoot.js <app.html> <prime|orig> <outPrefix> [mode=mock|offline] [state=quiet|live] [scale=1]
//   mock: Binance answered with synthetic candles (the sandbox cannot reach fapi.binance.com); CDNs reach the real network.
//   offline: every external request is aborted (as on a phone without signal).
//   live: plants the same panic/climax state the ticket test uses (s_prime_tickets_test.js) so Today shows real tickets.
// Writes <outPrefix>_<device>_<page>.png and <outPrefix>_perf.json.
const { chromium, devices } = require('playwright'); const fs = require('fs'); const path = require('path');
const [FILE, KIND, OUT, MODE = 'mock', STATE = 'quiet', SCALE = '1', ONLY = ''] = process.argv.slice(2);
const H = 3600e3;
const PRIME_PAGES = ['today', 'chart', 'signals', 'risk', 'evidence'];
const ORIG_PAGES = ['command', 'edgelab', 'posdesk', 'creed', 'rguard', 'mread', 'auto', 'settings'];
function kl(sym, iv, n){ const step = { '1m':60e3, '5m':300e3, '15m':900e3, '1h':H, '4h':4*H, '1d':24*H, '1w':7*24*H }[iv] || H; n = Math.min(n || 500, 1000);
  const end = Math.floor(Date.now()/step)*step; let p = /^BTC/.test(sym) ? 68000 : /^ETH/.test(sym) ? 2500 : /^SOL/.test(sym) ? 160 : /^BNB/.test(sym) ? 600 : /^XRP/.test(sym) ? 0.6 : 2, seed = 7 + (sym || '').length; const out = [];
  for(let i = 0; i < n; i++){ seed = (seed*16807) % 2147483647; const r = (seed/2147483647 - 0.5)*0.012 + 0.0004*Math.sin(i/9); const o = p, c = p*(1 + r); p = c; const v = 1000 + seed % 700;
    out.push([end - (n - i)*step, o.toPrecision(6), (Math.max(o, c)*1.003).toPrecision(6), (Math.min(o, c)*0.997).toPrecision(6), c.toPrecision(6), String(v), 0, String(v*o), 0, String(v*0.5), String(v*o*0.5)]); } return out; }
async function route(r){ const u = new URL(r.request().url()); if(u.protocol === 'file:' || u.protocol === 'data:') return r.continue();
  if(MODE === 'offline') return r.abort();
  const j = x => r.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) }); const q = u.searchParams;
  if(/binance/.test(u.hostname)){
    if(/klines$/i.test(u.pathname)) return j(kl(q.get('symbol') || q.get('pair'), q.get('interval'), +q.get('limit') || 500));
    if(/ticker\/24hr/.test(u.pathname)){ const L = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE', 'ADA', 'AVAX', 'LINK', 'TRX'].concat(Array.from({ length:35 }, (_, i) => 'C' + i)).map((s, i) => ({ symbol:s + 'USDT', lastPrice:String(kl(s, '1h', 2)[1][4]), priceChangePercent:String((i % 7 - 3)*0.8), quoteVolume:String(1e10/(i + 1)), volume:'1000' })); return j(q.get('symbol') ? L.find(x => x.symbol === q.get('symbol')) || L[0] : L); }
    if(/ticker\/price/.test(u.pathname)) return j(q.get('symbol') ? { symbol:q.get('symbol'), price:'68000' } : [{ symbol:'BTCUSDT', price:'68000' }]);
    if(/premiumIndex$/.test(u.pathname)) return j(q.get('symbol') ? { symbol:q.get('symbol'), markPrice:'68010', indexPrice:'68000', lastFundingRate:'0.0001', nextFundingTime:Date.now() + H, time:Date.now() } : [{ symbol:'BTCUSDT', markPrice:'68010', indexPrice:'68000', lastFundingRate:'0.0001', nextFundingTime:Date.now() + H, time:Date.now() }]);
    if(/fundingRate$/.test(u.pathname)){ const o = []; for(let t = Math.floor(Date.now()/(8*H))*8*H - 200*8*H; t < Date.now(); t += 8*H) o.push({ symbol:q.get('symbol'), fundingTime:t, fundingRate:'0.0001' }); return j(o); }
    if(/exchangeInfo$/.test(u.pathname)) return j({ symbols:[{ symbol:'BTCUSDT', contractType:'PERPETUAL', quoteAsset:'USDT', baseAsset:'BTC', status:'TRADING', onboardDate:Date.UTC(2019, 8, 8) }] });
    if(/openInterest$/.test(u.pathname)) return j({ symbol:q.get('symbol'), openInterest:'1000', time:Date.now() });
    if(/depth$/.test(u.pathname)){ const m = +kl(q.get('symbol'), '1h', 2)[1][4]; return j({ lastUpdateId:1, bids:Array.from({ length:50 }, (_, i) => [String(m*(1 - 0.0005*(i + 1))), String(i % 9 === 4 ? 40 : 3)]), asks:Array.from({ length:50 }, (_, i) => [String(m*(1 + 0.0005*(i + 1))), String(i % 11 === 6 ? 35 : 3)]) }); }
    return j([]); }
  if(/unpkg|jsdelivr|cdnjs/.test(u.hostname)) return r.continue();
  return r.abort(); }
function seed(){ const H = 3600e3, nh = Math.floor(Date.now()/H);
  localStorage.setItem('prime:prime_panic_v1', JSON.stringify({ lastH:nh - 1, scans:1, msg:'', th:{}, breadth:{ h:nh - 1, v:0.12 }, trades:[
    { sym:'AAAUSDT', rule:'H1', t:nh - 2, close:1.4, limit:1.2345, r24:-0.153, status:'pending' },
    { sym:'BBBUSDT', rule:'H3', t:nh - 30, entry:2.5, r24:-0.2, br:0.25, status:'open', due:nh - 3 },
    { sym:'DDDUSDT', rule:'H1', t:nh - 100, entry:10, fill:nh - 99, exit:10.3, net:0.0288, status:'closed' } ] }));
  localStorage.setItem('prime:prime_climax_v1', JSON.stringify({ lastH:nh - 1, scans:1, msg:'', trades:[
    { sym:'CCCUSDT', t:nh - 1, e:nh, z:-3.4, vr:4.1, loc:0.7, status:'open' },
    { sym:'EEEUSDT', t:nh - 200, e:nh - 199, z:-3.1, vr:3.5, loc:0.6, entry:5, exit:5.2, net:0.038, status:'closed' } ] })); }
function perfInit(){ window.__lt = []; try{ new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push([Math.round(e.startTime), Math.round(e.duration)]))).observe({ type:'longtask', buffered:true }); }catch(e){} }
(async () => {
  const b = await chromium.launch(); const pages = KIND === 'prime' ? PRIME_PAGES : ORIG_PAGES; const perf = { file:FILE, bytes:fs.statSync(FILE).size, mode:MODE, state:STATE, devices:{} };
  const devs = [['phone', Object.assign({}, devices['Pixel 7'], { deviceScaleFactor:+SCALE })], ['desktop', { viewport:{ width:1366, height:768 }, deviceScaleFactor:+SCALE }]];
  for(const [dn, opt] of devs){ if(ONLY && ONLY !== dn) continue;
    const ctx = await b.newContext(opt); await ctx.route('**/*', route); await ctx.addInitScript(perfInit); if(STATE === 'live') await ctx.addInitScript(seed);
    const pg = await ctx.newPage(); const errs = [], cons = [], failed = []; let cur = 'load';
    pg.on('pageerror', e => errs.push(cur + ': ' + String(e).slice(0, 200))); pg.on('console', m => { if(m.type() === 'error') cons.push(cur + ': ' + m.text().slice(0, 160)); }); pg.on('requestfailed', r => { const u = r.url(); if(!/^file:/.test(u)) failed.push(u.slice(0, 90)); });
    const cdp = await ctx.newCDPSession(pg); await cdp.send('Performance.enable'); if(dn === 'phone') await cdp.send('Emulation.setCPUThrottlingRate', { rate:4 });
    const t0 = Date.now(); await pg.goto('file://' + path.resolve(FILE), { waitUntil:'load' }); const tLoad = Date.now() - t0;
    await pg.waitForTimeout(KIND === 'prime' ? 6000 : 9000);
    const nav = await pg.evaluate(() => { const n = performance.getEntriesByType('navigation')[0] || {}, f = performance.getEntriesByName('first-contentful-paint')[0]; return { dcl:Math.round(n.domContentLoadedEventEnd || 0), load:Math.round(n.loadEventEnd || 0), fcp:f ? Math.round(f.startTime) : null, lt:window.__lt.slice() }; });
    const m = Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x => [x.name, x.value]));
    const D = { wallLoadMs:tLoad, dclMs:nav.dcl, loadMs:nav.load, fcpMs:nav.fcp, longTasksFirst6s:nav.lt.length, longTaskMsFirst6s:nav.lt.reduce((a, x) => a + x[1], 0), longestTaskMs:Math.max(0, ...nav.lt.map(x => x[1])), heapMB:+(m.JSHeapUsedSize/1048576).toFixed(1), scriptMs:Math.round(m.ScriptDuration*1000), layoutMs:Math.round(m.LayoutDuration*1000), cpuThrottle:dn === 'phone' ? 4 : 1, pages:{} };
    if(dn === 'phone') await cdp.send('Emulation.setCPUThrottlingRate', { rate:1 });
    for(const p of pages){ cur = p; const lt0 = await pg.evaluate(() => window.__lt.length);
      const tn = Date.now(); await pg.evaluate(x => navigate(x), p).catch(e => errs.push(p + ': navigate ' + e)); const navMs = Date.now() - tn; await pg.waitForTimeout(p === 'chart' || KIND === 'orig' ? 4500 : 2000);
      const info = await pg.evaluate(() => { const sec = document.querySelector('.page.on, .page.active') || document.body; const vw = innerWidth;
        // tap targets and small text in the visible page
        const btns = [...sec.querySelectorAll('button, a, input, select, label.btn-outline, [onclick]')].filter(e => e.offsetParent !== null); const small = btns.filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.height < 44 && r.width < 44 || r.height < 32); }).length;
        const nav = [...document.querySelectorAll('#bar button, #tabs button, .hamburger')].filter(e => e.offsetParent !== null).map(e => Math.round(e.getBoundingClientRect().height));
        const txt = [...sec.querySelectorAll('*')].filter(e => e.childNodes.length && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2) && e.offsetParent !== null); const fs = txt.map(e => parseFloat(getComputedStyle(e).fontSize)); const lt12 = fs.filter(x => x < 12).length;
        return { dom:document.getElementsByTagName('*').length, pageNodes:sec.getElementsByTagName('*').length, height:Math.round(document.documentElement.scrollHeight), screens:+(document.documentElement.scrollHeight/innerHeight).toFixed(1), wide:document.documentElement.scrollWidth > vw + 1, taps:btns.length, smallTaps:small, navH:nav, textEls:fs.length, textUnder12px:lt12, minFont:fs.length ? Math.min(...fs) : null, canvases:sec.querySelectorAll('canvas').length, svgs:sec.querySelectorAll('svg').length }; });
      info.navMs = navMs; info.longTasks = (await pg.evaluate(() => window.__lt.length)) - lt0; D.pages[p] = info;
      await pg.screenshot({ path:OUT + '_' + dn + '_' + p + '.png', fullPage:KIND === 'prime' || dn === 'phone' ? true : false }); }
    const m2 = Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x => [x.name, x.value])); D.heapAfterPagesMB = +(m2.JSHeapUsedSize/1048576).toFixed(1); D.nodesAfter = m2.Nodes;
    D.pageErrors = errs; D.consoleErrors = cons.slice(0, 30); D.failedRequests = [...new Set(failed)].slice(0, 20); perf.devices[dn] = D; await ctx.close(); }
  fs.writeFileSync(OUT + '_perf.json', JSON.stringify(perf, null, 1)); await b.close(); console.log(JSON.stringify(perf).slice(0, 3000)); })();
