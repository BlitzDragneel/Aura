<script>/* ═══ EDGE LIBRARY (v6.5.70) — the engine, rules, conditions and exits the Edge Lab explores with ═══
   The round-12 engine in the app (PLAN12/PLAN13): daily decisions at the close; every position a perpetual, 0.06% a side,
   longs pay funding; time-series rules sized to 20% yearly volatility (0.25x–1.5x), re-sized only on a sign change or a
   change over 0.15, 1/N per coin; cross-sectional rules long the top fifth / short the bottom fifth at each Sunday close;
   the harvest as spot + short perpetual (0.11% + 0.06% a side, P&L = funding − costs). Each rule is judged on its alpha
   against the equal-weight market of the same coins. The base rules carry the research code's names and reproduce it on
   the 25 studied coins (tests s70). Conditions and exits are the Edge Lab's new ground: no research round tested them. */
(function(){
  'use strict';
  var DAY = 86400e3, PERP = 0.0006, SPOT = 0.0011, SQ = Math.sqrt(365.25);
  function nan(T){ return new Float64Array(T).fill(NaN); }
  // ── rolling windows (a window needs every value present, as pandas with min_periods = window) ──
  function rsum(x, n){ var T = x.length, o = nan(T), s = 0, bad = 0;
    for(var t=0; t<T; t++){ var v = x[t]; if(v === v) s += v; else bad++; if(t >= n){ var u = x[t-n]; if(u === u) s -= u; else bad--; }
      if((t & 255) === 255 && t >= n - 1){ s = 0; for(var i=t-n+1; i<=t; i++) if(x[i] === x[i]) s += x[i]; }
      if(t >= n - 1 && bad === 0) o[t] = s; }
    return o; }
  function rmean(x, n){ var o = rsum(x, n); for(var t=0; t<o.length; t++) o[t] /= n; return o; }
  function rstd(x, n){ var T = x.length, o = nan(T); for(var t=n-1; t<T; t++){ var s = 0, ok = true; for(var i=t-n+1; i<=t; i++){ var v = x[i]; if(v !== v){ ok = false; break; } s += v; } if(!ok) continue; var m = s/n, q = 0; for(var k=t-n+1; k<=t; k++){ var d = x[k] - m; q += d*d; } o[t] = Math.sqrt(q/(n - 1)); } return o; }
  function rext(x, n, isMax){ var T = x.length, o = nan(T), dq = [], bad = 0;
    for(var t=0; t<T; t++){ var v = x[t]; if(v !== v) bad++; else { while(dq.length && (isMax ? x[dq[dq.length-1]] <= v : x[dq[dq.length-1]] >= v)) dq.pop(); dq.push(t); }
      if(t >= n){ if(x[t-n] !== x[t-n]) bad--; } while(dq.length && dq[0] <= t - n) dq.shift();
      if(t >= n - 1 && bad === 0 && dq.length) o[t] = x[dq[0]]; }
    return o; }
  function rmax(x, n){ return rext(x, n, true); } function rmin(x, n){ return rext(x, n, false); }
  function rmeanMin(x, n, mp){ var T = x.length, o = nan(T); for(var t=0; t<T; t++){ var s = 0, c = 0; for(var i=Math.max(0, t-n+1); i<=t; i++) if(x[i] === x[i]){ s += x[i]; c++; } if(c >= mp) o[t] = s/c; } return o; }
  function rstdMin(x, n, mp){ var T = x.length, o = nan(T); for(var t=0; t<T; t++){ var s = 0, c = 0; for(var i=Math.max(0, t-n+1); i<=t; i++) if(x[i] === x[i]){ s += x[i]; c++; } if(c < mp || c < 2) continue; var m = s/c, q = 0; for(var k=Math.max(0, t-n+1); k<=t; k++) if(x[k] === x[k]) q += (x[k] - m)*(x[k] - m); o[t] = Math.sqrt(q/(c - 1)); } return o; }
  function rrank(x, n, mp){ var T = x.length, o = nan(T); for(var t=0; t<T; t++){ var v = x[t]; if(v !== v) continue; var c = 0, lo = 0, eq = 0; for(var i=Math.max(0, t-n+1); i<=t; i++){ var u = x[i]; if(u !== u) continue; c++; if(u < v) lo++; else if(u === v) eq++; } if(c >= mp) o[t] = (lo + (eq + 1)/2)/c; } return o; }
  function bpos(w, v){ var lo = 0, hi = w.length; while(lo < hi){ var m = (lo + hi) >> 1; if(w[m] < v) lo = m + 1; else hi = m; } return lo; }
  function rmedian(x, n, mp){ var T = x.length, o = nan(T), w = [];
    for(var t=0; t<T; t++){ var v = x[t]; if(v === v) w.splice(bpos(w, v), 0, v); if(t >= n){ var u = x[t-n]; if(u === u) w.splice(bpos(w, u), 1); }
      if(w.length >= mp && w.length){ var h = w.length >> 1; o[t] = w.length & 1 ? w[h] : (w[h-1] + w[h])/2; } }
    return o; }
  function ewmA(x, alpha, minp){ var T = x.length, o = nan(T); if(!T) return o; var w = x[0], oldwt = 1, nobs = (x[0] === x[0]) ? 1 : 0; o[0] = nobs >= minp ? w : NaN;
    for(var i=1; i<T; i++){ var cur = x[i], obs = cur === cur; if(obs) nobs++;
      if(w === w){ oldwt *= (1 - alpha); if(obs){ if(w !== cur) w = (oldwt*w + alpha*cur)/(oldwt + alpha); oldwt = 1; } } else if(obs) w = cur;
      o[i] = nobs >= minp ? w : NaN; }
    return o; }
  function ema(x, n){ return ewmA(x, 2/(n + 1), n); } function wild(x, n){ return ewmA(x, 1/n, n); }
  function sh(x, k){ var T = x.length, o = nan(T); for(var t=k; t<T; t++) o[t] = x[t-k]; return o; }
  function sgn(v){ return v !== v ? NaN : (v > 0 ? 1 : (v < 0 ? -1 : 0)); }
  function sgnA(x){ var o = nan(x.length); for(var t=0; t<x.length; t++) o[t] = sgn(x[t]); return o; }
  function state(T, el, xl, es, xs){ var o = new Float64Array(T), p = 0; for(var t=0; t<T; t++){ if(p === 1 && xl(t)) p = 0; if(p === -1 && xs && xs(t)) p = 0; if(p === 0){ if(el(t)) p = 1; else if(es && es(t)) p = -1; } o[t] = p; } return o; }
  function hold(T, entry, n){ var o = new Float64Array(T), last = -1e9; for(var t=0; t<T; t++){ if(entry(t)) last = t; o[t] = (t - last < n) ? 1 : 0; } return o; }
  // ── per-coin indicators ──
  function pchg(c){ var T = c.length, r = nan(T); for(var t=1; t<T; t++) if(c[t] === c[t] && c[t-1] === c[t-1]) r[t] = c[t]/c[t-1] - 1; return r; }
  function rsi(c, p){ var T = c.length, up = nan(T), dn = nan(T); for(var t=1; t<T; t++) if(c[t] === c[t] && c[t-1] === c[t-1]){ var d = c[t] - c[t-1]; up[t] = d > 0 ? d : 0; dn[t] = d < 0 ? -d : 0; }
    var U = wild(up, p), D = wild(dn, p), o = nan(T); for(var i=0; i<T; i++){ var dd = D[i] === 0 ? NaN : D[i]; o[i] = 100 - 100/(1 + U[i]/dd); } return o; }
  function tr(c, h, l){ var T = c.length, o = nan(T); for(var t=0; t<T; t++){ var c1 = t ? c[t-1] : NaN, m = NaN; [h[t] - l[t], Math.abs(h[t] - c1), Math.abs(l[t] - c1)].forEach(function(v){ if(v === v && !(m >= v)) m = v; }); o[t] = m; } return o; }
  function atr(c, h, l, n){ return wild(tr(c, h, l), n); }
  function ret(c, n){ var o = nan(c.length); for(var t=n; t<c.length; t++) o[t] = c[t]/c[t-n] - 1; return o; }
  // ── base rules (names exactly as the research library r12lib; signals in long/short form, LF keeps the long side) ──
  var SIG = {
    tsmom:function(G, j, n){ return sgnA(ret(G.c[j], n)); },
    macross:function(G, j, f, s, k){ var m = k === 'sma' ? rmean : ema, a = m(G.c[j], f), b = m(G.c[j], s), o = nan(G.T); for(var t=0; t<G.T; t++) o[t] = sgn(a[t] - b[t]); return o; },
    above:function(G, j, n){ var m = rmean(G.c[j], n), c = G.c[j], o = nan(G.T); for(var t=0; t<G.T; t++) o[t] = sgn(c[t] - m[t]); return o; },
    donchian:function(G, j, n, m){ var c = G.c[j], H = sh(rmax(c, n), 1), L = sh(rmin(c, n), 1), Lm = sh(rmin(c, m), 1), Hm = sh(rmax(c, m), 1);
      return state(G.T, function(t){ return c[t] > H[t]; }, function(t){ return c[t] < Lm[t]; }, function(t){ return c[t] < L[t]; }, function(t){ return c[t] > Hm[t]; }); },
    supertrend:function(G, j, n, k){ var c = G.c[j], h = G.h[j], l = G.l[j], A = atr(c, h, l, n), T = G.T, o = nan(T), fu = NaN, fl = NaN, dir = 1;
      for(var t=0; t<T; t++){ var mid = (h[t] + l[t])/2, u = mid + k*A[t], b = mid - k*A[t], cc = c[t], pc = t ? c[t-1] : NaN;
        fu = (fu !== fu || u < fu || pc > fu) ? u : fu; fl = (fl !== fl || b > fl || pc < fl) ? b : fl; dir = cc > fu ? 1 : (cc < fl ? -1 : dir); o[t] = (isFinite(A[t]) && isFinite(cc)) ? dir : NaN; }
      return o; },
    keltner:function(G, j, n, k){ var c = G.c[j], m = ema(c, n), A = atr(c, G.h[j], G.l[j], n); return state(G.T, function(t){ return c[t] > m[t] + k*A[t]; }, function(t){ return c[t] < m[t]; }, function(t){ return c[t] < m[t] - k*A[t]; }, function(t){ return c[t] > m[t]; }); },
    bollB:function(G, j, n, k){ var c = G.c[j], m = rmean(c, n), s = rstd(c, n); return state(G.T, function(t){ return c[t] > m[t] + k*s[t]; }, function(t){ return c[t] < m[t]; }, function(t){ return c[t] < m[t] - k*s[t]; }, function(t){ return c[t] > m[t]; }); },
    bollR:function(G, j, n, k){ var c = G.c[j], m = rmean(c, n), s = rstd(c, n); return state(G.T, function(t){ return c[t] < m[t] - k*s[t]; }, function(t){ return c[t] > m[t]; }, function(t){ return c[t] > m[t] + k*s[t]; }, function(t){ return c[t] < m[t]; }); },
    macdZero:function(G, j, f, s){ var c = G.c[j], a = ema(c, f), b = ema(c, s), o = nan(G.T); for(var t=0; t<G.T; t++) o[t] = sgn(a[t] - b[t]); return o; },
    rsiMom:function(G, j, p, b){ var R = rsi(G.c[j], p); return state(G.T, function(t){ return R[t] > 50 + b; }, function(t){ return R[t] < 50; }, function(t){ return R[t] < 50 - b; }, function(t){ return R[t] > 50; }); },
    rsiRev:function(G, j, p, lo, hi){ var R = rsi(G.c[j], p); return state(G.T, function(t){ return R[t] < lo; }, function(t){ return R[t] > 50; }, function(t){ return R[t] > hi; }, function(t){ return R[t] < 50; }); },
    blend:function(G, j, ns){ var S = ns.map(function(n){ return SIG.tsmom(G, j, n); }), o = nan(G.T); for(var t=0; t<G.T; t++){ var s = 0; for(var i=0; i<S.length; i++) s += S[i][t]; o[t] = s/S.length; } return o; },
    linreg:function(G, j, n){ var c = G.c[j], T = G.T, y = new Float64Array(T), o = nan(T); for(var t=0; t<T; t++) y[t] = Math.log(c[t]);
      var jj = new Float64Array(T), yj = new Float64Array(T); for(var t1=0; t1<T; t1++){ jj[t1] = t1; yj[t1] = y[t1]*t1; }
      var mj = rmean(jj, n), my = rmean(y, n), myj = rmean(yj, n), j2 = new Float64Array(T); for(var t2=0; t2<T; t2++) j2[t2] = t2*t2; var mj2 = rmean(j2, n);
      for(var t3=0; t3<T; t3++){ var cov = myj[t3] - my[t3]*mj[t3], vj = mj2[t3] - mj[t3]*mj[t3]; o[t3] = sgn(cov/vj); } return o; },
    tstat:function(G, j, n){ var r = G.r[j], m = rmean(r, n), s = rstd(r, n), o = nan(G.T); for(var t=0; t<G.T; t++){ var z = m[t]/s[t]*Math.sqrt(n); o[t] = z !== z ? NaN : (z > 1 ? 1 : (z < -1 ? -1 : 0)); } return o; },
    zrev:function(G, j, n, k){ var c = G.c[j], m = rmean(c, n), s = rstd(c, n), z = nan(G.T); for(var t=0; t<G.T; t++) z[t] = (c[t] - m[t])/s[t]; return state(G.T, function(t){ return z[t] < -k; }, function(t){ return z[t] > 0; }, function(t){ return z[t] > k; }, function(t){ return z[t] < 0; }); },
    reversal:function(G, j, n){ var s = SIG.tsmom(G, j, n); for(var t=0; t<s.length; t++) s[t] = -s[t] + 0; return s; },
    fneg:function(G, j, n){ var s = rsum(G.fi[j], n), k = rsum(G.fc[j], n), o = nan(G.T); for(var t=0; t<G.T; t++) if(s[t] === s[t] && k[t] > 0) o[t] = s[t] < 0 ? 1 : 0; return o; },
    fext:function(G, j, n, kind){ var s = rsum(G.fi[j], n), k = rsum(G.fc[j], n), f = nan(G.T); for(var t=0; t<G.T; t++) if(s[t] === s[t] && k[t] > 0) f[t] = s[t];
      var p = rrank(f, 180, 90), o = nan(G.T); for(var t1=0; t1<G.T; t1++){ var q = p[t1]; if(q !== q) continue; var v = q >= 0.9 ? -1 : (q <= 0.1 ? 1 : 0); o[t1] = kind === 'contrarian' ? v : -v + 0; } return o; },
    taker:function(G, j, n, kind){ var a = rsum(G.tb[j], n), b = rsum(G.v[j], n), shr = nan(G.T); for(var t=0; t<G.T; t++) shr[t] = a[t]/b[t];
      var m = rmeanMin(shr, 180, 90), s = rstdMin(shr, 180, 90), o = nan(G.T); for(var t1=0; t1<G.T; t1++){ var z = (shr[t1] - m[t1])/s[t1]; if(z !== z) continue; var v = z > 1 ? 1 : (z < -1 ? -1 : 0); o[t1] = kind === 'follow' ? v : -v + 0; } return o; },
    obv:function(G, j, n){ var c = G.c[j], v = G.v[j], T = G.T, ob = nan(T), cum = 0; for(var t=0; t<T; t++){ var d = t ? sgn(c[t] - c[t-1]) : NaN; d = d !== d ? 0 : d; var x = d*v[t]; if(x === x){ cum += x; ob[t] = cum; } }
      var m = rmean(ob, n), o = nan(T); for(var t1=0; t1<T; t1++) o[t1] = sgn(ob[t1] - m[t1]); return o; },
    volbreak:function(G, j, n){ var c = G.c[j], v = G.v[j], H = sh(rmax(c, n), 1), mv = rmean(v, 30), T = G.T, w = Math.max(n, 30), e = hold(T, function(t){ return c[t] > H[t] && v[t] > 2*mv[t]; }, 10), o = nan(T); for(var t=w; t<T; t++) if(c[t-w] === c[t-w]) o[t] = e[t]; return o; },
    climax:function(G, j){ var c = G.c[j], v = G.v[j], mv = rmean(v, 30), T = G.T, e = hold(T, function(t){ return t > 0 && v[t] > 3*mv[t] && c[t] < c[t-1]; }, 5), o = nan(T); for(var t=30; t<T; t++) if(c[t-30] === c[t-30]) o[t] = e[t]; return o; },
    // new families (PLAN13 addendum A): never tested by research
    fundVsPrice:function(G, j){ var c = G.c[j], r7 = ret(c, 7), f7 = rsum(G.fi[j], 7), k7 = rsum(G.fc[j], 7), f = nan(G.T); for(var t=0; t<G.T; t++) if(f7[t] === f7[t] && k7[t] > 0) f[t] = f7[t];
      var p = rrank(f, 180, 90), o = nan(G.T); for(var t1=0; t1<G.T; t1++){ if(r7[t1] !== r7[t1] || f[t1] !== f[t1]) continue; o[t1] = (r7[t1] > 0 && f[t1] < 0) ? 1 : ((r7[t1] < 0 && p[t1] >= 0.9) ? -1 : 0); } return o; } };
  function score(G, j, kind, n){ var c = G.c[j], T = G.T, o = nan(T);
    if(kind === 'ret'){ return ret(c, n); }
    if(kind === 'negvol'){ var s = rstd(G.r[j], n); for(var t=0; t<T; t++) o[t] = -s[t]; return o; }
    if(kind === 'negfund'){ var f = rsum(G.fi[j], n), k = rsum(G.fc[j], n); for(var t1=0; t1<T; t1++) if(k[t1] > 0) o[t1] = -f[t1]; return o; }
    if(kind === 'near'){ var H = rmax(c, n); for(var t2=0; t2<T; t2++) o[t2] = c[t2]/H[t2]; return o; }
    if(kind === 'age'){ var first = -1; for(var t3=0; t3<T; t3++){ if(first < 0 && c[t3] === c[t3]) first = t3; if(first >= 0 && c[t3] === c[t3]) o[t3] = t3 - first; } return o; }
    throw new Error(kind); }
  var BASES = [];
  function B(name, fam, kind, mode, f, extra){ BASES.push(Object.assign({ name:name, fam:fam, kind:kind, mode:mode, f:f }, extra || {})); }
  B('TSMOM 14d LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.tsmom(G, j, 14); });
  B('TSMOM 30d LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.tsmom(G, j, 30); });
  B('TSMOM 90d LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.tsmom(G, j, 90); });
  B('SMA 10/50 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.macross(G, j, 10, 50, 'sma'); });
  B('EMA 7/28 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.macross(G, j, 7, 28, 'ema'); });
  B('close > SMA 50 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.above(G, j, 50); });
  B('Donchian 20/20 LS', 'breakout', 'ts', 'LS', function(G, j){ return SIG.donchian(G, j, 20, 20); });
  B('Donchian 55/20 LS', 'breakout', 'ts', 'LS', function(G, j){ return SIG.donchian(G, j, 55, 20); });
  B('Supertrend 7/2 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.supertrend(G, j, 7, 2); });
  B('Supertrend 10/3 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.supertrend(G, j, 10, 3); });
  B('Keltner 20/2.0 LF', 'breakout', 'ts', 'LF', function(G, j){ return SIG.keltner(G, j, 20, 2); });
  B('Bollinger breakout 20, 2.0 sd LS', 'breakout', 'ts', 'LS', function(G, j){ return SIG.bollB(G, j, 20, 2); });
  B('MACD 12/26/9 zero LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.macdZero(G, j, 12, 26); });
  B('RSI(14) momentum band 0 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.rsiMom(G, j, 14, 0); });
  B('trend blend 14/28/56 LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.blend(G, j, [14, 28, 56]); });
  B('regression slope 60d LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.linreg(G, j, 60); });
  B('t-stat momentum 30d LS', 'trend', 'ts', 'LS', function(G, j){ return SIG.tstat(G, j, 30); });
  B('RSI(5) 10/90 revert LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.rsiRev(G, j, 5, 10, 90); });
  B('RSI(3) 10/90 revert LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.rsiRev(G, j, 3, 10, 90); });
  B('RSI(2) 10/90 revert LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.rsiRev(G, j, 2, 10, 90); });
  B('RSI(14) 20/80 revert LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.rsiRev(G, j, 14, 20, 80); });
  B('Bollinger revert 20, 2.0 sd LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.bollR(G, j, 20, 2); });
  B('z-score to SMA 20 revert 2.0 LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.zrev(G, j, 20, 2); });
  B('reversal 3d LF', 'reversion', 'ts', 'LF', function(G, j){ return SIG.reversal(G, j, 3); });
  B('reversal 1d LS', 'reversion', 'ts', 'LS', function(G, j){ return SIG.reversal(G, j, 1); });
  B('long when 3d funding is negative', 'funding', 'ts', 'LF', function(G, j){ return SIG.fneg(G, j, 3); });
  B('funding 7d extremes contrarian', 'funding', 'ts', 'LS', function(G, j){ return SIG.fext(G, j, 7, 'contrarian'); });
  B('funding 30d extremes contrarian', 'funding', 'ts', 'LS', function(G, j){ return SIG.fext(G, j, 30, 'contrarian'); });
  B('taker-buy share 30d follow LS', 'volume', 'ts', 'LS', function(G, j){ return SIG.taker(G, j, 30, 'follow'); });
  B('OBV > its SMA 20 LS', 'volume', 'ts', 'LS', function(G, j){ return SIG.obv(G, j, 20); });
  B('breakout 20d on 2x volume, hold 10d', 'volume', 'ts', 'LF', function(G, j){ return SIG.volbreak(G, j, 20); });
  B('selling climax (3x volume, down day), long 5d', 'volume', 'ts', 'LF', function(G, j){ return SIG.climax(G, j); });
  B('XS momentum 28d LS', 'across coins', 'xs', 'LS', function(G, j){ return score(G, j, 'ret', 28); });
  B('XS reversal 7d LS', 'across coins', 'xs', 'NEG', function(G, j){ return score(G, j, 'ret', 7); });
  B('XS low vol 60d LS', 'across coins', 'xs', 'LS', function(G, j){ return score(G, j, 'negvol', 60); });
  B('XS carry 7d (short high funding)', 'across coins', 'xs', 'LS', function(G, j){ return score(G, j, 'negfund', 7); });
  B('XS carry 1d (short high funding)', 'across coins', 'xs', 'LS', function(G, j){ return score(G, j, 'negfund', 1); });
  B('XS nearness to 365d high LS', 'across coins', 'xs', 'LS', function(G, j){ return score(G, j, 'near', 365); });
  // ── the grid: every coin on the same days; A/B halves share the day axis and the market-wide context ──
  function grid(recs, endDay){
    recs = recs.filter(function(x){ return x && x.c && x.c.length; }).sort(function(a, b){ return a.sym < b.sym ? -1 : 1; });
    var K0 = Infinity, K1 = -Infinity; recs.forEach(function(x){ if(x.k0 < K0) K0 = x.k0; if(x.k0 + x.c.length - 1 > K1) K1 = x.k0 + x.c.length - 1; });
    if(endDay != null && K1 > endDay - 1) K1 = endDay - 1;
    var T = K1 - K0 + 1, G = { syms:[], K0:K0, T:T, c:[], h:[], l:[], v:[], tb:[], ff:[], fi:[], fc:[], E:[], r:[], size:[] };
    recs.forEach(function(x){ function put(src, pos){ var a = nan(T); if(!src) return a; for(var i=0; i<src.length; i++){ var t = x.k0 + i - K0; if(t < 0 || t >= T) continue; var v = src[i]; if(v != null && isFinite(v) && (!pos || v > 0)) a[t] = +v; } return a; }
      var ff = new Float64Array(T), fi = new Float64Array(T), fc = new Float64Array(T); for(var i=0; i<(x.ff || []).length; i++){ var t = x.k0 + i - K0; if(t < 0 || t >= T) continue; ff[t] = +x.ff[i] || 0; fi[t] = Math.round(ff[t]*1e8); fc[t] = +x.fc[i] || 0; }
      var c = put(x.c, true), E = new Uint8Array(T), f0 = -1; for(var t1=0; t1<T; t1++){ if(f0 < 0 && fc[t1] > 0) f0 = t1; E[t1] = (f0 >= 0 && t1 > f0 && c[t1] === c[t1]) ? 1 : 0; }
      G.syms.push(x.sym); G.c.push(c); G.h.push(put(x.h, true)); G.l.push(put(x.l, true)); G.v.push(put(x.v, false)); G.tb.push(put(x.tb, false)); G.ff.push(ff); G.fi.push(fi); G.fc.push(fc); G.E.push(E);
      var r = pchg(c), s = rstd(r, 20), z = new Float64Array(T); for(var t2=0; t2<T; t2++){ var q = 0.2/(s[t2]*SQ); z[t2] = q !== q ? NaN : Math.min(1.5, Math.max(0.25, q)); } G.r.push(r); G.size.push(z); });
    finish(G); G.ctx = context(G); return G; }
  function finish(G){ var T = G.T, n = G.syms.length; G.N = new Float64Array(T); G.m = new Float64Array(T);
    for(var t=0; t<T; t++){ var k = 0, s = 0, q = 0; for(var j=0; j<n; j++){ k += G.E[j][t]; if(t && G.E[j][t-1]){ var r = G.r[j][t]; if(r === r){ s += r; q++; } } } G.N[t] = k; G.m[t] = q ? s/q : 0; } }
  function subgrid(G, idx){ var S = { syms:[], K0:G.K0, T:G.T, c:[], h:[], l:[], v:[], tb:[], ff:[], fc:[], E:[], r:[], size:[], ctx:G.ctx };
    S.fi = []; idx.forEach(function(j){ ['c', 'h', 'l', 'v', 'tb', 'ff', 'fi', 'fc', 'E', 'r', 'size'].forEach(function(k){ S[k].push(G[k][j]); }); S.syms.push(G.syms[j]); }); finish(S); return S; }
  // ── market-wide and per-coin conditions (computed from all coins; known at each close) ──
  function context(G){ var T = G.T, n = G.syms.length, I = new Float64Array(T), lv = 1; for(var t=0; t<T; t++){ lv *= 1 + G.m[t]; I[t] = lv; }
    var Is = rmean(I, 200), bj = G.syms.indexOf('BTCUSDT'), btc = bj >= 0 ? G.c[bj] : nan(T), bs = rmean(btc, 100), mf = nan(T), br = nan(T), disp = nan(T);
    var sma50 = G.c.map(function(c){ return rmean(c, 50); }), f7 = G.ff.map(function(f){ return rsum(f, 7); });
    for(var t1=0; t1<T; t1++){ var s = 0, k = 0, up = 0, kb = 0, xs = []; for(var j=0; j<n; j++){ if(!G.E[j][t1]) continue; s += G.ff[j][t1]; k++; var m = sma50[j][t1]; if(m === m){ kb++; if(G.c[j][t1] > m) up++; } var f = f7[j][t1]; if(f === f) xs.push(f); }
      mf[t1] = k ? s/k : NaN; br[t1] = kb ? up/kb : NaN; if(xs.length >= 5){ var mu = xs.reduce(function(a, b){ return a + b; }, 0)/xs.length; disp[t1] = Math.sqrt(xs.reduce(function(a, b){ return a + (b - mu)*(b - mu); }, 0)/(xs.length - 1)); } }
    var mf7 = rmean(mf, 7), mfMed = rmedian(mf7, 365, 180), ir = pchg(I), iv = rstd(ir, 30), ivMed = rmedian(iv, 365, 180), dMed = rmedian(disp, 365, 180);
    function A(f){ var o = new Float64Array(T); for(var t=0; t<T; t++) o[t] = f(t) ? 1 : 0; return o; }
    return { mkt_up:A(function(t){ return I[t] > Is[t]; }), mkt_down:A(function(t){ return I[t] < Is[t]; }), btc_up:A(function(t){ return btc[t] > bs[t]; }), btc_down:A(function(t){ return btc[t] < bs[t]; }),
      fund_high:A(function(t){ return mfMed[t] === mfMed[t] && mf7[t] >= mfMed[t]; }), fund_low:A(function(t){ return mfMed[t] === mfMed[t] && mf7[t] < mfMed[t]; }),
      calm:A(function(t){ return ivMed[t] === ivMed[t] && iv[t] < ivMed[t]; }), rough:A(function(t){ return ivMed[t] === ivMed[t] && iv[t] >= ivMed[t]; }),
      breadth_up:A(function(t){ return br[t] > 0.5; }), breadth_down:A(function(t){ return br[t] < 0.5; }),
      disp_high:A(function(t){ return dMed[t] === dMed[t] && disp[t] >= dMed[t]; }), disp_low:A(function(t){ return dMed[t] === dMed[t] && disp[t] < dMed[t]; }), index:I }; }
  var MARKET_CONDS = ['mkt_up', 'mkt_down', 'btc_up', 'btc_down', 'fund_high', 'fund_low', 'calm', 'rough', 'breadth_up', 'breadth_down', 'align'], COIN_CONDS = ['cheap', 'dear', 'old', 'young', 'liquid', 'illiquid'], XS_CONDS = ['mkt_up', 'mkt_down', 'btc_up', 'btc_down', 'fund_high', 'fund_low', 'calm', 'rough', 'breadth_up', 'breadth_down', 'disp_high', 'disp_low'];
  var COND_TEXT = { none:'always', mkt_up:'only when the market is above its 200-day average', mkt_down:'only when the market is below its 200-day average', btc_up:'only when BTC is above its 100-day average', btc_down:'only when BTC is below its 100-day average',
    fund_high:'only when market funding is above its 1-year median', fund_low:'only when market funding is below its 1-year median', calm:'only in calm markets', rough:'only in rough markets', breadth_up:'only when most coins are above their 50-day average', breadth_down:'only when most coins are below their 50-day average',
    align:'longs only in an up market, shorts only in a down market', cheap:'only when the coin’s funding is cheaper than usual', dear:'only when the coin’s funding is dearer than usual', old:'only coins listed over a year', young:'only coins listed under a year', liquid:'only the more liquid half of coins', illiquid:'only the less liquid half of coins',
    disp_high:'only when funding differs a lot between coins', disp_low:'only when funding differs little between coins' };
  var EXIT_TEXT = { own:'its own exit', t5:'out after 5 days', t10:'out after 10 days', t20:'out after 20 days', atr3:'a 3-ATR trailing stop' };
  function coinCond(G, j, cond){ var key = cond + ':' + G.syms[j]; G._cc = G._cc || {}; if(G._cc[key]) return G._cc[key]; var r = coinCond0(G, j, cond); G._cc[key] = r; return r; }
  function coinCond0(G, j, cond){ var T = G.T, o = new Uint8Array(T);   // 1 = the condition holds that day (bytes: 290 coins × 6 conditions stay small on a phone)
    if(cond === 'cheap' || cond === 'dear'){ var f = rsum(G.fi[j], 7), med = rmedian(f, 180, 90); for(var t=0; t<T; t++) if(med[t] === med[t] && f[t] === f[t]) o[t] = (cond === 'cheap' ? f[t] < med[t] : f[t] >= med[t]) ? 1 : 0; return o; }
    if(cond === 'old' || cond === 'young'){ var c = G.c[j], first = -1; for(var t1=0; t1<T; t1++){ if(first < 0 && c[t1] === c[t1]) first = t1; if(first >= 0) o[t1] = ((t1 - first >= 365) === (cond === 'old')) ? 1 : 0; } return o; }
    if(cond === 'liquid' || cond === 'illiquid'){ if(!G._dv){ G._dv = G.c.map(function(c, q){ var x = nan(T); for(var t=0; t<T; t++) x[t] = c[t]*G.v[q][t]; return rmean(x, 30); }); G._dvMed = new Float64Array(T).fill(NaN);
        for(var t2=0; t2<T; t2++){ var w = []; for(var q=0; q<G.syms.length; q++) if(G.E[q][t2] && G._dv[q][t2] === G._dv[q][t2]) w.push(G._dv[q][t2]); if(w.length){ w.sort(function(a, b){ return a - b; }); var h = w.length >> 1; G._dvMed[t2] = w.length & 1 ? w[h] : (w[h-1] + w[h])/2; } } }
      for(var t3=0; t3<T; t3++){ var d = G._dv[j][t3], m = G._dvMed[t3]; if(d === d && m === m) o[t3] = ((d >= m) === (cond === 'liquid')) ? 1 : 0; } return o; }
    throw new Error(cond); }
  function applyCond(G, j, s, cond){ if(!cond || cond === 'none') return s; var T = G.T, o = new Float64Array(T);
    if(cond === 'align'){ var U = G.ctx.mkt_up, D = G.ctx.mkt_down; for(var t=0; t<T; t++){ var v = s[t]; o[t] = v !== v ? NaN : ((v > 0 && U[t]) || (v < 0 && D[t]) ? v : 0); } return o; }
    var g = G.ctx[cond] || coinCond(G, j, cond); for(var t1=0; t1<T; t1++){ var v1 = s[t1]; o[t1] = v1 !== v1 ? NaN : (g[t1] ? v1 : 0); } return o; }
  function applyExit(G, j, s, ex){ if(!ex || ex === 'own') return s; var T = G.T, c = G.c[j], o = new Float64Array(T), A = ex === 'atr3' ? atr(c, G.h[j], G.l[j], 14) : null, N = ex === 't5' ? 5 : ex === 't10' ? 10 : 20, d = 0, entry = -1, ext = NaN, blocked = 0;
    for(var t=0; t<T; t++){ var v = s[t], sg = sgn(v); if(sg !== sg) sg = 0; if(blocked && sg !== blocked) blocked = 0;
      if(sg !== d){ d = (sg === blocked) ? 0 : sg; entry = t; ext = c[t]; }
      if(d){ if(c[t] === c[t]) ext = d > 0 ? Math.max(ext === ext ? ext : c[t], c[t]) : Math.min(ext === ext ? ext : c[t], c[t]);
        var out = A ? (d > 0 ? c[t] < ext - 3*A[t] : c[t] > ext + 3*A[t]) : (t - entry >= N); if(out){ blocked = d; d = 0; } }
      o[t] = v !== v ? NaN : (d ? d*Math.abs(v) : 0); }
    return o; }
  // ── engine ──
  function tsRun(G, signalOf, mode, wantW){ var T = G.T, n = G.syms.length, gross = new Float64Array(T), cost = new Float64Array(T), Ws = wantW ? [] : null;
    for(var j=0; j<n; j++){ var s = signalOf(j), z = G.size[j], E = G.E[j], r = G.r[j], ff = G.ff[j], prev = 0, wPrev = 0, wPrev2 = 0, W = wantW ? new Float64Array(T) : null;
      for(var t=0; t<T; t++){ var sv = s[t]; if(mode === 'LF' && sv < 0) sv = 0; var want = (E[t] && sv === sv) ? sv*z[t] : NaN, cur = prev;
        if(want !== want) cur = 0; else if(Math.sign(want) !== Math.sign(prev) || Math.abs(want - prev) > 0.15) cur = want;
        prev = cur; var w = G.N[t] > 0 ? cur/G.N[t] : 0;
        if(t >= 1){ var rr = r[t]; gross[t] += wPrev*(rr === rr ? rr : 0) - wPrev*ff[t]; cost[t] += Math.abs(wPrev - wPrev2)*PERP; }
        wPrev2 = wPrev; wPrev = w; if(W) W[t] = w; }
      if(Ws) Ws.push(W); }
    return { gross:gross, cost:cost, W:Ws }; }
  function xsWeights(G, scoreOf, mode, daily, gate){ var T = G.T, n = G.syms.length, S = [], W = []; for(var j=0; j<n; j++){ S.push(scoreOf(j)); W.push(new Float64Array(T)); }
    var cur = new Float64Array(n), any = false;
    for(var t=0; t<T; t++){ var reb = daily || new Date((t + G.K0)*DAY).getUTCDay() === 0;
      if(reb){ any = true; var el = []; for(var j1=0; j1<n; j1++){ var v = S[j1][t]; if(G.E[j1][t] && v === v) el.push(j1); } cur = new Float64Array(n);
        if(el.length >= 10){ var k = Math.max(1, Math.round(el.length*0.2)); el.sort(function(a, b){ return (S[a][t] - S[b][t]) || (a - b); }); var top = el.slice(-k), bot = el.slice(0, k);
          if(mode === 'LS'){ top.forEach(function(q){ cur[q] = 0.5/k; }); bot.forEach(function(q){ cur[q] = -0.5/k; }); }
          else if(mode === 'NEG'){ top.forEach(function(q){ cur[q] = -0.5/k; }); bot.forEach(function(q){ cur[q] = 0.5/k; }); }
          else if(mode === 'LO'){ top.forEach(function(q){ cur[q] = 1/k; }); } } }
      for(var j2=0; j2<n; j2++) W[j2][t] = (any && G.E[j2][t]) ? cur[j2]*(gate ? gate[t] : 1) : 0; }
    return W; }
  function wRun(G, W){ var T = G.T, gross = new Float64Array(T), cost = new Float64Array(T);
    for(var j=0; j<W.length; j++){ var w = W[j], r = G.r[j], ff = G.ff[j]; for(var t=1; t<T; t++){ var P = w[t-1]; if(P){ var rr = r[t]; gross[t] += P*(rr === rr ? rr : 0) - P*ff[t]; } cost[t] += Math.abs(w[t-1] - (t >= 2 ? w[t-2] : 0)); } }
    for(var t1=0; t1<T; t1++) cost[t1] *= PERP; return { gross:gross, cost:cost }; }
  // the harvest, with the Edge Lab's new guards (opt.exitNeg: close a pair the day its funding sum falls below this; opt.old: coins listed over a year; opt.liquid; opt.cap: skip a coin whose 30-day weekly funding is above this)
  function harvest(G, opt){ var k = opt.k, hurdle = opt.hurdle, T = G.T, n = G.syms.length, gross = new Float64Array(T), cost = new Float64Array(T), S30 = [], cov = [], held = {}, live = {}, baskets = [];
    for(var j=0; j<n; j++){ var s = rsum(G.fi[j], 30); for(var t=0; t<T; t++) s[t] = s[t]/1e8*7/30; S30.push(s); var has = new Float64Array(T); for(var t1=0; t1<T; t1++) has[t1] = G.fc[j][t1] > 0 ? 1 : 0; cov.push(rsum(has, 7)); }
    var oldC = opt.old ? G.syms.map(function(_, j){ return coinCond(G, j, 'old'); }) : null, liqC = opt.liquid ? G.syms.map(function(_, j){ return coinCond(G, j, 'liquid'); }) : null;
    var sund = []; for(var t2=0; t2<T; t2++) if(new Date((t2 + G.K0)*DAY).getUTCDay() === 0) sund.push(t2);
    function choose(a){ var el = []; for(var j=0; j<n; j++) if(G.E[j][a] && cov[j][a] >= 6 && isFinite(S30[j][a]) && (!oldC || oldC[j][a]) && (!liqC || liqC[j][a]) && (!opt.cap || S30[j][a] <= opt.cap)) el.push(j);
      if(el.length < 5) return {};
      var ord = el.slice().sort(function(x, y){ return S30[y][a] - S30[x][a]; }), rk = {}, i = 0;
      while(i < ord.length){ var e = i; while(e + 1 < ord.length && S30[ord[e+1]][a] === S30[ord[i]][a]) e++; for(var q=i; q<=e; q++) rk[ord[q]] = (i + e + 2)/2; i = e + 1; }
      var want = {}; el.forEach(function(j){ var v = S30[j][a]; if(rk[j] <= k && v > hurdle) want[j] = 1; if(held[j] && rk[j] <= 2*k && v > 0) want[j] = 1; });
      var ks = Object.keys(want).map(Number); if(ks.length > k){ ks.sort(function(x, y){ return (S30[y][a] - S30[x][a]) || ((held[x] ? 0 : 1) - (held[y] ? 0 : 1)) || (G.syms[x] < G.syms[y] ? -1 : 1); }); ks = ks.slice(0, k); }
      var o = {}; ks.forEach(function(j){ o[j] = 1; }); return o; }
    for(var q=0; q+1<sund.length; q++){ var a = sund[q], b = sund[q+1], want = choose(a), ch = 0;
      Object.keys(want).forEach(function(j){ if(!live[j]) ch++; }); Object.keys(live).forEach(function(j){ if(!want[j]) ch++; });
      cost[a+1] += ch*(1/k)*(SPOT + PERP); live = {}; Object.keys(want).forEach(function(j){ live[j] = 1; });
      for(var t=a+1; t<=b; t++) Object.keys(live).forEach(function(j){ gross[t] += (1/k)*G.ff[j][t]; if(opt.exitNeg != null && G.ff[j][t] < opt.exitNeg){ delete live[j]; if(t + 1 < T) cost[t+1] += (1/k)*(SPOT + PERP); } });
      baskets.push({ a:a + G.K0, hold:Object.keys(want).map(function(j){ return G.syms[j]; }).sort() }); held = want; }
    var last = sund.length ? sund[sund.length - 1] : null, cur = null;
    if(last != null){ var prevHeld = held, w = choose(last); cur = { a:last + G.K0, hold:Object.keys(w).map(function(j){ return G.syms[j]; }).sort(), prev:Object.keys(prevHeld).map(function(j){ return G.syms[j]; }).sort() }; }
    return { gross:gross, cost:cost, current:cur, baskets:baskets }; }
  // ── a candidate: base rule × condition × exit, or a new family ──
  function run(G, cand, opt){ opt = opt || {}; var b = cand.base ? BASES.filter(function(x){ return x.name === cand.base; })[0] : null, cond = cand.cond || 'none', ex = cand.exit || 'own';
    if(cand.kind === 'harvest') return harvest(G, cand.h);
    if(cand.kind === 'blend'){ var g = new Float64Array(G.T), c = new Float64Array(G.T); cand.parts.forEach(function(p){ var R = run(G, p[0], opt); for(var t=0; t<G.T; t++){ g[t] += p[1]*R.gross[t]; c[t] += p[1]*R.cost[t]; } }); return { gross:g, cost:c }; }
    if(cand.kind === 'model'){ var XM = window.OMEGA_XSMODEL; if(!XM) throw new Error('the model module is missing'); var SM = XM.scores(G, cand.from), WM = xsWeights(G, function(j){ return SM[j]; }, 'LS', false), RM = wRun(G, WM); if(opt.wantW) RM.W = WM; return RM; }   // v6.5.73: round 14's frozen model
    if(cand.kind === 'agexs'){ var W = xsWeights(G, function(j){ return score(G, j, 'age'); }, cand.mode, false), RA = wRun(G, W); if(opt.wantW) RA.W = W; return RA; }
    if(cand.kind === 'fundprice') return tsRun(G, function(j){ return SIG.fundVsPrice(G, j); }, cand.mode, opt.wantW);
    if(!b) throw new Error('unknown base ' + cand.base);
    if(b.kind === 'xs'){ var gate = cond === 'none' ? null : G.ctx[cond]; var W2 = xsWeights(G, function(j){ return b.f(G, j); }, b.mode, false, gate); var R2 = wRun(G, W2); if(opt.wantW) R2.W = W2; return R2; }
    var cache = opt.sigCache; return tsRun(G, function(j){ var s = cache && cache[j] ? cache[j] : b.f(G, j); if(cache && !cache[j]) cache[j] = s; var f = applyCond(G, j, s, cond); if(cand.cond2) f = applyCond(G, j, f, cand.cond2); return applyExit(G, j, f, ex); }, b.mode, opt.wantW); }
  // ── judging: weekly alpha against the equal-weight market of the same coins ──
  function weekEnd(day){ var dow = new Date(day*DAY).getUTCDay(); return dow === 0 ? day : day + (7 - dow); }
  function nwT(x, lag){ lag = lag || 2; var n = x.length; if(n < 8) return null; var m = 0; for(var i=0; i<n; i++) m += x[i]; m /= n; var e = x.map(function(v){ return v - m; }), g0 = 0; e.forEach(function(v){ g0 += v*v; }); var lrv = g0/n;
    for(var k=1; k<=lag; k++){ var s = 0; for(var q=k; q<n; q++) s += e[q]*e[q-k]; lrv += 2*(1 - k/(lag + 1))*s/(n - k); } return lrv > 0 ? m/Math.sqrt(lrv/n) : null; }
  function judge(G, R, startDay, endDay){ var wk = [], cur = null, T = G.T, eq = 1, pk = 1, dd = 0;
    for(var t=0; t<T; t++){ var d = t + G.K0; if(d < startDay || d >= endDay) continue; var x1 = R.gross[t] - R.cost[t], x2 = R.gross[t] - 2*R.cost[t], we = weekEnd(d);
      if(!cur || cur.e !== we){ cur = { e:we, x:0, x2:0, m:0 }; wk.push(cur); } cur.x += x1; cur.x2 += x2; cur.m += G.m[t]; eq *= 1 + x1; if(eq > pk) pk = eq; if(eq/pk - 1 < dd) dd = eq/pk - 1; }
    var n = wk.length, sa = 0; wk.forEach(function(w){ sa += Math.abs(w.x); });
    if(n < 30 || sa === 0) return { weeks:n, ann:0, alpha:0, z:0, beta:0, years:{}, ypos:0, ny:0, costs2x:0, worst:0 };
    var mx = 0, mm = 0; wk.forEach(function(w){ mx += w.x; mm += w.m; }); mx /= n; mm /= n; var cxm = 0, vm = 0; wk.forEach(function(w){ cxm += (w.x - mx)*(w.m - mm); vm += (w.m - mm)*(w.m - mm); });
    var b = vm > 0 ? cxm/vm : 0, a = wk.map(function(w){ return w.x - b*w.m; }), a2 = wk.map(function(w){ return w.x2 - b*w.m; }), yrs = {}, cnt = {};
    wk.forEach(function(w, i){ var y = new Date(w.e*DAY).getUTCFullYear(); yrs[y] = (yrs[y] || 0) + a[i]; cnt[y] = (cnt[y] || 0) + 1; });
    var full = Object.keys(yrs).filter(function(y){ return cnt[y] >= 26; }), mean = function(x){ return x.reduce(function(p, q){ return p + q; }, 0)/x.length; };
    return { weeks:n, ann:100*mx*52, alpha:100*mean(a)*52, z:nwT(a) || 0, beta:b, years:yrs, ypos:full.filter(function(y){ return yrs[y] > 0; }).length, ny:full.length, costs2x:100*mean(a2)*52, worst:100*dd, a:a, ends:wk.map(function(w){ return w.e; }) }; }
  // ── the explorer's candidates (PLAN13 addendum A): every one untested by research ──
  function candidates(known, priority, tier){ tier = tier || 1; var out = [], seen = {}; function add(c){ c.key = c.key || (c.base + '|' + (c.cond || 'none') + '|' + (c.exit || 'own')); if(seen[c.key] || (known && known[c.key])) return; seen[c.key] = 1; out.push(c); }
    // new families first: they come from the lessons
    [-0.0005, -0.001, -0.003].forEach(function(x){ add({ key:'harvest 10 pairs, close a pair when its daily funding is below ' + (100*x).toFixed(2) + '%', kind:'harvest', h:{ k:10, hurdle:0.001, exitNeg:x }, fam:'harvest guard', tier:0 }); });
    add({ key:'harvest 10 pairs, coins listed over a year only', kind:'harvest', h:{ k:10, hurdle:0.001, old:true }, fam:'harvest guard', tier:0 });
    add({ key:'harvest 10 pairs, the more liquid half only', kind:'harvest', h:{ k:10, hurdle:0.001, liquid:true }, fam:'harvest guard', tier:0 });
    add({ key:'harvest 10 pairs, listed over a year and liquid, close on daily funding below -0.10%', kind:'harvest', h:{ k:10, hurdle:0.001, old:true, liquid:true, exitNeg:-0.001 }, fam:'harvest guard', tier:0 });
    add({ key:'harvest 10 pairs, skip coins paying over 1% a week', kind:'harvest', h:{ k:10, hurdle:0.001, cap:0.01 }, fam:'harvest guard', tier:0 });
    add({ key:'XS coin age: long the oldest fifth, short the newest fifth', kind:'agexs', mode:'LS', fam:'coin age', tier:0 });
    add({ key:'XS coin age: long the oldest fifth only', kind:'agexs', mode:'LO', fam:'coin age', tier:0 });
    add({ key:'funding against price LS', kind:'fundprice', mode:'LS', fam:'funding vs price', tier:0 });
    add({ key:'funding against price LF', kind:'fundprice', mode:'LF', fam:'funding vs price', tier:0 });
    var order = BASES.slice().sort(function(a, b){ return (priority[b.name] || 0) - (priority[a.name] || 0); });
    // tier 1: base × one condition × exit
    order.forEach(function(b){ var conds = b.kind === 'xs' ? ['none'].concat(XS_CONDS) : ['none'].concat(MARKET_CONDS, COIN_CONDS), exits = b.kind === 'xs' ? ['own'] : ['own', 't5', 't10', 't20', 'atr3'];
      conds.forEach(function(cd){ exits.forEach(function(ex){ if(cd === 'none' && ex === 'own') return; add({ base:b.name, cond:cd, exit:ex, fam:b.fam, tier:1 }); }); }); });
    // tier 2 (after tier 1 is done): base × one market condition × one coin condition, own exit
    if(tier >= 2) order.forEach(function(b){ if(b.kind === 'xs') return; MARKET_CONDS.forEach(function(mc){ COIN_CONDS.forEach(function(cc){ add({ key:b.name + '|' + mc + '+' + cc + '|own', base:b.name, cond:mc, cond2:cc, exit:'own', fam:b.fam, tier:2 }); }); }); });
    return out.filter(function(c){ return (c.tier || 0) <= tier; }); }
  function label(c){ if(!c.base) return c.key; var t = c.base; if(c.cond && c.cond !== 'none') t += ', ' + COND_TEXT[c.cond]; if(c.cond2) t += ' and ' + COND_TEXT[c.cond2].replace(/^only /, ''); if(c.exit && c.exit !== 'own') t += ', ' + EXIT_TEXT[c.exit]; return t; }
  window.OMEGA_EDGELIB = { label:label, grid:grid, subgrid:subgrid, run:run, judge:judge, harvest:harvest, candidates:candidates, BASES:BASES, COND_TEXT:COND_TEXT, EXIT_TEXT:EXIT_TEXT, weekEnd:weekEnd, nwT:nwT,
    _:{ rsum:rsum, rmean:rmean, rstd:rstd, rmax:rmax, rmin:rmin, rrank:rrank, rmedian:rmedian, ewmA:ewmA, rsi:rsi, atr:atr, applyCond:applyCond, applyExit:applyExit, coinCond:coinCond, tsRun:tsRun, xsWeights:xsWeights, wRun:wRun, SIG:SIG } };
})();
</script>
