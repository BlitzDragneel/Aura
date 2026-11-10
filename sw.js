/* The Scroll — offline service worker (v3: also keeps the icons and manifest).
   Serves the app instantly from the device, checks for a newer version in
   the background, and tells the page when one is ready so the reader can
   choose to reload. Nothing is ever sent anywhere but your own host. */
const CACHE = "the-scroll-v2";   /* name kept: the app writes its own copy into this cache */
const ASSETS = ["manifest.webmanifest","icon-192.png","icon-512.png","icon-192-maskable.png","icon-512-maskable.png","apple-touch-icon.png","favicon.svg"];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    try { const c = await caches.open(CACHE); await c.add(new Request("./", { cache: "reload" })); } catch (err) {}
    /* small files beside the app; each on its own so one miss never blocks the rest */
    try { const c = await caches.open(CACHE); await Promise.all(ASSETS.map(a => c.add(new Request(a, { cache: "reload" })).catch(() => {}))); } catch (err) {}
    self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

/* A version is identified by the server's ETag, else Last-Modified, else size. */
async function fingerprint(res) {
  if (!res) return "";
  const h = res.headers;
  const tag = h.get("etag") || h.get("last-modified");
  if (tag) return "h:" + tag;
  try { const b = await res.clone().blob(); return "s:" + b.size; } catch (e) { return ""; }
}
async function notify(msg) {
  const cs = await self.clients.matchAll({ includeUncontrolled: true, type: "window" });
  cs.forEach(c => c.postMessage(msg));
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  if (req.mode === "navigate" || req.destination === "document") {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const cached = await cache.match("./");
      /* Check the network in the background; never make the reader wait. */
      const refresh = (async () => {
        try {
          const res = await fetch(req, { cache: "no-cache" });
          if (!res || !res.ok) return null;
          const wasSnapshot = cached && cached.headers.get("x-scroll-snapshot") === "1";
          const changed = cached && !wasSnapshot && (await fingerprint(cached)) !== (await fingerprint(res));
          await cache.put("./", res.clone());
          if (changed) notify({ type: "scroll-update-ready" });
          return res;
        } catch (err) { return null; }
      })();
      e.waitUntil(refresh);
      return cached || (await refresh) || new Response(
        "<h1>The Scroll is offline</h1><p>Open it once while connected, then it will work with no signal.</p>",
        { headers: { "Content-Type": "text/html" } });
    })());
    return;
  }

  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req);
    /* the worker itself is never served from its own cache */
    if (url.pathname.endsWith("/sw.js")) return fetch(req);
    if (hit) {
      /* serve at once, refresh quietly so a new icon or manifest arrives with the next update */
      e.waitUntil(fetch(req).then(res => { if (res && res.ok && res.type === "basic") return cache.put(req, res.clone()); }).catch(() => {}));
      return hit;
    }
    try {
      const res = await fetch(req);
      if (res && res.ok && res.type === "basic") cache.put(req, res.clone());
      return res;
    } catch (err) { return Response.error(); }
  })());
});

self.addEventListener("message", (e) => {
  if (e.data === "cache-now") {
    e.waitUntil((async () => { try { const c = await caches.open(CACHE); await c.add(new Request("./", { cache: "reload" })); } catch (err) {} })());
  }
});
