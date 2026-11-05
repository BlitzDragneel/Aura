<script>/* ═══ MARKET PROFILES (v6.5.85, v6.5.86) — six markets studied one by one (plan E5), both directions (plan E7), and a forward record of when they move (plan E6) ═══
   v6.5.86: 'Both directions' on every profile (plan E7, md5 4601481e…, edge/anatomy.py → plans/E7_anatomy.json): rising vs falling
   hours and days, tails, the biggest hours and 24-hour moves with dates, swings (10%+ coins, 3%+ gold), volatility after
   big drops vs big rises, where big moves happen, the long and short side of plan E5's two-sided rules, and four short-only
   rules (blow-off, failed breakout, downtrend US hours, breakdown in a downtrend): NONE passed on any market.
   Gold (XAU/USD) and DOGE, LINK, LTC, ADA, AVAX. Every figure on these profiles comes from plan E5 (md5 1e94469c…,
   edge/dossier.py → plans/E5_dossiers.json): hourly data, gold Jul 2020 – Oct 2026 (Twelve Data), coins Jan 2020 – Oct 2026
   (Binance spot, 15-minute files resampled to hours). Plan E5 also tested seven simple rules per market, each chosen on
   2020–2023 and judged once on 2024–2026: NONE passed. The one pattern common to all six — gains outside US hours, a drift
   down during them, before costs — was found on data already used, so plan E6 (md5 893c6251…) records it forward from
   21 Oct 2026, using Binance perpetual hourly closes, and judges it once after 26 weeks. It is a timing fact being checked,
   not a trading rule. "What moves it" is general knowledge up to mid-2026, not live news. OMEGA places no orders. */
(function(){
  'use strict';
  var H = 3600e3, CFG = 'omega_mprof_cfg_v1', REC = 'omega_mprof_e6_v1', START_DAY = Date.UTC(2026, 9, 21)/864e5, FAPI = 'https://fapi.binance.com';
  var DATA = __DATA__;
  var TEXT = __TEXT__;
  var DATA2 = __DATA2__;
  var ORDER = ['XAUUSD', 'DOGEUSDT', 'LINKUSDT', 'LTCUSDT', 'ADAUSDT', 'AVAXUSDT'], LIVE = { XAUUSD:'XAUUSDT' };
  var SESS = [['Asia', 0, 8], ['London', 8, 13], ['US', 13, 21], ['Late', 21, 24]];
  var state = { live:{}, busy:false, msg:'', at:0 };
  function el(id){ return document.getElementById(id); }
  function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); }
  function cfg(){ try{ var v = JSON.parse(localStorage.getItem(CFG) || 'null'); if(v && DATA[v.sel]) return v; }catch(e){} return { sel:'XAUUSD', acct:100, risk:1 }; }
  function setCfg(v){ try{ localStorage.setItem(CFG, JSON.stringify(v)); }catch(e){} }
  function rec(){ try{ var v = JSON.parse(localStorage.getItem(REC) || 'null'); if(v && v.days) return v; }catch(e){} return { days:{}, gaps:0 }; }
  function setRec(v){ try{ localStorage.setItem(REC, JSON.stringify(v)); }catch(e){} }
  function sgn(x, d){ return (x > 0 ? '+' : '') + x.toFixed(d == null ? 1 : d); }
  function sessOf(h){ for(var i=0; i<SESS.length; i++) if(h >= SESS[i][1] && h < SESS[i][2]) return SESS[i][0]; return ''; }
  function tob(h){ return ((h - 4 + 24) % 24); }
  function live(sym){ return LIVE[sym] || sym; }
  // ── live data: last 1,000 hourly closes per market (Binance perpetuals, keyless) ──
  async function getKl(sym){ var r = await fetch(FAPI + '/fapi/v1/klines?symbol=' + live(sym) + '&interval=1h&limit=1000'); if(!r.ok) throw new Error('HTTP ' + r.status); var d = await r.json(); if(!Array.isArray(d)) throw new Error('bad answer'); return d; }
  function digest(sym, kl){ var nowH = Math.floor(Date.now()/H), rows = kl.filter(function(k){ return Math.floor(+k[0]/H) < nowH; }).map(function(k){ return { h:Math.floor(+k[0]/H), o:+k[1], hi:+k[2], lo:+k[3], c:+k[4] }; }).filter(function(x){ return x.c > 0 && x.hi >= x.lo; });
    if(rows.length < 30) return null; var n = rows.length, atr = null;
    for(var i=Math.max(1, n - 200); i<n; i++){ var pc = rows[i-1].c, tr = Math.max(rows[i].hi - rows[i].lo, Math.abs(rows[i].hi - pc), Math.abs(rows[i].lo - pc)); atr = atr == null ? tr : atr + (tr - atr)/14; }
    var last = rows[n-1], d24 = rows[Math.max(0, n - 25)], hi = -Infinity, lo = Infinity; rows.slice(-24).forEach(function(x){ hi = Math.max(hi, x.hi); lo = Math.min(lo, x.lo); });
    // plan E6: whole UTC days from 21 Oct 2026, outside-US and US sums of hourly log returns
    var R = rec(), days = R.days[sym] || (R.days[sym] = {}), byDay = {};
    for(i=1; i<n; i++){ if(rows[i].h - rows[i-1].h !== 1) continue; var d = Math.floor(rows[i].h/24), hh = rows[i].h % 24, lr = Math.log(rows[i].c/rows[i-1].c); if(d < START_DAY || d >= Math.floor(nowH/24)) continue;
      var b = byDay[d] || (byDay[d] = [0, 0, 0, 0]); if(hh >= 13 && hh <= 20){ b[1] += lr; b[3]++; } else { b[0] += lr; b[2]++; } }
    Object.keys(byDay).forEach(function(d){ var b = byDay[d]; if(b[2] + b[3] >= 20 || (sym === 'XAUUSD' && b[2] + b[3] >= 1)) days[d] = [+b[0].toFixed(6), +b[1].toFixed(6), b[2], b[3]]; });
    setRec(R); return { price:last.c, chg24:(last.c/d24.c - 1)*100, range24:(hi/lo - 1)*100, atrPct:atr/last.c*100, at:last.h }; }
  async function check(){ if(state.busy) return; state.busy = true; state.msg = 'Reading live prices…'; render();
    var ok = 0; for(var i=0; i<ORDER.length; i++){ try{ var x = digest(ORDER[i], await getKl(ORDER[i])); if(x){ state.live[ORDER[i]] = x; ok++; } }catch(e){} }
    state.busy = false; state.at = Date.now(); state.msg = ok ? 'Live prices for ' + ok + ' of 6 markets (Binance perpetuals, hourly).' : 'No live prices (offline?). The profiles below are from the research and still apply.'; render(); }
  function e6(sym){ var days = (rec().days[sym]) || {}, wk = {}; Object.keys(days).forEach(function(d){ d = +d; var w = d - ((d + 3) % 7); wk[w] = (wk[w] || 0) + days[d][0] - days[d][1]; });
    var thisW = (function(){ var d = Math.floor(Date.now()/864e5); return d - ((d + 3) % 7); })(), ws = Object.keys(wk).map(Number).filter(function(w){ return w < thisW; }).sort(), x = ws.map(function(w){ return wk[w]; }), n = x.length;
    var m = n ? x.reduce(function(a, b){ return a + b; }, 0)/n : null, sd = n > 1 ? Math.sqrt(x.reduce(function(a, b){ return a + (b - m)*(b - m); }, 0)/(n - 1)) : null;
    return { days:Object.keys(days).length, weeks:n, mean:m, t:sd > 0 ? m/(sd/Math.sqrt(n)) : null, outSum:Object.keys(days).reduce(function(a, d){ return a + days[d][0]; }, 0), usSum:Object.keys(days).reduce(function(a, d){ return a + days[d][1]; }, 0) }; }
  // ── visuals ──
  function clock(P, nowH){ var W = 360, Hh = 150, top = 14, bot = 30, pad = 6, bw = (W - 2*pad)/24, mx = Math.max.apply(null, P.hour_move_bps), md = Math.max.apply(null, P.hour_drift_bps.map(Math.abs)) || 1, s = '';
    SESS.forEach(function(se, k){ s += '<rect x="' + (pad + se[1]*bw).toFixed(1) + '" y="' + top + '" width="' + ((se[2] - se[1])*bw).toFixed(1) + '" height="' + (Hh - top - bot) + '" fill="' + (k % 2 ? 'var(--panel2)' : 'transparent') + '"/>' +
      '<text x="' + (pad + (se[1] + se[2])/2*bw).toFixed(1) + '" y="' + (top - 3) + '" text-anchor="middle" class="mp-ax">' + se[0] + '</text>'; });
    for(var h=0; h<24; h++){ var v = P.hour_move_bps[h], dr = P.hour_drift_bps[h], bh = (Hh - top - bot)*v/mx, x = pad + h*bw, a = 0.35 + 0.65*Math.min(Math.abs(dr)/md, 1);
      s += '<rect data-hour="' + h + '" x="' + (x + 1).toFixed(1) + '" y="' + (Hh - bot - bh).toFixed(1) + '" width="' + (bw - 2).toFixed(1) + '" height="' + bh.toFixed(1) + '" fill="' + (dr >= 0 ? 'var(--bull)' : 'var(--bear)') + '" fill-opacity="' + a.toFixed(2) + '"><title>' + h + ':00 UTC (' + tob(h) + ':00 Tobago): typical move ' + v.toFixed(1) + ' bp, average drift ' + sgn(dr, 2) + ' bp</title></rect>';
      if(h % 3 === 0) s += '<text x="' + (x + bw/2).toFixed(1) + '" y="' + (Hh - bot + 11) + '" text-anchor="middle" class="mp-ax">' + h + '</text><text x="' + (x + bw/2).toFixed(1) + '" y="' + (Hh - bot + 21) + '" text-anchor="middle" class="mp-ax2">' + tob(h) + '</text>'; }
    var nx = pad + (nowH + 0.5)*bw; s += '<line x1="' + nx.toFixed(1) + '" x2="' + nx.toFixed(1) + '" y1="' + top + '" y2="' + (Hh - bot) + '" stroke="var(--gold)" stroke-width="1.5" stroke-dasharray="3 2"/><text x="' + nx.toFixed(1) + '" y="' + (Hh - 2) + '" text-anchor="middle" class="mp-now">now</text>';
    return '<svg class="mp-clock" viewBox="0 0 ' + W + ' ' + Hh + '" role="img" aria-label="When ' + esc(P.name) + ' moves, hour by hour">' + s + '<text x="' + (W - pad) + '" y="' + (Hh - bot + 11) + '" text-anchor="end" class="mp-ax">UTC</text><text x="' + (W - pad) + '" y="' + (Hh - bot + 21) + '" text-anchor="end" class="mp-ax2">Tobago</text></svg>'; }
  function pill(t, c){ return '<span class="mp-pill ' + c + '">' + t + '</span>'; }
  function hrs(x){ return x == null ? '—' : (x < 48 ? Math.round(x) + ' hours' : Math.round(x/24) + ' days'); }
  function trow(a, b, c){ return '<tr><td>' + a + '</td><td>' + b + '</td><td>' + c + '</td></tr>'; }
  function bothDir(sym){ var A = DATA2[sym]; if(!A) return ''; var u = A.up_legs, d = A.down_legs, gold = sym === 'XAUUSD', h = '';
    h += '<div class="mp-sec" data-sec="both"><h4>Both directions: how it falls and how it rises</h4><table class="mp-tab"><tr><th></th><th>Rising</th><th>Falling</th></tr>' +
      trow('Share of hours / days', A.up_hours_pct + '% / ' + A.up_days_pct + '%', (100 - A.up_hours_pct).toFixed(1) + '% / ' + (100 - A.up_days_pct).toFixed(1) + '%') +
      trow('Average hour', '+' + A.avg_up_hour_bps + ' bp', A.avg_down_hour_bps + ' bp') +
      trow('1 hour in 100 moves at least', '+' + A.best1pct_hour_pct + '%', A.worst1pct_hour_pct + '%') +
      trow('Biggest hour', '+' + A.best_hour[0] + '% (' + A.best_hour[1].slice(0, 10) + ')', A.worst_hour[0] + '% (' + A.worst_hour[1].slice(0, 10) + ')') +
      trow('Biggest 24 hours', '+' + A.best_24h[0] + '% (' + A.best_24h[1] + ')', A.worst_24h[0] + '% (' + A.worst_24h[1] + ')') +
      trow('Swings of ' + A.swing_threshold_pct + '% or more', u.n + ', typically +' + u.median_pct + '% over ' + hrs(u.median_hours), d.n + ', typically ' + d.median_pct + '% over ' + hrs(d.median_hours)) +
      trow('Biggest swing / longest', '+' + u.biggest_pct + '% / ' + u.longest_days + ' days', d.biggest_pct + '% / ' + d.longest_days + ' days') +
      trow('Next 24 h after a big hour: movement vs normal', '×' + A.vol_after_big_up_x, '×' + A.vol_after_big_down_x) +
      trow('Big hours (2.5σ) that happen in US hours', A.big_up_by_session_pct.US + '%', A.big_down_by_session_pct.US + '%') + '</table>';
    var sk = A.skew_hourly, skt = sk > 0.5 ? 'Its sharpest hours are mostly <b>spikes up</b> (skew ' + sk + '): for a short, squeezes are the main danger.' : (sk < -0.5 ? 'Its sharpest hours are mostly <b>drops</b> (skew ' + sk + '): for a long, crashes are the main danger.' : 'Its sharpest hours are about as often up as down (skew ' + sk + ').');
    h += '<p class="hint">' + skt + ' Falls ' + (d.median_hours < u.median_hours ? 'tend to be quicker than rallies' : 'take about as long as rallies or longer') + ' (' + hrs(d.median_hours) + ' against ' + hrs(u.median_hours) + ' for a typical ' + A.swing_threshold_pct + '% swing). Big hours in both directions mostly arrive in US hours, and movement stays higher for the next day after either.</p>';
    var S5 = A.e5_direction_split, rows5 = Object.keys(S5).map(function(k){ var v = S5[k]; return '<tr><td>' + esc(k) + '</td><td class="' + (v.long.b >= 0 ? 'up' : 'dn') + '">' + sgn(v.long.b) + '%</td><td class="' + (v.short.b >= 0 ? 'up' : 'dn') + '">' + sgn(v.short.b) + '%</td></tr>'; }).join('');
    h += '<p><b>Long side vs short side</b> of the two-sided rules (plan E5), a year, 2024–2026, after costs:</p><table class="mp-tab"><tr><th>Rule</th><th>Long side</th><th>Short side</th></tr>' + rows5 + '</table>';
    var SH = A.shorts, rows7 = Object.keys(SH.rules).map(function(k){ var v = SH.rules[k]; return '<tr' + (k === SH.pick ? ' class="mp-cur"' : '') + '><td>' + esc(k) + (k === SH.pick ? ' (chosen)' : '') + '</td><td>' + sgn(v.t_a, 2) + '</td><td>' + sgn(v.t_b, 2) + '</td><td>' + v.trades + '</td></tr>'; }).join('');
    h += '<p><b>Short-only rules</b> (plan E7: chosen on 2020–2023, judged once on 2024–2026, t ≥ 2.40 needed): ' + pill(SH.passed ? 'PASS' : 'FAILED', SH.passed ? 'go' : 'off') + '</p><table class="mp-tab"><tr><th>Rule (costs included)</th><th>t 2020–23</th><th>t 2024–26</th><th>Trades</th></tr>' + rows7 + '</table>' +
      '<p class="hint">The blow-off short (the mirror of the climax reversal) needs a 3σ hour up on 3× volume that closes weak: on one market that happened only a handful of times in six years, too rarely to judge here. Funding, which usually pays shorts when futures trade above spot, is not counted, so short results are if anything slightly understated.</p>';
    h += '<ul class="mp-list"><li>Shorting is possible on Binance futures (and on MT5 for gold' + (gold ? ', where an overnight swap applies' : '') + '). It is the same trade in reverse, with the same costs.</li>' +
      '<li>Squeeze risk: the biggest hour up was +' + A.best_hour[0] + '% and the biggest 24 hours +' + A.best_24h[0] + '%. A short needs a real stop set by the hourly range and sized at 1% risk, never a mental stop.</li>' +
      '<li>No short-only rule passed, and the short sides of the two-sided rules held up no better than the long sides. The market goes both ways, but in these tests neither direction gave an edge on its own.</li></ul></div>';
    return h; }
  // ── the page ──
  function profile(sym){ var P = DATA[sym], T = TEXT[sym], L = state.live[sym], c = cfg(), nowH = new Date().getUTCHours(), ses = sessOf(nowH), h = '';
    var atr = L ? L.atrPct : P.atr_h_pct_recent, stop = 2*atr, pos = (+c.acct || 100)*(+c.risk || 1)/100/(stop/100), lev = pos/(+c.acct || 100), feeShare = 0.20/P.atr_h_pct_recent*100;
    var mv = P.hour_move_bps.map(function(v, i){ return [v, i]; }).sort(function(a, b){ return b[0] - a[0]; }).slice(0, 3).map(function(x){ return x[1]; }).sort(function(a, b){ return a - b; });
    h += '<div class="mp-head"><div><div class="mp-kicker">' + esc(T.kind) + '</div><h3>' + esc(T.title) + '</h3></div>' + (L ? '<div class="mp-price"><b>' + (L.price >= 100 ? L.price.toFixed(2) : L.price.toPrecision(5)) + '</b><span class="' + (L.chg24 >= 0 ? 'up' : 'dn') + '">' + sgn(L.chg24, 2) + '% 24h</span></div>' : '') + '</div>';
    h += '<p class="mp-what">' + esc(T.what) + '</p>';
    h += '<div class="mp-sec"><h4>Right now</h4><p>It is ' + nowH + ':00 UTC (' + tob(nowH) + ':00 Tobago), the <b>' + ses + '</b> session. This hour usually moves <b>' + P.hour_move_bps[nowH].toFixed(0) + ' bp</b> (the average hour: ' + (P.hour_move_bps.reduce(function(a, b){ return a + b; }, 0)/24).toFixed(0) + ' bp).' +
      (L ? ' Last 24 hours: ' + sgn(L.chg24, 2) + '%, range ' + L.range24.toFixed(2) + '% (a typical day: ' + P.day_range_pct_recent + '%). Hourly range now ' + L.atrPct.toFixed(2) + '% (research, last 90 days: ' + P.atr_h_pct_recent + '%).' : ' Live price not loaded.') + '</p></div>';
    h += '<div class="mp-sec"><h4>When it moves</h4>' + clock(P, nowH) + '<p class="hint">Bar height: how much it typically moves in that hour. Green: on average it rose in that hour; red: it fell (before costs, ' + P.from.slice(0, 4) + '–' + P.to.slice(0, 4) + '). Most movement: ' + mv.map(function(x){ return x + ':00'; }).join(', ') + ' UTC.</p>' +
      '<table class="mp-tab"><tr><th>Session (UTC)</th><th>Drift a year</th><th>Years up</th><th>Typical hour</th></tr>' + SESS.map(function(se){ var v = P.sessions[se[0]]; return '<tr' + (se[0] === ses ? ' class="mp-cur"' : '') + '><td>' + se[0] + ' ' + se[1] + '–' + se[2] + '</td><td class="' + (v.perYear >= 0 ? 'up' : 'dn') + '">' + sgn(v.perYear) + '%</td><td>' + v.yearsUp + ' of ' + v.years + '</td><td>' + v.move_bps + ' bp</td></tr>'; }).join('') + '</table>' +
      '<p class="hint">Before costs; log returns. The same pattern — up outside US hours, down during them — shows in all six markets, but it was found on data already used, so it is being recorded forward (plan E6) before anyone relies on it.</p></div>';
    var big4 = P.after_big_4h, big24 = P.after_big_24h, bo = P.after_breakout_24h;
    h += '<div class="mp-sec"><h4>How it behaves</h4><table class="mp-tab"><tr><th></th><th>2020–2023</th><th>2024–2026</th></tr>' +
      '<tr><td>After a big hour (2.5σ), next 4 h, in its direction</td><td>' + sgn(big4.a_bps) + ' bp</td><td>' + sgn(big4.b_bps) + ' bp</td></tr>' +
      '<tr><td>… next 24 h</td><td>' + sgn(big24.a_bps) + ' bp</td><td>' + sgn(big24.b_bps) + ' bp</td></tr>' +
      '<tr><td>After a close beyond the 24 h high/low, next 24 h, in its direction</td><td>' + sgn(bo.a_bps) + ' bp</td><td>' + sgn(bo.b_bps) + ' bp</td></tr>' +
      '<tr><td>Trend (above 1) or snap-back (below 1) within a day</td><td>' + P.vr24_a.toFixed(2) + '</td><td>' + P.vr24_b.toFixed(2) + '</td></tr></table>' +
      '<p class="hint">' + (P.corr_market != null ? 'Moves with the crypto market: correlation ' + P.corr_market + ', beta ' + P.beta_market + ' (1 = moves as much as the market). Weekends move about ' + Math.round((1 - P.weekend_vs_week_move)*100) + '% less than weekdays. Typical daily volume (Binance spot, last 90 days): $' + Math.round(P.day_volume_usd_recent/1e6) + 'M. ' : '') +
      'A round trip at taker fees (0.20% with slippage) is about ' + Math.round(feeShare) + '% of a typical hourly move' + (sym === 'XAUUSD' ? ' on Binance; much less on an MT5 raw account' : '') + '. Effects of a few bp are smaller than fees.</p></div>';
    h += bothDir(sym);
    h += '<div class="mp-sec"><h4>What moves it</h4><ul class="mp-list">' + T.drivers.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul><p class="hint">General knowledge up to mid-2026, not live news: check current events before trading.</p></div>';
    h += '<div class="mp-sec"><h4>How to trade it</h4><ul class="mp-list">' + T.how.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' +
      '<div class="mp-calc"><label>Account (USDT)<input type="number" min="5" step="1" data-mp="acct" value="' + esc(c.acct) + '"></label><label>Risk per trade (%)<input type="number" min="0.1" max="10" step="0.1" data-mp="risk" value="' + esc(c.risk) + '"></label></div>' +
      '<p class="mp-size">A stop 2 hourly ranges away (' + stop.toFixed(2) + '%) means a position of <b>' + pos.toFixed(2) + ' USDT</b> (' + lev.toFixed(1) + '× the account) to lose ' + ((+c.acct || 100)*(+c.risk || 1)/100).toFixed(2) + ' USDT if it is hit.' +
      (pos < 5 ? ' <b class="mp-warn">Below Binance’s 5 USDT minimum order: the minimum would make the risk ' + (5*stop/100/(+c.acct || 100)*100).toFixed(1) + '% of the account.</b>' : '') +
      (sym === 'XAUUSD' && L ? ' On MT5 the smallest gold trade (0.01 lot = 1 oz) is about ' + Math.round(L.price) + ' USD of gold, ' + (L.price/(+c.acct || 100)).toFixed(0) + '× this account: a 2-range stop there would risk about ' + (L.price*stop/100).toFixed(1) + ' USD.' : '') + '</p></div>';
    var S = P.strategy, rows = Object.keys(S.rules).map(function(k){ var v = S.rules[k]; return '<tr' + (k === S.pick ? ' class="mp-cur"' : '') + '><td>' + esc(k) + (k === S.pick ? ' (chosen)' : '') + '</td><td>' + sgn(v.t_a, 2) + '</td><td>' + sgn(v.t_b, 2) + '</td></tr>'; }).join('');
    h += '<div class="mp-sec"><h4>What has been tested on it</h4><p>Plan E5: seven rules, the best chosen on 2020–2023 and judged once on 2024–2026 (needed t ≥ 2.40 and every year positive). Result: ' + pill(S.passed ? 'PASS' : 'FAILED', S.passed ? 'go' : 'off') + '</p>' +
      '<table class="mp-tab"><tr><th>Rule (costs included)</th><th>t 2020–23</th><th>t 2024–26</th></tr>' + rows + '</table><ul class="mp-list">' + T.tested.map(function(x){ return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
    var f = e6(sym); h += '<div class="mp-sec"><h4>Forward record (plan E6)</h4><p class="hint">From 21 Oct 2026: each day, the move outside US hours and the move during them. ' + (f.days ? f.days + ' days recorded; so far outside ' + sgn(f.outSum*100, 2) + '%, US hours ' + sgn(f.usSum*100, 2) + '%. ' : 'No full day recorded yet. ') + (f.weeks >= 26 ? 'Weekly difference t ' + (f.t == null ? '—' : f.t.toFixed(2)) + ' (confirmed at 1.65).' : f.weeks + ' of 26 weeks — judged once at 26.') + ' Kept while the app is opened at least once a month.</p></div>';
    return h; }
  function css(){ if(el('mprofCss')) return; var st = document.createElement('style'); st.id = 'mprofCss';
    st.textContent = '.mp-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px;}.mp-tabs button{border:1px solid var(--border);background:var(--panel);color:var(--text);border-radius:999px;padding:6px 12px;font-size:13px;cursor:pointer;}' +
      '.mp-tabs button.on{border-color:var(--gold);color:var(--gold);background:rgba(201,162,75,.12);}.mp-tabs small{color:var(--text-dim);margin-left:4px;}.mp-card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:12px;}' +
      '.mp-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;}.mp-head h3{margin:2px 0 4px;font-size:18px;}.mp-kicker{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim);}' +
      '.mp-price{text-align:right;}.mp-price b{display:block;font-size:17px;}.mp-price span{font-size:12px;}.up{color:var(--bull);}.dn{color:var(--bear);}.mp-what{font-size:13px;color:var(--text);margin:6px 0 10px;line-height:1.5;}' +
      '.mp-sec{border-top:1px solid var(--border);padding:10px 0 4px;}.mp-sec h4{margin:0 0 6px;font-size:14px;color:var(--gold);}.mp-sec p{font-size:13px;line-height:1.5;margin:6px 0;}' +
      '.mp-clock{width:100%;height:auto;display:block;background:var(--bg);border:1px solid var(--border);border-radius:8px;}.mp-ax{font-size:8.5px;fill:var(--text-dim);}.mp-ax2{font-size:7.5px;fill:var(--text-dim);opacity:.75;}.mp-now{font-size:8.5px;fill:var(--gold);font-weight:700;}' +
      '.mp-tab{width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed;margin:6px 0;}.mp-tab th{text-align:left;color:var(--text-dim);font-weight:600;border-bottom:1px solid var(--border);padding:4px;}.mp-tab td{padding:4px;border-bottom:1px solid var(--border);white-space:normal;overflow-wrap:anywhere;}' +
      '.mp-tab tr.mp-cur td{background:rgba(201,162,75,.10);}.mp-list{margin:4px 0;padding-left:18px;font-size:13px;line-height:1.5;}.mp-list li{margin:3px 0;}.mp-calc{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 0;}.mp-calc label{font-size:11px;color:var(--text-dim);display:flex;flex-direction:column;gap:3px;}.mp-calc input{width:110px;}' +
      '.mp-size{background:var(--panel2);border-radius:8px;padding:8px 10px;}.mp-warn{color:var(--amber);}.mp-pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;}.mp-pill.off{background:rgba(255,77,94,.12);color:var(--bear);}.mp-pill.go{background:rgba(37,211,139,.16);color:var(--bull);}' +
      '.mp-start{border:1px solid var(--gold);border-radius:12px;padding:12px 14px;margin:0 0 12px;background:linear-gradient(135deg,rgba(201,162,75,.10),rgba(155,140,255,.05));}.mp-start h3{margin:0 0 6px;color:var(--gold);font-size:15px;}.mp-start p{font-size:13px;line-height:1.5;margin:4px 0;}';
    document.head.appendChild(st); }
  function html(){ var c = cfg();
    var start = '<div class="mp-start"><h3>Start here</h3><p>Pick a market below. Each profile says when it moves, how it behaves, what drives it, how to size a trade on your account, and everything tested on it.</p>' +
      '<p><b>What the research found:</b> no strategy passed on any of the six, buying or shorting (plans E5 and E7, judged on 2024–2026). Each profile now shows both directions: how it falls, how it rises, squeezes and crashes. The one pattern common to all six is <b>timing</b>: before costs they gained outside US hours and drifted down during them. It is being recorded forward from 21 Oct 2026 (plan E6) before anyone relies on it.</p></div>';
    var tabs = '<div class="mp-tabs">' + ORDER.map(function(s){ var L = state.live[s]; return '<button type="button" data-mpsel="' + s + '" class="' + (s === c.sel ? 'on' : '') + '">' + esc(TEXT[s].short) + (L ? '<small class="' + (L.chg24 >= 0 ? 'up' : 'dn') + '">' + sgn(L.chg24, 1) + '%</small>' : '') + '</button>'; }).join('') + '</div>';
    return start + tabs + '<div class="mp-card">' + profile(c.sel) + '</div><p class="hint" style="margin:8px 0 0;">' + esc(state.msg || '') + ' <button class="btn-outline" type="button" data-mp="refresh"' + (state.busy ? ' disabled' : '') + '>' + (state.busy ? 'Loading…' : 'Refresh live prices') + '</button></p>'; }
  function render(){ var host = el('mprofBody'); if(!host) return; css(); host.innerHTML = html();
    Array.prototype.forEach.call(host.querySelectorAll('[data-mpsel]'), function(b){ b.onclick = function(){ var v = cfg(); v.sel = b.getAttribute('data-mpsel'); setCfg(v); render(); }; });
    Array.prototype.forEach.call(host.querySelectorAll('[data-mp]'), function(b){ var k = b.getAttribute('data-mp');
      if(k === 'refresh') b.onclick = function(){ check(); };
      if(k === 'acct' || k === 'risk') b.onchange = function(){ var v = cfg(), x = parseFloat(b.value); if(isFinite(x) && x > 0){ v[k] = k === 'risk' ? Math.min(Math.max(x, 0.1), 10) : Math.max(x, 1); setCfg(v); } render(); }; }); }
  function onShow(){ render(); if(Date.now() - state.at > 30*60e3) check(); }
  setInterval(function(){ if(Date.now() - state.at > 60*60e3 && document.visibilityState !== 'hidden') check(); }, 5*60e3);
  window.OMEGA_MPROF = { render:render, onShow:onShow, check:check, state:function(){ return state; }, DATA:DATA, TEXT:TEXT, DATA2:DATA2, ORDER:ORDER, START_DAY:START_DAY,
    _:{ digest:digest, e6:e6, clock:clock, profile:profile, html:html, sessOf:sessOf, bothDir:bothDir } };
})();
</script>
