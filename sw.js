// CHRISTUS App v1.17.14 – Service Worker
// Bump APP_VERSION on every release so the old cache is purged automatically.
const APP_VERSION = '1.17.14';
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
  './app/bible.html',
  './app/themen.html',
  './app/install.html',
  './app/manifest.json',
  './app/translations.js',
  './app/icons/icon-192.png',
  './app/icons/icon-512.png',
  './elberfelder_1905.csv',
  './kjv_1769.csv',
];

// ── Install: pre-cache core pages ────────────────────────────────────────────
// Split large files (CSV) from core pages so a slow/failed CSV fetch never
// prevents the core app from going offline. Core pages are cached atomically;
// the CSV is cached as a best-effort addition.
const CORE_URLS  = PRECACHE_URLS.filter(u => !u.endsWith('.csv'));
const LARGE_URLS = PRECACHE_URLS.filter(u =>  u.endsWith('.csv'));

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_PAGES)
      .then(cache => cache.addAll(CORE_URLS)
        .then(() => cache.addAll(LARGE_URLS).catch(err => console.warn('[SW] Large-file cache failed (CSV may not be offline yet):', err)))
      )
    // No skipWaiting here: let the SW enter "waiting" so the update banner
    // on every app page can show. The user clicks "Jetzt aktualisieren" which
    // sends SKIP_WAITING (see message handler below), then the page reloads.
    // On first install there is no existing controller, so the browser activates
    // the SW automatically without needing skipWaiting().
  );
});

// ── Activate: delete all old caches and claim clients ────────────────────────
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          // Keep current versioned caches and the stable user-download cache
          .filter(k => k !== CACHE_STATIC && k !== CACHE_PAGES && k !== 'christus-offline-v1')
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
