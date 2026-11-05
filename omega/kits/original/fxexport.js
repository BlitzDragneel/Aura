<script>/* ═══ FOREX HISTORY FOR RESEARCH (v6.5.65) — decades of daily forex and metals, plus central-bank policy rates ═══
   For round 11 (PLAN11: carry and trend in forex). Downloads daily candles from Twelve Data with the key already set in
   OMEGA (as far back as Twelve Data serves, up to 10,000 days a pair, about 22 requests), and the policy rates of the ten
   currencies' central banks from the BIS statistics service. Saves one file (format omega-forex). The key is used only
   in the requests and never written into the file; the file is checked for it before saving. Nothing is stored on the
   phone. */
(function(){
  'use strict';
  var PAIRS = ['EUR/USD','GBP/USD','USD/JPY','AUD/USD','NZD/USD','USD/CAD','USD/CHF','USD/NOK','USD/SEK','XAU/USD','XAG/USD'];
  var AREAS = ['US','XM','GB','JP','AU','NZ','CA','CH','NO','SE'], busy = false, stop = false;
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function tdKey(){ var k = el('creedKey'); if(k && k.value && k.value.trim()) return k.value.trim(); try{ var s = localStorage.getItem('omega_td_key'); if(s) return s; }catch(e){} var a = el('apikey'); return (a && a.value) ? a.value.trim() : ''; }
  var lastTd = 0;
  async function tdGate(){ if(window.OMEGA_TD && typeof window.OMEGA_TD.acquire === 'function'){ await window.OMEGA_TD.acquire('history'); return; }   // the app's shared queue (7 a minute, the day's allowance); throws when the day's allowance is used
    var w = lastTd + 8000 - Date.now(); if(w > 0) await sleep(w); lastTd = Date.now(); }
  function dayNum(s){ return Math.round(Date.parse(String(s).slice(0, 10) + 'T00:00:00Z')/86400e3); }
  async function series(sym, key, onMsg){ var rows = {}, end = null, pages = 0;
    while(pages < 2 && !stop){ await tdGate(); pages++;
      var url = 'https://api.twelvedata.com/time_series?symbol=' + encodeURIComponent(sym) + '&interval=1day&outputsize=5000&timezone=UTC' + (end ? '&end_date=' + end : '') + '&apikey=' + encodeURIComponent(key);
      var j = null; for(var a=0; a<3 && !j; a++){ try{ j = await (await fetch(url)).json(); }catch(e){ await sleep(3000); } }
      if(!j) throw new Error('no answer');
      if(j.status === 'error' || !Array.isArray(j.values)){ if(pages === 1) throw new Error(String(j.message || j.code || 'error').replace(/apikey=[^&\s]+/gi, 'apikey=…').slice(0, 120)); break; }
      var vals = j.values, first = null;
      vals.forEach(function(v){ var d = dayNum(v.datetime); if(!isFinite(d)) return; rows[d] = [+v.open, +v.high, +v.low, +v.close]; if(first == null || d < first) first = d; });
      if(onMsg) onMsg(sym + ': ' + Object.keys(rows).length + ' days');
      if(vals.length < 5000 || first == null) break;
      end = new Date((first - 1)*86400e3).toISOString().slice(0, 10); }
    var ds = Object.keys(rows).map(Number).sort(function(a, b){ return a - b; });
    return { sym:sym, n:ds.length, t:ds, o:ds.map(function(d){ return rows[d][0]; }), h:ds.map(function(d){ return rows[d][1]; }), l:ds.map(function(d){ return rows[d][2]; }), c:ds.map(function(d){ return rows[d][3]; }) }; }
  // ── policy rates: BIS statistics service (SDMX); CSV if offered, else XML ──
  function parseCSV(txt){ var lines = txt.split(/\r?\n/).filter(Boolean); if(lines.length < 2) return null; var hd = lines[0].split(',').map(function(x){ return x.replace(/"/g, '').trim(); });
    var ia = hd.indexOf('REF_AREA'), it = hd.indexOf('TIME_PERIOD'), iv = hd.indexOf('OBS_VALUE'); if(ia < 0 || it < 0 || iv < 0) return null; var out = {};
    lines.slice(1).forEach(function(l){ var c = l.split(',').map(function(x){ return x.replace(/"/g, '').trim(); }), v = parseFloat(c[iv]); if(!isFinite(v)) return; (out[c[ia]] = out[c[ia]] || {})[c[it]] = v; }); return out; }
  function parseXML(txt){ var out = {}, found = false;
    var reS = /<(?:\w+:)?Series\b([^>]*)>([\s\S]*?)<\/(?:\w+:)?Series>/g, m;
    while((m = reS.exec(txt))){ var attrs = m[1], body = m[2], area = (attrs.match(/REF_AREA="([^"]+)"/) || [])[1];
      if(!area){ var g = body.match(/id="REF_AREA"\s+value="([^"]+)"/); area = g && g[1]; } if(!area) continue;
      var reO = /<(?:\w+:)?Obs\b([^>]*?)\/?>([\s\S]*?)(?:<\/(?:\w+:)?Obs>|(?=<(?:\w+:)?Obs\b)|$)/g, o;
      while((o = reO.exec(body))){ var at = o[1] + ' ' + (o[2] || ''), tp = (at.match(/TIME_PERIOD="([^"]+)"/) || at.match(/ObsDimension[^>]*value="([^"]+)"/) || [])[1], val = (at.match(/OBS_VALUE="([^"]+)"/) || at.match(/ObsValue[^>]*value="([^"]+)"/) || [])[1];
        if(tp && val != null && isFinite(parseFloat(val))){ (out[area] = out[area] || {})[tp] = parseFloat(val); found = true; } } }
    return found ? out : null; }
  async function policyRates(onMsg){ var log = [], base = 'https://stats.bis.org/api/v1/data/WS_CBPOL/', key = AREAS.join('+');
    var tries = [ [base + 'D.' + key + '/all?startPeriod=1990-01-01&detail=dataonly&format=csv', null], [base + 'D.' + key + '/all?startPeriod=1990-01-01&detail=dataonly', 'application/vnd.sdmx.data+csv;version=1.0.0'],
      [base + 'D.' + key + '/all?startPeriod=1990-01-01&detail=dataonly', null], [base + 'M.' + key + '/all?startPeriod=1990-01&detail=dataonly&format=csv', null], [base + 'M.' + key + '/all?startPeriod=1990-01&detail=dataonly', null] ];
    for(var i=0; i<tries.length && !stop; i++){ var u = tries[i][0], acc = tries[i][1];
      try{ if(onMsg) onMsg('policy rates: try ' + (i + 1) + ' of ' + tries.length); var r = await fetch(u, acc ? { headers:{ Accept:acc } } : undefined); var txt = await r.text();
        var p = /^\s*</.test(txt) ? parseXML(txt) : parseCSV(txt); log.push((i + 1) + ': HTTP ' + r.status + ', ' + txt.length + ' chars, ' + (p ? Object.keys(p).length + ' areas' : 'not parsed'));
        if(r.ok && p && Object.keys(p).length >= 5){ var freq = /\/M\./.test(u) ? 'monthly' : 'daily', rates = {};
          Object.keys(p).forEach(function(area){ var ks = Object.keys(p[area]).sort(); rates[area] = { t:ks.map(function(k){ return k.length === 7 ? dayNum(k + '-01') : dayNum(k); }), v:ks.map(function(k){ return Math.round(p[area][k]*1e4)/1e4; }) }; });
          return { ok:true, freq:freq, source:'BIS central bank policy rates (WS_CBPOL), ' + freq, rates:rates, log:log }; } }
      catch(e){ log.push((i + 1) + ': ' + String(e && e.message || e).slice(0, 80)); } await sleep(500); }
    return { ok:false, log:log }; }
  async function run(){ if(busy){ stop = true; return 'stopping'; } busy = true; stop = false; var msg = el('fxExportMsg'), b = el('fxExportBtn'); if(b) b.textContent = 'Stop';
    try{ var key = tdKey(); var out = { format:'omega-forex', v:1, exportedAt:new Date().toISOString(), src:'Twelve Data daily candles (UTC days)', fx:{}, skipped:[] };
      if(!key) out.skipped.push('forex candles: no Twelve Data key set in OMEGA');
      for(var i=0; key && i<PAIRS.length && !stop; i++){ var sym = PAIRS[i];
        try{ var s = await series(sym, key, function(t){ if(msg) msg.textContent = (i + 1) + ' of ' + PAIRS.length + ': ' + t + '…'; }); if(s.n >= 250) out.fx[sym] = s; else out.skipped.push(sym + ': only ' + s.n + ' days'); }
        catch(e){ var em = String(e && e.message || e).replace(/apikey=[^&\s]+/gi, 'apikey=…'); if(/allowance/i.test(em)) throw new Error(em); out.skipped.push(sym + ': ' + em); } }
      if(stop) throw new Error('stopped');
      var pr = await policyRates(function(t){ if(msg) msg.textContent = t + '…'; }); out.ratesProbe = pr.log; if(pr.ok){ out.rates = pr.rates; out.ratesSource = pr.source; } else out.skipped.push('policy rates: the BIS service could not be read from this phone');
      var txt = JSON.stringify(out);
      if(key && txt.indexOf(key) > -1) throw new Error('refused: the file would contain the key');
      if((window.__omegaLeak && window.__omegaLeak(txt)) || /"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
      var blob, name = 'omega-forex-' + new Date().toISOString().slice(0, 10);
      if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove();
      var ks = Object.keys(out.fx), r = 'Saved ' + name + ': ' + ks.length + ' pairs' + (ks.length ? ' (' + ks.map(function(k){ return k + ' from ' + new Date(out.fx[k].t[0]*86400e3).toISOString().slice(0, 4); }).join(', ') + ')' : '') + '; policy rates ' + (out.rates ? 'for ' + Object.keys(out.rates).length + ' central banks' : 'not available') + '. Attach it for research.';
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Forex download stopped: ' + String(e && e.message || e); return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = 'Download forex history (daily) for research'; } }
  function wire(){ var host = el('futExportBtn'); if(!host || el('fxExportBtn')) return !!el('fxExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '10px';
    wrap.innerHTML = '<button class="btn-outline" type="button" id="fxExportBtn">Download forex history (daily) for research</button> <span class="hint" id="fxExportMsg">Nine currency pairs, gold and silver, daily, as far back as Twelve Data serves (uses your Twelve Data key, about 22 requests, 3–4 minutes), plus central-bank interest rates. The key is never written into the file.</span>';
    host.parentNode.parentNode.appendChild(wrap); var b = el('fxExportBtn'); if(b) b.addEventListener('click', function(){ run(); }); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_FXEXPORT = { run:run, PAIRS:PAIRS, parseCSV:parseCSV, parseXML:parseXML };
})();
</script>
