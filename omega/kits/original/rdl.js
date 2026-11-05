<script>/* ═══ RESEARCH FILES (v6.5.88) — the daily history of the 25 studied coins, as one file for the next clean test ═══
   The 15-minute export of BTC, ETH, SOL, BNB and XRP was removed in an earlier build, and plan E10 (the market-level
   capitulation bounce) needs only their daily closes. The app's wide data store (OMEGA_WIDE) already keeps daily bars from
   Jan 2020 for the 25 studied coins (Binance spot: close, high, low, volume, taker-buy volume; and USDT-M funding by day).
   This card saves those 25 coins as one research file (omega-history, tf 1440, the same encoding as the other files; the
   store keeps no daily open, so opens equal closes in the file), and can fetch any of them the store does not have yet.
   Prices and funding only; checked for credential-like fields before saving. OMEGA places no orders. */
(function(){
  'use strict';
  var COINS = ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'].map(function(s){ return s + 'USDT'; });
  var NEED = ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT'], DAY = 86400e3, state = { busy:false, msg:'', have:null, saved:null };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function dpOf(px){ var d = 2; if(px < 1000) d = 3; if(px < 100) d = 4; if(px < 10) d = 5; if(px < 1) d = 6; if(px < 0.1) d = 7; if(px < 0.01) d = 8; return d; }
  function sig4(v){ if(!(v > 0)) return 0; var p = Math.pow(10, Math.max(0, 3 - Math.floor(Math.log10(v)))); return Math.round(v*p)/p; }
  function day(k){ return new Date(k*DAY).toISOString().slice(0, 10); }
  async function recs(){ var W = window.OMEGA_WIDE; if(!W) throw new Error('the wide data store is not loaded'); var all = await W.all(), by = {}; (all || []).forEach(function(r){ if(r && r.sym) by[r.sym] = r; }); return by; }
  function encode(r){ var idx = []; for(var i=0; i<r.c.length; i++) if(r.c[i] != null && r.c[i] > 0) idx.push(i); if(idx.length < 30) return null;
    var med = r.c[idx[Math.floor(idx.length/2)]], dp = dpOf(med), sc = Math.pow(10, dp), m = { sym:r.sym, src:'Binance spot daily (OMEGA wide store)', dp:dp, n:idx.length, t:[], c:[], o:[], h:[], l:[], v:[], tb:[], fs:[], fc:[] }, pt = 0, pc = 0;
    idx.forEach(function(i, q){ var th = (r.k0 + i)*24, ci = Math.round(r.c[i]*sc), hi = Math.round(Math.max(r.h[i] != null ? r.h[i] : r.c[i], r.c[i])*sc), li = Math.round(Math.min(r.l[i] != null ? r.l[i] : r.c[i], r.c[i])*sc);
      m.t.push(q ? th - pt : th); pt = th; m.c.push(q ? ci - pc : ci); pc = ci; m.o.push(0); m.h.push(Math.max(0, hi - ci)); m.l.push(Math.max(0, ci - li)); m.v.push(sig4(+r.v[i] || 0));
      var tb = (r.v[i] > 0 && r.tb[i] != null) ? Math.round(1000*r.tb[i]/r.v[i]) : -1; m.tb.push(tb); m.fs.push(Math.round(((r.ff && r.ff[i]) || 0)*1e7)); m.fc.push((r.fc && r.fc[i]) || 0); });
    return m; }
  async function build(){ var by = await recs(), out = { format:'omega-history', v:2, tf:1440, tunit:3600, exportedAt:new Date().toISOString(), src:'OMEGA v6.5.88 research file: daily bars of the 25 studied coins (plan E10 uses BTC, ETH, SOL, BNB, XRP); no daily opens (opens = closes); fs = daily funding sum ×1e7, fc = payments that day', markets:[], checks:{}, skipped:[] };
    COINS.forEach(function(s){ var r = by[s]; if(!r || r.k0 == null){ out.skipped.push(s + ': not in the store yet'); return; } var m = encode(r); if(!m){ out.skipped.push(s + ': under 30 days'); return; }
      out.markets.push(m); var t = 0; m.t.forEach(function(x){ t += x; }); out.checks[s] = { days:m.n, from:day(m.t[0]/24), to:day(t/24) }; });
    return out; }
  async function status(){ try{ var by = await recs(); state.have = COINS.filter(function(s){ return by[s] && by[s].k0 != null; }).map(function(s){ var r = by[s], last = null; for(var i=r.c.length-1; i>=0; i--) if(r.c[i] != null){ last = r.k0 + i; break; } return { sym:s, from:day(r.k0), to:last != null ? day(last) : '—' }; }); }catch(e){ state.have = null; state.msg = String(e.message || e); } render(); }
  async function fetchMissing(){ var W = window.OMEGA_WIDE; if(!W || state.busy) return; state.busy = true; state.msg = 'Fetching daily history (the 25 studied coins come first; a few minutes)…'; render();
    try{ var r = await W.runNow(6*60e3, function(t){ state.msg = t + '…'; render(); }); state.msg = (r && r.text) || 'Fetched.'; }catch(e){ state.msg = 'Stopped: ' + (e.message || e); }
    state.busy = false; await status(); }
  async function save(){ var out = await build(); if(!out.markets.length) throw new Error('no coins stored yet — press Fetch first');
    var miss = NEED.filter(function(s){ return !out.checks[s]; }); var txt = JSON.stringify(out);
    if(/"(apiKey|api_key|apikey|token|secret|password|phone|whatsapp)"\s*:/i.test(txt) || (window.__omegaLeak && window.__omegaLeak(txt))) throw new Error('refused: credential-like field');
    var name = 'omega-history-daily25-' + new Date().toISOString().slice(0, 10), blob;
    if(typeof CompressionStream !== 'undefined'){ var cs = new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip')); blob = await new Response(cs).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(url); a.remove(); }, 4000);
    state.saved = { name:name, kb:Math.round(blob.size/1024), coins:out.markets.length, miss:miss }; render(); return state.saved; }
  function html(){ var H = state.have, got = H ? H.length : 0, need = H ? NEED.filter(function(s){ return !H.some(function(x){ return x.sym === s; }); }) : NEED;
    return '<div class="card" style="margin-top:14px;"><h2 style="color:var(--gold);">Research files to send (plan E10)</h2>' +
      '<p class="hint" style="margin:0 0 8px;color:var(--text);">The next clean test, the market-level capitulation bounce, needs the daily history of <b>BTC, ETH, SOL, BNB and XRP</b> from 2020. The app already keeps it. Save it as one file and send it in the research chat.</p>' +
      '<p class="hint" style="margin:0 0 8px;">' + (H ? got + ' of 25 studied coins stored' + (got ? ' (BTC from ' + ((H.filter(function(x){ return x.sym === 'BTCUSDT'; })[0] || {}).from || '—') + ')' : '') + '. ' + (need.length ? 'Missing for plan E10: ' + need.map(function(s){ return s.replace('USDT', ''); }).join(', ') + ' — press Fetch first.' : 'All five needed coins are stored.') : 'Checking what is stored…') + '</p>' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;"><button class="btn-outline" type="button" data-rdl="fetch"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Fetching…' : 'Fetch missing coins') + '</button>' +
      '<button class="btn-outline" type="button" data-rdl="save"' + (state.busy || !got ? ' disabled' : '') + '>Save daily history (25 coins)</button></div>' +
      (state.msg ? '<p class="hint" style="margin:8px 0 0;">' + esc(state.msg) + '</p>' : '') +
      (state.saved ? '<p class="hint" style="margin:6px 0 0;">Saved <b>' + esc(state.saved.name) + '</b> (' + state.saved.kb + ' KB, ' + state.saved.coins + ' coins)' + (state.saved.miss.length ? '; still missing ' + state.saved.miss.join(', ') : '') + '. It is in your Downloads folder: attach it in the research chat.</p>' : '') + '</div>'; }
  function render(){ var host = el('rdlBody'); if(!host) return; host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-rdl]'), function(b){ var k = b.getAttribute('data-rdl');
      if(k === 'fetch') b.onclick = function(){ fetchMissing(); };
      if(k === 'save') b.onclick = function(){ save().catch(function(e){ state.msg = 'Not saved: ' + (e.message || e); render(); }); }; }); }
  var tries = 0, iv = setInterval(function(){ if(el('rdlBody')){ clearInterval(iv); status(); } else if(++tries > 60) clearInterval(iv); }, 1000);
  window.OMEGA_RDL = { build:build, save:save, status:status, fetchMissing:fetchMissing, render:render, state:function(){ return state; }, COINS:COINS, _:{ encode:encode } };
})();
</script>
