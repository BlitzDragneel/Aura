<script>/* ═══ RESEARCH DATA EXPORT (v6.5.50) — the stored price history as one compact file, for research off the phone ═══
   Hourly bars of every stored market (open, high, low, close, volume, taker-buy volume), built from the same stored
   1-minute / 15-minute history the Research Lab reads, gzip-compressed. Prices only: no keys, no journal, no settings.
   Format (omega-history v2; v1 had no funding): per market, times as hours since 1970 (first value absolute, then differences), prices as
   integers in units of 10^-dp (close: first absolute, then differences; open/high/low as distances from the close),
   volume to 4 significant figures, taker-buy share in thousandths; v2 adds funding (minutes since 1970 as differences, rate
   in units of 1e-7) and the open interest collected (value, 4 significant figures). */
(function(){
  'use strict';
  function el(id){ return document.getElementById(id); }
  function safe(f){ try{ return f(); }catch(e){ return null; } }
  function Y(){ return window.OMEGA_CALM && window.OMEGA_CALM.y ? window.OMEGA_CALM.y() : new Promise(function(r){ setTimeout(r, 0); }); }
  var busy = false;
  function dpOf(px){ var d = 2; if(px < 1000) d = 3; if(px < 100) d = 4; if(px < 10) d = 5; if(px < 1) d = 6; if(px < 0.1) d = 7; if(px < 0.01) d = 8; return d; }
  function sig4(v){ if(!(v > 0)) return 0; var p = Math.pow(10, Math.max(0, 3 - Math.floor(Math.log10(v)))); return Math.round(v*p)/p; }
  async function build(onProgress){ var H = window.OMEGA_HISTORY; if(!H) throw new Error('history store not ready');
    var syms = Object.keys(safe(function(){ return H.index(); }) || {}), out = { format:'omega-history', v:2, exportedAt:new Date().toISOString(), build: safe(function(){ return window.OMEGA_VERSION && window.OMEGA_VERSION.build; }) || null, tf:60, markets:[], skipped:[] };
    for(var k=0;k<syms.length;k++){ var sym = syms[k]; if(onProgress) onProgress(sym, k, syms.length); await Y();
      try{ var s = await H.load(sym, { stitch:true }), sm = H.summary(sym) || {}; if(!s || !s.n){ out.skipped.push(sym + ': no stored bars'); continue; }
        var rows = (await H.resampleA(s, 60)).filter(function(r){ return !r.partial; }); if(rows.length < 24){ out.skipped.push(sym + ': under a day of hourly bars'); continue; }
        var med = rows[Math.floor(rows.length/2)].c, dp = dpOf(med), sc = Math.pow(10, dp), m = { sym:sym, src:sm.src || '', dp:dp, n:rows.length, t:[], c:[], o:[], h:[], l:[], v:[], tb:[] }, pt = 0, pc = 0;
        for(var i=0;i<rows.length;i++){ var r = rows[i], th = Math.round(r.time/3600), ci = Math.round(r.c*sc);
          m.t.push(i ? th - pt : th); pt = th; m.c.push(i ? ci - pc : ci); pc = ci;
          m.o.push(Math.round(r.o*sc) - ci); m.h.push(Math.round(r.h*sc) - Math.max(ci, Math.round(r.o*sc))); m.l.push(Math.min(ci, Math.round(r.o*sc)) - Math.round(r.l*sc));
          m.v.push(sig4(r.v)); m.tb.push(r.v > 0 && isFinite(r.tb) ? Math.round(1000*r.tb/r.v) : -1);
          if((i & 4095) === 0) await Y(); }
        // v2: funding history (perpetuals, every 8 h, as the app stores it) and the open interest it has collected
        if(window.OMEGA_DERIV && /USDT$/.test(sym)){ try{ var dv = await window.OMEGA_DERIV.load(sym);
          if(dv && dv.fund && dv.fund.length){ var pf = 0; m.fund = { t:[], r:[] }; dv.fund.forEach(function(x, q){ var tm = Math.round(x[0]/60000); m.fund.t.push(q ? tm - pf : tm); pf = tm; m.fund.r.push(Math.round(x[1]*1e7)); }); }
          if(dv && dv.oi && dv.oi.length){ var po = 0; m.oi = { t:[], v:[] }; dv.oi.forEach(function(x, q){ var tm = Math.round(x[0]/60000); m.oi.t.push(q ? tm - po : tm); po = tm; m.oi.v.push(sig4(x[2] || x[1])); }); } }catch(eD){} }
        out.markets.push(m); }catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
    return out; }
  async function exportHistory(){ if(busy) return 'already running'; busy = true; var msg = el('histExportMsg');
    try{ var data = await build(function(sym, k, n){ if(msg) msg.textContent = 'Reading ' + sym + ' (' + (k + 1) + ' of ' + n + ')…'; }), txt = JSON.stringify(data), blob, name = 'omega-history-' + new Date().toISOString().slice(0, 10);
      if(!data.markets.length){ var r0 = 'Nothing to export: this copy of OMEGA has no stored price history yet' + (data.skipped.length ? ' (' + data.skipped.length + ' market(s) with too little)' : '') + '. If it opened as a new copy (see the notice on Command), your history is in the copy you used before: open this build under that copy\u2019s file name, or let the Autopilot download the history here first.'; if(msg) msg.textContent = r0; return r0; }
      if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt) || (window.__omegaLeak && window.__omegaLeak(txt))) throw new Error('refused: the file would contain a credential-like field');
      if(typeof CompressionStream !== 'undefined'){ var cs = new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip')); blob = await new Response(cs).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove();
      var bars = data.markets.reduce(function(s, m){ return s + m.n; }, 0), r = 'Saved ' + name + ' (' + Math.round(blob.size/1024/1024*10)/10 + ' MB): ' + data.markets.length + ' markets, ' + bars.toLocaleString() + ' hourly bars, funding for ' + data.markets.filter(function(m){ return m.fund; }).length + ' markets' + (data.skipped.length ? '; skipped ' + data.skipped.length : '') + '. Prices only — attach it for research.';
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Export stopped: ' + (e && e.message || e); throw e; } finally { busy = false; } }
  function wire(){ var b0 = el('ostratExport'); if(!b0 || el('histExportBtn')) return !!b0;
    var wrap = document.createElement('div'); wrap.style.marginTop = '10px';
    wrap.innerHTML = '<button class="btn-outline" type="button" id="histExportBtn">Export price history for research</button> <span class="hint" id="histExportMsg">Hourly bars of every stored market, compressed (prices only). Takes a minute or two.</span>';
    b0.parentNode.appendChild(wrap); var b = el('histExportBtn'); if(b) b.addEventListener('click', function(){ exportHistory().catch(function(){}); }); return true; }
  if(!wire()) { var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 20) clearInterval(iv); }, 1000); }
  window.OMEGA_HISTEXPORT = { build:build, exportHistory:exportHistory };
})();
</script>
