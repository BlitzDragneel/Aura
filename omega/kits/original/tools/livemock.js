// A stand-in for the OMEGA Live API (omega/live_api) for Playwright route(): /health, /fx/list, /fx/board, /fx/quote,
// /fx/klines, /bots/feed, /academy/* (empty); v6.5.118: /crypto/klines, /crypto/ticker, /assets, /assets/{BTC|XAU|XAG}. Data endpoints need "Authorization: Bearer <TOKEN>" like the real server.
// usage: const M = require(HARNESS + '/livemock.js'); await ctx.route('**/*', r => M.handle(r) || other(r));
const TOKEN = 'test-token-0123456789';
const LIST = { majors:['EURUSD','GBPUSD','USDJPY','USDCHF','AUDUSD','USDCAD','NZDUSD'],
  minors:['EURGBP','EURJPY','EURCHF','EURAUD','EURCAD','EURNZD','GBPJPY','GBPCHF','GBPAUD','GBPCAD','GBPNZD','AUDJPY','AUDCHF','AUDCAD','AUDNZD','CADJPY','CADCHF','CHFJPY','NZDJPY','NZDCHF','NZDCAD'],
  exotics:['USDMXN','USDZAR','USDTRY','USDSGD','USDHKD','USDNOK','USDSEK','USDDKK','USDPLN','USDHUF','USDCZK','USDCNH','USDTHB','EURTRY','EURNOK','EURSEK','EURPLN','USDTTD'],
  metals:['XAUUSD','XAGUSD','XPTUSD','XPDUSD'] };
const BASE = { EURUSD:1.0842, GBPUSD:1.2711, USDJPY:151.32, USDCHF:0.8812, AUDUSD:0.6612, USDCAD:1.3641, NZDUSD:0.6011, XAUUSD:2650.4, XAGUSD:31.21, XPTUSD:982.5, XPDUSD:1012.0, USDTTD:6.79, USDHUF:362.1, USDMXN:18.2 };
const STALE = { USDTTD:1 };
function px(s){ if(BASE[s]) return BASE[s]; let h = 0; for(const c of s) h = (h * 31 + c.charCodeAt(0)) % 997; return /JPY$/.test(s) ? 80 + h / 10 : 0.5 + h / 500; }
function quote(s){ const p = px(s), sp = /JPY$|HUF$/.test(s) ? 0.012 : /^XA[UG]/.test(s) ? (s === 'XAUUSD' ? 0.35 : 0.03) : p * 0.00008;
  return { symbol:s, bid:+(p - sp/2).toFixed(6), ask:+(p + sp/2).toFixed(6), price:p, spread:+sp.toFixed(6), ts:Date.now() - (STALE[s] ? 3600e3 : 2000), age_s:STALE[s] ? 3600 : 2, stale:!!STALE[s], note:STALE[s] ? 'market closed or feed paused' : null, source:'swissquote' }; }
const STEP = { '1m':6e4, '5m':3e5, '15m':9e5, '1h':36e5, '4h':144e5, '1d':864e5 };
function klines(s, tf, n){ const st = STEP[tf] || 36e5, end = Math.floor(Date.now() / st) * st, out = []; let p = px(s), seed = 11;
  for(let i = n - 1; i >= 0; i--){ seed = (seed * 16807) % 2147483647; const r = (seed / 2147483647 - 0.5) * 0.004; const o = p, c = p * (1 + r); p = c;
    out.push({ t:end - i * st, o, h:Math.max(o, c) * 1.0007, l:Math.min(o, c) * 0.9993, c, v:0, qv:0, closed:i > 0 }); }
  return { symbol:s, tf, source:/^X(AU|AG|PT|PD)/.test(s) ? 'yahoo (futures proxy GC=F)' : 'yahoo', candles:out }; }
const FEED = () => ({ source:'cloud bots (GitHub bot-state)', asof:Date.now(), note:'paper/testnet records and forecasts; information only, never an order',
  paper_bot:{ mode_config:'paper', kill_switch:false, approved:{ climax_a:'paper', panic_h1:'paper', panic_h3:'paper', panic5m_watch:'paper', panic15m_watch:'paper', breadth15m_watch:'paper', upscout_watch:'paper' },
    resting_orders:[{ id:'r1', strategy:'panic15m_watch', sym:'BCHUSDT', side:'long', kind:'limit', price:242.55, expires_at:new Date(Date.now() + 3 * 36e5).toISOString(), stop_price:121.27 }],
    open_positions:[{ id:'p1', strategy:'panic_h1', sym:'ARXUSDT', side:'long', entry:0.20835, stop_price:0.10417, exit_due:new Date(Date.now() + 8 * 36e5).toISOString(), status:'open' },
      { id:'p2', strategy:'climax_a', sym:'SOLUSDT', side:'long', entry:181.2, stop_price:90.6, exit_due:new Date(Date.now() + 5 * 36e5).toISOString(), status:'open' }],
    closed_trades:4, today_pnl_paper:0.42,
    recent_log:[{ t:new Date(Date.now() - 9e5).toISOString(), event:'refused', rule:'panic_h1', sym:'TRUSTUSDT', reasons:['3 positions/orders already open (max 3)'] },
      { t:new Date(Date.now() - 9e5).toISOString(), event:'refused', rule:'panic_h1', sym:'BICOUSDT', reasons:['3 positions/orders already open (max 3)'] },
      { t:new Date(Date.now() - 6e5).toISOString(), event:'order', rule:'panic15m_watch', sym:'BCHUSDT', kind:'limit', price:242.55, why:'r96 -5.07% <= own q10 -4.86%' }] },
  scouts_hourly:{ latest_time:new Date(Date.now() - 36e5).toISOString(), predictions:2400, scored:2100, base_rate_up:0.16, up_flags:{ flagged:40, hit_rate:0.25 }, down_flags:{ flagged:30, hit_rate:0.2 },
    latest:[{ sym:'BTCUSDT', close:'75829.9', p_up_move:'0.0244', p_down_move:'0.1168' }, { sym:'DOGEUSDT', close:'0.2', p_up_move:'0.3012', p_down_move:'0.05' }, { sym:'ETHUSDT', close:'2239', p_up_move:'0.11', p_down_move:'0.2215' }] },
  scouts_fast:{ latest_time:new Date(Date.now() - 9e5).toISOString(), predictions:900, scored:700, base_rate_up:0.14, up_flags:{ flagged:12, hit_rate:0.18 }, down_flags:{ flagged:9, hit_rate:null },
    latest:[{ sym:'SOLUSDT', close:'181', p_up_move:'0.19', p_down_move:'0.07' }] } });
const PERP_PX = { XAUUSDT:2655.1, XAGUSDT:31.4, BTCUSDT:75830 };
function cklines(sym, tf, n){ const k = klines(sym, tf, n); const p0 = PERP_PX[sym] || 100, r = p0 / k.candles[k.candles.length - 1].c;
  k.candles.forEach(c => { c.o *= r; c.h *= r; c.l *= r; c.c *= r; c.v = 10; c.qv = 10 * c.c; }); k.source = 'okx-swap'; return k; }
// The asset bots' desks, shaped like edges/assetbots writes them. A desk can be replaced by a test (DESKS.XAU = ...).
function desk(a){ const NAME = { BTC:'Bitcoin', XAU:'Gold', XAG:'Silver' }, PERP = { BTC:'BTCUSDT', XAU:'XAUUSDT', XAG:'XAGUSDT' };
  const wait = r => ({ state:'WAIT', since:new Date(Date.now() - 36e5).toISOString(), previous:'WAIT', direction:null, plain:'Nothing to do. No tested rule is calling a trade.', reasons:r || ['no rule for this asset and horizon has passed its test yet, so the bot calls no trades'], rules:[] });
  return { asset:a, name:NAME[a], perp:PERP[a], spot_symbol:a === 'BTC' ? null : a + 'USD', asof:new Date(Date.now() - 5 * 6e4).toISOString(), data_source:'okx-swap', errors:[], age_minutes:5, stale:false, available:true, source:'cloud bots (GitHub bot-state)',
    read:{ price:PERP_PX[PERP[a]], bar:new Date(Date.now() - 9e5).toISOString(), change_24h_pct:-0.42,
      trend:{ '15m':{ state:'flat' }, '1h':{ state:'down' }, '4h':{ state:'down' }, '1d':{ state:'up' } },
      volatility:{ atr1h_pct:0.31, atr1h_pctile:20.6, rv20d_ann_pct:45, rv20d_pctile:45.6, regime:'quiet', regime_daily:'normal', day_range_pct_median:2.5 },
      session:{ name:'New York', weekend:a !== 'BTC', note:a === 'BTC' ? 'Bitcoin trades 24/7' : 'spot gold/silver closed for the weekend; the perpetual still trades but thinly - moves are less reliable' },
      ranges:{ '24h':{ high:PERP_PX[PERP[a]] * 1.01, low:PERP_PX[PERP[a]] * 0.99, to_high_pct:1, to_low_pct:1, position:0.5 }, '30d':{ high:PERP_PX[PERP[a]] * 1.1, low:PERP_PX[PERP[a]] * 0.995, to_high_pct:10, to_low_pct:0.5, to_low_atr:0.8, position:0.05 } },
      spot:a === 'BTC' ? undefined : { price:a === 'XAU' ? 2650.4 : 31.21, stale:true, note:'market closed or feed paused', source:'swissquote' },
      funding:{ rate:0.00005, source:'okx-swap' },
      scouts:{ day:{ horizon:'4 h', p_big_move:0.3, flag:false, skill_ok:true, label:'own scout; validation AUC 0.67/0.71 (up/down); UNTESTED as a trading signal', direction:'none: big-move risk only' },
               swing:{ horizon:'24 h', p_big_move:0.19, flag:false, skill_ok:a !== 'XAG', label:a === 'XAG' ? 'NO SKILL on validation (AUC < 0.55): not used for WATCH' : 'validation AUC 0.61/0.64', direction:'none: big-move risk only' } } },
    horizons:{ day:wait(), swing:Object.assign(wait(['price is within 1 hourly ATR of its 30-day low: a break or a rejection is near', 'no rule for this asset and horizon has passed its test yet, so the bot calls no trades']), { state:'WATCH', plain:'Big-move risk, direction unknown. Watch only: no tested rule is calling a trade.' }), hold:wait() },
    open_calls:[], recent_calls:[], forward:{ day:{ scored:120, big_move_rate:0.21, watch_readings:14, big_move_rate_when_watch:0.36, text:'120 readings scored; big moves followed 21% of them, 36% after a WATCH (14 WATCH readings) - too few to judge yet' }, swing:{ scored:0, text:'no readings scored yet (each is scored once its horizon has passed)' }, hold:{ scored:0, text:'no readings scored yet (each is scored once its horizon has passed)' }, calls:{ closed:0, text:'no calls yet: no tested rule for this asset has fired' } },
    notebook:[{ title:'What the research found', lines:['The research on ' + NAME[a] + ' is still running.'] }, { title:'Day trades', lines:['No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.'] }, { title:'Habits I measure myself', lines:['A typical day ranges 2.5% from low to high (last 60 days).'] }],
    runs:42, honesty:'Calls come only from rules that passed a pre-registered test.', disclaimer:'information only: calls come only from rules that passed a pre-registered test; WAIT when nothing qualifies; never an order' }; }
const DESKS = {};
const calls = [], AUD = [];
function handle(route){ let u; try{ u = new URL(route.request().url()); }catch(e){ return null; } if(u.hostname !== 'omega-live-api.onrender.com' && u.hostname !== 'live.test') return null;
  const auth = route.request().headers()['authorization'] || '', q = u.searchParams; calls.push({ path:u.pathname, q:u.search, auth:!!auth });
  const j = (x, st) => route.fulfill({ status:st || 200, contentType:'application/json', headers:{ 'access-control-allow-origin':'*' }, body:JSON.stringify(x) });
  if(u.pathname === '/health') return j({ ok:true, version:'1.0.0', twelvedata_key:false, auth:true });
  if(u.pathname === '/fx/list') return j(Object.assign({}, LIST, { candles:'...', quotes:'Swissquote live bid/ask' }));
  if(u.pathname.startsWith('/academy')) return j({ detail:'no course' }, 404);
  if(auth !== 'Bearer ' + TOKEN) return j({ detail:'missing or wrong token' }, 401);
  if(u.pathname === '/fx/board'){ const g = q.get('group') || 'majors'; const syms = g === 'all' ? [].concat(LIST.majors, LIST.minors, LIST.exotics, LIST.metals) : LIST[g] || []; return j({ group:g, quotes:syms.map(quote), missing:[] }); }
  if(u.pathname === '/fx/quote') return j(quote((q.get('symbol') || 'EURUSD').replace('/', '').toUpperCase()));
  if(u.pathname === '/fx/klines') return j(klines((q.get('symbol') || 'EURUSD').replace('/', '').toUpperCase(), q.get('tf') || '1h', Math.min(+q.get('limit') || 200, 1500)));
  if(u.pathname === '/bots/feed') return j(FEED());
  if(u.pathname.startsWith('/auditor/')){ let body = {}; try{ body = route.request().postDataJSON() || {}; }catch(e){} AUD.push({ path:u.pathname, body });
    if(route.request().method() !== 'POST') return j({ detail:'Method Not Allowed' }, 405);
    if(u.pathname === '/auditor/parse'){ const m = /(XAUUSD|GOLD|EURUSD|US30)\s+(BUY|SELL)/i.exec(body.text || ''); if(!m) return j({ detail:'could not read a symbol and a side (buy/sell) in that message' }, 422);
      const n = k => { const x = new RegExp(k + '\\D{0,3}([0-9.]+)', 'i').exec(body.text); return x ? +x[1] : null; }; const stop = n('SL'), lim = /limit|@/i.test(body.text) ? n('(?:limit|@)') : null;
      return j({ signal:{ symbol:/GOLD/i.test(m[1]) ? 'XAUUSD' : m[1].toUpperCase(), side:m[2].toLowerCase(), logged_ms:Date.now(), entry:lim, entry_hi:null, stop, targets:[n('TP1') || n('TP')].filter(Boolean), provider:body.provider || '', note:String(body.text).slice(0, 500), claimed_pips:null, id:'' },
        problems:stop ? [] : ['NO STOP: cannot be measured in R (risk units)'] }); }
    if(u.pathname === '/auditor/score'){ const sc = (body.signals || []).map(d => { const base = { symbol:d.symbol, side:d.side, provider:d.provider, logged_ms:d.logged_ms, problems:d.stop ? [] : ['NO STOP: cannot be measured in R (risk units)'] };
        if(d.entry) return Object.assign(base, { status:'waiting for entry' });
        const win = d.side === 'buy'; return Object.assign(base, { status:'closed', fill_ms:d.logged_ms + 6e4, fill:4105.2, risk_pips:100, mfe_pips:60, mae_pips:20, source:'binance XAUUSDT 1m',
          tp1:{ outcome:win ? 'target 1' : 'stop', pips:win ? 47 : -103, R:win ? 0.47 : -1.03, exit_ms:d.logged_ms + 36e5, usd_per_lot:win ? 470 : -1030 }, ladder:{ outcome:win ? 'targets' : 'stop', pips:win ? 80 : -103, R:win ? 0.8 : -1.03, exit_ms:d.logged_ms + 72e5, usd_per_lot:0 } }); });
      const sum = L => { const c = L.filter(x => x.status === 'closed'), rs = c.map(x => x.tp1.R); return { logged:L.length, closed:c.length, not_filled:0, running:L.length - c.length, no_stop:0,
        tp1:{ n:c.length, avg_R:c.length ? +(rs.reduce((a, b) => a + b, 0) / c.length).toFixed(3) : undefined, win_rate:c.length ? rs.filter(x => x > 0).length / c.length : undefined, t:0.4, pips_scored:c.reduce((a, x) => a + x.tp1.pips, 0) }, ladder:{ n:c.length, pips_scored:c.reduce((a, x) => a + x.ladder.pips, 0) },
        verdict:'Too early: ' + c.length + ' closed signals with a stop. About 30 are needed before the numbers mean anything, 50+ to trust them.' }; };
      const by = {}; sc.forEach(x => (by[x.provider || 'unnamed'] = by[x.provider || 'unnamed'] || []).push(x)); return j({ scored:sc, summary:sum(sc), by_provider:Object.fromEntries(Object.entries(by).map(([k, v]) => [k, sum(v)])), rules:'edges/auditor/RULES.md' }); }
    if(u.pathname === '/auditor/risk'){ if(!(body.balance > 0) || !(body.positions || []).length) return j({ detail:'balance must be > 0 and at least one position is needed' }, 422); const p = body.positions[0], usd = p.lots * 100;
      return j({ balance:body.balance, by_symbol:[{ symbol:p.symbol, net_direction:p.side, usd_per_1_move:usd, usd_per_pip:usd / 10, move_to_lose_balance:+(body.balance / usd).toFixed(3), pips_to_lose_balance:+(body.balance / usd * 10).toFixed(1),
        typical_moves:{ '15-minute':4.2, day:40 }, plain:'a typical 15-minute move is 4.2 (' + Math.round(4.2 / (body.balance / usd) * 100) + '% of the balance); a typical day move is 40 (' + Math.round(40 / (body.balance / usd) * 100) + '% of the balance)' }] }); } }
  if(u.pathname === '/crypto/klines') return j(cklines((q.get('symbol') || 'BTCUSDT').toUpperCase(), q.get('tf') || '1h', Math.min(+q.get('limit') || 200, 1000)));
  if(u.pathname === '/crypto/ticker') return j((q.get('symbols') || 'BTCUSDT').split(',').map(x => ({ symbol:x, price:PERP_PX[x] || 100, bid:(PERP_PX[x] || 100) * 0.9999, ask:(PERP_PX[x] || 100) * 1.0001, ts:Date.now(), source:'okx-swap' })));
  if(u.pathname === '/assets') return j({ available:true, source:'cloud bots (GitHub bot-state)', assets:{ BTC:'Bitcoin', XAU:'Gold', XAG:'Silver' } });
  const am = u.pathname.match(/^\/assets\/(BTC|XAU|XAG)$/i); if(am){ const a = am[1].toUpperCase(); return j(DESKS[a] || desk(a)); }
  return j({ detail:'Not Found' }, 404); }
module.exports = { handle, TOKEN, calls, LIST, DESKS, desk, PERP_PX, AUD };
