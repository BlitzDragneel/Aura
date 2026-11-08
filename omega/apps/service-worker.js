/* OMEGA service worker: makes the installed app open offline.
   The app file and icons are cached; when online, the newest app version is fetched first (network-first), so updates
   arrive on the next open. Data requests (prices, the Live API, exchanges) are never cached here. */
const CACHE = 'omega-shell-v1';
const SHELL = ['/omega-v6_5-47.html', '/manifest.json', '/icons/omega-192.png', '/icons/omega-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== self.location.origin) return;   // never touch data from other hosts
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok && SHELL.includes(u.pathname)) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(u.pathname, copy)); }
    return r;
  }).catch(() => caches.match(u.pathname).then(m => m || caches.match('/omega-v6_5-47.html'))));
});
