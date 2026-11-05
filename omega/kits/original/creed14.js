// PLAN14 addendum C: CREED's own engine (the app's code, booted in the smoke harness) replayed on the creed15 files.
// Records every setup CREED shows ON TIME (acceptance on the decision bar), exactly as the app's replay finds them, with
// what each variant needs: direction, R after the as-taught exit (stop first, breakeven after 1R), cost in R, the sweep
// candle's 15-minute z, and the times needed to look up the premium without look-ahead.
// usage: HARNESS=/home/claude node creed14.js <build.html> <out.json> <creed15 file> [more files]
const smoke = require((process.env.HARNESS || '.') + '/smoke.js'), fakeIDB = require((process.env.HARNESS || '.') + '/fake_idb.js'), fs = require('fs'), zlib = require('zlib');
const [, , FILE, OUT, ...DATA] = process.argv; const sleep = ms => new Promise(r => setTimeout(r, ms));
function decode(path){ const d = JSON.parse(zlib.gunzipSync(fs.readFileSync(path)).toString()); const tu = d.tunit || 3600, out = {};
  for(const m of d.markets){ const sc = Math.pow(10, m.dp), n = m.t.length, s = { n, t:new Float64Array(n), o:new Float64Array(n), h:new Float64Array(n), l:new Float64Array(n), c:new Float64Array(n), v:new Float64Array(n), tb:new Float64Array(n) };
    let t = 0, c = 0; for(let i=0; i<n; i++){ t += m.t[i]; c += m.c[i]; const o = c + m.o[i], hi = Math.max(c, o) + m.h[i], lo = Math.min(c, o) - m.l[i];
      s.t[i] = t*tu/60; s.c[i] = c/sc; s.o[i] = o/sc; s.h[i] = hi/sc; s.l[i] = lo/sc; s.v[i] = m.v[i]; s.tb[i] = m.tb[i] >= 0 ? m.tb[i]/1000*m.v[i] : NaN; }
    out[m.sym] = s; }
  return out; }
(async () => {
  const G = smoke(FILE, { omega_jfix_v2:'1', omega_jfix_v3:'1' }, { indexedDB:fakeIDB() }); await G.drain(40); await sleep(5); await G.drain(40);
  const W = G.ctx, C = W.OMEGA_CREED, H = W.OMEGA_HISTORY, R = C.rule(), L4 = Math.max(60, R.lookback | 0), L1 = 250, L15 = Math.max(200, (R.scanBars | 0 || 400) + 20);
  console.log('CREED rules:', JSON.stringify(C.ruleForKey ? C.ruleForKey() : R));
  const out = { rules:C.ruleForKey ? C.ruleForKey() : R, coins:{} };
  for(const path of DATA){ const M = decode(path);
    for(const sym of Object.keys(M)){ const s = M[sym], t0 = Date.now();
      const m15 = H.resample(s, 15).filter(r => !r.partial), m1 = H.resample(s, 60).filter(r => !r.partial), m4 = H.resample(s, 240).filter(r => !r.partial);
      const lr = new Float64Array(m15.length).fill(NaN); for(let i=1; i<m15.length; i++) if(m15[i].c > 0 && m15[i-1].c > 0 && m15[i].time - m15[i-1].time === 900) lr[i] = Math.log(m15[i].c/m15[i-1].c);
      function zOf(si){ if(!(lr[si] === lr[si])) return null; let s1 = 0, s2 = 0, n = 0; for(let i = Math.max(1, si - 672); i < si; i++){ const x = lr[i]; if(x === x){ s1 += x; s2 += x*x; n++; } } if(n < 500) return null; const m = s1/n, v = (s2 - n*m*m)/(n - 1); return v > 0 ? lr[si]/Math.sqrt(v) : null; }
      let k1 = 0, k4 = 0; const seen = {}, trades = []; let shown = 0, late = 0; const VC = {}; if(process.env.DBG) console.log('lengths', m15.length, m1.length, m4.length, L4, L15, m15[0], m15[m15.length-1]);
      for(let i = L15; i < m15.length - 1; i++){ const close = m15[i].time + 900;
        while(k1 < m1.length && m1[k1].time + 3600 <= close) k1++; while(k4 < m4.length && m4[k4].time + 14400 <= close) k4++;
        if(k4 < L4 || k1 < 60) continue;
        let a = null; try{ a = C.analyseFor(sym, m4.slice(k4 - L4, k4), m1.slice(Math.max(0, k1 - L1), k1), m15.slice(i - L15 + 1, i + 1), null); }catch(e){ a = null; }
        if(process.env.DBG && a) VC[a.verdict] = (VC[a.verdict] || 0) + 1;
        const lvA = a && a.sweep ? (a.levels || (a.verdict === 'void' && a.rejectedLevels && isFinite(a.rejectedLevels.entry) ? a.rejectedLevels : null)) : null;
        if(!(lvA && (a.verdict === 'ready' || a.verdict === 'counter-trend' || a.verdict === 'void'))) continue;
        const sig = a.sweep.time + '|' + (a.sweep.level ? a.sweep.level.price : ''); if(seen[sig]) continue; seen[sig] = true;
        if(a.verdict !== 'ready') continue; const lv = lvA, rd = Math.abs(lv.entry - lv.stop); if(!(rd > 0) || !isFinite(lv.target)) continue;
        let accAbs = (a.acceptance && a.acceptance.at != null) ? i - L15 + 1 + a.acceptance.at : i; if(!(accAbs >= 0 && accAbs <= i)) accAbs = i;
        shown++; if(accAbs !== i){ late++; continue; }                                      // on time only (PLAN14 addendum C)
        const p = { dir:a.direction, entry:lv.entry, stop:lv.stop, target:lv.target, riskDist:rd }, ex = C.walkExit(p, m15.slice(i + 1, i + 1 + 96*14), { beAtR:1 });
        if(!ex) continue; const r = (p.dir === 'long' ? ex.px - p.entry : p.entry - ex.px)/rd;
        // PLAN14 addendum F: the same setup with other exits (a fresh position each time; a time exit after 14 days)
        const win = m15.slice(i + 1, i + 1 + 96*14), sg = p.dir === 'long' ? 1 : -1, xr = {};
        [['X1', null, 0], ['X2', null, 2], ['X3', 2, 0], ['X4', 1.5, 0]].forEach(function(v){ const q = { dir:p.dir, entry:p.entry, stop:lv.stop, target: v[1] ? p.entry + sg*v[1]*rd : p.target, riskDist:rd };
          const e2 = C.walkExit(q, win, v[2] ? { beAtR:v[2] } : {}), px = e2 ? e2.px : (win.length ? win[win.length - 1].c : p.entry); xr[v[0]] = +((sg*(px - p.entry))/rd).toFixed(6); });
        const si = i - L15 + 1 + a.sweep.bar;
        trades.push({ t:close*1000, d:p.dir === 'long' ? 'L' : 'S', r:+r.toFixed(6), c:+(2*0.0006*p.entry/rd).toFixed(6), w:ex.why, k:a.sweep.level ? a.sweep.level.kind : null, rr:+(Math.abs(lv.target - lv.entry)/rd).toFixed(3),
          x:xr, sweepT:a.sweep.time*1000, sweepClose:(m15[si] ? m15[si].time + 900 : null)*1000, z:zOf(si), sp:+(rd/p.entry).toPrecision(4) });
        if((i & 2047) === 0) await G.drain(5); }
      if(process.env.DBG) console.log('verdicts', JSON.stringify(VC), 'buffer', C.bufferFor ? C.bufferFor(sym, m15[m15.length-1].c) : null);
      out.coins[sym] = { bars:m15.length, from:m15[0].time*1000, to:m15[m15.length-1].time*1000, shown, late, trades };
      console.log(sym, m15.length, 'bars;', shown, 'shown,', late, 'late,', trades.length, 'on time;', Math.round((Date.now() - t0)/1000) + 's');
      fs.writeFileSync(OUT, JSON.stringify(out)); } }
  console.log('done'); process.exit(0);
})().catch(e => { console.log('CRASH', e && e.stack); process.exit(1); });
