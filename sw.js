/* ================================================================
   AutoRadar (backend) / Carnet (visible) — Service Worker
   Strategy: Cache-First for app shell, Network-First for API calls
   Note: cache name keeps "autoradar" prefix (backend identity);
         only the version is bumped to invalidate old caches.
   ================================================================ */

const CACHE_NAME    = 'autoradar-v3-carnet-pass1';
const CACHE_ASSETS  = [
  '/',
  '/index.html',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500;1,600;1,700;1,800&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=DM+Mono:wght@300;400;500&display=swap',
];

/* ── Install: pre-cache app shell ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CACHE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

/* ── Activate: clean old caches ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

/* ── Fetch: cache-first for assets, network-first for APIs ── */
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  /* Always network for external APIs (Nominatim, Anthropic, QR, EmailJS) */
  const isAPI = [
    'nominatim.openstreetmap.org',
    'api.anthropic.com',
    'api.qrserver.com',
    'emailjs.com',
    'xrplcluster.com',
    'fonts.gstatic.com',
  ].some(host => url.hostname.includes(host));

  if (isAPI || event.request.method !== 'GET') {
    event.respondWith(fetch(event.request));
    return;
  }

  /* Cache-first for app shell */
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        /* Cache successful same-origin responses */
        if (response.ok && url.origin === self.location.origin) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        /* Offline fallback: return cached index.html */
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html') || caches.match('/');
        }
      });
    })
  );
});

/* ── Push notifications (future) ── */
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'Carnet', {
      body:    data.body || 'Nouvelle alerte véhicule',
      icon:    '/icons/icon-192.png',
      badge:   '/icons/icon-72.png',
      vibrate: [200, 100, 200],
      data:    { url: data.url || '/' },
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});
