<script>/* ═══ AUTOPILOT COVERAGE (v6.5.87, v6.5.90, v6.5.91) — the five newest parts join the Autopilot ═══
   v6.5.91: the Autopilot switches Market Watch on again, but in LIGHT mode (one-minute bars instead of every trade), which
   is far lighter for a phone; switch the job off on the Autopilot page to stop it, or choose full mode in Market Watch.
   v6.5.90: the Market Watch job no longer starts the recorder by itself (full mode streams every trade of 25 coins and made
   phones stick); it keeps it running only when it was switched on in Market Watch. The download job now also fetches forex.
   Until v6.5.86 the climax watch (v6.5.78), Market Watch (v6.5.77), the Breakout Desk (v6.5.83), the gold and silver
   download (v6.5.84) and Market Profiles' forward record (v6.5.85) ran on their own timers while the app was open, outside
   the Autopilot: it neither ran nor showed them. This registers each as an Operator job, the same way the harvest, round 12,
   carry, BTC-trend, Edge Lab, workshop and wide-data modules already register theirs, so the one "Brain automation" switch
   runs everything and the Operator table shows each job's last result, next run and its own on/off switch. Each job only
   calls the part's own controls (check, start, run); their own timers stay as a fallback when the Autopilot is off. Paper
   only; nothing places orders; it works only while the app is open. */
(function(){
  'use strict';
  var H = 3600e3;
  function settling(){ var m = Date.now() % H; return m < 180e3 ? { skip:true, text:'waiting for the last hour’s bar to settle', retryIn:180e3 - m + 5e3 } : null; }
  function closedH(){ return Math.floor(Date.now()/H) - 1; }
  var JOBS = [
    { id:'climax', lane:'live', prio:3, label:'Climax watch (the rule that passed)', what:'Every hour: checks every Binance USDT perpetual for a climax flush and keeps its forward paper record (round 16’s frozen rule).', every:15*60e3,
      run: async function(){ var X = window.OMEGA_CLIMAX; if(!X) return { skip:true, text:'the climax watch is not loaded', retryIn:10*60e3 }; var w = settling(); if(w) return w;
        var s = X.state(); if(s.busy) return { skip:true, text:'already checking', retryIn:120e3 }; if(s.lastH != null && s.lastH >= closedH()) return 'Up to date to the hour ending ' + new Date((closedH() + 1)*H).toISOString().slice(11, 16) + ' UTC.';
        var r = await X.check(true); return r === 'busy' ? { skip:true, text:'already checking', retryIn:120e3 } : String(r || 'Checked.'); } },
    { id:'bdesk', lane:'live', prio:2, label:'Breakout Desk records (failed setups, kept as a record)', what:'Every hour, after the climax watch: steps both Breakout Desk paper accounts through the new hours (setups A and B failed a clean test; record only, no alerts).', every:15*60e3,
      run: async function(){ var B = window.OMEGA_BDESK; if(!B) return { skip:true, text:'the Breakout Desk is not loaded', retryIn:10*60e3 }; var w = settling(); if(w) return w;
        var s = B.state(); if(s.busy) return { skip:true, text:'already checking', retryIn:120e3 }; if(s.lastH != null && s.lastH >= closedH()) return 'Up to date.';
        var r = await B.check(true); return r === 'busy' ? { skip:true, text:'already checking', retryIn:120e3 } : String(r || 'Checked.'); } },
    { id:'mprof', lane:'live', prio:2, label:'Market Profiles: live prices and the session record (plan E6)', what:'Every hour: reads gold and the five coins from Binance and records each finished day’s moves outside and during US hours, for plan E6 (judged after 26 weeks).', every:60*60e3,
      run: async function(){ var M = window.OMEGA_MPROF; if(!M) return { skip:true, text:'Market Profiles is not loaded', retryIn:10*60e3 }; await M.check(); return String(M.state().msg || 'Checked.'); } },
    { id:'mwatch', lane:'live', prio:3, label:'Market Watch recorder (liquidations, open interest, order book)', what:'Keeps the recorder running: the public footprints of forced and large traders, which have no history at the exchange. Export it from Market Watch when asked.', every:10*60e3,
      run: async function(){ var W = window.OMEGA_WATCH; if(!W) return { skip:true, text:'Market Watch is not loaded', retryIn:10*60e3 }; var c = W.cfg ? W.cfg() : {}; if(!c.on && W.setCfg){ c.on = true; c.mode = 'light'; W.setCfg(c); }   // v6.5.91: the Autopilot runs it again, in light mode (one-minute bars, not every trade)
        if(W.running()) return 'Recording (' + (c.mode || 'full') + ' mode).'; await W.start(); return W.running() ? 'Started recording (' + (c.mode || 'full') + ' mode' + (c.mode === 'light' ? ', gentle on phones' : '') + ').' : { error:'the recorder did not start' }; } },
    { id:'goldh', lane:'heavy', prio:1, label:'Gold, silver and forex hourly download (plans E4, E15)', what:'Every 6 hours until done: continues the gold and silver hourly download through the shared Twelve Data queue. When complete, press Save file on the Breakout Desk gold card and send the file.', every:6*3600e3,
      run: async function(){ var G = window.OMEGA_GOLDH; if(!G) return { skip:true, text:'the gold download is not loaded', retryIn:30*60e3 }; var s = G.state();
        if(s.busy) return { skip:true, text:'already downloading', retryIn:10*60e3 }; await G.refresh();
        var done = G.SYMS.every(function(k){ var r = G.state().recs[k]; return r && r.done; }); if(done) return 'Complete: press Save file on the Breakout Desk gold card and send the file.';
        var msg = String(await G.run() || ''); if(/^Stopped/.test(msg)) return { skip:true, text:msg.replace(/^Stopped: /, ''), retryIn:3*3600e3 };
        var done2 = G.SYMS.every(function(k){ var r = G.state().recs[k]; return r && r.done; }); return done2 ? 'Complete: press Save file on the Breakout Desk gold card and send the file.' : msg; } }
  ];
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); JOBS.forEach(function(j){ if(!J.some(function(x){ return x.id === j.id; })) J.push(j); }); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  window.OMEGA_AUTOCOV = { JOBS:JOBS, register:register };
})();
</script>
