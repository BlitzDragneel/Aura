<script>/* ═══ MARKET CLOCK (v6.5.79) — when the market moves, the scheduled events ahead, and what research found about each
   (round 17, research/PLAN17.md; descriptive, 165 coins, hourly, 2020 – Oct 2026). Event dates from official sources:
   US CPI from the BLS release schedule (08:30 ET), FOMC statements from the Federal Reserve calendar (14:00 ET; 2027
   tentative). Options expiry: Deribit, Fridays 08:00 UTC (monthly = last Friday). CME crypto futures: Friday 16:00 CT
   close, Sunday 17:00 CT open. Description, not signals. ═══ */
(function(){
  'use strict';
  var DATA = __CLOCK__;
  var H = 3600e3;
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t == null ? '' : t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  // US daylight saving (second Sunday of March to first Sunday of November)
  function nthSunday(y, mo, n){ var d = new Date(Date.UTC(y, mo, 1)), first = (7 - d.getUTCDay()) % 7; return Date.UTC(y, mo, 1 + first + 7*(n - 1)); }
  function usDST(t){ var y = new Date(t).getUTCFullYear(); return t >= nthSunday(y, 2, 2) + 7*H && t < nthSunday(y, 10, 1) + 6*H; }
  function lastFriday(y, mo){ var d = new Date(Date.UTC(y, mo + 1, 0)); var back = (d.getUTCDay() - 5 + 7) % 7; return Date.UTC(y, mo + 1, 0 - back, 8); }
  function upcoming(now){ var out = [], y = new Date(now).getUTCFullYear(), mo = new Date(now).getUTCMonth();
    DATA.cpi.forEach(function(s){ var t = Date.parse(s); if(t > now - H) out.push({ t:t, kind:'cpi', name:'US CPI (inflation) release', what:'The CPI hour moved a median 1.3× a normal hour (5× in 2022). The market rose in 75% of releases against 51% on other weekdays, but fell hard in 2022.' }); });
    DATA.fomc.forEach(function(s){ var t = Date.parse(s); if(t > now - H) out.push({ t:t, kind:'fomc', name:'FOMC statement (Federal Reserve rate decision)', what:'The statement hour moved a median 1.9\u00d7 a normal hour. Across 53 statements the market rose in 70% of these hours (52% on other weekdays), mostly from 2021 to 2024; in 2025\u201326 it averaged flat.' }); });
    for(var k=0; k<3; k++){ var t = lastFriday(y, mo + k); if(t > now - H) out.push({ t:t, kind:'expiry', name:'Monthly options expiry (Deribit, 08:00 UTC)', what:'No distinct effect found: the day after looked like any Friday.' }); }
    var f = Math.ceil(now/(8*H))*8*H; out.push({ t:f, kind:'funding', name:'Funding settlement (every 8 hours)', what:'One of the busier hours. Round 8’s settlement-drift rule did not pass.' });
    var d = new Date(now), fri = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + ((5 - d.getUTCDay() + 7) % 7)), close = fri + (usDST(fri) ? 21 : 22)*H;
    if(close < now) { fri += 7*24*H; close = fri + (usDST(fri) ? 21 : 22)*H; }
    var sun = fri + 2*24*H, open = sun + (usDST(sun + 12*H) ? 22 : 23)*H;   /* Sunday 17:00 Chicago time */
    out.push({ t:close, kind:'cme', name:'CME crypto futures close for the weekend', what:'Weekends are about 20% calmer. The "CME gap fill" was not supported: big weekend moves reversed only half the time (353 weekends).' });
    out.push({ t:open, kind:'cme', name:'CME crypto futures reopen', what:'The next 3 days followed the weekend move slightly rather than reversing it.' });
    return out.filter(function(e){ return e.t > now - H; }).sort(function(a, b){ return a.t - b.t; }); }
  // tags for a moment (used by Market Watch's flight recordings)
  function tags(t){ var out = [], h0 = Math.floor(t/H)*H;
    DATA.cpi.forEach(function(s){ var x = Date.parse(s); if(Math.floor(x/H)*H === h0) out.push('CPI release hour'); });
    DATA.fomc.forEach(function(s){ var x = Date.parse(s); if(Math.floor(x/H)*H === h0) out.push('FOMC statement hour'); });
    var d = new Date(t); if(d.getUTCDay() === 5 && d.getUTCHours() === 8 && lastFriday(d.getUTCFullYear(), d.getUTCMonth()) === h0) out.push('monthly options expiry');
    return out; }
  function until(ms){ if(ms < 0) return 'now'; var m = Math.round(ms/60e3); if(m < 60) return 'in ' + m + ' min'; var h = Math.floor(m/60); if(h < 48) return 'in ' + h + ' h ' + (m % 60) + ' min'; return 'in ' + Math.round(h/24) + ' days'; }
  function when(t){ var d = new Date(t); return d.toUTCString().slice(0, 22) + ' UTC (' + d.toLocaleString([], { weekday:'short', hour:'2-digit', minute:'2-digit' }) + ' your time)'; }
  function render(){ var host = el('clockBody'); if(!host) return; var now = Date.now(), hNow = new Date(now).getUTCHours(), HR = DATA.hours, mx = 0, k;
    for(k=0; k<24; k++) mx = Math.max(mx, HR[k][0]);
    var me = HR[hNow], quiet = me[0] < 1.4, busy = me[0] >= 2.1;
    var bars = '<div style="display:flex;align-items:flex-end;gap:2px;height:70px;margin:8px 0 2px;">' + Array.apply(null, { length:24 }).map(function(_, h){ var v = HR[h][0], ht = Math.max(4, Math.round(64*v/mx));
        return '<div title="' + h + ':00 UTC: 3σ moves in ' + v + '% of hours, volume ' + HR[h][2] + '×" style="flex:1;height:' + ht + 'px;border-radius:2px;background:' + (h === hNow ? 'var(--gold)' : v >= 2.1 ? 'var(--bear)' : v < 1.4 ? 'var(--border)' : 'var(--dim, #8a8f98)') + ';"></div>'; }).join('') + '</div>' +
      '<div style="display:flex;justify-content:space-between;font-size:11px;" class="dim"><span>00</span><span>06</span><span>12</span><span>18</span><span>23 UTC</span></div>';
    var ev = upcoming(now).slice(0, 6);
    var h = '<div class="card" style="margin-bottom:14px;"><h2 style="color:var(--gold);">When the market moves</h2>' +
      '<p class="hint" style="margin-top:0;color:var(--text);"><b>Now: ' + hNow + ':00 UTC</b> (' + new Date(now).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' }) + ' your time). ' + (busy ? 'One of the busiest hours: ' : quiet ? 'A quiet hour: ' : 'An ordinary hour: ') + 'sudden 3σ moves happen in ' + me[0] + '% of these hours, with ' + me[2] + '× normal volume. Busiest are 13:00–16:00 UTC (US open) and 00:00 UTC (daily close); quietest are 03:00–11:00 UTC and weekends.</p>' + bars +
      '<p class="hint" style="margin:4px 0 8px;">Each bar is how often an hour had a 3σ move (165 coins, 2020–2026). Red = busiest, grey = quiet, gold = now.</p>' +
      '<p class="hint" style="margin:6px 0 4px;"><b>Coming up</b></p><ul class="hint" style="margin:0;padding-left:18px;line-height:1.5;">' + ev.map(function(e){ return '<li><b>' + esc(e.name) + '</b> · ' + esc(when(e.t)) + ' · ' + esc(until(e.t - now)) + '<br><span class="dim">' + esc(e.what) + '</span></li>'; }).join('') + '</ul>' +
      '<details style="margin-top:8px;"><summary class="hint" style="cursor:pointer;"><b>What moves a coin’s chart (round 17)</b></summary><ul class="hint" style="margin:6px 0 0;padding-left:18px;line-height:1.5;">' +
      '<li><b>The whole market explains about 60% of a coin’s hourly move</b> (BTC and ETH: 68%). The coin’s own aggressive buying and selling adds about 6 points more. The rest is the coin’s own news and noise. In 2026 the market explained less (45%).</li>' +
      '<li><b>The hour’s biggest movers give a little back the next hour.</b> So do the most aggressively bought coins. The effect is real but smaller than trading fees, and it has faded since 2024.</li>' +
      '<li><b>After a sudden market-wide fall</b> (3σ in an hour) the market rebounded +0.8% over the next 24 hours on average, against +0.13% for an ordinary day. The climax reversal rule rides this rebound through the coins whose fall was already being bought back within the hour.</li>' +
      '<li><b>A coin crashing alone by 8σ or more</b> lagged the market’s rebound by 1.3% over 12 hours. That usually means bad news about the coin itself.</li>' +
      '<li><b>A spike that is sold back within the hour</b> (a 3σ rise closing in the bottom 40% of the hour) kept lagging the market for 3 days (−1.9%, 309 cases). This is a hypothesis being watched, not a rule.</li>' +
      '<li><b>After an ordinary big move nothing follows on average.</b> Volatility stays only slightly higher for the next day.</li>' +
      '<li><b>Events.</b> The CPI and FOMC hours are the biggest scheduled moves (median 1.3× and 1.9× a normal hour). Options expiry shows no distinct effect, and the CME weekend "gap fill" is not supported.</li></ul>' +
      '<p class="hint" style="margin:6px 0 0;">All of this is description from history. Nothing here is a trading signal unless it passes a test.</p></details></div>';
    host.innerHTML = h; }
  function wire(){ var w = el('watchBody'); if(!w) return false; if(!el('clockBody')){ var d = document.createElement('div'); d.id = 'clockBody'; w.parentNode.insertBefore(d, w); } render(); return true; }
  var tries = 0, iv = setInterval(function(){ if(wire() || ++tries > 60) clearInterval(iv); }, 1000); setInterval(render, 60e3);
  window.OMEGA_MARKETCLOCK = { tags:tags, upcoming:upcoming, render:render, DATA:DATA, _:{ usDST:usDST, lastFriday:lastFriday } };
})();
</script>
