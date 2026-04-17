import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/index.css";
import App from "@/App";
import Admin from "@/Admin";
import Demo from "@/Demo";

// ═══════════════════════════════════════════════════════════════
// PWA Service Worker - Registro simples e estável
// ═══════════════════════════════════════════════════════════════
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      await navigator.serviceWorker.register('/sw.js', {
        updateViaCache: 'none'
      });
      console.log('[SoulNutri] SW registrado');
    } catch (err) {
      console.warn('[SoulNutri] SW falhou:', err);
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
