<script>/* ═══ OMEGA PRIME — core (before the reused modules) ═══
   1. PRIME_LS: all of Prime's data lives under the prefix "prime:" so it can never mix with the original OMEGA build, even
      when both files are opened in the same browser (file pages share one storage).
   2. The Autopilot: one scheduler. Modules register jobs (id, label, what, every, run); it runs each when due, one at a time,
      records last run and result, can switch any job off, and keeps running while the app is open. Jobs that belong to the
      original build's research machinery are not accepted here. OMEGA Prime places no orders. */
(function(){
  'use strict';
  var P = 'prime:';
  window.PRIME_LS = {
    getItem:function(k){ try{ return window.localStorage.getItem(P + k); }catch(e){ return null; } },
    setItem:function(k, v){ try{ window.localStorage.setItem(P + k, v); }catch(e){} },
    removeItem:function(k){ try{ window.localStorage.removeItem(P + k); }catch(e){} },
    keys:function(){ var out = []; try{ for(var i = 0; i < window.localStorage.length; i++){ var k = window.localStorage.key(i); if(k && k.indexOf(P) === 0) out.push(k.slice(P.length)); } }catch(e){} return out; } };
})();
</script>
<script>/* ═══ PRIME AUTOPILOT ═══ */
(function(){
  'use strict';
  var KEY = 'prime_op_v1', BLOCK = { mwdays:1, autoexp:1 }, JOBS = [], st = { jobs:{} }, busy = false, cur = null;
  try{ var v = JSON.parse(window.PRIME_LS.getItem(KEY) || 'null'); if(v && v.jobs) st = v; }catch(e){}
  function save(){ try{ window.PRIME_LS.setItem(KEY, JSON.stringify(st)); }catch(e){} }
  function js(id){ return st.jobs[id] || (st.jobs[id] = { enabled:true, last:0, result:'' }); }
  // modules push into jobs(); a filtered view keeps blocked research jobs out
  var view = { push:function(j){ if(!j || !j.id || BLOCK[j.id]) return JOBS.length; if(!JOBS.some(function(x){ return x.id === j.id; })) JOBS.push(j); return JOBS.length; },
    some:function(f){ return JOBS.some(f); }, filter:function(f){ return JOBS.filter(f); }, map:function(f){ return JOBS.map(f); }, forEach:function(f){ JOBS.forEach(f); }, find:function(f){ return JOBS.find(f); } };
  Object.defineProperty(view, 'length', { get:function(){ return JOBS.length; } });
  function everyOf(j){ return typeof j.every === 'function' ? 3600e3 : (+j.every || 3600e3); }
  function due(j, now){ var s = js(j.id); if(!s.enabled) return false; if(s.retryAt && now < s.retryAt) return false; return now - (s.last || 0) >= everyOf(j); }
  async function runJob(j){ var s = js(j.id), t0 = Date.now(); cur = j.id;
    try{ var r = await j.run(); r = (r && typeof r === 'object') ? r : { text:String(r == null ? '' : r) };
      if(r.skip){ s.result = 'Waiting: ' + (r.text || ''); s.retryAt = t0 + (r.retryIn || 10*60e3); }
      else if(r.error){ s.fails = (s.fails || 0) + 1; s.result = 'Problem: ' + r.error; s.last = t0; s.retryAt = t0 + Math.min(6*3600e3, 5*60e3*Math.pow(2, s.fails - 1)); }
      else { s.fails = 0; s.retryAt = 0; s.last = t0; s.result = String(r.text || 'Done.'); } }
    catch(e){ s.fails = (s.fails || 0) + 1; s.last = t0; s.result = 'Problem: ' + (e && e.message || e); s.retryAt = t0 + Math.min(6*3600e3, 5*60e3*Math.pow(2, s.fails - 1)); }
    s.ms = Date.now() - t0; cur = null; save(); if(window.PRIME_UI) window.PRIME_UI.autopilotChanged(); }
  async function loop(){ if(busy) return; busy = true; try{ var now = Date.now(); for(var i = 0; i < JOBS.length; i++){ if(due(JOBS[i], now)) await runJob(JOBS[i]); } } finally{ busy = false; } }
  async function tick(id){ var j = JOBS.find(function(x){ return x.id === id; }); if(j) await runJob(j); }
  function setEnabled(id, on){ js(id).enabled = !!on; save(); }
  setTimeout(function(){ loop(); setInterval(loop, 60e3); }, 4000);
  window.OMEGA_OPERATOR = { jobs:function(){ return view; }, list:function(){ return JOBS.slice(); }, state:function(){ return st; }, tick:tick, run:loop, setEnabled:setEnabled, current:function(){ return cur; } };
})();
</script>
