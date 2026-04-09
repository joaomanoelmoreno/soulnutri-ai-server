// SoulNutri Service Worker - v4 FORCE UPDATE
// Este SW limpa TODOS os caches e se desregistra automaticamente
const CACHE_NAME = 'soulnutri-v4';

// Install: skipWaiting para ativar imediatamente
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

// Activate: limpar TODOS os caches antigos e tomar controle
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          console.log('SoulNutri: Limpando cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      return self.clients.claim();
    }).then(() => {
      // Forcar reload em todos os clientes
      return self.clients.matchAll().then(clients => {
        clients.forEach(client => {
          client.postMessage({ type: 'SW_UPDATED', version: 'v4' });
        });
      });
    })
  );
});

// Fetch: NUNCA cachear - sempre buscar do servidor
self.addEventListener('fetch', (event) => {
  // Passar direto para o servidor, sem cache
  return;
});
