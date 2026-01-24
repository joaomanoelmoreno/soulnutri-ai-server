import React, { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";
import "./Premium.css";
import { PremiumRegister, PremiumLogin, DailyCounter } from "./Premium";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Timeout para requisições (evita travamentos)
const REQUEST_TIMEOUT = 15000; // 15 segundos

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
  const [cameraError, setCameraError] = useState(null);
  const [previewImageUrl, setPreviewImageUrl] = useState(null); // Preview da imagem selecionada
  const [showMultiCorrection, setShowMultiCorrection] = useState(false); // Modal correção multi
  const [multiCorrections, setMultiCorrections] = useState({ principal: '', acompanhamentos: '' }); // Correções
  // Premium states
  const [showPremium, setShowPremium] = useState(null); // null, 'login', 'register', 'dashboard'
  const [premiumUser, setPremiumUser] = useState(null);
  const [dailySummary, setDailySummary] = useState(null);
  // Menu e PWA
  const [showMenu, setShowMenu] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const loadingRef = useRef(false);
  const abortControllerRef = useRef(null);
  const mountedRef = useRef(true);
  const lastTouchRef = useRef(0);

  useEffect(() => { 
    mountedRef.current = true;
    checkStatus(); 
    startCamera();
    loadDishes();
    checkPremiumSession();
    
    // Detectar se já está instalado como PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }
    
    // Capturar evento de instalação PWA
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    
    return () => {
      mountedRef.current = false;
      stopCamera();
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      // Cancelar requisições pendentes
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const checkStatus = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/ai/status`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (mountedRef.current) setStatus(await res.json());
    } catch { 
      if (mountedRef.current) setStatus({ ok: false }); 
    }
  };

  const loadDishes = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/ai/dishes`, { signal: controller.signal });
      clearTimeout(timeoutId);
      const data = await res.json();
      if (data.ok && mountedRef.current) setDishes(data.dishes || []);
    } catch (e) { console.error('Erro ao carregar pratos:', e); }
  };

  // Verificar sessão Premium salva
  const checkPremiumSession = async () => {
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      if (pin && nome) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        const fd = new FormData();
        fd.append('pin', pin);
        fd.append('nome', nome);
        const res = await fetch(`${API}/premium/login`, { 
          method: 'POST', 
          body: fd,
          signal: controller.signal 
        });
        clearTimeout(timeoutId);
        const data = await res.json();
        if (data.ok && mountedRef.current) {
          setPremiumUser(data.user);
          loadDailySummary();
        }
      }
    } catch (e) {
      console.error('Erro ao verificar sessão:', e);
    }
  };

  // Carregar resumo diário
  const loadDailySummary = async () => {
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      if (!pin || !nome) return;
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const fd = new FormData();
      fd.append('pin', pin);
      fd.append('nome', nome);
      const res = await fetch(`${API}/premium/login`, { 
        method: 'POST', 
        body: fd,
        signal: controller.signal 
      });
      clearTimeout(timeoutId);
      const data = await res.json();
      
      if (!mountedRef.current) return;
      
      if (data.ok && data.daily_log) {
        setDailySummary({
          nome: data.user.nome,
          meta: data.user.meta_calorica?.meta_sugerida || 2000,
          consumido: data.daily_log.calorias_total || 0,
          restante: (data.user.meta_calorica?.meta_sugerida || 2000) - (data.daily_log.calorias_total || 0),
          percentual: ((data.daily_log.calorias_total || 0) / (data.user.meta_calorica?.meta_sugerida || 2000)) * 100,
          pratos: data.daily_log.pratos || [],
          totais: {
            calorias: data.daily_log.calorias_total || 0,
            proteinas: data.daily_log.proteinas_total || 0,
            carboidratos: data.daily_log.carboidratos_total || 0,
            gorduras: data.daily_log.gorduras_total || 0
          }
        });
      } else if (data.ok) {
        setDailySummary({
          nome: data.user.nome,
          meta: data.user.meta_calorica?.meta_sugerida || 2000,
          consumido: 0,
          restante: data.user.meta_calorica?.meta_sugerida || 2000,
          percentual: 0,
          pratos: [],
          totais: { calorias: 0, proteinas: 0, carboidratos: 0, gorduras: 0 }
        });
      }
    } catch (e) {
      console.error('Erro ao carregar resumo:', e);
    }
  };

  // Registrar refeição automaticamente após identificar
  const logMealToPremium = async (prato) => {
    if (!premiumUser || !mountedRef.current) return;
    
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      if (!pin) return;
      
      const fd = new FormData();
      fd.append('pin', pin);
      fd.append('prato_nome', prato.dish_display || prato.nome || 'Prato');
      fd.append('calorias', parseFloat(prato.nutrition?.calorias?.replace(/[^\d]/g, '') || 200));
      fd.append('proteinas', parseFloat(prato.nutrition?.proteinas?.replace(/[^\d]/g, '') || 10));
      fd.append('carboidratos', parseFloat(prato.nutrition?.carboidratos?.replace(/[^\d]/g, '') || 25));
      fd.append('gorduras', parseFloat(prato.nutrition?.gorduras?.replace(/[^\d]/g, '') || 8));
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/premium/log-meal`, { 
        method: 'POST', 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      if (data.ok) {
        setDailySummary(prev => ({
          ...prev,
          consumido: data.consumido,
          restante: data.restante,
          percentual: data.percentual,
          pratos: [...(prev?.pratos || []), { nome: prato.dish_display, calorias: fd.get('calorias'), hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }]
        }));
      }
    } catch (e) {
      console.error('Erro ao registrar refeição:', e);
    }
  };

  // Logout Premium
  const handlePremiumLogout = () => {
    localStorage.removeItem('soulnutri_pin');
    localStorage.removeItem('soulnutri_nome');
    localStorage.removeItem('soulnutri_user');
    setPremiumUser(null);
    setDailySummary(null);
    setShowPremium(null);
  };

  const startCamera = async () => {
    try {
      setCameraError(null);
      // Resolução reduzida para economizar memória em celulares
      const s = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment', 
          width: { ideal: 640, max: 1280 }, 
          height: { ideal: 480, max: 720 } 
        } 
      });
      setStream(s);
      if (videoRef.current) videoRef.current.srcObject = s;
    } catch (err) { 
      console.error("Câmera não disponível:", err);
      setCameraError(err.name === 'NotAllowedError' ? 'Permissão negada. Toque para permitir.' : 'Câmera não disponível');
    }
  };

  const stopCamera = () => { 
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };
  
  const handleCameraTouch = useCallback(() => {
    // Prevenir cliques múltiplos (debounce de 1s)
    const now = Date.now();
    if (now - lastTouchRef.current < 1000) return;
    lastTouchRef.current = now;
    
    if (loadingRef.current || !videoRef.current || !canvasRef.current) return;
    
    const v = videoRef.current, c = canvasRef.current;
    // Verificar se o vídeo está pronto
    if (v.videoWidth === 0 || v.videoHeight === 0) {
      console.warn('Vídeo ainda não está pronto');
      return;
    }
    
    // Limitar tamanho máximo do canvas para economizar memória
    const maxSize = 800;
    let w = v.videoWidth;
    let h = v.videoHeight;
    if (w > maxSize || h > maxSize) {
      const ratio = Math.min(maxSize / w, maxSize / h);
      w = Math.round(w * ratio);
      h = Math.round(h * ratio);
    }
    
    c.width = w; 
    c.height = h;
    const ctx = c.getContext('2d');
    ctx.drawImage(v, 0, 0, w, h);
    
    // Qualidade reduzida para economizar memória
    c.toBlob(b => {
      if (b && mountedRef.current) {
        setLastImageBlob(b);
        identifyImage(b);
      }
      // Limpar canvas após uso
      ctx.clearRect(0, 0, w, h);
    }, 'image/jpeg', 0.7);
  }, [multiMode]);

  const identifyImage = async (blob) => {
    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    loadingRef.current = true;
    setLoading(true);
    setResult(null);
    setMultiResult(null);
    setError(null);
    setFeedbackSent(false);
    setShowFeedback(false);
    
    const fd = new FormData(); 
    fd.append("file", blob, "photo.jpg");
    
    // Se for Premium, enviar credenciais para receber dados exclusivos
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      if (pin && nome && !multiMode) {
        fd.append("pin", pin);
        fd.append("nome", nome);
      }
    } catch (e) {
      console.warn('localStorage não disponível:', e);
    }
    
    // Criar AbortController com timeout
    abortControllerRef.current = new AbortController();
    const timeoutId = setTimeout(() => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    }, REQUEST_TIMEOUT);
    
    try {
      const t = Date.now();
      const endpoint = multiMode ? `${API}/ai/identify-multi` : `${API}/ai/identify`;
      const res = await fetch(endpoint, { 
        method: "POST", 
        body: fd,
        signal: abortControllerRef.current.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      
      if (multiMode) {
        setMultiResult({ ...data, totalTime: Date.now() - t });
      } else {
        setResult({ ...data, totalTime: Date.now() - t });
      }
    } catch (e) { 
      clearTimeout(timeoutId);
      if (!mountedRef.current) return;
      
      if (e.name === 'AbortError') {
        setError('Tempo limite excedido. Tente novamente.');
      } else {
        setError(e.message || 'Erro de conexão');
      }
    } finally { 
      loadingRef.current = false;
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Criar URL de preview para mostrar a imagem
      const previewUrl = URL.createObjectURL(file);
      setPreviewImageUrl(previewUrl);
      setLastImageBlob(file);
      identifyImage(file);
    }
  };

  const clearResult = () => {
    // Cancelar requisições pendentes
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setResult(null);
    setMultiResult(null);
    setError(null);
    setShowFeedback(false);
    setFeedbackSent(false);
    // Limpar preview da imagem
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl);
      setPreviewImageUrl(null);
    }
    // Liberar memória do blob
    if (lastImageBlob) {
      URL.revokeObjectURL(URL.createObjectURL(lastImageBlob));
    }
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const res = await fetch(`${API}/ai/feedback`, { 
        method: "POST", 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const res = await fetch(`${API}/ai/feedback`, { 
        method: "POST", 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
      }
    } catch (e) {
      console.error('Erro ao enviar feedback:', e);
    }
  };

  // SALVAR CORREÇÃO DE PRATO MÚLTIPLO
  const saveMultiCorrection = async () => {
    if (!lastImageBlob || !multiCorrections.principal.trim()) {
      alert('Por favor, informe pelo menos o prato principal');
      return;
    }
    
    setCreatingDish(true);
    
    try {
      // Converter blob para array buffer para evitar "body already read"
      const arrayBuffer = await lastImageBlob.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: 'image/jpeg' });
      
      // Salvar prato principal
      const fdPrincipal = new FormData();
      fdPrincipal.append("file", blob, "photo.jpg");
      fdPrincipal.append("dish_name", multiCorrections.principal.trim());
      
      // Adicionar acompanhamentos se existirem
      if (multiCorrections.acompanhamentos.trim()) {
        fdPrincipal.append("acompanhamentos", multiCorrections.acompanhamentos.trim());
      }
      
      const res = await fetch(`${API}/ai/create-dish`, { 
        method: "POST", 
        body: fdPrincipal
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      
      if (data.ok) {
        const pratoNome = multiCorrections.principal;
        setFeedbackSent(true);
        setShowMultiCorrection(false);
        setMultiCorrections({ principal: '', acompanhamentos: '' });
        alert(`✅ Prato "${pratoNome}" salvo com sucesso!\n\nA IA vai aprender com esta correção.`);
        loadDishes(); // Atualizar lista
      } else {
        alert(data.error || 'Erro ao salvar correção');
      }
    } catch (e) {
      console.error('Erro ao salvar correção:', e);
      alert('Erro ao salvar: ' + (e.message || 'Tente novamente'));
    } finally {
      setCreatingDish(false);
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s para criação
      const res = await fetch(`${API}/ai/create-dish`, { 
        method: "POST", 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
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
      if (e.name === 'AbortError') {
        alert('Tempo limite excedido. Tente novamente.');
      } else {
        alert('Erro ao criar prato: ' + (e.message || 'Erro de conexão'));
      }
    } finally {
      if (mountedRef.current) {
        setCreatingDish(false);
      }
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

  // Função para instalar PWA
  const handleInstallApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setIsInstalled(true);
      }
      setDeferredPrompt(null);
    }
    setShowMenu(false);
  };

  return (
    <div className="app">
      {/* Header com Logo e Menu */}
      <header className="hdr">
        <div className="logo-container">
          <img src="/images/soulnutri-logo.png" alt="SoulNutri" className="logo" />
          <span className="trademark">®</span>
        </div>
        <div className="header-right">
          {status?.ready && <span className="st">✓ {status.total_dishes} pratos</span>}
          <button 
            className="menu-btn" 
            onClick={() => setShowMenu(!showMenu)}
            data-testid="menu-button"
          >
            ☰
          </button>
        </div>
      </header>

      {/* Menu dropdown */}
      {showMenu && (
        <div className="menu-dropdown" data-testid="menu-dropdown">
          {!isInstalled && deferredPrompt && (
            <button className="menu-item install" onClick={handleInstallApp}>
              📲 Adicionar à tela inicial
            </button>
          )}
          {isInstalled && (
            <div className="menu-item installed">
              ✅ App instalado
            </div>
          )}
          {!deferredPrompt && !isInstalled && (
            <div className="menu-item info">
              📱 Para instalar: use o menu do navegador → "Adicionar à tela inicial"
            </div>
          )}
          <button className="menu-item" onClick={() => { setShowMenu(false); checkStatus(); loadDishes(); }}>
            🔄 Atualizar pratos
          </button>
          <button className="menu-item" onClick={() => setShowMenu(false)}>
            ✕ Fechar
          </button>
        </div>
      )}

      {/* Câmera com moldura guia */}
      <div 
        className="cam-box" 
        onClick={cameraError ? startCamera : handleCameraTouch}
        data-testid="camera-container"
      >
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={canvasRef} hidden />
        
        {/* Erro de câmera */}
        {cameraError && (
          <div className="cam-error" data-testid="camera-error">
            <span>📷</span>
            <p>{cameraError}</p>
            <button onClick={(e) => { e.stopPropagation(); startCamera(); }}>
              🔄 Tentar novamente
            </button>
          </div>
        )}
        
        {!cameraError && (
          <div className="cam-guide">
            <div className="guide-frame"></div>
            <span className="guide-text">Posicione o prato aqui</span>
          </div>
        )}
        
        {loading && (
          <div className="cam-loading">
            <span>🔍</span>
            <p>Identificando...</p>
          </div>
        )}
        
        {!loading && !r && !cameraError && (
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
        hidden 
        onChange={handleFileSelect} 
      />

      {/* RESULTADO */}
      {r?.ok && (
        <div className={`res ${r.confidence}`} data-testid="result-container">
          
          {/* Preview da imagem selecionada da galeria */}
          {previewImageUrl && (
            <div className="preview-image-container">
              <img src={previewImageUrl} alt="Foto do prato" className="preview-image" />
            </div>
          )}
          
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

          {/* ALERTAS PREMIUM EM TEMPO REAL */}
          {r.premium && (
            <div className="premium-alerts-section" data-testid="premium-alerts">
              {/* Alertas de alérgenos críticos */}
              {r.premium.alertas_alergenos?.length > 0 && (
                <div className="premium-alert-group critical">
                  {r.premium.alertas_alergenos.map((a, i) => (
                    <div key={i} className={`premium-alert ${a.severidade}`} data-testid={`allergen-alert-${i}`}>
                      <span className="alert-emoji">{a.emoji}</span>
                      <div className="alert-content">
                        <strong>{a.titulo}</strong>
                        <p>{a.mensagem}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Alertas baseados no histórico */}
              {r.premium.alertas_historico?.length > 0 && (
                <div className="premium-alert-group history">
                  {r.premium.alertas_historico.map((a, i) => (
                    <div key={i} className={`premium-alert ${a.tipo}`} data-testid={`history-alert-${i}`}>
                      <span className="alert-emoji">{a.emoji}</span>
                      <div className="alert-content">
                        <strong>{a.titulo}</strong>
                        <p>{a.mensagem}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Combinações inteligentes */}
              {r.premium.combinacoes_sugeridas?.length > 0 && (
                <div className="premium-suggestions">
                  <h4>💡 Combinações Inteligentes</h4>
                  {r.premium.combinacoes_sugeridas.map((c, i) => (
                    <div key={i} className="suggestion-card" data-testid={`combo-${i}`}>
                      <span className="sugg-emoji">{c.emoji}</span>
                      <div className="sugg-content">
                        <strong>{c.titulo}</strong>
                        <p className="sugg-examples">Ex: {c.exemplos?.join(', ')}</p>
                        <p className="sugg-benefit">{c.beneficio}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Substituições saudáveis */}
              {r.premium.substituicoes?.length > 0 && (
                <div className="premium-substitutions">
                  <h4>🔄 Substituições Mais Saudáveis</h4>
                  {r.premium.substituicoes.map((s, i) => (
                    <div key={i} className="substitution-card" data-testid={`subst-${i}`}>
                      <span className="subst-original">{s.original}</span>
                      <span className="subst-arrow">→</span>
                      <span className="subst-new">{s.substituto}</span>
                      <span className="subst-benefit">{s.beneficio}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Badge Premium se não tiver dados científicos */}
          {!r.is_premium && !r.beneficio_principal && (
            <div className="premium-upgrade-hint" onClick={() => setShowPremium('login')}>
              <span>⭐</span>
              <p>Desbloqueie informações científicas e alertas personalizados com o <strong>Premium</strong></p>
            </div>
          )}

          {/* SEÇÃO CIENTÍFICA - Informações relevantes (PREMIUM) */}
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

          {/* VERDADE OU MITO - Educação Nutricional (PREMIUM) */}
          {r.mito_verdade && (
            <div className="mito-verdade-section" data-testid="mito-verdade">
              <div className="mito-verdade-card">
                <h4>🤔 Verdade ou Mito?</h4>
                <p className="mito-afirmacao">"{r.mito_verdade.afirmacao}"</p>
                <div className={`mito-resposta ${r.mito_verdade.resposta === 'VERDADE' ? 'verdade' : r.mito_verdade.resposta === 'MITO' ? 'mito' : 'parcial'}`}>
                  <span className="mito-emoji">{r.mito_verdade.resposta_emoji}</span>
                  <span className="mito-label">{r.mito_verdade.resposta}</span>
                </div>
                <p className="mito-explicacao">{r.mito_verdade.explicacao}</p>
                <p className="mito-fonte">📚 {r.mito_verdade.fonte}</p>
              </div>
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

      {/* RESULTADO MULTI-ITEM */}
      {multiResult?.ok && (() => {
        // Determinar item principal (proteína > vegetariano > vegano)
        const itens = multiResult.itens || [];
        const proteinas = itens.filter(i => i.categoria === 'proteína animal');
        const vegetarianos = itens.filter(i => i.categoria === 'vegetariano');
        const veganos = itens.filter(i => i.categoria === 'vegano');
        
        const principal = proteinas[0] || vegetarianos[0] || veganos[0] || itens[0];
        const acompanhamentos = itens.filter(i => i.nome !== principal?.nome);
        
        const getCategoryEmoji = (cat) => {
          if (cat === 'proteína animal') return '🍖';
          if (cat === 'vegetariano') return '🥚';
          if (cat === 'vegano') return '🥬';
          return '🍽️';
        };
        
        return (
          <div className="res multi-result" data-testid="multi-result-container">
            
            {/* Preview da imagem selecionada da galeria */}
            {previewImageUrl && (
              <div className="preview-image-container">
                <img src={previewImageUrl} alt="Foto do prato" className="preview-image" />
              </div>
            )}
            
            {/* Header com item principal */}
            {principal && (
              <div className="prato-principal">
                <span className="principal-emoji">{getCategoryEmoji(principal.categoria)}</span>
                <div className="principal-info">
                  <h2 className="principal-nome">{principal.nome}</h2>
                  {acompanhamentos.length > 0 && (
                    <span className="acompanhamentos-count">+ {acompanhamentos.length} acompanhamento{acompanhamentos.length > 1 ? 's' : ''}</span>
                  )}
                </div>
              </div>
            )}
            
            {/* Lista de acompanhamentos */}
            {acompanhamentos.length > 0 && (
              <div className="acompanhamentos-lista">
                {acompanhamentos.map((item, idx) => (
                  <span key={idx} className={`acomp-tag ${item.categoria?.replace(' ', '-')}`}>
                    {getCategoryEmoji(item.categoria)} {item.nome}
                  </span>
                ))}
              </div>
            )}

            {/* Resumo nutricional */}
            {multiResult.resumo_nutricional && (
              <div className="multi-summary" data-testid="multi-summary">
                <div className="summary-grid">
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.calorias_totais || '~' + (itens.length * 150) + ' kcal'}</span>
                    <span className="summary-label">Calorias</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.proteinas_totais || '~' + (proteinas.length * 20) + 'g'}</span>
                    <span className="summary-label">Proteínas</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.carboidratos_totais || '~' + (veganos.length * 15) + 'g'}</span>
                    <span className="summary-label">Carbos</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.gorduras_totais || '~10g'}</span>
                    <span className="summary-label">Gorduras</span>
                  </div>
                </div>
              </div>
            )}

            {/* Equilíbrio */}
            {multiResult.equilibrio && (
              <div className={`equilibrio-badge ${multiResult.equilibrio}`}>
                {multiResult.equilibrio === 'balanceado' && '⚖️ Refeição Balanceada'}
                {multiResult.equilibrio === 'rico_em_carboidratos' && '🍞 Rico em Carboidratos'}
                {multiResult.equilibrio === 'rico_em_proteinas' && '💪 Rico em Proteínas'}
                {multiResult.equilibrio === 'rico_em_gorduras' && '🧈 Rico em Gorduras'}
              </div>
            )}

            {/* Alertas */}
            {multiResult.alertas_combinados?.length > 0 && (
              <div className="multi-alerts">
                {multiResult.alertas_combinados.map((alert, i) => (
                  <span key={i} className="alert-tag">⚠️ {alert}</span>
                ))}
              </div>
            )}

            {/* Dica */}
            {multiResult.dica_nutricional && (
              <div className="dica-box">
                <p>💡 {multiResult.dica_nutricional}</p>
              </div>
            )}

            <div className="time" data-testid="multi-response-time">
              ⚡ {multiResult.search_time_ms?.toFixed(0)}ms
            </div>

            {/* Compartilhar */}
            <button 
              className="share-btn"
              onClick={() => {
                const acompText = acompanhamentos.map(i => i.nome).join(', ');
                const text = `🍽️ Meu prato no Cibi Sana:\n\n${getCategoryEmoji(principal?.categoria)} ${principal?.nome}${acompText ? `\n+ ${acompText}` : ''}\n\n📊 ${multiResult.resumo_nutricional?.calorias_totais || 'Calculando calorias...'}\n\nAnalisado pelo SoulNutri!`;
                if (navigator.share) {
                  navigator.share({ title: 'SoulNutri', text });
                } else {
                  navigator.clipboard.writeText(text);
                  alert('Texto copiado! Cole para compartilhar.');
                }
              }}
              data-testid="multi-share-button"
            >
              📤 Compartilhar meu prato
            </button>

            {/* BOTÕES DE FEEDBACK - MULTI */}
            {!feedbackSent && (
              <div className="feedback-section">
                <p className="feedback-question">O reconhecimento está correto?</p>
                <div className="feedback-btns">
                  <button className="fb-btn correct" onClick={() => {
                    // Salvar feedback positivo para treino
                    setFeedbackSent(true);
                  }}>
                    ✅ Sim, correto
                  </button>
                  <button className="fb-btn incorrect" onClick={() => {
                    // Pré-preencher com o que a IA identificou
                    const principalNome = principal?.nome || '';
                    const acompNomes = acompanhamentos.map(a => a.nome).join(', ');
                    setMultiCorrections({
                      principal: principalNome,
                      acompanhamentos: acompNomes
                    });
                    setShowMultiCorrection(true);
                  }}>
                    ❌ Não, corrigir
                  </button>
                </div>
              </div>
            )}

            {feedbackSent && (
              <div className="feedback-thanks">
                ✅ Obrigado! Isso melhora o reconhecimento.
              </div>
            )}
          </div>
        );
      })()}

      {/* MODAL DE CORREÇÃO MULTI */}
      {showMultiCorrection && (
        <div className="modal-overlay" onClick={() => setShowMultiCorrection(false)}>
          <div className="modal-content multi-correction" onClick={e => e.stopPropagation()}>
            <h3>✏️ Corrigir Identificação</h3>
            
            <div className="correction-form">
              <div className="form-group">
                <label>🍽️ Item Principal (ou primeiro item):</label>
                <input 
                  type="text"
                  placeholder="Ex: Maminha ao Molho, Peixe Grelhado..."
                  value={multiCorrections.principal}
                  onChange={e => setMultiCorrections({...multiCorrections, principal: e.target.value})}
                  autoFocus
                />
              </div>
              
              <div className="form-group">
                <label>🥗 Outros itens do prato (separados por vírgula):</label>
                <textarea 
                  placeholder="Ex: Arroz, Salada, Feijão, Camarão..."
                  value={multiCorrections.acompanhamentos}
                  onChange={e => setMultiCorrections({...multiCorrections, acompanhamentos: e.target.value})}
                  rows={4}
                />
              </div>
              
              <small className="help-text">
                💡 Edite apenas o que está errado. O cliente pode misturar proteínas e veganos no mesmo prato.
              </small>
            </div>
            
            <div className="modal-actions-fixed">
              <button 
                className="save-correction-btn" 
                onClick={saveMultiCorrection}
                disabled={creatingDish || !multiCorrections.principal.trim()}
              >
                {creatingDish ? '⏳ Salvando...' : '💾 Salvar Correção'}
              </button>
              <button className="cancel-btn" onClick={() => setShowMultiCorrection(false)}>
                ✕ Cancelar
              </button>
            </div>
          </div>
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

      {/* PREMIUM - Mini contador flutuante */}
      {premiumUser && dailySummary && !showPremium && (
        <div className="mini-counter" onClick={() => setShowPremium('dashboard')} data-testid="mini-counter">
          <div className="mini-value">{dailySummary.consumido?.toFixed(0) || 0}</div>
          <div className="mini-label">de {dailySummary.meta?.toFixed(0)} kcal</div>
          <div className="mini-progress">
            <div 
              className="mini-fill" 
              style={{ 
                width: `${Math.min(dailySummary.percentual || 0, 100)}%`,
                background: dailySummary.percentual >= 100 ? '#ef4444' : dailySummary.percentual >= 75 ? '#f59e0b' : '#22c55e'
              }} 
            />
          </div>
        </div>
      )}

      {/* PREMIUM - Botão flutuante */}
      <button 
        className={`premium-btn ${premiumUser ? 'logged-in' : ''}`}
        onClick={() => setShowPremium(premiumUser ? 'dashboard' : 'login')}
        data-testid="premium-button"
      >
        {premiumUser ? 'Dieta' : 'Premium'}
      </button>

      {/* PREMIUM - Modal */}
      {showPremium && (
        <div className="modal-overlay" onClick={() => setShowPremium(null)}>
          <div className="modal-content premium-modal" onClick={e => e.stopPropagation()}>
            {showPremium === 'login' && (
              <PremiumLogin 
                onSuccess={(data) => {
                  setPremiumUser(data.user);
                  loadDailySummary();
                  setShowPremium('dashboard');
                }}
                onRegister={() => setShowPremium('register')}
                onCancel={() => setShowPremium(null)}
              />
            )}
            
            {showPremium === 'register' && (
              <PremiumRegister 
                onSuccess={(data) => {
                  setPremiumUser({ nome: data.nome, meta_calorica: data.meta_calorica });
                  setDailySummary({ nome: data.nome, meta: data.meta_calorica.meta_sugerida, consumido: 0, restante: data.meta_calorica.meta_sugerida, percentual: 0, pratos: [] });
                  setShowPremium('dashboard');
                }}
                onCancel={() => setShowPremium('login')}
              />
            )}
            
            {showPremium === 'dashboard' && premiumUser && (
              <DailyCounter 
                user={premiumUser}
                onLogout={handlePremiumLogout}
                onClose={() => setShowPremium(null)}
              />
            )}
          </div>
        </div>
      )}

      {/* Rodapé */}
      <footer className="footer">
        <small>Powered by Emergent</small>
      </footer>
    </div>
  );
}

export default App;
