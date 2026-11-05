// v6.5.50: the research data export round-trips: decoding the file gives back the hourly bars exactly (to the stated precision).
const smoke=require((process.env.HARNESS||'.')+'/smoke.js'), fakeIDB=require((process.env.HARNESS||'.')+'/fake_idb.js');
let pass=0,fail=0; const ok=(n,c,x)=>{c?(pass++,console.log('  ok   '+n)):(fail++,console.log('  FAIL '+n+(x!==undefined?' — '+JSON.stringify(x).slice(0,400):'')));};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ const G=smoke(process.argv[2], { omega_jfix_v2:'1', omega_jfix_v3:'1' }, { indexedDB:fakeIDB() }); await G.drain(40); await sleep(5); await G.drain(40);
  const W=G.ctx, H=W.OMEGA_HISTORY; let sd=5; const rn=()=>{ sd=(sd*1664525+1013904223)%4294967296; return sd/4294967296; };
  const mk=(base, n)=>{ const t=new Uint32Array(n), o=new Float32Array(n), h=new Float32Array(n), l=new Float32Array(n), c=new Float32Array(n), v=new Float32Array(n), tb=new Float32Array(n), t0=Math.floor(Date.UTC(2026,0,1)/60000); let p=base;
    for(let i=0;i<n;i++){ const nx=p*(1+(rn()-0.5)*0.003); t[i]=t0+i; o[i]=p; c[i]=nx; h[i]=Math.max(p,nx)*1.0005; l[i]=Math.min(p,nx)*0.9995; v[i]=10+rn()*5; tb[i]=v[i]*rn(); p=nx; } return { n, t, o, h, l, c, v, tb }; };
  const M={ BTCUSDT:mk(83000, 60*24*20), XRPUSDT:mk(0.52, 60*24*20), 'EUR/USD':mk(1.084, 60*24*10) }; H.index=()=>({ BTCUSDT:{}, XRPUSDT:{}, 'EUR/USD':{} }); H.load=async(s)=>M[s]; H.summary=s=>({ src:'test' });
  const FUND=[]; for(let k=0;k<60;k++) FUND.push([Date.UTC(2026,0,1)+k*8*3600e3, (k%7-3)*1e-5]); W.OMEGA_DERIV.load=async(s)=>(s==='BTCUSDT' ? { sym:s, fund:FUND, oi:[[Date.UTC(2026,0,5), 100, 8.3e9]], liq:{} } : { sym:s, fund:[], oi:[], liq:{} });
  let D; W.OMEGA_HISTEXPORT.build().then(x=>D=x); for(let k=0;k<20000 && !D;k++){ await G.drain(20); await sleep(1); }
  let worst=0, nbars=0;
  for(const m of D.markets){ const rows=(await new Promise(r=>{ let x; H.resampleA(M[m.sym], 60).then(v=>x=v); (async()=>{ for(let k=0;k<20000 && !x;k++){ await G.drain(20); await sleep(1); } r(x); })(); })).filter(r=>!r.partial), sc=Math.pow(10,m.dp);
    let t=0, c=0; for(let i=0;i<m.n;i++){ t+=m.t[i]; c+=m.c[i]; const o=c+m.o[i], hh=Math.max(c,o)+m.h[i], ll=Math.min(c,o)-m.l[i], r=rows[i];
      const e=Math.max(Math.abs(c/sc-r.c), Math.abs(o/sc-r.o), Math.abs(hh/sc-r.h), Math.abs(ll/sc-r.l))/r.c; if(e>worst) worst=e; if(t*3600!==r.time) worst=1; nbars++; } }
  ok('every stored market is exported, hourly, and decodes back to the same bars (times exact, prices within the stated precision)', D.format==='omega-history' && D.markets.length===3 && nbars>1000 && worst<2e-5, { worst, nbars, n:D.markets.map(m=>[m.sym, m.n, m.dp]) });
  { const m=D.markets.find(x=>x.sym==='BTCUSDT'); let t=0, ok2=true; for(let i=0;i<m.fund.t.length;i++){ t+=m.fund.t[i]; if(t*60000!==FUND[i][0] || Math.abs(m.fund.r[i]/1e7-FUND[i][1])>1e-9) ok2=false; }
    ok('v2: funding history is exported and decodes back exactly; markets without it carry none', D.v===2 && ok2 && m.fund.t.length===60 && !D.markets.find(x=>x.sym==='XRPUSDT').fund && m.oi && m.oi.v[0]===8.3e9, [D.v, m.fund && m.fund.t.length]); }
  ok('prices only: no keys, no journal, no settings in the file', !/apiKey|token|secret|journal|password/i.test(JSON.stringify(D)));
  ok('a button on the OMEGA Strategy page, beside the report export', /id="histExportBtn"|id=\\"histExportBtn\\"/.test(require('fs').readFileSync(process.argv[2],'utf8')));
  ok('no runtime errors', G.errors.length===0, G.errors);
  console.log('\n'+pass+' passed, '+fail+' failed'); process.exit(fail?1:0); })().catch(e=>{ console.log('CRASH', e.stack); process.exit(1); });
