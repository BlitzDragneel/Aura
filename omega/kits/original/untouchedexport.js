<script>/* ═══ UNTOUCHED COINS FOR THE FINAL TEST (v6.5.68) — every Binance coin no research round has used, daily, 2020 to now ═══
   For round 12 (PLAN12: 600 known strategies, 100 combinations). Every coin used so far (25 studied, 51 fresh, 90 new)
   has been seen by some rule, so the final test needs coins nothing has touched. The list is fixed by a rule written in
   the plan, not by hand: every Binance spot pair against USDT that is trading now, whose coin is not one of the 166
   already used, is not a stablecoin, fiat, wrapped coin or gold token, and has daily bars from before 1 Apr 2025.
   Downloads daily spot bars from Jan 2020 and USDT-M funding (when the coin has a perpetual), straight from Binance into
   one file (omega-history v2, part "final3"). Nothing is stored on the phone; prices and funding only. */
(function(){
  'use strict';
  var STUDIED = ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'];
  var NOT_COINS = ['USDC','FDUSD','TUSD','BUSD','DAI','USDP','PAX','USDS','USDE','USD1','XUSD','BFUSD','RLUSD','PYUSD','EUR','EURI','AEUR','GBP','AUD','TRY','BRL','BIDR','IDRT','UAH','RUB','ZAR','NGN','PLN','RON','ARS','JPY','MXN','COP','CZK','PAXG','XAUT','WBTC','WBETH','BETH','STETH','BNSOL','WBNB'];
  var FROM = Date.UTC(2020, 0, 1), LISTED_BEFORE = Date.UTC(2025, 3, 1), API = 'https://data-api.binance.vision/api/v3/', busy = false, stop = false;
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  async function getJSON(url){ for(var a=0; a<4; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(8000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 3) throw e; await sleep(1500*(a+1)); } } return []; }
  function used(){ var F = (window.OMEGA_FRESHEXPORT && window.OMEGA_FRESHEXPORT.FRESH) || [], N = (window.OMEGA_FRESH2EXPORT && window.OMEGA_FRESH2EXPORT.FRESH) || [], u = {};
    STUDIED.forEach(function(b){ u[b] = 1; }); F.concat(N).forEach(function(s){ u[String(s).replace(/USDT$/, '')] = 1; }); return u; }
  // the rule, applied to the list of symbols Binance serves now (pure, so it can be tested)
  function pick(symbols, U){ var out = [], why = {};
    symbols.forEach(function(s){ s = String(s); if(!/USDT$/.test(s)) return; var b = s.slice(0, -4);
      if(!b || U[b]){ return; }
      if(NOT_COINS.indexOf(b) > -1 || /USD/.test(b)){ why[s] = 'stablecoin, fiat, wrapped or gold'; return; }
      if(/(UP|DOWN|BULL|BEAR)$/.test(b) && b.length > 4){ why[s] = 'leveraged token'; return; }
      out.push(s); });
    return { list:out.sort(), excluded:why }; }
  async function symbolsNow(){ var d = null;
    try{ d = await getJSON(API + 'ticker/price'); if(Array.isArray(d) && d.length > 100) return d.map(function(x){ return x.symbol; }); }catch(e){}
    var e = await getJSON(API + 'exchangeInfo?permissions=SPOT'); if(e && Array.isArray(e.symbols)) return e.symbols.filter(function(x){ return x.status === 'TRADING'; }).map(function(x){ return x.symbol; });
    throw new Error('could not read the list of Binance coins'); }
  async function daily(sym, to){ var rows = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON(API + 'klines?symbol=' + sym + '&interval=1d&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < to) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + 86400e3; await sleep(120); }
    return rows; }
  async function funding(sym, to){ var out = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON('https://fapi.binance.com/fapi/v1/fundingRate?symbol=' + sym + '&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(x){ var ft = +x.fundingTime; if(ft >= t && ft < to) out.push([ft, +x.fundingRate]); }); var last = +d[d.length-1].fundingTime; if(!(last >= t) || d.length < 1000) break; t = last + 1; await sleep(150); }
    return out; }
  async function run(){ if(busy){ stop = true; return 'stopping'; } busy = true; stop = false; var msg = el('final3ExportMsg'), b = el('final3ExportBtn'); if(b) b.textContent = 'Stop';
    try{ var L = window.OMEGA_LONGEXPORT; if(!L || !L.encode) throw new Error('older-history module missing');
      var to = Math.floor(Date.now()/86400e3)*86400e3;   // up to the last finished day (UTC)
      if(msg) msg.textContent = 'Reading the list of Binance coins…'; var all = await symbolsNow(), P = pick(all, used());
      var out = { format:'omega-history', v:2, part:'final3', rule:'every Binance spot USDT pair trading now whose coin is not among the 166 used before (25 studied, 51 fresh, 90 new), not a stablecoin, fiat, wrapped coin or gold token, with daily bars from before 2025-04-01', from:new Date(FROM).toISOString(), to:new Date(to).toISOString(), exportedAt:new Date().toISOString(), tf:1440,
        symbolsServed:all.length, candidates:P.list.length, excluded:P.excluded, markets:[], skipped:[] };
      for(var k=0; k<P.list.length && !stop; k++){ var sym = P.list[k], head = sym + ' (' + (k + 1) + ' of ' + P.list.length + '): ';
        try{ if(msg) msg.textContent = head + 'daily bars…'; var rows = await daily(sym, to);
          if(!rows.length){ out.skipped.push(sym + ': no daily bars'); continue; }
          if(+rows[0][0] >= LISTED_BEFORE){ out.skipped.push(sym + ': listed ' + new Date(+rows[0][0]).toISOString().slice(0, 10) + ' (after 2025-03-31)'); continue; }
          if(+rows[rows.length - 1][0] < to - 3*86400e3){ out.skipped.push(sym + ': no bars in the last 3 days'); continue; }
          if(msg) msg.textContent = head + 'funding…'; var f = []; try{ f = await funding(sym, to); }catch(eF){}
          out.markets.push(L.encode(sym, rows, f)); }
        catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
      if(stop) throw new Error('stopped');
      var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
      var blob, name = 'omega-history-final3-' + new Date().toISOString().slice(0, 10);
      if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
      var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
      var again = el('final3SaveAgain'); if(again) again.innerHTML = 'Not in your Downloads? <a href="' + url + '" download="' + name + '">Tap here to save ' + name + '</a>.';
      var r = 'Saved ' + name + ' (' + Math.round(blob.size/1048576*10)/10 + ' MB): ' + out.markets.length + ' untouched coins, daily from 2020, funding for ' + out.markets.filter(function(m){ return m.fund; }).length + ' (' + out.skipped.length + ' skipped). Attach it for research.';
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Untouched-coins download ' + (stop ? 'stopped. Press again to start over.' : 'stopped: ' + (e && e.message || e) + '. Press again to start over.'); return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = 'Download the untouched coins for the final test'; } }
  function wire(){ var host = el('fresh2ExportBtn'); if(!host || el('final3ExportBtn')) return !!el('final3ExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '10px';
    wrap.innerHTML = '<button class="btn-outline" type="button" id="final3ExportBtn">Download the untouched coins for the final test</button> <span class="hint" id="final3ExportMsg">Every Binance coin no research round has used yet, daily from 2020, with funding: one file for round 12 (600 strategies and 100 combinations). About 10–20 minutes; keep the app open and the screen on. Nothing is stored on the phone.</span> <span class="hint" id="final3SaveAgain"></span>';
    host.parentNode.parentNode.appendChild(wrap); var bt = el('final3ExportBtn'); if(bt) bt.addEventListener('click', function(){ run(); }); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_FINAL3EXPORT = { run:run, pick:pick, used:used, NOT_COINS:NOT_COINS, LISTED_BEFORE:LISTED_BEFORE };
})();
</script>
