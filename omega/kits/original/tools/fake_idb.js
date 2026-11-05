// Minimal asynchronous IndexedDB stand-in for the smoke harness. Writes are buffered per
// transaction and applied atomically at commit, as a real browser does; `failNext` aborts
// the next read-write transaction (to prove callers never delete before a commit).
module.exports = function fakeIDB(){
  const dbs = {};
  const later = f => setImmediate(f);
  const clone = v => v === undefined ? undefined : JSON.parse(JSON.stringify(v));
  const api = { failNext:0, dbs, opens:0 };
  function makeDB(name){
    const d = dbs[name];
    const db = {
      name, get version(){ return d.version; },
      objectStoreNames:{ contains:n => !!d.stores[n], get length(){ return Object.keys(d.stores).length; } },
      createObjectStore(n, o){ d.stores[n] = { keyPath:(o&&o.keyPath)||null, auto:!!(o&&o.autoIncrement), data:new Map(), seq:1 }; return {}; },
      close(){},
      transaction(names, mode){
        names = [].concat(names);
        const tx = { error:null, oncomplete:null, onerror:null, onabort:null, mode };
        const writes = []; let pending = 0, done = false, failed = false;
        const willFail = mode === 'readwrite' && api.failNext > 0 && (!api.failOnly || api.failOnly === name) ? (api.failNext--, true) : false;
        function settle(){ if(done || pending) return; done = true;
          later(() => {
            if(willFail || failed){ tx.error = tx.error || new Error('QuotaExceededError (simulated)');
              if(tx.onerror) tx.onerror({ target:tx }); if(tx.onabort) tx.onabort({ target:tx }); return; }
            writes.forEach(w => w());
            if(tx.oncomplete) tx.oncomplete({ target:tx });
          });
        }
        function req(fn){ const r = { result:undefined, error:null, onsuccess:null, onerror:null }; pending++;
          later(() => { try{ r.result = fn(); if(r.onsuccess) r.onsuccess({ target:r }); }
            catch(e){ r.error = e; failed = true; if(r.onerror) r.onerror({ target:r }); }
            pending--; settle(); });
          return r; }
        tx.objectStore = n => {
          if(names.indexOf(n) < 0 || !d.stores[n]) throw new Error('NotFoundError: ' + n);
          const s = d.stores[n];
          const view = () => { const m = new Map(s.data); return m; };
          const keyOf = v => s.keyPath ? v[s.keyPath] : (s.seq++);
          return {
            put(v, k){ const key = k != null ? k : keyOf(v); if(key == null) throw new Error('DataError: no key'); const c = clone(v); writes.push(() => s.data.set(key, c)); return req(() => key); },
            add(v, k){ const key = k != null ? k : keyOf(v); const c = clone(v); writes.push(() => { if(!s.data.has(key)) s.data.set(key, c); }); return req(() => key); },
            get(k){ return req(() => clone(view().get(k))); },
            getAll(){ return req(() => [...view().entries()].sort((a,b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0).map(e => clone(e[1]))); },
            getAllKeys(){ return req(() => [...view().keys()].sort()); },
            count(){ return req(() => view().size); },
            delete(k){ writes.push(() => s.data.delete(k)); return req(() => undefined); },
            clear(){ writes.push(() => s.data.clear()); return req(() => undefined); }
          };
        };
        later(settle);
        return tx;
      }
    };
    return db;
  }
  api.open = function(name, version){
    api.opens++;
    const r = { result:null, error:null, onsuccess:null, onerror:null, onupgradeneeded:null, onblocked:null };
    later(() => {
      let d = dbs[name], upgrade = false;
      if(!d){ d = dbs[name] = { version:0, stores:{} }; }
      const v = version || Math.max(1, d.version);
      if(v > d.version){ upgrade = true; d.version = v; }
      r.result = makeDB(name);
      if(upgrade && r.onupgradeneeded) r.onupgradeneeded({ target:r, oldVersion:0, newVersion:v });
      if(r.onsuccess) r.onsuccess({ target:r });
    });
    return r;
  };
  api.deleteDatabase = function(name){ delete dbs[name]; const r = {}; later(() => r.onsuccess && r.onsuccess({})); return r; };
  return api;
};
