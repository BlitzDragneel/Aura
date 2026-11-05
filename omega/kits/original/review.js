<script>/* ═══ EVENTS AND MONTHLY REVIEW (v6.5.94) — the releases ahead where you decide trades, and a month-by-month review ═══
   1. Events ahead: reads the Market Clock's official calendar (US CPI from the BLS schedule, Fed decisions from the Federal
      Reserve calendar) and shows the next ones under Market now (Analysis and Market Read). From 2 hours before to 1 hour
      after a release it warns not to open new trades; the pre-trade check on the Risk Guard says the same. Advice only: the
      Growth Bot's rules stay as plan E17 fixed them.
   2. Monthly review (Risk Guard page): per calendar month, the Growth Bot (trades, result, end equity), the Daily Plan's
      forward record (trades, average and total R), your own logged trades (result, rule breaks and what they cost).
      What earned, what failed and what to keep — from the records, never edited by hand. OMEGA places no orders. */
(function(){
  'use strict';
  var H = 3600e3, BEFORE = 2*H, AFTER = H;
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function load(k, d){ try{ var v = JSON.parse(localStorage.getItem(k) || 'null'); return v && typeof v === 'object' ? v : d; }catch(e){ return d; } }
  function usd(x){ return (x < 0 ? '−' : '') + '$' + Math.abs(x).toFixed(2); }
  // ── events (pure, given the calendar) ──
  function events(D){ D = D || (window.OMEGA_MARKETCLOCK && window.OMEGA_MARKETCLOCK.DATA) || {}; var out = [];
    (D.cpi || []).forEach(function(x){ var t = Date.parse(x); if(t) out.push({ kind:'US inflation (CPI)', at:t }); });
    (D.fomc || []).forEach(function(x){ var t = Date.parse(x); if(t) out.push({ kind:'Fed decision (FOMC)', at:t }); });
    return out.sort(function(a, b){ return a.at - b.at; }); }
  function nextEvents(nowMs, D, n){ nowMs = nowMs || Date.now(); return events(D).filter(function(e){ return e.at + AFTER > nowMs; }).slice(0, n || 3); }
  function eventRisk(nowMs, D){ nowMs = nowMs || Date.now(); var e = events(D).filter(function(x){ return nowMs >= x.at - BEFORE && nowMs <= x.at + AFTER; })[0];
    return e ? { active:true, ev:e, mins:Math.round((e.at - nowMs)/60e3) } : { active:false }; }
  function when(ms, nowMs){ var d = ms - (nowMs || Date.now()), a = Math.abs(d), s = a < H ? Math.round(a/60e3) + ' min' : a < 48*H ? Math.round(a/H) + ' h' : Math.round(a/864e5) + ' days';
    return d >= 0 ? 'in ' + s : s + ' ago'; }
  function riskText(R){ return R.active ? 'Event risk: ' + R.ev.kind + ' ' + (R.mins >= 0 ? 'in ' + R.mins + ' min' : (-R.mins) + ' min ago') + '. Do not open new trades from 2 hours before to 1 hour after a release: spreads widen and stops get run.' : ''; }
  function eventsHtml(nowMs){ nowMs = nowMs || Date.now(); var N = nextEvents(nowMs), R = eventRisk(nowMs);
    if(!N.length) return '';
    return '<div class="dp-card ev-card"><h3 class="dp-h">Events ahead</h3>' + (R.active ? '<p class="ev-warn">' + esc(riskText(R)) + '</p>' : '') +
      '<table class="mr-tab">' + N.map(function(e){ var d = new Date(e.at), tob = new Date(e.at - 4*H); return '<tr><td>' + esc(e.kind) + '</td><td>' + d.toISOString().slice(5, 10) + ' ' + d.toISOString().slice(11, 16) + ' UTC · ' + tob.toISOString().slice(11, 16) + ' Tobago</td><td>' + when(e.at, nowMs) + '</td></tr>'; }).join('') + '</table>' +
      '<p class="hint">From the Market Clock’s official calendar (BLS for CPI, the Federal Reserve for FOMC). These releases move every market at once; the safest trades are opened outside the window from 2 hours before to 1 hour after.</p></div>'; }
  // ── the monthly review (pure, given the records) ──
  function month(ms){ return new Date(ms).toISOString().slice(0, 7); }
  function review(bot, plan, mine){ var M = {};
    function row(m){ return M[m] || (M[m] = { bot:{ n:0, pnl:0, eq:null }, plan:{ n:0, R:0 }, mine:{ n:0, pnl:0, breaks:0, breakPnl:0 } }); }
    ((bot && bot.closed) || []).slice().sort(function(a, b){ return a.at - b.at; }).forEach(function(c){ var r = row(month(c.at)); r.bot.n++; r.bot.pnl += c.pnl; });
    if(bot && bot.closed){ var eq = bot.start0 || 100; bot.closed.slice().sort(function(a, b){ return a.at - b.at; }).forEach(function(c){ eq += c.pnl; row(month(c.at)).bot.eq = eq; }); }
    ((plan && plan.trades) || []).forEach(function(t){ var r = row(month(t.h*H)); r.plan.n++; r.plan.R += t.R; });
    ((mine && mine.closed) || []).forEach(function(c){ var r = row(month(c.at)); r.mine.n++; r.mine.pnl += c.pnl; if(c.breach){ r.mine.breaks++; r.mine.breakPnl += c.pnl; } });
    return Object.keys(M).sort().reverse().map(function(m){ return Object.assign({ month:m }, M[m]); }); }
  function verdictLine(r){ var parts = [];
    if(r.bot.n) parts.push('the bot ' + (r.bot.pnl >= 0 ? 'earned ' : 'lost ') + usd(Math.abs(r.bot.pnl)));
    if(r.plan.n) parts.push('the Daily Plan averaged ' + (r.plan.R/r.plan.n >= 0 ? '+' : '') + (r.plan.R/r.plan.n).toFixed(2) + 'R');
    if(r.mine.breaks) parts.push('your rule breaks ' + (r.mine.breakPnl < 0 ? 'cost ' + usd(-r.mine.breakPnl) : 'made ' + usd(r.mine.breakPnl) + ' (luck, not a reason to repeat them)'));
    else if(r.mine.n) parts.push('you kept every rule');
    return parts.length ? parts.join('; ') + '.' : 'No closed trades.'; }
  function reviewHtml(){ var rows = review(load('omega_rguard_bot_v1', null), load('omega_dplan_v1', null), load('omega_rguard_mine_v1', null)), h = '<div class="dp-card"><h3 class="dp-h">Monthly review</h3>';
    if(!rows.length) return h + '<p class="hint">Nothing to review yet: the first month appears once trades close. Each month shows what earned, what failed and whether the rules were kept — straight from the records.</p></div>';
    h += '<table class="mr-tab"><tr><th>Month</th><th>Growth Bot</th><th>Daily Plan</th><th>Your trades</th></tr>' + rows.map(function(r){
      return '<tr><td><b>' + r.month + '</b></td><td>' + (r.bot.n ? r.bot.n + ' · ' + usd(r.bot.pnl) + (r.bot.eq != null ? '<br><span class="hint">ends ' + r.bot.eq.toFixed(2) + '</span>' : '') : '—') + '</td><td>' + (r.plan.n ? r.plan.n + ' · ' + (r.plan.R >= 0 ? '+' : '') + r.plan.R.toFixed(1) + 'R' : '—') + '</td><td>' + (r.mine.n ? r.mine.n + ' · ' + usd(r.mine.pnl) + (r.mine.breaks ? '<br><span class="dn">' + r.mine.breaks + ' rule break' + (r.mine.breaks === 1 ? '' : 's') + '</span>' : '') : '—') + '</td></tr><tr><td colspan="4" class="hint">' + esc(verdictLine(r)) + '</td></tr>'; }).join('') + '</table>';
    return h + '<p class="hint">Keep what earns over months, not days; retire what fails its fixed test; never fix a rule break by changing the rule.</p></div>'; }
  function css(){ if(el('evCss')) return; var st = document.createElement('style'); st.id = 'evCss'; st.textContent = '.ev-warn{background:rgba(255,77,94,.14);color:var(--bear);border-radius:8px;padding:8px 10px;font-size:13px;font-weight:600;margin:0 0 8px;}'; document.head.appendChild(st); }
  function render(){ css(); ['evAnaBody', 'evBody'].forEach(function(id){ var h = el(id); if(h) h.innerHTML = eventsHtml(); }); var r = el('reviewBody'); if(r) r.innerHTML = reviewHtml(); }
  var t = 0, iv = setInterval(function(){ if(el('evAnaBody') || el('evBody') || el('reviewBody')){ clearInterval(iv); render(); setInterval(render, 60e3); } else if(++t > 60) clearInterval(iv); }, 1000);
  window.OMEGA_REVIEW = { render:render, eventRisk:eventRisk, riskText:riskText, nextEvents:nextEvents, _:{ events:events, review:review, verdictLine:verdictLine, eventsHtml:eventsHtml, reviewHtml:reviewHtml } };
})();
</script>
