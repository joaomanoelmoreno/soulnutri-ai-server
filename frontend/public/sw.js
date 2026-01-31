// SoulNutri Service Worker
const CACHE_NAME = 'soulnutri-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/images/soulnutri-logo.png',
  '/images/soulnutri-logo-light.png'
];

// Install Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('SoulNutri: Cache aberto');
        return cache.addAll(urlsToCache);
      })
      .catch((err) => {
        console.log('SoulNutri: Erro ao cachear:', err);
      })
  );
  self.skipWaiting();
});

// Fetch - Network first, fallback to cache
self.addEventListener('fetch', (event) => {
  // Ignorar requisições de API (sempre online)
  if (event.request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clonar resposta para cache
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});

// Activate - limpar caches antigos
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('SoulNutri: Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});
