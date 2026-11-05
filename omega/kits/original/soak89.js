// Soak test: OMEGA left open (visible) for 8 simulated hours with the Autopilot on, against a fake exchange whose clock
// moves with the page's. A climax-style flush is planted on FLSHUSDT 4 hours in. Does everything keep running while open?
const pw = require('playwright'), path = require('path'), fs = require('fs'), H = 3600e3;
const FILE = process.argv[2], HOURS = +(process.argv[3] || 8);
const T0 = Math.floor(Date.UTC(2026, 9, 22, 6, 0)/H)*H + 7*60e3;        // 06:07 UTC
let fakeNow = T0; const FLUSH_H = Math.floor(T0/H) + 4;                    // the flush hour (bar opening at T0+4h)
const SYMS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'FLSHUSDT', 'DOGEUSDT', 'LINKUSDT', 'LTCUSDT', 'ADAUSDT', 'AVAXUSDT'];
const BASE = { BTCUSDT:90000, ETHUSDT:3000, SOLUSDT:150, BNBUSDT:600, XRPUSDT:0.6, FLSHUSDT:2, DOGEUSDT:0.2, LINKUSDT:15, LTCUSDT:90, ADAUSDT:0.5, AVAXUSDT:25, XAUUSDT:4100, XAGUSDT:48 };
function bar(sym, h, ms){ const b = BASE[sym] || 1; let p = b*Math.exp(0.004*Math.sin(h*0.71 + sym.length) + 0.003*Math.sin(h*1.37)), o = b*Math.exp(0.004*Math.sin((h - 1)*0.71 + sym.length) + 0.003*Math.sin((h - 1)*1.37)), v = 100000;
  let hi = Math.max(o, p)*1.001, lo = Math.min(o, p)*0.999;
  if(sym === 'FLSHUSDT' && h === FLUSH_H){ lo = o*0.80; p = o*0.93; hi = o*1.001; v = 900000; }           // a deep flush that closes in the top of its range
  if(sym === 'FLSHUSDT' && h > FLUSH_H){ const k = h - FLUSH_H; p = p*0.93*(1 + 0.01*Math.min(k, 6)); o = h === FLUSH_H + 1 ? b*Math.exp(0.004*Math.sin(FLUSH_H*0.71 + 8) + 0.003*Math.sin(FLUSH_H*1.37))*0.93 : p/(1.01); hi = Math.max(o, p)*1.002; lo = Math.min(o, p)*0.998; }
  return [h*H, o.toFixed(6), hi.toFixed(6), lo.toFixed(6), p.toFixed(6), String(v), h*H + H - 1, String(v*p), 100, String(v*0.5), String(v*0.5*p), '0']; }
function klines(sym, interval, q){ sym = sym || q.get('pair') || 'BTCUSDT'; const step = interval === '1h' ? H : interval === '15m' ? 15*60e3 : interval === '1m' ? 60e3 : interval === '1d' ? 24*H : interval === '4h' ? 4*H : H, nowBar = Math.floor(fakeNow/step) - 1;
  const lim = Math.min(+q.get('limit') || 500, 1500), endT = q.get('endTime') ? Math.min(Math.floor(+q.get('endTime')/step), nowBar) : nowBar, st = q.get('startTime') ? Math.floor(+q.get('startTime')/step) : endT - lim + 1, out = [];
  for(let k = Math.max(st, endT - 4000); k <= endT && out.length < lim; k++){ if(step === H){ out.push(bar(sym, k)); continue; } const hh = Math.floor(k*step/H), b0 = bar(sym, hh), p = +b0[4]; out.push([k*step, String(p), String(p*1.0005), String(p*0.9995), String(p), '1000', k*step + step - 1, String(1000*p), 10, '500', String(500*p), '0']); }
  return out; }
(async () => {
  const b = await pw.chromium.launch(), ctx = await b.newContext({ viewport:{ width:412, height:915 } }); const hits = {}; let errs = [], cons = [];
  let routeErr = 0; await ctx.route('**/*', async route => { try{ const u = new URL(route.request().url()); if(u.protocol === 'file:') return route.continue(); const q = u.searchParams, key = u.hostname + u.pathname; hits[key] = (hits[key] || 0) + 1;
    const j = (x, st) => route.fulfill({ status:st || 200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
    if(/klines$/.test(u.pathname)) return j(klines(q.get('symbol'), q.get('interval'), q));
    if(/exchangeInfo$/.test(u.pathname)) return j({ symbols:SYMS.map(s => ({ symbol:s, contractType:'PERPETUAL', quoteAsset:'USDT', baseAsset:s.replace('USDT', ''), status:'TRADING', underlyingType:'COIN', onboardDate:Date.UTC(2024, 0, 1), filters:[] })) });
    if(/ticker\/24hr$/.test(u.pathname)){ const s = q.get('symbol'); const one = x => { const h = Math.floor(fakeNow/H) - 1, c = +bar(x, h)[4]; return { symbol:x, lastPrice:String(c), priceChangePercent:'0.5', quoteVolume:'500000000', highPrice:String(c*1.02), lowPrice:String(c*0.98), openPrice:String(c) }; }; return j(s ? one(s) : SYMS.map(one)); }
    if(/premiumIndex$/.test(u.pathname)){ const s = q.get('symbol'); const one = x => ({ symbol:x, markPrice:bar(x, Math.floor(fakeNow/H) - 1)[4], indexPrice:bar(x, Math.floor(fakeNow/H) - 1)[4], lastFundingRate:'0.0001', nextFundingTime:fakeNow + 3600e3, time:fakeNow }); return j(s ? one(s) : SYMS.map(one)); }
    if(/fundingRate$|openInterestHist$|LongShort|takerlongshort/i.test(u.pathname)) return j([]);
    if(/openInterest$/.test(u.pathname)) return j({ symbol:q.get('symbol'), openInterest:'1000000', time:fakeNow });
    if(/depth$/.test(u.pathname)) return j({ lastUpdateId:1, bids:[['1', '1']], asks:[['1.001', '1']] });
    if(/ticker\/price$|ticker\/bookTicker$/.test(u.pathname)) return j([]);
    if(/twelvedata/.test(u.hostname)) return j({ status:'error', code:401, message:'no key in test' });
    if(/binance|coinbase|bybit|okx/.test(u.hostname)) return j([]);
    return route.abort(); }catch(e){ routeErr++; return route.fulfill({ status:200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:'[]' }).catch(() => {}); } });
  const pg = await ctx.newPage(); pg.on('pageerror', e => errs.push(String(e).slice(0, 240))); pg.on('console', m => { if(m.type() === 'error') cons.push(m.text().slice(0, 200)); });
  await pg.clock.install({ time:T0 }); await pg.goto('file://' + path.resolve(FILE)); await pg.waitForTimeout(5000);
  await pg.evaluate(() => { window.__jl = []; window.OMEGA_OPERATOR.jobs().forEach(j => { const f = j.run; j.run = async function(){ const e = { id:j.id, lane:j.lane, t0:Date.now(), t1:null, res:null }; window.__jl.push(e);
      try{ const r = await f.apply(this, arguments); e.t1 = Date.now(); e.res = typeof r === 'string' ? r.slice(0, 80) : JSON.stringify(r || null).slice(0, 80); return r; }catch(err){ e.t1 = Date.now(); e.res = 'THREW ' + String(err).slice(0, 80); throw err; } }; });
    window.OMEGA_AUTOPILOT.setBrain(true); window.OMEGA_AUTOPILOT.setTrade(true); });
  const log = []; const snap = async () => pg.evaluate(() => { const O = window.OMEGA_OPERATOR, S = O.state(), J = S.jobs || {}, out = {};
    ['climax', 'bdesk', 'mprof', 'mwatch', 'goldh', 'desk', 'market', 'creed', 'health', 'harvest', 'edge', 'r12', 'wide'].forEach(id => { const x = J[id]; if(x) out[id] = { last:x.last || x.lastRun || null, runs:x.runs || x.n || null, result:String(x.result || x.text || '').slice(0, 90) }; });
    const X = window.OMEGA_CLIMAX ? window.OMEGA_CLIMAX.state() : {}; return { now:Date.now(), jobs:out, jobKeys:Object.keys(J).slice(0, 40), climaxLastH:X.lastH, climaxMsg:String(X.msg || '').slice(0, 120), climaxKeys:Object.keys(X).slice(0, 20), brain:window.OMEGA_AUTOPILOT.cfg().brain }; });
  for(let step = 1; step <= HOURS*6; step++){ fakeNow += 10*60e3; await pg.clock.fastForward(10*60e3); await pg.waitForTimeout(1500); if(step % 6 === 0) log.push(await snap()); }
  await pg.waitForTimeout(2500); log.push(await snap());
  const climax = await pg.evaluate(() => { const X = window.OMEGA_CLIMAX; try{ return JSON.stringify(X.state()).slice(0, 1500); }catch(e){ return String(e); } });
  fs.writeFileSync('/tmp/soak89.json', JSON.stringify({ log, climax, errs, cons:cons.slice(0, 40), hits }, null, 1));
  console.log('fake-exchange handler errors:', routeErr, '| page errors:', errs.length, errs.slice(0, 5)); console.log('console errors:', cons.length); 
  log.forEach((L, k) => console.log('hour', k + 1, new Date(L.now).toISOString().slice(11, 16), '| brain', L.brain, '| climax lastH', L.climaxLastH, '(now hour ' + Math.floor(L.now/H) + ') |', Object.entries(L.jobs).map(([k, v]) => k + ':' + (v.last ? Math.round((L.now - v.last)/60e3) + 'm' : '—')).join(' ')));
  console.log('job keys seen:', log[log.length - 1].jobKeys.join(','));
  const jl = await pg.evaluate(() => window.__jl); const runs = {}; jl.forEach(e => { runs[e.id] = (runs[e.id] || 0) + 1; });
  console.log('job runs in 8 h:', JSON.stringify(runs));
  console.log('STILL RUNNING at the end (never finished):', JSON.stringify(jl.filter(e => e.t1 == null).map(e => ({ id:e.id, lane:e.lane, startedMinAgo:Math.round((fakeNow - e.t0)/60e3) }))));
  console.log('slowest finished:', JSON.stringify(jl.filter(e => e.t1 != null).map(e => ({ id:e.id, min:Math.round((e.t1 - e.t0)/60e3) })).sort((x, y) => y.min - x.min).slice(0, 6)));
  await b.close();
})();
