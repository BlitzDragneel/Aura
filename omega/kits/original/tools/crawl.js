// Crawl every page of a build; report page errors, console errors, suspicious text (NaN, undefined, Infinity, [object Object]) and sideways overflow.
const { chromium } = require('playwright'); const fs = require('fs');
const FILE = process.argv[2], MODE = process.argv[3] || 'offline', OUT = process.argv[4];
const PAGES = ['command','journal','score','brain','posdesk','edgelab','watch','futures','creed','radar','simulation','ostrat','ostratscan','ostratbt','auto','mind','intel','flow','osig','bdesk','mprof','mread','rguard','lab','analysis','growth','bot','settings'];
const H = 3600e3;
function kl(sym, interval, start, limit){ const step = { '1m':60e3, '5m':300e3, '15m':900e3, '1h':H, '4h':4*H, '1d':24*H, '1w':7*24*H, '1M':30*24*H }[interval] || H; const n = Math.min(limit || 500, 1000); const end = Math.floor(Date.now()/step)*step; const t0 = start ? Math.max(+start, end - 3000*step) : end - n*step;
  let p = sym && sym.startsWith('BTC') ? 60000 : sym && sym.startsWith('ETH') ? 3000 : 2, out = []; let seed = 7; for(let t = t0; t <= end && out.length < n; t += step){ seed = (seed*16807) % 2147483647; const r = (seed/2147483647 - 0.5)*0.01; const o = p, c = p*(1 + r); p = c; const v = 1000 + seed % 500; out.push([t, o.toFixed(4), (Math.max(o, c)*1.002).toFixed(4), (Math.min(o, c)*0.998).toFixed(4), c.toFixed(4), String(v), t + step - 1, String(v*c), 100, String(v*0.52), String(v*0.52*c), '0']); } return out; }
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport:{ width:412, height:915 } });
  let calls = {};
  await ctx.route('**/*', async route => { const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); if(MODE === 'offline') return route.abort();
    const j = x => route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) }); const k = u.hostname + u.pathname; calls[k] = (calls[k] || 0) + 1; const q = u.searchParams;
    if(/binance/.test(u.hostname)){
      if(/klines$/.test(u.pathname) || /indexPriceKlines|premiumIndexKlines|markPriceKlines/.test(u.pathname)) return j(kl(q.get('symbol') || q.get('pair'), q.get('interval'), q.get('startTime'), +q.get('limit') || 500));
      if(/ticker\/price/.test(u.pathname)) return j(q.get('symbol') ? { symbol:q.get('symbol'), price:'60000' } : [{ symbol:'BTCUSDT', price:'60000' }, { symbol:'ETHUSDT', price:'3000' }]);
      if(/ticker\/24hr/.test(u.pathname)) return j(q.get('symbol') ? { symbol:q.get('symbol'), lastPrice:'60000', priceChangePercent:'1.2', quoteVolume:'1000000000', volume:'20000' } : [{ symbol:'BTCUSDT', lastPrice:'60000', priceChangePercent:'1.2', quoteVolume:'1000000000', volume:'20000' }, { symbol:'ETHUSDT', lastPrice:'3000', priceChangePercent:'-0.5', quoteVolume:'500000000', volume:'100000' }]);
      if(/premiumIndex$/.test(u.pathname)) return j(q.get('symbol') ? { symbol:q.get('symbol'), markPrice:'60010', indexPrice:'60000', lastFundingRate:'0.0001', nextFundingTime:Date.now() + 3600e3, time:Date.now() } : [{ symbol:'BTCUSDT', markPrice:'60010', indexPrice:'60000', lastFundingRate:'0.0001', nextFundingTime:Date.now() + 3600e3, time:Date.now() }]);
      if(/fundingRate$/.test(u.pathname)){ const out = []; for(let t = Math.floor(Date.now()/(8*H))*8*H - 400*8*H; t < Date.now(); t += 8*H) out.push({ symbol:q.get('symbol'), fundingTime:t, fundingRate:'0.0001' }); return j(out.slice(-(+q.get('limit') || 1000))); }
      if(/exchangeInfo$/.test(u.pathname)) return j({ symbols:[{ symbol:'BTCUSDT', contractType:'PERPETUAL', quoteAsset:'USDT', baseAsset:'BTC', status:'TRADING', underlyingType:'COIN', onboardDate:Date.UTC(2019, 8, 8) }, { symbol:'ETHUSDT', contractType:'PERPETUAL', quoteAsset:'USDT', baseAsset:'ETH', status:'TRADING', underlyingType:'COIN', onboardDate:Date.UTC(2019, 10, 27) }] });
      if(/openInterestHist|LongShort|takerlongshort/.test(u.pathname)) return j([]);
      if(/openInterest$/.test(u.pathname)) return j({ symbol:q.get('symbol'), openInterest:'1000', time:Date.now() });
      if(/depth$/.test(u.pathname)) return j({ lastUpdateId:1, bids:[['59990', '1']], asks:[['60010', '1']] });
      if(/aggTrades$/.test(u.pathname)) return j([]);
      return j([]); }
    return route.abort(); });
  const pg = await ctx.newPage(); const errs = [], cons = [];
  pg.on('pageerror', e => errs.push({ at:cur, e:String(e).slice(0, 300) })); pg.on('console', m => { if(m.type() === 'error' && !/net::ERR|Failed to load resource|ERR_FAILED/.test(m.text())) cons.push({ at:cur, e:m.text().slice(0, 200) }); });
  let cur = 'load'; await pg.goto('file://' + FILE); await pg.waitForTimeout(6000);
  const rep = {};
  for(const p of PAGES){ cur = p; await pg.evaluate(x => { try{ navigate(x); }catch(e){ throw e; } }, p).catch(e => errs.push({ at:p, e:'navigate: ' + e })); await pg.waitForTimeout(MODE === 'offline' ? 2500 : 5000);
    const r = await pg.evaluate(x => { const el = document.getElementById('page-' + x); if(!el) return { missing:true }; const t = el.innerText || ''; const bad = []; const re = /(\bNaN\b|\bundefined\b|\bInfinity\b|\[object Object\]|null%|NaN%)/g; let m; while((m = re.exec(t))){ bad.push(t.slice(Math.max(0, m.index - 60), m.index + 40).replace(/\n/g, ' ')); if(bad.length > 6) break; }
      return { active:el.classList.contains('active'), chars:t.length, bad, wide:document.documentElement.scrollWidth > window.innerWidth, wideEls:Array.from(el.querySelectorAll('*')).filter(e => e.getBoundingClientRect().right > window.innerWidth + 2 && getComputedStyle(e).position !== 'fixed' && !e.closest('[style*="overflow"]') && !e.closest('.table-wrap,.chart,canvas')).slice(0, 3).map(e => e.tagName + '#' + e.id + '.' + String(e.className).slice(0, 30)) }; }, p);
    rep[p] = r; }
  const out = { mode:MODE, errs, cons:cons.slice(0, 40), pages:rep, calls:Object.keys(calls).length };
  if(OUT) fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
  console.log('page errors:', errs.length); errs.slice(0, 20).forEach(e => console.log('  ', e.at, e.e));
  console.log('console errors:', cons.length); cons.slice(0, 20).forEach(e => console.log('  ', e.at, e.e));
  for(const p of PAGES){ const r = rep[p]; if(r.missing || !r.active || r.bad.length || r.wide || r.chars < 40) console.log('PAGE', p, JSON.stringify(r).slice(0, 600)); }
  console.log('pages checked', PAGES.length); await b.close(); })();
