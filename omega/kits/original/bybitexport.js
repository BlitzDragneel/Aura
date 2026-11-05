<script>/* ═══ BYBIT FUNDING FOR RESEARCH (v6.5.75) — round 15: the harvest on the better-paying venue ═══
   PLAN15: the funding harvest has passed on untouched data four times, but Binance funding has thinned. Bybit pays a
   different rate on the same coins. This downloads the funding history of Bybit's USDT perpetual with the same symbol for
   every research coin: the 166 used before, the 125 untouched coins with a Binance perpetual, and the 199 new listings
   of the final-test file. Three files, each saved as soon as it is done; each can be downloaded again on its own.
   Funding rates only, from Bybit's public API; nothing is stored on the phone except which files were saved. */
(function(){
  'use strict';
  var YOUNG = ["0GUSDT", "2ZUSDT", "4USDT", "ACUUSDT", "AGTUSDT", "AIAUSDT", "AIGENSYNUSDT", "AINUSDT", "AIOTUSDT", "AIOUSDT", "AKEUSDT", "ALLOUSDT", "APRUSDT", "ARIAUSDT", "ARXUSDT", "ASTERUSDT", "ATHUSDT", "ATUSDT", "AUSDT", "AVNTUSDT", "AWEUSDT", "AZTECUSDT", "B2USDT", "BABYUSDT", "BANKUSDT", "BARDUSDT", "BASEDUSDT", "BASUSDT", "BEATUSDT", "BILLUSDT", "BIRBUSDT", "BLESSUSDT", "BLUAIUSDT", "BREVUSDT", "BSBUSDT", "BTRUSDT", "BTWUSDT", "BULLAUSDT", "BUSDT", "CAPUSDT", "CARVUSDT", "CCUSDT", "CFGUSDT", "CHIPUSDT", "CLANKERUSDT", "CLOUSDT", "COAIUSDT", "COLLECTUSDT", "CROSSUSDT", "CTRUSDT", "CUSDT", "CYSUSDT", "DATAIPUSDT", "DEEPUSDT", "DOLOUSDT", "DOODUSDT", "DOSUSDT", "EDENUSDT", "EDGEUSDT", "ELSAUSDT", "ENSOUSDT", "ERAUSDT", "ESPORTSUSDT", "ESPUSDT", "EULUSDT", "EVAAUSDT", "FFUSDT", "FHEUSDT", "FIGHTUSDT", "FLOCKUSDT", "FLUIDUSDT", "FOGOUSDT", "FOLKSUSDT", "FRAXUSDT", "FUSDT", "GENIUSUSDT", "GIGGLEUSDT", "GRAMUSDT", "GRVTUSDT", "GUAUSDT", "GWEIUSDT", "HAEDALUSDT", "HANAUSDT", "HEMIUSDT", "HOLOUSDT", "HOMEUSDT", "HUMAUSDT", "HUSDT", "HYPERUSDT", "HYPEUSDT", "ICNTUSDT", "IDOLUSDT", "INITUSDT", "INUSDT", "INXUSDT", "IRYSUSDT", "JCTUSDT", "KATUSDT", "KERNELUSDT", "KGENUSDT", "KITEUSDT", "LABUSDT", "LAUSDT", "LIGHTUSDT", "LINEAUSDT", "LITUSDT", "LYNUSDT", "MAGMAUSDT", "MANTRAUSDT", "MEGAUSDT", "MERLUSDT", "METUSDT", "MIRAUSDT", "MITOUSDT", "MMTUSDT", "MONUSDT", "MUSDT", "MYXUSDT", "NAORISUSDT", "NEWTUSDT", "NIGHTUSDT", "NOMUSDT", "NXPCUSDT", "ONUSDT", "OPENUSDT", "OPGUSDT", "OPNUSDT", "ORDERUSDT", "OUSDT", "PHAROSUSDT", "PIEVERSEUSDT", "PLAYUSDT", "POWERUSDT", "PRLUSDT", "PROVEUSDT", "PTBUSDT", "PUMPUSDT", "QUSDT", "RAVEUSDT", "RECALLUSDT", "RESOLVUSDT", "REUSDT", "RIVERUSDT", "ROBOUSDT", "SAHARAUSDT", "SAPIENUSDT", "SENTUSDT", "SIGNUSDT", "SKRUSDT", "SKYAIUSDT", "SKYUSDT", "SLXUSDT", "SOMIUSDT", "SOONUSDT", "SOPHUSDT", "SPACEUSDT", "SPKUSDT", "SPORTFUNUSDT", "SQDUSDT", "STABLEUSDT", "STARUSDT", "STBLUSDT", "STOUSDT", "SXTUSDT", "TACUSDT", "TAGUSDT", "TAIKOUSDT", "TAKEUSDT", "TAUSDT", "TOSHIUSDT", "TOWNSUSDT", "TRADOORUSDT", "TREEUSDT", "TRIAUSDT", "TRUSTUSDT", "TRUTHUSDT", "TURTLEUSDT", "UAIUSDT", "UBUSDT", "USELESSUSDT", "USUSDT", "VELVETUSDT", "WCTUSDT", "WETUSDT", "WLFIUSDT", "XANUSDT", "XNYUSDT", "XPINUSDT", "XPLUSDT", "YBUSDT", "ZAMAUSDT", "ZBTUSDT", "ZESTUSDT", "ZKCUSDT", "ZKPUSDT", "ZORAUSDT", "\u5e01\u5b89\u4eba\u751fUSDT", "\u6211\u8e0f\u9a6c\u6765\u4e86USDT", "\u9f99\u867eUSDT"], F3P = ["1000CAT", "1000CHEEMS", "1000SATS", "1MBABYDOGE", "ACT", "AI", "AIXBT", "ALPINE", "ANIME", "ARK", "ASR", "ASTR", "AUCTION", "AUDIO", "AVA", "AXL", "BANANAS31", "BANANA", "BB", "BEAMX", "BEL", "BERA", "BIO", "BMT", "BOME", "BROCCOLI714", "CAKE", "CATI", "CETUS", "CGPT", "COOKIE", "COW", "CTK", "CVC", "CVX", "DEXE", "DGB", "DIA", "DODO", "DOGS", "EIGEN", "EPIC", "FIDA", "FLUX", "FORM", "FTT", "GAS", "GLMR", "GPS", "GUN", "G", "HEI", "HIVE", "HMSTR", "HOT", "ILV", "JST", "KAIA", "KAITO", "LAYER", "LISTA", "LSK", "LUMIA", "LUNA", "MBL", "MEME", "METIS", "ME", "MOVE", "MOVR", "MUBARAK", "NEIRO", "NIL", "OG", "ONG", "ORCA", "PARTI", "PENGU", "PHA", "PIXEL", "PNUT", "POL", "POLYX", "POWR", "PROM", "PUNDIX", "QUICK", "RAD", "RARE", "RAY", "RED", "RENDER", "REZ", "RIF", "RONIN", "RPL", "SANTOS", "SCR", "SC", "SHELL", "SLP", "SOLV", "SPELL", "STEEM", "STRAX", "SUN", "S", "SYN", "TAO", "THE", "TRUMP", "TST", "TURBO", "T", "TUT", "USTC", "USUAL", "VANA", "VELODROME", "VTHO", "WAXP", "WIF", "W", "XVG", "ZRO"];
  var STUDIED = ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'];
  var API = 'https://api.bybit.com/v5/market/funding/history', FROM = Date.UTC(2020, 0, 1), PKEY = 'omega_bybitdl_v1', busy = false, stop = false, kept = [];
  function el(id){ return document.getElementById(id); }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function lsGet(){ try{ var v = JSON.parse(localStorage.getItem(PKEY) || 'null'); return v && typeof v === 'object' && v.done ? v : { done:{} }; }catch(e){ return { done:{} }; } }
  function lsSet(v){ try{ localStorage.setItem(PKEY, JSON.stringify(v)); }catch(e){} }
  function seen(){ var F = (window.OMEGA_FRESHEXPORT && window.OMEGA_FRESHEXPORT.FRESH) || [], N = (window.OMEGA_FRESH2EXPORT && window.OMEGA_FRESH2EXPORT.FRESH) || [];
    return STUDIED.map(function(b){ return b + 'USDT'; }).concat(F, N); }
  function groups(){ return [ { id:'by-seen', label:'the 166 coins used before', coins:seen() }, { id:'by-final', label:'the 125 untouched coins', coins:F3P.map(function(b){ return b + 'USDT'; }) }, { id:'by-new', label:'the 199 new listings', coins:YOUNG } ]; }
  var SHORT = { 'by-seen':'Used coins', 'by-final':'Untouched coins', 'by-new':'New listings' };
  async function getJSON(url){ for(var a=0; a<5; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 403){ await sleep(10000*(a+1)); continue; } if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 4) throw e; await sleep(1500*(a+1)); } } return null; }
  // all settlements of one perpetual, newest first from Bybit, paged backwards to Jan 2020
  async function funding(sym, to){ var out = [], end = to, guard = 0;
    while(end > FROM && !stop && guard++ < 400){ var d = await getJSON(API + '?category=linear&symbol=' + sym + '&endTime=' + end + '&limit=200');   // only endTime: the 200 settlements up to it, newest first
      if(!d) break; if(d.retCode && d.retCode !== 0){ if(!out.length) return { missing:String(d.retMsg || d.retCode) }; break; }
      var L = (d.result && d.result.list) || []; if(!L.length) break; var oldest = Infinity;
      L.forEach(function(x){ var t = +x.fundingRateTimestamp, r = +x.fundingRate; if(t >= FROM && t <= to && isFinite(r)) out.push([t, r]); if(t < oldest) oldest = t; });
      if(!(oldest < end) || L.length < 200) break; end = oldest - 1; await sleep(130); }
    var by = {}; out.forEach(function(x){ by[x[0]] = x[1]; }); var ts = Object.keys(by).map(Number).sort(function(a, b){ return a - b; });
    return { list:ts.map(function(t){ return [t, by[t]]; }) }; }
  function encode(sym, list){ var m = { sym:sym, src:'Bybit USDT linear perpetual', n:list.length, fund:{ t:[], r:[] } }, pt = 0;
    list.forEach(function(x, i){ var tm = Math.round(x[0]/60000); m.fund.t.push(i ? tm - pt : tm); pt = tm; m.fund.r.push(Math.round(x[1]*1e7)); }); return m; }
  async function save(out, name){ var txt = JSON.stringify(out); if(/"(apiKey|api_key|token|secret|password|phone|whatsapp)"\s*:/i.test(txt)) throw new Error('refused: credential-like field');
    var blob; if(typeof CompressionStream !== 'undefined'){ blob = await new Response(new Blob([txt]).stream().pipeThrough(new CompressionStream('gzip'))).blob(); name += '.json.gz'; } else { blob = new Blob([txt], { type:'application/json' }); name += '.json'; }
    var url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    var mb = Math.round(blob.size/1048576*10)/10; kept = kept.filter(function(k){ return k.name !== name; }); kept.push({ name:name, url:url, mb:mb }); showKept(); return { name:name, mb:mb }; }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function showKept(){ var k = el('bySaveAgain'); if(!k) return; if(!kept.length){ k.innerHTML = ''; return; }
    k.innerHTML = 'Not in your Downloads? Tap a name to save it again: ' + kept.map(function(x){ return '<a href="' + x.url + '" download="' + esc(x.name) + '">' + esc(x.name) + '</a> (' + x.mb + ' MB)'; }).join(' · '); }
  function oneButtons(){ var row = el('byOneRow'); if(!row) return; var P = lsGet(); groups().forEach(function(g){ var bt = row.querySelector('[data-g="' + g.id + '"]'); if(!bt) return; bt.textContent = (P.done[g.id] ? '✓ ' : '') + SHORT[g.id]; bt.disabled = busy; }); }
  function label(){ var G = groups(), P = lsGet(), n = G.filter(function(g){ return P.done[g.id]; }).length; return n === G.length ? 'Download the Bybit funding again' : n ? 'Continue the Bybit funding (' + n + ' of ' + G.length + ' files saved)' : 'Download Bybit funding for research (' + G.length + ' files)'; }
  async function run(onlyId){ if(busy){ stop = true; return 'stopping'; } var G = groups(); if(onlyId && !G.some(function(g){ return g.id === onlyId; })) return 'no such file';
    busy = true; stop = false; var msg = el('byExportMsg'), b = el('byExportBtn'); if(b) b.textContent = 'Stop'; oneButtons();
    var P = lsGet(); if(!onlyId && G.every(function(g){ return P.done[g.id]; })) P = { done:{} }; var said = [];
    try{ for(var gi=0; gi<G.length && !stop; gi++){ var g = G[gi]; if(onlyId ? g.id !== onlyId : P.done[g.id]) continue;
        var to = Date.now(), head = 'File ' + (gi + 1) + ' of ' + G.length + ' (' + g.label + '): ';
        var out = { format:'omega-bybit-funding', v:1, part:g.id, plan:'PLAN15', src:'Bybit public API, USDT linear perpetuals, same symbol', from:new Date(FROM).toISOString(), to:new Date(to).toISOString(), exportedAt:new Date().toISOString(), markets:[], missing:[], skipped:[] };
        for(var k=0; k<g.coins.length && !stop; k++){ var sym = g.coins[k]; if(msg) msg.textContent = head + sym + ' (' + (k + 1) + ' of ' + g.coins.length + ')…';
          try{ var f = await funding(sym, to); if(f.missing){ out.missing.push(sym + ': ' + f.missing); continue; } if(!f.list.length){ out.missing.push(sym + ': no funding'); continue; } out.markets.push(encode(sym, f.list)); }
          catch(e){ out.skipped.push(sym + ': ' + (e && e.message || e)); } }
        if(stop) break;
        var sv = await save(out, 'omega-bybit-funding-' + g.id.slice(3) + '-' + new Date().toISOString().slice(0, 10)); P.done[g.id] = sv.name; lsSet(P); said.push(sv.name + ' (' + sv.mb + ' MB, ' + out.markets.length + ' coins)'); await sleep(1500); }
      var n = G.filter(function(g){ return P.done[g.id]; }).length, r = (stop ? 'Stopped. ' : '') + (onlyId ? (said.length ? 'Saved now: ' + said.join(', ') + '. Attach it for research.' : 'Nothing saved.') : n + ' of ' + G.length + ' files saved.' + (said.length ? ' Saved now: ' + said.join(', ') + '.' : '') + ' ' + (n === G.length ? 'All done — attach all ' + G.length + ' files for research.' : 'Press again to continue from the next file.'));
      if(msg) msg.textContent = r; return r; }
    catch(e){ if(msg) msg.textContent = 'Bybit download stopped: ' + (e && e.message || e) + '. Press again to continue.'; return String(e && e.message || e); }
    finally{ busy = false; stop = false; if(b) b.textContent = label(); oneButtons(); } }
  function wire(){ var host = el('c15ExportBtn'); if(!host || el('byExportBtn')) return !!el('byExportBtn');
    var wrap = document.createElement('div'); wrap.style.marginTop = '14px';
    wrap.innerHTML = '<p class="hint" style="margin:0 0 6px;color:var(--text);"><b>Round 15: Bybit funding.</b> Funding history of Bybit’s perpetual for every research coin, to test the funding harvest on whichever venue pays more. 3 files, about an hour in all; keep the app open and the screen on. Funding rates only.</p>' +
      '<button class="btn-outline" type="button" id="byExportBtn">' + label() + '</button> <span class="hint" id="byExportMsg"></span>';
    var one = document.createElement('div'); one.id = 'byOneRow'; one.style.cssText = 'margin-top:6px; display:flex; flex-wrap:wrap; gap:6px; align-items:center';
    one.innerHTML = '<span class="hint">One file on its own:</span>' + groups().map(function(g){ return '<button class="btn-outline" type="button" style="padding:5px 9px" data-g="' + g.id + '">' + SHORT[g.id] + '</button>'; }).join('') + '<span class="hint" id="bySaveAgain" style="flex-basis:100%; word-break:break-all"></span>';
    wrap.appendChild(one); host.parentNode.parentNode.appendChild(wrap); var b = el('byExportBtn'); if(b) b.addEventListener('click', function(){ run(); });
    Array.prototype.forEach.call(one.querySelectorAll('[data-g]'), function(bt){ bt.addEventListener('click', function(){ run(bt.getAttribute('data-g')); }); }); oneButtons(); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 90) clearInterval(iv); }, 1000);
  window.OMEGA_BYBITEXPORT = { run:run, groups:groups, funding:funding, encode:encode, progress:lsGet, kept:function(){ return kept.map(function(k){ return { name:k.name, mb:k.mb }; }); } };
})();
</script>
