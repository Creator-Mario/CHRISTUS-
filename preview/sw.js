// Service Worker – Buch des Dienstes zur Evangelisation
// © 2025 Mario Reiner Denzer · Version 1.0.0

const CACHE_NAME = 'bde-bibel-v8';
const ASSETS = [
  './standalone.html',
  './manifest.json',
  './sw.js',
  '../index.html',
];

const OFFLINE_HTML = `<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Offline – BDE Bibel</title>
<style>
  body{font-family:Georgia,serif;background:#0d1b2a;color:#f7f3e9;
       display:flex;flex-direction:column;align-items:center;justify-content:center;
       min-height:100vh;text-align:center;padding:2rem;gap:1rem;}
  .icon{font-size:72px;}.title{color:#c9a227;font-size:1.5rem;font-weight:700;}
  p{opacity:.8;max-width:340px;line-height:1.6;}
  button{margin-top:1rem;padding:.7rem 1.6rem;background:#c9a227;color:#0d1b2a;
         border:none;border-radius:8px;font-size:1rem;font-family:Georgia,serif;
         cursor:pointer;font-weight:700;}
</style></head>
<body>
  <div class="icon">✝</div>
  <div class="title">Buch des Dienstes zur Evangelisation</div>
  <p>Du bist gerade offline.<br>
  Bitte öffne die App zuerst einmal online, damit sie vollständig gespeichert wird.</p>
  <button onclick="location.reload()">🔄 Erneut versuchen</button>
</body></html>`;

// Install: pre-cache all assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // addAll stops on first failure; use individual puts for robustness
      return Promise.allSettled(
        ASSETS.map(url =>
          fetch(url).then(r => r.ok ? cache.put(url, r) : null).catch(() => null)
        )
      );
    })
  );
  self.skipWaiting();
});

// Activate: clean up old caches, notify clients of update
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => {
      return self.clients.matchAll({ type: 'window' }).then(clients => {
        clients.forEach(client =>
          client.postMessage({ type: 'SW_UPDATED', version: CACHE_NAME })
        );
      });
    })
  );
  self.clients.claim();
});

// Fetch: cache-first, network fallback + update cache in background
self.addEventListener('fetch', event => {
  // Only handle GET requests for same-origin or relative assets
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.open(CACHE_NAME).then(cache =>
      cache.match(event.request).then(cached => {
        const networkFetch = fetch(event.request).then(response => {
          if (response && response.ok) {
            cache.put(event.request, response.clone());
          }
          return response;
        }).catch(() => null);

        // Return cached immediately; fetch in background for freshness
        if (cached) {
          // trigger background refresh
          event.waitUntil(networkFetch);
          return cached;
        }

        // No cache – try network, then offline fallback
        return networkFetch.then(r => r || new Response(OFFLINE_HTML, {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        }));
      })
    )
  );
});
