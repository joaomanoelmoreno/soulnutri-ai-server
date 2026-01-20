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
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => { checkStatus(); startCamera(); return () => stopCamera(); }, []);

  useEffect(() => {
    let interval;
    if (autoCapture && stream) {
      interval = setInterval(captureAndIdentify, 3000);
    }
    return () => clearInterval(interval);
  }, [autoCapture, stream]);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API}/ai/status`);
      setStatus(await res.json());
    } catch { setStatus({ ok: false }); }
  };

  const startCamera = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      setStream(s);
      if (videoRef.current) videoRef.current.srcObject = s;
    } catch { console.error("Câmera não disponível"); }
  };

  const stopCamera = () => { stream?.getTracks().forEach(t => t.stop()); };

  const captureAndIdentify = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || loading) return;
    const v = videoRef.current, c = canvasRef.current;
    c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    c.toBlob(b => b && identifyImage(b), 'image/jpeg', 0.8);
  }, [loading]);

  const identifyImage = async (blob) => {
    setLoading(true);
    const fd = new FormData(); fd.append("file", blob, "photo.jpg");
    try {
      const t = Date.now();
      const res = await fetch(`${API}/ai/identify`, { method: "POST", body: fd });
      const data = await res.json();
      setResult({ ...data, totalTime: Date.now() - t });
    } catch (e) { setResult({ ok: false, message: e.message }); }
    finally { setLoading(false); }
  };

  const r = result;
  const confColor = { alta: "#10b981", média: "#f59e0b", baixa: "#ef4444" }[r?.confidence] || "#666";
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
          <button className="cap-btn" onClick={captureAndIdentify} disabled={loading}>
            {loading ? "⏳" : "📸"}
          </button>
          <label className="auto-lbl">
            <input type="checkbox" checked={autoCapture} onChange={e => setAutoCapture(e.target.checked)} />
            Auto 3s
          </label>
        </div>
      </div>

      <input ref={fileInputRef} type="file" accept="image/*" hidden onChange={e => e.target.files[0] && identifyImage(e.target.files[0])} />
      <button className="gal-btn" onClick={() => fileInputRef.current?.click()}>🖼️ Galeria</button>

      {loading && <div className="load"><span>🔍</span></div>}

      {r?.ok && (
        <div className={`res ${r.confidence}`}>
          <div className="res-top">
            <span className="cat" style={{background: catColor}}>{r.category_emoji} {r.category}</span>
            <span className="conf" style={{background: confColor}}>{(r.score*100).toFixed(0)}%</span>
          </div>
          
          <h2>{r.dish_display}</h2>
          
          {r.descricao && <p className="desc">{r.descricao}</p>}
          
          {r.nutrition && (
            <div className="nutr">
              <div className="nutr-title">Informação Nutricional (100g)</div>
              <div className="nutr-grid">
                <div><b>{r.nutrition.calorias}</b><small>Calorias</small></div>
                <div><b>{r.nutrition.proteinas}</b><small>Proteínas</small></div>
                <div><b>{r.nutrition.carboidratos}</b><small>Carbos</small></div>
                <div><b>{r.nutrition.gorduras}</b><small>Gorduras</small></div>
              </div>
            </div>
          )}

          {r.ingredientes?.length > 0 && (
            <div className="info-box">
              <h4>🥗 Ingredientes</h4>
              <p>{r.ingredientes.join(', ')}</p>
            </div>
          )}

          {r.beneficios?.length > 0 && (
            <div className="info-box good">
              <h4>✅ Benefícios</h4>
              <ul>{r.beneficios.map((b,i) => <li key={i}>{b}</li>)}</ul>
            </div>
          )}

          {r.riscos?.length > 0 && (
            <div className="info-box warn">
              <h4>⚠️ Atenção</h4>
              <ul>{r.riscos.map((x,i) => <li key={i}>{x}</li>)}</ul>
            </div>
          )}

          <div className="time">⚡ {r.search_time_ms?.toFixed(0)}ms</div>

          {r.alternatives?.length > 0 && (
            <div className="alts">
              <small>Também pode ser:</small>
              {r.alternatives.map((a,i) => <span key={i}>{a}</span>)}
            </div>
          )}
        </div>
      )}

      {r && !r.ok && <div className="err">❌ {r.message}</div>}
    </div>
  );
}
export default App;
