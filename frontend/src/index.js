import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/index.css";
import App from "@/App";
import Admin from "@/Admin";

// PWA: Registrar Service Worker para instalacao
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => {
        console.log('SoulNutri: SW registrado', reg.scope);
        // Verificar atualizacoes periodicamente
        reg.update();
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
      </Routes>
    </BrowserRouter>,
);
