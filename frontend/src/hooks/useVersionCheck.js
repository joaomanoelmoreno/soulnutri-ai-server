import { useState, useEffect } from 'react';

const API = `${process.env.REACT_APP_BACKEND_URL || ''}/api`;
const LS_VERSION_KEY = 'soulnutri_backend_version';

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

    async function check() {
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
          setHasUpdate(true);
        }
      } catch (_) {
        // Silencioso — nao exibir banner se API estiver fora
      }
    }

    check();
    return () => { cancelled = true; };
  }, []);

  return { hasUpdate, serverVersion, triggerHardUpdate };
}
