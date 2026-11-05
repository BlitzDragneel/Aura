// v6.5.49 checks (Node + the smoke harness): the Strategy Workshop on synthetic markets.
// usage: HARNESS=<folder with smoke.js, fake_idb.js> node s49_test.js omega-v6_5-49.html
const smoke=require((process.env.HARNESS||'.')+'/smoke.js'), fakeIDB=require((process.env.HARNESS||'.')+'/fake_idb.js'), fs=require('fs');
let pass=0,fail=0; const ok=(n,c,x)=>{c?(pass++,console.log('  ok   '+n)):(fail++,console.log('  FAIL '+n+(x!==undefined?' — '+JSON.stringify(x).slice(0,600):'')));};
const FILE=process.argv[2]; const sleep=ms=>new Promise(r=>setTimeout(r,ms));
// 5-minute bars, 700 days; hourly log-returns; optional planted effect: after a fall of 4%+ over 10 hours, a drift up over the next 24 hours
function market(seed, planted){ let sd=seed; const rn=()=>{ sd=(sd*1664525+1013904223)%4294967296; return sd/4294967296; }; const g=()=>{ let u=0; for(let k=0;k<6;k++) u+=rn(); return (u-3)/Math.sqrt(0.5); };
  const H=700*24, hr=new Float64Array(H); let boost=0; const lr=[]; let px=100; const closes=[];
  for(let i=0;i<H;i++){ let r=0.006*g(); if(planted && boost>0){ r+=0.004; boost--; } hr[i]=r; closes.push(px); px*=Math.exp(r);
    if(planted && i>=10){ let s=0; for(let k=i-9;k<=i;k++) s+=hr[k]; if(s<-0.04 && boost===0) boost=24; } }
  const per=12, n=H*per, t=new Uint32Array(n), o=new Float32Array(n), h=new Float32Array(n), l=new Float32Array(n), c=new Float32Array(n), v=new Float32Array(n), tb=new Float32Array(n), t0=Math.floor(Date.UTC(2024,10,1)/60000);
  let p=100; for(let i=0;i<H;i++){ const step=hr[i]/per; for(let k=0;k<per;k++){ const j=i*per+k, nx=p*Math.exp(step+0.0008*g()); t[j]=t0+j*5; o[j]=p; c[j]=nx; h[j]=Math.max(p,nx)*1.0004; l[j]=Math.min(p,nx)*0.9996; v[j]=1+rn(); tb[j]=v[j]*(0.4+0.2*rn()); p=nx; } }
  return { n, t, o, h, l, c, v, tb }; }
async function run(planted){ const G=smoke(FILE, { omega_jfix_v2:'1', omega_jfix_v3:'1' }, { indexedDB:fakeIDB() }); await G.drain(40); await sleep(5); await G.drain(40);
  const W=G.ctx, L=W.OMEGA_LAB, H=W.OMEGA_HISTORY, WS=W.OMEGA_WORKSHOP, syms=['AAAUSDT','BBBUSDT','CCCUSDT','DDDUSDT','EEEUSDT','FFFUSDT'], M={};
  syms.forEach((s,i)=>{ M[s]=Object.assign({ sym:s }, market(101+i*7, planted)); });
  H.load=async(sym)=>M[sym]; H.summary=(sym)=>({ n:M[sym].n, src:'Binance', last:M[sym].t[M[sym].n-1] }); L.cleanSeries=async(sym, s)=>({ s, dq:{ score:100 }, cls:'crypto' });
  const from=M.AAAUSDT.t[0]*60000, to=M.AAAUSDT.t[M.AAAUSDT.n-1]*60000; L.results=()=>({ markets:syms.map(s=>({ sym:s, from, to })), rows:{}, tested:0 });
  const msgs=[]; for(let k=0;k<40;k++){ let m; WS.runNext().then(x=>m=x, e=>m='ERR '+e.stack); for(let q=0;q<20000 && m===undefined;q++){ await G.drain(20); await sleep(1); } msgs.push(m); if(/tested\.$/.test(m)) break; }
  return { G, WS, msgs, st:WS.state(), from, to }; }
(async()=>{
  const A=await run(false); const sa=A.st, R=sa.rounds[0];
  console.log(A.msgs.slice(0,3).join('\n'), '\n…\n', A.msgs.slice(-2).join('\n'));
  ok('a round observes only the first 60% of history and tests on the rest', R && Math.abs(R.designCut - (A.from + 0.6*(A.to - A.from))) < 3600e3 && R.validEnd===A.to && R.phase==='done', R && { cut:R.designCut, phase:R.phase });
  ok('it proposes at most 10 frozen rules, at most two per pair of measurements, each with its observed record', sa.rules.length>0 && sa.rules.length<=10 && sa.proposed===sa.rules.length && sa.rules.every(r=>r.design && r.design.n>=200 && r.design.weeks>=30) && Object.values(sa.rules.reduce((m,r)=>{ m[r.fa+'-'+r.fb]=(m[r.fa+'-'+r.fb]||0)+1; return m; },{})).every(c=>c<=2), sa.rules.map(r=>[r.id, r.fa, r.fb, r.dir]));
  ok('pure random prices: rules are still proposed (the best of 700 cells always looks good), and the test on unseen data passes none', sa.rules.every(r=>r.test && r.status==='FAILED THE TEST'), sa.rules.map(r=>[r.id, r.test && r.test.n, r.test && +(r.test.mean||0).toFixed(3), r.test && r.test.z && +r.test.z.toFixed(2), r.why]));
  ok('the bar counts every rule ever proposed', Math.abs(sa.rules[0].test.bar - (function(){ const N=A.G.ctx.OMEGA_LAB.ncdf; let lo=0,hi=9; for(let k=0;k<60;k++){ const m=(lo+hi)/2; if(1-N(m)>0.05/sa.proposed) lo=m; else hi=m; } return (lo+hi)/2; })())<1e-6);
  const B=await run(true); const sb=B.st, good=sb.rules.filter(r=>r.status==='PASSED — JUDGED FORWARD');
  console.log(sb.rules.map(r=>[r.id, B.WS.ruleText(r), r.test && r.test.n, r.test && +(r.test.mean||0).toFixed(3), r.test && r.test.z && +r.test.z.toFixed(2), r.status]).map(x=>x.join(' | ')).join('\n'));
  ok('a planted effect (a drift up for a day after a sharp fall) is found from observation and passes the test on data it never saw, long', good.length>=1 && good.every(r=>r.dir==='long'), sb.rules.map(r=>[r.id, r.dir, r.status]));
  ok('rules that are the same evidence (mostly the same trades as a stronger passed rule) are noted, not followed twice', good.length < sb.rules.filter(r=>/^PASSED/.test(r.status)).length && sb.rules.filter(r=>r.sameAs).every(r=>good.some(g=>g.id===r.sameAs)), sb.rules.map(r=>[r.id, r.status]));
  ok('a passed rule is then judged only on trades after the round', good.every(r=>r.fwdFrom===sb.rounds[0].validEnd && r.fwd && r.fwd.n===0));
  ok('no look-ahead in the observation: outcomes must end before the design cut', /if\(\(h1\[i\+24\]\.time \+ 3600\)\*1000 > R\.designCut\) break;/.test(fs.readFileSync(FILE,'utf8')));
  ok('the job is registered with the Autopilot as research, and the report carries the workshop', B.G.ctx.OMEGA_OPERATOR.jobs().some(j=>j.id==='workshop') && !!B.G.ctx.OMEGA_STRATEGY.reportForReview().workshop);
  const doc=B.G.ctx.document; const pg=doc.getElementById('page-ostrat'); B.WS.render(); const card=(pg.children||[]).find(c=>c && c.id==='workshopCard');
  ok('the OMEGA Strategy page shows everything the Autopilot researches and the workshop\'s rules', !!card && /Everything the Autopilot researches/.test(card.innerHTML) && /Strategy Workshop/.test(card.innerHTML) && /W1-1/.test(card.innerHTML));
  ok('no runtime errors', A.G.errors.length===0 && B.G.errors.length===0, A.G.errors.concat(B.G.errors).slice(0,3));
  console.log('\n'+pass+' passed, '+fail+' failed'); process.exit(fail?1:0);
})().catch(e=>{ console.log('CRASH', e.stack); process.exit(1); });
