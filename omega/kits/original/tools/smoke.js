// Boots an OMEGA build against a DOM stand-in. Elements exist only for ids in the
// file (or ids written later through innerHTML); unknown ids return null, as a
// browser would. Real Storage; short timers fire, long ones are held.
const fs=require('fs'), vm=require('vm');
module.exports=function smoke(file, preset, opts){
  opts=opts||{};
  const html=fs.readFileSync(file,'utf8'), errors=[], held=[];
  const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  // ── storage ──
  class Storage{ constructor(){ this._d={}; } getItem(k){ return Object.prototype.hasOwnProperty.call(this._d,k)?this._d[k]:null; } setItem(k,v){ v=String(v); if(this._quota){ let t=0; for(const kk in this._d) if(kk!==k) t+=kk.length+this._d[kk].length; if(t+k.length+v.length>this._quota){ const e=new Error('QuotaExceededError'); e.name='QuotaExceededError'; throw e; } } this._d[k]=v; } removeItem(k){ delete this._d[k]; } clear(){ this._d={}; } key(i){ return Object.keys(this._d)[i]||null; } get length(){ return Object.keys(this._d).length; } }
  const ls=new Storage(), ss=new Storage(); if(opts.quota) ls._quota=opts.quota; if(preset) Object.keys(preset).forEach(k=>ls.setItem(k,preset[k]));
  // ── elements ──
  const byId={};
  function noop(){ return NOOP; }
  const NOOP=new Proxy(function(){}, { get:(t,k)=> k===Symbol.toPrimitive ? ()=>'' : k==='length'?0 : k==='then'?undefined : NOOP, apply:()=>NOOP, set:()=>true });
  function attrs(tag){ const a={}; for(const m of tag.matchAll(/([\w-:]+)(?:=("([^"]*)"|'([^']*)'|([^\s>]+)))?/g)){ a[m[1].toLowerCase()]= m[3]!=null?m[3]: m[4]!=null?m[4]: m[5]!=null?m[5]:''; } return a; }
  function makeEl(tagName, at, inner){
    const listeners={}, style={ setProperty(k,v){ this[k]=v; }, removeProperty(k){ delete this[k]; }, getPropertyValue(k){ return this[k]||''; } }, cls=new Set((at['class']||'').split(/\s+/).filter(Boolean));
    if(at.style){ at.style.split(';').forEach(p=>{ const i=p.indexOf(':'); if(i>0){ const k=p.slice(0,i).trim().replace(/-([a-z])/g,(_,c)=>c.toUpperCase()); style[k]=p.slice(i+1).trim(); } }); }
    let opts=[];
    if(tagName==='select' && inner!=null){ for(const m of inner.matchAll(/<option([^>]*)>([\s\S]*?)<\/option>/g)){ const oa=attrs(m[1]); opts.push(makeOpt(oa.value!=null?oa.value:m[2].replace(/<[^>]+>/g,'').trim(), m[2].replace(/<[^>]+>/g,'').trim(), 'selected' in oa)); } }
    const e={ tagName:tagName.toUpperCase(), nodeName:tagName.toUpperCase(), id:at.id||'', style, dataset:{}, _l:listeners, _html:inner||'', textContent:(inner||'').replace(/<[^>]+>/g,''),
      type:at.type||'', name:at.name||'', placeholder:at.placeholder||'', disabled:'disabled' in at, hidden:'hidden' in at, checked:'checked' in at, title:at.title||'', href:at.href||'',
      min:at.min, max:at.max, step:at.step, children:[], childNodes:[], parentNode:null, parentElement:null, scrollTop:0, scrollHeight:0, clientWidth:800, clientHeight:400, offsetWidth:800, offsetHeight:400,
      get options(){ return opts; }, set options(v){},
      get selectedIndex(){ const i=opts.findIndex(o=>o.selected); return i<0?(opts.length?0:-1):i; }, set selectedIndex(i){ opts.forEach((o,j)=>o.selected=j===i); },
      get selectedOptions(){ return this._selOpts || opts.filter(o=>o.selected); }, set selectedOptions(v){ this._selOpts=v; },
      get value(){ if(tagName==='select'){ const o=opts.find(o=>o.selected)||opts[0]; return this._v!=null?this._v:(o?o.value:''); } return this._v!=null?this._v:(at.value!=null?at.value:''); },
      set value(v){ this._v=String(v); if(tagName==='select'){ opts.forEach(o=>o.selected=o.value===String(v)); } },
      get innerHTML(){ return this._html; }, set innerHTML(v){ this._html=String(v); this.textContent=this._html.replace(/<[^>]+>/g,''); registerIds(this._html); },
      get outerHTML(){ return '<'+tagName+'>'+this._html+'</'+tagName+'>'; },
      get className(){ return [...cls].join(' '); }, set className(v){ cls.clear(); String(v).split(/\s+/).filter(Boolean).forEach(c=>cls.add(c)); },
      classList:{ add:(...c)=>c.forEach(x=>cls.add(x)), remove:(...c)=>c.forEach(x=>cls.delete(x)), contains:c=>cls.has(c), toggle:(c,f)=>{ const on=f===undefined?!cls.has(c):!!f; on?cls.add(c):cls.delete(c); return on; } },
      addEventListener(t,f){ (listeners[t]=listeners[t]||[]).push(f); }, removeEventListener(t,f){ if(listeners[t]) listeners[t]=listeners[t].filter(x=>x!==f); },
      dispatchEvent(ev){ (listeners[ev.type]||[]).forEach(f=>f.call(e,ev)); return true; },
      click(){ const ev={type:'click',target:e,currentTarget:e,preventDefault(){},stopPropagation(){}}; (listeners.click||[]).forEach(f=>f.call(e,ev)); if(typeof e.onclick==='function') e.onclick(ev); },
      focus(){}, blur(){}, select(){}, scrollIntoView(){}, scrollTo(){}, remove(){}, setAttribute(k,v){ at[k]=String(v); if(k==='id') e.id=v; if(k==='class') e.className=v; }, getAttribute(k){ return at[k]!=null?at[k]:null; }, hasAttribute(k){ return k in at; }, removeAttribute(k){ delete at[k]; },
      appendChild(c){ e.children.push(c); if(c&&typeof c==='object'){ c.parentNode=e; c.parentElement=e; } return c; }, insertBefore(c){ return e.appendChild(c); }, prepend(c){ e.children.unshift(c); }, append(...c){ c.forEach(x=>e.appendChild(x)); }, removeChild(c){ e.children=e.children.filter(x=>x!==c); return c; }, replaceChildren(){ e.children=[]; },
      insertAdjacentHTML(p,h){ e.innerHTML = p==='afterbegin' ? h+e._html : e._html+h; }, insertAdjacentElement(p,c){ return c; },
      querySelector(s){ return qs(s); }, querySelectorAll(s){ return qsa(s); }, closest(){ return null; }, contains(){ return false; }, matches(){ return false; },
      getBoundingClientRect(){ return {top:0,left:0,right:800,bottom:400,width:800,height:400,x:0,y:0}; }, getContext(){ return NOOP; }, toDataURL(){ return 'data:,'; },
      animate(){ return {finished:Promise.resolve(),cancel(){},onfinish:null}; }, cloneNode(){ return makeEl(tagName,Object.assign({},at),this._html); }, attachShadow(){ return e; },
      showModal(){}, close(){}, play(){ return Promise.resolve(); }, pause(){}, load(){}, requestFullscreen(){ return Promise.resolve(); }
    };
    if(tagName==='select'){ e.add=o=>opts.push(o); e.remove=i=>opts.splice(i,1); e.appendChild=c=>{ if(c && c.tagName==='OPTION'){ opts.push(c); return c; } e.children.push(c); return c; };
      Object.defineProperty(e,'innerHTML',{ get(){ return e._html; }, set(v){ e._html=String(v); opts=[]; for(const m of e._html.matchAll(/<option([^>]*)>([\s\S]*?)<\/option>/g)){ const oa=attrs(m[1]); opts.push(makeOpt(oa.value!=null?oa.value:m[2].replace(/<[^>]+>/g,'').trim(), m[2].replace(/<[^>]+>/g,'').trim(), 'selected' in oa)); } e._v=null; } }); }
    return e;
  }
  function makeOpt(value,text,selected){ return { tagName:'OPTION', value:String(value), text, textContent:text, selected:!!selected, disabled:false, style:{}, setAttribute(){}, getAttribute(){ return null; } }; }
  function registerIds(h){ for(const m of String(h).matchAll(/<(\w+)([^>]*\sid="([\w-]+)"[^>]*)>/g)){ if(!byId[m[3]]){ const tag=m[1].toLowerCase(); let inner=''; if(tag==='select'){ const end=h.indexOf('</select>',m.index); inner=end>0?h.slice(m.index+m[0].length,end):''; } byId[m[3]]=makeEl(tag,attrs(m[2]),inner); } } }
  // every id in the file, with inner HTML for selects/textareas
  for(const m of html.matchAll(/<(\w+)((?:[^>"']|"[^"]*"|'[^']*')*?\sid="([\w-]+)"(?:[^>"']|"[^"]*"|'[^']*')*)>/g)){
    const tag=m[1].toLowerCase(), id=m[3]; if(byId[id]) continue; let inner='';
    if(tag==='select'||tag==='textarea'){ const end=html.indexOf('</'+tag+'>',m.index); inner=end>0?html.slice(m.index+m[0].length,end):''; }
    byId[id]=makeEl(tag,attrs(m[2]),inner);
  }
  function qs(s){ s=String(s).trim(); const m=/^#([\w-]+)$/.exec(s); if(m) return byId[m[1]]||null; return null; }
  function qsa(s){ s=String(s).trim(); const m=/^#([\w-]+)$/.exec(s); const r=m&&byId[m[1]]?[byId[m[1]]]:[]; r.item=i=>r[i]; return r; }
  // ── document / window ──
  const docL={}, winL={};
  const body=makeEl('body',{},''), head=makeEl('head',{},''), htmlEl=makeEl('html',{},'');
  const document={ readyState:'loading', body, head, documentElement:htmlEl, hidden:false, visibilityState:'visible', title:'', cookie:'', activeElement:body, fonts:{ ready:Promise.resolve(), load:()=>Promise.resolve() },
    getElementById:id=>byId[id]||null, querySelector:qs, querySelectorAll:qsa, getElementsByClassName:()=>[], getElementsByTagName:t=>t==='body'?[body]:t==='head'?[head]:[],
    createElement:t=>makeEl(String(t).toLowerCase(),{},''), createElementNS:(n,t)=>makeEl(String(t).toLowerCase(),{},''), createTextNode:t=>({textContent:t}), createDocumentFragment:()=>makeEl('fragment',{},''),
    addEventListener:(t,f)=>{ (docL[t]=docL[t]||[]).push(f); }, removeEventListener(){}, dispatchEvent:ev=>{ (docL[ev.type]||[]).forEach(f=>f(ev)); return true; }, execCommand:()=>true, hasFocus:()=>true };
  const timers={ n:1 };
  function setT(f,ms,...a){ const id=timers.n++; if(typeof f!=='function') return id; if(!ms || ms<=100) setImmediate(()=>{ try{ f(...a); }catch(e){ errors.push('timer: '+(e&&e.stack||e)); } }); else held.push({id,f,ms}); return id; }
  const sandbox={ console:{ log(){}, info(){}, debug(){}, warn(){}, error:(...a)=>{ const t=a.map(String).join(' '); if(/Uncaught|TypeError|ReferenceError|SyntaxError/.test(t)) errors.push('console.error: '+t.slice(0,300)); }, group(){}, groupEnd(){}, table(){}, time(){}, timeEnd(){} },
    document, localStorage:ls, sessionStorage:ss, setTimeout:setT, setInterval:(f,ms)=>{ const id=timers.n++; held.push({id,f,ms,repeat:true}); return id; }, clearTimeout(){}, clearInterval(){},
    requestAnimationFrame:f=>setT(()=>f(Date.now()),16), cancelAnimationFrame(){}, requestIdleCallback:f=>setT(()=>f({timeRemaining:()=>10,didTimeout:false}),1),
    queueMicrotask, structuredClone:typeof structuredClone!=='undefined'?structuredClone:(x=>JSON.parse(JSON.stringify(x))), Promise, Date, Math, JSON, URL, URLSearchParams, TextEncoder, TextDecoder, Blob:typeof Blob!=='undefined'?Blob:function(){}, AbortController, Intl,
    atob:s=>Buffer.from(s,'base64').toString('binary'), btoa:s=>Buffer.from(String(s),'binary').toString('base64'),
    fetch:()=>Promise.reject(new Error('no network in tests')), WebSocket:undefined, indexedDB:opts.indexedDB||undefined,
    navigator:{ userAgent:'node-smoke', language:'en-US', languages:['en-US'], onLine:true, clipboard:{ writeText:()=>Promise.resolve() }, vibrate:()=>true, share:undefined, serviceWorker:{ register:()=>Promise.reject(new Error('no network in tests')), getRegistrations:()=>Promise.resolve([]), addEventListener(){}, controller:null }, wakeLock:undefined, storage:{ estimate:()=>Promise.resolve({usage:0,quota:5e9}), persist:()=>Promise.resolve(false), persisted:()=>Promise.resolve(false) }, hardwareConcurrency:4, maxTouchPoints:0 },
    location:{ href:'file:///omega.html', protocol:'file:', host:'', hostname:'', pathname:'/omega.html', search:'', hash:'', origin:'null', reload(){}, assign(){}, replace(){} },
    history:{ pushState(){}, replaceState(){}, back(){} }, screen:{ width:1280, height:800 }, innerWidth:1280, innerHeight:800, devicePixelRatio:1,
    matchMedia:q=>({ matches:false, media:q, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} }),
    getComputedStyle:()=>new Proxy({}, { get:(t,k)=> k==='getPropertyValue' ? ()=>'' : '' }),
    Notification:Object.assign(function(){ return {close(){}}; },{ permission:'default', requestPermission:()=>Promise.resolve('default') }),
    Audio:function(){ return { play:()=>Promise.resolve(), pause(){}, load(){}, addEventListener(){} }; }, AudioContext:undefined, webkitAudioContext:undefined, speechSynthesis:undefined,
    IntersectionObserver:function(){ return { observe(){}, unobserve(){}, disconnect(){} }; }, ResizeObserver:function(){ return { observe(){}, unobserve(){}, disconnect(){} }; }, MutationObserver:function(){ return { observe(){}, disconnect(){}, takeRecords(){ return []; } }; },
    performance:{ now:()=>Number(process.hrtime.bigint()/1000000n), mark(){}, measure(){}, getEntriesByType:()=>[], memory:undefined },
    crypto:{ randomUUID:()=>require('crypto').randomUUID(), getRandomValues:a=>require('crypto').randomFillSync(a), subtle:undefined },
    alert(){}, confirm:()=>true, prompt:()=>null, open:()=>null, print(){}, scrollTo(){}, scrollBy(){}, focus(){}, close(){},
    Event:function(t,o){ this.type=t; Object.assign(this,o||{}); this.preventDefault=()=>{}; this.stopPropagation=()=>{}; }, CustomEvent:function(t,o){ this.type=t; this.detail=o&&o.detail; },
    FileReader:function(){ this.readAsText=()=>{}; this.readAsDataURL=()=>{}; }, Image:function(){ return makeEl('img',{},''); },
    HTMLElement:function(){}, Element:function(){}, Node:function(){}, SVGElement:function(){}, DOMParser:function(){ this.parseFromString=()=>({ querySelectorAll:()=>[], querySelector:()=>null, getElementsByTagName:()=>[] }); },
    LightweightCharts:undefined, TradingView:undefined, Chart:undefined,
    addEventListener:(t,f)=>{ (winL[t]=winL[t]||[]).push(f); }, removeEventListener(){}, dispatchEvent:ev=>{ (winL[ev.type]||[]).forEach(f=>f(ev)); return true; },
    Float32Array, Float64Array, Uint32Array, Int32Array, Uint8Array, Uint16Array, ArrayBuffer, DataView, Map, Set, WeakMap, WeakSet, Symbol, Proxy, Reflect, Error, TypeError, RangeError, Number, String, Boolean, Array, Object, RegExp, isFinite, isNaN, parseFloat, parseInt, encodeURIComponent, decodeURIComponent, escape, unescape, BigInt };
  sandbox.Storage=Storage; sandbox.window=sandbox; sandbox.self=sandbox; sandbox.globalThis=sandbox; sandbox.top=sandbox; sandbox.parent=sandbox; sandbox.frames=sandbox;
  const ctx=vm.createContext(sandbox);
  process.on('unhandledRejection', e=>{ const t=String(e&&e.stack||e); if(!/no network in tests/.test(t)) errors.push('unhandled rejection: '+t.slice(0,400)); });
  scripts.forEach((src,i)=>{ try{ vm.runInContext(src, ctx, { filename:'block'+i+'.js' }); }catch(e){ errors.push('block '+i+': '+(e&&e.stack||e).toString().split('\n').slice(0,3).join(' | ')); } });
  document.readyState='interactive';
  try{ (docL.DOMContentLoaded||[]).forEach(f=>{ try{ f({type:'DOMContentLoaded'}); }catch(e){ errors.push('DOMContentLoaded: '+(e&&e.stack||e).toString().split('\n').slice(0,3).join(' | ')); } }); }catch(e){}
  document.readyState='complete';
  try{ (winL.load||[]).forEach(f=>{ try{ f({type:'load'}); }catch(e){ errors.push('load: '+(e&&e.stack||e).toString().split('\n').slice(0,3).join(' | ')); } }); }catch(e){}
  async function drain(n){ for(let i=0;i<(n||30);i++) await new Promise(r=>setImmediate(r)); }
  function fireHeld(filter){ held.slice().forEach(h=>{ if(!filter || filter(h)){ try{ h.f(); }catch(e){ errors.push('held timer: '+(e&&e.stack||e).toString().split('\n')[0]); } } }); }
  return { ctx, errors, store:ls._d, getEl:id=>byId[id]||null, drain, held, fireHeld, byId };
};
