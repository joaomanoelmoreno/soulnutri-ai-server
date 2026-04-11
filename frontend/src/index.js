import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/index.css";
import App from "@/App";
import Admin from "@/Admin";
import Demo from "@/Demo";

// ═══════════════════════════════════════════════════════════════
// PWA Service Worker - Registro limpo com atualização forçada
// ═══════════════════════════════════════════════════════════════
if ('serviceWorker' in navigator) {
  // Guardar se já havia um controller ANTES de registrar o novo SW
  const hadController = !!navigator.serviceWorker.controller;

  window.addEventListener('load', async () => {
    try {
      const reg = await navigator.serviceWorker.register('/sw.js', {
        updateViaCache: 'none'
      });
      console.log('[SoulNutri] SW registrado');

      // Forçar verificação de atualização
      reg.update();

      // Se há um SW esperando, forçar ativação
      if (reg.waiting) {
        reg.waiting.postMessage({ type: 'SKIP_WAITING' });
      }

      // Detectar quando novo SW é instalado
      reg.addEventListener('updatefound', () => {
        const newSW = reg.installing;
        if (newSW) {
          newSW.addEventListener('statechange', () => {
            // Só recarrega se já havia um controller (= atualização, não primeiro install)
            if (newSW.state === 'installed' && hadController) {
              console.log('[SoulNutri] Atualização detectada, recarregando...');
              newSW.postMessage({ type: 'SKIP_WAITING' });
            }
          });
        }
      });

      // Só recarregar no controllerchange se já havia um controller antigo
      let refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (hadController && !refreshing) {
          refreshing = true;
          window.location.reload();
        }
      });
    } catch (err) {
      console.warn('[SoulNutri] SW falhou:', err);
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// Limpeza de caches órfãos (fora do SW, uma vez por sessão)
// ═══════════════════════════════════════════════════════════════
if ('caches' in window) {
  caches.keys().then(keys => {
    if (keys.length > 0) {
      console.log('[SoulNutri] Limpando', keys.length, 'caches órfãos');
      keys.forEach(key => caches.delete(key));
    }
  });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/demo" element={<Demo />} />
      </Routes>
    </BrowserRouter>,
);
