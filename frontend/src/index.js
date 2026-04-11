import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/index.css";
import App from "@/App";
import Admin from "@/Admin";
import Demo from "@/Demo";

// PWA: Registrar Service Worker com anti-cache forçado
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })
      .then(reg => {
        console.log('SoulNutri: SW registrado', reg.scope);
        // Forçar verificação de atualização a cada abertura
        reg.update();
        // Verificar periodicamente (a cada 60s)
        setInterval(() => reg.update(), 60000);
      })
      .catch(err => console.warn('SoulNutri: SW falhou', err));
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
