// CHRISTUS App v1.10 – Service Worker
const CACHE = 'christus-v1.10';
const ASSETS = [
  '/index.html',
  '/app/login.html',
  '/app/home.html',
  '/app/learn.html',
  '/app/settings.html',
  '/app/manifest.json',
  '/Lernprogramm_Bibel.csv'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  // Only intercept same-origin GET requests for navigation/HTML
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(resp => {
        if (!resp || resp.status !== 200 || resp.type === 'opaque') return resp;
        const clone = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return resp;
      }).catch(() => {
        // Only return fallback page for HTML navigation requests
        const accept = e.request.headers.get('Accept') || '';
        if (accept.includes('text/html')) {
          return caches.match('/app/home.html');
        }
        return new Response('', { status: 503 });
      });
    })
  );
});
