<script>/* ═══ FRESH COINS FOR RESEARCH (v6.5.57) — 50 coins no rule has ever been designed or tested on, Jan 2020 to now ═══
   Every year of the 25 studied coins has been used, so a rule designed now can only be tested honestly on data nothing
   has seen. Other coins are such data. This downloads hourly spot bars and USDT-M funding for the fixed list below,
   straight from Binance into one file (omega-history v2, part "fresh"). Nothing is stored on the phone; prices and
   funding only. The list was fixed in the research plan before any of it was downloaded. */
(function(){
  'use strict';
  var FRESH = ['AAVE','HBAR','EOS','ALGO','VET','THETA','XTZ','ZEC','DASH','NEO','IOTA','ONT','QTUM','ZIL','KAVA','RUNE','SNX','COMP','CRV','SUSHI','YFI','1INCH','GRT','SAND','MANA',
    'AXS','CHZ','ENJ','EGLD','LDO','IMX','STX','FET','KSM','BAT','ZRX','CELO','ROSE','GALA','APE','DYDX','MASK','AR','KNC','IOTX','ANKR','RVN','ICX','ONE','GMT','CFX'].map(function(s){ return s + 'USDT'; });
  var FROM = Date.UTC(2020, 0, 1), busy = false, stop = false;
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  async function getJSON(url){ for(var a=0; a<4; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(5000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 3) throw e; await sleep(1500*(a+1)); } } return []; }
  async function klines(sym, to, onPage){ var rows = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON('https://data-api.binance.vision/api/v3/klines?symbol=' + sym + '&interval=1h&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < to) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + 3600e3; if(onPage) onPage(rows.length); await sleep(120); }
    return rows; }
  async function funding(sym, to){ var out = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON('https://fapi.binance.com/fapi/v1/fundingRate?symbol=' + sym + '&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(x){ var ft = +x.fundingTime; if(ft >= t && ft < to) out.push([ft, +x.fundingRate]); }); var last = +d[d.length-1].fundingTime; if(!(last >= t) || d.length < 1000) break; t = last + 1; await sleep(150); }
    return out; }
  async function run(){ if(busy){ stop = true; return 'stopping'; } busy = true; stop = false; var msg = el('freshExportMsg'), b = el('freshExportBtn'); if(b) b.textContent = 'Stop';
    try{ var L = window.OMEGA_LONGEXPORT; if(!L || !L.encode) throw new Error('older-history module missing');
      var to = Math.floor(Date.now()/3600e3)*3600e3;   // up to the last finished hour
      var out = { format:'omega-history', v:2, part:'fresh', from:new Date(FROM).toISOString(), to:new Date(to).toISOString(), exportedAt:new Date().toISOString(), tf:60, markets:[], skipped:[] };
      for(var k=0; k<FRESH.length && !stop; k++){ var sym = FRESH[k];
        try{ var rows = await klines(sym, to, function(n){ if(msg) msg.textContent = sym + ' (' + (k + 1) + ' of ' + FRESH.length + '): ' + n.toLocaleString() + ' hourly bars…'; });
          if(rows.length < 24*30){ out.skipped.push(sym + ': ' + (rows.length ? 'under a month of bars' : 'not served by Binance spot')); continue; }
          if(msg) msg.textContent = sym + ' (' + (k + 1) + ' of ' + FRESH.length + '): funding…'; var f = []; try{ f = await funding(sym, to); }catch(eF){}
          if(!f.length) out.skipped.push(sym + ': no USDT-M funding (prices kept)');
          out.markets.push(L.encode(sym, rows, f)); }catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
      if(stop) throw new Error('stopped');
      var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
      var blob, name = 'omega-history-fresh-' + new Date().toISOString().slice(0, 10);
      if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove();
      var bars = out.markets.reduce(function(s, m){ return s + m.n; }, 0), r = 'Saved ' + name + ' (' + Math.round(blob.size/1048576*10)/10 + ' MB): ' + out.markets.length + ' coins, ' + bars.toLocaleString() + ' hourly bars from 2020, funding for ' + out.markets.filter(function(m){ return m.fund; }).length + '. Attach it for research.';
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Fresh-coins download ' + (stop ? 'stopped.' : 'stopped: ' + (e && e.message || e)); return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = 'Download fresh coins (2020 – now) for research'; } }
  function wire(){ var host = el('longExportBtn'); if(!host || el('freshExportBtn')) return !!el('freshExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '10px';
    wrap.innerHTML = '<button class="btn-outline" type="button" id="freshExportBtn">Download fresh coins (2020 – now) for research</button> <span class="hint" id="freshExportMsg">' + FRESH.length + ' coins no rule has ever been tested on, straight from Binance into one file (about 3,000 requests, 10–20 minutes; nothing is stored on the phone). Keep the app open and the screen on.</span>';
    host.parentNode.parentNode.appendChild(wrap); var b = el('freshExportBtn'); if(b) b.addEventListener('click', function(){ run(); }); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 40) clearInterval(iv); }, 1000);
  window.OMEGA_FRESHEXPORT = { run:run, FRESH:FRESH, FROM:FROM };
})();
</script>
