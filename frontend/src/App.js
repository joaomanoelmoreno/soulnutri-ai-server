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
  const [showFeedback, setShowFeedback] = useState(false);
  const [dishes, setDishes] = useState([]);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [lastImageBlob, setLastImageBlob] = useState(null);
  const [newDishName, setNewDishName] = useState("");
  const [creatingDish, setCreatingDish] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [multiMode, setMultiMode] = useState(false);
  const [multiResult, setMultiResult] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const loadingRef = useRef(false);

  useEffect(() => { 
    checkStatus(); 
    startCamera();
    loadDishes();
    return () => stopCamera();
  }, []);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API}/ai/status`);
      setStatus(await res.json());
    } catch { setStatus({ ok: false }); }
  };

  const loadDishes = async () => {
    try {
      const res = await fetch(`${API}/ai/dishes`);
      const data = await res.json();
      if (data.ok) setDishes(data.dishes || []);
    } catch (e) { console.error('Erro ao carregar pratos:', e); }
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

  const handleCameraTouch = useCallback(() => {
    if (loadingRef.current || !videoRef.current || !canvasRef.current) return;
    
    const v = videoRef.current, c = canvasRef.current;
    c.width = v.videoWidth; 
    c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    c.toBlob(b => {
      if (b) {
        setLastImageBlob(b);
        identifyImage(b);
      }
    }, 'image/jpeg', 0.85);
  }, []);

  const identifyImage = async (blob) => {
    loadingRef.current = true;
    setLoading(true);
    setResult(null);
    setMultiResult(null);
    setError(null);
    setFeedbackSent(false);
    setShowFeedback(false);
    
    const fd = new FormData(); 
    fd.append("file", blob, "photo.jpg");
    
    try {
      const t = Date.now();
      const endpoint = multiMode ? `${API}/ai/identify-multi` : `${API}/ai/identify`;
      const res = await fetch(endpoint, { method: "POST", body: fd });
      const data = await res.json();
      
      if (multiMode) {
        setMultiResult({ ...data, totalTime: Date.now() - t });
      } else {
        setResult({ ...data, totalTime: Date.now() - t });
      }
    } catch (e) { 
      setError(e.message);
    } finally { 
      loadingRef.current = false;
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setLastImageBlob(file);
      identifyImage(file);
    }
  };

  const clearResult = () => {
    setResult(null);
    setMultiResult(null);
    setError(null);
    setShowFeedback(false);
    setFeedbackSent(false);
    setLastImageBlob(null);
    setNewDishName("");
    setSearchFilter("");
  };

  // Enviar feedback - CORRETO
  const sendFeedbackCorrect = async () => {
    if (!lastImageBlob || !result?.dish) return;
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_slug", result.dish);
    fd.append("is_correct", "true");
    
    try {
      const res = await fetch(`${API}/ai/feedback`, { method: "POST", body: fd });
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
      }
    } catch (e) {
      console.error('Erro ao enviar feedback:', e);
    }
  };

  // Enviar feedback - INCORRETO (com correção)
  const sendFeedbackIncorrect = async (correctSlug) => {
    if (!lastImageBlob) return;
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_slug", correctSlug);
    fd.append("is_correct", "false");
    fd.append("original_dish", result?.dish || "");
    
    try {
      const res = await fetch(`${API}/ai/feedback`, { method: "POST", body: fd });
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
      }
    } catch (e) {
      console.error('Erro ao enviar feedback:', e);
    }
  };

  // CRIAR PRATO NOVO com IA
  const createNewDish = async () => {
    if (!lastImageBlob || !newDishName.trim()) return;
    
    setCreatingDish(true);
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_name", newDishName.trim());
    
    try {
      const res = await fetch(`${API}/ai/create-dish`, { method: "POST", body: fd });
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
        setNewDishName("");
        // Atualizar lista de pratos
        loadDishes();
        // Mostrar resultado do novo prato
        if (data.dish_info) {
          setResult({
            ok: true,
            identified: true,
            dish: data.dish_slug,
            dish_display: data.dish_name,
            confidence: 'alta',
            score: 1.0,
            message: 'Prato cadastrado com sucesso!',
            ...data.dish_info,
            source: 'new_dish'
          });
        }
      } else {
        alert(data.error || 'Erro ao criar prato');
      }
    } catch (e) {
      console.error('Erro ao criar prato:', e);
      alert('Erro ao criar prato: ' + e.message);
    } finally {
      setCreatingDish(false);
    }
  };

  // Descartar foto
  const discardPhoto = () => {
    setShowFeedback(false);
    setFeedbackSent(true);
    setNewDishName("");
  };

  const r = result;
  
  // Config de confiança
  const confidenceConfig = {
    alta: { color: "#10b981", label: "ALTA CONFIANÇA", bg: "rgba(16,185,129,0.15)" },
    média: { color: "#f59e0b", label: "MÉDIA CONFIANÇA", bg: "rgba(245,158,11,0.15)" },
    baixa: { color: "#ef4444", label: "BAIXA CONFIANÇA", bg: "rgba(239,68,68,0.15)" }
  };
  
  const confData = confidenceConfig[r?.confidence] || confidenceConfig.baixa;
  
  // Cores das categorias
  const getCategoryStyle = (cat) => {
    switch(cat) {
      case 'vegano': return { bg: '#22c55e', color: '#fff' };
      case 'vegetariano': return { bg: '#fff', color: '#333', border: '1px solid #333' };
      case 'proteína animal': return { bg: '#f97316', color: '#fff' };
      default: return { bg: '#666', color: '#fff' };
    }
  };
  
  const catStyle = getCategoryStyle(r?.category);

  // Formatar alertas de alérgenos - SEMPRE MOSTRAR
  const getAllergenDisplay = (riscos) => {
    if (!riscos || riscos.length === 0) {
      return { hasAllergens: false, text: "✅ Não contém alérgenos conhecidos" };
    }
    
    const allergenRisks = riscos.filter(r => 
      r.toLowerCase().includes('alérgeno') || 
      r.toLowerCase().includes('contém') ||
      r.toLowerCase().includes('glúten') ||
      r.toLowerCase().includes('lactose') ||
      r.toLowerCase().includes('crustáceo') ||
      r.toLowerCase().includes('camarão') ||
      r.toLowerCase().includes('amendoim') ||
      r.toLowerCase().includes('soja') ||
      r.toLowerCase().includes('ovo')
    );
    
    if (allergenRisks.length === 0) {
      return { hasAllergens: false, text: "✅ Não contém alérgenos conhecidos" };
    }
    
    return { 
      hasAllergens: true, 
      alerts: allergenRisks.map(risco => ({
        type: risco.toLowerCase().includes('pode conter') ? 'possible' : 'definite',
        text: risco
      }))
    };
  };

  const allergenInfo = getAllergenDisplay(r?.riscos);

  // Filtrar pratos na busca
  const filteredDishes = dishes.filter(d => 
    d.name.toLowerCase().includes(searchFilter.toLowerCase())
  );

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

      {/* Câmera com moldura guia */}
      <div 
        className="cam-box" 
        onClick={handleCameraTouch}
        data-testid="camera-container"
      >
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={canvasRef} hidden />
        
        <div className="cam-guide">
          <div className="guide-frame"></div>
          <span className="guide-text">Posicione o prato aqui</span>
        </div>
        
        {loading && (
          <div className="cam-loading">
            <span>🔍</span>
            <p>Identificando...</p>
          </div>
        )}
        
        {!loading && !r && (
          <div className="cam-hint">
            <span>👆</span>
            <p>Toque para fotografar</p>
          </div>
        )}
      </div>

      {/* Botões de ação */}
      <div className="action-btns">
        <button 
          className="action-btn gallery" 
          onClick={() => fileInputRef.current?.click()}
          data-testid="gallery-button"
        >
          🖼️ Galeria
        </button>
        <button 
          className={`action-btn mode ${multiMode ? 'active' : ''}`}
          onClick={() => setMultiMode(!multiMode)}
          data-testid="multi-mode-button"
        >
          {multiMode ? '🍽️ Multi' : '🍴 Único'}
        </button>
        <button 
          className="action-btn clear" 
          onClick={clearResult}
          disabled={!r && !multiResult && !error}
          data-testid="clear-button"
        >
          🔄 Nova
        </button>
      </div>

      {/* Indicador de modo */}
      {multiMode && (
        <div className="mode-indicator" data-testid="mode-indicator">
          📊 Modo Multi-Item: Identifica vários alimentos no prato
        </div>
      )}

      <input 
        ref={fileInputRef} 
        type="file" 
        accept="image/*"
        capture="environment"
        hidden 
        onChange={handleFileSelect} 
      />

      {/* RESULTADO */}
      {r?.ok && (
        <div className={`res ${r.confidence}`} data-testid="result-container">
          
          {/* Indicador de fonte */}
          {r.source === 'generic_ai' && (
            <div className="source-badge" data-testid="source-badge">
              🤖 Identificado por IA Genérica (prato não cadastrado)
            </div>
          )}
          {r.source === 'new_dish' && (
            <div className="source-badge new" data-testid="source-badge">
              ✨ Novo prato cadastrado com sucesso!
            </div>
          )}
          
          {/* Nome do Prato */}
          <h2 className="dish-name" data-testid="dish-name">{r.dish_display}</h2>
          
          {/* CATEGORIA */}
          <div 
            className="category-badge" 
            style={{ background: catStyle.bg, color: catStyle.color, border: catStyle.border || 'none' }}
            data-testid="category-badge"
          >
            {r.category_emoji} {r.category?.toUpperCase()}
          </div>

          {/* ALÉRGENOS - SEMPRE MOSTRAR */}
          <div className={`allergen-section ${allergenInfo.hasAllergens ? 'has-allergens' : 'no-allergens'}`}>
            {allergenInfo.hasAllergens ? (
              allergenInfo.alerts.map((alert, i) => (
                <div key={i} className={`alert-item ${alert.type}`}>
                  ⚠️ {alert.text}
                </div>
              ))
            ) : (
              <div className="alert-item safe">
                {allergenInfo.text}
              </div>
            )}
          </div>

          {/* Indicador de Confiança */}
          <div className="conf-indicator" style={{ background: confData.bg, borderColor: confData.color }}>
            <span className="conf-label" style={{ color: confData.color }}>{confData.label}</span>
            <span className="conf-score" style={{ color: confData.color }}>{(r.score * 100).toFixed(0)}%</span>
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

          {/* SEÇÃO CIENTÍFICA - Informações relevantes */}
          {(r.beneficio_principal || r.curiosidade_cientifica) && (
            <div className="scientific-section" data-testid="scientific-section">
              {r.beneficio_principal && (
                <div className="sci-box benefit" data-testid="main-benefit">
                  <h4>🔬 Você Sabia?</h4>
                  <p>{r.beneficio_principal}</p>
                </div>
              )}
              
              {r.curiosidade_cientifica && (
                <div className="sci-box curiosity" data-testid="curiosity">
                  <h4>💡 Curiosidade Científica</h4>
                  <p>{r.curiosidade_cientifica}</p>
                </div>
              )}
              
              {r.alerta_saude && (
                <div className="sci-box alert" data-testid="health-alert">
                  <h4>⚠️ Atenção</h4>
                  <p>{r.alerta_saude}</p>
                </div>
              )}
              
              {r.referencia_pesquisa && (
                <div className="sci-reference" data-testid="reference">
                  📚 Fonte: {r.referencia_pesquisa}
                </div>
              )}
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
              {r.aviso_cibi_sana && (
                <div className="cibi-sana-text" data-testid="cibi-sana-badge">{r.aviso_cibi_sana}</div>
              )}
            </div>
          )}

          <div className="time" data-testid="response-time">⚡ {r.search_time_ms?.toFixed(0)}ms</div>

          {/* Alternativas */}
          {r.alternatives?.length > 0 && r.confidence !== 'alta' && (
            <div className="alts" data-testid="alternatives-box">
              <small>Também pode ser:</small>
              {r.alternatives.map((a,i) => <span key={i}>{a}</span>)}
            </div>
          )}

          {/* BOTÕES DE FEEDBACK */}
          {!feedbackSent && r.source !== 'new_dish' && (
            <div className="feedback-section">
              <p className="feedback-question">Este reconhecimento está correto?</p>
              <div className="feedback-btns">
                <button className="fb-btn correct" onClick={sendFeedbackCorrect}>
                  ✅ Sim, correto
                </button>
                <button className="fb-btn incorrect" onClick={() => setShowFeedback(true)}>
                  ❌ Não, corrigir
                </button>
              </div>
            </div>
          )}

          {feedbackSent && (
            <div className="feedback-thanks">
              ✅ Obrigado pelo feedback! Isso ajuda a melhorar o reconhecimento.
            </div>
          )}

          {/* BOTÃO DE COMPARTILHAR */}
          {(r.beneficio_principal || r.curiosidade_cientifica) && (
            <button 
              className="share-btn"
              onClick={() => {
                const text = `🍽️ ${r.dish_display}\n\n🔬 ${r.beneficio_principal || ''}\n\n💡 ${r.curiosidade_cientifica || ''}\n\n📚 ${r.referencia_pesquisa || ''}\n\nDescubra mais no SoulNutri - seu agente de nutrição virtual!`;
                if (navigator.share) {
                  navigator.share({ title: 'SoulNutri', text });
                } else {
                  navigator.clipboard.writeText(text);
                  alert('Texto copiado! Cole para compartilhar.');
                }
              }}
              data-testid="share-button"
            >
              📤 Compartilhar curiosidade
            </button>
          )}
        </div>
      )}

      {/* MODAL DE CORREÇÃO */}
      {showFeedback && (
        <div className="modal-overlay" onClick={() => setShowFeedback(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Corrigir identificação</h3>
            
            {/* Campo para NOVO PRATO */}
            <div className="new-dish-section">
              <p className="section-label">📝 Cadastrar prato novo:</p>
              <div className="new-dish-input">
                <input 
                  type="text"
                  placeholder="Digite o nome do prato..."
                  value={newDishName}
                  onChange={e => setNewDishName(e.target.value)}
                />
                <button 
                  onClick={createNewDish} 
                  disabled={!newDishName.trim() || creatingDish}
                  className="create-btn"
                >
                  {creatingDish ? '⏳' : '➕'} {creatingDish ? 'Criando...' : 'Criar'}
                </button>
              </div>
              <small>A IA vai gerar automaticamente: categoria, ingredientes, benefícios, riscos e alérgenos</small>
            </div>

            <div className="divider">ou selecione um prato existente:</div>

            {/* Busca */}
            <input 
              type="text"
              className="search-input"
              placeholder="🔍 Buscar prato..."
              value={searchFilter}
              onChange={e => setSearchFilter(e.target.value)}
            />

            {/* Lista de pratos */}
            <div className="dishes-list">
              {filteredDishes.map(d => (
                <button 
                  key={d.slug} 
                  className="dish-option"
                  onClick={() => sendFeedbackIncorrect(d.slug)}
                >
                  {d.category_emoji} {d.name}
                </button>
              ))}
            </div>
            
            {/* Ações do modal - FIXAS NO FINAL */}
            <div className="modal-actions-fixed">
              <button className="discard-btn" onClick={discardPhoto}>
                🗑️ Descartar foto (inutilizável)
              </button>
              <button className="cancel-btn" onClick={() => setShowFeedback(false)}>
                ✕ Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {r && !r.ok && (
        <div className="err" data-testid="error-message">❌ {r.message}</div>
      )}

      {error && (
        <div className="err" data-testid="network-error">❌ Erro de conexão: {error}</div>
      )}

      {/* Rodapé */}
      <footer className="footer">
        <small>Powered by Emergent</small>
      </footer>
    </div>
  );
}

export default App;
