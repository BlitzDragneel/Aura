<script>/* ═══ WIDE DATA STORE (v6.5.70) — daily bars and funding for the 291 research coins, kept on the phone for the Edge Lab ═══
   The coins: the 25 studied, 51 fresh and 90 new coins, and the 125 untouched coins of round 12 that have a perpetual.
   For each: daily open/high/low/close, volume and taker-buy volume (Binance spot, Jan 2020 on) and the daily sum and count
   of its USDT-M funding payments, plus the last three days of payments (for the squeeze and delisting warnings).
   Stored in this phone's IndexedDB (database omega_wide), filled the first time in about 15–25 minutes, then topped up
   by the Autopilot every few hours (two small requests a coin). Prices and funding only; nothing is sent anywhere. */
(function(){
  'use strict';
  var DB = 'omega_wide', DAY = 86400e3, FROM = Date.UTC(2020, 0, 1), API = 'https://data-api.binance.vision/api/v3/', FAPI = 'https://fapi.binance.com/fapi/v1/', busy = false, stop = false, version = 0, cache = null, msg = '';
  var STUDIED = ['BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'];
  var FINAL3 = __FINAL3__;
  function list(){ var F = (window.OMEGA_FRESHEXPORT && window.OMEGA_FRESHEXPORT.FRESH) || [], N = (window.OMEGA_FRESH2EXPORT && window.OMEGA_FRESH2EXPORT.FRESH) || [], out = [], seen = {};
    STUDIED.concat(F, N, FINAL3).forEach(function(s){ s = String(s).replace(/USDT$/, '') + 'USDT'; if(!seen[s]){ seen[s] = 1; out.push(s); } }); return out; }
  function lastBar(r){ if(!r || r.k0 == null) return null; for(var i=r.c.length-1; i>=0; i--) if(r.c[i] != null) return r.k0 + i; return null; }
  function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
  function open(){ return new Promise(function(res, rej){ var r = indexedDB.open(DB, 1); r.onupgradeneeded = function(){ var d = r.result; if(!d.objectStoreNames.contains('coins')) d.createObjectStore('coins', { keyPath:'sym' }); if(!d.objectStoreNames.contains('meta')) d.createObjectStore('meta'); };
    r.onsuccess = function(){ res(r.result); }; r.onerror = function(){ rej(r.error); }; }); }
  var dbp = null; function db(){ return dbp || (dbp = open()); }
  function tx(store, mode, fn){ return db().then(function(d){ return new Promise(function(res, rej){ var t = d.transaction(store, mode), s = t.objectStore(store), out = fn(s);
    t.oncomplete = function(){ res(out && typeof out === 'object' && 'onsuccess' in out ? out.result : out); };   // a request: its result (undefined when the key is missing), never the request itself
    t.onerror = function(){ rej(t.error); }; t.onabort = function(){ rej(t.error); }; }); }); }
  function get(sym){ return tx('coins', 'readonly', function(s){ return s.get(sym); }); }
  function put(rec){ return tx('coins', 'readwrite', function(s){ s.put(rec); }); }
  function all(){ if(cache && cache.v === version) return Promise.resolve(cache.recs);
    return tx('coins', 'readonly', function(s){ return s.getAll(); }).then(function(r){ cache = { v:version, recs:r || [] }; return cache.recs; }); }
  async function getJSON(url){ for(var a=0; a<4; a++){ try{ var r = await fetch(url); if(r.status === 429 || r.status === 418){ await sleep(8000*(a+1)); continue; } if(r.status === 400) return []; if(!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }catch(e){ if(a === 3) throw e; await sleep(1500*(a+1)); } } return []; }
  async function klines(sym, from, to){ var rows = [], t = from;
    while(t < to && !stop){ var d = await getJSON(API + 'klines?symbol=' + sym + '&interval=1d&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(k){ var ot = +k[0]; if(ot >= t && ot < to) rows.push(k); }); var last = +d[d.length-1][0]; if(!(last >= t)) break; t = last + DAY; await sleep(100); }
    return rows; }
  async function funding(sym, from, to){ var out = [], t = from;
    while(t < to && !stop){ var d = await getJSON(FAPI + 'fundingRate?symbol=' + sym + '&limit=1000&startTime=' + t + '&endTime=' + (to - 1));
      if(!Array.isArray(d) || !d.length) break; d.forEach(function(x){ var ft = +x.fundingTime; if(ft >= t && ft < to) out.push([ft, +x.fundingRate]); }); var last = +d[d.length-1].fundingTime; if(!(last >= t) || d.length < 1000) break; t = last + 1; await sleep(120); }
    return out; }
  // merge new daily bars and funding into a record (day arrays share k0; funding before the first bar extends the arrays back)
  function merge(rec, sym, rows, fund, now){ rec = rec || { sym:sym, k0:null, c:[], h:[], l:[], v:[], tb:[], ff:[], fc:[], f1:null, fev:[] };
    var days = rows.map(function(k){ return Math.floor(+k[0]/DAY); }).concat(fund.map(function(q){ return Math.floor(q[0]/DAY); }));
    if(!days.length && rec.k0 == null) return null;
    var lo = Math.min.apply(null, days.length ? days : [rec.k0]), K0 = rec.k0 == null ? lo : Math.min(rec.k0, lo);
    if(rec.k0 != null && K0 < rec.k0){ var pad = rec.k0 - K0; ['c', 'h', 'l', 'v', 'tb'].forEach(function(k){ rec[k] = new Array(pad).fill(null).concat(rec[k]); }); rec.ff = new Array(pad).fill(0).concat(rec.ff); rec.fc = new Array(pad).fill(0).concat(rec.fc); }
    rec.k0 = K0;
    rows.forEach(function(k){ var i = Math.floor(+k[0]/DAY) - K0; rec.c[i] = +k[4]; rec.h[i] = +k[2]; rec.l[i] = +k[3]; rec.v[i] = +k[5]; rec.tb[i] = +k[9]; });
    // funding: rebuild the touched days from the payments fetched (a day's sum and count)
    var byDay = {}; fund.forEach(function(q){ var d = Math.floor(q[0]/DAY); (byDay[d] = byDay[d] || []).push(q); });
    Object.keys(byDay).forEach(function(d){ var i = +d - K0, ps = byDay[d], keep = (rec._seen && rec._seen[d]) || {}; ps.forEach(function(q){ keep[q[0]] = q[1]; }); var s = 0, c = 0; Object.keys(keep).forEach(function(t){ s += keep[t]; c++; }); rec.ff[i] = s; rec.fc[i] = c; rec._seen = rec._seen || {}; rec._seen[d] = keep; });
    // keep only the last few days of per-payment detail
    if(rec._seen){ var cut = Math.floor(now/DAY) - 4; Object.keys(rec._seen).forEach(function(d){ if(+d < cut) delete rec._seen[d]; }); }
    var n = Math.max(rec.c.length, rec.ff.length); ['c', 'h', 'l', 'v', 'tb'].forEach(function(k){ for(var i=0; i<n; i++) if(rec[k][i] === undefined) rec[k][i] = null; }); for(var j=0; j<n; j++){ if(rec.ff[j] === undefined) rec.ff[j] = 0; if(rec.fc[j] === undefined) rec.fc[j] = 0; }
    fund.forEach(function(q){ if(rec.f1 == null || q[0] > rec.f1) rec.f1 = q[0]; });
    var ev = []; Object.keys(rec._seen || {}).forEach(function(d){ Object.keys(rec._seen[d]).forEach(function(t){ ev.push([+t, rec._seen[d][t]]); }); }); rec.fev = ev.sort(function(a, b){ return a[0] - b[0]; });
    rec.upd = now; return rec; }
  async function one(sym, now){ var rec = await get(sym), today = Math.floor(now/DAY)*DAY;
    var lb = lastBar(rec), from = lb != null ? (lb - 2)*DAY : FROM, ffrom = rec && rec.f1 ? rec.f1 + 1 : FROM;
    if(rec && rec.upd && now - rec.upd < 6*3600e3 && Math.floor(rec.upd/DAY) === Math.floor(now/DAY)) return 'fresh';
    var rows = await klines(sym, Math.max(FROM, from), today), fund = []; try{ fund = await funding(sym, ffrom, now); }catch(e){}
    if(!rec && !rows.length) return 'none';
    var r = merge(rec, sym, rows, fund, now); if(!r) return 'none'; r.noPerp = !(r.f1); await put(r); version++; return rec ? 'updated' : 'added'; }
  async function status(){ var L = list(), recs = await all().catch(function(){ return []; }), have = {}; recs.forEach(function(r){ have[r.sym] = r; });
    var stored = L.filter(function(s){ return have[s]; }), today = Math.floor(Date.now()/DAY), fresh = stored.filter(function(s){ var b = lastBar(have[s]); return b != null && b >= today - 2; });
    var lastDay = stored.reduce(function(m, s){ var b = lastBar(have[s]); return b != null ? Math.max(m, b) : m; }, 0), withPerp = stored.filter(function(s){ return have[s].f1; }).length;
    return { coins:L.length, stored:stored.length, fresh:fresh.length, withPerp:withPerp, lastDay:lastDay || null, complete:stored.length >= L.length - 3, busy:busy, msg:msg }; }
  async function runNow(budgetMs, onMsg){ if(busy) return { skip:true, text:'already running' }; busy = true; stop = false; var t0 = Date.now(), L = list(), now = Date.now(), done = 0, added = 0, skipped = 0, lastErr = '';
    try{ var recs = await all().catch(function(){ return []; }), have = {}; recs.forEach(function(r){ have[r.sym] = r; });
      var order = L.filter(function(s){ return !have[s]; }).concat(L.filter(function(s){ return have[s] && !(have[s].upd && Math.floor(have[s].upd/DAY) === Math.floor(now/DAY) && now - have[s].upd < 6*3600e3); }));
      for(var i=0; i<order.length && !stop; i++){ if(budgetMs && Date.now() - t0 > budgetMs) break; var s = order[i]; msg = 'Coin data: ' + s.replace(/USDT$/, '') + ' (' + (i + 1) + ' of ' + order.length + ')'; if(onMsg) onMsg(msg);
        try{ var r = await one(s, now); done++; if(r === 'added') added++; if(r === 'none') skipped++; }catch(e){ skipped++; lastErr = s + ': ' + String(e && e.message || e).slice(0, 120); } }
      var st = await status(); msg = ''; return { text:'Coin data: ' + st.stored + ' of ' + st.coins + ' coins stored (' + st.fresh + ' up to date); this run ' + done + ' (' + added + ' new' + (skipped ? ', ' + skipped + ' not stored' + (lastErr ? '; last problem ' + lastErr : '') : '') + ').' }; }
    catch(e){ return { error:(e && e.message) || String(e) }; }
    finally{ busy = false; msg = ''; } }
  function every(){ var s = lastStatus; if(!s || !s.complete) return 3*60e3; return 4*3600e3; }
  var lastStatus = null; setInterval(function(){ status().then(function(s){ lastStatus = s; }).catch(function(){}); }, 60e3); setTimeout(function(){ status().then(function(s){ lastStatus = s; }).catch(function(){}); }, 3000);
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(J.some(function(j){ return j.id === 'wide'; })) return true;
    J.push({ id:'wide', lane:'heavy', prio:3, label:'Coin data for the Edge Lab (291 coins, daily)', what:'Downloads and tops up daily bars and funding for the 291 research coins from Binance, a few coins at a time. Prices and funding only.', every:every, run:function(){ return runNow(45e3); } }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  function getMeta(k){ return tx('meta', 'readonly', function(s){ return s.get(k); }); }
  function putMeta(k, v){ return tx('meta', 'readwrite', function(s){ s.put(v, k); }); }
  function release(){ cache = null; }   // the Edge Lab copies the records into its own arrays, then lets these go
  window.OMEGA_WIDE = { release:release, getMeta:getMeta, putMeta:putMeta, lastBar:lastBar, list:list, all:all, get:get, status:status, runNow:runNow, stop:function(){ stop = true; }, version:function(){ return version; }, _:{ merge:merge, put:put } };
})();
</script>
