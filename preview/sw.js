// Service Worker for Christus – Bibel PWA
// Caches standalone.html for full offline support.

const CACHE_NAME = 'christus-bible-v1';
const ASSETS = [
  './standalone.html',
  './manifest.json',
];

// Install: pre-cache all assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Fetch: serve from cache, fall back to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).catch(() =>
        // Network failed and no cache hit – return a minimal offline response
        new Response(
          '<h2 style="font-family:sans-serif;padding:2rem">Offline – bitte Seite neu laden.</h2>',
          { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
        )
      );
    })
  );
});
