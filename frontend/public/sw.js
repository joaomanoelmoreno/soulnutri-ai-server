// SoulNutri Service Worker v11 - NETWORK FIRST para navegação
// CORRIGE: PWA instalado carregando versão antiga após deploy
// ESTRATÉGIA: intercepts de navegação sempre buscam HTML fresh da rede.
// Sem isso, o browser serve index.html do cache de disco mesmo após novo deploy.

const SW_VERSION = 'v11-network-first';
const HTML_CACHE = 'soulnutri-html-v11';

// Install: ativa imediatamente (não espera SW anterior)
self.addEventListener('install', (event) => {
  console.log('[SW] Install', SW_VERSION);
  self.skipWaiting();
});

// Activate: limpa TODOS os caches anteriores e assume controle imediato
self.addEventListener('activate', (event) => {
  console.log('[SW] Activate', SW_VERSION);
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.map(key => {
        console.log('[SW] Deletando cache:', key);
        return caches.delete(key);
      })))
      .then(() => self.clients.claim())
  );
});

// Fetch: intercepta APENAS navegações (document requests = index.html)
// NETWORK FIRST: sempre busca na rede → garante bundle novo após deploy
// Outros recursos (JS/CSS/imagens): browser usa cache normal (hashes garantem frescor)
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Intercepta APENAS requisições de navegação HTML
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request, { cache: 'no-store' })
        .then(response => {
          // Guardar cópia no cache para fallback offline
          const clone = response.clone();
          caches.open(HTML_CACHE).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => {
          // Offline fallback: servir do cache HTML local
          return caches.match('/') || caches.match('/index.html');
        })
    );
    return;
  }

  // Todos os outros requests: comportamento padrão do browser (sem interceptação)
  // Os bundles JS/CSS têm hash no nome → imutáveis → cache do browser é seguro
});

// Receber SKIP_WAITING de clientes (index.js postMessage)
self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') {
    console.log('[SW] SKIP_WAITING recebido');
    self.skipWaiting();
  }
});
