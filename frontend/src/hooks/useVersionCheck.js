import { useState, useEffect } from 'react';

const API = `${process.env.REACT_APP_BACKEND_URL || ''}/api`;
const LS_VERSION_KEY = 'soulnutri_backend_version';
const LS_FRONTEND_VERSION_KEY = 'soulnutri_frontend_version';

// Keys criticas que NUNCA sao apagadas no hard update
const CRITICAL_KEYS = [
  'soulnutri_pin',
  'soulnutri_nome',
  'soulnutri_user',
  'soulnutri_restaurant',
  'soulnutri_location_manual',
];

function versionKey(data) {
  const phase = data?.phase || '';
  const commit = data?.git_commit || '';
  return `${phase}::${commit}`;
}

async function triggerHardUpdate() {
  // 1. Salvar keys criticas antes de limpar
  const saved = {};
  CRITICAL_KEYS.forEach(k => {
    const v = localStorage.getItem(k);
    if (v !== null) saved[k] = v;
  });

  // 2. Limpar todo o localStorage
  localStorage.clear();

  // 3. Restaurar keys criticas
  Object.entries(saved).forEach(([k, v]) => localStorage.setItem(k, v));

  // 4. Limpar Cache Storage
  if ('caches' in window) {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map(k => caches.delete(k)));
    } catch (_) {}
  }

  // 5. Desregistrar Service Worker
  if ('serviceWorker' in navigator) {
    try {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map(r => r.unregister()));
    } catch (_) {}
  }

  // 6. Reload limpo
  window.location.reload(true);
}

export function useVersionCheck() {
  const [hasUpdate, setHasUpdate] = useState(false);
  const [serverVersion, setServerVersion] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function checkFrontendVersion() {
      try {
        const res = await fetch(`/asset-manifest.json?t=${Date.now()}`, {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
          },
        });

        if (!res.ok || cancelled) return;

        const manifest = await res.json();
        const latestFrontend = manifest?.files?.['main.js'];

        if (!latestFrontend) return;

        const storedFrontend = localStorage.getItem(LS_FRONTEND_VERSION_KEY);

        if (!storedFrontend) {
          localStorage.setItem(LS_FRONTEND_VERSION_KEY, latestFrontend);
          return;
        }

        if (storedFrontend !== latestFrontend) {
          // Gravar antes do reload impede ciclo infinito.
          localStorage.setItem(LS_FRONTEND_VERSION_KEY, latestFrontend);
          window.location.reload();
        }
      } catch (_) {
        // Falha silenciosa: o app continua operando normalmente.
      }
    }

    async function check() {
      await checkFrontendVersion();

      if (cancelled) return;

      try {
        const res = await fetch(`${API}/debug/version`, {
          cache: 'no-store',
          signal: AbortSignal.timeout(4000),
        });
        if (!res.ok || cancelled) return;
        const data = await res.json();
        const latest = versionKey(data);
        const stored = localStorage.getItem(LS_VERSION_KEY);

        setServerVersion(data);

        if (!stored) {
          // Primeira vez — apenas salvar, sem banner
          localStorage.setItem(LS_VERSION_KEY, latest);
          return;
        }
        if (stored !== latest) {
          // Mudanças exclusivamente no backend já entram em vigor nas próximas
          // chamadas de API e não exigem atualização manual do aplicativo.
          localStorage.setItem(LS_VERSION_KEY, latest);
        }
      } catch (_) {
        // Silencioso — nao exibir banner se API estiver fora
      }
    }

    check();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        checkFrontendVersion();
      }
    };

    const handleFocus = () => {
      checkFrontendVersion();
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      cancelled = true;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  return { hasUpdate, serverVersion, triggerHardUpdate };
}
