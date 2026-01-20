import React, { useState, useRef } from "react";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const fileInputRef = useRef(null);

  // Verificar status da API ao carregar
  React.useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await fetch(`${API}/ai/status`);
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      setStatus({ ok: false, message: "Erro ao conectar com servidor" });
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleCapture = () => {
    fileInputRef.current?.click();
  };

  const identifyDish = async () => {
    if (!image) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", image);

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
        message: "Erro ao identificar prato: " + error.message 
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

  const getConfidenceEmoji = (confidence) => {
    switch (confidence) {
      case "alta": return "✅";
      case "média": return "⚠️";
      case "baixa": return "❌";
      default: return "❓";
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>🍽️ SoulNutri</h1>
        <p className="tagline">Como o Waze para alimentação saudável</p>
      </header>

      {/* Status */}
      <div className="status-bar">
        {status?.ready ? (
          <span className="status-ok">✅ Sistema pronto ({status.total_dishes} pratos)</span>
        ) : (
          <span className="status-warn">⚠️ {status?.message || "Verificando..."}</span>
        )}
      </div>

      {/* Main Content */}
      <main className="main">
        {/* Upload Area */}
        <div className="upload-area" onClick={handleCapture}>
          {preview ? (
            <img src={preview} alt="Preview" className="preview-image" />
          ) : (
            <div className="upload-placeholder">
              <span className="upload-icon">📷</span>
              <p>Clique para tirar foto ou selecionar imagem</p>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleImageChange}
            style={{ display: "none" }}
          />
        </div>

        {/* Identify Button */}
        {image && (
          <button 
            className="identify-btn"
            onClick={identifyDish}
            disabled={loading}
          >
            {loading ? "🔍 Identificando..." : "🔍 Identificar Prato"}
          </button>
        )}

        {/* Result */}
        {result && (
          <div className={`result-card ${result.confidence}`}>
            {result.ok ? (
              <>
                <div className="result-header">
                  <span className="confidence-emoji">
                    {getConfidenceEmoji(result.confidence)}
                  </span>
                  <span 
                    className="confidence-badge"
                    style={{ backgroundColor: getConfidenceColor(result.confidence) }}
                  >
                    Confiança {result.confidence?.toUpperCase()}
                  </span>
                </div>

                <h2 className="dish-name">{result.dish_display || result.dish}</h2>
                
                <p className="result-message">{result.message}</p>

                <div className="result-details">
                  <p><strong>Score:</strong> {(result.score * 100).toFixed(1)}%</p>
                  <p><strong>Tempo de busca:</strong> {result.search_time_ms?.toFixed(0)}ms</p>
                  <p><strong>Tempo total:</strong> {result.totalTime}ms</p>
                </div>

                {result.alternatives?.length > 0 && (
                  <div className="alternatives">
                    <p><strong>Alternativas:</strong></p>
                    <ul>
                      {result.alternatives.map((alt, i) => (
                        <li key={i}>{alt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              <div className="error-result">
                <span>❌</span>
                <p>{result.message}</p>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="instructions">
          <h3>Como usar:</h3>
          <ol>
            <li>📷 Tire uma foto do prato ou selecione uma imagem</li>
            <li>🔍 Clique em "Identificar Prato"</li>
            <li>✅ Veja o resultado com nível de confiança</li>
          </ol>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>SoulNutri © 2025 - Informação em tempo real para escolhas conscientes</p>
      </footer>
    </div>
  );
}

export default App;
