<script>/* ═══ OLDER HISTORY FOR RESEARCH (v6.5.54) — 2019 to Oct 2023, downloaded from Binance straight into a file ═══
   Research on the stored 3 years has looked at the same data many times; a period no rule has ever been tested on is
   worth more than any new idea. This downloads hourly bars from 1 Jan 2019 (or listing) to 1 Oct 2023 for every crypto
   market OMEGA studies, and their funding history from Sep 2019, and saves them in the same compact format as the
   price-history export (omega-history v2, part "older"). Nothing is stored on the phone; prices and funding only. */
(function(){
  'use strict';
  var FROM = Date.UTC(2019, 0, 1), TO = Date.UTC(2023, 9, 1), busy = false, stop = false;
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function dpOf(px){ var d = 2; if(px < 1000) d = 3; if(px < 100) d = 4; if(px < 10) d = 5; if(px < 1) d = 6; if(px < 0.1) d = 7; if(px < 0.01) d = 8; return d; }
  function sig4(v){ if(!(v > 0)) return 0; var p = Math.pow(10, Math.max(0, 3 - Math.floor(Math.log10(v)))); return Math.round(v*p)/p; }
  async function getJSON(url){ for(var a=0; a<4; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(5000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 3) throw e; await sleep(1500*(a+1)); } } return []; }
  async function klines(sym, onPage){ var rows = [], t = FROM;
    while(t < TO && !stop){ var d = await getJSON('https://data-api.binance.vision/api/v3/klines?symbol=' + sym + '&interval=1h&limit=1000&startTime=' + t + '&endTime=' + (TO - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < TO) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + 3600e3; if(onPage) onPage(rows.length); await sleep(120); }
    return rows; }
  async function funding(sym){ var out = [], t = FROM;
    while(t < TO && !stop){ var d = await getJSON('https://fapi.binance.com/fapi/v1/fundingRate?symbol=' + sym + '&limit=1000&startTime=' + t + '&endTime=' + (TO - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(x){ var ft = +x.fundingTime; if(ft >= t && ft < TO) out.push([ft, +x.fundingRate]); }); var last = +d[d.length-1].fundingTime; if(!(last >= t) || d.length < 1000) break; t = last + 1; await sleep(150); }
    return out; }
  function encode(sym, rows, fund){ var med = +rows[Math.floor(rows.length/2)][4], dp = dpOf(med), sc = Math.pow(10, dp), m = { sym:sym, src:'Binance spot (downloaded for research)', dp:dp, n:rows.length, t:[], c:[], o:[], h:[], l:[], v:[], tb:[] }, pt = 0, pc = 0;
    rows.forEach(function(k, i){ var th = Math.round(+k[0]/3600e3), ci = Math.round(+k[4]*sc), oi = Math.round(+k[1]*sc), v = +k[5], tb = +k[9];   // bar time = its open, as the app's hourly bars
      m.t.push(i ? th - pt : th); pt = th; m.c.push(i ? ci - pc : ci); pc = ci; m.o.push(oi - ci); m.h.push(Math.round(+k[2]*sc) - Math.max(ci, oi)); m.l.push(Math.min(ci, oi) - Math.round(+k[3]*sc));
      m.v.push(sig4(v)); m.tb.push(v > 0 && isFinite(tb) ? Math.round(1000*tb/v) : -1); });
    if(fund && fund.length){ var pf = 0; m.fund = { t:[], r:[] }; fund.forEach(function(x, q){ var tm = Math.round(x[0]/60000); m.fund.t.push(q ? tm - pf : tm); pf = tm; m.fund.r.push(Math.round(x[1]*1e7)); }); }
    return m; }
  function markets(){ var H = window.OMEGA_HISTORY, ks = []; try{ ks = Object.keys(H.index() || {}); }catch(e){}
    var u = ks.filter(function(s){ return /USDT$/.test(s) && !/^(XAU|XAG|PAXG)/.test(s); }); if(u.length) return u;
    try{ return (window.OMEGA_DERIV.universe() || []).filter(function(s){ return /USDT$/.test(s); }); }catch(e){ return []; } }
  async function run(){ if(busy){ stop = true; return 'stopping'; } busy = true; stop = false; var msg = el('longExportMsg'), b = el('longExportBtn'); if(b) b.textContent = 'Stop';
    try{ var syms = markets(); if(!syms.length) throw new Error('no crypto markets on this copy yet');
      var out = { format:'omega-history', v:2, part:'older', from:new Date(FROM).toISOString(), to:new Date(TO).toISOString(), exportedAt:new Date().toISOString(), tf:60, markets:[], skipped:[] };
      for(var k=0; k<syms.length && !stop; k++){ var sym = syms[k];
        try{ var rows = await klines(sym, function(n){ if(msg) msg.textContent = sym + ' (' + (k + 1) + ' of ' + syms.length + '): ' + n.toLocaleString() + ' hourly bars…'; });
          if(rows.length < 24*30){ out.skipped.push(sym + ': ' + (rows.length ? 'under a month before Oct 2023' : 'not listed before Oct 2023')); continue; }
          if(msg) msg.textContent = sym + ' (' + (k + 1) + ' of ' + syms.length + '): funding…'; var f = []; try{ f = await funding(sym); }catch(eF){}
          out.markets.push(encode(sym, rows, f)); }catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
      if(stop) throw new Error('stopped');
      var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
      var blob, name = 'omega-history-older-' + new Date().toISOString().slice(0, 10);
      if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove();
      var bars = out.markets.reduce(function(s, m){ return s + m.n; }, 0), r = 'Saved ' + name + ' (' + Math.round(blob.size/1048576*10)/10 + ' MB): ' + out.markets.length + ' markets, ' + bars.toLocaleString() + ' hourly bars from 2019, funding for ' + out.markets.filter(function(m){ return m.fund; }).length + '. Attach it for research.';
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Older-history download ' + (stop ? 'stopped.' : 'stopped: ' + (e && e.message || e)); return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = 'Download older history (2019 – Oct 2023) for research'; } }
  function wire(){ var host = el('histExportBtn'); if(!host || el('longExportBtn')) return !!el('longExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '10px';
    wrap.innerHTML = '<button class="btn-outline" type="button" id="longExportBtn">Download older history (2019 – Oct 2023) for research</button> <span class="hint" id="longExportMsg">Downloads straight from Binance into one file (about 1,000 requests, a few minutes; nothing is stored on the phone). Keep the app open.</span>';
    host.parentNode.parentNode.appendChild(wrap); var b = el('longExportBtn'); if(b) b.addEventListener('click', function(){ run(); }); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 30) clearInterval(iv); }, 1000);
  window.OMEGA_LONGEXPORT = { run:run, encode:encode, FROM:FROM, TO:TO };
})();
</script>
