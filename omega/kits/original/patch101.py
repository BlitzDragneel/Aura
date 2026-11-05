"""v6.5.101: Market Watch recorder (+ E15 and E13 rows in the research card) — when the live streams deliver nothing (seen in a 7-day export: 0 minute rows), it now
(1) rotates the spot stream through three addresses, (2) closes connections that stay silent so the rotation happens,
(3) fills empty minutes from Binance's and Coinbase's 1-minute candles (prices, taker buy/sell volume, trade counts; never
overwriting stream data; only since recording started), (4) exports a 'diag' section (feeds, errors, backup counts, a daily
live/dead log) so a file explains itself, and (5) says on its card when the backup is filling in. Nothing else changed."""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
i = s.index('<script>/* ═══ MARKET WATCH (v6.5.77)'); j = s.index('</script>', i); m = s[i:j]
def rep(a, b):
    global m; assert m.count(a) == 1, (a[:70], m.count(a)); m = m.replace(a, b)
rep("""   addresses ended 23 Apr 2026). Minutes with no data stay empty (never filled in). Runs only while the app is open. */""",
"""   addresses ended 23 Apr 2026). Minutes with no data stay empty (never filled in). Runs only while the app is open.
   v6.5.101: a 7-day export (19–26 Oct 2026) held 0 minute rows although the app was open on 4 days: the live streams
   delivered nothing on that device. Now the spot stream rotates through three addresses, a connection that stays silent is
   closed so the next address is tried, and while a feed is not live its empty minutes are filled from the exchange's
   1-minute candles (close, taker buy/sell volume, trade count; spot high/low; Coinbase closes) — real exchange data,
   never overwriting stream data, only since recording started. Liquidations, large orders and flight recordings need the
   live stream. Every export carries 'diag': each feed's state, messages, last error and address, the backup's counts and a
   daily log of live and dead minutes, with the hours the backup filled (per coin and feed, last 8 days). */""")
rep("""  var URL_SPOT = 'wss://stream.binance.com:9443/stream?streams=',""",
    """  var SPOT_ALTS = ['wss://stream.binance.com:9443/stream?streams=', 'wss://stream.binance.com:443/stream?streams=', 'wss://data-stream.binance.vision/stream?streams='], SPOT_HOSTS = ['https://api.binance.com', 'https://data-api.binance.vision'];
  var URL_SPOT = 'wss://stream.binance.com:9443/stream?streams=',""")
rep("""if(S.state !== 'live'){ S.state = 'live'; S.tries = 0; S.err = null; }""", """if(S.state !== 'live'){ S.state = 'live'; S.tries = 0; S.err = null; S.everLive = true; }""")
rep("""  function retry(S){ if(!running) return; clearTimeout(S.timer);""",
    """  function retry(S){ if(!running) return; clearTimeout(S.timer);
    if(S.alts && !S.everLive && S.tries >= 2){ S.alt = ((S.alt || 0) + 1) % S.alts.length; S.url = S.alts[S.alt] + S.suffix; S.tries = 0; S.rotations = (S.rotations || 0) + 1; }   // never live here: try the next address
   """)
rep("""      if(S.state === 'open' && S.opened && t - S.opened > 60e3) S.state = 'silent';""",
    """      if(S.state === 'open' && S.opened && t - S.opened > 60e3) S.state = 'silent';
      if(S.state === 'silent' && S.opened && t - S.opened > 90e3){ try{ S.ws.close(); }catch(e){} }      // silent too long: close, so a retry (and the next address) follows""")
rep("""    sock('spot', URL_SPOT + S.spot.join('/'), onSpot);""",
    """    var SP = sock('spot', URL_SPOT + S.spot.join('/'), onSpot); SP.alts = SPOT_ALTS; SP.suffix = S.spot.join('/');""")
rep("""  function minuteJobs(){ var nh = Math.floor(now()/H);""", """  // ── backup: when a feed is not live, fill its empty minutes from the exchange's 1-minute candles (v6.5.101) ──
  var REST = { s:{ on:false, ok:0, bad:0, min:0, at:0, err:null, last:0, host:0 }, p:{ on:false, ok:0, bad:0, min:0, at:0, err:null, last:0 }, c:{ on:false, ok:0, bad:0, min:0, at:0, err:null } }, restHours = {}, restBusy = false;
  var FLOG_KEY = 'omega_watch_feedlog_v1';
  function feedLive(S){ return !!(S && S.state === 'live' && Date.now() - (S.last || 0) < 120e3); }
  async function fetchJ(u){ var ac = typeof AbortController !== 'undefined' ? new AbortController() : null, to = ac ? setTimeout(function(){ ac.abort(); }, 10e3) : null;
    try{ var r = await fetch(u, ac ? { signal:ac.signal } : undefined); if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); } finally { if(to) clearTimeout(to); } }
  function feedLog(){ try{ var L = JSON.parse(localStorage.getItem(FLOG_KEY) || '{}'), d = new Date().toISOString().slice(0, 10), D = L[d] = L[d] || {};
      ['spot', 'futures', 'coinbase'].forEach(function(k){ var x = D[k] = D[k] || { live:0, dead:0 }; if(feedLive(socks[k])) x.live++; else x.dead++; });
      D.backupMin = (D.backupMin || 0); var ks = Object.keys(L).sort(); while(ks.length > 30) delete L[ks.shift()]; localStorage.setItem(FLOG_KEY, JSON.stringify(L)); return L; }catch(e){ return {}; } }
  async function restFill(){ if(!running || restBusy || !store) return; restBusy = true; var filled = 0;
    try{ var c = cfg(), tnow = now(), since = st.since || tnow;
      for(var q = 0; q < 2; q++){ var mk = q ? 'p' : 's', S = q ? socks.futures : socks.spot, R = REST[mk];
        if(feedLive(S)){ R.on = false; continue; } R.on = true;
        var from = Math.max(since - 60e3, R.last ? R.last + 60e3 : 0), lim = Math.max(3, Math.min(60, Math.ceil((tnow - from)/60e3) + 1)), ok = 0, bad = 0, err = null, newest = R.last || 0;
        for(var i = 0; i < c.coins.length && running; i++){ var sym = c.coins[i];
          try{ var base = mk === 's' ? SPOT_HOSTS[R.host % SPOT_HOSTS.length] + '/api/v3/klines' : FAPI + '/fapi/v1/klines';
            var ks = await fetchJ(base + '?symbol=' + sym + '&interval=1m&limit=' + lim); ok++;
            (ks || []).forEach(function(k){ var t = +k[0], c0 = +k[4], qv = +k[7], Qb = +k[10];
              if(!(t > 0) || !(c0 > 0) || +k[6] >= tnow || t < since - 60e3) return;                         // closed minutes since recording started
              if(!nan(get(sym, Math.floor(t/60e3), mk + 'C'))) return;                                       // the stream has it: never overwrite
              put(sym, t, mk + 'C', c0); if(qv >= 0 && Qb >= 0){ put(sym, t, mk + 'Buy', Qb); put(sym, t, mk + 'Sell', Math.max(0, qv - Qb)); } put(sym, t, mk + 'N', +k[8]);
              if(mk === 's'){ put(sym, t, 'sH', +k[2]); put(sym, t, 'sL', +k[3]); if(sym === 'BTCUSDT') put(MKT, t, 'bnBTC', c0); if(sym === 'ETHUSDT') put(MKT, t, 'bnETH', c0); }
              restHours[sym + '|' + mk + '|' + Math.floor(t/H)] = 1; R.min++; filled++; if(t > newest) newest = t; }); }
          catch(e){ bad++; err = err || String(e && e.message || e); if(mk === 's' && i === 0) R.host++; } }
        R.ok += ok; R.bad += bad; R.err = err; R.at = Date.now(); if(newest) R.last = newest; }
      var CBR = REST.c;
      if(feedLive(socks.coinbase)) CBR.on = false;
      else { CBR.on = true; var P = [['BTC-USD', 'cbBTC'], ['ETH-USD', 'cbETH'], ['USDT-USD', 'cbUSDT']];
        for(var k2 = 0; k2 < P.length && running; k2++){ try{ var cs = await fetchJ('https://api.exchange.coinbase.com/products/' + P[k2][0] + '/candles?granularity=60'); CBR.ok++;
            (cs || []).forEach(function(x){ var t = +x[0]*1000, cl = +x[4]; if(!(cl > 0) || t < since - 60e3 || t + 60e3 > tnow) return; if(!nan(get(MKT, Math.floor(t/60e3), P[k2][1]))) return; put(MKT, t, P[k2][1], cl); CBR.min++; filled++; }); }
          catch(e){ CBR.bad++; CBR.err = String(e && e.message || e); } }
        CBR.at = Date.now(); } }
    finally { restBusy = false; }
    try{ var L = JSON.parse(localStorage.getItem(FLOG_KEY) || '{}'), d = new Date().toISOString().slice(0, 10); if(L[d]){ L[d].backupMin = (L[d].backupMin || 0) + filled;
        var bh = L[d].bh = L[d].bh || {}; Object.keys(restHours).forEach(function(k){ var p = k.split('|'), kk = p[0] + '|' + p[1], h = +p[2]; bh[kk] = bh[kk] || []; if(bh[kk].indexOf(h) < 0) bh[kk].push(h); });   // which hours the backup filled, per coin and feed
        Object.keys(L).sort().slice(0, -8).forEach(function(x){ delete L[x].bh; }); localStorage.setItem(FLOG_KEY, JSON.stringify(L)); } }catch(e){}
    return filled; }
  function diag(){ var o = { at:new Date().toISOString(), feeds:{}, backup:JSON.parse(JSON.stringify(REST)), backupHours:Object.keys(restHours).length, err:st.err || null, since:st.since ? new Date(st.since).toISOString() : null, daily:{} };
    Object.keys(socks).forEach(function(k){ var S = socks[k]; o.feeds[k] = { state:S.state, msgs:S.n, bytes:S.bytes, last:S.last ? new Date(S.last).toISOString() : null, err:S.err || null, closeCode:S.code || null, tries:S.tries, everLive:!!S.everLive, rotations:S.rotations || 0, address:String(S.url || '').split('?')[0] }; });
    try{ o.daily = JSON.parse(localStorage.getItem(FLOG_KEY) || '{}'); }catch(e){} return o; }
  function restLine(){ var on = [['s', 'spot'], ['p', 'futures'], ['c', 'Coinbase']].filter(function(x){ return REST[x[0]].on; }); if(!on.length || !running) return '';
    var n = REST.s.min + REST.p.min + REST.c.min, e = REST.s.err || REST.p.err || REST.c.err;
    return '<p class="hint" style="margin:0 0 8px;color:var(--gold);"><b>Backup on:</b> the live ' + on.map(function(x){ return x[1]; }).join(' and ') + ' stream' + (on.length > 1 ? 's are' : ' is') + ' not delivering, so prices and buy/sell volumes are filled each minute from the exchange’s 1-minute candles (' + n.toLocaleString() + ' minutes so far). Liquidations, large orders and flight recordings need the live stream and stay empty until it works.' + (e ? ' Last backup error: ' + esc(e) + '.' : '') + '</p>'; }
  function minuteJobs(){ var nh = Math.floor(now()/H); feedLog(); restFill().then(function(n){ if(n) maybeRender(); }).catch(function(){});""")
rep("""Event rows: t in seconds from the trigger.' };""", """Event rows: t in seconds from the trigger.', diag:diag() };""")
rep("""pill('Coinbase', socks.coinbase) + '</div>';""", """pill('Coinbase', socks.coinbase) + '</div>' + restLine();""")
rep("""    _:{ watchdog:watchdog,""", """    _:{ restFill:restFill, diag:diag, REST:REST, feedLive:feedLive, watchdog:watchdog,""")
s = s[:i] + m + s[j:]
R0 = """    ['', '', '· Hour-of-day timing', 'The biggest average hourly moves are 0.03–0.09%; a round trip costs 0.12–0.20%.']
  ];"""
R1 = """    ['', '', '· Hour-of-day timing', 'The biggest average hourly moves are 0.03–0.09%; a round trip costs 0.12–0.20%.'],
    ['FAILED', 'var(--bear)', 'Forex majors hour by hour (E15)', 'EUR/USD, GBP/USD, USD/JPY, AUD/USD and USD/CAD, 2020 → Oct 2026, eleven rules each at 0.015% a side: no rule was even promising before 2024 (best t 1.39), and every pick was flat or negative from 2024.'],
    ['WAITING', 'var(--gold)', 'Market Watch questions (E13)', 'Liquidation flushes, absorption, Coinbase leading Binance. The 19–26 Oct recording held no minute data: the live streams delivered nothing on that device. v6.5.101 adds a backup and explains every export; E13 needs 5 days with the live streams working (the backup has no liquidations).']
  ];"""
assert s.count(R0) == 1, 'rows anchor'; s = s.replace(R0, R1)
now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.100 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']: s = s.replace('v6.5.100 ' + sep + ' build ' + o + ' UTC', 'v6.5.101 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.101 · build' in s and 'v6.5.100 · build' not in s
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now)
