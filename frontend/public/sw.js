// SoulNutri Service Worker v10 - MINIMAL (apenas para PWA installability)
// NÃO cacheia nada. NÃO intercepta fetch. Apenas limpa caches antigos.
// O browser usa HTTP cache normal (React build já gera hashes nos arquivos).

const SW_VERSION = 'v10-minimal';

// Install: ativa imediatamente (não espera SW anterior)
self.addEventListener('install', () => {
  console.log('[SW] Install', SW_VERSION);
  self.skipWaiting();
});

// Activate: limpa TODOS os caches anteriores e assume controle
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

// Fetch: NÃO intercepta. Deixa o browser operar normalmente.
// Sem fetch listener = zero risco de "body locked", respostas stale, etc.
