import React, { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [stream, setStream] = useState(null);
  const [autoCapture, setAutoCapture] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const autoIntervalRef = useRef(null);
  const countdownIntervalRef = useRef(null);

  useEffect(() => { 
    checkStatus(); 
    startCamera(); 
    return () => {
      stopCamera();
      clearAllIntervals();
    };
  }, []);

  const clearAllIntervals = () => {
    if (autoIntervalRef.current) clearInterval(autoIntervalRef.current);
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
  };

  // Gerenciar auto-captura com countdown visual
  useEffect(() => {
    clearAllIntervals();
    
    if (autoCapture && stream && !loading) {
      // Iniciar countdown
      setCountdown(3);
      
      countdownIntervalRef.current = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) return 3;
          return prev - 1;
        });
      }, 1000);

      // Captura a cada 3 segundos
      autoIntervalRef.current = setInterval(() => {
        captureAndIdentify();
      }, 3000);
    } else {
      setCountdown(0);
    }

    return () => clearAllIntervals();
  }, [autoCapture, stream]);

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

  const captureAndIdentify = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || loading) return;
    
    // LIMPAR resultado anterior antes de nova busca
    setResult(null);
    
    const v = videoRef.current, c = canvasRef.current;
    c.width = v.videoWidth; 
    c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    c.toBlob(b => b && identifyImage(b), 'image/jpeg', 0.85);
  }, [loading]);

  const identifyImage = async (blob) => {
    setLoading(true);
    // LIMPAR resultado anterior
    setResult(null);
    
    const fd = new FormData(); 
    fd.append("file", blob, "photo.jpg");
    
    try {
      const t = Date.now();
      const res = await fetch(`${API}/ai/identify`, { method: "POST", body: fd });
      const data = await res.json();
      setResult({ ...data, totalTime: Date.now() - t });
    } catch (e) { 
      setResult({ ok: false, message: e.message }); 
    } finally { 
      setLoading(false); 
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Desativar auto-captura ao selecionar da galeria
      setAutoCapture(false);
      identifyImage(file);
    }
  };

  const toggleAutoCapture = (enabled) => {
    setAutoCapture(enabled);
    if (enabled) {
      // Limpar resultado ao ativar auto
      setResult(null);
    }
  };

  const r = result;
  
  // Cores e labels de confiança
  const confidenceConfig = {
    alta: { color: "#10b981", label: "ALTA CONFIANÇA", bg: "rgba(16,185,129,0.15)" },
    média: { color: "#f59e0b", label: "MÉDIA CONFIANÇA", bg: "rgba(245,158,11,0.15)" },
    baixa: { color: "#ef4444", label: "BAIXA CONFIANÇA", bg: "rgba(239,68,68,0.15)" }
  };
  
  const confData = confidenceConfig[r?.confidence] || confidenceConfig.baixa;
  const catColor = { vegano: "#22c55e", vegetariano: "#84cc16", "proteína animal": "#f97316" }[r?.category] || "#666";

  return (
    <div className="app">
      <header className="hdr">
        <h1>🍽️ SoulNutri</h1>
        {status?.ready && <span className="st">✓ {status.total_dishes} pratos</span>}
      </header>

      <div className="cam-box">
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={canvasRef} hidden />
        <div className="cam-ctrl">
          <button 
            className="cap-btn" 
            onClick={captureAndIdentify} 
            disabled={loading}
            data-testid="capture-button"
          >
            {loading ? "⏳" : "📸"}
          </button>
          <label className="auto-lbl">
            <input 
              type="checkbox" 
              checked={autoCapture} 
              onChange={e => toggleAutoCapture(e.target.checked)}
              data-testid="auto-capture-toggle" 
            />
            Auto {autoCapture && countdown > 0 ? `(${countdown}s)` : "3s"}
          </label>
        </div>
      </div>

      <input 
        ref={fileInputRef} 
        type="file" 
        accept="image/*" 
        hidden 
        onChange={handleFileSelect} 
      />
      <button 
        className="gal-btn" 
        onClick={() => fileInputRef.current?.click()}
        data-testid="gallery-button"
      >
        🖼️ Galeria
      </button>

      {loading && (
        <div className="load">
          <span>🔍</span>
        </div>
      )}

      {r?.ok && (
        <div className={`res ${r.confidence}`} data-testid="result-container">
          {/* Indicador de Confiança */}
          <div className="conf-indicator" style={{ background: confData.bg, borderColor: confData.color }}>
            <span className="conf-label" style={{ color: confData.color }}>
              {confData.label}
            </span>
            <span className="conf-score" style={{ color: confData.color }}>
              {(r.score * 100).toFixed(0)}%
            </span>
          </div>

          <div className="res-top">
            <span className="cat" style={{background: catColor}} data-testid="category-badge">
              {r.category_emoji} {r.category}
            </span>
          </div>
          
          <h2 data-testid="dish-name">{r.dish_display}</h2>
          
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
              <h4>✅ Benefícios</h4>
              <ul>{r.beneficios.map((b,i) => <li key={i}>{b}</li>)}</ul>
            </div>
          )}

          {/* Riscos/Atenção */}
          {r.riscos?.length > 0 && (
            <div className="info-box warn" data-testid="risks-box">
              <h4>⚠️ Atenção (Alérgenos e Riscos)</h4>
              <ul>{r.riscos.map((x,i) => <li key={i}>{x}</li>)}</ul>
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
            </div>
          )}

          {/* Aviso Cibi Sana */}
          {r.aviso_cibi_sana && (
            <div className="cibi-sana-badge" data-testid="cibi-sana-badge">
              <span>🌿 {r.aviso_cibi_sana}</span>
            </div>
          )}

          <div className="time" data-testid="response-time">⚡ {r.search_time_ms?.toFixed(0)}ms</div>

          {r.alternatives?.length > 0 && (
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
    </div>
  );
}

export default App;
