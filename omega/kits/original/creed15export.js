<script>/* ═══ CREED RESEARCH DATA (v6.5.71) — 15-minute candles for the 25 studied coins, Jan 2020 to now ═══
   CREED decides on 15-minute candles. Its replays covered Oct 2023 – Oct 2026 and showed that setups taken when CREED
   shows them have no edge (+0.015R a trade before costs over 2,497 setups). Testing a better trigger needs 15-minute
   data the replays never saw: Jan 2020 – Sep 2023 is untouched for CREED questions and becomes the final test
   (PLAN14 addendum A). Five files of five coins, Binance spot 15-minute candles with taker-buy volume, each saved as
   soon as it is done. Prices only. */
(function(){
  'use strict';
  var COINS = ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'].map(function(s){ return s + 'USDT'; });
  var FROM = Date.UTC(2020, 0, 1), API = 'https://data-api.binance.vision/api/v3/klines', PKEY = 'omega_creed15dl_v1', busy = false, stop = false, kept = [];
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function lsGet(){ try{ var v = JSON.parse(localStorage.getItem(PKEY) || 'null'); return v && typeof v === 'object' && v.done ? v : { done:{} }; }catch(e){ return { done:{} }; } }
  function lsSet(v){ try{ localStorage.setItem(PKEY, JSON.stringify(v)); }catch(e){} }
  function groups(){ var g = []; for(var i=0; i<COINS.length; i += 5) g.push({ id:'c15-' + (i/5 + 1), label:'coins ' + (i + 1) + '–' + Math.min(COINS.length, i + 5) + ' (' + COINS.slice(i, i + 5).map(function(s){ return s.replace(/USDT$/, ''); }).join(', ') + ')', coins:COINS.slice(i, i + 5) }); return g; }
  function dpOf(px){ var d = 2; if(px < 1000) d = 3; if(px < 100) d = 4; if(px < 10) d = 5; if(px < 1) d = 6; if(px < 0.1) d = 7; if(px < 0.01) d = 8; return d; }
  function sig4(v){ if(!(v > 0)) return 0; var p = Math.pow(10, Math.max(0, 3 - Math.floor(Math.log10(v)))); return Math.round(v*p)/p; }
  // like the hourly files, but times count quarter-hours (tunit 900 s)
  function encode15(sym, rows){ var lo = Infinity; rows.forEach(function(k){ var c = +k[4]; if(c > 0 && c < lo) lo = c; });
    var dp = dpOf(lo), sc = Math.pow(10, dp), m = { sym:sym, src:'Binance spot (downloaded for research)', dp:dp, n:rows.length, t:[], c:[], o:[], h:[], l:[], v:[], tb:[] }, pt = 0, pc = 0;
    rows.forEach(function(k, i){ var tq = Math.round(+k[0]/900e3), ci = Math.round(+k[4]*sc), oi = Math.round(+k[1]*sc), v = +k[5], tb = +k[9];
      m.t.push(i ? tq - pt : tq); pt = tq; m.c.push(i ? ci - pc : ci); pc = ci; m.o.push(oi - ci); m.h.push(Math.round(+k[2]*sc) - Math.max(ci, oi)); m.l.push(Math.min(ci, oi) - Math.round(+k[3]*sc));
      m.v.push(sig4(v)); m.tb.push(v > 0 && isFinite(tb) ? Math.round(1000*tb/v) : -1); });
    return m; }
  async function getJSON(url){ for(var a=0; a<5; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(10000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 4) throw e; await sleep(1500*(a+1)); } } return []; }
  async function klines(sym, to, onPage){ var rows = [], t = FROM;
    while(t < to && !stop){ var d = await getJSON(API + '?symbol=' + sym + '&interval=15m&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < to) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + 900e3; if(onPage && rows.length % 20000 < 1000) onPage(rows.length); await sleep(110); }
    return rows; }
  async function save(out, name){ var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
    var blob; if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    var mb = Math.round(blob.size/1048576*10)/10; kept = kept.filter(function(k){ return k.name !== name; }); kept.push({ name:name, url:url, mb:mb }); showKept(); return { name:name, mb:mb }; }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function showKept(){ var k = el('c15SaveAgain'); if(!k) return; if(!kept.length){ k.innerHTML = ''; return; }
    k.innerHTML = 'Not in your Downloads? Tap a name to save it again: ' + kept.map(function(x){ return '<a href="' + x.url + '" download="' + esc(x.name) + '">' + esc(x.name) + '</a> (' + x.mb + ' MB)'; }).join(' · '); }
  function oneButtons(){ var row = el('c15OneRow'); if(!row) return; var P = lsGet();
    groups().forEach(function(g){ var bt = row.querySelector('[data-g="' + g.id + '"]'); if(!bt) return; bt.textContent = (P.done[g.id] ? '✓ ' : '') + 'Part ' + g.id.slice(4); bt.title = g.label; bt.disabled = busy; }); }
  function label(){ var G = groups(), P = lsGet(), n = G.filter(function(g){ return P.done[g.id]; }).length; return n === G.length ? 'Download the 15-minute CREED data again' : n ? 'Continue the 15-minute CREED data (' + n + ' of ' + G.length + ' files saved)' : 'Download 15-minute data for CREED research (' + G.length + ' files)'; }
  async function run(onlyId){ if(busy){ stop = true; return 'stopping'; } var G = groups(); if(onlyId && !G.some(function(g){ return g.id === onlyId; })) return 'no such file';
    busy = true; stop = false; var msg = el('c15ExportMsg'), b = el('c15ExportBtn'); if(b) b.textContent = 'Stop'; oneButtons();
    var P = lsGet(); if(!onlyId && G.every(function(g){ return P.done[g.id]; })) P = { done:{} };
    var said = [];
    try{ for(var gi=0; gi<G.length && !stop; gi++){ var g = G[gi]; if(onlyId ? g.id !== onlyId : P.done[g.id]) continue;
        var to = Math.floor(Date.now()/900e3)*900e3, head = 'File ' + (gi + 1) + ' of ' + G.length + ' (' + g.label + '): ';
        var out = { format:'omega-history', v:2, part:'creed15-' + g.id.slice(4), plan:'PLAN14 addendum A', tf:15, tunit:900, from:new Date(FROM).toISOString(), to:new Date(to).toISOString(), exportedAt:new Date().toISOString(), markets:[], skipped:[] };
        for(var k=0; k<g.coins.length && !stop; k++){ var sym = g.coins[k], tag = head + sym + ': ';
          try{ var rows = await klines(sym, to, function(n){ if(msg) msg.textContent = tag + n.toLocaleString() + ' fifteen-minute candles…'; });
            if(rows.length < 96*30){ out.skipped.push(sym + ': under a month of candles'); continue; } out.markets.push(encode15(sym, rows)); }
          catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
        if(stop) break;
        if(msg) msg.textContent = head + 'saving…';
        var sv = await save(out, 'omega-history-creed15-' + g.id.slice(4) + '-' + new Date().toISOString().slice(0, 10)); P.done[g.id] = sv.name; lsSet(P); said.push(sv.name + ' (' + sv.mb + ' MB)'); await sleep(1500); }
      var n = G.filter(function(g){ return P.done[g.id]; }).length, r = (stop ? 'Stopped. ' : '') + (onlyId ? (said.length ? 'Saved now: ' + said.join(', ') + '. Attach it for research.' : 'Nothing saved.')
        : n + ' of ' + G.length + ' files saved.' + (said.length ? ' Saved now: ' + said.join(', ') + '.' : '') + ' ' + (n === G.length ? 'All done — attach all ' + G.length + ' files for research.' : 'Press again to continue from the next file.'));
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = '15-minute download stopped: ' + (e && e.message || e) + '. Press again to continue.'; return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = label(); oneButtons(); } }
  function wire(){ var host = el('f4ExportBtn'); if(!host || el('c15ExportBtn')) return !!el('c15ExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '14px';
    wrap.innerHTML = '<p class="hint" style="margin:0 0 6px;color:var(--text);"><b>CREED research data.</b> 15-minute candles for the 25 studied coins, Jan 2020 to now: CREED’s replays never saw 2020–2023, so those years are a clean test for a better CREED trigger. 5 files, about 25 minutes in all.</p>' +
      '<button class="btn-outline" type="button" id="c15ExportBtn">' + label() + '</button> <span class="hint" id="c15ExportMsg"></span>';
    var one = document.createElement('div'); one.id = 'c15OneRow'; one.style.cssText = 'margin-top:6px; display:flex; flex-wrap:wrap; gap:6px; align-items:center';
    one.innerHTML = '<span class="hint">One file on its own:</span>' + groups().map(function(g){ return '<button class="btn-outline" type="button" style="padding:5px 9px" data-g="' + g.id + '">Part ' + g.id.slice(4) + '</button>'; }).join('') +
      '<span class="hint" id="c15SaveAgain" style="flex-basis:100%; word-break:break-all"></span>';
    wrap.appendChild(one); host.parentNode.parentNode.appendChild(wrap); var b = el('c15ExportBtn'); if(b) b.addEventListener('click', function(){ run(); });
    Array.prototype.forEach.call(one.querySelectorAll('[data-g]'), function(bt){ bt.addEventListener('click', function(){ run(bt.getAttribute('data-g')); }); }); oneButtons(); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 80) clearInterval(iv); }, 1000);
  window.OMEGA_CREED15EXPORT = { run:run, groups:groups, encode15:encode15, progress:lsGet, kept:function(){ return kept.map(function(k){ return { name:k.name, mb:k.mb }; }); } };
})();
</script>
