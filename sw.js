// CHRISTUS App v1.12 – Service Worker
// Bump APP_VERSION on every release so the old cache is purged automatically.
const APP_VERSION = '1.12.0';
const CACHE_STATIC = 'christus-static-' + APP_VERSION;
const CACHE_PAGES  = 'christus-pages-'  + APP_VERSION;

// Core app pages to pre-cache so the app works offline from the first visit.
// Paths are relative to the SW location (root sw.js → scope covers everything).
const PRECACHE_URLS = [
  './index.html',
  './app/home.html',
  './app/login.html',
  './app/learn.html',
  './app/settings.html',
  './app/manifest.json',
  './app/translations.js',
  './app/icons/icon-192.png',
  './app/icons/icon-512.png',
];

// ── Install: pre-cache core pages, then activate immediately ─────────────────
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_PAGES)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ── Activate: delete all old caches and claim clients ────────────────────────
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_STATIC && k !== CACHE_PAGES)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: network-first for HTML, cache-first for everything else ────────────
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  const url = new URL(e.request.url);

  // Only handle same-origin requests
  if (url.origin !== self.location.origin) return;

  const isHtml = e.request.headers.get('Accept')?.includes('text/html') ||
                 url.pathname.endsWith('.html') ||
                 url.pathname.endsWith('/');

  if (isHtml) {
    // Network-first: always try the network; fall back to cache when offline
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(CACHE_PAGES).then(c => c.put(e.request, clone)).catch(() => {});
          }
          return resp;
        })
        .catch(() => caches.match(e.request).then(cached => {
          if (cached) return cached;
          // Last-resort fallback: return index page from cache
          return caches.match(new URL('./index.html', self.location).href);
        }))
    );
  } else {
    // Cache-first for static assets (CSV, manifest, etc.)
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(resp => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(CACHE_STATIC).then(c => c.put(e.request, clone)).catch(() => {});
          }
          return resp;
        }).catch(() => new Response('', { status: 503 }));
      })
    );
  }
});

// ── Message: allow clients to trigger skipWaiting manually ───────────────────
self.addEventListener('message', e => {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});
