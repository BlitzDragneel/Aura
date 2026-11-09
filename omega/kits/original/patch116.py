"""v6.5.116: one Autopilot that runs the app by itself. CREED's engine is byte-identical.
 1. One scheduler: the job runner (OMEGA_OPERATOR). OMEGA_AUTOPILOT keeps its paper trading and risk governor, but no
    longer runs its own 60 s timer when the runner exists: the runner's new job "paper" calls it every minute. Other own
    timers moved into the runner too: the Brain's daily reflection (job "reflect"), the Forex board's 20 s and the bots
    feed's 2 min page timers (jobs "fxboard", "botsfeed").
 2. Audit (what each job feeds). Kept: intel (Market Intelligence, Home), scanner (CREED Scanner, Home), positioning
    (Positioning Desk, Live data), live (Live Market Data), journal (Journal, Brain), reason (Brain ledger, Signals), desk
    (CREED desk, Home), analysis (Charts scan), bots (in-app bots), health (self-test, storage), panic, climax (Signals),
    mread, dplan (Market Read, Charts), rguard (Risk Guard), cockpit (Charts), truth (data check). Back in the runner because
    a kept page reads them: forecast (Brain prediction scorecard and range forecasts) and reflect (Brain "What it has
    learned about itself"). Retired for good (their pages left in v6.5.109; nothing kept reads them): deep (3-year
    downloads), creed (replay over downloaded history), patterns, topup, lab, edge, context, entry, council. Their runner
    state entries are dropped; every stored result (history, replays, lab results) stays in storage untouched.
 3. New jobs: fxboard (1 min while the board is open, else 15 min), botsfeed (2 min while Bots or Home is open, else 15),
    scouts (/scouts?speed=fast, 15 min), academy (catalog, daily), connections (30 min: Live API /health, token present and
    accepted, Binance reachable or OKX in use, Twelve Data key or the Live API fallback).
 4. Runs itself: the Autopilot is ON on first launch (flag omega_selfrun116; switching it off later is respected), comes
    back after any reload or crash (its switch is stored), catches up missed runs on open one job per lane (most overdue
    first, never all at once), backs off on errors (5 min doubling to 6 h, as before). Heavy jobs (forecast, reflect,
    journal) run only while the tab is visible and the device is charging (or the battery is unknown, as on desktops).
 5. "OMEGA is running itself" card on Home and the Autopilot page: on/off, jobs on, last and next run, problems with a
    one-tap fix (no token -> Settings, server asleep -> retry, Binance down -> OKX in use, failing job -> retry), a first-run
    checklist (server, token, theme, install, Autopilot) completed by itself where it can, the plain truth that a browser
    app runs only while open (24/7 = laptop Station and cloud bots, About link) and "Keep screen on" (Wake Lock).
usage: python3 patch116.py <v6.5.115> <out>
"""
import sys, re, datetime
src, dst = sys.argv[1], sys.argv[2]; s = open(src, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:140])
    s = s.replace(a, b)


# 1-2. runner: retired list, forecast and reflect back, the paper core as a job, heavy-lane gate
rep("  JOBS = JOBS.filter(function(j){ return ['deep','creed','patterns','topup','lab','edge','context','entry','forecast','reflect','council'].indexOf(j.id) < 0; });",
    "  // v6.5.116: forecast and reflect are back (the Brain page reads them); the rest stay retired and leave the runner's state\n"
    "  var RETIRED = ['deep','creed','patterns','topup','lab','edge','context','entry','council'];\n"
    "  JOBS = JOBS.filter(function(j){ return RETIRED.indexOf(j.id) < 0; });\n"
    "  (function(){ var n = 0; RETIRED.concat(['backtests','explore','portfolio','workshop','harvest','r12','btctrend','wide','edgelab','bdesk','mprof','mwatch','mwdays','goldh','autoexp']).forEach(function(id){ if(st.jobs && st.jobs[id]){ delete st.jobs[id]; n++; } }); if(n) try{ save(); }catch(e){} })();\n"
    "  JOBS.push({ id:'paper', lane:'live', prio:5, label:'Paper trading and risk governor', what:'Every minute: the Autopilot\\u2019s own cycle (revalidation of conditions, paper trades that pass the risk governor when that switch is on). No real orders.', every:60e3,\n"
    "    run: async function(){ var A = window.OMEGA_AUTOPILOT; if(!A || !A.tick) return 'Autopilot core not available.'; await A.tick(); var c = A.cfg ? A.cfg() : {}; return c.trade ? 'Paper trading on; governor checked.' : 'Conditions revalidated (paper trading is switched off).'; } });")
rep("""    { id:'paper', label:'Paper trading', what:'Takes OMEGA signals that pass the risk governor (separate switch). No real orders.', last:function(){ var c = safe(function(){ return window.OMEGA_AUTOPILOT.book().closed; }) || []; return c.length ? c[c.length-1].closedAt || null : null; }, every:null }
""", "")
rep("      if(k === 'heavy' && window.OMEGA_CALM && !window.OMEGA_CALM.heavyOk()) return;",
    "      if(k === 'heavy' && window.OMEGA_CALM && !window.OMEGA_CALM.heavyOk()) return;\n"
    "      if(k === 'heavy' && window.OMEGA_SELFRUN && !window.OMEGA_SELFRUN.heavyOk()) return;   // v6.5.116: visible tab, charging (or unknown)")
rep("  function start(){ if(timer) return; timer = setInterval(function(){ if(!document.hidden) tick(); }, 60e3); }",
    "  function start(){ if(timer || window.OMEGA_OPERATOR) return; timer = setInterval(function(){ if(!document.hidden) tick(); }, 60e3); }   // v6.5.116: the job runner drives it (job \"paper\")")
rep("    setInterval(function(){ if(document.hidden) return; var l = lsGet('omega_reflect_last_v1', 0); if(Date.now() - l > 24*3600e3) try{ reflect(); }catch(e){} }, 3600e3);\n",
    "    // v6.5.116: the daily reflection is the runner's job \"reflect\"\n")
rep("    setInterval(tick, 20000); setInterval(tickFeed, 120000);\n",
    "    // v6.5.116: refreshed by the Autopilot's jobs \"fxboard\" and \"botsfeed\" (one scheduler)\n")
rep("    fx:{ list:function(){ return LIST; }, state:function(){ return FX; }, load:loadBoard, render:renderFx, open:openOnCharts },",
    "    fx:{ list:function(){ return LIST; }, state:function(){ return FX; }, load:loadBoard, render:renderFx, open:openOnCharts }, tick:tick, tickFeed:tickFeed, active:active,")

# 5. hosts
rep('      <div id="homeBotsFeed" class="om-feed om-feed-sm"></div>\n',
    '      <div id="selfRunHome" class="sr-host"></div>\n      <div id="homeBotsFeed" class="om-feed om-feed-sm"></div>\n')
rep('      <div id="autoDeck" class="ad-deck" aria-live="polite"></div>',
    '      <div id="selfRunAuto" class="sr-host"></div>\n      <div id="autoDeck" class="ad-deck" aria-live="polite"></div>')

CSS = r'''<style id="selfRunCss">/* v6.5.116: OMEGA is running itself */
.sr-card{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:16px;margin:0 0 14px}
.sr-top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}.sr-top h3{margin:0;font-size:15px;color:var(--text);display:flex;align-items:center;gap:8px}
.sr-dot{width:9px;height:9px;border-radius:50%;background:var(--text-dim)}.sr-dot.on{background:var(--bull);box-shadow:0 0 0 4px color-mix(in srgb,var(--bull) 16%,transparent)}.sr-dot.warn{background:var(--amber)}
.sr-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 0}.sr-stats div{background:var(--panel2);border-radius:10px;padding:8px 10px;min-width:0}.sr-stats b{display:block;font-size:15px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sr-stats span{font-size:11px;color:var(--text-dim)}
.sr-list{list-style:none;margin:0;padding:0}.sr-list li{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 0;border-top:1px solid var(--border);font-size:13px}.sr-list li:first-child{border-top:0}
.sr-list li span{min-width:0}.sr-list li .btn-ghost,.sr-list li .btn-outline{white-space:nowrap;flex:none;padding:6px 12px}.sr-ok{color:var(--bull);font-weight:600;white-space:nowrap}.sr-todo{color:var(--amber);font-weight:600;white-space:nowrap}
.sr-note{font-size:12.5px;color:var(--text-dim);line-height:1.55;margin:10px 0 0}.sr-h{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim);margin:12px 0 4px}
</style>
'''
JS = r'''<script>/* ═══ OMEGA RUNS ITSELF (v6.5.116) ═══
   One scheduler: the job runner (OMEGA_OPERATOR). This adds the jobs for the Live API features, the connections check,
   the first-run switch-on, the heavy-job gate (visible tab, charging or unknown battery) and the status card. */
(function(){
  'use strict';
  var KEY = 'omega_selfrun_v1', FLAG = 'omega_selfrun116';
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function lsGet(k, d){ try{ var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); }catch(e){ return d; } }
  function lsSet(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  var S = lsGet(KEY, null) || {}; S.conn = S.conn || null; S.hideCheck = !!S.hideCheck;
  function save(){ lsSet(KEY, S); }
  function L(){ return window.OMEGA_LAPI; } function O(){ return window.OMEGA_OPERATOR; } function A(){ return window.OMEGA_AUTOPILOT; }
  function active(p){ var e = el('page-' + p); return !!(e && e.classList.contains('active')); }
  function visible(){ return !document.hidden; }
  // ── heavy jobs: visible tab, and charging (or a battery the browser does not report, as on most desktops) ──
  var bat = null; try{ if(navigator.getBattery) navigator.getBattery().then(function(b){ bat = b; }, function(){}); }catch(e){}
  function heavyOk(){ if(!visible()) return false; return !bat || !!bat.charging; }
  function heavyWhy(){ return !visible() ? 'the tab is hidden' : (bat && !bat.charging ? 'on battery: waits for the charger' : ''); }
  async function timed(url, ms){ var c = typeof AbortController !== 'undefined' ? new AbortController() : null, t = setTimeout(function(){ try{ c && c.abort(); }catch(e){} }, ms || 12000);
    try{ var r = await fetch(url, c ? { signal:c.signal, cache:'no-store' } : { cache:'no-store' }); return r.ok; }catch(e){ return false; } finally{ clearTimeout(t); } }
  async function connections(){ var c = { at:Date.now() }, LA = L();
    try{ var h = LA ? await LA.get('/health', 70000) : null; c.server = !!(h && h.ok); c.version = h && h.version; c.serverTD = !!(h && h.twelvedata_key); }catch(e){ c.server = false; c.serverErr = String(e && e.message || e); }
    c.token = !!(LA && LA.token());
    if(c.token && c.server){ try{ await LA.get('/fx/quote?symbol=EURUSD', 30000); c.tokenOk = true; }catch(e){ c.tokenOk = false; c.tokenErr = String(e && e.message || e); } }
    c.binance = await timed('https://data-api.binance.vision/api/v3/ping', 10000);
    c.okx = c.binance ? null : await timed('https://www.okx.com/api/v5/public/time', 10000);
    var td = ''; try{ td = localStorage.getItem('omega_td_key') || ''; }catch(e){} c.tdKey = !!td; c.forex = c.tdKey ? 'twelvedata' : (c.tokenOk ? 'liveapi' : 'none');
    S.conn = c; save(); draw();
    var p = []; p.push('Live API ' + (c.server ? 'up' : 'not reachable')); p.push(c.token ? (c.tokenOk ? 'token accepted' : c.tokenOk === false ? 'token refused' : 'token not checked') : 'no token');
    p.push(c.binance ? 'Binance reachable' : c.okx ? 'Binance down, OKX in use' : 'Binance and OKX not reachable'); p.push('forex via ' + (c.forex === 'twelvedata' ? 'Twelve Data' : c.forex === 'liveapi' ? 'the Live API' : 'nothing yet (no key, no token)'));
    if(!c.binance && !c.okx && !c.server) return { error:'no data source answered (offline?)' };
    return p.join('; ') + '.'; }
  var JOBS = [
    { id:'fxboard', lane:'live', prio:3, label:'Forex board quotes', what:'Live bid/ask for the Forex board from the Live API: every minute while the board is open, every 15 minutes otherwise.',
      every:function(){ return active('forex') && visible() ? 60e3 : 15*60e3; },
      run:async function(){ var LA = L(); if(!LA || !LA.on()) return { skip:true, text:'no Live API token (Settings > Data & Keys)', retryIn:30*60e3 };
        await LA.fx.load(true); var F = LA.fx.state(); if(F.err) return { error:F.err }; return 'Quotes for ' + Object.keys(F.data[F.group] || {}).length + ' ' + F.group + '.'; } },
    { id:'botsfeed', lane:'live', prio:3, label:'Bots feed', what:'The 24/7 paper bot and the scouts from the Live API: every 2 minutes while Bots or Home is open, every 15 minutes otherwise.',
      every:function(){ return (active('bot') || active('command')) && visible() ? 120e3 : 15*60e3; },
      run:async function(){ var LA = L(); if(!LA || !LA.on()) return { skip:true, text:'no Live API token', retryIn:30*60e3 };
        await LA.feed.load(true); var B = LA.feed.state(); if(B.err) return { error:B.err }; var pb = (B.j || {}).paper_bot || {};
        return 'Paper bot: ' + (pb.open_positions || []).length + ' open, ' + (pb.resting_orders || []).length + ' resting.'; } },
    { id:'scouts', lane:'live', prio:2, label:'Fast scouts reading', what:'The fast scouts’ reading from the latest closed 15-minute candle (/scouts?speed=fast). Forecast information, never an order.', every:15*60e3,
      run:async function(){ var LA = L(); if(!LA || !LA.on()) return { skip:true, text:'no Live API token', retryIn:30*60e3 };
        var j = await LA.get('/scouts?speed=fast', 60000); var rows = (j && (j.rows || j.latest || j.predictions)) || []; S.scouts = { at:Date.now(), n:Array.isArray(rows) ? rows.length : 0 }; save(); return 'Read ' + S.scouts.n + ' coin(s).'; } },
    { id:'academy', lane:'live', prio:1, label:'Academy catalog', what:'Refreshes the course list from the server once a day (lessons stay readable offline).', every:24*3600e3,
      run:async function(){ var AC = window.OMEGA_ACADEMY; if(!AC || !AC.load) return 'Academy not available.'; await AC.load(true); var st = AC.state(); return st.src === 'server' ? 'Course loaded from the server.' : (st.err || 'Built-in lessons in use.'); } },
    { id:'connections', lane:'live', prio:4, label:'Connections check', what:'Every 30 minutes: the Live API answers, the token is present and accepted, Binance is reachable (or OKX is used), forex has Twelve Data or the Live API.', every:30*60e3,
      run:connections } ];
  function register(){ var Op = O(); if(!Op || !Op.jobs) return false; var J = Op.jobs(); JOBS.forEach(function(j){ if(!J.some(function(x){ return x.id === j.id; })) J.push(j); }); return true; }
  // ── first launch: switch the Autopilot on once ──
  function firstRun(){ var a = A(); if(!a) return; try{ if(!localStorage.getItem(FLAG)){ if(a.cfg && !a.cfg().brain && a.setBrain) a.setBrain(true); localStorage.setItem(FLAG, String(Date.now())); } }catch(e){} }
  // ── the card ──
  function ago(t){ if(!t) return '—'; var m = Math.round((Date.now() - t)/60000); return m < 1 ? 'just now' : m < 90 ? m + ' min ago' : Math.round(m/60) + ' h ago'; }
  function inT(ms){ if(ms <= 0) return 'now'; var m = Math.round(ms/60000); return m < 1 ? 'in <1 min' : m < 90 ? 'in ' + m + ' min' : 'in ' + Math.round(m/60) + ' h'; }
  function stats(){ var Op = O(); if(!Op) return null; var st = Op.state(), jobs = Op.jobs(), on = jobs.filter(function(j){ var x = st.jobs[j.id]; return !x || x.enabled !== false; });
    var last = null, next = null, fails = [];
    on.forEach(function(j){ var x = st.jobs[j.id] || {}; if(x.last && (!last || x.last > last.t)) last = { t:x.last, j:j };
      var due = x.retryAt && x.retryAt > Date.now() ? x.retryAt : (x.last || 0) + Op.everyOf(j); if(!next || due < next.t) next = { t:due, j:j };
      if(x.fails) fails.push(j); });
    return { n:on.length, all:jobs.length, last:last, next:next, fails:fails }; }
  function problems(){ var out = [], c = S.conn, a = A(), on = !!(a && a.cfg && a.cfg().brain), LA = L(), st = stats();
    if(!on) out.push({ t:'The Autopilot is off: nothing refreshes by itself.', b:'Switch on', f:'on' });
    if(LA && !LA.token()) out.push({ t:'No Live API token: no forex board, no bots feed.', b:'Open Settings', f:'settings' });
    else if(c && c.tokenOk === false) out.push({ t:'The Live API refused the token.', b:'Open Settings', f:'settings' });
    if(c && !c.server) out.push({ t:'Live API not reachable (a sleeping server takes about a minute to wake).', b:'Check again', f:'conn' });
    if(c && !c.binance && c.okx) out.push({ t:'Binance not reachable: switched to OKX automatically.', b:'', f:'' });
    if(c && !c.binance && !c.okx) out.push({ t:'Neither Binance nor OKX answers: are you offline?', b:'Check again', f:'conn' });
    if(c && c.forex === 'none') out.push({ t:'Forex has no source: add a Twelve Data key or the Live API token.', b:'Open Settings', f:'settings' });
    if(st && st.fails.length) out.push({ t:st.fails.length + ' job(s) hit a problem and back off: ' + st.fails.slice(0, 3).map(function(j){ return j.label; }).join(', ') + '.', b:'Retry now', f:'retry' });
    var hw = heavyWhy(); if(on && hw && /battery/.test(hw)) out.push({ t:'Heavy jobs (forecasts, reflection, journal review) wait: ' + hw + '.', b:'', f:'' });
    return out; }
  function checklist(){ var c = S.conn || {}, a = A(), I = window.OMEGA_INSTALL, ist = I && I.state ? I.state() : {};
    return [ { t:'Server reachable', ok:!!c.server, f:'conn', b:'Check' }, { t:'Live API token', ok:!!(L() && L().token() && c.tokenOk !== false), f:'settings', b:'Add token' },
      { t:'Theme', ok:true, note:document.documentElement.getAttribute('data-theme') === 'heaven' ? 'Heaven' : 'your choice' },
      { t:'Installed as an app', ok:!!ist.installed, f:'install', b:'Install' }, { t:'Autopilot on', ok:!!(a && a.cfg && a.cfg().brain), f:'on', b:'Switch on' } ]; }
  function cardHtml(where){ var a = A(), on = !!(a && a.cfg && a.cfg().brain), st = stats() || { n:0, all:0 }, pr = problems(), ck = checklist(), todo = ck.filter(function(x){ return !x.ok; });
    var h = '<div class="sr-card" data-sr="' + where + '"><div class="sr-top"><h3><i class="sr-dot ' + (on ? (pr.length ? 'warn' : 'on') : '') + '"></i>' + (on ? 'OMEGA is running itself' : 'OMEGA is paused') + '</h3>' +
      '<button class="btn-ghost" type="button" data-srf="' + (on ? 'off' : 'on') + '">' + (on ? 'Pause' : 'Switch on') + '</button></div>' +
      '<div class="sr-stats"><div><b>' + st.n + ' of ' + st.all + '</b><span>jobs on</span></div><div><b>' + esc(st.last ? ago(st.last.t) : '—') + '</b><span>' + esc(st.last ? st.last.j.label : 'last run') + '</span></div>' +
      '<div><b>' + esc(on && st.next ? inT(st.next.t - Date.now()) : '—') + '</b><span>' + esc(on && st.next ? st.next.j.label : 'next run') + '</span></div></div>';
    if(pr.length) h += '<ul class="sr-list">' + pr.map(function(p){ return '<li><span>' + esc(p.t) + '</span>' + (p.b ? '<button class="btn-outline" type="button" data-srf="' + p.f + '">' + esc(p.b) + '</button>' : '') + '</li>'; }).join('') + '</ul>';
    else if(on) h += '<p class="sr-note" style="margin:0">Everything is connected. Jobs run by themselves, catch up after a break one at a time, and back off when a source fails.</p>';
    if(todo.length && !S.hideCheck) h += '<p class="sr-h">Setup check</p><ul class="sr-list">' + ck.map(function(x){ return '<li><span>' + esc(x.t) + (x.note ? ' · ' + esc(x.note) : '') + '</span>' +
        (x.ok ? '<span class="sr-ok">✓ done</span>' : '<button class="btn-outline" type="button" data-srf="' + x.f + '">' + esc(x.b) + '</button>') + '</li>'; }).join('') + '</ul><p class="sr-note"><button class="btn-ghost" type="button" data-srf="hidecheck">Hide the setup check</button></p>';
    h += '<p class="sr-note">A browser app works only while it is open, and a hidden tab is slowed down by the browser. Running 24/7 is done by the laptop Station and the cloud bots (<a href="#" data-srf="about">About › The bots</a>).' +
      (('wakeLock' in navigator) ? ' <button class="btn-ghost" type="button" data-srf="wake">' + (a && a.cfg && a.cfg().wake ? 'Screen stays on ✓' : 'Keep screen on') + '</button>' : '') + '</p></div>';
    return h; }
  function act(f){ var a = A(), Op = O();
    var ST = window.OMEGA_STATUS;   // "When the app opens" (autostart) follows the same switch, so a pause survives a reload
    if(f === 'on' && a && a.setBrain){ a.setBrain(true); try{ ST && ST.setAutostart && ST.setAutostart('autopilot', true); }catch(e){} }
    else if(f === 'off' && a && a.setBrain){ a.setBrain(false); try{ ST && ST.setAutostart && ST.setAutostart('autopilot', false); }catch(e){} }
    else if(f === 'settings'){ window.navigate('settings'); try{ window.switchSettings && window.switchSettings('data'); }catch(e){} setTimeout(function(){ var i = el('liveTokenInput'); if(i) i.scrollIntoView({ block:'center' }); }, 120); }
    else if(f === 'conn' && Op){ Op.runNow('connections'); }
    else if(f === 'retry' && Op){ Op.runAllDue(); }
    else if(f === 'install' && window.OMEGA_INSTALL){ window.OMEGA_INSTALL.open(); }
    else if(f === 'hidecheck'){ S.hideCheck = true; save(); }
    else if(f === 'wake' && a && a.setWake){ a.setWake(!(a.cfg && a.cfg().wake)); }
    else if(f === 'about'){ window.navigate('about'); setTimeout(function(){ var d = Array.prototype.filter.call(document.querySelectorAll('#page-about details.ab-sec'), function(x){ return /The bots/.test(x.querySelector('summary').textContent); })[0]; if(d){ d.open = true; d.scrollIntoView({ block:'start' }); } }, 80); }
    setTimeout(draw, 60); }
  function draw(){ ['selfRunHome', 'selfRunAuto'].forEach(function(id){ var host = el(id); if(!host) return; var pg = host.closest('.page'); if(pg && !pg.classList.contains('active') && host.innerHTML) return;
      var html = cardHtml(id === 'selfRunHome' ? 'home' : 'auto'); if(host.__h === html) return; host.__h = html; host.innerHTML = html;
      Array.prototype.forEach.call(host.querySelectorAll('[data-srf]'), function(b){ b.onclick = function(e){ e.preventDefault(); act(b.getAttribute('data-srf')); }; }); }); }
  function boot(){ register(); firstRun(); draw(); setInterval(function(){ if(!document.hidden) draw(); }, 15000);
    if(!S.conn || Date.now() - S.conn.at > 30*60e3) setTimeout(connections, 3000); }   // the setup check completes itself
  var prevAfter = window.__omegaAfterNav;
  window.__omegaAfterNav = function(p){ try{ if(typeof prevAfter === 'function') prevAfter(p); }catch(e){} if(p === 'command' || p === 'auto') setTimeout(draw, 30); };
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(boot, 0); }); else setTimeout(boot, 0);
  window.OMEGA_SELFRUN = { heavyOk:heavyOk, heavyWhy:heavyWhy, connections:connections, draw:draw, problems:problems, checklist:checklist, state:function(){ return S; }, JOBS:JOBS, act:act, stats:stats };
})();
</script>
'''
rep('</body>', CSS + JS + '</body>')

now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M')
o = re.search(r'v6\.5\.115 (?:·|\\u00b7) build (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC', s).group(1)
for sep in ['·', '\\u00b7']:
    s = s.replace('v6.5.115 ' + sep + ' build ' + o + ' UTC', 'v6.5.116 ' + sep + ' build ' + now + ' UTC')
assert 'v6.5.116 · build' in s and 'v6.5.115 · build' not in s
# wording: research no longer runs in the app (it runs in the repo and the cloud bots)
for a, b in (('Autopilot <span>researches, tests and paper-trades on its own while the app is open</span>',
              'Autopilot <span>watches the markets, refreshes every page and paper-trades on its own while the app is open</span>'),
             ('<p>Autopilot researches, tests and paper-trades on its own while the app is open.</p>',
              '<p>Autopilot watches the markets, refreshes every page and paper-trades on its own while the app is open. Research runs outside the app (progress board).</p>')):
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(dst, 'w', encoding='utf-8').write(s); print('wrote', dst, now, 'size', len(s.encode('utf-8')))
