// v6.5.48 checks (Node, with the smoke harness): CREED's replay measures after the as-taught walk use the setup's own stop.
// usage: node s48_test.js OLD(v6.5.47).html NEW(v6.5.48).html   (smoke.js and fake_idb.js from the verification bundle)
const smoke=require(process.env.HARNESS ? process.env.HARNESS+'/smoke.js' : './smoke.js'), fakeIDB=require(process.env.HARNESS ? process.env.HARNESS+'/fake_idb.js' : './fake_idb.js'), fs=require('fs');
let pass=0,fail=0; const ok=(n,c,x)=>{c?(pass++,console.log('  ok   '+n)):(fail++,console.log('  FAIL '+n+(x!==undefined?' — '+JSON.stringify(x).slice(0,500):'')));};
const [OLD, NEW]=process.argv.slice(2); const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function replay(file, seed, vol){ const G=smoke(file, { omega_jfix_v2:'1', omega_jfix_v3:'1' }, { indexedDB:fakeIDB() }); await G.drain(40); await sleep(5); await G.drain(40); const n=60*24*150;
  const t=new Uint32Array(n), o=new Float32Array(n), h=new Float32Array(n), l=new Float32Array(n), c=new Float32Array(n), v=new Float32Array(n), tb=new Float32Array(n); const t0=Math.floor(Date.UTC(2025,0,1)/60000); let sd=seed, px=100; const rn=()=>{ sd=(sd*1664525+1013904223)%4294967296; return sd/4294967296; };
  for(let i=0;i<n;i++){ t[i]=t0+i; const nx=px*(1+(rn()-0.5)*vol); o[i]=px; c[i]=nx; h[i]=Math.max(px,nx)*(1+rn()*vol/3); l[i]=Math.min(px,nx)*(1-rn()*vol/3); v[i]=1+rn(); tb[i]=v[i]/2; px=nx; }
  const ser={ sym:'AAAUSDT', n, t, o, h, l, c, v, tb }; const H=G.ctx.OMEGA_HISTORY; H.load=async()=>ser; H.summary=()=>({ n, src:'Binance', last:t[n-1] });
  let out; G.ctx.OMEGA_OPERATOR.creedReplay('AAAUSDT').then(x=>out=x); for(let k=0;k<30000 && !out;k++){ await G.drain(50); await sleep(1); } return { out, errors:G.errors }; }
const strip=tr=>tr.map(t=>{ const o={}; ['t','lag','d','r','c','w','k','sp','m','h','tr','nb'].forEach(k=>{ if(t[k]!==undefined) o[k]=t[k]; }); return o; });
const per=x=>x && x.n ? +(x.net/x.n).toFixed(3) : null;
(async()=>{
  const html=fs.readFileSync(NEW,'utf8'); const rows=[]; let same=true, moreFills=true, moreTaken=true, allLate=[0,0,0,0];
  for(const [seed, vol] of [[7,0.003],[11,0.003],[19,0.004],[23,0.002]]){
    const A=(await replay(OLD, seed, vol)).out, B=(await replay(NEW, seed, vol)).out;
    if(JSON.stringify(A.ready)!==JSON.stringify(B.ready) || JSON.stringify(A.rejected)!==JSON.stringify(B.rejected) || JSON.stringify(strip(A.trades))!==JSON.stringify(strip(B.trades))) same=false;
    const lateA=A.trades.filter(t=>t.lag>0), lateB=B.trades.filter(t=>t.lag>0);
    allLate[0]+=lateA.filter(t=>t.rl!=null).length; allLate[1]+=lateB.filter(t=>t.rl!=null).length; allLate[2]+=lateA.filter(t=>t.rd!=null).length; allLate[3]+=lateB.filter(t=>t.rd!=null).length;
    rows.push({ seed, setups:A.ready.n, late:lateA.length, asTaught:per(A.ready), v47:{ market:per(A.takeMarket.all), marketN:A.takeMarket.all.n, limit:per(A.takeLimit.all), limitN:A.takeLimit.all.n }, v48:{ market:per(B.takeMarket.all), marketN:B.takeMarket.all.n, limit:per(B.takeLimit.all), limitN:B.takeLimit.all.n }, v:B.v, costKey:B.costKey }); }
  console.log(JSON.stringify(rows, null, 1));
  ok('CREED as taught is unchanged: every setup taken and turned down, every trade, on 4 random-walk histories', same);
  ok('replay version 9, and it records the cost it used', rows.every(r=>r.v===9 && +r.costKey>0), rows.map(r=>[r.v, r.costKey]));
  ok('late setups that later reached +1R are no longer dropped: more are tradeable when shown and more limit orders fill (v6.5.47 used a stop at the entry for them)', allLate[3]>=allLate[2] && allLate[1]>allLate[0], allLate);
  ok('the as-taken figures (market and limit) come only from version-9 replays; the Avoid list and the lens too', (html.match(/\(x\.v \|\| 0\) < 9\) return;/g)||[]).length>=2 && /\(x\.v \|\| 0\) >= 9 && Array\.isArray\(x\.lens\)/.test(html));
  ok('a market is replayed again when the cost setting changes', /\|\| \(prev\.v \|\| 0\) < 9 \|\| \(prev\.costKey \|\| ''\) !== replayCostKey\(sym, \(sm && sm\.src\) \|\| ''\)/.test(html));
  ok('a crypto cost above 0.5% round trip gets a plain check next to the input', /Check: you entered ' \+ costs\.cryptoPct \+ '% round trip for crypto/.test(html));
  console.log('\n'+pass+' passed, '+fail+' failed'); process.exit(fail?1:0);
})().catch(e=>{ console.log('CRASH', e.stack); process.exit(1); });
