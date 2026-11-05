// v6.5.71 checks (Node + the smoke harness): CREED's replay measures setups shown on time on their own; the history card,
// the scoreboard and the verdict use them; the backtest offers entry when shown; the two research downloads pick and
// encode exactly what PLAN14 addendum A fixed.
// usage: HARNESS=<folder with smoke.js, fake_idb.js> node s71_test.js omega-v6_5-71.html
const smoke=require((process.env.HARNESS||'.')+'/smoke.js'), fakeIDB=require((process.env.HARNESS||'.')+'/fake_idb.js'), fs=require('fs'), cp=require('child_process'), zlib=require('zlib'), path=require('path');
let pass=0,fail=0; const ok=(n,c,x)=>{c?(pass++,console.log('  ok   '+n)):(fail++,console.log('  FAIL '+n+(x!==undefined?' — '+JSON.stringify(x).slice(0,600):'')));};
const FILE=process.argv[2]; const sleep=ms=>new Promise(r=>setTimeout(r,ms)); const html=fs.readFileSync(FILE,'utf8');
function rng(seed){ let s=seed>>>0; return ()=>{ s=(s+0x6D2B79F5)>>>0; let t=s; t=Math.imul(t^(t>>>15),t|1); t^=t+Math.imul(t^(t>>>7),t|61); return ((t^(t>>>14))>>>0)/4294967296; }; }
// 15-minute bars with swings (so CREED finds structure, sweeps and acceptances), 360 days
function bars15(seed){ const r=rng(seed), n=360*96, t0=Math.floor(Date.UTC(2026,3,1)/1000), out=[]; let p=100, ph=0;
  for(let i=0;i<n;i++){ ph+=0.004+0.006*r(); const drift=0.0012*Math.sin(ph)+0.0006*Math.sin(i/500); const ret=drift+0.003*(r()+r()+r()-1.5); const o=p, c=p*Math.exp(ret);
    const h=Math.max(o,c)*(1+0.0015*r()), l=Math.min(o,c)*(1-0.0015*r()); out.push({ time:t0+i*900, o, h, l, c, v:1+r(), partial:false }); p=c; }
  return out; }
function resample(rows, k){ const out=[]; for(let i=0;i+k<=rows.length;i+=k){ const g=rows.slice(i,i+k); out.push({ time:g[0].time, o:g[0].o, h:Math.max(...g.map(x=>x.h)), l:Math.min(...g.map(x=>x.l)), c:g[k-1].c, v:g.reduce((a,x)=>a+x.v,0), partial:false }); } return out; }
async function settle(G, p){ let v, e, done=false; p.then(x=>{ v=x; done=true; }, x=>{ e=x; done=true; }); for(let q=0;q<200000 && !done;q++){ await G.drain(20); await sleep(0); } if(e) throw e; return v; }
(async()=>{
  const G=smoke(FILE, { omega_jfix_v2:'1', omega_jfix_v3:'1' }, { indexedDB:fakeIDB() }); await G.drain(40); await sleep(5); await G.drain(40);
  const W=G.ctx, H=W.OMEGA_HISTORY, O=W.OMEGA_OPERATOR;
  // ── 1. the replay, version 10 ──
  const m15=bars15(71), m1=resample(m15,4), m4=resample(m15,16);
  H.load=async()=>({ n:2, t:[m15[0].time/60, m15[m15.length-1].time/60] }); H.resampleA=async(s, mins)=>mins===15?m15:mins===60?m1:m4; H.summary=()=>({ src:'Binance', last:m15[m15.length-1].time/60, n:m15.length });
  const t0=Date.now(); const out=await settle(G, O.creedReplay('ZZZUSDT')); console.log('  replay:', out && out.ready.n, 'setups,', out && out.onTime && out.onTime.n, 'on time,', Math.round((Date.now()-t0)/1000)+'s');
  ok('the replay is version 10 and re-runs every market replayed before it', out && out.v===10 && /\(prev\.v \|\| 0\) < 10 \|\|/.test(html));
  const T=out.trades, on=T.filter(x=>x.lag===0), late=T.filter(x=>x.lag>0);
  ok('setups shown on time are counted on their own: every setup is either on time or late', out.ready.n>5 && out.ready.n<=300 && out.onTime.n===on.length && on.length+late.length===out.ready.n && late.length>0, { n:out.ready.n, on:on.length, late:late.length });
  const R=on.reduce((a,x)=>a+x.r,0), C=on.reduce((a,x)=>a+(x.c||0),0);
  ok('their totals are the sums of their own trades (before and after costs)', Math.abs(out.onTime.all.R-R)<1e-9 && Math.abs(out.onTime.all.net-(R-C))<1e-9 && Math.abs(out.onTime.all.netAvg-(R-C)/on.length)<1e-12);
  ok('breakeven-off and three-tier versions use the same on-time setups', out.onTime.beOff.n===on.filter(x=>x.nb!=null).length && out.onTime.tiers.n===on.filter(x=>x.tr!=null).length && Math.abs(out.onTime.share-on.length/out.ready.n)<1e-12);
  ok('earlier and later parts split the on-time setups at the replay’s cut', out.onTime.early.n+out.onTime.late.n===on.length && out.onTime.early.n===on.filter(x=>x.t<out.cut).length);
  // ── 2. the verdict, the card, the scoreboard, the signal list ──
  const cv=W.OMEGA_EXPLORE.creedVerdict();
  ok('the CREED verdict adds up the on-time setups of every replayed market', cv.onTime && cv.onTime.markets===1 && cv.onTime.n===on.length && Math.abs(cv.onTime.avg-(R-C)/on.length)<1e-12 && Math.abs(cv.onTime.gross-R/on.length)<1e-12);
  try{ O.render(); }catch(e){ ok('the Autopilot page renders', false, String(e)); } const card=(W.document.getElementById('opCreed')||{}).innerHTML||'';
  ok('the CREED history card leads with the honest record and labels the total as hindsight', card.indexOf('CREED’s honest record: setups shown on time')>-1 && card.indexOf('Total as taught (counts hindsight)')>-1 && card.indexOf('Shown on time, a trade after costs')>-1, card.slice(0,300));
  ok('the scoreboard and the signal list read on-time figures', /cs \+= o\.netAvg\*o\.n/.test(html) && html.indexOf("label:'CREED replayed on stored history, a setup shown on time, after costs'")>-1 && (html.match(/setups shown on time, ' : ' setups as taught \(counts hindsight\), '/g)||[]).length===2);
  // ── 3. the backtest's entry choice ──
  const sel=html.match(/<select id="creedBtEntryWhen"[^>]*>([\s\S]*?)<\/select>/);
  ok('the CREED Backtest offers the entry when shown (first, the default) or as taught', sel && /^<option value="shown">/.test(sel[1]) && /value="taught"/.test(sel[1]) && /entryWhen: \(function\(\)\{ var c = el\('creedBtEntryWhen'\); return c && c\.value === 'taught' \? 'taught' : 'shown'; \}\)\(\)/.test(html));
  ok('a setup shown late is entered at the close it is shown on, and skipped if price is already past the stop or target', /if\(cfg\.entryWhen === 'shown' && lateBars > 0\)\{ entryPx = \+bar\.c;/.test(html) && /BT\.skippedLate = \(BT\.skippedLate \|\| 0\) \+ 1; entryPx = NaN;/.test(html));
  // ── 4–5. v6.5.82 retired the round-14 downloads (data collected and used; code kept in the build kit) ──
  ok('the round-14 final-test and CREED 15-minute downloads are retired on purpose (v6.5.82)', !W.OMEGA_FINAL4EXPORT && !W.OMEGA_CREED15EXPORT && /ROUND 14 FINAL TEST DATA/.test(fs.readFileSync(path.join(__dirname, 'final4export.js'), 'utf8')));
  console.log('\n'+pass+' passed, '+fail+' failed'); process.exit(fail?1:0);
})().catch(e=>{ console.log('CRASH', e && e.stack); process.exit(1); });
