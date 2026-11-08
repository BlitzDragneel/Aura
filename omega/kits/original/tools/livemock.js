// A stand-in for the OMEGA Live API (omega/live_api) for Playwright route(): /health, /fx/list, /fx/board, /fx/quote,
// /fx/klines, /bots/feed, /academy/* (empty). Data endpoints need "Authorization: Bearer <TOKEN>" like the real server.
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
const calls = [];
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
  return j({ detail:'Not Found' }, 404); }
module.exports = { handle, TOKEN, calls, LIST };
