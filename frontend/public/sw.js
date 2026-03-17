// SoulNutri Service Worker - v3 (fix postMessage clone error)
const CACHE_NAME = 'soulnutri-v3';
const urlsToCache = [
  '/manifest.json',
  '/images/soulnutri-logo.png',
  '/images/soulnutri-logo-light.png'
];

// Install Service Worker - limpar caches antigos
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('SoulNutri: Cache v2 aberto');
        return cache.addAll(urlsToCache);
      })
      .catch((err) => {
        console.log('SoulNutri: Erro ao cachear:', err);
      })
  );
  self.skipWaiting();
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

// Fetch - Network first para HTML/JS, cache only para imagens
self.addEventListener('fetch', (event) => {
  // Ignorar requisições de API, blob URLs e media streams
  if (event.request.url.includes('/api/') ||
      event.request.url.startsWith('blob:') ||
      event.request.url.startsWith('data:') ||
      event.request.url.includes('mediastream') ||
      event.request.method !== 'GET') {
    return;
  }
  
  // HTML e JS sempre do servidor (evita cache desatualizado)
  if (event.request.url.endsWith('.html') || 
      event.request.url.endsWith('.js') ||
      event.request.url.endsWith('/') ||
      event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(event.request))
    );
    return;
  }
  
  // Outros recursos: network first com fallback para cache
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.status === 200) {
          try {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone).catch(() => {});
            });
          } catch (e) {
            // Request nao pode ser clonado (blob, media, etc) - ignorar
          }
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
