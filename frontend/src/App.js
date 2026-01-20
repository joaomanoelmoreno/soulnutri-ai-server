import React, { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [mode, setMode] = useState('camera'); // 'camera' ou 'gallery'
  const [stream, setStream] = useState(null);
  const [autoCapture, setAutoCapture] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const captureIntervalRef = useRef(null);

  // Verificar status da API
  useEffect(() => {
    checkStatus();
  }, []);

  // Iniciar câmera automaticamente
  useEffect(() => {
    if (mode === 'camera') {
      startCamera();
    }
    return () => stopCamera();
  }, [mode]);

  // Auto-captura a cada 3 segundos quando ativado
  useEffect(() => {
    if (autoCapture && stream) {
      captureIntervalRef.current = setInterval(() => {
        captureAndIdentify();
      }, 3000);
    }
    return () => {
      if (captureIntervalRef.current) {
        clearInterval(captureIntervalRef.current);
      }
    };
  }, [autoCapture, stream]);

  const checkStatus = async () => {
    try {
      const response = await fetch(`${API}/ai/status`);
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      setStatus({ ok: false, message: "Erro ao conectar" });
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 640, height: 480 }
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (error) {
      console.error("Erro ao acessar câmera:", error);
      setMode('gallery');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setAutoCapture(false);
  };

  const captureAndIdentify = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || loading) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    canvas.toBlob(async (blob) => {
      if (blob) {
        await identifyImage(blob);
      }
    }, 'image/jpeg', 0.8);
  }, [loading]);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (file) {
      await identifyImage(file);
    }
  };

  const identifyImage = async (imageBlob) => {
    setLoading(true);

    const formData = new FormData();
    formData.append("file", imageBlob, "photo.jpg");

    try {
      const startTime = Date.now();
      const response = await fetch(`${API}/ai/identify`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      const totalTime = Date.now() - startTime;
      
      setResult({ ...data, totalTime });
    } catch (error) {
      setResult({ 
        ok: false, 
        message: "Erro: " + error.message 
      });
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case "alta": return "#22c55e";
      case "média": return "#f59e0b";
      case "baixa": return "#ef4444";
      default: return "#6b7280";
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case "vegano": return "#22c55e";
      case "vegetariano": return "#84cc16";
      case "proteína animal": return "#f97316";
      default: return "#6b7280";
    }
  };

  return (
    <div className="app">
      {/* Header compacto */}
      <header className="header">
        <h1>🍽️ SoulNutri</h1>
        {status?.ready && (
          <span className="status-badge">✅ {status.total_dishes} pratos</span>
        )}
      </header>

      {/* Área principal */}
      <main className="main">
        {/* Seletor de modo */}
        <div className="mode-selector">
          <button 
            className={mode === 'camera' ? 'active' : ''} 
            onClick={() => setMode('camera')}
          >
            📷 Câmera
          </button>
          <button 
            className={mode === 'gallery' ? 'active' : ''} 
            onClick={() => { setMode('gallery'); fileInputRef.current?.click(); }}
          >
            🖼️ Galeria
          </button>
        </div>

        {/* Câmera */}
        {mode === 'camera' && (
          <div className="camera-container">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className="camera-video"
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            
            <div className="camera-controls">
              <button 
                className="capture-btn"
                onClick={captureAndIdentify}
                disabled={loading || !stream}
              >
                {loading ? "⏳" : "📸"}
              </button>
              
              <label className="auto-capture-toggle">
                <input 
                  type="checkbox"
                  checked={autoCapture}
                  onChange={(e) => setAutoCapture(e.target.checked)}
                />
                Auto (3s)
              </label>
            </div>
          </div>
        )}

        {/* Input de arquivo escondido */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {/* Loading */}
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner">🔍</div>
            <p>Identificando...</p>
          </div>
        )}

        {/* Resultado */}
        {result && result.ok && (
          <div className={`result-card ${result.confidence}`}>
            {/* Cabeçalho do resultado */}
            <div className="result-header">
              <span className="category-badge" style={{ backgroundColor: getCategoryColor(result.category) }}>
                {result.category_emoji} {result.category}
              </span>
              <span 
                className="confidence-badge"
                style={{ backgroundColor: getConfidenceColor(result.confidence) }}
              >
                {(result.score * 100).toFixed(0)}%
              </span>
            </div>

            {/* Nome do prato */}
            <h2 className="dish-name">{result.dish_display}</h2>

            {/* Informações nutricionais */}
            {result.nutrition && (
              <div className="nutrition-grid">
                <div className="nutrition-item">
                  <span className="nutrition-value">{result.nutrition.calorias}</span>
                  <span className="nutrition-label">Calorias</span>
                </div>
                <div className="nutrition-item">
                  <span className="nutrition-value">{result.nutrition.proteinas}</span>
                  <span className="nutrition-label">Proteínas</span>
                </div>
                <div className="nutrition-item">
                  <span className="nutrition-value">{result.nutrition.carboidratos}</span>
                  <span className="nutrition-label">Carbos</span>
                </div>
                <div className="nutrition-item">
                  <span className="nutrition-value">{result.nutrition.gorduras}</span>
                  <span className="nutrition-label">Gorduras</span>
                </div>
              </div>
            )}

            {/* Tempo de resposta */}
            <div className="response-time">
              ⚡ {result.search_time_ms?.toFixed(0)}ms
            </div>

            {/* Alternativas (só se confiança média/baixa) */}
            {result.alternatives?.length > 0 && (
              <div className="alternatives">
                <p>Também pode ser:</p>
                <div className="alternatives-list">
                  {result.alternatives.map((alt, i) => (
                    <span key={i} className="alt-tag">{alt}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Erro */}
        {result && !result.ok && (
          <div className="error-card">
            <span>❌</span>
            <p>{result.message}</p>
          </div>
        )}
      </main>

      {/* Instruções */}
      <footer className="footer">
        <p>Aponte a câmera para o prato • Resultado em tempo real</p>
      </footer>
    </div>
  );
}

export default App;
