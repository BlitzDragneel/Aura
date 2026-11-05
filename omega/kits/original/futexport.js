<script>/* ═══ FUTURES DATA FOR RESEARCH, THE REST IN ONE RUN (v6.5.65; one file on its own, v6.5.66) — perpetual candles, premium and funding for the 141
   fresh and new research coins, plus open interest and long/short ratios for BTC and ETH (the 25 studied coins' file
   comes from v6.5.64's button) ═══
   Everything so far used spot prices plus funding. One tap downloads the rest of what round 10 (PLAN10) needs, straight
   from Binance:
   · for the 51 fresh coins and the 90 new coins: the perpetual contracts' own hourly candles
     (with futures taker-buy volume), the hourly premium index (perpetual vs index, the live input behind funding) and
     funding, Jan 2020 to now;
   · for BTC and ETH: Binance's daily metrics archive (open interest, top-trader and all-account long/short ratios,
     taker ratio), reduced to hourly.
   It saves 6 files, each as soon as its part is done (so nothing is lost if it stops), and pressing again continues
   from the first unsaved file. Nothing is stored on the phone except which files are already saved.
   v6.5.66: a phone can drop a download the app hands it (a 'several downloads' prompt, say) and the app cannot see
   that, so (1) each file can be downloaded again on its own, and (2) every file made in this visit stays behind a link
   to save it again by hand (a tap always saves). */
(function(){
  'use strict';
  var STUDIED = ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','AVAXUSDT','LINKUSDT','LTCUSDT','TRXUSDT','DOTUSDT','BCHUSDT',
    'NEARUSDT','ATOMUSDT','UNIUSDT','APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','FILUSDT','ICPUSDT','ETCUSDT','XLMUSDT','INJUSDT'];
  var FROM = Date.UTC(2020, 0, 1), FAPI = 'https://fapi.binance.com', ARCH = 'https://data.binance.vision/data/futures/um/daily/metrics/', PKEY = 'omega_futdl_v1', busy = false, stop = false, kept = [];
  var SHORT = { 'fresh-a':'Fresh coins 1', 'fresh-b':'Fresh coins 2', 'new-a':'New coins 1', 'new-b':'New coins 2', 'new-c':'New coins 3', 'metrics':'BTC/ETH positioning' };
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function lsGet(){ try{ var v = JSON.parse(localStorage.getItem(PKEY) || 'null'); return v && typeof v === 'object' ? v : { done:{} }; }catch(e){ return { done:{} }; } }
  function lsSet(v){ try{ localStorage.setItem(PKEY, JSON.stringify(v)); }catch(e){} }
  function groups(){ var F = (window.OMEGA_FRESHEXPORT && window.OMEGA_FRESHEXPORT.FRESH) || [], N = (window.OMEGA_FRESH2EXPORT && window.OMEGA_FRESH2EXPORT.FRESH) || [];
    return [ { id:'fresh-a', label:'fresh coins, part 1', coins:F.slice(0, 26) }, { id:'fresh-b', label:'fresh coins, part 2', coins:F.slice(26) },
      { id:'new-a', label:'new coins, part 1', coins:N.slice(0, 30) }, { id:'new-b', label:'new coins, part 2', coins:N.slice(30, 60) }, { id:'new-c', label:'new coins, part 3', coins:N.slice(60) },
      { id:'metrics', label:'BTC and ETH open interest and long/short ratios', coins:['BTCUSDT', 'ETHUSDT'], kind:'metrics' } ].filter(function(g){ return g.coins.length; }); }
  async function getJSON(url){ for(var a=0; a<5; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(15000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 4) throw e; await sleep(2000*(a+1)); } } return []; }
  async function paged(path, sym, to, onPage){ var rows = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON(FAPI + path + '?symbol=' + sym + '&interval=1h&limit=1500&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < to) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + 3600e3; if(onPage) onPage(rows.length); await sleep(320); }
    return rows; }
  async function funding(sym, to){ var out = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON(FAPI + '/fapi/v1/fundingRate?symbol=' + sym + '&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(x){ var ft = +x.fundingTime; if(ft >= t && ft < to) out.push([ft, +x.fundingRate]); }); var last = +d[d.length-1].fundingTime; if(!(last >= t) || d.length < 1000) break; t = last + 1; await sleep(200); }
    return out; }
  function encodePrem(rows){ var p = { t:[], c:[] }, pt = 0; rows.forEach(function(k, i){ var th = Math.round(+k[0]/3600e3); p.t.push(i ? th - pt : th); pt = th; p.c.push(Math.round(+k[4]*1e7)); }); return p; }
  // ── the metrics archive (one zip a day, a CSV of 5-minute rows) ──
  async function unzipFirst(buf){ var dv = new DataView(buf.buffer); if(dv.getUint32(0, true) !== 0x04034b50) throw new Error('not a zip');
    var method = dv.getUint16(8, true), csize = dv.getUint32(18, true), nlen = dv.getUint16(26, true), xlen = dv.getUint16(28, true), start = 30 + nlen + xlen;
    if(method === 0) return new TextDecoder().decode(buf.slice(start, start + csize));
    if(method !== 8 || typeof DecompressionStream === 'undefined') throw new Error('cannot unzip here');
    return await new Response(new Blob([buf.slice(start, start + csize)]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).text(); }
  async function dayFile(sym, d){ var ds = new Date(d).toISOString().slice(0, 10); try{ var r = await fetch(ARCH + sym + '/' + sym + '-metrics-' + ds + '.zip'); if(!r.ok) return null; return await unzipFirst(new Uint8Array(await r.arrayBuffer())); }catch(e){ return null; } }
  function sig4(v){ if(!(v > 0)) return 0; var p = Math.pow(10, Math.max(0, 3 - Math.floor(Math.log10(v)))); return Math.round(v*p)/p; }
  async function metricsFor(sym, onMsg){ var now = Date.now(), first = null;
    for(var y=2020; y<=new Date(now).getUTCFullYear() && first == null && !stop; y++) for(var m=0; m<12 && first == null && !stop; m++){ var d = Date.UTC(y, m, 1); if(d > now) break; if(onMsg) onMsg(sym + ': looking for the archive’s start (' + new Date(d).toISOString().slice(0, 7) + ')'); if(await dayFile(sym, d)) first = Date.UTC(y, m - 1, 1); await sleep(60); }
    if(first == null) return null;
    var H = {}, end = Math.floor(now/86400e3)*86400e3 - 86400e3, got = 0, miss = 0;
    for(var day=first; day<=end && !stop; day+=86400e3){ var txt = await dayFile(sym, day); if(!txt){ miss++; await sleep(40); continue; } got++;
      txt.split(/\r?\n/).forEach(function(line){ if(!line || /create_time/i.test(line)) return; var c = line.split(','); if(c.length < 8) return;
        var ts = /^\d+$/.test(c[0]) ? +c[0] : Date.parse(c[0].replace(' ', 'T') + 'Z'); if(!isFinite(ts)) return; var h = Math.floor(ts/3600e3), x = H[h] || (H[h] = { tk:0, tn:0 });
        x.oi = +c[2]; x.oiv = +c[3]; x.ttA = +c[4]; x.ttP = +c[5]; x.lsA = +c[6]; if(isFinite(+c[7]) && c[7] !== ''){ x.tk += +c[7]; x.tn++; } });
      if(onMsg && got % 10 === 0) onMsg(sym + ': ' + got + ' days of open interest… (' + new Date(day).toISOString().slice(0, 10) + ')'); await sleep(60); }
    var hs = Object.keys(H).map(Number).sort(function(a, b){ return a - b; }), o = { sym:sym, src:'Binance futures metrics archive (5-minute, last value of each hour; taker ratio averaged)', days:got, missingDays:miss, n:hs.length, t:[], oi:[], oiv:[], ttA:[], ttP:[], lsA:[], tk:[] }, pt = 0;
    function q(v){ return isFinite(v) && v > 0 ? Math.round(v*1e4) : -1; }
    hs.forEach(function(h, i){ var x = H[h]; o.t.push(i ? h - pt : h); pt = h; o.oi.push(sig4(x.oi)); o.oiv.push(sig4(x.oiv)); o.ttA.push(q(x.ttA)); o.ttP.push(q(x.ttP)); o.lsA.push(q(x.lsA)); o.tk.push(x.tn ? q(x.tk/x.tn) : -1); });
    return o; }
  async function save(out, name){ var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
    var blob; if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    var mb = Math.round(blob.size/1048576*10)/10; kept = kept.filter(function(k){ return k.name !== name; }); kept.push({ name:name, url:url, mb:mb }); showKept(); return { name:name, mb:mb }; }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function showKept(){ var k = el('futSaveAgain'); if(!k) return; if(!kept.length){ k.innerHTML = ''; return; }
    k.innerHTML = 'Not in your Downloads? Tap a name to save it again: ' + kept.map(function(x){ return '<a href="' + x.url + '" download="' + esc(x.name) + '">' + esc(x.name) + '</a> (' + x.mb + ' MB)'; }).join(' · '); }
  function oneButtons(){ var row = el('futOneRow'); if(!row) return; var P = lsGet();
    groups().forEach(function(g){ var bt = row.querySelector('[data-g="' + g.id + '"]'); if(!bt) return; bt.textContent = (P.done[g.id] ? '✓ ' : '') + (SHORT[g.id] || g.id); bt.disabled = busy; bt.title = g.label + (P.done[g.id] ? ' (handed to your phone before)' : ''); }); }
  function label(){ var G = groups(), P = lsGet(), n = G.filter(function(g){ return P.done[g.id]; }).length; return n === G.length ? 'Download all ' + G.length + ' futures files again' : n ? 'Continue the futures download (' + n + ' of ' + G.length + ' files saved)' : 'Download the rest of the futures data (' + G.length + ' files)'; }
  async function run(onlyId){ if(busy){ stop = true; return 'stopping'; } var G = groups(); if(onlyId && !G.some(function(g){ return g.id === onlyId; })) return 'no such file';
    busy = true; stop = false; var msg = el('futExportMsg'), b = el('futExportBtn'); if(b) b.textContent = 'Stop'; oneButtons();
    var P = lsGet(); if(!onlyId && G.every(function(g){ return P.done[g.id]; })) P = { done:{} };   // all saved before: start over (one file on its own never resets the others)
    var said = [];
    try{ var L = window.OMEGA_LONGEXPORT; if(!L || !L.encode) throw new Error('older-history module missing');
      for(var gi=0; gi<G.length && !stop; gi++){ var g = G[gi]; if(onlyId ? g.id !== onlyId : P.done[g.id]) continue;
        var to = Math.floor(Date.now()/3600e3)*3600e3, head = 'File ' + (gi + 1) + ' of ' + G.length + ' (' + g.label + '): ';
        var out = { format:'omega-history', v:2, part:'futures-' + g.id, src:g.kind === 'metrics' ? 'Binance futures metrics archive' : 'Binance USD-M perpetuals', from:new Date(FROM).toISOString(), to:new Date(to).toISOString(), exportedAt:new Date().toISOString(), tf:60, markets:[], skipped:[] };
        for(var k=0; k<g.coins.length && !stop; k++){ var sym = g.coins[k], tag = head + sym + ' (' + (k + 1) + ' of ' + g.coins.length + '): ';
          try{
            if(g.kind === 'metrics'){ var mt = await metricsFor(sym, function(t){ if(msg) msg.textContent = head + t; }); if(mt) out.markets.push(mt); else out.skipped.push(sym + ': metrics archive not readable from this phone'); continue; }
            var rows = await paged('/fapi/v1/klines', sym, to, function(n){ if(msg) msg.textContent = tag + n.toLocaleString() + ' perpetual hours…'; });
            if(rows.length < 24*30){ out.skipped.push(sym + ': under a month of perpetual candles'); continue; }
            var prem = await paged('/fapi/v1/premiumIndexKlines', sym, to, function(n){ if(msg) msg.textContent = tag + n.toLocaleString() + ' premium hours…'; });
            if(msg) msg.textContent = tag + 'funding…'; var f = []; try{ f = await funding(sym, to); }catch(eF){}
            var m = L.encode(sym, rows, f); m.src = 'Binance USD-M perpetual'; if(prem.length) m.prem = encodePrem(prem); out.markets.push(m); }
          catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
        if(stop) break;
        if(msg) msg.textContent = head + 'saving…';
        var sv = await save(out, 'omega-history-futures-' + g.id + '-' + new Date().toISOString().slice(0, 10)); P.done[g.id] = sv.name; lsSet(P); said.push(sv.name + ' (' + sv.mb + ' MB)'); if(b) b.textContent = 'Stop'; await sleep(1500); }
      var n = G.filter(function(g){ return P.done[g.id]; }).length, r = onlyId ? (stop ? 'Stopped. ' : '') + (said.length ? 'Saved now: ' + said.join(', ') + '. Attach it for research. If it is not in your Downloads, tap its name below.' : 'Nothing saved.')
        : (stop ? 'Stopped. ' : '') + n + ' of ' + G.length + ' files saved.' + (said.length ? ' Saved now: ' + said.join(', ') + '.' : '') + ' ' + (n === G.length ? 'All done — attach all ' + G.length + ' files for research.' : 'Press again to continue from the next file.');
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Futures download stopped: ' + (e && e.message || e) + '. Press again to continue.'; return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = label(); oneButtons(); } }
  function wire(){ var host = el('fresh2ExportBtn') || el('freshExportBtn'); if(!host || el('futExportBtn')) return !!el('futExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '10px';
    wrap.innerHTML = '<button class="btn-outline" type="button" id="futExportBtn">' + label() + '</button> <span class="hint" id="futExportMsg">Perpetual candles, premium and funding for the other 141 research coins, plus BTC and ETH open interest and long/short ratios: 6 files, each saved as soon as it is done (about 75 minutes in all; if your phone asks to allow several downloads, allow it). Keep the app open and the screen on; if it stops, press again to continue.</span>';
    var one = document.createElement('div'); one.id = 'futOneRow'; one.style.cssText = 'margin-top:6px; display:flex; flex-wrap:wrap; gap:6px; align-items:center';
    one.innerHTML = '<span class="hint">One file on its own:</span>' + groups().map(function(g){ return '<button class="btn-outline" type="button" style="padding:5px 9px" data-g="' + g.id + '">' + esc(SHORT[g.id] || g.id) + '</button>'; }).join('') +
      '<span class="hint" style="flex-basis:100%">✓ means the app handed that file to your phone. If one is missing from your Downloads, tap it to download just that file.</span><span class="hint" id="futSaveAgain" style="flex-basis:100%; word-break:break-all"></span>';
    wrap.appendChild(one); host.parentNode.parentNode.appendChild(wrap); var b = el('futExportBtn'); if(b) b.addEventListener('click', function(){ run(); });
    Array.prototype.forEach.call(one.querySelectorAll('[data-g]'), function(bt){ bt.addEventListener('click', function(){ run(bt.getAttribute('data-g')); }); }); oneButtons(); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 50) clearInterval(iv); }, 1000);
  window.OMEGA_FUTEXPORT = { run:run, groups:groups, metricsFor:metricsFor, progress:lsGet, kept:function(){ return kept.map(function(k){ return { name:k.name, mb:k.mb }; }); } };
})();
</script>
