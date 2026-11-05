<script>/* ═══ ROUND 14 FINAL TEST DATA (v6.5.71) — hourly perpetuals of coins no research round has touched ═══
   Round 14 (PLAN14) found one rule that passed its screen and its validation on hourly perpetual data: buying a coin
   after a capitulation hour (a fall of 5 or more of its own hourly standard deviations) while its perpetual trades at
   an unusual discount to spot, held 12 hours. Its final test needs hourly data for coins nothing has touched. The list
   is fixed by addendum A of the plan (written before any of this data existed):
   · the 125 coins of the round-12 untouched file that have a USDT perpetual under the same symbol;
   · every USDT-M perpetual trading now, onboarded on or after 1 Apr 2025, whose coin is not one of the 166 coins used
     before, the 155 of the untouched file, a stablecoin, fiat, wrapped or gold token, or a leveraged token, with at
     least 60 days of candles.
   For each: hourly perpetual candles (with taker-buy volume), the hourly premium index and funding, from Jan 2020 (or
   listing) to now. Saved in parts as each part finishes; each part can be downloaded again on its own. Prices only. */
(function(){
  'use strict';
  var F3P = ["1000CAT", "1000CHEEMS", "1000SATS", "1MBABYDOGE", "ACT", "AI", "AIXBT", "ALPINE", "ANIME", "ARK", "ASR", "ASTR", "AUCTION", "AUDIO", "AVA", "AXL", "BANANAS31", "BANANA", "BB", "BEAMX", "BEL", "BERA", "BIO", "BMT", "BOME", "BROCCOLI714", "CAKE", "CATI", "CETUS", "CGPT", "COOKIE", "COW", "CTK", "CVC", "CVX", "DEXE", "DGB", "DIA", "DODO", "DOGS", "EIGEN", "EPIC", "FIDA", "FLUX", "FORM", "FTT", "GAS", "GLMR", "GPS", "GUN", "G", "HEI", "HIVE", "HMSTR", "HOT", "ILV", "JST", "KAIA", "KAITO", "LAYER", "LISTA", "LSK", "LUMIA", "LUNA", "MBL", "MEME", "METIS", "ME", "MOVE", "MOVR", "MUBARAK", "NEIRO", "NIL", "OG", "ONG", "ORCA", "PARTI", "PENGU", "PHA", "PIXEL", "PNUT", "POL", "POLYX", "POWR", "PROM", "PUNDIX", "QUICK", "RAD", "RARE", "RAY", "RED", "RENDER", "REZ", "RIF", "RONIN", "RPL", "SANTOS", "SCR", "SC", "SHELL", "SLP", "SOLV", "SPELL", "STEEM", "STRAX", "SUN", "S", "SYN", "TAO", "THE", "TRUMP", "TST", "TURBO", "T", "TUT", "USTC", "USUAL", "VANA", "VELODROME", "VTHO", "WAXP", "WIF", "W", "XVG", "ZRO"], F3A = ["1000CAT", "1000CHEEMS", "1000SATS", "1MBABYDOGE", "ACM", "ACT", "ADX", "AI", "AIXBT", "ALPINE", "AMP", "ANIME", "ARK", "ASR", "ASTR", "ATM", "AUCTION", "AUDIO", "AVA", "AXL", "BANANA", "BANANAS31", "BAR", "BB", "BEAMX", "BEL", "BERA", "BIO", "BMT", "BOME", "BONK", "BROCCOLI714", "BTTC", "CAKE", "CATI", "CETUS", "CGPT", "CITY", "COOKIE", "COW", "CTK", "CVC", "CVX", "DCR", "DEXE", "DGB", "DIA", "DODO", "DOGS", "EIGEN", "EPIC", "FIDA", "FLOKI", "FLUX", "FORM", "FTT", "G", "GAS", "GLMR", "GNO", "GNS", "GPS", "GUN", "HEI", "HIVE", "HMSTR", "HOT", "ILV", "IQ", "JST", "JUV", "KAIA", "KAITO", "LAYER", "LAZIO", "LISTA", "LSK", "LUMIA", "LUNA", "LUNC", "MBL", "ME", "MEME", "METIS", "MOVE", "MOVR", "MUBARAK", "NEIRO", "NEXO", "NIL", "OG", "ONG", "ORCA", "OSMO", "PARTI", "PENGU", "PEPE", "PHA", "PIXEL", "PNUT", "POL", "POLYX", "PORTO", "POWR", "PROM", "PSG", "PUNDIX", "QI", "QKC", "QUICK", "RAD", "RARE", "RAY", "RED", "RENDER", "REQ", "REZ", "RIF", "RONIN", "RPL", "S", "SANTOS", "SC", "SCR", "SHELL", "SHIB", "SLP", "SOLV", "SPELL", "STEEM", "STRAX", "SUN", "SYN", "T", "TAO", "TFUEL", "THE", "TKO", "TRUMP", "TST", "TURBO", "TUT", "USTC", "USUAL", "VANA", "VELODROME", "VTHO", "W", "WAXP", "WIF", "WIN", "XEC", "XNO", "XVG", "ZRO"];
  var STUDIED = ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'];
  var NOT_COINS = ['USDC','FDUSD','TUSD','BUSD','DAI','USDP','PAX','USDS','USDE','USD1','XUSD','BFUSD','RLUSD','PYUSD','EUR','EURI','AEUR','GBP','AUD','TRY','BRL','BIDR','IDRT','UAH','RUB','ZAR','NGN','PLN','RON','ARS','JPY','MXN','COP','CZK','PAXG','XAUT','WBTC','WBETH','BETH','STETH','BNSOL','WBNB'];
  var FROM = Date.UTC(2020, 0, 1), YOUNG_FROM = Date.UTC(2025, 3, 1), FAPI = 'https://fapi.binance.com', PKEY = 'omega_final4dl_v1', busy = false, stop = false, kept = [], youngList = null;
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function lsGet(){ try{ var v = JSON.parse(localStorage.getItem(PKEY) || 'null'); return v && typeof v === 'object' && v.done ? v : { done:{} }; }catch(e){ return { done:{} }; } }
  function lsSet(v){ try{ localStorage.setItem(PKEY, JSON.stringify(v)); }catch(e){} }
  function norm(b){ return String(b).replace(/^(1000000|100000|10000|1000|1M)(?=[A-Z])/, ''); }
  function usedSet(){ var u = {}, F = (window.OMEGA_FRESHEXPORT && window.OMEGA_FRESHEXPORT.FRESH) || [], N = (window.OMEGA_FRESH2EXPORT && window.OMEGA_FRESH2EXPORT.FRESH) || [];
    STUDIED.forEach(function(b){ u[b] = 1; }); F.concat(N).forEach(function(s){ u[norm(String(s).replace(/USDT$/, ''))] = 1; }); F3A.forEach(function(b){ u[norm(b)] = 1; }); return u; }
  // the plan's rule for the young perpetuals, applied to Binance's futures exchangeInfo (pure, so it can be tested)
  function pickYoung(info, U){ var out = [], why = {};
    ((info && info.symbols) || []).forEach(function(x){ var s = String(x.symbol || ''), b = String(x.baseAsset || '');
      if(x.contractType !== 'PERPETUAL' || x.quoteAsset !== 'USDT' || x.status !== 'TRADING' || !/USDT$/.test(s)) return;
      if(!(+x.onboardDate >= YOUNG_FROM)) return;
      if(x.underlyingType && x.underlyingType !== 'COIN'){ why[s] = 'not a coin (' + x.underlyingType + ')'; return; }
      var nb = norm(b);
      if(/^(XAU|XAG|XPT|XPD)$/.test(nb)){ why[s] = 'metal'; return; }
      if(U[nb]){ why[s] = 'used before or in the untouched file'; return; }
      if(NOT_COINS.indexOf(nb) > -1 || /USD/.test(nb)){ why[s] = 'stablecoin, fiat, wrapped or gold'; return; }
      if(/(UP|DOWN|BULL|BEAR)$/.test(nb) && nb.length > 4){ why[s] = 'leveraged token'; return; }
      out.push(s); });
    return { list:out.sort(), excluded:why }; }
  function groups(){ var g = [], P = F3P.map(function(b){ return b + 'USDT'; });
    for(var i=0; i<P.length; i += 32) g.push({ id:'f4-' + 'abcd'.charAt(i/32), label:'untouched coins, part ' + (i/32 + 1), coins:P.slice(i, i + 32) });
    g.push({ id:'f4-young', label:'perpetuals listed since April 2025', young:true });
    return g; }
  var SHORT = { 'f4-a':'Untouched 1', 'f4-b':'Untouched 2', 'f4-c':'Untouched 3', 'f4-d':'Untouched 4', 'f4-young':'New listings' };
  async function getJSON(url){ for(var a=0; a<5; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(15000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 4) throw e; await sleep(2000*(a+1)); } } return []; }
  async function paged(path, sym, from, to, onPage){ var rows = [], t = from;
    while(t < to && !stop){ var d = await getJSON(FAPI + path + '?symbol=' + sym + '&interval=1h&limit=1500&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < to) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + 3600e3; if(onPage) onPage(rows.length); await sleep(320); }
    return rows; }
  async function funding(sym, from, to){ var out = [], t = from;
    while(t < to && !stop){ var d = await getJSON(FAPI + '/fapi/v1/fundingRate?symbol=' + sym + '&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(x){ var ft = +x.fundingTime; if(ft >= t && ft < to) out.push([ft, +x.fundingRate]); }); var last = +d[d.length-1].fundingTime; if(!(last >= t) || d.length < 1000) break; t = last + 1; await sleep(200); }
    return out; }
  function encodePrem(rows){ var p = { t:[], c:[] }, pt = 0; rows.forEach(function(k, i){ var th = Math.round(+k[0]/3600e3); p.t.push(i ? th - pt : th); pt = th; p.c.push(Math.round(+k[4]*1e7)); }); return p; }
  async function save(out, name){ var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
    var blob; if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    var mb = Math.round(blob.size/1048576*10)/10; kept = kept.filter(function(k){ return k.name !== name; }); kept.push({ name:name, url:url, mb:mb }); showKept(); return { name:name, mb:mb }; }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function showKept(){ var k = el('f4SaveAgain'); if(!k) return; if(!kept.length){ k.innerHTML = ''; return; }
    k.innerHTML = 'Not in your Downloads? Tap a name to save it again: ' + kept.map(function(x){ return '<a href="' + x.url + '" download="' + esc(x.name) + '">' + esc(x.name) + '</a> (' + x.mb + ' MB)'; }).join(' · '); }
  function oneButtons(){ var row = el('f4OneRow'); if(!row) return; var P = lsGet();
    groups().forEach(function(g){ var bt = row.querySelector('[data-g="' + g.id + '"]'); if(!bt) return; bt.textContent = (P.done[g.id] ? '✓ ' : '') + (SHORT[g.id] || g.id); bt.disabled = busy; }); }
  function label(){ var G = groups(), P = lsGet(), n = G.filter(function(g){ return P.done[g.id]; }).length; return n === G.length ? 'Download all ' + G.length + ' final-test files again' : n ? 'Continue the final-test download (' + n + ' of ' + G.length + ' files saved)' : 'Download the round-14 final-test data (' + G.length + ' files)'; }
  async function coinInto(out, sym, from, to, tag, msg, minHours){
    var rows = await paged('/fapi/v1/klines', sym, from, to, function(n){ if(msg) msg.textContent = tag + n.toLocaleString() + ' perpetual hours…'; });
    if(rows.length < minHours){ out.skipped.push(sym + ': ' + rows.length + ' hours of perpetual candles (under ' + minHours + ')'); return; }
    var prem = await paged('/fapi/v1/premiumIndexKlines', sym, from, to, function(n){ if(msg) msg.textContent = tag + n.toLocaleString() + ' premium hours…'; });
    if(msg) msg.textContent = tag + 'funding…'; var f = []; try{ f = await funding(sym, from, to); }catch(eF){}
    var m = window.OMEGA_LONGEXPORT.encode(sym, rows, f); m.src = 'Binance USD-M perpetual'; if(prem.length) m.prem = encodePrem(prem); out.markets.push(m); }
  async function run(onlyId){ if(busy){ stop = true; return 'stopping'; } var G = groups(); if(onlyId && !G.some(function(g){ return g.id === onlyId; })) return 'no such file';
    busy = true; stop = false; var msg = el('f4ExportMsg'), b = el('f4ExportBtn'); if(b) b.textContent = 'Stop'; oneButtons();
    var P = lsGet(); if(!onlyId && G.every(function(g){ return P.done[g.id]; })) P = { done:{} };
    var said = [];
    try{ if(!window.OMEGA_LONGEXPORT || !window.OMEGA_LONGEXPORT.encode) throw new Error('older-history module missing');
      for(var gi=0; gi<G.length && !stop; gi++){ var g = G[gi]; if(onlyId ? g.id !== onlyId : P.done[g.id]) continue;
        var to = Math.floor(Date.now()/3600e3)*3600e3, head = 'File ' + (gi + 1) + ' of ' + G.length + ' (' + g.label + '): ';
        var out = { format:'omega-history', v:2, part:'final4-' + g.id.slice(3), plan:'PLAN14 addendum A', src:'Binance USD-M perpetuals', from:new Date(FROM).toISOString(), to:new Date(to).toISOString(), exportedAt:new Date().toISOString(), tf:60, markets:[], skipped:[] };
        var coins = g.coins;
        if(g.young){ if(msg) msg.textContent = head + 'reading Binance’s list of perpetuals…'; var info = await getJSON(FAPI + '/fapi/v1/exchangeInfo'); var pk = pickYoung(info, usedSet()); coins = pk.list; youngList = coins;
          out.rule = 'USDT-M perpetuals trading now, onboarded on or after 2025-04-01, coin not among the 166 used, the 155 of final3, stablecoins/fiat/wrapped/gold or leveraged tokens; at least 60 days of candles'; out.excluded = pk.excluded; out.served = ((info && info.symbols) || []).length; }
        for(var k=0; k<coins.length && !stop; k++){ var sym = coins[k], tag = head + sym + ' (' + (k + 1) + ' of ' + coins.length + '): ';
          try{ await coinInto(out, sym, g.young ? YOUNG_FROM - 86400e3 : FROM, to, tag, msg, g.young ? 24*60 : 24*30); }catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
        if(stop) break;
        if(msg) msg.textContent = head + 'saving…';
        var sv = await save(out, 'omega-history-final4-' + g.id.slice(3) + '-' + new Date().toISOString().slice(0, 10)); P.done[g.id] = sv.name; lsSet(P); said.push(sv.name + ' (' + sv.mb + ' MB, ' + out.markets.length + ' coins)'); await sleep(1500); }
      var n = G.filter(function(g){ return P.done[g.id]; }).length, r = (stop ? 'Stopped. ' : '') + (onlyId ? (said.length ? 'Saved now: ' + said.join(', ') + '. Attach it for research.' : 'Nothing saved.')
        : n + ' of ' + G.length + ' files saved.' + (said.length ? ' Saved now: ' + said.join(', ') + '.' : '') + ' ' + (n === G.length ? 'All done — attach all ' + G.length + ' files for research.' : 'Press again to continue from the next file.'));
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Final-test download stopped: ' + (e && e.message || e) + '. Press again to continue.'; return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = label(); oneButtons(); } }
  function wire(){ var host = el('futExportBtn'); if(!host || el('f4ExportBtn')) return !!el('f4ExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '14px';
    wrap.innerHTML = '<p class="hint" style="margin:0 0 6px;color:var(--text);"><b>Round 14 final test.</b> Hourly perpetual candles, premium and funding for coins no research round has touched (the 125 untouched coins with a perpetual, plus perpetuals listed since April 2025). 5 files, each saved as soon as it is done — about 90 minutes in all. Keep the app open and the screen on; if it stops, press again to continue.</p>' +
      '<button class="btn-outline" type="button" id="f4ExportBtn">' + label() + '</button> <span class="hint" id="f4ExportMsg"></span>';
    var one = document.createElement('div'); one.id = 'f4OneRow'; one.style.cssText = 'margin-top:6px; display:flex; flex-wrap:wrap; gap:6px; align-items:center';
    one.innerHTML = '<span class="hint">One file on its own:</span>' + groups().map(function(g){ return '<button class="btn-outline" type="button" style="padding:5px 9px" data-g="' + g.id + '">' + esc(SHORT[g.id] || g.id) + '</button>'; }).join('') +
      '<span class="hint" id="f4SaveAgain" style="flex-basis:100%; word-break:break-all"></span>';
    wrap.appendChild(one); host.parentNode.parentNode.appendChild(wrap); var b = el('f4ExportBtn'); if(b) b.addEventListener('click', function(){ run(); });
    Array.prototype.forEach.call(one.querySelectorAll('[data-g]'), function(bt){ bt.addEventListener('click', function(){ run(bt.getAttribute('data-g')); }); }); oneButtons(); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_FINAL4EXPORT = { run:run, groups:groups, pickYoung:pickYoung, usedSet:usedSet, norm:norm, progress:lsGet, youngList:function(){ return youngList; }, kept:function(){ return kept.map(function(k){ return { name:k.name, mb:k.mb }; }); } };
})();
</script>
