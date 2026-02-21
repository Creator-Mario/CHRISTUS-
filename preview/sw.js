// Service Worker – Buch des Dienstes zur Evangelisation
// © 2025 Mario Reiner Denzer · Version 1.0.0

const CACHE_NAME = 'bde-bibel-v2';
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

// Activate: clean up old caches, notify clients of update
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => {
      // Broadcast update notification to all open clients
      return self.clients.matchAll({ type: 'window' }).then(clients => {
        clients.forEach(client =>
          client.postMessage({ type: 'SW_UPDATED', version: CACHE_NAME })
        );
      });
    })
  );
  self.clients.claim();
});

// Fetch: serve from cache, fall back to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).catch(() =>
        new Response(
          '<h2 style="font-family:Georgia,serif;padding:2rem;color:#0d1b2a">Offline – bitte Seite neu laden.</h2>',
          { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
        )
      );
    })
  );
});
