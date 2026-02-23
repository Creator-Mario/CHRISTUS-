// CHRISTUS App v1.10 – Service Worker
// Bump APP_VERSION on every release so the old cache is purged automatically.
const APP_VERSION = '1.10.3';
const CACHE_STATIC = 'christus-static-' + APP_VERSION;
const CACHE_PAGES  = 'christus-pages-'  + APP_VERSION;

// ── Install: skip waiting immediately (no pre-caching to avoid path issues) ──
self.addEventListener('install', e => {
  e.waitUntil(self.skipWaiting());
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
            caches.open(CACHE_PAGES).then(c => c.put(e.request, resp.clone()));
          }
          return resp;
        })
        .catch(() => caches.match(e.request).then(cached => {
          if (cached) return cached;
          // Last-resort fallback: return home page from cache
          return caches.match(new URL('home.html', self.location).href);
        }))
    );
  } else {
    // Cache-first for static assets (CSV, manifest, etc.)
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(resp => {
          if (resp && resp.status === 200 && resp.type !== 'opaque') {
            caches.open(CACHE_STATIC).then(c => c.put(e.request, resp.clone()));
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
