import React, { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const loadingRef = useRef(false);

  useEffect(() => { 
    checkStatus(); 
    startCamera(); 
    return () => stopCamera();
  }, []);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API}/ai/status`);
      setStatus(await res.json());
    } catch { setStatus({ ok: false }); }
  };

  const startCamera = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } } 
      });
      setStream(s);
      if (videoRef.current) videoRef.current.srcObject = s;
    } catch { console.error("Câmera não disponível"); }
  };

  const stopCamera = () => { stream?.getTracks().forEach(t => t.stop()); };

  // Toque na câmera para capturar
  const handleCameraTouch = useCallback(() => {
    if (loadingRef.current || !videoRef.current || !canvasRef.current) return;
    
    const v = videoRef.current, c = canvasRef.current;
    c.width = v.videoWidth; 
    c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    c.toBlob(b => b && identifyImage(b), 'image/jpeg', 0.85);
  }, []);

  const identifyImage = async (blob) => {
    loadingRef.current = true;
    setLoading(true);
    setResult(null);
    setError(null);
    
    const fd = new FormData(); 
    fd.append("file", blob, "photo.jpg");
    
    try {
      const t = Date.now();
      const res = await fetch(`${API}/ai/identify`, { method: "POST", body: fd });
      const data = await res.json();
      setResult({ ...data, totalTime: Date.now() - t });
    } catch (e) { 
      setError(e.message);
    } finally { 
      loadingRef.current = false;
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) identifyImage(file);
  };

  const clearResult = () => {
    setResult(null);
    setError(null);
  };

  const r = result;
  
  // Config de confiança
  const confidenceConfig = {
    alta: { color: "#10b981", label: "ALTA CONFIANÇA", bg: "rgba(16,185,129,0.15)" },
    média: { color: "#f59e0b", label: "MÉDIA CONFIANÇA", bg: "rgba(245,158,11,0.15)" },
    baixa: { color: "#ef4444", label: "BAIXA CONFIANÇA", bg: "rgba(239,68,68,0.15)" }
  };
  
  const confData = confidenceConfig[r?.confidence] || confidenceConfig.baixa;
  
  // Cores das categorias conforme diretriz
  const getCategoryStyle = (cat) => {
    switch(cat) {
      case 'vegano': return { bg: '#22c55e', color: '#fff' };
      case 'vegetariano': return { bg: '#fff', color: '#333', border: '1px solid #333' };
      case 'proteína animal': return { bg: '#f97316', color: '#fff' };
      default: return { bg: '#666', color: '#fff' };
    }
  };
  
  const catStyle = getCategoryStyle(r?.category);

  // Formatar alertas de alérgenos
  const formatAllergenAlert = (riscos, confidence) => {
    if (!riscos || riscos.length === 0) return null;
    
    const alerts = riscos.map(risco => {
      // Se contém definitivamente
      if (risco.toLowerCase().includes('contém') || risco.toLowerCase().includes('alérgeno:')) {
        return { type: 'definite', text: risco.replace('Alérgeno:', 'Atenção: este prato contém') };
      }
      // Se pode conter (traços ou incerteza)
      if (risco.toLowerCase().includes('pode conter') || risco.toLowerCase().includes('traços')) {
        return { type: 'possible', text: `${risco}. Verifique com o atendente.` };
      }
      return { type: 'info', text: risco };
    });
    
    return alerts;
  };

  const allergenAlerts = formatAllergenAlert(r?.riscos, r?.confidence);

  return (
    <div className="app">
      {/* Header com Logo */}
      <header className="hdr">
        <div className="logo-container">
          <img src="/images/soulnutri-logo.png" alt="SoulNutri" className="logo" />
          <span className="trademark">®</span>
        </div>
        {status?.ready && <span className="st">✓ {status.total_dishes} pratos</span>}
      </header>

      {/* Câmera - TOQUE PARA CAPTURAR */}
      <div 
        className="cam-box" 
        onClick={handleCameraTouch}
        data-testid="camera-container"
      >
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={canvasRef} hidden />
        
        {/* Overlay de loading */}
        {loading && (
          <div className="cam-loading">
            <span>🔍</span>
            <p>Identificando...</p>
          </div>
        )}
        
        {/* Instrução de toque */}
        {!loading && !r && (
          <div className="cam-hint">
            <span>👆</span>
            <p>Toque para fotografar</p>
          </div>
        )}
      </div>

      {/* Botões de ação - MAIORES */}
      <div className="action-btns">
        <button 
          className="action-btn gallery" 
          onClick={() => fileInputRef.current?.click()}
          data-testid="gallery-button"
        >
          🖼️ Galeria
        </button>
        <button 
          className="action-btn clear" 
          onClick={clearResult}
          disabled={!r && !error}
          data-testid="clear-button"
        >
          🔄 Nova Foto
        </button>
      </div>

      <input 
        ref={fileInputRef} 
        type="file" 
        accept="image/*" 
        hidden 
        onChange={handleFileSelect} 
      />

      {/* RESULTADO */}
      {r?.ok && (
        <div className={`res ${r.confidence}`} data-testid="result-container">
          
          {/* Nome do Prato */}
          <h2 className="dish-name" data-testid="dish-name">{r.dish_display}</h2>
          
          {/* CATEGORIA - Logo abaixo do nome */}
          <div 
            className="category-badge" 
            style={{ 
              background: catStyle.bg, 
              color: catStyle.color,
              border: catStyle.border || 'none'
            }}
            data-testid="category-badge"
          >
            {r.category_emoji} {r.category?.toUpperCase()}
          </div>

          {/* ALÉRGENOS EM DESTAQUE */}
          {allergenAlerts && allergenAlerts.length > 0 && (
            <div className="allergen-alert" data-testid="allergen-alert">
              {allergenAlerts.map((alert, i) => (
                <div key={i} className={`alert-item ${alert.type}`}>
                  ⚠️ {alert.text}
                </div>
              ))}
            </div>
          )}

          {/* Indicador de Confiança */}
          <div className="conf-indicator" style={{ background: confData.bg, borderColor: confData.color }}>
            <span className="conf-label" style={{ color: confData.color }}>
              {confData.label}
            </span>
            <span className="conf-score" style={{ color: confData.color }}>
              {(r.score * 100).toFixed(0)}%
            </span>
          </div>
          
          {/* Descrição */}
          {r.descricao && <p className="desc" data-testid="dish-description">{r.descricao}</p>}

          {/* Técnica de Preparo */}
          {r.tecnica && (
            <div className="tecnica-box" data-testid="technique-box">
              <span>👨‍🍳 {r.tecnica}</span>
            </div>
          )}

          {/* Ingredientes */}
          {r.ingredientes?.length > 0 && (
            <div className="info-box" data-testid="ingredients-box">
              <h4>🥗 Ingredientes</h4>
              <p>{Array.isArray(r.ingredientes) ? r.ingredientes.join(', ') : r.ingredientes}</p>
            </div>
          )}

          {/* Benefícios */}
          {r.beneficios?.length > 0 && (
            <div className="info-box good" data-testid="benefits-box">
              <h4>✅ Benefícios para a Saúde</h4>
              <ul>{r.beneficios.map((b,i) => <li key={i}>{b}</li>)}</ul>
            </div>
          )}

          {/* Informação Nutricional */}
          {r.nutrition && (
            <div className="nutr" data-testid="nutrition-box">
              <div className="nutr-title">Informação Nutricional (100g)</div>
              <div className="nutr-grid">
                <div><b>{r.nutrition.calorias}</b><small>Calorias</small></div>
                <div><b>{r.nutrition.proteinas}</b><small>Proteínas</small></div>
                <div><b>{r.nutrition.carboidratos}</b><small>Carbos</small></div>
                <div><b>{r.nutrition.gorduras}</b><small>Gorduras</small></div>
              </div>
              {/* Aviso Cibi Sana */}
              {r.aviso_cibi_sana && (
                <div className="cibi-sana-text" data-testid="cibi-sana-badge">
                  {r.aviso_cibi_sana}
                </div>
              )}
            </div>
          )}

          <div className="time" data-testid="response-time">⚡ {r.search_time_ms?.toFixed(0)}ms</div>

          {/* Alternativas (apenas se confiança média/baixa) */}
          {r.alternatives?.length > 0 && r.confidence !== 'alta' && (
            <div className="alts" data-testid="alternatives-box">
              <small>Também pode ser:</small>
              {r.alternatives.map((a,i) => <span key={i}>{a}</span>)}
            </div>
          )}
        </div>
      )}

      {r && !r.ok && (
        <div className="err" data-testid="error-message">
          ❌ {r.message}
        </div>
      )}

      {error && (
        <div className="err" data-testid="network-error">
          ❌ Erro de conexão: {error}
        </div>
      )}

      {/* Rodapé discreto */}
      <footer className="footer">
        <small>Powered by Emergent</small>
      </footer>
    </div>
  );
}

export default App;
