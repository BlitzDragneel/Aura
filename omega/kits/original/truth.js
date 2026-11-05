<script>/* ═══ DATA CHECK AND BASELINES (v6.5.96) — is every feed live, do prices make sense, does the bot beat holding BTC, does it survive worse fills ═══
   From the competitor audit, only what helps find an edge or keeps data honest:
   1. Data check (Analysis page, top): every Autopilot job — fresh, overdue (more than twice its schedule plus 10 minutes),
      failing, never run, or switched off — and, for every market Market Read has read, whether its newest finished candle
      is current (older than 2 hours = the data stopped) and whether the futures mark price is within 0.5% of the spot index
      (Binance's index is built from several spot exchanges). Problems are listed plainly and notified once every 6 hours.
   2. Baseline (Risk Guard page): the Growth Bot's change against simply holding BTC over the same period (from the first
      time this check saw the bot), and against cash. Signals that cannot beat holding add nothing.
   3. Fill stress (Risk Guard page): the bot's result again with worse fills — +0.05% and +0.15% extra cost a side on every
      trade. A result that only survives perfect fills is fragile. It reads records; it changes nothing. */
(function(){
  'use strict';
  var H = 3600e3, KT = 'omega_truth_v1', state = { last:null };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function load(k){ try{ return JSON.parse(localStorage.getItem(k) || 'null'); }catch(e){ return null; } }
  function save(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function ago(ms){ if(ms == null) return 'never'; var m = Math.round(ms/60e3); return m < 60 ? m + ' min ago' : m < 2880 ? Math.round(m/60) + ' h ago' : Math.round(m/1440) + ' days ago'; }
  // ── 1. data check (pure, given the Operator and the reads) ──
  function jobsCheck(jobs, st, now){ return (jobs || []).map(function(j){ var s = (st || {})[j.id] || {}, every = typeof j.every === 'function' ? H : (+j.every || H), age = s.last ? now - s.last : null, on = s.enabled !== false;
      var status = !on ? 'off' : !s.last ? 'never run' : /^Problem/.test(s.result || '') ? 'failing' : age > 2*every + 10*60e3 ? 'overdue' : 'fresh';
      return { id:j.id, label:j.label || j.id, age:age, status:status, result:s.result || '' }; }); }
  function readsCheck(reads, now){ var out = []; Object.keys(reads || {}).forEach(function(sym){ var A = reads[sym]; if(!A || A.err) return;
      var candleAge = A.lastH != null ? now - (A.lastH + 1)*H : null, prem = A.pos && A.pos.premium != null ? A.pos.premium : null, issues = [];
      if(candleAge != null && candleAge > 2*H) issues.push('newest finished candle is ' + ago(candleAge).replace(' ago', '') + ' old');
      if(prem != null && Math.abs(prem) > 0.005) issues.push('futures price ' + (prem*100).toFixed(2) + '% from the spot index');
      if(A.at && now - A.at > 3*H) issues.push('read ' + ago(now - A.at));
      out.push({ sym:sym, ok:!issues.length, issues:issues, prem:prem, candleAge:candleAge }); }); return out; }
  // ── 2 and 3. baseline and fill stress (pure, given the bot and BTC prices) ──
  function baseline(bot, T, btcNow){ if(!bot || !T || !(T.btc0 > 0) || !(btcNow > 0)) return null; var botChg = bot.eq/T.eq0 - 1, btcChg = btcNow/T.btc0 - 1; return { since:T.t0, bot:botChg, btc:btcChg, beats:botChg > btcChg }; }
  function stress(bot){ if(!bot || !bot.closed) return null; var c = bot.closed.filter(function(x){ return x.nt > 0; }), skipped = bot.closed.length - c.length, base = 0, cons = 0, hard = 0;
    c.forEach(function(x){ base += x.pnl; cons += x.pnl - x.nt*0.0005*2; hard += x.pnl - x.nt*0.0015*2; });
    var s0 = bot.start0 || 100, word = !c.length ? 'no trades yet' : base <= 0 ? 'losing even with base fills' : hard > 0 ? 'robust: still positive with much worse fills' : cons > 0 ? 'sensitive: survives slightly worse fills, not much worse' : 'fragile: only positive with perfect fills';
    return { n:c.length, skipped:skipped, base:s0 + base, cons:s0 + cons, hard:s0 + hard, word:word }; }
  function btcPrice(){ try{ var a = window.OMEGA_MREAD.state().reads.BTCUSDT; if(a && a.price && Date.now() - a.at < 6*H) return a.price; }catch(e){} try{ var d = window.OMEGA_DPLAN.state().reads.BTCUSDT; if(d && d.price && Date.now() - d.at < 6*H) return d.price; }catch(e){} return null; }
  // ── run ──
  function run(){ var now = Date.now(), O = window.OMEGA_OPERATOR, reads = {};
    try{ var r1 = window.OMEGA_MREAD.state().reads || {}; Object.keys(r1).forEach(function(k){ reads[k] = r1[k]; }); }catch(e){}
    try{ var r2 = window.OMEGA_DPLAN.state().reads || {}; Object.keys(r2).forEach(function(k){ if(!reads[k] || (r2[k] && r2[k].at > reads[k].at)) reads[k] = r2[k]; }); }catch(e){}
    var J = O && O.jobs ? jobsCheck(O.jobs(), (O.state() || {}).jobs, now) : [], R = readsCheck(reads, now), bot = load('omega_rguard_bot_v1'), T = load(KT) || {}, btc = btcPrice();
    if(bot && btc && !(T.btc0 > 0)){ T = { t0:now, btc0:btc, eq0:bot.eq }; save(KT, T); }
    var bad = J.filter(function(j){ return j.status === 'overdue' || j.status === 'failing'; }), badR = R.filter(function(r){ return !r.ok; });
    state.last = { at:now, jobs:J, reads:R, bad:bad, badR:badR, base:baseline(bot, T, btc), stress:stress(bot) };
    var key = bad.map(function(j){ return j.id; }).concat(badR.map(function(r){ return r.sym; })).join(',');
    if(key && (T.told !== key || now - (T.toldAt || 0) > 6*H)){ T.told = key; T.toldAt = now; save(KT, T); try{ if(typeof Notification !== 'undefined' && Notification.permission === 'granted') new Notification('OMEGA data check: ' + (bad.length + badR.length) + ' problem' + (bad.length + badR.length === 1 ? '' : 's'), { body:'Open the Analysis page to see which feed is late or wrong.' }); }catch(e){} }
    render(); return state.last; }
  // ── views ──
  function checkHtml(){ var L = state.last; if(!L) return ''; var ok = !L.bad.length && !L.badR.length, h = '<div class="dp-card"><h3 class="dp-h">Data check</h3>';
    h += '<p class="dp-p ' + (ok ? 'up' : 'dn') + '"><b>' + (ok ? 'Everything checked is live and consistent.' : (L.bad.length + L.badR.length) + ' problem' + (L.bad.length + L.badR.length === 1 ? '' : 's') + ' found.') + '</b> ' + L.jobs.filter(function(j){ return j.status === 'fresh'; }).length + ' of ' + L.jobs.length + ' Autopilot jobs fresh; ' + L.reads.filter(function(r){ return r.ok; }).length + ' of ' + L.reads.length + ' markets read with current candles and sane prices.</p>';
    if(L.bad.length) h += '<table class="mr-tab"><tr><th>Late or failing</th><th>Last run</th></tr>' + L.bad.map(function(j){ return '<tr><td>' + esc(j.label) + '<br><span class="hint">' + esc(j.result.slice(0, 120)) + '</span></td><td class="dn">' + esc(j.status) + ', ' + ago(j.age) + '</td></tr>'; }).join('') + '</table>';
    if(L.badR.length) h += '<table class="mr-tab"><tr><th>Market</th><th>Problem</th></tr>' + L.badR.map(function(r){ return '<tr><td>' + esc(r.sym.replace('USDT', '')) + '</td><td class="dn">' + esc(r.issues.join('; ')) + '</td></tr>'; }).join('') + '</table>';
    var never = L.jobs.filter(function(j){ return j.status === 'never run'; }).length, off = L.jobs.filter(function(j){ return j.status === 'off'; }).length;
    if(never || off) h += '<p class="hint">' + (never ? never + ' job' + (never === 1 ? ' has' : 's have') + ' not run yet (normal right after opening). ' : '') + (off ? off + ' switched off on the Autopilot page.' : '') + '</p>';
    h += '<p class="hint">Checked ' + ago(Date.now() - L.at) + '. A candle older than 2 hours means a feed stopped; a futures price more than 0.5% from the spot index means something is off.</p></div>'; return h; }
  function baseHtml(){ var L = state.last; if(!L) return ''; var B = L.base, S = L.stress, pc = function(x){ return (x >= 0 ? '+' : '') + (x*100).toFixed(2) + '%'; }, h = '<div class="dp-card"><h3 class="dp-h">Is the bot worth it?</h3>';
    h += B ? '<table class="mr-tab"><tr><td>Growth Bot since ' + new Date(B.since).toISOString().slice(0, 10) + '</td><td><b class="' + (B.bot >= 0 ? 'up' : 'dn') + '">' + pc(B.bot) + '</b></td></tr><tr><td>Holding BTC over the same time</td><td>' + pc(B.btc) + '</td></tr><tr><td>Cash</td><td>0.00%</td></tr></table><p class="dp-p">' + (B.beats ? 'So far the signals beat simply holding BTC.' : 'So far simply holding BTC did better: the signals have not yet added anything.') + ' Early weeks prove nothing either way.</p>' : '<p class="hint">The baseline starts the first time BTC has been read while the bot exists.</p>';
    h += S && S.n ? '<table class="mr-tab"><tr><th>Fills</th><th>Bot ends at</th></tr><tr><td>As recorded</td><td>' + S.base.toFixed(2) + '</td></tr><tr><td>+0.05% a side worse</td><td>' + S.cons.toFixed(2) + '</td></tr><tr><td>+0.15% a side worse</td><td>' + S.hard.toFixed(2) + '</td></tr></table><p class="dp-p"><b>' + esc(S.word) + '.</b></p>' : '<p class="hint">Fill stress: no closed bot trades to test yet.</p>';
    return h + '</div>'; }
  function render(){ var a = el('truthBody'), b = el('truthRgBody'); if(a) a.innerHTML = checkHtml(); if(b) b.innerHTML = baseHtml(); }
  var JOB = { id:'truth', lane:'live', prio:1, label:'Data check: every feed live, prices sane; the bot against holding BTC and worse fills', what:'Every 30 minutes: finds late or failing Autopilot jobs, stale candles and futures prices far from the spot index (notifies once every 6 hours), and compares the Growth Bot with holding BTC and with worse fills.', every:30*60e3,
    run: async function(){ var L = run(); return (L.bad.length + L.badR.length ? (L.bad.length + L.badR.length) + ' problem(s): ' + L.bad.map(function(j){ return j.id + ' ' + j.status; }).concat(L.badR.map(function(r){ return r.sym + ' ' + r.issues[0]; })).join('; ') : 'All checked feeds live and consistent') + '.'; } };
  function register(){ var O = window.OMEGA_OPERATOR; if(!O || !O.jobs) return false; var J = O.jobs(); if(!J.some(function(x){ return x.id === JOB.id; })) J.push(JOB); return true; }
  if(!register()){ var tries = 0, iv = setInterval(function(){ if(register() || ++tries > 20) clearInterval(iv); }, 3000); }
  var seen = {}; setInterval(function(){ ['truthBody', 'truthRgBody'].forEach(function(id){ var h = el(id), vis = !!(h && h.offsetParent !== null); if(vis && !seen[id]) run(); seen[id] = vis; }); }, 1500);
  window.OMEGA_TRUTH = { run:run, render:render, JOB:JOB, state:function(){ return state; }, _:{ jobsCheck:jobsCheck, readsCheck:readsCheck, baseline:baseline, stress:stress } };
})();
</script>
